from database.supabase_client import get_supabase
from utils.constants import NOTE_TYPE_LABELS


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
    return f"https://www.google.com/search?q={quote_plus(query)}"
