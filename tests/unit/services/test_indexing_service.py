from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest

from app.infrastructure.life365_api.client import Life365ApiClient
from app.infrastructure.life365_api.dto import CategoryDTO, ProductDTO, StockRowDTO
from app.infrastructure.opensearch.bulk_indexer import BulkIndexer
from app.infrastructure.opensearch.index_manager import IndexManager
from app.services.indexing_service import IndexingService


@pytest.mark.asyncio
async def test_reindex_all_orders_create_bulk_and_alias_calls():
    call_order: list[str] = []

    async def create_index_side_effect(version: int) -> str:
        call_order.append("create_index")
        return f"products_v{version}"

    async def bulk_index_side_effect(index_name: str, products: list[object]) -> None:
        call_order.append("bulk_index")

    async def switch_alias_side_effect(index_name: str) -> None:
        call_order.append("switch_alias")

    categories_tree: list[CategoryDTO] = [
        CategoryDTO(
            id=1,
            title={"it": "L1"},
            zchildren=[
                CategoryDTO(
                    id=2,
                    title={"it": "L2"},
                    zchildren=[CategoryDTO(id=3, title={"it": "L3"}, zchildren=[])],
                )
            ],
        )
    ]

    products_for_level3: list[ProductDTO] = [
        ProductDTO(
            id=100,
            titles={"it": "Prodotto"},
            descriptions={},
            keywords={},
            product_stocks=[StockRowDTO(stock=5, invisible=False, outlet=False)],
            level_1=1,
            level_2=2,
            level_3=3,
        )
    ]

    get_categories_tree_mock = AsyncMock(return_value=categories_tree)
    get_products_by_level3_mock = AsyncMock(return_value=products_for_level3)
    get_next_version_mock = AsyncMock(return_value=7)
    create_index_mock = AsyncMock(side_effect=create_index_side_effect)
    switch_alias_mock = AsyncMock(side_effect=switch_alias_side_effect)
    bulk_index_mock = AsyncMock(side_effect=bulk_index_side_effect)

    api_client = cast(
        Life365ApiClient,
        SimpleNamespace(
            get_categories_tree=get_categories_tree_mock,
            get_products_by_level3=get_products_by_level3_mock,
        ),
    )
    index_manager = cast(
        IndexManager,
        SimpleNamespace(
            get_next_version=get_next_version_mock,
            create_index=create_index_mock,
            switch_alias=switch_alias_mock,
        ),
    )
    bulk_indexer = cast(
        BulkIndexer,
        SimpleNamespace(bulk_index=bulk_index_mock),
    )

    service = IndexingService(
        api_client=api_client,
        index_manager=index_manager,
        bulk_indexer=bulk_indexer,
    )

    result = await service.reindex_all()

    assert result == "products_v7"
    get_categories_tree_mock.assert_awaited_once()
    get_products_by_level3_mock.assert_awaited_once_with(3)
    create_index_mock.assert_awaited_once_with(7)
    bulk_index_mock.assert_awaited_once()
    switch_alias_mock.assert_awaited_once_with("products_v7")

    assert call_order.index("create_index") < call_order.index("bulk_index")
    assert call_order.index("bulk_index") < call_order.index("switch_alias")
