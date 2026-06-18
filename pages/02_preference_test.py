import streamlit as st

from services.recommendation_service import run_full_recommendation_flow
from utils.constants import NOTE_TYPE_OPTIONS
from utils.session import has_auth, init_session, current_user_id

# --- [1. 페이지 설정 및 가드] ---
st.set_page_config(
    page_title="향수 취향 탐색",
    page_icon="🧪",
    layout="centered"
)
init_session()

if not has_auth():
    st.warning("로그인 또는 비회원 시작이 필요한 페이지입니다.")
    st.switch_page("pages/01_auth.py")

st.title("🧪 나만의 향수 취향 탐색")
st.caption("원하는 향조 버튼을 누른 후 다음 단계로 진행하세요.")
st.divider()

# --- [2. 데이터 및 상수가 정의된 구역] ---
SCENT_DATA = {
    "시트러스": ["레몬", "오렌지", "자몽", "베르가못"],
    "그린": ["풀잎", "대나무", "녹차", "무화과 잎"],
    "프루티": ["복숭아", "사과", "배", "베리"],
    "플로럴": ["장미", "자스민", "백합", "일랑일랑"],
    "머스크": ["화이트 머스크", "클린 머스크", "앰버 머스크", "파우더리 머스크"],
    "아쿠아틱": ["씨솔트", "워터", "오존", "마린노트"],
    "구르망": ["바닐라", "초콜릿", "캐러멜", "커피"],
    "오리엔탈": ["앰버", "인센스", "스파이스", "레진"],
    "우디": ["샌달우드", "시더우드", "베티버", "패출리"]
}

SUB_CATEGORY_ORDER = ["머스크", "시트러스", "오리엔탈", "그린", "아쿠아틱", "우디", "프루티", "플로럴", "구르망"]

current_step = st.session_state.get("pref_step", 1)

st.progress(current_step / 4)
st.markdown(f"**진행 단계: {current_step} / 4**")
st.write("")


# ==========================================
# [STEP 1] 주향 선택
# ==========================================
if current_step == 1:
    st.markdown("### 1. 가장 선호하는 주향을 고르세요")
    
    main_categories = list(SCENT_DATA.keys())
    if "tmp_selected_main" not in st.session_state:
        st.session_state["tmp_selected_main"] = main_categories[0]
        
    current_selected = st.session_state["tmp_selected_main"]
    
    for i in range(0, len(main_categories), 3):
        row_categories = main_categories[i:i+3]
        cols = st.columns(3)
        for idx, cat in enumerate(row_categories):
            with cols[idx]:
                btn_type = "primary" if cat == current_selected else "secondary"
                if st.button(f"{cat}", type=btn_type, use_container_width=True, key=f"btn_{cat}"):
                    st.session_state["tmp_selected_main"] = cat
                    st.rerun()

    st.markdown(f"🎯 현재 선택된 향조: **{st.session_state['tmp_selected_main']}**")
    st.write("")
    
    if st.button("다음 단계로 ➡️", type="primary", use_container_width=True, key="next_1"):
        st.session_state["pref_main_category"] = st.session_state["tmp_selected_main"]
        st.session_state["pref_step"] = 2
        st.session_state["perf_result_ready"] = False # 단계를 이동하면 이전 결과 초기화
        if "tmp_selected_main" in st.session_state:
            del st.session_state["tmp_selected_main"]
        st.rerun()


# ==========================================
# [STEP 2] 세부향 선택
# ==========================================
elif current_step == 2:
    chosen_main = st.session_state.get("pref_main_category", "시트러스")
    st.markdown(f"### 2. '{chosen_main}' 계열의 세부향을 선택하세요")
    
    detail_options = SCENT_DATA.get(chosen_main, [])
    if "tmp_selected_detail" not in st.session_state:
        st.session_state["tmp_selected_detail"] = detail_options[0]
        
    current_selected_detail = st.session_state["tmp_selected_detail"]
    
    for i in range(0, len(detail_options), 2):
        row_details = detail_options[i:i+2]
        cols = st.columns(2)
        for idx, det in enumerate(row_details):
            with cols[idx]:
                btn_type = "primary" if det == current_selected_detail else "secondary"
                if st.button(f"{det}", type=btn_type, use_container_width=True, key=f"btn_det_{det}"):
                    st.session_state["tmp_selected_detail"] = det
                    st.rerun()
                    
    st.markdown(f"🎯 현재 선택된 세부향: **{st.session_state['tmp_selected_detail']}**")
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전으로", use_container_width=True, key="prev_2"):
            st.session_state["pref_step"] = 1
            st.session_state["perf_result_ready"] = False
            if "tmp_selected_detail" in st.session_state:
                del st.session_state["tmp_selected_detail"]
            st.rerun()
    with col2:
        if st.button("다음 단계로 ➡️", type="primary", use_container_width=True, key="next_2"):
            st.session_state["pref_main_scent"] = st.session_state["tmp_selected_detail"]
            st.session_state["pref_step"] = 3
            st.session_state["perf_result_ready"] = False
            if "tmp_selected_detail" in st.session_state:
                del st.session_state["tmp_selected_detail"]
            st.rerun()


# ==========================================
# [STEP 3] 발향시점 선택
# ==========================================
elif current_step == 3:
    st.markdown("### 3. 주향이 언제 가장 돋보이기를 원하시나요?")
    
    options_map = {label: key for key, label in NOTE_TYPE_OPTIONS}
    labels_list = list(options_map.keys())
    
    if "tmp_selected_label" not in st.session_state:
        st.session_state["tmp_selected_label"] = labels_list[0]
        
    current_selected_label = st.session_state["tmp_selected_label"]
    
    cols = st.columns(3)
    for idx, label in enumerate(labels_list):
        with cols[idx]:
            s_key = label.split(' ')[0]
            btn_type = "primary" if label == current_selected_label else "secondary"
            if st.button(f"{label}", type=btn_type, use_container_width=True, key=f"btn_lbl_{s_key}"):
                st.session_state["tmp_selected_label"] = label
                st.rerun()
                
    st.markdown(f"🎯 현재 선택된 발향시점: **{st.session_state['tmp_selected_label']}**")
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전으로", use_container_width=True, key="prev_3"):
            st.session_state["pref_step"] = 2
            st.session_state["perf_result_ready"] = False
            if "tmp_selected_label" in st.session_state:
                del st.session_state["tmp_selected_label"]
            st.rerun()
    with col2:
        if st.button("다음 단계로 ➡️", type="primary", use_container_width=True, key="next_3"):
            st.session_state["pref_note_type"] = options_map[st.session_state["tmp_selected_label"]]
            st.session_state["pref_step"] = 4
            st.session_state["perf_result_ready"] = False
            if "tmp_selected_label" in st.session_state:
                del st.session_state["tmp_selected_label"]
            st.rerun()


# ==========================================
# [STEP 4] 보조향 선택 및 결과 하단 노출 구역
# ==========================================
elif current_step == 4:
    chosen_main = st.session_state.get("pref_main_category", "시트러스")
    st.markdown("### 4. 향을 다채롭게 채워줄 보조향을 선택하세요")
    
    available_subs = [cat for cat in SUB_CATEGORY_ORDER if cat != chosen_main]
    st.info(f"현재 주향으로 **[{chosen_main}]**을 선택하셨기 때문에, 보조향 옵션에서 제외되었습니다.")
    
    if "tmp_selected_sub" not in st.session_state:
        st.session_state["tmp_selected_sub"] = available_subs[0]
        
    current_selected_sub = st.session_state["tmp_selected_sub"]
    
    for i in range(0, len(available_subs), 4):
        row_subs = available_subs[i:i+4]
        cols = st.columns(4)
        for idx, sub in enumerate(row_subs):
            with cols[idx]:
                btn_type = "primary" if sub == current_selected_sub else "secondary"
                if st.button(f"{sub}", type=btn_type, use_container_width=True, key=f"btn_sub_{sub}"):
                    st.session_state["tmp_selected_sub"] = sub
                    # 버튼을 새로 골랐을 때 기존 연산 결과를 닫아 자연스러운 재출력을 유도합니다
                    st.session_state["perf_result_ready"] = False 
                    st.rerun()
                    
    st.markdown(f"🎯 현재 선택된 보조향: **{st.session_state['tmp_selected_sub']}**")
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전으로", use_container_width=True, key="prev_4"):
            st.session_state["pref_step"] = 3
            st.session_state["perf_result_ready"] = False
            if "tmp_selected_sub" in st.session_state:
                del st.session_state["tmp_selected_sub"]
            st.rerun()
            
    with col2:
        if st.button("추천 결과 보기 🎯", type="primary", use_container_width=True, key="submit_pref"):
            st.session_state["pref_additional_categories"] = [st.session_state["tmp_selected_sub"]]
            
            with st.spinner("선택하신 노트를 바탕으로 가중치 점수를 연산하고 있습니다..."):
                try:
                    # 백엔드 핵심 추천 로직 연산 가동
                    test_id, recommendations = run_full_recommendation_flow(
                        category_id=1,
                        scent_id=1,
                        preferred_note_type=st.session_state["pref_note_type"],
                        additional_category_ids=[2],
                        user_id=current_user_id()
                    )
                    
                    st.session_state["test_id"] = test_id
                    st.session_state["recommendations"] = recommendations
                    
                    # ✨ 페이지를 이동하지 않고 하단에 바로 그리도록 지시하는 트리거 플래그 활성화!
                    st.session_state["perf_result_ready"] = True
                    
                except Exception as e:
                    st.error(f"추천 연산 중 오류가 발생했습니다: {e}")
                    st.session_state["perf_result_ready"] = False

    # 🌟 [결과 실시간 출력 컨테이너] 
    # 결과 보기 버튼을 클릭하여 플래그가 True가 되면, 아래 구역에 UI가 동적으로 이어져 나타납니다.
    if st.session_state.get("perf_result_ready", False):
        st.divider()
        st.success("🎉 분석이 완료되었습니다! 당신을 위한 맞춤 향수 목록입니다.")
        
        recs = st.session_state.get("recommendations", [])
        
        if not recs:
            st.info("조건에 일치하는 매칭 향수 데이터가 데이터베이스에 존재하지 않습니다.")
        else:
            # 받아온 향수 데이터를 하단에 예쁘게 카드 형태로 출력하는 커스텀 결과 레이아웃 구역
            for idx, perfume in enumerate(recs):
                # 가상의 인덱스 대응용 키 분리 규칙 적용 (가져오는 객체 구조에 맞춤)
                p_name = perfume.get("name", f"추천 향수 제품 {idx+1}")
                p_brand = perfume.get("brand", "프리미엄 퍼퓸 하우스")
                p_desc = perfume.get("description", "당신의 선호 취향 노트를 조화롭게 매칭한 매력적인 향수입니다.")
                p_score = perfume.get("score", 95)
                
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.subheader(f"{idx+1}. {p_name}")
                        st.caption(f"브랜드: {p_brand}")
                        st.write(p_desc)
                    with c2:
                        st.metric(label="매칭도", value=f"{p_score}점")