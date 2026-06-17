import streamlit as st

from database.repositories import scent_repository
from services.recommendation_service import run_full_recommendation_flow
from utils.constants import NOTE_TYPE_LABELS, NOTE_TYPE_OPTIONS
from utils.scent_catalog import CATEGORY_SUB_SCENTS_KO, PRIMARY_CATEGORY_ORDER, SECONDARY_CATEGORY_ORDER
from utils.session import has_auth, init_session, is_logged_in, reset_preference_wizard

st.set_page_config(page_title="취향 테스트", layout="wide")
init_session()

if not has_auth():
    st.switch_page("pages/01_auth.py")

header_cols = st.columns([5, 1])
with header_cols[0]:
    st.title("향 취향 테스트")
with header_cols[1]:
    if is_logged_in():
        if st.button("👤", help="프로필"):
            st.switch_page("pages/04_profile.py")

step = st.session_state["pref_step"]
st.progress(step / 4, text=f"단계 {step} / 4")

try:
    categories = scent_repository.get_scent_categories_ordered(PRIMARY_CATEGORY_ORDER)
except Exception as exc:
    st.error(f"DB 연결 실패: {exc}")
    st.stop()

if not categories:
    st.warning("향 계열 데이터가 없습니다. `sql/nine_categories_seed.sql`을 실행해 주세요.")
    st.stop()

category_by_name = {c["category_name"]: c for c in categories}

if step == 1:
    st.subheader("1. 주향 계열을 선택하세요")

    for row_start in range(0, len(categories), 3):
        cols = st.columns(3)
        for col, category in zip(cols, categories[row_start : row_start + 3]):
            name = category["category_name"]
            with col:
                if st.button(
                    name,
                    key=f"cat_{category['category_id']}",
                    use_container_width=True,
                ):
                    st.session_state["pref_main_category"] = category
                    st.session_state["pref_step"] = 2
                    st.rerun()

elif step == 2:
    main_category = st.session_state["pref_main_category"]
    cat_name = main_category["category_name"]
    sub_scents = CATEGORY_SUB_SCENTS_KO.get(cat_name, [])

    st.subheader(f"2. 세부향 선택")
    st.markdown(f"**주향: {cat_name}**")
    st.caption("아래 4가지 세부향 중 하나를 선택하세요.")

    if st.button("← 주향 다시 선택"):
        st.session_state["pref_step"] = 1
        st.rerun()

    try:
        scents = scent_repository.get_scents_by_category(
            main_category["category_id"],
            category_name=cat_name,
        )
    except Exception as exc:
        st.error(f"향 목록 조회 실패: {exc}")
        st.stop()

    scent_by_ko = {s["scent_name_ko"]: s for s in scents}
    display_scents = [scent_by_ko[ko] for ko in sub_scents if ko in scent_by_ko]

    if not display_scents:
        st.warning(
            f"'{cat_name}' 계열 세부향이 DB에 없습니다. "
            "`sql/nine_categories_seed.sql` 실행 후 다시 시도해 주세요."
        )
        for ko in sub_scents:
            st.write(f"- {ko}")
        st.stop()

    row1 = st.columns(2)
    row2 = st.columns(2)
    for idx, scent in enumerate(display_scents):
        col = row1[idx] if idx < 2 else row2[idx - 2]
        with col:
            with st.container(border=True):
                st.markdown(f"### {scent['scent_name_ko']}")
                st.caption(cat_name)
                if st.button(
                    "선택",
                    key=f"scent_{scent['scent_id']}",
                    use_container_width=True,
                ):
                    st.session_state["pref_main_scent"] = scent
                    st.session_state["pref_step"] = 3
                    st.rerun()

elif step == 3:
    main_category = st.session_state["pref_main_category"]
    main_scent = st.session_state["pref_main_scent"]
    st.subheader("3. 발향 시점을 선택하세요")
    st.markdown(
        f"**{main_category['category_name']}** · **{main_scent['scent_name_ko']}**"
    )
    if st.button("← 세부향 다시 선택"):
        st.session_state["pref_step"] = 2
        st.rerun()

    for value, label in NOTE_TYPE_OPTIONS:
        if st.button(label, key=f"note_{value}", use_container_width=True):
            st.session_state["pref_note_type"] = value
            st.session_state["pref_step"] = 4
            st.rerun()

elif step == 4:
    main_category = st.session_state["pref_main_category"]
    main_scent = st.session_state["pref_main_scent"]
    note_type = st.session_state["pref_note_type"]
    note_label = NOTE_TYPE_LABELS.get(note_type, note_type)

    st.subheader("4. 보조향 계열을 선택하세요 (최대 2개)")
    st.markdown(
        f"**주향:** {main_category['category_name']} - {main_scent['scent_name_ko']} ({note_label})"
    )
    st.caption(
        "보조향은 **계열 이름만** 고릅니다. (세부향은 고르지 않습니다.) "
        "주향에서 이미 고른 계열은 목록에 나오지 않습니다."
    )

    if st.button("← 발향 시점 다시 선택"):
        st.session_state["pref_step"] = 3
        st.session_state.pop("pref_secondary_selected", None)
        st.rerun()

    if "pref_secondary_selected" not in st.session_state:
        st.session_state["pref_secondary_selected"] = []

    selected_names: list[str] = st.session_state["pref_secondary_selected"]

    secondary_categories = scent_repository.get_scent_categories_ordered(
        SECONDARY_CATEGORY_ORDER
    )
    available = [
        c for c in secondary_categories if c["category_name"] != main_category["category_name"]
    ]

    if selected_names:
        st.info(f"선택한 보조향: {', '.join(selected_names)} ({len(selected_names)}/2)")

    for row_start in range(0, len(available), 3):
        cols = st.columns(3)
        for col, category in zip(cols, available[row_start : row_start + 3]):
            name = category["category_name"]
            is_selected = name in selected_names
            label = f"✓ {name}" if is_selected else name
            with col:
                if st.button(
                    label,
                    key=f"sec_{category['category_id']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    if is_selected:
                        selected_names.remove(name)
                    elif len(selected_names) < 2:
                        selected_names.append(name)
                    else:
                        st.toast("보조향은 최대 2개까지 선택할 수 있습니다.")
                    st.session_state["pref_secondary_selected"] = selected_names
                    st.rerun()

    if st.button("추천 받기", type="primary", use_container_width=True):
        additional_category_ids = [
            category_by_name[name]["category_id"] for name in selected_names
        ]
        user_id = st.session_state.get("user_id") if is_logged_in() else None

        with st.spinner("추천을 계산하는 중..."):
            try:
                test_id, recommendations = run_full_recommendation_flow(
                    category_id=main_category["category_id"],
                    scent_id=main_scent["scent_id"],
                    preferred_note_type=note_type,
                    additional_category_ids=additional_category_ids,
                    user_id=user_id,
                )
            except Exception as exc:
                st.error(f"추천 처리 실패: {exc}")
                st.stop()

        if not recommendations:
            st.warning("조건에 맞는 향수를 찾지 못했습니다.")
            st.stop()

        st.session_state["test_id"] = test_id
        st.session_state["recommendations"] = recommendations
        st.session_state["test_summary"] = {
            "main_category": main_category["category_name"],
            "main_scent": main_scent["scent_name_ko"],
            "note_type": note_type,
            "note_label": note_label,
            "additional_categories": selected_names,
        }
        reset_preference_wizard()
        st.session_state.pop("pref_secondary_selected", None)
        st.switch_page("pages/03_recommendation_result.py")
