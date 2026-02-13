from typing import Any

from opensearchpy import AsyncOpenSearch

from app.domain.search import SearchHit, SearchQuery, SearchResult
from app.services.search_repository import SearchRepository
from app.settings import get_settings


class OpenSearchRepository(SearchRepository):
    def __init__(self, client: AsyncOpenSearch):
        self._client = client
        self._settings = get_settings()
        self._alias = f"{self._settings.opensearch_index_prefix}_current"

    def _build_text_query(self, query: SearchQuery) -> dict[str, Any]:
        if not query.text:
            return {"match_all": {}}

        lang: str = query.language

        title_field: str = f"title_{lang}"
        description_field: str = f"description_{lang}"
        keywords_field: str = f"keywords_{lang}"
        category_field: str = f"category_level_3_title_{lang}"

        return {
            "multi_match": {
                "query": query.text,
                "fields": [
                    f"{title_field}^3",
                    f"{keywords_field}^2",
                    description_field,
                    category_field,
                ],
                "type": "best_fields",
            }
        }

    def _build_filters(self, query: SearchQuery) -> list[dict[str, Any]]:
        filters: list[dict[str, Any]] = []

        if query.category_level_1 is not None:
            filters.append({"term": {"category_level_1_id": query.category_level_1}})

        if query.category_level_2 is not None:
            filters.append({"term": {"category_level_2_id": query.category_level_2}})

        if query.category_level_3 is not None:
            filters.append({"term": {"category_level_3_id": query.category_level_3}})

        if query.brand:
            filters.append({"term": {"brand": query.brand}})

        filters.append({"term": {"is_available": query.is_available}})
        filters.append({"term": {"is_visible": query.is_visible}})
        filters.append({"term": {"is_outlet": query.is_outlet}})

        return filters

    def _build_sort(self, query: SearchQuery) -> list[Any]:
        if query.sort == "newest":
            return [{"created_at": {"order": "desc"}}]

        if query.sort == "brand":
            return [{"brand": {"order": "asc"}}]

        return ["_score"]

    async def search(self, query: SearchQuery) -> SearchResult:
        from_: int = (query.page - 1) * query.page_size

        body: dict[str, Any] = {
            "query": {
                "bool": {
                    "must": self._build_text_query(query),
                    "filter": self._build_filters(query),
                }
            },
            "from": from_,
            "size": query.page_size,
            "sort": self._build_sort(query),
        }

        response = await self._client.search(index=self._alias, body=body)

        total = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]

        results: list[SearchHit] = [self._map_hit(hit, query.language) for hit in hits]

        return SearchResult(
            total=total, page=query.page, page_size=query.page_size, results=results
        )

    def _map_hit(self, hit: dict[str, Any], language: str) -> SearchHit:
        source = hit["_source"]

        title_field: str = f"title_{language}"

        return SearchHit(
            product_id=source["product_id"],
            title=source.get(title_field) or "",
            brand=source.get("brand"),
            is_available=source.get("is_available", False),
            is_outlet=source.get("is_outlet", False),
        )
