from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.category import CategoryPath, CategoryTitle
from app.domain.product import MultilingualText, Product, StockInfo
from app.infrastructure.opensearch.bulk_indexer import BulkIndexer


def _make_product(product_id: int) -> Product:
    return Product(
        id=product_id,
        brand="Brand",
        title=MultilingualText(it="Titolo"),
        description=MultilingualText(it="Descrizione"),
        keywords=MultilingualText(it="Parola"),
        category=CategoryPath(
            level_1_id=1,
            level_1_title=CategoryTitle(it="L1"),
            level_2_id=2,
            level_2_title=CategoryTitle(it="L2"),
            level_3_id=3,
            level_3_title=CategoryTitle(it="L3"),
        ),
        stock=StockInfo(is_available=True, is_visible=True, is_outlet=False),
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_index_batch_builds_operations_with_expected_ids():
    client = SimpleNamespace(
        bulk=AsyncMock(return_value={"errors": False}),
        indices=SimpleNamespace(refresh=AsyncMock()),
    )
    indexer: BulkIndexer = BulkIndexer(client=client, chunk_size=500)  # type: ignore
    products: list[Product] = [_make_product(10), _make_product(20)]

    with patch(
        "app.infrastructure.opensearch.bulk_indexer.build_product_document",
        side_effect=[{"doc": "one"}, {"doc": "two"}],
    ):
        await indexer._index_batch("products-index", products)  # type: ignore

    client.bulk.assert_awaited_once()
    call_kwargs = client.bulk.await_args.kwargs
    operations = call_kwargs["body"]

    assert call_kwargs["params"] == {"refresh": "false"}
    assert len(operations) == 4
    assert operations[0]["index"]["_id"] == 10
    assert operations[0]["index"]["_index"] == "products-index"
    assert operations[1] == {"doc": "one"}
    assert operations[2]["index"]["_id"] == 20
    assert operations[3] == {"doc": "two"}


@pytest.mark.asyncio
async def test_index_batch_raises_when_bulk_returns_errors():
    client = SimpleNamespace(
        bulk=AsyncMock(
            return_value={
                "errors": True,
                "items": [{"index": {"_id": "10", "error": {"type": "mapper_error"}}}],
            }
        ),
        indices=SimpleNamespace(refresh=AsyncMock()),
    )
    indexer = BulkIndexer(client=client, chunk_size=500)  # type: ignore

    with patch(
        "app.infrastructure.opensearch.bulk_indexer.build_product_document",
        return_value={"doc": "one"},
    ):
        with pytest.raises(RuntimeError, match="Bulk indexing failed for 1 documents"):
            await indexer._index_batch("products-index", [_make_product(10)])  # type: ignore
