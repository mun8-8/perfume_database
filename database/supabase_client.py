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
