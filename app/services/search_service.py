from app.domain.search import SearchQuery, SearchResult
from app.services.search_repository import SearchRepository


class SearchService:
    def __init__(self, repository: SearchRepository):
        self._repository: SearchRepository = repository

    async def search(self, query: SearchQuery) -> SearchResult:
        if query.page < 1:
            raise ValueError("Page must be >= 1")

        if query.page_size > 100:
            raise ValueError("Max page_size is 100")

        return await self._repository.search(query)
