"""
Read-only market-data API router.

This router exposes canonical market-data DTOs through the shared
market-data composition root.

No endpoint performs broker execution, order placement, portfolio
mutation, registry writes, or live-trading activation.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
from fastapi.encoders import jsonable_encoder

from backend.app.stacks.market_data.dto import (
    HistoricalBarsRequest,
)
from backend.app.stacks.market_data.provider_registry import (
    ProviderCapabilityUnavailableError,
)
from backend.app.stacks.market_data.provider_router import (
    ProviderRoutingError,
)
from backend.app.stacks.market_data.runtime_composition import (
    get_market_data_runtime,
)
from backend.app.stacks.market_data.yfinance_provider import (
    YFinanceProviderError,
)


router = APIRouter(
    prefix="/api/v1/market-data",
    tags=["market-data"],
)


def _parse_datetime(
    value: str,
    field_name: str,
) -> datetime:
    candidate = value.strip()

    if not candidate:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{field_name} must not be empty"
            ),
        )

    if candidate.endswith("Z"):
        candidate = (
            candidate[:-1]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            candidate
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{field_name} must be an ISO-8601 "
                "date or datetime"
            ),
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=UTC
        )

    return parsed.astimezone(
        UTC
    )


def _provider_failure(
    exc: Exception,
) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail={
            "error": "market_data_unavailable",
            "type": type(exc).__name__,
            "message": str(exc),
        },
    )


@router.get("/status")
def market_data_status() -> object:
    """
    Return read-only composition, cache, provider, and session status.

    This endpoint performs no external market-data request.
    """

    runtime = get_market_data_runtime()

    records = runtime.registry.records(
        include_disabled=True
    )

    cache = runtime.cache.stats()

    session = runtime.session.now()

    return jsonable_encoder(
        {
            "status": "ready",
            "mode": "read_only",
            "providers": [
                {
                    "name": record.name,
                    "priority": record.priority,
                    "enabled": record.enabled,
                }
                for record in records
            ],
            "cache": {
                "size": cache.size,
                "maximum_size": (
                    cache.maximum_size
                ),
                "hits": cache.hits,
                "misses": cache.misses,
                "expirations": (
                    cache.expirations
                ),
                "evictions": cache.evictions,
            },
            "session": {
                "state": (
                    session.state.value
                ),
                "observed_at": (
                    session.observed_at
                ),
                "exchange_time": (
                    session.exchange_time
                ),
                "exchange_timezone": (
                    session.exchange_timezone
                ),
                "holiday_calendar_applied": (
                    session
                    .holiday_calendar_applied
                ),
            },
            "broker_execution_enabled": False,
            "live_trading_enabled": False,
        }
    )


@router.get("/quote/{symbol}")
def market_data_quote(
    symbol: str,
    use_cache: bool = Query(
        default=True,
    ),
) -> object:
    runtime = get_market_data_runtime()

    try:
        quote = runtime.router.get_quote(
            symbol,
            use_cache=use_cache,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except (
        ProviderCapabilityUnavailableError,
        ProviderRoutingError,
        YFinanceProviderError,
    ) as exc:
        raise _provider_failure(
            exc
        ) from exc

    return jsonable_encoder(
        quote
    )


@router.get("/historical/{symbol}")
def market_data_historical(
    symbol: str,
    start: str = Query(
        description=(
            "ISO-8601 start date or datetime"
        )
    ),
    end: str = Query(
        description=(
            "ISO-8601 end date or datetime"
        )
    ),
    interval: str = Query(
        default="1d",
        min_length=1,
        max_length=16,
    ),
    adjusted: bool = Query(
        default=True,
    ),
    limit: int | None = Query(
        default=None,
        ge=1,
        le=5000,
    ),
    use_cache: bool = Query(
        default=True,
    ),
) -> object:
    runtime = get_market_data_runtime()

    try:
        request = HistoricalBarsRequest(
            symbol=symbol,
            start=_parse_datetime(
                start,
                "start",
            ),
            end=_parse_datetime(
                end,
                "end",
            ),
            interval=interval,
            adjusted=adjusted,
            limit=limit,
        )

        result = (
            runtime.router
            .get_historical_bars(
                request,
                use_cache=use_cache,
            )
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except (
        ProviderCapabilityUnavailableError,
        ProviderRoutingError,
        YFinanceProviderError,
    ) as exc:
        raise _provider_failure(
            exc
        ) from exc

    return jsonable_encoder(
        result
    )


# NEUROVEST_F9_R3_DEV_QUOTE_DIAGNOSTICS
# Read-only and fail-closed. No broker or portfolio capability.
from datetime import datetime as _F9DateTime, timezone as _F9Timezone
from fastapi import Depends as _F9Depends
from fastapi import HTTPException as _F9HTTPException

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal as _f9_require_principal,
)
from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal as _F9Principal,
)
from backend.app.stacks.chat_public.developer_role_guard import (
    authenticated_developer_role as _f9_verified_dev,
)


def _f9_safe_number(value: object) -> float | None:
    import math

    if isinstance(value, bool):
        return None

    if not isinstance(value, (int, float)):
        return None

    number = float(value)
    return number if math.isfinite(number) else None


def _f9_observation_time(value: object) -> str | None:
    """Normalize genuine provider times; never substitute retrieval time."""
    if isinstance(value, _F9DateTime):
        if value.tzinfo is None or value.utcoffset() is None:
            return None
        observed = value.astimezone(_F9Timezone.utc)

    elif isinstance(value, str):
        try:
            observed = _F9DateTime.fromisoformat(
                value.strip().replace("Z", "+00:00")
            )
        except ValueError:
            return None
        if observed.tzinfo is None or observed.utcoffset() is None:
            return None
        observed = observed.astimezone(_F9Timezone.utc)

    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            observed = _F9DateTime.fromtimestamp(
                float(value),
                _F9Timezone.utc,
            )
        except (ValueError, OverflowError, OSError):
            return None
    else:
        return None

    now = _F9DateTime.now(_F9Timezone.utc)
    if not (
        _F9DateTime(2000, 1, 1, tzinfo=_F9Timezone.utc)
        <= observed
        <= now
    ):
        return None

    return observed.isoformat()


@router.get("/developer/quote-diagnostics/{symbol}")
async def f9_developer_quote_diagnostics(
    symbol: str,
    principal: _F9Principal = _F9Depends(
        _f9_require_principal
    ),
):
    """Read-only quote diagnostics for a verified developer only."""
    if not _f9_verified_dev(principal):
        raise _F9HTTPException(
            status_code=403,
            detail="Authenticated developer role required.",
        )

    import re

    requested = symbol.strip().upper()

    if not re.fullmatch(
        r"[A-Z0-9][A-Z0-9.\\^-]{0,19}",
        requested,
    ):
        raise _F9HTTPException(
            status_code=422,
            detail="Invalid market symbol.",
        )

    from backend.app.stacks.market_data.market_data_service import (
        get_live_market_prices_for_api,
    )

    try:
        payload = await get_live_market_prices_for_api([requested])
    except Exception:
        raise _F9HTTPException(
            status_code=503,
            detail="Market-data service unavailable.",
        )

    retrieved_at = _F9DateTime.now(_F9Timezone.utc)

    quotes = (
        payload.get("quotes")
        if isinstance(payload, dict)
        else None
    )

    quote = (
        quotes.get(requested)
        if isinstance(quotes, dict)
        else None
    )

    if not isinstance(quote, dict):
        raise _F9HTTPException(
            status_code=503,
            detail="Quote unavailable.",
        )

    # Keep provider timestamps separate from retrieval time.
    observed_at = None
    observed_from = None

    for field in ("observed_at", "market_time", "timestamp", "as_of"):
        candidate = _f9_observation_time(quote.get(field))
        if candidate is not None:
            observed_at = candidate
            observed_from = field
            break

    observed_age_seconds = None
    if observed_at is not None:
        observed_dt = _F9DateTime.fromisoformat(observed_at)
        observed_age_seconds = max(
            0,
            int((retrieved_at - observed_dt).total_seconds()),
        )

    price = _f9_safe_number(quote.get("price"))
    previous_close = _f9_safe_number(
        quote.get("previous_close")
    )

    difference = None
    difference_percent = None
    if (
        price is not None
        and previous_close is not None
        and previous_close > 0
    ):
        difference = round(price - previous_close, 8)
        difference_percent = round(
            difference / previous_close * 100,
            6,
        )

    provider = quote.get("provider")
    currency = quote.get("currency")
    session = quote.get("session")
    delayed = quote.get("delayed")

    return {
        "status": "ok",
        "scope": "verified_developer_only",
        "symbol": requested,
        "quote_status": str(quote.get("status") or "unknown")[:32],
        "price": price,
        "previous_close": previous_close,
        "difference_from_previous_close": difference,
        "difference_percent": difference_percent,
        "currency": (
            currency[:8] if isinstance(currency, str) else None
        ),
        "provider": (
            provider[:64] if isinstance(provider, str) else None
        ),
        "market_session": (
            str(session)[:32] if session is not None else None
        ),
        "provider_delayed": (
            delayed if isinstance(delayed, bool) else None
        ),
        "provider_observed_at": observed_at,
        "observation_field": observed_from,
        "observed_age_seconds": observed_age_seconds,
        "api_retrieved_at": retrieved_at.isoformat(),
        "bulk_cache_ttl_seconds": 30,
        "cache_hit": None,
        "source_timestamp_available": observed_at is not None,
        "note": (
            "API retrieval is not market observation. "
            "Cache policy does not establish a cache hit. "
            "Missing source timestamps remain unavailable."
        ),
    }
