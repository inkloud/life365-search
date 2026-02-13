from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter, Depends

from app.domain.search import SearchQuery, SearchResult
from app.infrastructure.opensearch.client import opensearch_client_context
from app.infrastructure.opensearch.health import check_opensearch_health
from app.infrastructure.opensearch.search_repository import OpenSearchRepository
from app.routers.search_models import SearchHitResponse, SearchRequest, SearchResponse
from app.services.search_repository import SearchRepository
from app.services.search_service import SearchService

router: APIRouter = APIRouter(tags=["search"])


@asynccontextmanager
async def search_searvice_context() -> AsyncIterator[SearchService]:
    async with opensearch_client_context() as client:
        repo: SearchRepository = OpenSearchRepository(client)
        yield SearchService(repo)


@router.get("/health")
async def health_check() -> dict[str, str]:
    async with opensearch_client_context() as client:
        ok: bool = await check_opensearch_health(client)

    return {"api": "ok", "opensearch": "ok" if ok else "unreachable"}


@router.get("/search", response_model=SearchResponse)
async def search_endpoint(params: SearchRequest = Depends()):
    async with search_searvice_context() as service:
        query: SearchQuery = SearchQuery(
            text=params.q,
            category_level_1=params.category_level_1,
            category_level_2=params.category_level_2,
            category_level_3=params.category_level_3,
            brand=params.brand,
            is_available=params.available,
            is_visible=params.visible,
            is_outlet=params.outlet,
            page=params.page,
            page_size=params.page_size,
            language=params.lang,
            sort=params.sort,
        )

        result: SearchResult = await service.search(query)

        return SearchResponse(
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            results=[
                SearchHitResponse(
                    product_id=r.product_id,
                    title=r.title,
                    brand=r.brand,
                    is_available=r.is_available,
                    is_outlet=r.is_outlet,
                )
                for r in result.results
            ],
        )
