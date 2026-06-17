from database.repositories import preference_repository, recommendation_repository


def run_full_recommendation_flow(
    category_id: int,
    scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
    user_id: str | None = None,
) -> tuple[int, list[dict]]:
    """
    테스트 저장 → SQL(또는 동일 규칙 fallback) 추천 → 결과 저장.
    반환: (test_id, recommendations)
    """
    test_id = preference_repository.create_user_preference_test(user_id=user_id)

    preference_repository.save_main_choice(
        test_id=test_id,
        category_id=category_id,
        scent_id=scent_id,
        preferred_note_type=preferred_note_type,
    )
    preference_repository.save_additional_categories(
        test_id=test_id,
        category_ids=additional_category_ids,
    )

    recommendations = _score_perfumes(
        main_scent_id=scent_id,
        preferred_note_type=preferred_note_type,
        additional_category_ids=additional_category_ids,
    )

    recommendation_repository.save_recommendation_results(test_id, recommendations)
    return test_id, recommendations


def _score_perfumes(
    main_scent_id: int,
    preferred_note_type: str,
    additional_category_ids: list[int],
) -> list[dict]:
    try:
        return recommendation_repository.score_perfumes_via_rpc(
            main_scent_id=main_scent_id,
            preferred_note_type=preferred_note_type,
            additional_category_ids=additional_category_ids,
        )
    except Exception:
        return recommendation_repository.score_perfumes_via_join_query(
            main_scent_id=main_scent_id,
            preferred_note_type=preferred_note_type,
            additional_category_ids=additional_category_ids,
        )
