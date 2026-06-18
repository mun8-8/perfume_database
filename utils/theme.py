"""다크 모드 · 공통 페이지 테마."""

from __future__ import annotations

import streamlit as st

from utils.session import init_session


def inject_theme_styles() -> None:
    if not st.session_state.get("dark_mode"):
        return

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stApp [data-testid="stHeader"] {
            background-color: rgba(14, 17, 23, 0.95);
        }
        .stApp [data-testid="stSidebar"] {
            background-color: #161b22;
        }
        .stApp [data-testid="stSidebar"] * {
            color: #e6edf3 !important;
        }
        .stApp .block-container {
            color: #e6edf3;
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp p, .stApp label, .stApp span, .stApp li {
            color: #e6edf3;
        }
        .stApp [data-testid="stMarkdownContainer"] p {
            color: #e6edf3;
        }
        .stApp div[data-testid="stMetric"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 0.5rem;
            padding: 0.5rem;
        }
        .stApp [data-testid="stExpander"] details {
            background-color: #161b22;
            border: 1px solid #30363d;
        }
        .stApp [data-testid="stExpander"] summary {
            color: #e6edf3 !important;
        }
        .stApp [data-testid="stForm"] {
            border-color: #30363d;
        }
        .stApp .stAlert {
            border: 1px solid #30363d;
        }
        .stApp hr {
            border-color: #30363d;
        }
        .stApp [data-baseweb="tab-list"] {
            background-color: #161b22;
        }
        .stApp button[kind="secondary"] {
            background-color: #21262d;
            color: #e6edf3;
            border-color: #30363d;
        }
        .stApp [data-testid="stCaptionContainer"] {
            color: #8b949e !important;
        }
        .stApp .scent-desc-panel,
        .stApp .scent-desc-panel * {
            color: #1a1a1a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle(location: str = "sidebar") -> None:
    """다크 모드 토글 — sidebar 또는 상단."""
    st.session_state.setdefault("dark_mode", False)

    target = st.sidebar if location == "sidebar" else st
    with target:
        st.toggle("🌙 다크 모드", key="dark_mode")


def apply_page_theme(*, toggle_in_sidebar: bool = True) -> None:
    """init_session 이후 각 페이지에서 호출."""
    if toggle_in_sidebar:
        render_theme_toggle("sidebar")
    inject_theme_styles()
