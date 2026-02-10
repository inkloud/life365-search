from app.domain.category import CategoryPath, CategoryTitle
from app.domain.product import Product
from app.infrastructure.life365_api.dto import BrandDTO, ProductDTO, StockRowDTO
from app.infrastructure.life365_api.mappers import map_product


def test_map_product_basic():
    dto: ProductDTO = ProductDTO(
        id=1,
        titles={"it": "Prodotto"},
        descriptions={},
        keywords={},
        brand=BrandDTO(brand_name="Devia"),
        product_stocks=[StockRowDTO(stock=5)],
        level_1=1,
        level_2=2,
        level_3=3,
    )

    category: CategoryPath = CategoryPath(
        level_1_id=1,
        level_1_title=CategoryTitle(it="L1"),
        level_2_id=2,
        level_2_title=CategoryTitle(it="L2"),
        level_3_id=3,
        level_3_title=CategoryTitle(it="L3"),
    )

    product: Product = map_product(dto, category)

    assert product.id == 1
    assert product.brand == "Devia"
    assert product.stock.is_available is True
