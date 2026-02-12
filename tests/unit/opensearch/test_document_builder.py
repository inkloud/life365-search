from datetime import datetime, timezone
from typing import Any

from app.domain.category import CategoryPath, CategoryTitle
from app.domain.product import MultilingualText, Product, StockInfo
from app.infrastructure.opensearch.document_builder import build_product_document


def test_build_product_document_normalizes_and_filters_none_fields():
    product: Product = Product(
        id=42,
        brand=None,
        title=MultilingualText(it="   ", en="<b> Hello&nbsp;World </b>", cn=None),
        description=MultilingualText(it=None, en=None, cn="  <p>Descrizione</p>  "),
        keywords=MultilingualText(it=None, en=None, cn=None),
        category=CategoryPath(
            level_1_id=1,
            level_1_title=CategoryTitle(it="L1 IT", en="L1 EN", cn=None),
            level_2_id=2,
            level_2_title=CategoryTitle(it="L2 IT", en=None, cn=None),
            level_3_id=3,
            level_3_title=CategoryTitle(it="L3 IT", en="L3 EN", cn="L3 CN"),
        ),
        stock=StockInfo(is_available=True, is_visible=True, is_outlet=False),
        created_at=None,
        updated_at=datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )

    doc: dict[str, Any] = build_product_document(product)

    assert doc["product_id"] == 42
    assert doc["title_en"] == "Hello World"
    assert doc["title_it"] == "Hello World"
    assert doc["title_cn"] == "Hello World"
    assert doc["description_cn"] == "Descrizione"
    assert doc["description_it"] == "Descrizione"
    assert doc["description_en"] == "Descrizione"
    assert doc["category_level_1_title_en"] == "L1 EN"
    assert doc["category_level_3_title_cn"] == "L3 CN"
    assert doc["updated_at"] == "2025-01-02T03:04:05+00:00"
    assert doc["is_available"] is True
    assert doc["is_visible"] is True
    assert doc["is_outlet"] is False

    assert "brand" not in doc
    assert "created_at" not in doc
    assert "keywords_it" not in doc
    assert "keywords_en" not in doc
    assert "keywords_cn" not in doc
    assert "category_level_1_title_cn" not in doc
    assert "category_level_2_title_en" not in doc
    assert "category_level_2_title_cn" not in doc
