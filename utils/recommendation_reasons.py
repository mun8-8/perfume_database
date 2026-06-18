"""향수별 추천 이유(가중치 매칭) 문구 생성."""

from __future__ import annotations

from database.repositories import perfume_repository


def build_recommendation_reasons(
    perfume_id: int | None,
    context: dict | None,
    score: int | None = None,
) -> list[str]:
    """
    선택 취향 대비 해당 향수의 일치 항목을 한국어로 반환.
    perfume_id 없음(데모)이면 점수·요약 기반 추정.
    """
    if not context:
        return []

    main_category = context.get("main_category", "")
    main_scent = context.get("main_scent", "")
    note_label = context.get("note_label", "")
    sub_categories = context.get("additional_categories") or []
    sub_name = sub_categories[0] if sub_categories else ""

    if not perfume_id:
        return _demo_reasons(main_category, main_scent, note_label, sub_name, score)

    notes = perfume_repository.get_perfume_notes(perfume_id)
    if not notes:
        return _demo_reasons(main_category, main_scent, note_label, sub_name, score)

    main_category_id = context.get("main_category_id")
    main_scent_id = context.get("main_scent_id")
    note_type = context.get("note_type")
    additional_ids = set(context.get("additional_category_ids") or [])

    has_main_category = False
    has_detail_scent = False
    has_note_match = False
    has_sub_category = False

    for row in notes:
        scent = row.get("scents") or {}
        scent_ko = scent.get("scent_name_ko")
        category = scent.get("scent_categories") or {}
        category_name = category.get("category_name")
        row_note_type = row.get("note_type")

        if main_category and category_name == main_category:
            has_main_category = True
        if main_scent and scent_ko == main_scent:
            has_detail_scent = True
            if note_type and row_note_type == note_type:
                has_note_match = True
        if (
            sub_name
            and category_name == sub_name
            and category_name != main_category
        ):
            has_sub_category = True

        # ID 기반 보조 (컨텍스트에 ID가 있을 때)
        if main_category_id or main_scent_id or additional_ids:
            scent_id = scent.get("scent_id")
            category_id = scent.get("category_id") or category.get("category_id")
            if main_category_id and category_id == main_category_id:
                has_main_category = True
            if main_scent_id and scent_id == main_scent_id:
                has_detail_scent = True
                if note_type and row_note_type == note_type:
                    has_note_match = True
            if (
                category_id in additional_ids
                and main_category_id
                and category_id != main_category_id
            ):
                has_sub_category = True

    reasons: list[str] = []
    if has_main_category and main_category:
        reasons.append(f"주향({main_category}) 계열 노트 포함")
    if has_detail_scent and main_scent:
        reasons.append(f"세부향({main_scent}) 일치")
    if has_note_match and note_label:
        reasons.append(f"발향 시점({note_label}) 일치")
    if has_sub_category and sub_name:
        reasons.append(f"보조향({sub_name}) 계열 노트 포함")

    if not reasons and score:
        return _demo_reasons(main_category, main_scent, note_label, sub_name, score)
    return reasons


def _demo_reasons(
    main_category: str,
    main_scent: str,
    note_label: str,
    sub_name: str,
    score: int | None,
) -> list[str]:
    """데모 향수용 — 점수 구간별 추정 이유."""
    tier = score or 0
    reasons: list[str] = []
    if tier >= 30 and main_category:
        reasons.append(f"주향({main_category}) 계열과 어울리는 노트")
    if tier >= 60 and main_scent:
        reasons.append(f"세부향({main_scent})과 유사한 향조")
    if tier >= 80 and note_label:
        reasons.append(f"발향 시점({note_label})에 맞는 구성")
    if tier >= 100 and sub_name:
        reasons.append(f"보조향({sub_name}) 계열과의 조화")
    if not reasons:
        reasons.append("선택하신 취향 프로필과 유사한 향 조합")
    return reasons
