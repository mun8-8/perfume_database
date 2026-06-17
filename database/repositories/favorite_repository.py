from database.supabase_client import get_supabase


def get_saved_perfume_ids(user_id: str) -> set[int]:
    response = (
        get_supabase()
        .table("saved_perfumes")
        .select("perfume_id")
        .eq("user_id", user_id)
        .execute()
    )
    return {row["perfume_id"] for row in (response.data or [])}


def list_saved_perfumes(user_id: str) -> list[dict]:
    response = (
        get_supabase()
        .table("saved_perfumes")
        .select(
            "saved_id, perfume_id, created_at, perfumes(perfume_id, perfume_name, brand_name)"
        )
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def save_perfume(user_id: str, perfume_id: int) -> None:
    get_supabase().table("saved_perfumes").upsert(
        {"user_id": user_id, "perfume_id": perfume_id},
        on_conflict="user_id,perfume_id",
    ).execute()


def remove_saved_perfume(user_id: str, perfume_id: int) -> None:
    (
        get_supabase()
        .table("saved_perfumes")
        .delete()
        .eq("user_id", user_id)
        .eq("perfume_id", perfume_id)
        .execute()
    )
