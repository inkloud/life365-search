from app.infrastructure.normalization.text import normalize_text


def test_normalize_text_strips_html():
    raw: str = "<p>Hello&nbsp;<b>world</b></p>"
    assert normalize_text(raw) == "Hello world"


def test_normalize_text_empty_returns_none():
    assert normalize_text("   ") is None
    assert normalize_text("<p><br></p>") is None
