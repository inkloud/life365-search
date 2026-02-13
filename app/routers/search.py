from fastapi import APIRouter

from app.domain.search import SearchQuery, SearchResult
from app.infrastructure.opensearch.client import opensearch_client_context
from app.infrastructure.opensearch.health import check_opensearch_health
from app.infrastructure.opensearch.search_repository import OpenSearchRepository
from app.services.search_repository import SearchRepository
from app.services.search_service import SearchService

router: APIRouter = APIRouter(tags=["search"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    async with opensearch_client_context() as client:
        ok: bool = await check_opensearch_health(client)

    return {"api": "ok", "opensearch": "ok" if ok else "unreachable"}


@router.get("/search")
async def search_endpoint(q: str | None = None) -> SearchResult:
    async with opensearch_client_context() as client:
        repo: SearchRepository = OpenSearchRepository(client)
        service: SearchService = SearchService(repo)
        result: SearchResult = await service.search(SearchQuery(text=q))

        return result
