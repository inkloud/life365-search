from types import SimpleNamespace

from app.domain.search import SearchQuery
from app.infrastructure.opensearch.search_repository import OpenSearchRepository


def test_build_text_query_includes_isin_term():
    repo: OpenSearchRepository = OpenSearchRepository(client=SimpleNamespace())  # type: ignore[arg-type]

    query = repo._build_text_query(SearchQuery(text="DETPUPD03228", language="it"))

    assert "bool" in query
    assert query["bool"]["minimum_should_match"] == 1
    should_clauses = query["bool"]["should"]
    assert {"term": {"isin": {"value": "DETPUPD03228", "boost": 10}}} in should_clauses


def test_build_text_query_without_text_uses_match_all():
    repo: OpenSearchRepository = OpenSearchRepository(client=SimpleNamespace())  # type: ignore[arg-type]

    query = repo._build_text_query(SearchQuery(text=None))

    assert query == {"match_all": {}}
