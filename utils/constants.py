"""앱 전역 상수."""

from utils.scent_catalog import PRIMARY_CATEGORY_ORDER, SECONDARY_CATEGORY_ORDER

NOTE_TYPE_OPTIONS = [
    ("top", "탑 노트"),
    ("middle", "미들 노트"),
    ("base", "베이스 노트"),
]

NOTE_TYPE_LABELS = {
    "top": "탑 노트",
    "middle": "미들 노트",
    "base": "베이스 노트",
}

NOTE_TYPE_ENGLISH_LABELS: dict[str, str] = {
    "top": "Top Note (Head Note)",
    "middle": "Middle Note (Heart Note)",
    "base": "Base Note (Bottom Note)",
}

NOTE_TYPE_DESCRIPTIONS: dict[str, list[str]] = {
    "top": [
        "향수를 뿌린 직후 가장 먼저 느껴지는 향입니다.",
        "향수의 첫인상을 결정하며, 가볍고 휘발성이 높은 향료로 이루어져 있습니다.",
        "보통 5~15분 정도 지속됩니다.",
    ],
    "middle": [
        "향수의 중심이 되는 단계입니다.",
        "전체 향의 약 70%를 차지하며, 향수의 분위기와 개성을 결정합니다.",
        "다른 향들과 자연스럽게 어우러지는 역할을 합니다.",
        "약 20~60분 정도 지속됩니다.",
    ],
    "base": [
        "향수의 마지막까지 남는 잔향으로, 가장 오래 지속되는 향입니다.",
        "향수의 마무리를 담당하며 깊고 부드러운 느낌을 줍니다.",
        "향의 깊이와 지속력을 높여줍니다.",
        "보통 6시간 이상 유지됩니다.",
    ],
}
