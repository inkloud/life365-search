import httpx

from app.infrastructure.life365_api.dto import CategoryDTO, ProductDTO


class Life365ApiClient:
    def __init__(self, base_url: str):
        self._base_url: str = base_url

    async def get_categories_tree(self) -> list[CategoryDTO]:
        url: str = f"{self._base_url}/api/warehouse/categoriesTree"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response: httpx.Response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        return [CategoryDTO.model_validate(item) for item in data]

    async def get_products_by_level3(self, level3_id: int) -> list[ProductDTO]:
        url: str = f"{self._base_url}/api/products/level_3/{level3_id}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response: httpx.Response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        return [ProductDTO.model_validate(item) for item in data]
