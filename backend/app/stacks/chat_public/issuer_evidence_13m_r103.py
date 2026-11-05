"""
R103 issuer-aware financial claim comparison.

Conservative extension of R101 using R100 structured sources.
No network, database, model calls, orders, or authorization.
"""

from __future__ import annotations

import re

from backend.app.stacks.chat_public.financial_evidence_13j_r100 import (
    extract_sources,
)
from backend.app.stacks.chat_public.financial_claims_13k_r101 import (
    extract_claims,
    classify_pair,
)

# NEUROVEST_R103_ISSUER_EVIDENCE_ENGINE

MAX_ANSWER_CLAIMS = 32
MAX_SOURCE_CLAIMS = 96

ISSUER_KEYS = (
    "issuer_cik",
    "cik",
    "company_id",
    "issuer_id",
    "issuer_ticker",
    "ticker",
    "symbol",
)

ISSUER_NAME_KEYS = (
    "issuer_name",
    "company_name",
    "legal_entity_name",
)

GENERIC_NAMES = frozenset({
    "company",
    "the company",
    "issuer",
    "business",
    "unknown",
    "example company",
})

def normalized_issuer(value):
    if not isinstance(value, str):
        return None

    value = re.sub(r"\s+", " ", value.strip()).casefold()

    if not value or len(value) > 160:
        return None

    if value in GENERIC_NAMES:
        return None

    return value


def issuer_identity(record):
    """
    Read explicit structured identifiers only.
    Do not infer issuer from an unrelated website hostname.
    """

    if not isinstance(record, dict):
        return None

    for key in ISSUER_KEYS:
        value = record.get(key)

        if isinstance(value, int) and not isinstance(value, bool):
            value = str(value)

        if isinstance(value, str):
            candidate = normalized_issuer(value)

            if candidate:
                return {
                    "type": key,
                    "value": candidate,
                }

    for key in ISSUER_NAME_KEYS:
        candidate = normalized_issuer(record.get(key))

        if candidate:
            return {
                "type": "issuer_name",
                "value": candidate,
            }

    return None


def compatible_issuers(a, b):
    """
    Only identical identifier types and values are comparable.

    CIK vs ticker, or legal name vs ticker, requires a trusted
    entity mapping not provided by this module.
    """

    if not isinstance(a, dict) or not isinstance(b, dict):
        return False

    left_type = a.get("type")
    right_type = b.get("type")

    aliases = {"cik", "issuer_cik"}

    if left_type in aliases and right_type in aliases:
        return a.get("value") == b.get("value")

    return (
        left_type == right_type
        and a.get("value") == b.get("value")
    )


def _walk_records(value, depth=0, seen=None):
    if seen is None:
        seen = set()

    if depth > 5:
        return

    if isinstance(value, (dict, list, tuple)):
        identity = id(value)

        if identity in seen:
            return

        seen.add(identity)

    if isinstance(value, dict):
        yield value

        for nested in list(value.values())[:60]:
            if isinstance(nested, (dict, list, tuple)):
                yield from _walk_records(
                    nested, depth + 1, seen
                )

    elif isinstance(value, (list, tuple)):
        for nested in value[:80]:
            if isinstance(nested, (dict, list, tuple)):
                yield from _walk_records(
                    nested, depth + 1, seen
                )


def issuer_source_records(retrieval):
    """
    Connect explicitly identified records to source URLs.

    Multiple records with the same URL and conflicting issuer
    identities are deliberately rejected as ambiguous.
    """

    allowed = {
        item["url"]
        for item in extract_sources(retrieval)
    }

    records = {}
    ambiguous = set()

    from backend.app.stacks.chat_public.financial_evidence_13j_r100 import (
        normalize_url,
    )

    for record in _walk_records(retrieval):
        identifier = issuer_identity(record)

        if identifier is None:
            continue

        urls = []

        for key in (
            "url", "source_url", "filing_url",
            "document_url", "href", "link",
        ):
            url = normalize_url(record.get(key))

            if url and url in allowed:
                urls.append(url)

        snippet = next(
            (
                record.get(key)
                for key in (
                    "snippet", "excerpt", "summary",
                    "text", "description",
                )
                if isinstance(record.get(key), str)
            ),
            "",
        )

        for url in urls:
            previous = records.get(url)

            if previous is not None and not compatible_issuers(
                previous["issuer"], identifier
            ):
                ambiguous.add(url)
                continue

            records[url] = {
                "issuer": identifier,
                "excerpt": snippet[:1000],
            }

    for url in ambiguous:
        records.pop(url, None)

    return records


def assess_issuer_claims(
    question,
    answer,
    retrieval,
    subject=None,
):
    """
    Fail closed for numerical disagreement without common issuer.

    `subject` must come from trusted, structured resolution.
    Never derive it merely from free-form question wording.

    Findings remain provisional without accounting-basis review.
    """

    answer_claims = extract_claims(
        answer,
        limit=MAX_ANSWER_CLAIMS,
    )

    sources = extract_sources(retrieval)
    records = issuer_source_records(retrieval)

    subject_identity = issuer_identity(subject)

    counts = {
        "aligned": 0,
        "rounding_difference": 0,
        "potential_discrepancy": 0,
        "insufficient_matching_evidence": 0,
        "ambiguous_multiple_sources": 0,
    }

    observations = []
    source_claim_count = 0

    for claim in answer_claims:
        comparisons = []
        eligible_sources = 0

        for source in sources[:48]:
            record = records.get(source["url"])

            if record is None:
                continue

            if not compatible_issuers(
                subject_identity,
                record["issuer"],
            ):
                continue

            eligible_sources += 1

            # Use the issuer-tagged record's own excerpt.
            excerpt = record["excerpt"]

            for sourced_claim in extract_claims(
                excerpt, limit=8
            ):
                source_claim_count += 1

                if source_claim_count > MAX_SOURCE_CLAIMS:
                    break

                state = classify_pair(
                    claim,
                    sourced_claim,
                )

                if state != "not_comparable":
                    comparisons.append(state)

            if source_claim_count > MAX_SOURCE_CLAIMS:
                break

        states = set(comparisons)

        if not states:
            status = "insufficient_matching_evidence"
        elif len(states) > 1:
            status = "ambiguous_multiple_sources"
        else:
            status = next(iter(states))

        counts[status] += 1

        observations.append({
            "metric": claim["metric"],
            "period": claim["period"],
            "currency": claim["currency"],
            "status": status,
            "comparable_source_count": eligible_sources,
            "issuer_identity_required": True,
        })

    return {
        # R102 expects the R101 result contract.
        "version": "R101",
        "issuer_gate_version": "R103",
        "answer_claim_count": len(answer_claims),
        "source_claim_count": min(
            source_claim_count, MAX_SOURCE_CLAIMS
        ),
        "structured_source_count": len(sources),
        "identified_source_count": len(records),
        "subject_identity_resolved": (
            subject_identity is not None
        ),
        "counts": counts,
        "observations": observations[:MAX_ANSWER_CLAIMS],
        "claim_values_exposed": False,
        "claim_truth_verified": False,
        "entity_identity_verified": False,
        "accounting_basis_verified": False,
        "evidence_sufficient": None,
        "read_only": True,
        "orders_executed": False,
        "authorization_changed": False,
    }
