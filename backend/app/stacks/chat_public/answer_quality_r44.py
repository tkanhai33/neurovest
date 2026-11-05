"""R44: bounded answer consistency and bibliography screening.

No remote requests, account access, trading or tool execution.
These checks are conservative and are not general proof verification
or proof of peer-review status.
"""
from __future__ import annotations

import re

VERSION = "NEUROVEST_G43_R44_ANSWER_QUALITY"


def math_findings(answer):
    """Check two exact, provable L2 normalization identities.

    Not a general-purpose mathematical proof verifier.
    """
    if not isinstance(answer, str):
        return []

    compact = re.sub(r"\s+", "", answer)
    compact = compact.replace(r"\left", "").replace(r"\right", "")
    compact = compact.replace(r"\lVert", "|").replace(r"\rVert", "|")
    compact = compact.replace(r"\|", "|")
    compact = compact.replace(r"\pi", "pi")

    has_exp = bool(re.search(
        r"e\^\{?int\}?", compact, re.I
    ))
    has_interval = bool(re.search(
        r"\[0,2pi\]", compact, re.I
    ))

    if not (has_exp and has_interval):
        return []

    findings = []

    wrong_norm = bool(re.search(
        r"\|x_n\|=1(?![0-9.])",
        compact,
    ))

    wrong_distance = bool(re.search(
        r"\|x_n-x_m\|\^?\{?2\}?=2pi(?![0-9])",
        compact,
    ))

    if wrong_norm:
        findings.append({
            "code": "unnormalized_exponential_norm",
            "detail": (
                "On [0,2pi], exp(int) has L2 norm "
                "sqrt(2pi), not 1."
            ),
        })

    if wrong_distance:
        findings.append({
            "code": "exponential_distance_error",
            "detail": (
                "For different integer frequencies, "
                "the squared L2 distance is 4pi, not 2pi."
            ),
        })

    return findings



def publication_findings(record):
    """Screen weak bibliographic entries; not peer-review certification."""
    if not isinstance(record, dict):
        return [{"code": "invalid_publication_record"}]

    title = str(record.get("title") or "").strip()
    journal = str(record.get("journal") or "").strip()
    doi = str(record.get("doi") or "").strip()
    year = record.get("year")
    findings = []

    if not title or not journal or not doi:
        findings.append({"code": "missing_bibliography_metadata"})

    if not isinstance(year, int) or not 1800 <= year <= 2100:
        findings.append({"code": "invalid_publication_year"})

    if re.search(
        r"\b(?:book review|editorial|correction|"
        r"erratum|retraction)\b",
        title,
        re.I,
    ):
        findings.append({"code": "non_research_publication_type"})

    # This publication venue is a science magazine.
    # Metadata alone cannot establish original research.
    if journal.casefold() == "new scientist":
        findings.append({"code": "science_magazine_not_research_journal"})

    # Some Crossref journal entries use a review-related
    # DOI suffix. Treat this as a screening signal only
    # when the title also resembles a named book/report.
    if (
        doi.casefold().endswith("br")
        and re.search(
            r"\b(?:report|assessment|climate change \d{4})\b",
            title,
            re.I,
        )
    ):
        findings.append({"code": "possible_book_review"})

    return findings


def screened_publications(records):
    """Return clean records plus exclusions for traceability."""
    accepted = []
    excluded = []
    seen = set()

    for record in records or ():
        findings = publication_findings(record)
        if findings:
            excluded.append({
                "title": (
                    str(record.get("title", ""))[:160]
                    if isinstance(record, dict)
                    else ""
                ),
                "findings": findings,
            })
            continue

        doi = str(record["doi"]).casefold()

        if doi in seen:
            continue

        seen.add(doi)
        accepted.append(record)

    return accepted, excluded
