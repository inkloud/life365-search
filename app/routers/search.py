from fastapi import APIRouter

from app.infrastructure.opensearch.client import OpenSearchClient
from app.infrastructure.opensearch.health import check_opensearch_health

router: APIRouter = APIRouter(tags=["search"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    os_client: OpenSearchClient = OpenSearchClient()

    ok: bool = await check_opensearch_health(os_client.client)
    await os_client.close()

    return {"api": "ok", "opensearch": "ok" if ok else "unreachable"}
