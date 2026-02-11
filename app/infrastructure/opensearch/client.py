from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from opensearchpy import AsyncOpenSearch

from app.settings import Settings, get_settings


class OpenSearchClient:
    def __init__(self) -> None:
        settings: Settings = get_settings()

        self._client: AsyncOpenSearch = AsyncOpenSearch(
            hosts=[settings.opensearch_host],
            http_auth=(settings.opensearch_user, settings.opensearch_password)
            if settings.opensearch_user
            else None,
            use_ssl=settings.opensearch_host.startswith("https"),
            verify_certs=False,
        )

    @property
    def client(self) -> AsyncOpenSearch:
        return self._client

    async def close(self) -> None:
        await self._client.close()


@asynccontextmanager
async def opensearch_client_context() -> AsyncIterator[AsyncOpenSearch]:
    os_client: OpenSearchClient = OpenSearchClient()
    try:
        yield os_client.client
    finally:
        await os_client.close()
