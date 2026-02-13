from typing import Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    q: str | None = Field(None, description="Full-text search query")

    category_level_1: int | None = None
    category_level_2: int | None = None
    category_level_3: int | None = None

    brand: str | None = None

    available: bool = True
    visible: bool = True
    outlet: bool = False

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    lang: Literal["it", "en", "cn"] = Field("it", pattern="^(it|en|cn)$")
    sort: Literal["relevance", "newest", "brand"] = Field(
        "relevance", pattern="^(relevance|newest|brand)$"
    )


class SearchHitResponse(BaseModel):
    product_id: int
    title: str
    brand: str | None
    is_available: bool
    is_outlet: bool


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SearchHitResponse]
