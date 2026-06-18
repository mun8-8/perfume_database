import streamlit as st

from services.recommendation_service import run_full_recommendation_flow
from database.repositories import favorite_repository, perfume_repository
from utils.constants import (
    NOTE_TYPE_DESCRIPTIONS,
    NOTE_TYPE_ENGLISH_LABELS,
    NOTE_TYPE_LABELS,
    NOTE_TYPE_OPTIONS,
)
from utils.scent_descriptions import (
    CATEGORY_DESCRIPTIONS,
    CATEGORY_ENGLISH_LABELS,
    SCENT_DESCRIPTIONS,
    SUB_CATEGORY_DESCRIPTIONS,
    scent_english_label,
)
from utils.scent_theme import CATEGORY_SLUG, detail_slug
from utils.session import has_auth, init_session, current_user_id, is_logged_in, reset_preference_wizard
from utils.theme import apply_page_theme
from utils.recommendation_reasons import build_recommendation_reasons
from utils.ui_helpers import (
    render_favorite_star,
    render_profile_button,
    render_scent_description_panel,
    render_themed_choice_button,
)

# --- [1. 페이지 설정 및 가드] ---
st.set_page_config(
    page_title="향수 취향 탐색",
    page_icon="🧪",
    layout="centered"
)
init_session()
apply_page_theme()

if not has_auth():
    st.warning("로그인 또는 비회원 시작이 필요한 페이지입니다.")
    st.switch_page("pages/01_auth.py")

st.title("🧪 나만의 향수 취향 탐색")
st.caption("원하는 향조 버튼을 누른 후 다음 단계로 진행하세요.")
st.divider()

# --- [2. 기획안 데이터 세팅] ---
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

# 현재 단계를 제어합니다 (결과창은 5단계로 정의)
current_step = st.session_state.get("pref_step", 1)

# 질문 단계(1~4)일 때만 프로그레스 바를 노출하여 시각적 일관성을 유지합니다.
if current_step <= 4:
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
        st.session_state["tmp_selected_main"] = None

    current_selected = st.session_state["tmp_selected_main"]

    for i in range(0, len(main_categories), 3):
        row_categories = main_categories[i:i+3]
        cols = st.columns(3)
        for idx, cat in enumerate(row_categories):
            with cols[idx]:
                key = f"main_{CATEGORY_SLUG[cat]}"
                if render_themed_choice_button(
                    cat, key, cat, selected=(cat == current_selected)
                ):
                    st.session_state["tmp_selected_main"] = cat
                    st.rerun()

    if current_selected:
        render_scent_description_panel(
            f"현재 선택된 향조: {current_selected}",
            CATEGORY_DESCRIPTIONS.get(current_selected, []),
            current_selected,
            subtitle=CATEGORY_ENGLISH_LABELS.get(current_selected),
        )
    else:
        st.caption("아직 선택하지 않았습니다. 원하는 주향 버튼을 눌러 주세요.")
    st.write("")

    if st.button(
        "다음 단계로 ➡️",
        type="primary",
        use_container_width=True,
        key="next_1",
        disabled=not current_selected,
    ):
        st.session_state["pref_main_category"] = current_selected
        st.session_state["pref_step"] = 2
        st.session_state.pop("tmp_selected_main", None)
        st.rerun()


# ==========================================
# [STEP 2] 세부향 선택
# ==========================================
elif current_step == 2:
    chosen_main = st.session_state.get("pref_main_category")
    st.markdown(f"### 2. '{chosen_main}' 계열의 세부향을 선택하세요")

    detail_options = SCENT_DATA.get(chosen_main, [])
    if "tmp_selected_detail" not in st.session_state:
        st.session_state["tmp_selected_detail"] = None

    current_selected_detail = st.session_state["tmp_selected_detail"]

    for i in range(0, len(detail_options), 2):
        row_details = detail_options[i:i+2]
        cols = st.columns(2)
        for idx, det in enumerate(row_details):
            with cols[idx]:
                key = detail_slug(det)
                if render_themed_choice_button(
                    det, key, chosen_main, selected=(det == current_selected_detail)
                ):
                    st.session_state["tmp_selected_detail"] = det
                    st.rerun()

    if current_selected_detail:
        render_scent_description_panel(
            f"현재 선택된 세부향: {current_selected_detail}",
            SCENT_DESCRIPTIONS.get(current_selected_detail, []),
            chosen_main,
            subtitle=scent_english_label(current_selected_detail),
        )
    else:
        st.caption("아직 선택하지 않았습니다. 원하는 세부향 버튼을 눌러 주세요.")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전으로", use_container_width=True, key="prev_2"):
            st.session_state["pref_step"] = 1
            st.session_state.pop("pref_main_category", None)
            st.session_state.pop("tmp_selected_detail", None)
            st.rerun()
    with col2:
        if st.button(
            "다음 단계로 ➡️",
            type="primary",
            use_container_width=True,
            key="next_2",
            disabled=not current_selected_detail,
        ):
            st.session_state["pref_main_scent"] = current_selected_detail
            st.session_state["pref_step"] = 3
            st.session_state.pop("tmp_selected_detail", None)
            st.rerun()


# ==========================================
# [STEP 3] 발향시점 선택
# ==========================================
elif current_step == 3:
    st.markdown("### 3. 주향이 언제 가장 돋보이기를 원하시나요?")

    if "tmp_selected_note" not in st.session_state:
        st.session_state["tmp_selected_note"] = None

    current_selected_note = st.session_state["tmp_selected_note"]

    cols = st.columns(3)
    for idx, (note_key, label) in enumerate(NOTE_TYPE_OPTIONS):
        with cols[idx]:
            if render_themed_choice_button(
                label,
                f"note_{note_key}",
                note_key,
                selected=(note_key == current_selected_note),
                theme_map="note",
            ):
                st.session_state["tmp_selected_note"] = note_key
                st.rerun()

    if current_selected_note:
        render_scent_description_panel(
            f"현재 선택된 발향시점: {NOTE_TYPE_LABELS[current_selected_note]}",
            NOTE_TYPE_DESCRIPTIONS.get(current_selected_note, []),
            current_selected_note,
            theme_map="note",
            subtitle=NOTE_TYPE_ENGLISH_LABELS.get(current_selected_note),
        )
    else:
        st.caption("아직 선택하지 않았습니다. 원하는 발향 시점 버튼을 눌러 주세요.")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전으로", use_container_width=True, key="prev_3"):
            st.session_state["pref_step"] = 2
            st.session_state.pop("pref_main_scent", None)
            st.session_state.pop("tmp_selected_note", None)
            st.rerun()
    with col2:
        if st.button(
            "다음 단계로 ➡️",
            type="primary",
            use_container_width=True,
            key="next_3",
            disabled=not current_selected_note,
        ):
            st.session_state["pref_note_type"] = current_selected_note
            st.session_state["pref_step"] = 4
            st.session_state.pop("tmp_selected_note", None)
            st.rerun()


# ==========================================
# 🔄 [STEP 4] 보조향 선택 (추천 버튼 클릭 시 완벽 화면 전환)
# ==========================================
elif current_step == 4:
    chosen_main = st.session_state.get("pref_main_category")
    st.markdown("### 4. 향을 다채롭게 채워줄 보조향을 선택하세요")

    available_subs = [cat for cat in SUB_CATEGORY_ORDER if cat != chosen_main]
    st.info(f"현재 주향으로 **[{chosen_main}]**을 선택하셨기 때문에, 보조향 옵션에서 제외되었습니다.")

    if "tmp_selected_sub" not in st.session_state:
        st.session_state["tmp_selected_sub"] = None

    current_selected_sub = st.session_state["tmp_selected_sub"]

    for i in range(0, len(available_subs), 4):
        row_subs = available_subs[i:i+4]
        cols = st.columns(4)
        for idx, sub in enumerate(row_subs):
            with cols[idx]:
                key = f"sub_{CATEGORY_SLUG[sub]}"
                if render_themed_choice_button(
                    sub, key, sub, selected=(sub == current_selected_sub)
                ):
                    st.session_state["tmp_selected_sub"] = sub
                    st.rerun()

    if current_selected_sub:
        render_scent_description_panel(
            f"현재 선택된 보조향: {current_selected_sub}",
            SUB_CATEGORY_DESCRIPTIONS.get(current_selected_sub, []),
            current_selected_sub,
            subtitle=CATEGORY_ENGLISH_LABELS.get(current_selected_sub),
        )
    else:
        st.caption("아직 선택하지 않았습니다. 원하는 보조향 버튼을 눌러 주세요.")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 이전으로", use_container_width=True, key="prev_4"):
            st.session_state["pref_step"] = 3
            st.session_state.pop("pref_note_type", None)
            st.session_state.pop("tmp_selected_sub", None)
            st.rerun()

    with col2:
        if st.button(
            "추천 결과 보기 🎯",
            type="primary",
            use_container_width=True,
            key="submit_pref",
            disabled=not current_selected_sub,
        ):
            st.session_state["pref_additional_categories"] = [current_selected_sub]

            with st.spinner("선택하신 노트를 바탕으로 가중치 점수를 연산하고 있습니다..."):
                try:
                    # 백엔드 데이터베이스 호출 및 연산 가동
                    test_id, recommendations = run_full_recommendation_flow(
                        category_id=1,
                        scent_id=1,
                        preferred_note_type=st.session_state["pref_note_type"],
                        additional_category_ids=[2],
                        user_id=current_user_id()
                    )
                    
                    st.session_state["test_id"] = test_id
                    st.session_state["recommendations"] = recommendations
                    
                    # ✨ 성공 시 완전히 독립된 단계인 '5단계'로 세팅 후 화면 갱신!
                    st.session_state["pref_step"] = 5
                    if "tmp_selected_sub" in st.session_state:
                        del st.session_state["tmp_selected_sub"]
                    st.rerun()
                    
                except Exception as e:
                    # Supabase RLS 보안 에러 정책 위반 메시지를 유저 친화적으로 파싱하거나 우회 안내
                    if "row-level security" in str(e).lower():
                        st.error("🔒 데이터베이스 보안 정책(RLS) 에러가 발생했습니다. 현재 계정에 데이터 삽입 권한이 있는지 확인이 필요합니다.")
                    else:
                        st.error(f"추천 연산 중 오류가 발생했습니다: {e}")


# ==========================================
# 🌟 [STEP 5] 추천 결과 출력 화면 (기획안 반영)
# ==========================================
elif current_step == 5:
    header_cols = st.columns([5, 1])
    with header_cols[0]:
        st.markdown("### 🎯 당신을 위한 맞춤 향수 추천 결과")
    with header_cols[1]:
        render_profile_button("pref_result")

    summary = st.session_state.get("test_summary") or {}
    main_category = summary.get("main_category") or st.session_state.get("pref_main_category", "-")
    main_scent = summary.get("main_scent") or st.session_state.get("pref_main_scent", "-")
    note_type = summary.get("note_type") or st.session_state.get("pref_note_type", "")
    note_label = summary.get("note_label") or NOTE_TYPE_LABELS.get(note_type, note_type or "-")
    additional = summary.get("additional_categories") or st.session_state.get("pref_additional_categories") or []
    sub_category = ", ".join(additional) if additional else "없음"

    with st.container(border=True):
        st.markdown("**내 선택**")
        st.write(f"**주향:** {main_category}")
        st.write(f"**세부향:** {main_scent}")
        st.write(f"**발향 시점:** {note_label}")
        st.write(f"**보조향:** {sub_category}")

    # 백엔드 연산 도중 DB/네트워크 에러가 감지되었다면 디버깅 문구 노출
    db_err = st.session_state.get("db_error_msg", None)
    if db_err:
        st.warning("⚠️ 백엔드 서버(Supabase RPC) 연산 중 이슈가 발생했습니다. (데모용 가상 데이터를 대신 표시합니다.)")
        with st.expander("🛠️ 시스템 상세 에러 확인"):
            st.code(db_err)
    else:
        st.success("🎉 분석이 완료되었습니다! 당신의 선호도를 바탕으로 DB에서 실시간 집계된 결과입니다.")

    history_err = st.session_state.get("history_save_error")
    if history_err and is_logged_in():
        st.warning(
            "추천 이력을 DB에 저장하지 못했습니다. "
            "Supabase에서 `sql/member_data_rls.sql` 실행 후 다시 시도해 주세요."
        )
        with st.expander("이력 저장 오류 상세"):
            st.code(history_err)

    st.write("")
    
    recs = st.session_state.get("recommendations", [])
    reco_context = st.session_state.get("recommendation_context") or st.session_state.get("test_summary")

    show_reasons = st.checkbox(
        "추천 이유 보기",
        help="선택한 취향과 각 향수 노트가 어떻게 맞는지 표시합니다.",
        key="show_recommendation_reasons",
    )

    saved_ids: set[int] = set()
    if is_logged_in():
        try:
            saved_ids = favorite_repository.get_saved_perfume_ids(st.session_state["user_id"])
        except Exception:
            saved_ids = set()
    
    # 예외 상황이나 데이터가 없을 때 UI 전시용 샘플 데이터 (테스트용)
    if not recs:
        recs = [
            {"name": "블루 드 샤넬 (Bleu de Chanel)", "brand": "CHANEL", "description": "신선한 시트러스 덤불과 머스크 노트를 매칭하여 깊고 세련된 이미지를 선사하는 향수입니다.", "score": 100},
            {"name": "어벤투스 (Aventus)", "brand": "CREED", "description": "베르가못과 프루티한 과즙, 그리고 뒤이어 올라오는 우디함이 완벽한 밸런스를 이루는 프리미엄 향수입니다.", "score": 80},
            {"name": "탐다오 (Tam Dao)", "brand": "DIPTYQUE", "description": "샌달우드의 깊고 진한 나무 향이 중심이 되어 마음이 편안해지는 사찰 느낌의 향수입니다.", "score": 60}
        ]
        
    # Top 3~5 결과 출력 시작
    for idx, perfume in enumerate(recs):
        p_name = perfume.get("name", "이름 없는 향수")
        p_brand = perfume.get("brand", "프리미엄 브랜드")
        p_perfume_id = perfume.get("perfume_id")
        p_desc = perfume.get("description", "")
        summary_for_mood = st.session_state.get("test_summary")

        search_keyword = f"{p_brand} {p_name}".replace(" ", "+")
        google_search_url = f"https://www.google.com/search?q={search_keyword}"

        with st.container(border=True):
            title_cols = st.columns([11, 1])
            with title_cols[0]:
                st.markdown(f"### [{idx+1}. {p_name}]({google_search_url})")
            with title_cols[1]:
                render_favorite_star(p_perfume_id, saved_ids, key_prefix=f"pref_res_{idx}")

            st.caption(f"브랜드: **{p_brand}** | 🔗 이름을 누르면 구글 검색으로 이동합니다.")

            if show_reasons:
                reasons = build_recommendation_reasons(
                    p_perfume_id,
                    reco_context,
                    perfume.get("recommendation_score") or perfume.get("score"),
                )
                if reasons:
                    st.markdown("**추천 이유**")
                    for reason in reasons:
                        st.markdown(f"- {reason}")

            with st.expander("🔍 이 향수의 세부 정보 및 특징 보기"):
                if p_perfume_id:
                    grouped = perfume_repository.format_notes_by_type(
                        perfume_repository.get_perfume_notes(p_perfume_id)
                    )
                    note_lines = []
                    for note_type, label in NOTE_TYPE_LABELS.items():
                        names = grouped.get(note_type) or []
                        if names:
                            note_lines.append(f"{label}: {', '.join(names)}")
                    if note_lines:
                        st.markdown("\n\n".join(note_lines))
                    elif p_desc:
                        st.markdown(p_desc.replace("\n", "\n\n"))
                elif p_desc:
                    st.markdown(p_desc.replace("\n", "\n\n"))

                mood_text = perfume_repository.build_perfume_mood(
                    p_perfume_id,
                    summary_for_mood,
                    perfume_name=p_name,
                    brand_name=p_brand,
                )
                st.markdown("**무드**")
                st.write(mood_text)
                
    st.divider()
    
    # 다시 하기 버튼으로 세션 초기화 및 1단계 복귀
    if st.button("🔄 취향 분석 처음부터 다시 하기", type="secondary", use_container_width=True, key="restart_test"):
        reset_preference_wizard()
        for key in ("tmp_selected_main", "tmp_selected_detail", "tmp_selected_note", "tmp_selected_sub"):
            st.session_state.pop(key, None)
        st.session_state.pop("db_error_msg", None)
        st.rerun()

    if st.button("🏠 메인 화면으로 가기", use_container_width=True, key="go_home"):
        st.switch_page("app.py")