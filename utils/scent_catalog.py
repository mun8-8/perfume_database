"""
9개 주향 계열 · 각 4개 세부향 — 앱·DB·시드의 단일 기준.
"""

from __future__ import annotations

# (category_name, [(scent_name_en, scent_name_ko), ...])
SCENT_CATALOG: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "시트러스",
        [
            ("Lemon", "레몬"),
            ("Orange", "오렌지"),
            ("Grapefruit", "자몽"),
            ("Bergamot", "베르가못"),
        ],
    ),
    (
        "그린",
        [
            ("Grass Leaf", "풀잎"),
            ("Bamboo", "대나무"),
            ("Green Tea", "녹차"),
            ("Fig Leaf", "무화과 잎"),
        ],
    ),
    (
        "프루티",
        [
            ("Peach", "복숭아"),
            ("Apple", "사과"),
            ("Pear", "배"),
            ("Berry", "베리"),
        ],
    ),
    (
        "플로럴",
        [
            ("Rose", "장미"),
            ("Jasmine", "자스민"),
            ("Lily", "백합"),
            ("Ylang Ylang", "일랑일랑"),
        ],
    ),
    (
        "머스크",
        [
            ("White Musk", "화이트 머스크"),
            ("Clean Musk", "클린 머스크"),
            ("Amber Musk", "앰버 머스크"),
            ("Powdery Musk", "파우더리 머스크"),
        ],
    ),
    (
        "아쿠아틱",
        [
            ("Sea Salt", "씨솔트"),
            ("Water", "워터"),
            ("Ozone", "오존"),
            ("Marine Note", "마린노트"),
        ],
    ),
    (
        "구르망",
        [
            ("Vanilla", "바닐라"),
            ("Chocolate", "초콜릿"),
            ("Caramel", "캐러멜"),
            ("Coffee", "커피"),
        ],
    ),
    (
        "오리엔탈",
        [
            ("Amber", "앰버"),
            ("Incense", "인센스"),
            ("Spice", "스파이스"),
            ("Resin", "레진"),
        ],
    ),
    (
        "우디",
        [
            ("Sandalwood", "샌달우드"),
            ("Cedarwood", "시더우드"),
            ("Vetiver", "베티버"),
            ("Patchouli", "패출리"),
        ],
    ),
]

PRIMARY_CATEGORY_ORDER = [name for name, _ in SCENT_CATALOG]

SECONDARY_CATEGORY_ORDER = [
    "머스크",
    "시트러스",
    "오리엔탈",
    "그린",
    "아쿠아틱",
    "우디",
    "프루티",
    "플로럴",
    "구르망",
]

# 엑셀·기존 데이터의 변형 이름 → 카탈로그 세부향(한국어)
SCENT_ALIASES_KO: dict[str, str] = {
    "로즈": "장미",
    "파출리": "패출리",
    "화이트 마스크": "화이트 머스크",
    "클린머스크": "클린 머스크",
    "소프트 머스크": "클린 머스크",
    "머스크": "클린 머스크",
    "샌달 우드": "샌달우드",
    "샌달우": "샌달우드",
    "베티바": "베티버",
    "베르가모스 레몬": "베르가못",
    "베리가못": "베르가못",
    "엠버": "앰버",
    "피치": "복숭아",
    "스파이시": "스파이스",
}

CANONICAL_SCENTS_KO: set[str] = {
    ko for _, scents in SCENT_CATALOG for _, ko in scents
}

KO_TO_CATEGORY: dict[str, str] = {
    ko: category for category, scents in SCENT_CATALOG for _, ko in scents
}

KO_TO_EN: dict[str, str] = {
    ko: en for _, scents in SCENT_CATALOG for en, ko in scents
}

CATEGORY_SUB_SCENTS_KO: dict[str, list[str]] = {
    category: [ko for _, ko in scents] for category, scents in SCENT_CATALOG
}


def normalize_scent_ko(name: str) -> str | None:
    """카탈로그 세부향으로 정규화. 매핑 불가 시 None."""
    cleaned = SCENT_ALIASES_KO.get(name.strip(), name.strip())
    if cleaned in CANONICAL_SCENTS_KO:
        return cleaned
    return None


def catalog_scent_order(category_name: str) -> list[str]:
    return CATEGORY_SUB_SCENTS_KO.get(category_name, [])
