"""향 계열·발향 시점별 버튼 테마 색상."""

import hashlib

SCENT_THEME: dict[str, dict[str, str]] = {
    "시트러스": {"bg": "#F9A825", "text": "#3E2723", "light": "#FFF8E1"},
    "그린": {"bg": "#43A047", "text": "#FFFFFF", "light": "#E8F5E9"},
    "프루티": {"bg": "#EC407A", "text": "#FFFFFF", "light": "#FCE4EC"},
    "플로럴": {"bg": "#D81B60", "text": "#FFFFFF", "light": "#F8BBD9"},
    "머스크": {"bg": "#78909C", "text": "#FFFFFF", "light": "#ECEFF1"},
    "아쿠아틱": {"bg": "#039BE5", "text": "#FFFFFF", "light": "#E1F5FE"},
    "구르망": {"bg": "#8D6E63", "text": "#FFFFFF", "light": "#EFEBE9"},
    "오리엔탈": {"bg": "#7B1FA2", "text": "#FFFFFF", "light": "#F3E5F5"},
    "우디": {"bg": "#6D4C41", "text": "#FFFFFF", "light": "#EFEBE9"},
}

NOTE_THEME: dict[str, dict[str, str]] = {
    "top": {"bg": "#FFB300", "text": "#3E2723", "light": "#FFF8E1"},
    "middle": {"bg": "#E91E63", "text": "#FFFFFF", "light": "#FCE4EC"},
    "base": {"bg": "#5D4037", "text": "#FFFFFF", "light": "#EFEBE9"},
}

CATEGORY_SLUG: dict[str, str] = {
    "시트러스": "citrus",
    "그린": "green",
    "프루티": "fruity",
    "플로럴": "floral",
    "머스크": "musk",
    "아쿠아틱": "aquatic",
    "구르망": "gourmand",
    "오리엔탈": "oriental",
    "우디": "woody",
}

NOTE_SLUG: dict[str, str] = {
    "탑": "top",
    "미들": "middle",
    "베이스": "base",
}

NOTE_KEY_TO_THEME = {
    "탑": "top",
    "미들": "middle",
    "베이스": "base",
}

def detail_slug(detail_name: str) -> str:
    digest = hashlib.md5(detail_name.encode("utf-8")).hexdigest()[:10]
    return f"det_{digest}"
