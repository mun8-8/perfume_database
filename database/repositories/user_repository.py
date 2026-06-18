from database.supabase_client import get_supabase


def upsert_user(user_id: str, email: str, nickname: str) -> None:
    """로그인 세션(JWT) 기준으로 프로필 저장. RPC 우선, 실패 시 테이블 upsert."""
    client = get_supabase()
    try:
        client.rpc(
            "upsert_user_profile",
            {"p_email": email, "p_nickname": nickname},
        ).execute()
        return
    except Exception:
        pass

    client.table("users").upsert(
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
