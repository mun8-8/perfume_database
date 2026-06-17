from datetime import datetime

import streamlit as st

from database.repositories import (
    favorite_repository,
    history_repository,
    perfume_repository,
    recommendation_repository,
    user_repository,
)
from services import auth_service
from utils.session import clear_auth, init_session, is_logged_in

st.set_page_config(page_title="프로필", layout="wide")
init_session()

if not is_logged_in():
    st.warning("프로필은 로그인한 회원만 이용할 수 있습니다.")
    if st.button("로그인하기"):
        st.switch_page("pages/01_auth.py")
    st.stop()

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

        with st.container(border=True):
            cols = st.columns([5, 1, 1])
            with cols[0]:
                st.markdown(f"**{name}**")
                if brand:
                    st.caption(brand)
            with cols[1]:
                url = perfume_repository.google_search_url(name, brand)
                st.link_button("검색", url)
            with cols[2]:
                if perfume_id and st.button("☆", key=f"unsave_{perfume_id}"):
                    favorite_repository.remove_saved_perfume(user_id, perfume_id)
                    st.rerun()

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

        row_cols = st.columns([4, 1])
        with row_cols[0]:
            st.markdown(f"**{date_label}**")
            st.write(summary_line)
        with row_cols[1]:
            if st.button("결과 보기", key=f"hist_{test_id}"):
                st.session_state["view_history_test_id"] = test_id
                st.rerun()

if view_test_id:
    st.markdown("---")
    st.markdown("#### 해당 시점 추천 향수")
    summary = history_repository.get_test_summary(view_test_id)
    if summary:
        st.write(summary["summary_line"])

    try:
        rows = recommendation_repository.get_recommendations_by_test(view_test_id)
    except Exception as exc:
        st.error(f"추천 결과 조회 실패: {exc}")
        rows = []

    saved_ids = favorite_repository.get_saved_perfume_ids(user_id)
    for idx, row in enumerate(rows, start=1):
        perfume = row.get("perfumes") or {}
        score = row.get("recommendation_score", 0)
        name = perfume.get("perfume_name", "이름 없음")
        brand = perfume.get("brand_name", "")
        perfume_id = perfume.get("perfume_id")

        with st.container(border=True):
            st.markdown(f"**{idx}. {name}**")
            if brand:
                st.caption(brand)
            st.metric("추천 점수", score)
            if perfume_id:
                cols = st.columns([1, 1])
                with cols[0]:
                    st.link_button(
                        "Google 검색",
                        perfume_repository.google_search_url(name, brand),
                        key=f"hist_search_{view_test_id}_{perfume_id}",
                    )
                with cols[1]:
                    is_saved = perfume_id in saved_ids
                    if st.button(
                        "★" if is_saved else "☆",
                        key=f"hist_fav_{view_test_id}_{perfume_id}",
                    ):
                        if is_saved:
                            favorite_repository.remove_saved_perfume(user_id, perfume_id)
                        else:
                            favorite_repository.save_perfume(user_id, perfume_id)
                        st.rerun()

    if st.button("이력 상세 닫기"):
        st.session_state.pop("view_history_test_id", None)
        st.rerun()

st.divider()
if st.button("로그아웃", type="primary"):
    auth_service.sign_out(
        st.session_state.get("access_token"),
        st.session_state.get("refresh_token"),
    )
    clear_auth()
    st.session_state.pop("test_id", None)
    st.session_state.pop("recommendations", None)
    st.session_state.pop("test_summary", None)
    st.session_state.pop("view_history_test_id", None)
    st.switch_page("app.py")
