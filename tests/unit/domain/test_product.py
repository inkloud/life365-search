from app.domain.product import MultilingualText, StockInfo, aggregate_stock


def test_multilingual_fallback():
    text: MultilingualText = MultilingualText(it="ciao", en="hello")

    assert text.best_for("it") == "ciao"
    assert text.best_for("en") == "hello"
    assert text.best_for("cn") == "ciao"


def test_stock_aggregation():
    rows: list[dict[str, bool | int]] = [
        {"stock": 0, "invisible": False, "outlet": False},
        {"stock": 5, "invisible": False, "outlet": False},
    ]

    stock: StockInfo = aggregate_stock(rows)

    assert stock.is_available is True
    assert stock.is_visible is True
    assert stock.is_outlet is False
