import logging
from typing import Any, cast

from opensearchpy import AsyncOpenSearch
from opensearchpy.exceptions import OpenSearchException

from app.domain.search import SearchHit, SearchQuery, SearchResult
from app.services.exceptions import SearchUnavailableError
from app.services.search_repository import SearchRepository
from app.settings import get_settings

logger = logging.getLogger(__name__)


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
            "bool": {
                "should": [
                    {
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
                    },
                    {"term": {"isin": {"value": query.text, "boost": 10}}},
                    {"term": {"barcodes": {"value": query.text, "boost": 10}}},
                ],
                "minimum_should_match": 1,
            }
        }

    def _build_exact_identifier_query(self, text: str) -> dict[str, Any]:
        return {
            "bool": {
                "should": [
                    {"term": {"isin": {"value": text}}},
                    {"term": {"barcodes": {"value": text}}},
                ],
                "minimum_should_match": 1,
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

        if query.type1:
            filters.append({"term": {"type1": query.type1}})

        if query.type2:
            filters.append({"term": {"type2": query.type2}})

        filters.append({"term": {"is_available": query.is_available}})
        filters.append({"term": {"is_visible": query.is_visible}})

        return filters

    def _build_sort(self, query: SearchQuery) -> list[Any]:
        if query.sort == "newest":
            return [{"created_at": {"order": "desc"}}]

        if query.sort == "brand":
            return [{"brand": {"order": "asc"}}]

        return ["_score"]

    def _build_aggregations(self) -> dict[str, Any]:
        return {
            "brand": {
                "terms": {
                    "field": "brand",
                    "size": 1000,
                    "order": {"_count": "desc"},
                }
            },
            "category_level_1": {
                "terms": {
                    "field": "category_level_1_id",
                    "size": 1000,
                    "order": {"_count": "desc"},
                }
            },
            "category_level_2": {
                "terms": {
                    "field": "category_level_2_id",
                    "size": 1000,
                    "order": {"_count": "desc"},
                }
            },
            "category_level_3": {
                "terms": {
                    "field": "category_level_3_id",
                    "size": 1000,
                    "order": {"_count": "desc"},
                }
            },
            "type1": {
                "terms": {
                    "field": "type1",
                    "size": 1000,
                    "order": {"_count": "desc"},
                }
            },
            "type2": {
                "terms": {
                    "field": "type2",
                    "size": 1000,
                    "order": {"_count": "desc"},
                }
            },
        }

    def _build_search_body(
        self,
        query: SearchQuery,
        *,
        text_query: dict[str, Any],
    ) -> dict[str, Any]:
        from_: int = (query.page - 1) * query.page_size

        return {
            "query": {
                "bool": {
                    "must": text_query,
                    "filter": self._build_filters(query),
                }
            },
            "from": from_,
            "size": query.page_size,
            "sort": self._build_sort(query),
            "aggs": self._build_aggregations(),
        }

    async def _execute_search(self, body: dict[str, Any]) -> dict[str, Any]:
        try:
            response: dict[str, Any] = await self._client.search(
                index=self._alias, body=body
            )
        except OpenSearchException:
            raise SearchUnavailableError("OpenSearch query failed")

        return response

    def _map_search_response(
        self, response: dict[str, Any], query: SearchQuery
    ) -> SearchResult:
        total = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]
        groups = self._map_groups(response)

        logger.debug("Search returned %d results", total)

        results: list[SearchHit] = [self._map_hit(hit, query.language) for hit in hits]

        return SearchResult(
            total=total,
            page=query.page,
            page_size=query.page_size,
            results=results,
            groups=groups,
        )

    async def search(self, query: SearchQuery) -> SearchResult:
        logger.debug(
            "Executing search | text=%s | page=%d | size=%d",
            query.text,
            query.page,
            query.page_size,
        )

        if query.text:
            exact_body: dict[str, Any] = self._build_search_body(
                query,
                text_query=self._build_exact_identifier_query(query.text),
            )
            exact_response = await self._execute_search(exact_body)
            exact_total = exact_response["hits"]["total"]["value"]

            if exact_total > 0:
                logger.debug("Exact identifier match found: %d results", exact_total)
                return self._map_search_response(exact_response, query)

        body: dict[str, Any] = self._build_search_body(
            query,
            text_query=self._build_text_query(query),
        )
        response = await self._execute_search(body)

        return self._map_search_response(response, query)

    def _extract_terms_group(
        self, aggregations_dict: dict[str, object], group_key: str
    ) -> dict[str, int]:
        group_agg = aggregations_dict.get(group_key)
        if not isinstance(group_agg, dict):
            return {}

        group_agg_dict = cast(dict[str, object], group_agg)
        buckets = group_agg_dict.get("buckets")
        if not isinstance(buckets, list):
            return {}
        buckets_list = cast(list[object], buckets)

        grouped_values: dict[str, int] = {}

        for bucket in buckets_list:
            if not isinstance(bucket, dict):
                continue

            bucket_dict = cast(dict[str, object], bucket)
            key = bucket_dict.get("key")
            count = bucket_dict.get("doc_count")

            if isinstance(count, int) and isinstance(key, (int, str)):
                grouped_values[str(key)] = count

        return grouped_values

    def _map_groups(self, response: dict[str, Any]) -> dict[str, dict[str, int]]:
        aggregations = response.get("aggregations")

        if not isinstance(aggregations, dict):
            return {
                "brand": {},
                "category_level_1": {},
                "category_level_2": {},
                "category_level_3": {},
                "type1": {},
                "type2": {},
            }

        aggregations_dict = cast(dict[str, object], aggregations)
        return {
            "brand": self._extract_terms_group(aggregations_dict, "brand"),
            "category_level_1": self._extract_terms_group(
                aggregations_dict, "category_level_1"
            ),
            "category_level_2": self._extract_terms_group(
                aggregations_dict, "category_level_2"
            ),
            "category_level_3": self._extract_terms_group(
                aggregations_dict, "category_level_3"
            ),
            "type1": self._extract_terms_group(aggregations_dict, "type1"),
            "type2": self._extract_terms_group(aggregations_dict, "type2"),
        }

    def _map_hit(self, hit: dict[str, Any], language: str) -> SearchHit:
        source = hit["_source"]

        title_field: str = f"title_{language}"

        return SearchHit(
            product_id=source["product_id"],
            title=source.get(title_field) or "",
            brand=source.get("brand"),
            is_available=source.get("is_available", False),
        )
