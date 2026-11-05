"""
NeuroVest 10R-R2 — canonical quote presentation validation.

Called only after the existing market-data provider router
returns a canonical MarketQuote.

The provider-reported observation timestamp does not
independently prove exchange-level real-time freshness.

No provider fetching, brokerage execution, DB or I/O.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from backend.app.stacks.market_data.dto import (
    MarketQuote,
    normalize_symbol,
)

VERSION = "neuro-market-quote-truth-10r-r2-v1"

MAX_RECENT_AGE = timedelta(minutes=15)
MAX_FUTURE_SKEW = timedelta(minutes=2)


@dataclass(frozen=True)
class QuotePresentation:
    label: str
    note: str
    freshness_state: str
    observation_age_seconds: float
    provider_reported: bool = True
    real_time_independently_verified: bool = False


def validate_quote_for_chat(
    quote: MarketQuote,
    requested_symbol: str,
    *,
    now: datetime | None = None,
) -> QuotePresentation:
    """
    Return truthful presentation metadata for a quote.

    Invalid quotes raise ValueError and must be handled
    by the existing read-only quote failure path.
    """
    if not isinstance(quote, MarketQuote):
        raise ValueError(
            "market-data provider returned a non-canonical quote"
        )

    try:
        expected = normalize_symbol(requested_symbol)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "requested quote symbol is invalid"
        ) from exc

    if quote.symbol != expected:
        raise ValueError(
            "market-data quote symbol mismatch"
        )

    if not isinstance(quote.provider, str) or not quote.provider.strip():
        raise ValueError(
            "market-data quote provider is missing"
        )

    if not isinstance(quote.currency, str) or not quote.currency.strip():
        raise ValueError(
            "market-data quote currency is missing"
        )

    try:
        price = float(quote.price)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "market-data quote price is invalid"
        ) from exc

    if not math.isfinite(price) or price <= 0:
        raise ValueError(
            "market-data quote price must be positive and finite"
        )

    observed = quote.observed_at

    if (
        not isinstance(observed, datetime)
        or observed.tzinfo is None
        or observed.utcoffset() is None
    ):
        raise ValueError(
            "market-data observation time is not timezone-aware"
        )

    if now is None:
        now = datetime.now(timezone.utc)

    if (
        not isinstance(now, datetime)
        or now.tzinfo is None
        or now.utcoffset() is None
    ):
        raise ValueError(
            "reference time must be timezone-aware"
        )

    age = (
        now.astimezone(timezone.utc)
        - observed.astimezone(timezone.utc)
    )

    if age < -MAX_FUTURE_SKEW:
        raise ValueError(
            "market-data observation timestamp is in the future"
        )

    # NEUROVEST_TIMESTAMP_PROVENANCE_10S
    metadata = quote.metadata

    origin = (
        metadata.get("neurovest_timestamp_origin")
        if hasattr(metadata, "get")
        else None
    )

    if origin == "locally_synthesized":
        state = "timestamp_unverified"
        label = "quote with unverified observation time"
        explanation = (
            "The observation timestamp was locally generated "
            "because the source payload did not establish "
            "an observation time. The price cannot be "
            "qualified as recently observed market data."
        )

        if bool(quote.delayed):
            explanation += (
                " The provider also marks this quote as delayed."
            )

    elif age > MAX_RECENT_AGE:
        state = "stale"
        label = "last available quote"
        explanation = (
            "The observation is older than the "
            "15-minute recency window. "
            "It must not be treated as a current price."
        )
    elif bool(quote.delayed):
        state = "delayed"
        label = "delayed quote"
        explanation = (
            "The provider explicitly marks this quote as delayed."
        )
    else:
        state = "recent_provider_reported"
        label = "recent provider-reported quote"
        explanation = (
            "The reported observation is within the "
            "15-minute recency window."
        )

    if age > MAX_RECENT_AGE and bool(quote.delayed):
        explanation += (
            " The provider also marks the quote as delayed."
        )

    explanation += (
        " The timestamp is provider-reported and is not "
        "independent proof of a real-time exchange quote. "
        "A recent report may still reflect delayed or "
        "synthesized source timing."
    )

    return QuotePresentation(
        label=label,
        note="Quote timing: " + explanation,
        freshness_state=state,
        observation_age_seconds=max(
            0.0, age.total_seconds()
        ),
    )
