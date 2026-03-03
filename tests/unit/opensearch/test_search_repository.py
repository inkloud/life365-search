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


def test_build_exact_identifier_query_matches_isin_and_barcodes():
    repo: OpenSearchRepository = OpenSearchRepository(client=SimpleNamespace())  # type: ignore[arg-type]

    query = repo._build_exact_identifier_query("DETPUPD03228")

    assert query == {
        "bool": {
            "should": [
                {"term": {"isin": {"value": "DETPUPD03228"}}},
                {"term": {"barcodes": {"value": "DETPUPD03228"}}},
            ],
            "minimum_should_match": 1,
        }
    }


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
            },
            "category_level_1": {
                "buckets": [
                    {"key": 1, "doc_count": 10},
                    {"key": 14, "doc_count": 2},
                ]
            },
            "category_level_2": {"buckets": [{"key": 188, "doc_count": 6}]},
            "category_level_3": {"buckets": [{"key": 1134, "doc_count": 4}]},
            "type1": {"buckets": [{"key": "200W", "doc_count": 3}]},
            "type2": {"buckets": [{"key": "Blue-White", "doc_count": 2}]},
        },
    }

    client = SimpleNamespace(search=AsyncMock(return_value=response))
    repo = OpenSearchRepository(client=client)  # type: ignore[arg-type]

    result = await repo.search(SearchQuery(text="Toner", language="it"))

    assert result.groups == {
        "brand": {"Pro-Brother": 6, "Pro-Canon": 4},
        "category_level_1": {"1": 10, "14": 2},
        "category_level_2": {"188": 6},
        "category_level_3": {"1134": 4},
        "type1": {"200W": 3},
        "type2": {"Blue-White": 2},
    }

    search_body = client.search.await_args.kwargs["body"]
    assert "aggs" in search_body
    assert search_body["aggs"]["brand"]["terms"]["field"] == "brand"
    assert (
        search_body["aggs"]["category_level_1"]["terms"]["field"]
        == "category_level_1_id"
    )
    assert (
        search_body["aggs"]["category_level_2"]["terms"]["field"]
        == "category_level_2_id"
    )
    assert (
        search_body["aggs"]["category_level_3"]["terms"]["field"]
        == "category_level_3_id"
    )
    assert search_body["aggs"]["type1"]["terms"]["field"] == "type1"
    assert search_body["aggs"]["type2"]["terms"]["field"] == "type2"


@pytest.mark.asyncio
async def test_search_prioritizes_exact_identifier_matches():
    exact_response = {
        "hits": {
            "total": {"value": 1},
            "hits": [
                {
                    "_source": {
                        "product_id": 2455,
                        "title_it": "B Prodotti per Test magazzino GNU102",
                        "brand": "Z-Brand",
                        "is_available": True,
                    }
                }
            ],
        },
        "aggregations": {
            "brand": {"buckets": [{"key": "Z-Brand", "doc_count": 1}]},
            "category_level_1": {"buckets": [{"key": 1, "doc_count": 1}]},
            "category_level_2": {"buckets": [{"key": 51, "doc_count": 1}]},
            "category_level_3": {"buckets": [{"key": 1056, "doc_count": 1}]},
            "type1": {"buckets": []},
            "type2": {"buckets": []},
        },
    }

    client = SimpleNamespace(search=AsyncMock(return_value=exact_response))
    repo = OpenSearchRepository(client=client)  # type: ignore[arg-type]

    result = await repo.search(SearchQuery(text="DIYCAN-040", language="it"))

    assert result.total == 1
    assert [hit.product_id for hit in result.results] == [2455]
    assert client.search.await_count == 1
    first_body = client.search.await_args.kwargs["body"]
    should_clauses = first_body["query"]["bool"]["must"]["bool"]["should"]
    assert {"term": {"isin": {"value": "DIYCAN-040"}}} in should_clauses
    assert {"term": {"barcodes": {"value": "DIYCAN-040"}}} in should_clauses


@pytest.mark.asyncio
async def test_search_falls_back_to_full_text_when_no_exact_identifier_match():
    no_exact_response = {
        "hits": {"total": {"value": 0}, "hits": []},
        "aggregations": {
            "brand": {"buckets": []},
            "category_level_1": {"buckets": []},
            "category_level_2": {"buckets": []},
            "category_level_3": {"buckets": []},
            "type1": {"buckets": []},
            "type2": {"buckets": []},
        },
    }
    full_text_response = {
        "hits": {
            "total": {"value": 1},
            "hits": [
                {
                    "_source": {
                        "product_id": 11071,
                        "title_it": "Black Compatible HP M552dn,M553dn,M577dn-6K#508A/Canon 040",
                        "brand": "Pro-HP",
                        "is_available": True,
                    }
                }
            ],
        },
        "aggregations": {
            "brand": {"buckets": [{"key": "Pro-HP", "doc_count": 1}]},
            "category_level_1": {"buckets": [{"key": 1, "doc_count": 1}]},
            "category_level_2": {"buckets": [{"key": 82, "doc_count": 1}]},
            "category_level_3": {"buckets": [{"key": 1071, "doc_count": 1}]},
            "type1": {"buckets": [{"key": "Toner Cartridge", "doc_count": 1}]},
            "type2": {"buckets": [{"key": "HP508A", "doc_count": 1}]},
        },
    }

    client = SimpleNamespace(
        search=AsyncMock(side_effect=[no_exact_response, full_text_response])
    )
    repo = OpenSearchRepository(client=client)  # type: ignore[arg-type]

    result = await repo.search(SearchQuery(text="DIYCAN-040", language="it"))

    assert result.total == 1
    assert [hit.product_id for hit in result.results] == [11071]
    assert client.search.await_count == 2

    first_body = client.search.await_args_list[0].kwargs["body"]
    first_should_clauses = first_body["query"]["bool"]["must"]["bool"]["should"]
    assert {"term": {"isin": {"value": "DIYCAN-040"}}} in first_should_clauses

    second_body = client.search.await_args_list[1].kwargs["body"]
    second_should_clauses = second_body["query"]["bool"]["must"]["bool"]["should"]
    assert any("multi_match" in clause for clause in second_should_clauses)
