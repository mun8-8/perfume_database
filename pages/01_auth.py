import streamlit as st

from services.auth_service import auth_service
from utils.session import has_auth, init_session, set_guest, set_member

# --- [초기 설정] ---
st.set_page_config(
    page_title="인증 및 시작하기",
    page_icon="🔐",
    layout="centered",
)
init_session()

# 안전장치: 이미 인증 세션이 활성화되어 있다면 곧바로 3번(주향 선택) 단계로 리다이렉트
if has_auth():
    st.switch_page("pages/02_preference_test.py")

st.title("🔑 시작하기")
st.markdown(
    "향수 취향 탐색을 시작합니다. 회원으로 가입하시면 **즐겨찾기 보관** 및 "
    "**과거 추천 이력 조회** 기능을 제공받으실 수 있습니다."
)
st.divider()

# --- [2번 기능: 탭 UI 구성] ---
tab_guest, tab_login, tab_signup = st.tabs(["💡 비회원 시작", "🔓 로그인", "📝 회원가입"])

# ==========================================
# 1. 비회원 시작 탭
# ==========================================
with tab_guest:
    st.markdown("### 계정 없이 바로 추천받기")
    st.info(
        "비회원으로 진행 시 취향 분석 및 향수 추천은 동일하게 작동하나, "
        "결과 화면에서의 **즐겨찾기(★)** 기능과 **마이페이지 이력 저장**이 제한됩니다."
    )
    
    # 기획안 연계: 버튼 클릭 즉시 세션을 guest로 굽고 설문(주향 선택) 페이지로 강제 라우팅
    if st.button("비회원으로 추천 시작하기", type="secondary", use_container_width=True):
        set_guest()
        st.success("비회원 모드로 진입합니다. 주향 선택 페이지로 이동합니다.")
        st.switch_page("pages/02_preference_test.py")


# ==========================================
# 2. 로그인 탭
# ==========================================
with tab_login:
    st.markdown("### 회원 로그인")
    
    # st.form을 사용하여 입력값 제출 시 매끄러운 트랜잭션 보장
    with st.form("login_container", clear_on_submit=False):
        login_email = st.text_input(
            "이메일 주소", 
            placeholder="example@domain.com"
        ).strip()
        
        login_password = st.text_input(
            "비밀번호", 
            type="password", 
            placeholder="비밀번호를 입력하세요"
        ).strip()
        
        submit_login = st.form_submit_button("로그인 후 시작하기", type="primary", use_container_width=True)

    if submit_login:
        if not login_email or not login_password:
            st.error("이메일과 비밀번호를 모두 정확히 입력해 주세요.")
        else:
            with st.spinner("사용자 정보를 확인하고 있습니다..."):
                # auth_service 인스턴스를 통해 백엔드(Supabase GoTrue) 검증 진행
                success, user_info, error_msg = auth_service.login_user(login_email, login_password)
                
                if success and user_info:
                    # 기획안 연계: 로그인 성공 시 세션에 유저의 고유 메타데이터 주입
                    set_member(
                        user_id=user_info["user_id"],
                        email=user_info["email"],
                        nickname=user_info["nickname"],
                        access_token=user_info["access_token"],
                        refresh_token=user_info["refresh_token"]
                    )
                    st.success(f"🎉 {user_info['nickname']}님 환영합니다! 취향 분석 페이지로 이동합니다.")
                    st.switch_page("pages/02_preference_test.py")
                else:
                    st.error(error_msg or "이메일 또는 비밀번호가 올바르지 않습니다. 다시 시도해 주세요.")


# ==========================================
# 3. 회원가입 탭
# ==========================================
with tab_signup:
    st.markdown("### 새 계정 생성")
    st.caption("간단한 정보 입력으로 회원 전용 기능을 무제한 이용해 보세요.")
    
    with st.form("signup_container", clear_on_submit=False):
        new_email = st.text_input(
            "이메일 주소 *", 
            placeholder="사용하실 이메일을 입력하세요"
        ).strip()
        
        new_nickname = st.text_input(
            "닉네임 *", 
            placeholder="앱에서 사용될 이메일/프로필용 닉네임"
        ).strip()
        
        new_password = st.text_input(
            "비밀번호 *", 
            type="password", 
            placeholder="최소 6자 이상의 안전한 비밀번호"
        ).strip()
        
        confirm_password = st.text_input(
            "비밀번호 확인 *", 
            type="password", 
            placeholder="비밀번호를 한 번 더 입력하세요"
        ).strip()
        
        submit_signup = st.form_submit_button("가입 완료하고 로그인하러 가기", use_container_width=True)

    if submit_signup:
        # 필수 필드 유효성 검증
        if not new_email or not new_nickname or not new_password or not confirm_password:
            st.error("모든 필수 입력 항목(*)을 입력해야 합니다.")
        elif new_password != confirm_password:
            st.error("비밀번호 확인 칸의 입력값이 일치하지 않습니다.")
        elif len(new_password) < 6:
            st.error("안전을 위해 비밀번호는 최소 6자 이상으로 설정해 주세요.")
        else:
            with st.spinner("Supabase 계정을 생성하는 중..."):
                # auth_service를 거쳐 인증 메인 스키마 및 public.users 테이블에 프로필 적재
                success, message = auth_service.register_user(
                    email=new_email,
                    password=new_password,
                    nickname=new_nickname
                )
                
                if success:
                    st.success(f"✨ {message}")
                else:
                    st.error(message)