"""NeuroVest R114-G6: bounded verification of public DOI citations."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from backend.app.stacks.chat_public.context.free_knowledge_14e_r114 import (
    AGENT,
    _safe_query,
    _r114f_relevance,
)

VERSION = "NEUROVEST_R114G6_CITATION_INTEGRITY"

DOI_RE = re.compile(
    r"(?i)\b10\.\d{4,9}/[a-z0-9._;()/:\-]+"
)

MAX_DOI_BYTES = 524288
DOI_TIMEOUT = 4.0


def eligible(question):
    if not isinstance(question, str):
        return False

    # This normalizes public request wording only.
    # Do not relax screening of personal content.
    screened = re.sub(
        r"\bgive\s+me\b",
        "provide",
        question,
        flags=re.I,
    )

    if _safe_query(screened) is None:
        return False

    q = question.casefold()

    publications = re.search(
        r"\b(papers?|articles?|publications?|"
        r"studies|journals?)\b",
        q,
    )

    metadata = re.search(
        r"\b(dois?|titles?|journals?|"
        r"publication years?|sources?)\b",
        q,
    )

    request = re.search(
        r"\b(find|show|list|give|retrieve|"
        r"provide|identify)\b",
        q,
    )

    return bool(publications and metadata and request)


def extract_dois(answer):
    if not isinstance(answer, str):
        return []

    found = []
    seen = set()

    # Supports encoded DOI URLs as well as plain DOI text.
    text = urllib.parse.unquote(answer[:12000])

    for match in DOI_RE.finditer(text):
        doi = match.group(0).rstrip(".,;")

        # Strip only unmatched closing parentheses.
        while (
            doi.endswith(")")
            and doi.count(")") > doi.count("(")
        ):
            doi = doi[:-1]

        key = doi.casefold()

        if key not in seen:
            seen.add(key)
            found.append(doi)

        if len(found) >= 3:
            break

    return found


def clean(value, limit=240):
    if not isinstance(value, str):
        return ""

    value = re.sub(
        r"[\x00-\x1f\x7f]+",
        " ",
        value,
    )

    return " ".join(value.split())[:limit]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch_doi(doi):
    """Fixed Crossref host, bounded HTTPS, no redirects."""

    if not isinstance(doi, str):
        return None

    if len(doi) > 200 or not DOI_RE.fullmatch(doi):
        return None

    encoded = urllib.parse.quote(
        doi,
        safe="",
    )

    # No user-controlled hostname or arbitrary URL.
    url = (
        "https://api.crossref.org/works/"
        + encoded
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": AGENT,
            "Accept": "application/json",
        },
    )

    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(),
        NoRedirect(),
    )

    try:
        with opener.open(
            request,
            timeout=DOI_TIMEOUT,
        ) as response:

            if response.status != 200:
                return None

            if (
                urllib.parse.urlsplit(
                    response.url
                ).hostname != "api.crossref.org"
            ):
                return None

            raw = response.read(
                MAX_DOI_BYTES + 1
            )

            if len(raw) > MAX_DOI_BYTES:
                return None

            data = json.loads(
                raw.decode("utf-8")
            )

            return data if isinstance(data, dict) else None

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        return None


def canonical_record(doi, fetch=None):
    if not isinstance(doi, str):
        return None

    if len(doi) > 200 or not DOI_RE.fullmatch(doi):
        return None

    if fetch is None:
        fetch = fetch_doi

    data = fetch(doi)

    if not isinstance(data, dict):
        return None

    item = data.get("message")

    if not isinstance(item, dict):
        return None

    returned = item.get("DOI")

    if (
        not isinstance(returned, str)
        or returned.casefold() != doi.casefold()
    ):
        return None

    if item.get("type") != "journal-article":
        return None

    titles = item.get("title")
    journals = item.get("container-title")

    if not (
        isinstance(titles, list)
        and titles
        and isinstance(journals, list)
        and journals
    ):
        return None

    title = clean(titles[0])
    journal = clean(journals[0], 160)

    date = (
        item.get("published")
        or item.get("published-online")
        or item.get("published-print")
        or {}
    )

    if not isinstance(date, dict):
        return None

    parts = date.get("date-parts") or []

    if not (
        isinstance(parts, list)
        and parts
        and isinstance(parts[0], list)
        and parts[0]
        and isinstance(parts[0][0], int)
    ):
        return None

    year = parts[0][0]

    if not (
        title
        and journal
        and 1800 <= year <= datetime.now(
            timezone.utc
        ).year
    ):
        return None

    return {
        "title": title,
        "journal": journal,
        "year": year,
        "doi": returned,
        "url": (
            "https://doi.org/"
            + urllib.parse.quote(
                returned,
                safe="/",
            )
        ),
    }



# NEUROVEST_R114H_VERIFIED_RESEARCH_RECOVERY
def recover_publications(question, excluded_dois=(), provider=None,
                         lookup=None):
    if not eligible(question):
        return []

    if provider is None:
        from backend.app.stacks.chat_public.context.free_knowledge_14e_r114 import (
            _crossref,
        )
        provider = _crossref

    if lookup is None:
        lookup = canonical_record

    try:
        candidates = provider(question)
    except Exception:
        return []

    if not isinstance(candidates, list):
        return []

    excluded = {
        doi.casefold()
        for doi in excluded_dois
        if isinstance(doi, str)
    }

    recovered = []

    for candidate in candidates[:8]:
        if not isinstance(candidate, dict):
            continue

        if candidate.get("source") != "Crossref":
            continue

        url = candidate.get("url", "")

        if not (
            isinstance(url, str)
            and url.startswith("https://doi.org/")
        ):
            continue

        doi = urllib.parse.unquote(
            url[len("https://doi.org/"):]
        )

        if (
            len(doi) > 200
            or not DOI_RE.fullmatch(doi)
            or doi.casefold() in excluded
        ):
            continue

        try:
            record = lookup(doi)
        except Exception:
            record = None

        if not isinstance(record, dict):
            continue

        canonical_doi = record.get("doi", "")
        title = record.get("title", "")

        if not (
            isinstance(canonical_doi, str)
            and canonical_doi.casefold() == doi.casefold()
            and isinstance(title, str)
        ):
            continue

        if _r114f_relevance(
            question, title, strict=True
        ) <= 0:
            continue

        if not (
            record.get("journal")
            and isinstance(record.get("year"), int)
            and record.get("url", "").startswith(
                "https://doi.org/"
            )
        ):
            continue

        recovered.append(record)
        excluded.add(doi.casefold())

        if len(recovered) >= 2:
            break

    return recovered


def format_recovered_publications(records):
    if not records:
        return None

    lines = [
        "The original DOI citations could not be verified. "
        "I found the following alternative publication "
        "records and checked their metadata against Crossref:"
    ]

    for index, record in enumerate(records, 1):
        lines.append(
            f"**{index}. {record['title']}**\n"
            f"- Publication year: {record['year']}\n"
            f"- Journal: {record['journal']}\n"
            f"- DOI: `{record['doi']}`\n"
            f"- Source: {record['url']}"
        )

    if len(records) < 2:
        lines.append(
            "I could verify only one relevant replacement "
            "record. I won't invent a second citation."
        )

    lines.append(
        "These are verified bibliographic records. "
        "Crossref metadata does not independently establish "
        "peer-review status or validate scientific findings."
    )

    return "\n\n".join(lines)


def verify_answer(question, answer, fetch=None):
    if not eligible(question):
        return None

    dois = extract_dois(answer)

    if not dois:
        # NEUROVEST_G43_R42D_CROSSREF_RECOVERY
        if __import__('os').environ.get(
            'NV_R42D_CROSSREF_RECOVERY_ENABLED'
        ) == '1':
            return _r42d_recover_without_doi(question)
        return None

    verified = []
    excluded = 0
    unavailable = 0

    # Maximum two remote lookups.
    for doi in dois[:2]:
        try:
            record = canonical_record(
                doi,
                fetch=fetch,
            )
        except Exception:
            record = None

        if record is None:
            unavailable += 1
            continue

        relevance = _r114f_relevance(
            question,
            record["title"],
            strict=True,
        )

        if relevance <= 0:
            excluded += 1
            continue

        verified.append(record)

    # NEUROVEST_R114H5_FILL_MISSING_CITATION_SLOTS
    # Keep canonical verified records; recover only missing slots.
    if verified and len(verified) < 2:
        try:
            already_seen = {
                record["doi"].casefold()
                for record in verified
            }

            excluded_dois = list(dois)
            excluded_dois.extend(
                record["doi"] for record in verified
            )

            replacements = recover_publications(
                question,
                excluded_dois=excluded_dois,
            )

            for replacement in replacements:
                if len(verified) >= 2:
                    break

                if not isinstance(replacement, dict):
                    continue

                replacement_doi = replacement.get("doi", "")
                replacement_title = replacement.get("title", "")

                if not (
                    isinstance(replacement_doi, str)
                    and replacement_doi
                    and isinstance(replacement_title, str)
                    and replacement_title
                ):
                    continue

                if replacement_doi.casefold() in already_seen:
                    continue

                if _r114f_relevance(
                    question,
                    replacement_title,
                    strict=True,
                ) <= 0:
                    continue

                if not (
                    isinstance(replacement.get("year"), int)
                    and replacement.get("journal")
                    and replacement.get("url", "").startswith(
                        "https://doi.org/"
                    )
                ):
                    continue

                verified.append(replacement)
                already_seen.add(replacement_doi.casefold())

                # A successful replacement fills one missing slot.
                if unavailable:
                    unavailable -= 1
                elif excluded:
                    excluded -= 1

        except Exception:
            # Preserve the verified partial answer if recovery fails.
            pass

    if not verified:
        # NEUROVEST_R114H_RECOVERY_CALL
        # Only canonical Crossref-verified replacements.
        try:
            replacements = recover_publications(
                question,
                excluded_dois=dois[:2],
            )
            replacement_answer = format_recovered_publications(
                replacements
            )
            if replacement_answer:
                return replacement_answer
        except Exception:
            pass

        # Preserve the existing R114-G8 fallback.
        if unavailable:
            return (
                "I could not verify the cited publication "
                "details against Crossref at this time. "
                "The DOI references and associated titles, "
                "journals, and years remain unverified. "
                "I will not present them as confirmed."
            )

        return (
            "I could not substantiate the supplied DOI "
            "citations as relevant publications using "
            "Crossref metadata."
        )

    lines = [
        "I verified these publication records "
        "against Crossref:"
    ]

    for index, record in enumerate(verified, 1):
        lines.append(
            f"**{index}. {record['title']}**\n"
            f"- Publication year: {record['year']}\n"
            f"- Journal: {record['journal']}\n"
            f"- DOI: `{record['doi']}`\n"
            f"- Source: {record['url']}"
        )

    if excluded:
        lines.append(
            f"{excluded} citation(s) were excluded "
            "because their metadata did not match "
            "the requested subject."
        )

    if unavailable:
        lines.append(
            f"{unavailable} citation(s) could not be "
            "verified; their status remains unknown."
        )

    lines.append(
        "Crossref confirms publication metadata, "
        "not the scientific conclusions themselves."
    )

    return "\n\n".join(lines)


# NEUROVEST_G43_R42D_CROSSREF_RECOVERY
_r42d_original_eligible = eligible

def eligible(question):
    if _r42d_original_eligible(question):
        return True

    if __import__("os").environ.get(
        "NV_R42D_CROSSREF_RECOVERY_ENABLED"
    ) != "1":
        return False

    if not isinstance(question, str):
        return False

    screened = re.sub(
        r"\bgive\s+me\b", "provide", question, flags=re.I
    )

    # Retain the existing private-content, length, URL and
    # time-sensitive request restrictions.
    if _safe_query(screened) is None:
        return False

    has_publication = bool(re.search(
        r"\b(?:papers?|articles?|publications?|studies)\b",
        question, re.I,
    ))

    has_discovery = bool(re.search(
        r"\b(?:find|identify|list|show|provide|retrieve)\b",
        screened, re.I,
    ))

    has_subject = bool(_r114f_relevance(
        question,
        _r114f_topic(question),
        strict=False,
    )) if False else bool(_r114f_topic(question))

    return has_publication and has_discovery and has_subject


def _r42d_recover_without_doi(question):
    # Only called for eligible public publication requests.
    # No generated DOI or citation is assumed to be true.
    records = recover_publications(question)

    if not records:
        return (
            "I couldn't verify relevant publication records "
            "against Crossref for this request. I won't invent "
            "titles, journals, years or DOI links."
        )

    lines = [
        "I found these publication records and verified "
        "their bibliographic metadata against Crossref:"
    ]

    for index, record in enumerate(records[:2], 1):
        lines.append(
            f"**{index}. {record['title']}**\n"
            f"- Publication year: {record['year']}\n"
            f"- Journal: {record['journal']}\n"
            f"- DOI: `{record['doi']}`\n"
            f"- Source: {record['url']}"
        )

    if len(records) < 2:
        lines.append(
            "Only one relevant publication record could be "
            "verified. I won't invent a second."
        )

    lines.append(
        "Crossref confirms publication metadata, not "
        "the scientific conclusions themselves."
    )

    return "\n\n".join(lines)

from backend.app.stacks.chat_public.context.free_knowledge_14e_r114 import (
    _r114f_topic,
)


# NEUROVEST_G43_R44_ANSWER_QUALITY
import os as _r44_citation_os

_r44_previous_canonical_record = canonical_record

def canonical_record(doi, fetch=None):
    record = _r44_previous_canonical_record(
        doi, fetch=fetch
    )

    if _r44_citation_os.environ.get(
        "NV_R44_ANSWER_QUALITY_ENABLED"
    ) != "1":
        return record

    if record is None:
        return None

    from backend.app.stacks.chat_public.answer_quality_r44 import (
        publication_findings,
    )

    if publication_findings(record):
        return None

    return record
