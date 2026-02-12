from typing import Any

from app.domain.product import MultilingualText, Product
from app.infrastructure.normalization.text import normalize_multilingual_text


def build_product_document(product: Product) -> dict[str, Any]:
    title: MultilingualText = normalize_multilingual_text(product.title)
    description: MultilingualText = normalize_multilingual_text(product.description)
    keywords: MultilingualText = normalize_multilingual_text(product.keywords)

    doc: dict[str, Any] = {
        "product_id": product.id,
        "title_it": title.best_for("it"),
        "title_en": title.best_for("en"),
        "title_cn": title.best_for("cn"),
        "description_it": description.best_for("it"),
        "description_en": description.best_for("en"),
        "description_cn": description.best_for("cn"),
        "keywords_it": keywords.best_for("it"),
        "keywords_en": keywords.best_for("en"),
        "keywords_cn": keywords.best_for("cn"),
        "brand": product.brand,
        "category_level_1_id": product.category.level_1_id,
        "category_level_2_id": product.category.level_2_id,
        "category_level_3_id": product.category.level_3_id,
        "category_level_1_title_it": product.category.level_1_title.it,
        "category_level_1_title_en": product.category.level_1_title.en,
        "category_level_1_title_cn": product.category.level_1_title.cn,
        "category_level_2_title_it": product.category.level_2_title.it,
        "category_level_2_title_en": product.category.level_2_title.en,
        "category_level_2_title_cn": product.category.level_2_title.cn,
        "category_level_3_title_it": product.category.level_3_title.it,
        "category_level_3_title_en": product.category.level_3_title.en,
        "category_level_3_title_cn": product.category.level_3_title.cn,
        "is_available": product.stock.is_available,
        "is_visible": product.stock.is_visible,
        "is_outlet": product.stock.is_outlet,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }

    return {k: v for k, v in doc.items() if v is not None}
