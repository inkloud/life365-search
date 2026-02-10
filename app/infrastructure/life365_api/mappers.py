from datetime import datetime

from app.domain.category import CategoryNode, CategoryPath, CategoryTitle
from app.domain.product import (
    MultilingualText,
    Product,
    aggregate_stock,
)
from app.infrastructure.life365_api.dto import CategoryDTO, ProductDTO


def map_category(dto: CategoryDTO) -> CategoryNode:
    return CategoryNode(
        id=dto.id,
        title=CategoryTitle.from_dict(dto.title),
        children=[map_category(child) for child in dto.zchildren],
    )


def map_product(dto: ProductDTO, category_path: CategoryPath) -> Product:
    return Product(
        id=dto.id,
        brand=dto.brand.brand_name if dto.brand else None,
        title=MultilingualText.from_dict(dto.titles),
        description=MultilingualText.from_dict(dto.descriptions),
        keywords=MultilingualText.from_dict(dto.keywords),
        category=category_path,
        stock=aggregate_stock([e.model_dump() for e in dto.product_stocks]),
        created_at=parse_datetime(dto.created_at),
        updated_at=parse_datetime(dto.updated_at),
    )


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
