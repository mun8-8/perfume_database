import streamlit as st

from utils.session import has_auth, init_session, is_logged_in
from utils.theme import apply_page_theme

st.set_page_config(
    page_title="향수 취향 탐색",
    page_icon="🌸",
    layout="wide",
)
init_session()
apply_page_theme()

st.markdown("## 나만의 향수 추천")
st.markdown(
    "주향과 세부향을 고르면 성향에 맞는 향수를 추천해드려요."
)
st.divider()

left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.markdown("### 향수 추천 시작")
        st.caption("비회원/회원 모두 가능")
        st.write("주향 → 세부향 → 발향시점 → 보조향 순서로 진행합니다.")
        if st.button("추천 시작하기", type="primary", use_container_width=True):
            if has_auth():
                st.switch_page("pages/02_preference_test.py")
            else:
                st.switch_page("pages/01_auth.py")

with right:
    with st.container(border=True):
        st.markdown("### 내 프로필")
        st.caption("회원 전용")
        st.write("즐겨찾기, 이전 추천 기록, 로그아웃을 관리합니다.")
        
        # 💡 [요구사항 반영]: 로그인 여부에 따라 버튼의 액션을 다르게 처리
        if is_logged_in():
            if st.button("프로필 열기", use_container_width=True):
                st.switch_page("pages/04_profile.py")
        else:
            # 로그인이 안 되어 있을 때도 버튼을 누를 수 있게 만들고, 누르면 로그인 창으로 연동
            if st.button("로그인 후 이용 가능 (로그인하러 가기)", type="secondary", use_container_width=True):
                st.switch_page("pages/01_auth.py")

if has_auth():
    mode = "회원" if is_logged_in() else "비회원"
    st.caption(f"현재 접속 상태: {mode}")
    if st.button("다른 계정으로 시작"):
        from utils.session import start_with_different_account

        start_with_different_account()
        st.rerun()

with st.expander("개발/실행 정보"):
    st.code(
        """pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml 에 Supabase URL/KEY 입력
streamlit run app.py""",
        language="bash",
    )
    st.markdown(
        "Supabase SQL Editor에서 `sql/nine_categories_seed.sql`, "
        "`sql/recommendation_scoring.sql`을 실행하세요."
    )

with st.expander("환경 진단"):
    from database.supabase_client import get_supabase

    if st.button("진단 실행"):
        url_ok = False
        key_ok = False
        try:
            url_ok = bool(st.secrets.get("SUPABASE_URL"))
            key_ok = bool(st.secrets.get("SUPABASE_KEY"))
        except Exception:
            st.error(".streamlit/secrets.toml 파일을 읽지 못했습니다.")
            st.stop()

        st.write(f"- SUPABASE_URL 설정: {'OK' if url_ok else '누락'}")
        st.write(f"- SUPABASE_KEY 설정: {'OK' if key_ok else '누락'}")

        if url_ok and key_ok:
            try:
                get_supabase().table("scent_categories").select("category_id").limit(1).execute()
                st.success("Supabase 연결 성공")
            except Exception as exc:
                st.error(f"Supabase 연결 실패: {exc}")