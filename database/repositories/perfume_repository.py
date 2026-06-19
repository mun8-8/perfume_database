from database.supabase_client import get_supabase
from utils.constants import NOTE_TYPE_LABELS
from utils.perfume_mood_catalog import lookup_perfume_mood


def get_perfumes_by_ids(perfume_ids: list[int]) -> dict[int, dict]:
    if not perfume_ids:
        return {}
    response = (
        get_supabase()
        .table("perfumes")
        .select("perfume_id, perfume_name, brand_name")
        .in_("perfume_id", perfume_ids)
        .execute()
    )
    return {row["perfume_id"]: row for row in (response.data or [])}


def build_perfume_description(perfume_id: int) -> str:
    notes = get_perfume_notes(perfume_id)
    if not notes:
        return "선택하신 노트를 조화롭게 조합한 추천 향수입니다."

    grouped = format_notes_by_type(notes)
    parts: list[str] = []
    for note_type, label in NOTE_TYPE_LABELS.items():
        names = grouped.get(note_type) or []
        if names:
            parts.append(f"{label}: {', '.join(names)}")
    return "\n".join(parts) if parts else "선택하신 노트를 조화롭게 조합한 추천 향수입니다."


def get_perfume_moods(perfume_id: int) -> list[str]:
    response = (
        get_supabase()
        .table("perfume_moods")
        .select("mood_keywords(mood_name_ko)")
        .eq("perfume_id", perfume_id)
        .execute()
    )
    moods: list[str] = []
    for row in response.data or []:
        mood = (row.get("mood_keywords") or {}).get("mood_name_ko", "")
        if mood:
            moods.append(mood)
    return moods


def build_perfume_mood(
    perfume_id: int | None,
    summary: dict | None = None,
    *,
    perfume_name: str | None = None,
    brand_name: str | None = None,
) -> str:
    name = perfume_name
    brand = brand_name

    if perfume_id and (not name or not brand):
        perfumes = get_perfumes_by_ids([perfume_id])
        row = perfumes.get(perfume_id) or {}
        name = name or row.get("perfume_name")
        brand = brand or row.get("brand_name")

    if name:
        catalog_mood = lookup_perfume_mood(brand or "", name)
        if catalog_mood:
            return catalog_mood

    if perfume_id:
        moods = get_perfume_moods(perfume_id)
        if moods:
            return ", ".join(moods)

    if not summary:
        return "선택하신 향조가 조화롭게 어우러진 편안한 분위기입니다."

    main_category = summary.get("main_category", "")
    main_scent = summary.get("main_scent", "")
    additional = summary.get("additional_categories") or []

    if main_category and main_scent and additional:
        sub_text = ", ".join(additional)
        return (
            f"{main_category}의 {main_scent}와 {sub_text} 보조 노트가 어우러져 "
            f"당신의 취향에 맞는 분위기를 연출합니다."
        )
    if main_category and main_scent:
        return f"{main_category}의 {main_scent}이 중심이 되어 은은하고 조화로운 분위기를 만듭니다."
    if main_category:
        return f"{main_category} 계열의 향이 주는 깔끔하고 편안한 분위기입니다."
    return "선택하신 향조가 조화롭게 어우러진 편안한 분위기입니다."


def get_perfume_notes(perfume_id: int) -> list[dict]:
    response = (
        get_supabase()
        .table("perfume_notes")
        .select(
            "note_type, scents(scent_name_ko, scent_name_en, scent_categories(category_name))"
        )
        .eq("perfume_id", perfume_id)
        .execute()
    )
    return response.data or []


def format_notes_by_type(notes: list[dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {"top": [], "middle": [], "base": []}
    for row in notes:
        note_type = row.get("note_type", "")
        scent = row.get("scents") or {}
        label = scent.get("scent_name_ko") or scent.get("scent_name_en") or ""
        if note_type in grouped and label:
            grouped[note_type].append(label)
    return grouped


def google_search_url(perfume_name: str, brand_name: str = "") -> str:
    from urllib.parse import quote_plus

    query = f"{brand_name} {perfume_name}".strip()
    return f"https://www.google.com/search?q={quote_plus(query)}&hl=ko"
