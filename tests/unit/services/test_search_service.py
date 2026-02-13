import pytest

from app.domain.search import SearchQuery, SearchResult
from app.services.search_repository import SearchRepository
from app.services.search_service import SearchService


class FakeRepo(SearchRepository):
    async def search(self, query: SearchQuery):
        return SearchResult(
            total=0, page=query.page, page_size=query.page_size, results=[]
        )


@pytest.mark.asyncio
async def test_page_validation():
    service: SearchService = SearchService(FakeRepo())

    with pytest.raises(ValueError):
        await service.search(SearchQuery(page=0))
