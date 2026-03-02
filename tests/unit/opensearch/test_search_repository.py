from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.domain.search import SearchQuery
from app.infrastructure.opensearch.search_repository import OpenSearchRepository


def test_build_text_query_includes_isin_term():
    repo: OpenSearchRepository = OpenSearchRepository(client=SimpleNamespace())  # type: ignore[arg-type]

    query = repo._build_text_query(SearchQuery(text="DETPUPD03228", language="it"))

    assert "bool" in query
    assert query["bool"]["minimum_should_match"] == 1
    should_clauses = query["bool"]["should"]
    assert {"term": {"isin": {"value": "DETPUPD03228", "boost": 10}}} in should_clauses
    assert {
        "term": {"barcodes": {"value": "DETPUPD03228", "boost": 10}}
    } in should_clauses


def test_build_text_query_without_text_uses_match_all():
    repo: OpenSearchRepository = OpenSearchRepository(client=SimpleNamespace())  # type: ignore[arg-type]

    query = repo._build_text_query(SearchQuery(text=None))

    assert query == {"match_all": {}}


@pytest.mark.asyncio
async def test_search_returns_brand_groups_from_aggregations():
    response = {
        "hits": {
            "total": {"value": 1},
            "hits": [
                {
                    "_source": {
                        "product_id": 1,
                        "title_it": "Toner",
                        "brand": "Pro-Brother",
                        "is_available": True,
                    }
                }
            ],
        },
        "aggregations": {
            "brand": {
                "buckets": [
                    {"key": "Pro-Brother", "doc_count": 6},
                    {"key": "Pro-Canon", "doc_count": 4},
                ]
            }
        },
    }

    client = SimpleNamespace(search=AsyncMock(return_value=response))
    repo = OpenSearchRepository(client=client)  # type: ignore[arg-type]

    result = await repo.search(SearchQuery(text="Toner", language="it"))

    assert result.groups == {"brand": {"Pro-Brother": 6, "Pro-Canon": 4}}

    search_body = client.search.await_args.kwargs["body"]
    assert "aggs" in search_body
    assert search_body["aggs"]["brand"]["terms"]["field"] == "brand"
