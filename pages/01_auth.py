import streamlit as st

from services import auth_service
from utils.session import clear_auth, has_auth, init_session, set_guest, set_member

st.set_page_config(page_title="로그인", layout="centered")
init_session()

if has_auth():
    st.switch_page("pages/02_preference_test.py")

st.title("시작하기")
st.markdown("비회원은 **추천만** 이용 가능합니다. 즐겨찾기·이전 기록·Google 검색은 **회원 전용**입니다.")

tab_guest, tab_login, tab_signup = st.tabs(["비회원", "로그인", "회원가입"])

with tab_guest:
    st.info("로그인 없이 바로 취향 테스트를 진행합니다.")
    if st.button("비회원으로 시작", type="primary", use_container_width=True):
        set_guest()
        st.switch_page("pages/02_preference_test.py")

with tab_login:
    login_email = st.text_input("이메일", key="login_email")
    login_password = st.text_input("비밀번호", type="password", key="login_password")
    st.caption("비밀번호는 6자 이상이어야 합니다.")
    if st.button("로그인", type="primary", use_container_width=True):
        if not login_email or not login_password:
            st.error("이메일과 비밀번호를 입력해 주세요.")
        else:
            try:
                result = auth_service.sign_in(login_email, login_password)
                set_member(
                    user_id=result["user_id"],
                    email=result["email"],
                    nickname=result["nickname"],
                    access_token=result["access_token"],
                    refresh_token=result["refresh_token"],
                )
                st.switch_page("pages/02_preference_test.py")
            except Exception as exc:
                st.error(f"로그인 실패: {exc}")

with tab_signup:
    signup_email = st.text_input("이메일", key="signup_email")
    signup_nickname = st.text_input("닉네임", key="signup_nickname")
    signup_password = st.text_input("비밀번호", type="password", key="signup_password")
    signup_password2 = st.text_input("비밀번호 확인", type="password", key="signup_password2")
    st.caption("비밀번호는 6자 이상으로 입력해 주세요.")
    if st.button("회원가입", type="primary", use_container_width=True):
        if not all([signup_email, signup_nickname, signup_password, signup_password2]):
            st.error("모든 항목을 입력해 주세요.")
        elif signup_password != signup_password2:
            st.error("비밀번호가 일치하지 않습니다.")
        elif len(signup_password) < 6:
            st.error("비밀번호는 6자 이상이어야 합니다.")
        else:
            try:
                result = auth_service.sign_up(signup_email, signup_password, signup_nickname)
                if result["access_token"]:
                    set_member(
                        user_id=result["user_id"],
                        email=result["email"],
                        nickname=result["nickname"],
                        access_token=result["access_token"],
                        refresh_token=result["refresh_token"],
                    )
                    st.switch_page("pages/02_preference_test.py")
                else:
                    st.success("가입이 완료되었습니다. 이메일 인증 후 로그인해 주세요.")
            except Exception as exc:
                st.error(f"회원가입 실패: {exc}")

if st.button("홈으로"):
    clear_auth()
    st.switch_page("app.py")
