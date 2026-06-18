"""CSV 기반 향수별 무드 카탈로그 (data/perfume_moods.csv)."""

from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path

_CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "perfume_moods.csv"

_BRAND_ALIASES: dict[str, str] = {
    "chanel": "Chanel",
    "dior": "Dior",
    "diptyque": "Diptyque",
    "creed": "크리드",
    "크리드": "크리드",
    "tomford": "톰포드",
    "톰포드": "톰포드",
    "jo malone": "조말론",
    "jomalone": "조말론",
    "조말론": "조말론",
    "byredo": "바이레도",
    "바이레도": "바이레도",
    "le labo": "르라보",
    "lelabo": "르라보",
    "르라보": "르라보",
    "maison francis kurkdjian": "메종 프란시스 커정",
    "메종프란시스커정": "메종 프란시스 커정",
    "메종 프란시스 커정": "메종 프란시스 커정",
    "maison margiela": "메종 마르지엘라",
    "메종마르지엘라": "메종 마르지엘라",
    "메종 마르지엘라": "메종 마르지엘라",
    "kilian": "킬리안",
    "킬리안": "킬리안",
    "acqua di parma": "아쿠아 디파르마",
    "아쿠아디파르마": "아쿠아 디파르마",
    "아쿠아 디파르마": "아쿠아 디파르마",
}


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text.strip().lower())


def _normalize_brand(brand: str) -> str:
    cleaned = " ".join(brand.split())
    key = _compact(cleaned)
    return _BRAND_ALIASES.get(key, cleaned)


def _normalize_perfume_name(name: str) -> str:
    name = re.sub(r"\s*\([^)]*\)", "", name)
    return " ".join(name.split())


def _format_mood(raw: str) -> str:
    """쉼표 구분 무드를 읽기 좋게 정리."""
    parts = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
    return ", ".join(parts)


@lru_cache(maxsize=1)
def _load_mood_index() -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    if not _CSV_PATH.exists():
        return index

    with _CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            brand = (row.get("brand") or "").strip()
            name = (row.get("perfume_name") or "").strip()
            mood = (row.get("mood") or "").strip()
            if not brand or not name or not mood:
                continue
            brand_n = _normalize_brand(brand)
            name_n = _normalize_perfume_name(name)
            index[(_compact(brand_n), _compact(name_n))] = _format_mood(mood)
            # 브랜드 없이 이름만 (보조)
            index[("", _compact(name_n))] = _format_mood(mood)
    return index


def lookup_perfume_mood(brand_name: str, perfume_name: str) -> str | None:
    """브랜드·향수명으로 무드 문자열 조회."""
    if not perfume_name:
        return None

    index = _load_mood_index()
    brand_n = _normalize_brand(brand_name or "")
    name_n = _normalize_perfume_name(perfume_name)

    mood = index.get((_compact(brand_n), _compact(name_n)))
    if mood:
        return mood

    return index.get(("", _compact(name_n)))


def lookup_perfume_mood_list(brand_name: str, perfume_name: str) -> list[str]:
    text = lookup_perfume_mood(brand_name, perfume_name)
    if not text:
        return []
    return [m.strip() for m in text.split(",") if m.strip()]
