"""Supabase Auth 연동."""

from database.repositories import user_repository
from database.supabase_client import get_supabase, ensure_authenticated_session


def format_auth_error(exc: Exception) -> str:
    """Supabase Auth 오류를 사용자 친화적 한국어로 변환."""
    raw = str(getattr(exc, "message", None) or exc)
    msg = raw.lower()

    if "rate limit" in msg:
        return (
            "이메일 발송 한도를 초과했습니다. "
            "개발·테스트 중이라면 Supabase 대시보드 → Authentication → Providers → Email 에서 "
            "**Confirm email(이메일 인증)** 을 끄면 해결됩니다. "
            "또는 1시간 정도 기다린 뒤 다시 시도하거나, 이미 가입됐다면 **로그인** 탭에서 접속해 보세요."
        )
    if "already registered" in msg or "user already registered" in msg:
        return "이미 가입된 이메일입니다. 로그인 탭에서 로그인해 주세요."
    if "email not confirmed" in msg:
        return "이메일 인증이 완료되지 않았습니다. 받은 편지함(스팸함 포함)을 확인해 주세요."
    if "invalid login credentials" in msg:
        return "이메일 또는 비밀번호가 올바르지 않습니다."
    if "invalid email" in msg:
        return "올바른 이메일 주소 형식이 아닙니다."
    if "row-level security" in msg:
        return (
            "프로필 저장 권한(RLS) 오류입니다. "
            "Supabase SQL Editor에서 `sql/fix_users_rls.sql` 파일 내용을 실행해 주세요."
        )
    if "user not found" in msg:
        return "등록되지 않은 이메일입니다."
    return raw


class AuthService:
    """01_auth 페이지에서 사용하는 (success, payload) 형태 래퍼."""

    def login_user(self, email: str, password: str) -> tuple[bool, dict | None, str]:
        try:
            return True, sign_in(email, password), ""
        except Exception as exc:
            return False, None, format_auth_error(exc)

    def register_user(
        self, email: str, password: str, nickname: str
    ) -> tuple[bool, str]:
        try:
            result = sign_up(email, password, nickname)
            if result.get("needs_confirmation"):
                return (
                    True,
                    "회원가입이 완료되었습니다. 이메일 인증 후 로그인해 주세요.",
                )
            return True, "회원가입이 완료되었습니다. 로그인 탭에서 바로 로그인할 수 있습니다."
        except Exception as exc:
            return False, format_auth_error(exc)

    def change_password(self, new_password: str) -> tuple[bool, str]:
        try:
            change_password(new_password)
            return True, "비밀번호가 변경되었습니다."
        except Exception as exc:
            return False, format_auth_error(exc)


auth_service = AuthService()


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

    if session:
        client.auth.set_session(session.access_token, session.refresh_token)
        try:
            user_repository.upsert_user(
                user_id=str(user.id),
                email=email,
                nickname=nickname,
            )
        except Exception:
            pass

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
        "needs_confirmation": True,
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

    client.auth.set_session(session.access_token, session.refresh_token)

    profile = None
    try:
        profile = user_repository.get_user(str(user.id))
    except Exception:
        pass

    nickname = (profile or {}).get("nickname") or user.user_metadata.get("nickname") or email.split("@")[0]

    try:
        user_repository.upsert_user(
            user_id=str(user.id),
            email=user.email or email,
            nickname=nickname,
        )
    except Exception:
        pass

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


def change_password(new_password: str) -> None:
    if len(new_password) < 6:
        raise ValueError("비밀번호는 최소 6자 이상이어야 합니다.")
    ensure_authenticated_session()
    get_supabase().auth.update_user({"password": new_password})
