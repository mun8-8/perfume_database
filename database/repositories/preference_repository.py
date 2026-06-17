from database.supabase_client import get_supabase


def create_user_preference_test(user_id: str | None = None) -> int:
    payload: dict = {}
    if user_id is not None:
        payload["user_id"] = user_id

    response = get_supabase().table("user_preference_tests").insert(payload).execute()
    if not response.data:
        raise RuntimeError("취향 테스트 기록 생성에 실패했습니다.")
    return response.data[0]["test_id"]


def save_main_choice(
    test_id: int,
    category_id: int,
    scent_id: int,
    preferred_note_type: str,
) -> None:
    get_supabase().table("user_test_main_choice").insert(
        {
            "test_id": test_id,
            "category_id": category_id,
            "scent_id": scent_id,
            "preferred_note_type": preferred_note_type,
        }
    ).execute()


def save_additional_categories(test_id: int, category_ids: list[int]) -> None:
    if not category_ids:
        return

    rows = [{"test_id": test_id, "category_id": cid} for cid in category_ids]
    get_supabase().table("user_test_additional_categories").insert(rows).execute()
