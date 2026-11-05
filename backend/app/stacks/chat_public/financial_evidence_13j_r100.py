"""
NeuroVest R100 — financial evidence provenance.

Analyzes the already-assembled retrieval result and response.
No external requests, no model calls, no persistence, and no orders.

Provenance is structural, not proof of factual truth.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit, urlunsplit

# NEUROVEST_R100_FINANCIAL_EVIDENCE_ENGINE

MAX_DEPTH = 5
MAX_NODES = 350
MAX_SOURCES = 48
MAX_ANSWER = 50000

URL_RE = re.compile(
    r"https?://[^\s<>\]\"']+",
    re.IGNORECASE,
)

NUMERIC_RE = re.compile(
    r"(?<![\w.])"
    r"(?:USD\s*|CAD\s*|\$)?"
    r"-?\d[\d,]*(?:\.\d+)?"
    r"%?"
)

FINANCIAL_TERMS = re.compile(
    r"\b("
    r"stock|stocks|equity|equities|ticker|shares|"
    r"earnings|revenue|profit|valuation|dividend|"
    r"portfolio|financial|market|markets|"
    r"investment|investing|sec filing|balance sheet|"
    r"cash flow|10-k|10-q|p/e ratio"
    r")\b",
    re.IGNORECASE,
)

URL_KEYS = frozenset({
    "url", "source_url", "href", "link",
    "document_url", "filing_url",
})

NAME_KEYS = (
    "title", "name", "source", "publisher",
    "document_type", "filing_type",
)

TEXT_KEYS = (
    "snippet", "summary", "excerpt",
    "description", "text",
)

def normalize_url(value):
    if not isinstance(value, str):
        return None

    value = value.strip().rstrip(".,;)>")

    if len(value) > 2048:
        return None

    try:
        parsed = urlsplit(value)

        if parsed.scheme.lower() not in ("https", "http"):
            return None

        if not parsed.hostname or parsed.username or parsed.password:
            return None

        if parsed.hostname.lower() in (
            "localhost", "127.0.0.1", "::1"
        ):
            return None

        if any(c.isspace() for c in value):
            return None

        return urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.query,
            "",
        ))

    except (ValueError, TypeError):
        return None


def extract_sources(bundle):
    """Only explicit structured source URLs qualify."""

    if bundle is None:
        return []

    sources = []
    seen_urls = set()
    seen_nodes = set()
    remaining = [MAX_NODES]

    def visit(node, depth):
        if depth > MAX_DEPTH or remaining[0] <= 0:
            return

        remaining[0] -= 1

        if isinstance(node, (dict, list, tuple)):
            identity = id(node)

            if identity in seen_nodes:
                return

            seen_nodes.add(identity)

        if isinstance(node, dict):
            found = []

            for key in URL_KEYS:
                url = normalize_url(node.get(key))

                if url:
                    found.append(url)

            for url in found:
                if url in seen_urls or len(sources) >= MAX_SOURCES:
                    continue

                seen_urls.add(url)

                title = next(
                    (
                        node.get(key)
                        for key in NAME_KEYS
                        if isinstance(node.get(key), str)
                        and node.get(key).strip()
                    ),
                    "",
                )

                excerpt = next(
                    (
                        node.get(key)
                        for key in TEXT_KEYS
                        if isinstance(node.get(key), str)
                        and node.get(key).strip()
                    ),
                    "",
                )

                sources.append({
                    "url": url,
                    "title": str(title)[:180],
                    "excerpt": str(excerpt)[:500],
                })

            for value in list(node.values())[:60]:
                if isinstance(value, (dict, list, tuple)):
                    visit(value, depth + 1)

        elif isinstance(node, (list, tuple)):
            for item in node[:80]:
                if isinstance(item, (dict, list, tuple)):
                    visit(item, depth + 1)

        elif depth == 0:
            # Unknown object contracts are not converted into
            # purported evidence or introspected via reflection.
            return

    visit(bundle, 0)
    return sources


def answer_urls(answer):
    if not isinstance(answer, str):
        return []

    result = []
    seen = set()

    for raw in URL_RE.findall(answer[:MAX_ANSWER]):
        url = normalize_url(raw)

        if url and url not in seen:
            seen.add(url)
            result.append(url)

    return result[:60]


def numeric_observations(sources):
    """
    Extract bounded illustrative numeric observations.
    Different numbers do not, by themselves, establish
    a contradiction: units, periods and definitions matter.
    """

    observations = []

    for source in sources[:MAX_SOURCES]:
        excerpt = source["excerpt"]

        for match in list(NUMERIC_RE.finditer(excerpt))[:12]:
            raw = match.group()

            try:
                normalized = raw.replace(
                    ",", ""
                ).replace(
                    "USD", ""
                ).replace(
                    "CAD", ""
                ).replace(
                    "$", ""
                ).replace(
                    "%", ""
                ).strip()

                Decimal(normalized)

            except (InvalidOperation, ValueError):
                continue

            observations.append({
                "source_url": source["url"],
                "value": raw,
            })

            if len(observations) >= 120:
                return observations

    return observations


def assess_financial_evidence(question, answer, retrieval):
    if not isinstance(question, str):
        question = ""

    if not isinstance(answer, str):
        answer = ""

    is_financial = bool(
        FINANCIAL_TERMS.search(question[:6000])
    )

    sources = extract_sources(retrieval)
    supported = {s["url"] for s in sources}
    cited = answer_urls(answer)

    matched = [url for url in cited if url in supported]
    unmatched = [url for url in cited if url not in supported]

    numeric = numeric_observations(sources)

    if not is_financial:
        state = "out_of_scope"
    elif retrieval is None:
        state = "retrieval_unavailable"
    elif not sources:
        state = "no_structured_sources"
    elif unmatched:
        state = "unsupported_citation_urls"
    elif not cited:
        state = "no_answer_urls"
    else:
        state = "source_urls_matched"

    return {
        "version": "R100",
        "scope": "financial" if is_financial else "other",
        "state": state,
        "structured_source_count": len(sources),
        "answer_url_count": len(cited),
        "matched_source_url_count": len(matched),
        "unmatched_source_url_count": len(unmatched),
        "numeric_observation_count": len(numeric),
        "numeric_conflicts_verified": False,
        "source_content_verified": False,
        "evidence_sufficient": None,
        "external_requests_made": False,
        "orders_executed": False,
        "authorization_changed": False,
    }
