"""공통 UI 헬퍼."""

import streamlit as st

from database.repositories import favorite_repository, perfume_repository
from utils.session import is_logged_in


def render_profile_button(key_suffix: str = "") -> None:
    if is_logged_in():
        if st.button("👤 프로필", key=f"profile_btn_{key_suffix}"):
            st.switch_page("pages/04_profile.py")
    else:
        st.caption("👤 프로필 (회원 전용)")


def render_perfume_card(
    rank: int,
    perfume: dict,
    score: int,
    saved_ids: set[int],
    key_prefix: str,
    show_search: bool = True,
    show_favorite: bool = True,
) -> None:
    perfume_id = perfume.get("perfume_id")
    name = perfume.get("perfume_name", "이름 없음")
    brand = perfume.get("brand_name", "")
    is_saved = perfume_id in saved_ids

    with st.container(border=True):
        header_cols = st.columns([6, 1])
        with header_cols[0]:
            if show_search and brand:
                st.markdown(f"### {rank}. [{name}]({perfume_repository.google_search_url(name, brand)})")
            elif show_search:
                st.markdown(f"### {rank}. [{name}]({perfume_repository.google_search_url(name)})")
            else:
                st.markdown(f"### {rank}. {name}")
            if brand:
                st.caption(f"브랜드: {brand}")
        with header_cols[1]:
            if show_favorite and is_logged_in() and perfume_id:
                star = "★" if is_saved else "☆"
                if st.button(star, key=f"{key_prefix}_fav_{perfume_id}"):
                    user_id = st.session_state["user_id"]
                    if is_saved:
                        favorite_repository.remove_saved_perfume(user_id, perfume_id)
                    else:
                        favorite_repository.save_perfume(user_id, perfume_id)
                    st.rerun()

        st.metric("추천 점수", score)

        with st.expander("세부 정보 보기"):
            notes = perfume_repository.get_perfume_notes(perfume_id)
            grouped = perfume_repository.format_notes_by_type(notes)
            for note_type, label in [
                ("top", "탑 노트"),
                ("middle", "미들 노트"),
                ("base", "베이스 노트"),
            ]:
                items = grouped.get(note_type, [])
                if items:
                    st.write(f"**{label}:** {', '.join(items)}")

            summary = st.session_state.get("test_summary")
            if summary:
                st.divider()
                st.caption("점수 구성 (이번 선택 기준)")
                st.write(f"- 메인 세부향 일치: +50")
                st.write(f"- 발향 시점({summary.get('note_label', '')}) 일치: +30")
                for cat in summary.get("additional_categories", []):
                    st.write(f"- 보조 계열({cat}) 일치: +10")

            if show_search:
                url = perfume_repository.google_search_url(name, brand)
                st.link_button("Google에서 검색", url, use_container_width=True)
            else:
                st.info("Google 검색은 회원만 이용할 수 있습니다.")
