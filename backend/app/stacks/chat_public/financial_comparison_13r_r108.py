"""
R108: deterministic, provider-grounded annual comparisons.

Accept only structured R105 financial evidence.
Never infer fiscal year-end dates from the provider's
statement-column dates.

No database, authentication, brokerage or execution access.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
import re

# NEUROVEST_R108_DETERMINISTIC_COMPARISON_ENGINE

ROW = re.compile(
    r"^-\s*(Revenue|Net income|Operating income|Gross profit)"
    r";\s*(?:provider statement date|fiscal period end)\s*"
    r"(\d{4}-\d{2}-\d{2});\s*"
    r"([A-Z]{3})\s+(-?[0-9,]+(?:\.[0-9]+)?)\s*$",
    re.I | re.M,
)

ISSUER = re.compile(
    r"(?m)^Resolved equity symbol:\s*([A-Z]{1,5})\s*$"
)

CURRENCY = re.compile(
    r"(?m)^Financial reporting currency:\s*([A-Z]{3})\s*$"
)

METRICS = {
    "revenue": "Revenue",
    "net income": "Net income",
    "operating income": "Operating income",
    "gross profit": "Gross profit",
}

MAX_EVIDENCE = 10000
MAX_CONTEXT = 2400


def parse_observations(evidence):
    if (
        not isinstance(evidence, str)
        or len(evidence) > MAX_EVIDENCE
    ):
        return None

    issuer_matches = ISSUER.findall(evidence)
    currency_matches = CURRENCY.findall(evidence)

    if len(issuer_matches) != 1 or len(currency_matches) != 1:
        return None

    ticker = issuer_matches[0]
    reporting_currency = currency_matches[0]

    values = {}
    conflicting = set()

    for metric, period, currency, amount in ROW.findall(evidence):
        metric = metric.casefold()

        if metric not in METRICS:
            continue

        if currency != reporting_currency:
            return None

        try:
            date.fromisoformat(period)
            value = Decimal(amount.replace(",", ""))
        except (ValueError, InvalidOperation):
            return None

        if not value.is_finite():
            return None

        key = (period, metric)

        if key in values and values[key] != value:
            conflicting.add(key)

        values[key] = value

    if conflicting:
        return None

    return {
        "ticker": ticker,
        "currency": reporting_currency,
        "values": values,
    }


def latest_comparable_periods(observations):
    if not isinstance(observations, dict):
        return None

    values = observations.get("values")

    if not isinstance(values, dict):
        return None

    periods = sorted(
        {
            period
            for period, metric in values
            if (
                metric == "revenue"
                and values.get((period, "net income")) is not None
                and values.get((period, "revenue")) is not None
                and values[(period, "revenue")] > 0
            )
        },
        reverse=True,
    )

    if len(periods) < 2:
        return None

    return periods[0], periods[1]


def percent_change(current, previous):
    if previous == 0:
        return None

    return (
        (current - previous)
        / abs(previous)
        * Decimal(100)
    )


def percentage(numerator, denominator):
    if denominator <= 0:
        return None

    return numerator / denominator * Decimal(100)


def signed_percent(value):
    if value is None:
        return "unavailable"

    return f"{value:+.2f}%"


def build_comparison_context(evidence):
    observations = parse_observations(evidence)

    if observations is None:
        return ""

    periods = latest_comparable_periods(observations)

    if periods is None:
        return ""

    current, previous = periods
    ticker = observations["ticker"]
    currency = observations["currency"]
    values = observations["values"]

    lines = [
        "[R108 DETERMINISTIC ANNUAL FINANCIAL COMPARISON]",
        f"Company ticker: {ticker}",
        f"Financial reporting currency: {currency}",
        f"LATEST PROVIDER STATEMENT DATE: {current}",
        f"PREVIOUS PROVIDER STATEMENT DATE: {previous}",
        "These are provider statement dates, NOT verified",
        "official corporate fiscal year-end dates.",
        "The newer period is ALWAYS the first period below.",
        "Do not reverse the dates or percentages.",
    ]

    for metric, label in METRICS.items():
        newer = values.get((current, metric))
        older = values.get((previous, metric))

        if newer is None or older is None:
            continue

        change = percent_change(newer, older)

        lines.extend([
            f"{label}:",
            f"  Current [{current}]: {currency} {newer:,.0f}",
            f"  Previous [{previous}]: {currency} {older:,.0f}",
            f"  Change current vs previous: {signed_percent(change)}",
        ])

    ratio_metrics = (
        ("net income", "Net profit margin"),
        ("operating income", "Operating margin"),
        ("gross profit", "Gross margin"),
    )

    for metric, label in ratio_metrics:
        newer_income = values.get((current, metric))
        older_income = values.get((previous, metric))

        newer_revenue = values.get((current, "revenue"))
        older_revenue = values.get((previous, "revenue"))

        if (
            newer_income is None
            or older_income is None
            or newer_revenue is None
            or older_revenue is None
        ):
            continue

        newer_margin = percentage(
            newer_income,
            newer_revenue,
        )
        older_margin = percentage(
            older_income,
            older_revenue,
        )

        if newer_margin is None or older_margin is None:
            continue

        delta = newer_margin - older_margin

        lines.extend([
            f"{label}:",
            f"  Current [{current}]: {newer_margin:.2f}%",
            f"  Previous [{previous}]: {older_margin:.2f}%",
            f"  Change: {delta:+.2f} percentage points",
        ])

    lines.extend([
        "Use these deterministic calculations for the",
        "latest two comparable annual reporting periods.",
        "Do not invent a different reporting period,",
        "reverse the year labels, or recalculate ratios",
        "using figures from mismatched periods.",
        "Describe changes in percentage points for margins.",
        "Distinguish reported observations from calculations.",
        "Do not invent causal explanations for growth.",
        "Do not expose R108 internal evidence markers.",
        "[END R108 DETERMINISTIC COMPARISON]",
    ])

    result = "\n".join(lines)

    if len(result) > MAX_CONTEXT:
        return ""

    return result
