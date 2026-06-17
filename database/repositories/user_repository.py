from database.supabase_client import get_supabase


def upsert_user(user_id: str, email: str, nickname: str) -> None:
    get_supabase().table("users").upsert(
        {
            "user_id": user_id,
            "email": email,
            "nickname": nickname,
        }
    ).execute()


def get_user(user_id: str) -> dict | None:
    response = (
        get_supabase()
        .table("users")
        .select("user_id, email, nickname, created_at")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
