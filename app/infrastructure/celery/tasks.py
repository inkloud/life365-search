from app.infrastructure.celery.app import celery_app
from app.infrastructure.life365_api.client import Life365ApiClient
from app.infrastructure.opensearch.bulk_indexer import BulkIndexer
from app.infrastructure.opensearch.client import opensearch_client_context
from app.infrastructure.opensearch.index_manager import IndexManager
from app.services.indexing_service import IndexingService


@celery_app.task(  # type: ignore
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def reindex_all_task(self):  # type: ignore
    import asyncio

    async def run() -> str:
        async with opensearch_client_context() as client:
            api_client: Life365ApiClient = Life365ApiClient(
                base_url="https://b2b.life365.eu"
            )

            index_manager: IndexManager = IndexManager(client)
            bulk_indexer: BulkIndexer = BulkIndexer(client)

            service: IndexingService = IndexingService(
                api_client, index_manager, bulk_indexer
            )

            result: str = await service.reindex_all()
            return result

    return asyncio.run(run())
