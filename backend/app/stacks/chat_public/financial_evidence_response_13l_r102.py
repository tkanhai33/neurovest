"""
NeuroVest R102 — guarded financial evidence disclosure.

Uses existing R100/R101 diagnostics.
Pure logic; no network, database, trading or authority changes.
"""

from __future__ import annotations

import re

# NEUROVEST_R102_EVIDENCE_RESPONSE_ENGINE

MAX_ANSWER = 45000

FINANCIAL_RESEARCH = re.compile(
    r"\b("
    r"revenue|earnings|financial results|"
    r"net income|gross profit|free cash flow|"
    r"operating income|sec filing|"
    r"10-k|10-q|balance sheet|"
    r"financial statements?"
    r")\b",
    re.I,
)

PROTECTED = re.compile(
    r"\b("
    r"developer|admin|authorization|authentication|"
    r"permissions?|credentials?|password|"
    r"broker|brokerage|place an order|"
    r"execute|execution|live trading|"
    r"buy shares|sell shares|"
    r"emergency.stop|withdraw|"
    r"private account|portfolio holdings"
    r")\b",
    re.I,
)

LIMITATION_MARKER = (
    "**Evidence qualification:**"
)

def _nonnegative_int(value):
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return max(0, min(value, 10000))


def build_evidence_disclosure(
    question,
    answer,
    provenance,
    claims,
):
    """
    Return (candidate, metadata).

    Candidate is still untrusted until existing runtime
    verification and diagnostic safety inspections succeed.
    """

    metadata = {
        "version": "R102",
        "eligible": False,
        "changed": False,
        "reason": "not_applicable",
        "provenance_issue": False,
        "claim_review_issue": False,
        "trading_authorized": False,
        "permissions_changed": False,
    }

    if not isinstance(question, str):
        metadata["reason"] = "invalid_question"
        return answer, metadata

    if not isinstance(answer, str) or not answer.strip():
        metadata["reason"] = "invalid_answer"
        return answer, metadata

    if len(answer) > MAX_ANSWER:
        metadata["reason"] = "answer_too_long"
        return answer, metadata

    if PROTECTED.search(question):
        metadata["reason"] = "protected_scope"
        return answer, metadata

    if not FINANCIAL_RESEARCH.search(question):
        metadata["reason"] = "outside_research_scope"
        return answer, metadata

    if not isinstance(provenance, dict):
        metadata["reason"] = "no_provenance"
        return answer, metadata

    if not isinstance(claims, dict):
        metadata["reason"] = "no_claim_assessment"
        return answer, metadata

    if (
        provenance.get("version") != "R100"
        or claims.get("version") != "R101"
    ):
        metadata["reason"] = "incompatible_evidence"
        return answer, metadata

    if provenance.get("scope") != "financial":
        metadata["reason"] = "outside_provenance_scope"
        return answer, metadata

    sources = _nonnegative_int(
        provenance.get("structured_source_count")
    )

    if sources == 0:
        metadata["reason"] = "no_structured_sources"
        return answer, metadata

    unsupported = _nonnegative_int(
        provenance.get("unmatched_source_url_count")
    )

    counts = claims.get("counts")

    if not isinstance(counts, dict):
        metadata["reason"] = "missing_claim_counts"
        return answer, metadata

    discrepancies = _nonnegative_int(
        counts.get("potential_discrepancy")
    )

    ambiguous = _nonnegative_int(
        counts.get("ambiguous_multiple_sources")
    )

    metadata["eligible"] = True
    metadata["provenance_issue"] = unsupported > 0
    metadata["claim_review_issue"] = (
        discrepancies > 0 or ambiguous > 0
    )

    reasons = []

    if unsupported:
        reasons.append(
            "One or more cited URLs could not be matched "
            "to the structured sources available to this "
            "research response."
        )

    if discrepancies:
        reasons.append(
            "At least one financial amount differs "
            "materially from a comparable value extracted "
            "from the available source excerpts."
        )

    if ambiguous:
        reasons.append(
            "Multiple source excerpts produced differing "
            "comparisons for at least one financial claim."
        )

    if not reasons:
        metadata["reason"] = "no_material_flags"
        return answer, metadata

    if LIMITATION_MARKER in answer:
        metadata["reason"] = "already_disclosed"
        return answer, metadata

    caution = (
        "\n\n---\n\n"
        + LIMITATION_MARKER
        + " "
        + " ".join(reasons)
        + " These are preliminary evidence checks, "
        + "not independently verified conclusions. "
        + "Confirm the company, reporting period, "
        + "currency, accounting basis and original "
        + "filing before relying on disputed figures."
    )

    metadata["changed"] = True
    metadata["reason"] = "candidate_disclosure"

    return answer.rstrip() + caution, metadata
