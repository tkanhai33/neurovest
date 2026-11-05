"""
NeuroVest R101 — bounded financial claim matching.

Diagnostic-only analysis of existing retrieval evidence.
No network requests, financial orders, persistence or permissions.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from backend.app.stacks.chat_public.financial_evidence_13j_r100 import (
    extract_sources,
)

# NEUROVEST_R101_CLAIM_EVIDENCE_ENGINE

MAX_TEXT = 30000
MAX_CLAIMS = 32
MAX_SOURCE_CLAIMS = 96

METRICS = (
    ("free_cash_flow", r"\bfree cash flow\b"),
    ("operating_income", r"\boperating income\b"),
    ("net_income", r"\bnet income\b"),
    ("revenue", r"\b(?:revenue|net sales)\b"),
    ("gross_profit", r"\bgross profit\b"),
)

MONEY = re.compile(
    r"(?P<currency>CAD\s*|USD\s*|CA\$|US\$|\$)"
    r"\s*(?P<amount>-?\d[\d,]*(?:\.\d+)?)"
    r"\s*(?P<scale>trillion|billion|million|thousand|"
    r"tn|bn|mn|m|k)?\b",
    re.I,
)

PERIOD = re.compile(
    r"\b(?:FY\s*20\d{2}|"
    r"Q[1-4]\s*(?:FY\s*)?20\d{2}|"
    r"20\d{2}\s*fiscal\s*year)\b",
    re.I,
)

SENTENCES = re.compile(r"(?<=[.!?])\s+|\n+")

MULTIPLIERS = {
    "": Decimal(1),
    "k": Decimal(1000),
    "thousand": Decimal(1000),
    "m": Decimal(1000000),
    "mn": Decimal(1000000),
    "million": Decimal(1000000),
    "bn": Decimal(1000000000),
    "billion": Decimal(1000000000),
    "tn": Decimal(1000000000000),
    "trillion": Decimal(1000000000000),
}


def normalize_period(value):
    if not isinstance(value, str):
        return None

    value = re.sub(r"\s+", "", value.upper())

    m = re.fullmatch(r"FY(20\d{2})", value)
    if m:
        return "FY" + m.group(1)

    m = re.fullmatch(r"Q([1-4])(?:FY)?(20\d{2})", value)
    if m:
        return "Q" + m.group(1) + "-" + m.group(2)

    m = re.fullmatch(r"(20\d{2})FISCALYEAR", value)
    if m:
        return "FY" + m.group(1)

    return None


def currency_code(token):
    token = token.strip().upper().replace(" ", "")

    if token in ("USD", "US$"):
        return "USD"

    if token in ("CAD", "CA$"):
        return "CAD"

    # A bare dollar sign is ambiguous.
    return "UNSPECIFIED_DOLLAR"


def extract_claims(text, limit=MAX_CLAIMS):
    if not isinstance(text, str):
        return []

    claims = []
    seen = set()

    for sentence in SENTENCES.split(text[:MAX_TEXT]):
        sentence = sentence.strip()

        if not sentence or len(sentence) > 1000:
            continue

        periods = list(PERIOD.finditer(sentence))
        amounts = list(MONEY.finditer(sentence))

        if not periods or not amounts:
            continue

        for metric, pattern in METRICS:
            labels = list(re.finditer(pattern, sentence, re.I))

            if not labels:
                continue

            for label in labels:
                # Use the nearest monetary amount within the same
                # short sentence, with a bounded distance.
                amount_match = min(
                    amounts,
                    key=lambda m: abs(m.start() - label.start()),
                )

                if abs(amount_match.start() - label.start()) > 125:
                    continue

                period_match = min(
                    periods,
                    key=lambda m: abs(m.start() - label.start()),
                )

                period = normalize_period(period_match.group())

                if not period:
                    continue

                try:
                    number = Decimal(
                        amount_match.group("amount").replace(",", "")
                    )

                    scale = (
                        amount_match.group("scale") or ""
                    ).lower()

                    normalized = (
                        number * MULTIPLIERS[scale]
                    )
                except (
                    InvalidOperation,
                    ValueError,
                    KeyError,
                ):
                    continue

                claim = {
                    "metric": metric,
                    "period": period,
                    "currency": currency_code(
                        amount_match.group("currency")
                    ),
                    "amount": str(normalized),
                }

                key = tuple(claim.items())

                if key not in seen:
                    seen.add(key)
                    claims.append(claim)

                if len(claims) >= limit:
                    return claims

    return claims


def classify_pair(answer_claim, source_claim):
    if (
        answer_claim["metric"] != source_claim["metric"]
        or answer_claim["period"] != source_claim["period"]
        or answer_claim["currency"] != source_claim["currency"]
    ):
        return "not_comparable"

    a = Decimal(answer_claim["amount"])
    b = Decimal(source_claim["amount"])

    if a == b:
        return "aligned"

    baseline = max(abs(b), Decimal(1))
    difference = abs(a - b) / baseline

    # More than 1% triggers review, not a declaration
    # that either source or the assistant is wrong.
    if difference > Decimal("0.01"):
        return "potential_discrepancy"

    return "rounding_difference"


def assess_claims(question, answer, retrieval):
    """
    Compare explicit metric/period/currency combinations only.

    Matching source text may still belong to a different entity,
    reporting scope, accounting basis or filing amendment.
    Results are candidate evidence signals, not verified facts.
    """

    answer_claims = extract_claims(answer)
    sources = extract_sources(retrieval)

    source_claims = []

    for source in sources[:48]:
        for claim in extract_claims(source["excerpt"], limit=8):
            source_claims.append({
                **claim,
                "source_url": source["url"],
            })

            if len(source_claims) >= MAX_SOURCE_CLAIMS:
                break

        if len(source_claims) >= MAX_SOURCE_CLAIMS:
            break

    observations = []
    counts = {
        "aligned": 0,
        "rounding_difference": 0,
        "potential_discrepancy": 0,
        "insufficient_matching_evidence": 0,
        "ambiguous_multiple_sources": 0,
    }

    for claim in answer_claims:
        candidates = []

        for source in source_claims:
            state = classify_pair(claim, source)

            if state != "not_comparable":
                candidates.append({
                    "status": state,
                    "source_url": source["source_url"],
                })

        if not candidates:
            status = "insufficient_matching_evidence"
        elif len({c["status"] for c in candidates}) > 1:
            status = "ambiguous_multiple_sources"
        else:
            status = candidates[0]["status"]

        counts[status] += 1

        observations.append({
            "metric": claim["metric"],
            "period": claim["period"],
            "currency": claim["currency"],
            "status": status,
            "matching_source_count": len(candidates),
        })

    return {
        "version": "R101",
        "answer_claim_count": len(answer_claims),
        "source_claim_count": len(source_claims),
        "structured_source_count": len(sources),
        "counts": counts,
        "observations": observations[:MAX_CLAIMS],
        "claim_values_exposed": False,
        "claim_truth_verified": False,
        "entity_identity_verified": False,
        "accounting_basis_verified": False,
        "evidence_sufficient": None,
        "read_only": True,
        "orders_executed": False,
        "authorization_changed": False,
    }
