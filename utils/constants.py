"""앱 전역 상수."""

from utils.scent_catalog import PRIMARY_CATEGORY_ORDER, SECONDARY_CATEGORY_ORDER

NOTE_TYPE_OPTIONS = [
    ("top", "탑 노트 (처음에 느껴지는 향)"),
    ("middle", "미들 노트 (중간에 느께지는 향)"),
    ("base", "베이스 노트 (마지막에 남는 향)"),
]

NOTE_TYPE_LABELS = {
    "top": "탑 노트",
    "middle": "미들 노트",
    "base": "베이스 노트",
}
