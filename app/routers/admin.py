from fastapi import APIRouter

from app.infrastructure.life365_api.client import Life365ApiClient
from app.infrastructure.opensearch.bulk_indexer import BulkIndexer
from app.infrastructure.opensearch.client import opensearch_client_context
from app.infrastructure.opensearch.index_manager import IndexManager
from app.services.indexing_service import IndexingService

router: APIRouter = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reindex")
async def reindex_all() -> dict[str, str]:
    async with opensearch_client_context() as os_client:
        api_client: Life365ApiClient = Life365ApiClient(
            base_url="https://b2b.life365.eu"
        )
        index_manager: IndexManager = IndexManager(os_client)
        bulk_indexer: BulkIndexer = BulkIndexer(os_client)

        service: IndexingService = IndexingService(
            api_client, index_manager, bulk_indexer
        )

        new_index: str = await service.reindex_all()

    return {"status": "done", "index": new_index}
