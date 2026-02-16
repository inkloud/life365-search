import os
from datetime import datetime, timezone

import pytest
from opensearchpy import AsyncOpenSearch

from app.domain.category import CategoryPath, CategoryTitle
from app.domain.product import MultilingualText, Product, StockInfo
from app.domain.search import SearchQuery, SearchResult
from app.infrastructure.opensearch.bulk_indexer import BulkIndexer
from app.infrastructure.opensearch.index_manager import IndexManager
from app.infrastructure.opensearch.search_repository import OpenSearchRepository
from app.services.search_repository import SearchRepository

os.environ["OPENSEARCH_INDEX_PREFIX"] = "products_test"


def make_product(product_id: int, title: str) -> Product:
    category: CategoryPath = CategoryPath(
        level_1_id=1,
        level_1_title=CategoryTitle(it="Accessori"),
        level_2_id=2,
        level_2_title=CategoryTitle(it="Protezione"),
        level_3_id=3,
        level_3_title=CategoryTitle(it="Pellicole"),
    )

    return Product(
        id=product_id,
        brand="Devia",
        title=MultilingualText(it=title),
        description=MultilingualText(it="Descrizione prodotto"),
        keywords=MultilingualText(it="vetro temperato"),
        category=category,
        stock=StockInfo(is_available=True, is_visible=True, is_outlet=False),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_index_and_search_flow():
    client: AsyncOpenSearch = AsyncOpenSearch(hosts=["http://localhost:9200"])
    try:
        index_manager: IndexManager = IndexManager(client)
        bulk_indexer: BulkIndexer = BulkIndexer(client)
        repo: SearchRepository = OpenSearchRepository(client)

        # Create new index
        version: int = await index_manager.get_next_version()
        index_name: str = await index_manager.create_index(version)

        # Create products
        products: list[Product] = [
            make_product(1, "Pellicola Vetro Temperato"),
            make_product(2, "Custodia Silicone"),
            make_product(3, "Pellicola Privacy"),
        ]

        # Bulk index
        await bulk_indexer.bulk_index(index_name, products)

        # Switch alias
        await index_manager.switch_alias(index_name)

        # Perform search
        result: SearchResult = await repo.search(
            SearchQuery(text="pellicola", language="it")
        )

        assert result.total >= 2
        titles = [r.title for r in result.results]

        assert any("Pellicola" in t for t in titles)

        await client.indices.delete(index=index_name)
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_title_boost_ranking():
    client: AsyncOpenSearch = AsyncOpenSearch(hosts=["http://localhost:9200"])
    try:
        index_manager: IndexManager = IndexManager(client)
        bulk_indexer: BulkIndexer = BulkIndexer(client)
        repo: SearchRepository = OpenSearchRepository(client)

        version: int = await index_manager.get_next_version()
        index_name: str = await index_manager.create_index(version)

        products: list[Product] = [
            make_product(10, "iPhone Pellicola Vetro"),
            make_product(11, "Custodia iPhone"),
        ]

        await bulk_indexer.bulk_index(index_name, products)
        await index_manager.switch_alias(index_name)

        result: SearchResult = await repo.search(
            SearchQuery(text="pellicola", language="it")
        )

        assert result.results[0].product_id == 10

        await client.indices.delete(index=index_name)
    finally:
        await client.close()
