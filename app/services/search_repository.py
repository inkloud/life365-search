from typing import Protocol

from app.domain.search import SearchQuery, SearchResult


class SearchRepository(Protocol):
    async def search(self, query: SearchQuery) -> SearchResult: ...
