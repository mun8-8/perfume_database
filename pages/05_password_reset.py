"""비밀번호 재설정 — 이메일 링크 또는 인증 코드."""

import streamlit as st
import streamlit.components.v1 as components

from services.auth_service import auth_service, establish_recovery_session
from utils.session import init_session
from utils.theme import apply_page_theme

st.set_page_config(page_title="비밀번호 재설정", page_icon="🔒", layout="centered")
init_session()
apply_page_theme()

# 이메일 링크의 #access_token=... 을 query string 으로 옮김 (Streamlit은 hash 미지원)
components.html(
    """
    <script>
    (function () {
        const h = window.parent.location.hash.substring(1);
        if (!h) return;
        const p = new URLSearchParams(h);
        if (!p.get("access_token")) return;
        const u = new URL(window.parent.location.href);
        if (u.searchParams.get("access_token")) return;
        p.forEach((v, k) => u.searchParams.set(k, v));
        u.hash = "";
        window.parent.location.replace(u.toString());
    })();
    </script>
    """,
    height=0,
)

access_token = st.query_params.get("access_token")
refresh_token = st.query_params.get("refresh_token")
recovery_type = st.query_params.get("type")

if access_token and refresh_token and not st.session_state.get("recovery_session_ready"):
    try:
        establish_recovery_session(access_token, refresh_token)
        st.session_state["recovery_session_ready"] = True
    except Exception as exc:
        st.error(f"재설정 링크 처리 실패: {exc}")

st.title("🔒 비밀번호 재설정")

if st.session_state.get("recovery_session_ready") or recovery_type == "recovery":
    st.info("새 비밀번호를 입력해 주세요.")
    with st.form("recovery_password_form"):
        new_password = st.text_input("새 비밀번호", type="password", placeholder="6자 이상")
        confirm = st.text_input("새 비밀번호 확인", type="password")
        submit = st.form_submit_button("비밀번호 변경", type="primary", use_container_width=True)

    if submit:
        if not new_password or not confirm:
            st.error("비밀번호를 입력해 주세요.")
        elif new_password != confirm:
            st.error("비밀번호 확인이 일치하지 않습니다.")
        elif len(new_password) < 6:
            st.error("비밀번호는 최소 6자 이상이어야 합니다.")
        else:
            ok, msg = auth_service.reset_password_in_recovery_session(new_password)
            if ok:
                st.session_state.pop("recovery_session_ready", None)
                st.success(msg)
                if st.button("로그인하러 가기"):
                    st.switch_page("pages/01_auth.py")
            else:
                st.error(msg)
else:
    st.markdown(
        "이메일로 받은 **인증 코드**와 **새 비밀번호**로 재설정할 수 있습니다. "
        "메일의 링크가 앱으로 연결되면 자동으로 재설정 화면이 열립니다."
    )

    with st.form("otp_recovery_form"):
        email = st.text_input("가입 이메일", placeholder="example@domain.com").strip()
        token = st.text_input(
            "인증 코드",
            placeholder="이메일에 포함된 코드",
            help="재설정 메일 본문 또는 링크 URL의 token 값",
        ).strip()
        new_password = st.text_input("새 비밀번호", type="password")
        confirm = st.text_input("새 비밀번호 확인", type="password")
        submit_otp = st.form_submit_button("비밀번호 변경", type="primary", use_container_width=True)

    if submit_otp:
        if not email or not token or not new_password or not confirm:
            st.error("모든 항목을 입력해 주세요.")
        elif new_password != confirm:
            st.error("비밀번호 확인이 일치하지 않습니다.")
        elif len(new_password) < 6:
            st.error("비밀번호는 최소 6자 이상이어야 합니다.")
        else:
            ok, msg = auth_service.reset_password_with_token(email, token, new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

st.divider()
if st.button("← 로그인 화면으로"):
    st.switch_page("pages/01_auth.py")
