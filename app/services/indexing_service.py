import asyncio
import logging
from collections.abc import Awaitable

from app.domain.category import CategoryNode, CategoryPath, extract_level_3_paths
from app.domain.product import Product
from app.infrastructure.life365_api.client import Life365ApiClient
from app.infrastructure.life365_api.dto import CategoryDTO, ProductDTO
from app.infrastructure.life365_api.mappers import map_category, map_product
from app.infrastructure.opensearch.bulk_indexer import BulkIndexer
from app.infrastructure.opensearch.index_manager import IndexManager

logger = logging.getLogger(__name__)


class IndexingService:
    def __init__(
        self,
        api_client: Life365ApiClient,
        index_manager: IndexManager,
        bulk_indexer: BulkIndexer,
        max_concurrency: int = 5,
    ):
        self._api_client: Life365ApiClient = api_client
        self._index_manager = index_manager
        self._bulk_indexer = bulk_indexer
        self._max_concurrency: int = max_concurrency

    async def _fetch_all_products(
        self, category_paths: list[CategoryPath]
    ) -> list[Product]:
        semaphore: asyncio.Semaphore = asyncio.Semaphore(self._max_concurrency)

        async def fetch_one(category_path: CategoryPath) -> list[Product]:
            async with semaphore:
                dtos: list[ProductDTO] = await self._api_client.get_products_by_level3(
                    category_path.level_3_id
                )
                return [map_product(dto, category_path) for dto in dtos]

        tasks: list[Awaitable[list[Product]]] = [
            fetch_one(path) for path in category_paths
        ]
        results: list[list[Product]] = await asyncio.gather(*tasks)

        return [product for sublist in results for product in sublist]

    async def reindex_all(self) -> str:
        logger.info("Starting reindex process")

        version: int = await self._index_manager.get_next_version()
        index_name: str = await self._index_manager.create_index(version)
        logger.info("Index created: %s", index_name)

        category_dtos: list[CategoryDTO] = await self._api_client.get_categories_tree()
        roots: list[CategoryNode] = [map_category(dto) for dto in category_dtos]
        category_paths: list[CategoryPath] = extract_level_3_paths(roots)
        logger.info("Found %d level-3 categories", len(category_paths))

        products: list[Product] = await self._fetch_all_products(category_paths)
        logger.info("Fetched %d products", len(products))

        await self._bulk_indexer.bulk_index(index_name, products)

        logger.info("Switching alias to %s", index_name)
        await self._index_manager.switch_alias(index_name)
        logger.info("Reindex completed successfully")

        return index_name
