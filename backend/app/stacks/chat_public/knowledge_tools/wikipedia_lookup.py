"""
Read-only Wikipedia lookup for straightforward general questions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


_API_URL = "https://en.wikipedia.org/w/api.php"
_CACHE_TTL = timedelta(hours=1)

_PREFIXES = (
    "what is ",
    "what are ",
    "who is ",
    "who was ",
    "tell me about ",
    "explain ",
    "define ",
    "where is ",
    "when was ",
)

_BLOCKED_TERMS = (
    "weather",
    "temperature",
    "temp ",
    "stock",
    "price",
    "quote",
    "market",
    "portfolio",
    "economic",
    "interest rate",
    "integral",
    "derivative",
    "differentiate",
    "solve ",
    "matrix",
    "determinant",
)

_LINK_TERMS = (
    " link",
    " source",
    " sources",
    " wikipedia",
    " read more",
    " learn more",
)


@dataclass(frozen=True, slots=True)
class WikipediaArticle:
    title: str
    summary: str
    url: str


_cached_at: dict[str, datetime] = {}
_cached_articles: dict[str, WikipediaArticle] = {}


def extract_wikipedia_topic(message: str) -> str | None:
    source = str(message or "").strip()
    lowered = source.casefold()

    for prefix in _PREFIXES:
        if not lowered.startswith(prefix):
            continue

        topic = source[len(prefix):].split(
            "?",
            1,
        )[0].strip(" .,!?:;\n\t")

        lowered_topic = topic.casefold()

        if (
            not topic
            or any(
                term in lowered_topic
                for term in _BLOCKED_TERMS
            )
        ):
            return None

        return topic

    return None


def wikipedia_link_requested(message: str) -> bool:
    lowered = " " + str(message or "").casefold()

    return any(
        term in lowered
        for term in _LINK_TERMS
    )


def _fetch_json(params: dict) -> dict:
    request = Request(
        _API_URL + "?" + urlencode(params),
        headers={
            "Accept": "application/json",
            "User-Agent": "NeuroVestWikipediaLookup/1.0",
        },
    )

    with urlopen(request, timeout=20) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def _short_summary(value: str) -> str:
    summary = " ".join(str(value or "").split())

    if len(summary) <= 950:
        return summary

    return (
        summary[:950]
        .rsplit(" ", 1)[0]
        .strip()
        + "…"
    )


def lookup_wikipedia_article(
    topic: str,
    *,
    use_cache: bool = True,
) -> WikipediaArticle:
    requested_topic = str(topic or "").strip()

    if not requested_topic:
        raise ValueError("A Wikipedia topic is required.")

    cache_key = requested_topic.casefold()
    now = datetime.now(UTC)

    if (
        use_cache
        and cache_key in _cached_at
        and cache_key in _cached_articles
        and now - _cached_at[cache_key] <= _CACHE_TTL
    ):
        return _cached_articles[cache_key]

    search = _fetch_json(
        {
            "action": "query",
            "list": "search",
            "srsearch": requested_topic,
            "srlimit": 1,
            "format": "json",
            "formatversion": 2,
        }
    )

    matches = (
        search.get("query", {})
        .get("search", [])
    )

    if not matches:
        raise LookupError(
            "No matching Wikipedia article was found."
        )

    title = str(matches[0].get("title", "")).strip()

    article = _fetch_json(
        {
            "action": "query",
            "prop": "extracts|info",
            "titles": title,
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "format": "json",
            "formatversion": 2,
        }
    )

    pages = article.get("query", {}).get("pages", [])

    if not pages:
        raise LookupError(
            "Wikipedia article details were unavailable."
        )

    page = pages[0]
    summary = _short_summary(page.get("extract", ""))
    url = str(page.get("fullurl", "")).strip()

    if not summary or not url:
        raise LookupError(
            "Wikipedia article summary was unavailable."
        )

    result = WikipediaArticle(
        title=str(page.get("title") or title),
        summary=summary,
        url=url,
    )

    _cached_at[cache_key] = now
    _cached_articles[cache_key] = result

    return result


__all__ = [
    "WikipediaArticle",
    "extract_wikipedia_topic",
    "lookup_wikipedia_article",
    "wikipedia_link_requested",
]
