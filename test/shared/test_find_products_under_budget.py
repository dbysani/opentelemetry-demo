import pytest
from src.shared import tools


@pytest.mark.asyncio
async def test_nothing_affordable(patch_catalog):
    assert await tools.find_products_under_budget(0.50) == []


@pytest.mark.asyncio
async def test_cheapest_item_only(patch_catalog):
    result = await tools.find_products_under_budget(1.00)
    assert [p["name"] for p in result] == ["The Comet Book"]


@pytest.mark.asyncio
async def test_one_cent_below_boundary(patch_catalog):
    result = await tools.find_products_under_budget(21.94)
    assert [p["name"] for p in result] == ["The Comet Book"]


@pytest.mark.asyncio
async def test_exact_boundary_is_included(patch_catalog):
    """Written without AI. price == budget must qualify."""
    result = await tools.find_products_under_budget(21.95)
    assert [p["name"] for p in result] == ["The Comet Book", "Lens Cleaning Kit"]


@pytest.mark.asyncio
async def test_seventy_dollars_ordered_cheapest_first(patch_catalog):
    result = await tools.find_products_under_budget(70.00)
    assert [p["name"] for p in result] == [
        "The Comet Book",
        "Lens Cleaning Kit",
        "Red Flashlight",
        "Solar Filter",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("budget", [0, -5])
async def test_invalid_budget_returns_error(patch_catalog, budget):
    result = await tools.find_products_under_budget(budget)
    assert isinstance(result, str) and result.startswith("Error")


@pytest.mark.asyncio
async def test_response_contains_no_description(patch_catalog):
    result = await tools.find_products_under_budget(70.00)
    assert all(set(p) == {"id", "name", "price_usd"} for p in result)


@pytest.mark.asyncio
async def test_upstream_failure_is_not_an_empty_list(patch_catalog_failure):
    result = await tools.find_products_under_budget(70.00)
    assert isinstance(result, str) and result.startswith("Error")
