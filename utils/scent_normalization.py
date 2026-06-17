"""
향 이름 표준화 — 카탈로그 기준.
"""

from utils.scent_catalog import SCENT_ALIASES_KO, normalize_scent_ko

SCENT_SYNONYMS_KO: dict[str, str] = SCENT_ALIASES_KO


def normalize_ko_to_en(ko_name: str) -> str:
    from utils.scent_catalog import KO_TO_EN

    canonical = normalize_scent_ko(ko_name)
    if canonical:
        return KO_TO_EN[canonical]
    return ko_name.strip()
