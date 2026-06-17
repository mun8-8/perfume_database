from database.supabase_client import get_supabase
from utils.constants import NOTE_TYPE_LABELS


def list_user_tests(user_id: str) -> list[dict]:
    response = (
        get_supabase()
        .table("user_preference_tests")
        .select("test_id, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def get_test_summary(test_id: int) -> dict | None:
    main_response = (
        get_supabase()
        .table("user_test_main_choice")
        .select(
            "preferred_note_type, "
            "scent_categories(category_name), "
            "scents(scent_name_ko)"
        )
        .eq("test_id", test_id)
        .limit(1)
        .execute()
    )
    main_rows = main_response.data or []
    if not main_rows:
        return None

    main = main_rows[0]
    category = (main.get("scent_categories") or {}).get("category_name", "")
    scent = (main.get("scents") or {}).get("scent_name_ko", "")
    note_type = main.get("preferred_note_type", "")
    note_label = NOTE_TYPE_LABELS.get(note_type, note_type)

    add_response = (
        get_supabase()
        .table("user_test_additional_categories")
        .select("scent_categories(category_name)")
        .eq("test_id", test_id)
        .execute()
    )
    additional = [
        (row.get("scent_categories") or {}).get("category_name", "")
        for row in (add_response.data or [])
        if row.get("scent_categories")
    ]

    return {
        "test_id": test_id,
        "main_category": category,
        "main_scent": scent,
        "note_type": note_type,
        "note_label": note_label,
        "additional_categories": additional,
        "summary_line": f"{category} - {scent} ({note_label}) / {', '.join(additional) if additional else '없음'}",
    }
