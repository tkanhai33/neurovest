"""
Read-only official Canadian economic-release feeds.

Only release titles, issuer names, timestamps, and source links are
returned. No database writes, broker access, or trading actions occur.
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


_CACHE_TTL = timedelta(minutes=5)
_RSS = "{http://purl.org/rss/1.0/}"
_DC = "{http://purl.org/dc/elements/1.1/}"
_ATOM = "{http://www.w3.org/2005/Atom}"

_BANK_OF_CANADA_PRESS_RELEASES = (
    "https://www.bankofcanada.ca/content_type/"
    "press-releases/feed/"
)

_STATISTICS_CANADA_DAILY = (
    "https://www150.statcan.gc.ca/n1/rss/"
    "dai-quo/0-eng.atom"
)

_ECONOMIC_TITLE_PATTERN = re.compile(
    r"\b("
    r"economic|economy|inflation|consumer price|"
    r"gross domestic product|\bgdp\b|"
    r"employment|labour|labor|unemployment|"
    r"earnings|wages|retail trade|wholesale trade|"
    r"international trade|manufacturing|"
    r"housing|building permits|investment|"
    r"productivity|interest rate|financial"
    r")\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class OfficialEconomicRelease:
    title: str
    issuer: str
    published_at: datetime
    url: str


_cached_at: datetime | None = None
_cached_releases: tuple[OfficialEconomicRelease, ...] = ()


def _text(element) -> str:
    if element is None:
        return ""

    return " ".join(
        " ".join(part.split())
        for part in element.itertext()
        if part and part.strip()
    ).strip()


def _parse_timestamp(value: str) -> datetime:
    normalized = str(value or "").strip()

    if not normalized:
        raise ValueError("Official feed item has no timestamp.")

    parsed = datetime.fromisoformat(
        normalized.replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def _download_xml(url: str) -> ET.Element:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "NeuroVestOfficialEconomicFeeds/1.0"
            ),
        },
    )

    with urlopen(request, timeout=20) as response:
        payload = response.read(1_500_000)

    return ET.fromstring(payload)


def _is_economic_release(
    release: OfficialEconomicRelease,
) -> bool:
    return bool(
        _ECONOMIC_TITLE_PATTERN.search(
            release.title
        )
    )


def _bank_of_canada_releases() -> list[OfficialEconomicRelease]:
    root = _download_xml(
        _BANK_OF_CANADA_PRESS_RELEASES
    )

    releases: list[OfficialEconomicRelease] = []

    for item in root.findall(f".//{_RSS}item"):
        title = _text(item.find(f"{_RSS}title"))
        url = _text(item.find(f"{_RSS}link"))
        published = _text(item.find(f"{_DC}date"))

        if title and url and published:
            releases.append(
                OfficialEconomicRelease(
                    title=title,
                    issuer="Bank of Canada",
                    published_at=_parse_timestamp(
                        published
                    ),
                    url=url,
                )
            )

    return releases


def _statistics_canada_releases() -> list[OfficialEconomicRelease]:
    root = _download_xml(
        _STATISTICS_CANADA_DAILY
    )

    releases: list[OfficialEconomicRelease] = []

    for entry in root.findall(f".//{_ATOM}entry"):
        title = _text(entry.find(f"{_ATOM}title"))
        link = entry.find(f"{_ATOM}link")
        published = _text(entry.find(f"{_ATOM}updated"))

        url = (
            str(link.get("href", "")).strip()
            if link is not None
            else ""
        )

        if title and url and published:
            releases.append(
                OfficialEconomicRelease(
                    title=title,
                    issuer="Statistics Canada",
                    published_at=_parse_timestamp(
                        published
                    ),
                    url=url,
                )
            )

    return releases


def fetch_official_economic_releases(
    *,
    limit: int = 5,
    use_cache: bool = True,
) -> list[OfficialEconomicRelease]:
    global _cached_at, _cached_releases

    bounded_limit = max(1, min(int(limit), 10))
    now = datetime.now(UTC)

    if (
        use_cache
        and _cached_at is not None
        and now - _cached_at <= _CACHE_TTL
    ):
        return list(_cached_releases[:bounded_limit])

    releases: list[OfficialEconomicRelease] = []
    errors: list[str] = []

    for loader in (
        _bank_of_canada_releases,
        _statistics_canada_releases,
    ):
        try:
            releases.extend(loader())
        except Exception as error:
            errors.append(
                type(error).__name__ + ": " + str(error)
            )

    unique: dict[str, OfficialEconomicRelease] = {}

    for release in releases:
        if _is_economic_release(release):
            unique[release.url] = release

    ordered = tuple(
        sorted(
            unique.values(),
            key=lambda release: release.published_at,
            reverse=True,
        )
    )

    if not ordered:
        detail = "; ".join(errors) or "no releases returned"
        raise RuntimeError(
            "Official economic feeds were unavailable: "
            + detail
        )

    _cached_at = now
    _cached_releases = ordered

    return list(ordered[:bounded_limit])


__all__ = [
    "OfficialEconomicRelease",
    "fetch_official_economic_releases",
]
