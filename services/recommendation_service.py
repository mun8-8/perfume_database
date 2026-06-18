"""취향 테스트 저장 + 추천 점수 연산 오케스트레이션."""

from __future__ import annotations

import streamlit as st

from database.repositories import (
    perfume_repository,
    preference_repository,
    recommendation_repository,
    scent_repository,
)
from utils.constants import NOTE_TYPE_LABELS


def _resolve_selection_ids(
    main_category: str,
    detail_scent: str,
    sub_category: str | None,
) -> tuple[int, int, list[int]]:
    categories = scent_repository.get_scent_categories()
    cat_by_name = {c["category_name"]: c["category_id"] for c in categories}

    main_category_id = cat_by_name.get(main_category)
    if main_category_id is None:
        raise ValueError(f"주향 '{main_category}'을 DB에서 찾을 수 없습니다.")

    scents = scent_repository.get_scents_by_category(main_category_id, main_category)
    scent_by_ko = {s["scent_name_ko"]: s["scent_id"] for s in scents}
    main_scent_id = scent_by_ko.get(detail_scent)
    if main_scent_id is None:
        raise ValueError(f"세부향 '{detail_scent}'을 DB에서 찾을 수 없습니다.")

    additional_ids: list[int] = []
    if sub_category:
        sub_id = cat_by_name.get(sub_category)
        if sub_id is not None and sub_id != main_category_id:
            additional_ids.append(sub_id)

    return main_category_id, main_scent_id, additional_ids


def _score_perfumes(
    main_category_id: int,
    main_scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
) -> list[dict]:
    try:
        return recommendation_repository.score_perfumes_via_rpc(
            main_category_id,
            main_scent_id,
            preferred_note_type,
            additional_category_ids,
        )
    except Exception:
        return recommendation_repository.score_perfumes_via_join_query(
            main_category_id,
            main_scent_id,
            preferred_note_type,
            additional_category_ids,
        )


def _build_recommendation_cards(scored_rows: list[dict]) -> list[dict]:
    perfume_ids = [row["perfume_id"] for row in scored_rows]
    perfumes = perfume_repository.get_perfumes_by_ids(perfume_ids)

    cards: list[dict] = []
    for row in scored_rows:
        perfume_id = row["perfume_id"]
        score = row.get("recommendation_score", 0)
        perfume = perfumes.get(perfume_id, {})
        cards.append(
            {
                "perfume_id": perfume_id,
                "name": perfume.get("perfume_name", "이름 없음"),
                "brand": perfume.get("brand_name", ""),
                "description": perfume_repository.build_perfume_description(perfume_id),
                "score": int(score),
                "recommendation_score": int(score),
            }
        )
    return cards


def run_full_recommendation_flow(
    category_id: int,
    scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list,
    user_id: str | None = None,
) -> tuple[int | None, list[dict]]:
    """
    세션의 한국어 선택값을 DB ID로 변환한 뒤 recommend_perfumes RPC로 Top 5를 계산합니다.
    """
    main_cat = st.session_state.get("pref_main_category")
    detail_scent = st.session_state.get("pref_main_scent")
    note_type = preferred_note_type or st.session_state.get("pref_note_type")
    sub_categories = st.session_state.get("pref_additional_categories") or []
    sub_cat = sub_categories[0] if sub_categories else None

    if not main_cat or not detail_scent or not note_type:
        raise ValueError("취향 선택 정보가 부족합니다. 처음부터 다시 진행해 주세요.")

    main_category_id, main_scent_id, resolved_additional_ids = _resolve_selection_ids(
        main_cat,
        detail_scent,
        sub_cat,
    )

    test_id: int | None = None
    save_error: str | None = None
    if user_id:
        from database.supabase_client import ensure_authenticated_session

        ensure_authenticated_session()
        try:
            test_id = preference_repository.create_user_preference_test(user_id)
            preference_repository.save_main_choice(
                test_id,
                main_category_id,
                main_scent_id,
                note_type,
            )
            preference_repository.save_additional_categories(
                test_id,
                resolved_additional_ids,
            )
        except Exception as exc:
            test_id = None
            save_error = str(exc)

    scored_rows = _score_perfumes(
        main_category_id,
        main_scent_id,
        note_type,
        resolved_additional_ids,
    )

    if test_id and scored_rows:
        try:
            recommendation_repository.save_recommendation_results(test_id, scored_rows)
        except Exception as exc:
            if save_error is None:
                save_error = str(exc)

    if save_error:
        st.session_state["history_save_error"] = save_error
    else:
        st.session_state.pop("history_save_error", None)

    recommendations = _build_recommendation_cards(scored_rows)

    note_label = NOTE_TYPE_LABELS.get(note_type, note_type)
    st.session_state["test_summary"] = {
        "main_category": main_cat,
        "main_scent": detail_scent,
        "note_type": note_type,
        "note_label": note_label,
        "additional_categories": sub_categories,
        "summary_line": (
            f"{main_cat} - {detail_scent} ({note_label}) / "
            f"{', '.join(sub_categories) if sub_categories else '없음'}"
        ),
    }
    st.session_state["recommendation_context"] = {
        "main_category": main_cat,
        "main_scent": detail_scent,
        "note_type": note_type,
        "note_label": note_label,
        "additional_categories": sub_categories,
        "main_category_id": main_category_id,
        "main_scent_id": main_scent_id,
        "additional_category_ids": resolved_additional_ids,
    }

    return test_id, recommendations
