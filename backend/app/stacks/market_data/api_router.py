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
