from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.scent_catalog import SCENT_CATALOG, normalize_scent_ko

EXCEL_PATH = "data/perfume_db.xlsx"
OUTPUT_SQL = "scripts/generated_seed.sql"


def split_notes(note_text: str) -> list[str]:
    if pd.isna(note_text):
        return []

    text = str(note_text)
    for sep in [",", "/", "•", "·"]:
        text = text.replace(sep, "|")

    notes = [x.strip() for x in text.split("|") if x.strip()]
    return list(dict.fromkeys(notes))


def main() -> None:
    df = pd.read_excel(EXCEL_PATH)
    sql_lines: list[str] = []

    sql_lines.append("-- 향수 데이터 (excel_to_seed.py 자동 생성)")
    sql_lines.append("-- 실행 전 nine_categories_seed.sql 을 먼저 실행하세요.")
    sql_lines.append("BEGIN;")
    sql_lines.append("")

    perfume_id = 1
    for _, row in df.iterrows():
        brand = str(row.get("브랜드", "")).replace("'", "''")
        perfume_name = str(row.get("향수 이름", "")).replace("'", "''")
        if perfume_name in ("nan", ""):
            continue
        sql_lines.append(
            f"INSERT INTO perfumes (perfume_name, brand_name) "
            f"SELECT '{perfume_name}', '{brand}' "
            f"WHERE NOT EXISTS ("
            f"SELECT 1 FROM perfumes WHERE perfume_name = '{perfume_name}' "
            f"AND brand_name = '{brand}'"
            f");"
        )
        perfume_id += 1

    sql_lines.append("")
    sql_lines.append("-- 카탈로그 세부향 (9계열 × 4개)")
    scent_to_id: dict[str, int] = {}
    scent_en_by_ko: dict[str, str] = {}

    for category_name, scents in SCENT_CATALOG:
        for scent_en, scent_ko in scents:
            scent_en_sql = scent_en.replace("'", "''")
            scent_ko_sql = scent_ko.replace("'", "''")
            sql_lines.append(
                f"INSERT INTO scents (scent_name_en, scent_name_ko, category_id) "
                f"SELECT '{scent_en_sql}', '{scent_ko_sql}', category_id "
                f"FROM scent_categories WHERE category_name = '{category_name}' "
                f"ON CONFLICT (scent_name_en) DO NOTHING;"
            )
            scent_en_by_ko[scent_ko] = scent_en

    sql_lines.append("")
    sql_lines.append("-- 향수 노트 (카탈로그 세부향으로 정규화)")

    for _, row in df.iterrows():
        brand = str(row.get("브랜드", "")).replace("'", "''")
        perfume_name = str(row.get("향수 이름", "")).replace("'", "''")
        if perfume_name in ("nan", ""):
            continue

        for excel_col, note_type in [("Top", "top"), ("Middle", "middle"), ("Base", "base")]:
            for raw_note in split_notes(row.get(excel_col, "")):
                canonical = normalize_scent_ko(raw_note)
                if not canonical:
                    continue
                scent_en = scent_en_by_ko[canonical].replace("'", "''")
                sql_lines.append(
                    f"INSERT INTO perfume_notes (perfume_id, scent_id, note_type) "
                    f"SELECT p.perfume_id, s.scent_id, '{note_type}' "
                    f"FROM perfumes p "
                    f"JOIN scents s ON s.scent_name_en = '{scent_en}' "
                    f"WHERE p.perfume_name = '{perfume_name}' AND p.brand_name = '{brand}' "
                    f"ON CONFLICT (perfume_id, scent_id, note_type) DO NOTHING;"
                )

    sql_lines.append("COMMIT;")

    Path("scripts").mkdir(exist_ok=True)
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))

    print("generated:", OUTPUT_SQL)
    print("catalog scents:", len(scent_en_by_ko))


if __name__ == "__main__":
    main()
