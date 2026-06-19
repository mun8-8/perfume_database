from datetime import datetime

import streamlit as st

from database.repositories import (
    favorite_repository,
    history_repository,
    user_repository,
)
from database.supabase_client import ensure_authenticated_session
from services.auth_service import auth_service
from utils.session import clear_auth, clear_test_session, init_session, is_logged_in
from utils.theme import apply_page_theme
from utils.ui_helpers import (
    inject_history_date_styles,
    render_favorite_list_item,
    render_history_recommendations,
    toggle_history_test,
)

st.set_page_config(page_title="프로필", layout="wide")
init_session()
apply_page_theme()

if not is_logged_in():
    st.warning("프로필은 로그인한 회원만 이용할 수 있습니다.")
    if st.button("로그인하기"):
        st.switch_page("pages/01_auth.py")
    st.stop()

ensure_authenticated_session()
user_id = st.session_state["user_id"]

header_cols = st.columns([5, 1])
with header_cols[0]:
    st.title("내 프로필")
with header_cols[1]:
    if st.button("홈"):
        st.switch_page("app.py")

try:
    profile = user_repository.get_user(user_id)
except Exception as exc:
    st.error(f"프로필 조회 실패: {exc}")
    profile = None

nickname = (profile or {}).get("nickname") or st.session_state.get("user_nickname", "")
email = (profile or {}).get("email") or st.session_state.get("user_email", "")

st.subheader("계정 정보")
st.write(f"**닉네임:** {nickname}")
st.write(f"**이메일:** {email}")

with st.expander("닉네임 변경", expanded=False):
    with st.form("change_nickname_form"):
        new_nickname = st.text_input(
            "새 닉네임",
            value=nickname,
            placeholder="앱에서 표시될 이름",
            max_chars=100,
        ).strip()
        submit_nick = st.form_submit_button("닉네임 저장", use_container_width=True)

    if submit_nick:
        if not new_nickname:
            st.error("닉네임을 입력해 주세요.")
        elif new_nickname == nickname:
            st.info("변경된 내용이 없습니다.")
        else:
            ok, msg = auth_service.change_nickname(new_nickname)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

with st.expander("비밀번호 변경", expanded=False):
    st.caption("로그인 상태에서 이메일 인증 없이 변경할 수 있습니다.")
    with st.form("change_password_form"):
        new_password = st.text_input("새 비밀번호", type="password", placeholder="6자 이상")
        confirm_password = st.text_input("새 비밀번호 확인", type="password")
        submit_pw = st.form_submit_button("비밀번호 변경", use_container_width=True)

    if submit_pw:
        if not new_password or not confirm_password:
            st.error("새 비밀번호를 입력해 주세요.")
        elif new_password != confirm_password:
            st.error("비밀번호 확인이 일치하지 않습니다.")
        elif len(new_password) < 6:
            st.error("비밀번호는 최소 6자 이상이어야 합니다.")
        else:
            ok, msg = auth_service.change_password(new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

st.divider()
st.subheader("즐겨찾기")

try:
    favorites = favorite_repository.list_saved_perfumes(user_id)
except Exception as exc:
    st.error(f"즐겨찾기 조회 실패: {exc}")
    favorites = []

if not favorites:
    st.caption("저장한 향수가 없습니다.")
else:
    for item in favorites:
        perfume = item.get("perfumes") or {}
        perfume_id = perfume.get("perfume_id")
        name = perfume.get("perfume_name", "이름 없음")
        brand = perfume.get("brand_name", "")
        render_favorite_list_item(
            perfume_id, name, brand, user_id, key_prefix=f"fav_{perfume_id}"
        )

st.divider()
st.subheader("이전 추천 결과")

view_test_id = st.session_state.get("view_history_test_id")

try:
    tests = history_repository.list_user_tests(user_id)
except Exception as exc:
    st.error(f"이력 조회 실패: {exc}")
    tests = []

if not tests:
    st.caption("이전 추천 기록이 없습니다.")
else:
    inject_history_date_styles()
    saved_ids = favorite_repository.get_saved_perfume_ids(user_id)

    for test in tests:
        test_id = test["test_id"]
        created_at = test.get("created_at", "")
        try:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            date_label = dt.strftime("%Y.%m.%d. %H.%M")
        except (ValueError, AttributeError):
            date_label = str(created_at)

        summary = history_repository.get_test_summary(test_id)
        summary_line = summary["summary_line"] if summary else "선택 정보 없음"
        is_open = view_test_id == test_id

        with st.container(border=True):
            header_cols = st.columns([11, 1])
            with header_cols[0]:
                if st.button(
                    date_label,
                    key=f"hist_date_{test_id}",
                    type="tertiary",
                    help="클릭하면 추천 향수를 펼칩니다",
                ):
                    toggle_history_test(test_id)
                    st.rerun()
            with header_cols[1]:
                toggle_icon = "▲" if is_open else "▼"
                toggle_help = "추천 향수 접기" if is_open else "추천 향수 펼치기"
                if st.button(
                    toggle_icon,
                    key=f"hist_toggle_{test_id}",
                    type="tertiary",
                    help=toggle_help,
                ):
                    toggle_history_test(test_id)
                    st.rerun()

            st.write(summary_line)

            if is_open:
                render_history_recommendations(test_id, user_id, saved_ids)
                if st.button(
                    "▲",
                    key=f"hist_collapse_{test_id}",
                    type="tertiary",
                    help="추천 향수 접기",
                ):
                    st.session_state["view_history_test_id"] = None
                    st.rerun()

st.divider()
if st.button("로그아웃", type="primary"):
    auth_service.sign_out(
        st.session_state.get("access_token"),
        st.session_state.get("refresh_token"),
    )
    clear_auth()
    clear_test_session()
    st.switch_page("app.py")
