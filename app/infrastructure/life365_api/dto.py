from typing import Any

from pydantic import BaseModel, Field, field_validator


class CategoryDTO(BaseModel):
    id: int
    title: dict[str, str | None]
    zchildren: list["CategoryDTO"] = Field(default_factory=list)

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
    titles: dict[str, str | None] = Field(default_factory=dict)
    descriptions: dict[str, str | None] = Field(default_factory=dict)
    keywords: dict[str, str | None] = Field(default_factory=dict)
    brand: BrandDTO | None = None
    product_stocks: list[StockRowDTO] = Field(default_factory=list)
    level_1: int
    level_2: int
    level_3: int
    created_at: str | None = None
    updated_at: str | None = None

    @field_validator("titles", "descriptions", "keywords", mode="before")
    @classmethod
    def _none_to_empty_dict(cls, value: Any) -> Any:
        return {} if value is None else value
