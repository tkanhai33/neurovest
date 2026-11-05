from __future__ import annotations

import json
import re
from datetime import date, datetime
from decimal import Decimal
from math import isfinite

from backend.app.stacks.chat_public import (
    financial_research_13d_r58 as research,
)

from backend.app.stacks.market_data.dto import MarketQuote

VERSION = "NEUROVEST_13D_R61_CANONICAL_MARKET_QUOTES"

INTENT = re.compile(
    r"\b(?:stock price|share price|price action|"
    r"share performance|stock performance|"
    r"quote|trading price|market price|"
    r"market performance|financial performance|"
    r"compare|comparison|valuation|"
    r"revenue|earnings|gross margin|"
    r"financial results|financial analysis)\b",
    re.I,
)

ALLOWED_FIELDS = (
    "symbol", "price", "last_price", "last",
    "last_trade_price", "close", "previous_close",
    "currency", "timestamp", "as_of", "provider",
    "source", "retrieved_at", "market_time",
    "volume", "change", "change_percent",
    "percent_change", "status", "is_stale",
    "delay_minutes", "observed_at", "delayed", "bid", "ask", "session",
)

PRICE_FIELDS = (
    "price", "last_price", "last",
    "last_trade_price", "close",
)

def _safe_scalar(value):
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value[:160]
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if isfinite(value) else None
    if isinstance(value, Decimal):
        return str(value) if value.is_finite() else None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return None

def normalize_quote(quote):
    if not isinstance(quote, MarketQuote):
        raise ValueError("non_canonical_market_quote")

    result = {}
    for field in ALLOWED_FIELDS:
        if hasattr(quote, field):
            result[field] = _safe_scalar(
                getattr(quote, field)
            )

    price = next(
        (
            result[name]
            for name in PRICE_FIELDS
            if result.get(name) is not None
        ),
        None,
    )

    if price is None:
        raise ValueError("quote_price_unavailable")

    try:
        numeric_price = Decimal(str(price))
    except Exception as exc:
        raise ValueError("quote_price_invalid") from exc

    if not numeric_price.is_finite() or numeric_price <= 0:
        raise ValueError("quote_price_invalid")

    result["evidence_origin"] = (
        "neurovest_canonical_market_data_provider"
    )
    result["verification"] = "provider_returned_canonical_dto"
    result["real_time_guaranteed"] = False
    result["note"] = (
        "Provider quote may be delayed or cached. "
        "Use provider timestamp when available. "
        "Do not claim exchange-verified real-time pricing."
    )
    return result

def collect_quote_evidence(
    message,
    *,
    quote_loader=None,
):
    if not isinstance(message, str):
        return None
    if not message.strip() or len(message) > 500:
        return None
    if not INTENT.search(message):
        return None

    companies = research.companies_in_text(message)
    if not companies:
        return None

    if quote_loader is None:
        from backend.app.stacks.market_data.runtime_composition import (
            get_market_data_runtime,
        )
        router = get_market_data_runtime().router
        quote_loader = router.get_quote

    items = []
    for ticker, _ in companies[:2]:
        try:
            quote = quote_loader(ticker)
            items.append({
                "ticker": ticker,
                "status": "ok",
                "quote": normalize_quote(quote),
            })
        except Exception:
            items.append({
                "ticker": ticker,
                "status": "unavailable",
                "reason": (
                    "Canonical market quote could not "
                    "be retrieved or validated"
                ),
            })

    return {
        "source": "NeuroVest existing market-data router",
        "capability": "read_only_canonical_quotes",
        "results": items,
        "caveat": (
            "Quotes may be delayed or cached. "
            "No real-time exchange guarantee."
        ),
    }

def attach_market_quote_evidence(
    context,
    message,
    *,
    quote_loader=None,
):
    if not isinstance(context, str):
        return context
    if VERSION in context or len(context) > 48000:
        return context

    result = collect_quote_evidence(
        message, quote_loader=quote_loader
    )
    if result is None:
        return context

    payload = json.dumps(
        result, sort_keys=True, ensure_ascii=True,
        separators=(",", ":"),
    )

    if len(payload) > 4500:
        return context

    return (
        context
        + "\n\n[" + VERSION + "]\n"
        + "READ-ONLY MARKET QUOTE EVIDENCE\n"
        + payload
        + "\nUse available canonical quote values, "
        + "their currency, provider and timestamp. "
        + "Do not invent absent prices, claim prices "
        + "are real time, or describe errors as success. "
        + "Keep SEC reported fundamentals distinct "
        + "from third-party price quotations. "
        + "No account or broker actions are permitted."
        + "\n[/" + VERSION + "]"
    )


# NEUROVEST_13D_R62_HISTORICAL_INTELLIGENCE
_r62_original_attach_market_quote_evidence = (
    attach_market_quote_evidence
)

def attach_market_quote_evidence(
    context,
    message,
    *,
    quote_loader=None,
    history_loader=None,
):
    from backend.app.stacks.chat_public.historical_market_evidence_13d_r62 import (
        attach_historical_evidence,
    )

    quoted = _r62_original_attach_market_quote_evidence(
        context,
        message,
        quote_loader=quote_loader,
    )

    return attach_historical_evidence(
        quoted,
        message,
        history_loader=history_loader,
    )
