import streamlit as st

from database.repositories import favorite_repository, recommendation_repository
from utils.session import has_auth, init_session, is_logged_in
from utils.ui_helpers import render_perfume_card, render_profile_button

st.set_page_config(page_title="추천 결과", layout="wide")
init_session()

if not has_auth():
    st.switch_page("pages/01_auth.py")

header_cols = st.columns([5, 1])
with header_cols[0]:
    st.title("추천 결과 Top 5")
with header_cols[1]:
    render_profile_button("result")

test_id = st.session_state.get("test_id")
summary = st.session_state.get("test_summary")

if test_id is None:
    st.info("먼저 취향 테스트를 진행해 주세요.")
    if st.button("취향 테스트로 이동"):
        st.switch_page("pages/02_preference_test.py")
    st.stop()

if summary:
    add_text = ", ".join(summary["additional_categories"]) if summary["additional_categories"] else "없음"
    st.markdown(
        f"**{summary['main_category']}** - {summary['main_scent']} "
        f"({summary['note_label']}) / 보조: {add_text}"
    )

try:
    rows = recommendation_repository.get_recommendations_by_test(test_id)
except Exception as exc:
    st.error(f"결과 조회 실패: {exc}")
    rows = []

if not rows:
    cached = st.session_state.get("recommendations")
    if cached:
        st.warning("DB 조회에 실패해 세션 데이터를 표시합니다.")
        for item in cached:
            st.write(f"향수 ID {item['perfume_id']} — 점수 {item['recommendation_score']}")
    else:
        st.warning("저장된 추천 결과가 없습니다.")
    st.stop()

saved_ids: set[int] = set()
if is_logged_in():
    try:
        saved_ids = favorite_repository.get_saved_perfume_ids(st.session_state["user_id"])
    except Exception:
        pass

member_features = is_logged_in()

for idx, row in enumerate(rows, start=1):
    perfume = row.get("perfumes") or {}
    score = row.get("recommendation_score", 0)
    render_perfume_card(
        rank=idx,
        perfume=perfume,
        score=score,
        saved_ids=saved_ids,
        key_prefix=f"result_{test_id}",
        show_search=member_features,
        show_favorite=member_features,
    )

if not member_features:
    st.info("비회원은 추천 결과만 볼 수 있습니다. 즐겨찾기·Google 검색·이전 기록은 회원 전용입니다.")

st.divider()
if st.button("다시 테스트하기"):
    st.session_state.pop("test_id", None)
    st.session_state.pop("recommendations", None)
    st.session_state.pop("test_summary", None)
    st.switch_page("pages/02_preference_test.py")
