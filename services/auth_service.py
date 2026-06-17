"""Supabase Auth 연동."""

from database.repositories import user_repository
from database.supabase_client import get_supabase


def sign_up(email: str, password: str, nickname: str) -> dict:
    client = get_supabase()
    response = client.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {"data": {"nickname": nickname}},
        }
    )
    user = response.user
    session = response.session
    if not user:
        raise RuntimeError("회원가입에 실패했습니다.")

    user_repository.upsert_user(
        user_id=str(user.id),
        email=email,
        nickname=nickname,
    )

    if session:
        return {
            "user_id": str(user.id),
            "email": email,
            "nickname": nickname,
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }

    return {
        "user_id": str(user.id),
        "email": email,
        "nickname": nickname,
        "access_token": None,
        "refresh_token": None,
    }


def sign_in(email: str, password: str) -> dict:
    client = get_supabase()
    response = client.auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    user = response.user
    session = response.session
    if not user or not session:
        raise RuntimeError("로그인에 실패했습니다.")

    profile = user_repository.get_user(str(user.id))
    nickname = (profile or {}).get("nickname") or user.user_metadata.get("nickname") or email.split("@")[0]

    user_repository.upsert_user(
        user_id=str(user.id),
        email=user.email or email,
        nickname=nickname,
    )

    return {
        "user_id": str(user.id),
        "email": user.email or email,
        "nickname": nickname,
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
    }


def sign_out(access_token: str | None, refresh_token: str | None) -> None:
    client = get_supabase()
    if access_token and refresh_token:
        try:
            client.auth.set_session(access_token, refresh_token)
        except Exception:
            pass
    try:
        client.auth.sign_out()
    except Exception:
        pass
