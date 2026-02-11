import asyncio
from collections.abc import Awaitable

from app.domain.category import CategoryPath
from app.domain.product import Product
from app.infrastructure.life365_api.client import Life365ApiClient
from app.infrastructure.life365_api.mappers import ProductDTO, map_product


class IndexingService:
    def __init__(self, api_client: Life365ApiClient):
        self._api_client: Life365ApiClient = api_client
        self._max_concurrency: int = 5

    async def fetch_products_for_categories(
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
