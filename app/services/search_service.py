from app.domain.search import SearchQuery, SearchResult
from app.services.exceptions import InvalidSearchRequestError
from app.services.search_repository import SearchRepository


class SearchService:
    def __init__(self, repository: SearchRepository):
        self._repository: SearchRepository = repository

    async def search(self, query: SearchQuery) -> SearchResult:
        if query.page < 1:
            raise InvalidSearchRequestError("Page must be >= 1")

        if query.page_size > 100:
            raise InvalidSearchRequestError("Max page_size is 100")

        return await self._repository.search(query)
