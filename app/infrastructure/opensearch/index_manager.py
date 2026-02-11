import re
from typing import Any

from opensearchpy import AsyncOpenSearch

from app.infrastructure.opensearch.mappings import build_product_index_mapping
from app.settings import get_settings


class IndexManager:
    def __init__(self, client: AsyncOpenSearch):
        self._client = client
        self._settings = get_settings()
        self._prefix = self._settings.opensearch_index_prefix
        self._alias = f"{self._prefix}_current"

    async def _list_indices(self) -> list[str]:
        indices = await self._client.indices.get_alias(index="*")
        return list(indices.keys())

    async def get_existing_versions(self) -> list[int]:
        indices: list[str] = await self._list_indices()

        pattern = re.compile(rf"{self._prefix}_v(\d+)")
        versions: list[int] = []

        for name in indices:
            match = pattern.match(name)
            if match:
                versions.append(int(match.group(1)))

        return sorted(versions)

    async def get_next_version(self) -> int:
        versions: list[int] = await self.get_existing_versions()
        return (max(versions) + 1) if versions else 1

    async def create_index(self, version: int) -> str:
        index_name: str = f"{self._prefix}_v{version}"
        mapping: dict[str, Any] = build_product_index_mapping()

        await self._client.indices.create(index=index_name, body=mapping)
        return index_name

    async def switch_alias(self, new_index: str) -> None:
        actions: list[dict[str, Any]] = []

        try:
            current = await self._client.indices.get_alias(name=self._alias)
            for index in current.keys():
                actions.append({"remove": {"index": index, "alias": self._alias}})
        except Exception:
            pass

        actions.append({"add": {"index": new_index, "alias": self._alias}})

        await self._client.indices.update_aliases(body={"actions": actions})

    async def delete_index(self, version: int) -> None:
        index_name: str = f"{self._prefix}_v{version}"
        await self._client.indices.delete(index=index_name)
