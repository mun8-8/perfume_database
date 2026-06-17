from pathlib import Path

from database.supabase_client import get_supabase

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def score_perfumes_via_rpc(
    main_scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
) -> list[dict]:
    """Supabase SQL 함수 recommend_perfumes 호출."""
    response = get_supabase().rpc(
        "recommend_perfumes",
        {
            "p_main_scent_id": main_scent_id,
            "p_preferred_note_type": preferred_note_type,
            "p_additional_category_ids": additional_category_ids or [],
        },
    ).execute()
    return response.data or []


def score_perfumes_via_join_query(
    main_scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
) -> list[dict]:
    """
    RPC 미설치 시 동작하는 fallback.
    PostgREST 로 perfume_notes + scents 조인 데이터를 가져온 뒤
    SQL 스코어링과 동일한 규칙으로 집계합니다.
    """
    response = (
        get_supabase()
        .table("perfume_notes")
        .select("perfume_id, note_type, scents(scent_id, category_id)")
        .execute()
    )
    rows = response.data or []
    additional_set = set(additional_category_ids or [])

    scores: dict[int, dict] = {}

    for row in rows:
        perfume_id = row["perfume_id"]
        scent = row.get("scents") or {}
        scent_id = scent.get("scent_id")
        category_id = scent.get("category_id")
        note_type = row.get("note_type")

        if perfume_id not in scores:
            scores[perfume_id] = {
                "perfume_id": perfume_id,
                "has_main_scent": False,
                "has_main_scent_with_note": False,
                "additional_category_match_count": 0,
                "matched_additional_categories": set(),
            }

        entry = scores[perfume_id]

        if scent_id == main_scent_id:
            entry["has_main_scent"] = True
            if note_type == preferred_note_type:
                entry["has_main_scent_with_note"] = True

        if category_id in additional_set:
            entry["matched_additional_categories"].add(category_id)

    results: list[dict] = []
    for entry in scores.values():
        additional_count = len(entry["matched_additional_categories"])
        score = (
            (50 if entry["has_main_scent"] else 0)
            + (30 if entry["has_main_scent_with_note"] else 0)
            + (additional_count * 10)
        )
        if score > 0:
            results.append(
                {
                    "perfume_id": entry["perfume_id"],
                    "recommendation_score": score,
                }
            )

    results.sort(key=lambda x: (-x["recommendation_score"], x["perfume_id"]))
    return results[:5]


def save_recommendation_results(test_id: int, recommendations: list[dict]) -> None:
    if not recommendations:
        return

    rows = [
        {
            "test_id": test_id,
            "perfume_id": item["perfume_id"],
            "recommendation_score": item["recommendation_score"],
        }
        for item in recommendations
    ]
    get_supabase().table("recommendation_results").insert(rows).execute()


def get_recommendations_by_test(test_id: int) -> list[dict]:
    response = (
        get_supabase()
        .table("recommendation_results")
        .select(
            "recommendation_id, recommendation_score, perfumes(perfume_id, perfume_name, brand_name)"
        )
        .eq("test_id", test_id)
        .order("recommendation_score", desc=True)
        .limit(5)
        .execute()
    )
    return response.data or []
