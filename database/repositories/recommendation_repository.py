from pathlib import Path

from database.supabase_client import ensure_authenticated_session, get_supabase

SQL_DIR = Path(__file__).resolve().parents[2] / "sql"


def score_perfumes_via_rpc(
    main_category_id: int,
    main_scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
) -> list[dict]:
    """Supabase SQL 함수 recommend_perfumes 호출 (30/30/20/20)."""
    response = get_supabase().rpc(
        "recommend_perfumes",
        {
            "p_main_category_id": main_category_id,
            "p_main_scent_id": main_scent_id,
            "p_preferred_note_type": preferred_note_type,
            "p_additional_category_ids": additional_category_ids or [],
        },
    ).execute()
    return response.data or []


def score_perfumes_via_join_query(
    main_category_id: int,
    main_scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
) -> list[dict]:
    """RPC 미설치 시 Python fallback — SQL과 동일한 30/30/20/20 규칙."""
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
                "has_main_category": False,
                "has_detail_scent": False,
                "has_note_match": False,
                "has_sub_category": False,
            }

        entry = scores[perfume_id]

        if category_id == main_category_id:
            entry["has_main_category"] = True

        if scent_id == main_scent_id:
            entry["has_detail_scent"] = True
            if note_type == preferred_note_type:
                entry["has_note_match"] = True

        if (
            category_id in additional_set
            and category_id != main_category_id
        ):
            entry["has_sub_category"] = True

    results: list[dict] = []
    for entry in scores.values():
        score = (
            (30 if entry["has_main_category"] else 0)
            + (30 if entry["has_detail_scent"] else 0)
            + (20 if entry["has_note_match"] else 0)
            + (20 if entry["has_sub_category"] else 0)
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

    ensure_authenticated_session()
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
