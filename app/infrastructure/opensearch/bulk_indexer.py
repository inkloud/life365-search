from typing import Any, Iterable

from opensearchpy import AsyncOpenSearch

from app.domain.product import Product
from app.infrastructure.opensearch.document_builder import build_product_document


def chunked[T](iterable: list[T], size: int) -> Iterable[list[T]]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


class BulkIndexer:
    def __init__(self, client: AsyncOpenSearch, chunk_size: int = 500):
        self._client: AsyncOpenSearch = client
        self._chunk_size: int = chunk_size

    async def bulk_index(self, index_name: str, products: list[Product]) -> None:
        for batch in chunked(products, self._chunk_size):
            await self._index_batch(index_name, batch)
        await self._client.indices.refresh(index=index_name)

    async def _index_batch(self, index_name: str, products: list[Product]) -> None:
        operations: list[dict[str, Any]] = []

        for product in products:
            doc: dict[str, Any] = build_product_document(product)

            operations.append({"index": {"_index": index_name, "_id": product.id}})
            operations.append(doc)

        response: dict[str, Any] = await self._client.bulk(
            body=operations, params={"refresh": "false"}
        )

        if response.get("errors"):
            self._handle_bulk_errors(response)

    def _handle_bulk_errors(self, response: dict[str, Any]) -> None:
        errors: list[Any] = [
            item
            for item in response.get("items", [])
            if "error" in item.get("index", {})
        ]

        if errors:
            raise RuntimeError(f"Bulk indexing failed for {len(errors)} documents")
