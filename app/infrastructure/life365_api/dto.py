from typing import Any

from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int
    title: dict[str, str]
    zchildren: list["CategoryDTO"] = []

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "CategoryDTO":
        return cls.model_validate(data)


CategoryDTO.model_rebuild()


class StockRowDTO(BaseModel):
    stock: int | None = 0
    invisible: bool = False
    outlet: bool = False


class BrandDTO(BaseModel):
    brand_name: str | None = None


class ProductDTO(BaseModel):
    id: int
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    keywords: dict[str, str] = {}
    brand: BrandDTO | None = None
    product_stocks: list[StockRowDTO] = []
    level_1: int
    level_2: int
    level_3: int
    created_at: str | None = None
    updated_at: str | None = None
