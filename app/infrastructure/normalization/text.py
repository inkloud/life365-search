import html
import re

from app.domain.product import MultilingualText

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(value: str) -> str:
    res: str = html.unescape(value)
    res: str = _TAG_RE.sub(" ", res)

    return res


def normalize_whitespace(value: str) -> str:
    res: str = value.replace("\u00a0", " ")
    res: str = _WS_RE.sub(" ", res)
    return res.strip()


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    v: str = value.strip()
    if len(v) == 0:
        return None

    if "<" in v and ">" in v:
        v: str = strip_html(v)

    v: str = normalize_whitespace(v)

    return v if len(v) > 0 else None


def normalize_multilingual_text(text: MultilingualText) -> MultilingualText:
    return MultilingualText(
        it=normalize_text(text.it),
        en=normalize_text(text.en),
        cn=normalize_text(text.cn),
    )
