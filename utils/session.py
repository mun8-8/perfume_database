"""Streamlit 세션 상태 · 인증 헬퍼."""

import streamlit as st


def init_session() -> None:
    defaults = {
        "auth_mode": None,
        "user_id": None,
        "user_email": None,
        "user_nickname": None,
        "access_token": None,
        "refresh_token": None,
        "test_id": None,
        "recommendations": None,
        "test_summary": None,
        "pref_step": 1,
        "pref_main_category": None,
        "pref_main_scent": None,
        "pref_note_type": None,
        "pref_additional_categories": None,
        "perf_result_ready": False,
        "show_recommendation_reasons": False,
        "recommendation_context": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_logged_in() -> bool:
    return st.session_state.get("auth_mode") == "member" and bool(
        st.session_state.get("user_id")
    )


def is_guest() -> bool:
    return st.session_state.get("auth_mode") == "guest"


def has_auth() -> bool:
    return is_logged_in() or is_guest()


def current_user_id() -> str | None:
    if is_logged_in():
        return st.session_state.get("user_id")
    return None


def set_guest() -> None:
    st.session_state["auth_mode"] = "guest"
    st.session_state["user_id"] = None
    st.session_state["user_email"] = None
    st.session_state["user_nickname"] = None
    st.session_state["access_token"] = None
    st.session_state["refresh_token"] = None


def set_member(
    user_id: str,
    email: str,
    nickname: str,
    access_token: str,
    refresh_token: str,
) -> None:
    st.session_state["auth_mode"] = "member"
    st.session_state["user_id"] = user_id
    st.session_state["user_email"] = email
    st.session_state["user_nickname"] = nickname
    st.session_state["access_token"] = access_token
    st.session_state["refresh_token"] = refresh_token


def clear_test_session() -> None:
    """취향 테스트·추천 결과 관련 세션 초기화."""
    reset_preference_wizard()
    for key in (
        "test_id",
        "recommendations",
        "test_summary",
        "recommendation_context",
        "history_save_error",
        "view_history_test_id",
        "db_error_msg",
        "tmp_selected_main",
        "tmp_selected_detail",
        "tmp_selected_note",
        "tmp_selected_sub",
        "_pending_wizard_reset",
    ):
        st.session_state.pop(key, None)


def start_with_different_account() -> None:
    """다른 계정으로 시작 — 로그아웃 후 테스트·추천 결과까지 초기화."""
    if is_logged_in():
        from services.auth_service import sign_out

        sign_out(
            st.session_state.get("access_token"),
            st.session_state.get("refresh_token"),
        )
    clear_auth()
    clear_test_session()


def clear_auth() -> None:
    set_guest()
    st.session_state["auth_mode"] = None


def reset_preference_wizard() -> None:
    st.session_state["pref_step"] = 1
    st.session_state["pref_main_category"] = None
    st.session_state["pref_main_scent"] = None
    st.session_state["pref_note_type"] = None
    st.session_state["pref_additional_categories"] = None
    st.session_state["show_recommendation_reasons"] = False
    st.session_state.pop("show_recommendation_reasons_widget", None)


def request_preference_wizard_reset() -> None:
    """위젯 렌더 후 session_state 수정 오류를 피하기 위해 다음 rerun 에서 초기화."""
    st.session_state["_pending_wizard_reset"] = True