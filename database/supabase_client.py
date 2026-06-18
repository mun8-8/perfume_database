"""Supabase 클라이언트 (Streamlit secrets 기반)."""

from functools import lru_cache

import streamlit as st
from supabase import Client, create_client


@lru_cache
def get_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError) as exc:
        raise RuntimeError(
            "Supabase 연결 정보가 없습니다. "
            ".streamlit/secrets.toml 에 SUPABASE_URL, SUPABASE_KEY 를 설정하세요."
        ) from exc
    return create_client(url, key)


def ensure_authenticated_session() -> None:
    """로그인 JWT 를 클라이언트에 설정해 RLS INSERT/SELECT 가 동작하게 합니다."""
    access = st.session_state.get("access_token")
    refresh = st.session_state.get("refresh_token")
    if not access or not refresh:
        return
    try:
        get_supabase().auth.set_session(access, refresh)
    except Exception:
        pass
