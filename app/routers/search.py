from fastapi import APIRouter

from app.infrastructure.opensearch.client import opensearch_client_context
from app.infrastructure.opensearch.health import check_opensearch_health

router: APIRouter = APIRouter(tags=["search"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    async with opensearch_client_context() as client:
        ok: bool = await check_opensearch_health(client)

    return {"api": "ok", "opensearch": "ok" if ok else "unreachable"}
