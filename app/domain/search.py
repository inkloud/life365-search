from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    text: str | None = None

    category_level_1: int | None = None
    category_level_2: int | None = None
    category_level_3: int | None = None

    brand: str | None = None

    is_available: bool = True
    is_visible: bool = True
    is_outlet: bool = False

    page: int = 1
    page_size: int = 20

    language: str = "it"

    sort: str = "relevance"


@dataclass(frozen=True)
class SearchHit:
    product_id: int
    title: str
    brand: str | None
    is_available: bool
    is_outlet: bool


@dataclass(frozen=True)
class SearchResult:
    total: int
    page: int
    page_size: int
    results: list[SearchHit]
