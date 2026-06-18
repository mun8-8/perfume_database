"""공통 UI 헬퍼."""

import html

import streamlit as st

from database.repositories import favorite_repository, perfume_repository
from utils.constants import NOTE_TYPE_LABELS
from utils.scent_theme import NOTE_THEME, SCENT_THEME
from utils.session import is_logged_in


def _theme_colors(theme_id: str, theme_map: str) -> dict[str, str] | None:
    palette = SCENT_THEME if theme_map == "scent" else NOTE_THEME
    return palette.get(theme_id)


def render_themed_choice_button(
    label: str,
    streamlit_key: str,
    theme_id: str,
    *,
    selected: bool = False,
    theme_map: str = "scent",
) -> bool:
    """
    미선택: Streamlit 기본 버튼.
    선택됨: 향조 색상 카드(HTML) — CSS 우회로 색상이 확실히 보임.
    """
    colors = _theme_colors(theme_id, theme_map)
    if selected and colors:
        bg, text = colors["bg"], colors["text"]
        st.markdown(
            f"""
            <div style="
                background-color: {bg};
                color: {text};
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                text-align: center;
                font-weight: 600;
                font-size: 1rem;
                line-height: 1.4;
                min-height: 2.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
                box-shadow: 0 2px 8px {bg}66;
            ">{label}</div>
            """,
            unsafe_allow_html=True,
        )
        return False

    return st.button(
        label,
        key=streamlit_key,
        type="secondary",
        use_container_width=True,
    )


def render_scent_description_panel(
    title: str,
    description: str | list[str],
    theme_id: str,
    *,
    theme_map: str = "scent",
    subtitle: str | None = None,
) -> None:
    """선택한 향·세부향 설명 — 향조 테마 색상 강조 박스."""
    if not description:
        return

    colors = _theme_colors(theme_id, theme_map)
    if colors:
        bg = colors.get("light", colors["bg"])
        accent = colors["bg"]
    else:
        bg = "#F0F2F6"
        accent = "#FF4B4B"

    # 제목·본문은 항상 진한 검정 (다크 모드 CSS·테마 text 흰색 덮어쓰기 방지)
    title_style = "color: #1a1a1a !important;"
    body_style = "color: #1a1a1a !important;"
    subtitle_style = "color: #333333 !important;"

    safe_title = html.escape(title)
    if isinstance(description, list):
        body = (
            "<ul style='margin: 0.35rem 0 0 1.15rem; padding: 0;'>"
            + "".join(
                f"<li style='margin-bottom: 0.4rem; {body_style}'>{html.escape(item)}</li>"
                for item in description
            )
            + "</ul>"
        )
    else:
        body = f'<span style="{body_style}">{html.escape(description)}</span>'

    subtitle_html = ""
    if subtitle:
        subtitle_html = (
            f'<div style="font-size: 0.92rem; font-weight: 600; '
            f'margin-bottom: 0.5rem; {subtitle_style}">{html.escape(subtitle)}</div>'
        )

    st.markdown(
        f"""
        <div class="scent-desc-panel" style="
            background: linear-gradient(135deg, {bg} 0%, #ffffff 100%);
            border: 1px solid {accent}44;
            border-left: 5px solid {accent};
            border-radius: 0.6rem;
            padding: 0.9rem 1.1rem;
            margin: 0.75rem 0 1rem 0;
            box-shadow: 0 2px 10px {accent}22;
        ">
            <div style="
                font-weight: 700;
                font-size: 1.08rem;
                margin-bottom: 0.45rem;
                {title_style}
            ">🎯 {safe_title}</div>
            {subtitle_html}
            <div style="
                font-size: 0.98rem;
                line-height: 1.6;
                {body_style}
            ">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_favorite_star(
    perfume_id: int | None,
    saved_ids: set[int],
    key_prefix: str,
) -> None:
    """향수 이름 우측 즐겨찾기 별 — 회원만 토글 가능."""
    if not is_logged_in():
        st.button(
            "☆",
            key=f"{key_prefix}_fav_guest",
            disabled=True,
            help="즐겨찾기는 로그인한 회원만 이용할 수 있습니다.",
        )
        return

    if not perfume_id:
        st.button(
            "☆",
            key=f"{key_prefix}_fav_na",
            disabled=True,
            help="이 향수는 즐겨찾기에 저장할 수 없습니다.",
        )
        return

    is_saved = perfume_id in saved_ids
    star = "★" if is_saved else "☆"
    if st.button(
        star,
        key=f"{key_prefix}_fav_{perfume_id}",
        help="즐겨찾기 추가/해제",
    ):
        user_id = st.session_state["user_id"]
        try:
            if is_saved:
                favorite_repository.remove_saved_perfume(user_id, perfume_id)
            else:
                favorite_repository.save_perfume(user_id, perfume_id)
        except Exception:
            pass
        st.rerun()


def render_perfume_detail_expander(
    perfume_id: int | None,
    name: str,
    brand: str,
    key_prefix: str,
    *,
    show_search: bool = True,
) -> None:
    """노트 구성 · 무드 · Google 검색."""
    with st.expander("향수 상세 보기", expanded=False):
        if perfume_id:
            notes = perfume_repository.get_perfume_notes(perfume_id)
            grouped = perfume_repository.format_notes_by_type(notes)
            note_lines: list[str] = []
            for note_type, label in NOTE_TYPE_LABELS.items():
                items = grouped.get(note_type) or []
                if items:
                    note_lines.append(f"**{label}:** {', '.join(items)}")
            if note_lines:
                st.markdown("\n\n".join(note_lines))
            else:
                st.caption("등록된 노트 정보가 없습니다.")

            st.markdown("**무드**")
            st.write(
                perfume_repository.build_perfume_mood(
                    perfume_id,
                    None,
                    perfume_name=name,
                    brand_name=brand,
                )
            )
        else:
            st.caption("상세 정보를 불러올 수 없습니다.")

        if show_search:
            st.link_button(
                "Google에서 검색",
                perfume_repository.google_search_url(name, brand),
                use_container_width=True,
                key=f"{key_prefix}_search",
            )


def toggle_history_test(test_id: int) -> None:
    """이전 추천 항목 펼침/접힘 토글."""
    current = st.session_state.get("view_history_test_id")
    st.session_state["view_history_test_id"] = None if current == test_id else test_id


def inject_history_date_styles() -> None:
    """이전 추천 날짜·삼각형 토글 버튼 스타일."""
    st.markdown(
        """
        <style>
        [class*="st-key-hist_date_"] button,
        [class*="st-key-hist_toggle_"] button,
        [class*="st-key-hist_collapse_"] button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #31333F !important;
            padding: 0 !important;
            min-height: 0 !important;
            height: auto !important;
        }
        [class*="st-key-hist_date_"] button {
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            text-align: left !important;
            justify-content: flex-start !important;
        }
        [class*="st-key-hist_date_"] button:hover,
        [class*="st-key-hist_toggle_"] button:hover,
        [class*="st-key-hist_collapse_"] button:hover {
            color: #FF4B4B !important;
            background: transparent !important;
        }
        [class*="st-key-hist_date_"] button p {
            font-weight: 700 !important;
        }
        [class*="st-key-hist_toggle_"] button,
        [class*="st-key-hist_collapse_"] button {
            font-size: 0.95rem !important;
            line-height: 1 !important;
        }
        [class*="st-key-hist_collapse_"] {
            display: flex;
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_history_recommendations(
    test_id: int,
    user_id: str,
    saved_ids: set[int],
) -> None:
    """해당 시점 추천 향수 목록 (이력 항목 바로 아래)."""
    from database.repositories import recommendation_repository

    try:
        rows = recommendation_repository.get_recommendations_by_test(test_id)
    except Exception as exc:
        st.error(f"추천 결과 조회 실패: {exc}")
        return

    if not rows:
        st.caption("저장된 추천 결과가 없습니다.")
        return

    st.caption("해당 시점 추천 향수")
    for idx, row in enumerate(rows, start=1):
        perfume = row.get("perfumes") or {}
        name = perfume.get("perfume_name", "이름 없음")
        brand = perfume.get("brand_name", "")
        perfume_id = perfume.get("perfume_id")

        with st.container(border=True):
            title_cols = st.columns([11, 1])
            with title_cols[0]:
                url = perfume_repository.google_search_url(name, brand)
                st.markdown(f"**{idx}. [{name}]({url})**")
                if brand:
                    st.caption(brand)
            with title_cols[1]:
                render_favorite_star(
                    perfume_id, saved_ids, key_prefix=f"hist_{test_id}_{idx}"
                )

            if perfume_id:
                render_perfume_detail_expander(
                    perfume_id, name, brand, f"hist_{test_id}_{idx}", show_search=True
                )


def render_favorite_list_item(
    perfume_id: int | None,
    name: str,
    brand: str,
    user_id: str,
    key_prefix: str,
) -> None:
    """프로필 즐겨찾기 한 항목."""
    with st.container(border=True):
        header = st.columns([5, 1])
        with header[0]:
            st.markdown(f"**{name}**")
            if brand:
                st.caption(brand)
        with header[1]:
            if perfume_id and st.button("☆", key=f"{key_prefix}_unsave", help="즐겨찾기 해제"):
                favorite_repository.remove_saved_perfume(user_id, perfume_id)
                st.rerun()

        render_perfume_detail_expander(
            perfume_id, name, brand, key_prefix, show_search=True
        )


def render_profile_button(key_suffix: str = "") -> None:
    """우측 상단 프로필 — 회원은 프로필 페이지, 비회원은 로그인 페이지로 이동."""
    key = f"profile_btn_{key_suffix}"
    if is_logged_in():
        st.page_link(
            "pages/04_profile.py",
            label="👤 프로필",
            use_container_width=True,
        )
    else:
        if st.button(
            "👤 프로필",
            key=key,
            use_container_width=True,
            help="로그인 후 이용할 수 있습니다.",
        ):
            st.switch_page("pages/01_auth.py")


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
                st.write("- 주향 계열 일치: +30")
                st.write("- 세부향 일치: +30")
                st.write(f"- 발향 시점({summary.get('note_label', '')}) 일치: +20")
                for cat in summary.get("additional_categories", []):
                    st.write(f"- 보조향({cat}) 일치: +20")

            if show_search:
                url = perfume_repository.google_search_url(name, brand)
                st.link_button("Google에서 검색", url, use_container_width=True)
            else:
                st.info("Google 검색은 회원만 이용할 수 있습니다.")
