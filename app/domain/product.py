from dataclasses import dataclass
from datetime import datetime

from app.domain.category import CategoryPath


@dataclass(frozen=True)
class MultilingualText:
    it: str | None = None
    en: str | None = None
    cn: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> "MultilingualText":
        return cls(it=data.get("it"), en=data.get("en"), cn=data.get("cn"))

    def best_for(self, lang: str) -> str | None:
        if lang == "it" and self.it is not None:
            return self.it
        if lang == "en" and self.en is not None:
            return self.en
        if lang == "cn" and self.cn is not None:
            return self.cn

        if self.it is not None:
            return self.it
        if self.en is not None:
            return self.en
        if self.cn is not None:
            return self.cn


@dataclass(frozen=True)
class StockInfo:
    is_available: bool
    is_visible: bool
    is_outlet: bool


@dataclass(frozen=True)
class Product:
    id: int
    brand: str | None

    title: MultilingualText
    description: MultilingualText
    keywords: MultilingualText

    category: CategoryPath

    stock: StockInfo

    created_at: datetime | None = None
    updated_at: datetime | None = None


def aggregate_stock(rows: list[dict[str, bool | int]]) -> StockInfo:
    is_visible = any(not row.get("invisible", False) for row in rows)
    is_available = any(
        row.get("stock", 0) > 0 and not row.get("invisible", False) for row in rows
    )
    is_outlet = any(row.get("outlet", False) for row in rows)

    return StockInfo(
        is_available=is_available, is_visible=is_visible, is_outlet=is_outlet
    )
