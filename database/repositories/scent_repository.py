from database.supabase_client import get_supabase


def get_scent_categories_ordered(category_order: list[str]) -> list[dict]:
    categories = get_scent_categories()
    by_name = {c["category_name"]: c for c in categories}
    ordered = [by_name[name] for name in category_order if name in by_name]
    for category in categories:
        if category not in ordered:
            ordered.append(category)
    return ordered


def get_scent_categories() -> list[dict]:
    response = (
        get_supabase()
        .table("scent_categories")
        .select("category_id, category_name")
        .order("category_name")
        .execute()
    )
    return response.data or []


def get_scents_by_category(category_id: int, category_name: str | None = None) -> list[dict]:
    response = (
        get_supabase()
        .table("scents")
        .select("scent_id, scent_name_en, scent_name_ko, category_id")
        .eq("category_id", category_id)
        .execute()
    )
    scents = response.data or []

    if category_name:
        from utils.scent_catalog import catalog_scent_order

        order = catalog_scent_order(category_name)
        if order:
            order_index = {name: idx for idx, name in enumerate(order)}
            scents = [s for s in scents if s["scent_name_ko"] in order_index]
            scents.sort(key=lambda s: order_index[s["scent_name_ko"]])

    return scents
