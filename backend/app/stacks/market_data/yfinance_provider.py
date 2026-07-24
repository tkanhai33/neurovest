"""
Canonical yfinance provider wrapper.

The real yfinance-backed helper modules are imported lazily so:

- fixture-only tests do not require yfinance to be installed
- importing this provider performs no external-provider setup
- live provider dependencies are resolved only when default loaders
  are actually required
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime
from math import isfinite
from time import perf_counter
from typing import Any, Callable

from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsRequest,
    HistoricalBarsResult,
    MarketDataCapability,
    MarketQuote,
    MarketSessionState,
    ProviderHealth,
    normalize_symbol,
)


class YFinanceProviderError(RuntimeError):
    """Base error for yfinance provider failures."""


class YFinanceDependencyError(
    YFinanceProviderError
):
    """Raised when the real yfinance dependency is unavailable."""


class YFinanceQuoteError(
    YFinanceProviderError
):
    """Raised when quote retrieval or normalization fails."""


class YFinanceHistoricalBarsError(
    YFinanceProviderError
):
    """Raised when historical retrieval or normalization fails."""


class YFinanceNormalizationError(
    YFinanceProviderError
):
    """Raised when an upstream payload cannot be normalized."""


QuoteLoader = Callable[
    [str],
    object,
]

HistoricalLoader = Callable[
    [
        str,
        str,
        str,
        str,
    ],
    object,
]


def _load_default_quote_loader() -> QuoteLoader:
    """
    Build a synchronous yfinance quote loader.

    Existing NeuroVest feed helpers are asynchronous and therefore
    cannot be called directly by the synchronous MarketDataProvider
    and ProviderRouter contracts.

    This private loader performs only quote retrieval. It does not
    change feed.py, main.py, API routing, or application composition.
    """

    try:
        import yfinance as yf

    except ModuleNotFoundError as exc:
        if exc.name == "yfinance":
            raise YFinanceDependencyError(
                "The yfinance package is not installed in the "
                "active NeuroVest environment."
            ) from exc

        raise

    def load_quote(
        symbol: str,
    ) -> object:
        ticker = yf.Ticker(
            symbol
        )

        fast_info = ticker.fast_info

        price = None
        currency = None
        previous_close = None

        if fast_info is not None:
            try:
                price = fast_info.get(
                    "last_price"
                )
            except (
                AttributeError,
                KeyError,
                TypeError,
            ):
                price = None

            try:
                currency = fast_info.get(
                    "currency"
                )
            except (
                AttributeError,
                KeyError,
                TypeError,
            ):
                currency = None

            try:
                previous_close = fast_info.get(
                    "previous_close"
                )
            except (
                AttributeError,
                KeyError,
                TypeError,
            ):
                previous_close = None

        if price is None:
            history = ticker.history(
                period="5d",
                interval="1d",
                auto_adjust=False,
            )

            if history is None or history.empty:
                raise YFinanceQuoteError(
                    "yfinance returned no quote or "
                    f"history for {symbol}"
                )

            close_series = history[
                "Close"
            ].dropna()

            if close_series.empty:
                raise YFinanceQuoteError(
                    "yfinance returned no usable close "
                    f"price for {symbol}"
                )

            price = float(
                close_series.iloc[-1]
            )

            if (
                previous_close is None
                and len(close_series) > 1
            ):
                previous_close = float(
                    close_series.iloc[-2]
                )

        if currency is None:
            try:
                currency = ticker.info.get(
                    "currency"
                )
            except Exception:
                currency = None

        return {
            "symbol": symbol,
            "price": price,
            "currency": currency or "USD",
            "previous_close": previous_close,
            "observed_at": datetime.now(
                UTC
            ),
            "provider": "yfinance",
        }

    return load_quote


def _load_default_historical_loader() -> HistoricalLoader:
    try:
        from backend.app.stacks.market_data.yfinance_historical_bars_adapter import (
            get_historical_bars,
        )

    except ModuleNotFoundError as exc:
        if exc.name == "yfinance":
            raise YFinanceDependencyError(
                "The yfinance package is not installed in the "
                "active NeuroVest environment."
            ) from exc

        raise

    return get_historical_bars


def _first_present(
    mapping: Mapping[str, Any],
    names: Iterable[str],
    *,
    default: Any = None,
) -> Any:
    lowered = {
        str(key).lower(): value
        for key, value in mapping.items()
    }

    for name in names:
        if name in mapping:
            return mapping[name]

        lowered_name = name.lower()

        if lowered_name in lowered:
            return lowered[
                lowered_name
            ]

    return default


def _finite_float(
    value: object,
    field_name: str,
    *,
    allow_none: bool = False,
) -> float | None:
    if value is None:
        if allow_none:
            return None

        raise YFinanceNormalizationError(
            f"{field_name} is missing"
        )

    try:
        numeric = float(value)

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise YFinanceNormalizationError(
            f"{field_name} is not numeric"
        ) from exc

    if not isfinite(numeric):
        raise YFinanceNormalizationError(
            f"{field_name} is not finite"
        )

    return numeric


def _aware_datetime(
    value: object,
    field_name: str,
) -> datetime:
    if isinstance(value, datetime):
        parsed = value

    elif isinstance(value, date):
        parsed = datetime(
            value.year,
            value.month,
            value.day,
            tzinfo=UTC,
        )

    elif isinstance(value, (int, float)):
        parsed = datetime.fromtimestamp(
            float(value),
            tz=UTC,
        )

    elif isinstance(value, str):
        candidate = value.strip()

        if not candidate:
            raise YFinanceNormalizationError(
                f"{field_name} is empty"
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
            raise YFinanceNormalizationError(
                f"{field_name} is not a supported datetime"
            ) from exc

    else:
        raise YFinanceNormalizationError(
            f"{field_name} is not a supported datetime"
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=UTC
        )

    return parsed.astimezone(
        UTC
    )


def _session_state(
    value: object,
) -> MarketSessionState:
    if isinstance(
        value,
        MarketSessionState,
    ):
        return value

    normalized = str(
        value or ""
    ).strip().lower()

    aliases = {
        "pre": MarketSessionState.PRE_MARKET,
        "pre_market": MarketSessionState.PRE_MARKET,
        "premarket": MarketSessionState.PRE_MARKET,
        "regular": MarketSessionState.OPEN,
        "open": MarketSessionState.OPEN,
        "market": MarketSessionState.OPEN,
        "after": MarketSessionState.AFTER_HOURS,
        "after_hours": MarketSessionState.AFTER_HOURS,
        "post": MarketSessionState.AFTER_HOURS,
        "postmarket": MarketSessionState.AFTER_HOURS,
        "closed": MarketSessionState.CLOSED,
    }

    return aliases.get(
        normalized,
        MarketSessionState.UNKNOWN,
    )


def _normalize_quote_payload(
    payload: object,
    requested_symbol: str,
) -> MarketQuote:
    if isinstance(
        payload,
        MarketQuote,
    ):
        if payload.symbol != requested_symbol:
            raise YFinanceNormalizationError(
                "quote symbol does not match request"
            )

        return payload

    if isinstance(
        payload,
        (int, float),
    ):
        return MarketQuote(
            symbol=requested_symbol,
            price=float(payload),
            currency="USD",
            observed_at=datetime.now(
                UTC
            ),
            provider="yfinance",
        )

    if not isinstance(
        payload,
        Mapping,
    ):
        raise YFinanceNormalizationError(
            "quote payload must be a mapping, number, "
            "or MarketQuote"
        )

    symbol = normalize_symbol(
        str(
            _first_present(
                payload,
                (
                    "symbol",
                    "ticker",
                ),
                default=requested_symbol,
            )
        )
    )

    if symbol != requested_symbol:
        raise YFinanceNormalizationError(
            "quote symbol does not match request"
        )

    price = _finite_float(
        _first_present(
            payload,
            (
                "price",
                "regularMarketPrice",
                "last_price",
                "last",
                "close",
                "current_price",
            ),
        ),
        "price",
    )

    assert price is not None

    observed_raw = _first_present(
        payload,
        (
            "observed_at",
            "timestamp",
            "datetime",
            "time",
            "regularMarketTime",
        ),
        default=datetime.now(
            UTC
        ),
    )

    return MarketQuote(
        symbol=symbol,
        price=price,
        currency=str(
            _first_present(
                payload,
                (
                    "currency",
                    "currency_code",
                ),
                default="USD",
            )
        ).strip().upper() or "USD",
        observed_at=_aware_datetime(
            observed_raw,
            "observed_at",
        ),
        provider=str(
            _first_present(
                payload,
                (
                    "provider",
                    "source",
                ),
                default="yfinance",
            )
        ).strip() or "yfinance",
        bid=_finite_float(
            _first_present(
                payload,
                (
                    "bid",
                    "bid_price",
                ),
            ),
            "bid",
            allow_none=True,
        ),
        ask=_finite_float(
            _first_present(
                payload,
                (
                    "ask",
                    "ask_price",
                ),
            ),
            "ask",
            allow_none=True,
        ),
        previous_close=_finite_float(
            _first_present(
                payload,
                (
                    "previous_close",
                    "previousClose",
                    "regularMarketPreviousClose",
                ),
            ),
            "previous_close",
            allow_none=True,
        ),
        volume=_finite_float(
            _first_present(
                payload,
                (
                    "volume",
                    "regularMarketVolume",
                ),
            ),
            "volume",
            allow_none=True,
        ),
        session=_session_state(
            _first_present(
                payload,
                (
                    "session",
                    "market_state",
                    "marketState",
                ),
            )
        ),
        delayed=bool(
            _first_present(
                payload,
                (
                    "delayed",
                    "is_delayed",
                ),
                default=False,
            )
        ),
        metadata={
            "upstream_payload_type": (
                type(payload).__name__
            ),
        },
    )


def _bar_records(
    payload: object,
) -> tuple[
    Mapping[str, Any],
    ...,
]:
    records: object = payload

    if isinstance(
        payload,
        Mapping,
    ):
        records = _first_present(
            payload,
            (
                "bars",
                "data",
                "results",
                "history",
            ),
            default=payload,
        )

        if records is payload:
            lowered_keys = {
                str(key).lower()
                for key in payload.keys()
            }

            if {
                "open",
                "high",
                "low",
                "close",
            }.issubset(
                lowered_keys
            ):
                records = [payload]

    if isinstance(
        records,
        Mapping,
    ):
        records = [
            records
        ]

    if (
        not isinstance(
            records,
            Iterable,
        )
        or isinstance(
            records,
            (
                str,
                bytes,
            ),
        )
    ):
        raise YFinanceNormalizationError(
            "historical payload does not contain iterable bars"
        )

    normalized = []

    for item in records:
        if not isinstance(
            item,
            Mapping,
        ):
            raise YFinanceNormalizationError(
                "historical bar is not a mapping"
            )

        normalized.append(item)

    return tuple(normalized)


def _normalize_bar(
    payload: Mapping[str, Any],
    request: HistoricalBarsRequest,
) -> HistoricalBar:
    symbol = normalize_symbol(
        str(
            _first_present(
                payload,
                (
                    "symbol",
                    "ticker",
                ),
                default=request.symbol,
            )
        )
    )

    if symbol != request.symbol:
        raise YFinanceNormalizationError(
            "historical bar symbol does not match request"
        )

    timestamp = _aware_datetime(
        _first_present(
            payload,
            (
                "timestamp",
                "datetime",
                "date",
                "time",
                "index",
            ),
        ),
        "bar timestamp",
    )

    open_price = _finite_float(
        _first_present(
            payload,
            (
                "open",
                "Open",
            ),
        ),
        "open",
    )

    high_price = _finite_float(
        _first_present(
            payload,
            (
                "high",
                "High",
            ),
        ),
        "high",
    )

    low_price = _finite_float(
        _first_present(
            payload,
            (
                "low",
                "Low",
            ),
        ),
        "low",
    )

    close_price = _finite_float(
        _first_present(
            payload,
            (
                "close",
                "Close",
                "adj_close",
                "Adj Close",
            ),
        ),
        "close",
    )

    volume = _finite_float(
        _first_present(
            payload,
            (
                "volume",
                "Volume",
            ),
            default=0,
        ),
        "volume",
    )

    assert open_price is not None
    assert high_price is not None
    assert low_price is not None
    assert close_price is not None
    assert volume is not None

    return HistoricalBar(
        symbol=symbol,
        timestamp=timestamp,
        interval=request.interval,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=volume,
        provider="yfinance",
    )


def _normalize_historical_payload(
    payload: object,
    request: HistoricalBarsRequest,
) -> HistoricalBarsResult:
    if isinstance(
        payload,
        HistoricalBarsResult,
    ):
        if payload.request.symbol != request.symbol:
            raise YFinanceNormalizationError(
                "historical result symbol does not match request"
            )

        return payload

    records = _bar_records(
        payload
    )

    bars = tuple(
        sorted(
            (
                _normalize_bar(
                    item,
                    request,
                )
                for item in records
            ),
            key=lambda bar: (
                bar.timestamp
            ),
        )
    )

    warnings: tuple[str, ...] = ()
    complete = True

    if isinstance(
        payload,
        Mapping,
    ):
        warning_value = _first_present(
            payload,
            (
                "warnings",
                "warning",
            ),
        )

        if isinstance(
            warning_value,
            str,
        ):
            warnings = (
                warning_value,
            )

        elif (
            isinstance(
                warning_value,
                Iterable,
            )
            and not isinstance(
                warning_value,
                (
                    str,
                    bytes,
                ),
            )
        ):
            warnings = tuple(
                str(item)
                for item in warning_value
            )

        complete = bool(
            _first_present(
                payload,
                (
                    "complete",
                    "is_complete",
                ),
                default=True,
            )
        )

    if request.limit is not None:
        bars = bars[
            : request.limit
        ]

    return HistoricalBarsResult(
        request=request,
        provider="yfinance",
        bars=bars,
        fetched_at=datetime.now(
            UTC
        ),
        complete=complete,
        warnings=warnings,
    )


class YFinanceProvider:
    """Canonical wrapper around existing yfinance helpers."""

    def __init__(
        self,
        *,
        quote_loader: QuoteLoader | None = None,
        historical_loader: HistoricalLoader | None = None,
    ) -> None:
        self._quote_loader = quote_loader
        self._historical_loader = (
            historical_loader
        )

    @property
    def provider_name(self) -> str:
        return "yfinance"

    @property
    def capabilities(
        self,
    ) -> frozenset[
        MarketDataCapability
    ]:
        return frozenset(
            {
                MarketDataCapability.QUOTE,
                MarketDataCapability.HISTORICAL_BARS,
            }
        )

    def supports(
        self,
        capability: MarketDataCapability,
    ) -> bool:
        return capability in self.capabilities

    def _quote_dependency(
        self,
    ) -> QuoteLoader:
        if self._quote_loader is None:
            self._quote_loader = (
                _load_default_quote_loader()
            )

        return self._quote_loader

    def _historical_dependency(
        self,
    ) -> HistoricalLoader:
        if self._historical_loader is None:
            self._historical_loader = (
                _load_default_historical_loader()
            )

        return self._historical_loader

    def get_quote(
        self,
        symbol: str,
    ) -> MarketQuote:
        normalized_symbol = (
            normalize_symbol(
                symbol
            )
        )

        try:
            payload = self._quote_dependency()(
                normalized_symbol
            )

        except YFinanceDependencyError:
            raise

        except Exception as exc:
            raise YFinanceQuoteError(
                "yfinance quote retrieval failed "
                f"for {normalized_symbol}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        return _normalize_quote_payload(
            payload,
            normalized_symbol,
        )

    def get_historical_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> HistoricalBarsResult:
        try:
            payload = (
                self._historical_dependency()(
                    request.symbol,
                    request.start.date().isoformat(),
                    request.end.date().isoformat(),
                    request.interval,
                )
            )

        except YFinanceDependencyError:
            raise

        except Exception as exc:
            raise YFinanceHistoricalBarsError(
                "yfinance historical retrieval failed "
                f"for {request.symbol}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        return _normalize_historical_payload(
            payload,
            request,
        )

    def healthcheck(
        self,
    ) -> ProviderHealth:
        started = perf_counter()

        healthy = (
            self._quote_loader is not None
            and self._historical_loader
            is not None
        )

        message = (
            "injected provider dependencies available"
            if healthy
            else (
                "provider wrapper available; real dependencies "
                "not loaded"
            )
        )

        return ProviderHealth(
            provider=self.provider_name,
            healthy=True,
            checked_at=datetime.now(
                UTC
            ),
            latency_ms=(
                perf_counter()
                - started
            )
            * 1000,
            message=message,
            capabilities=self.capabilities,
        )


def healthcheck() -> dict[str, object]:
    health = (
        YFinanceProvider()
        .healthcheck()
    )

    return {
        "component": "yfinance_provider",
        "healthy": health.healthy,
        "provider": health.provider,
        "capabilities": sorted(
            item.value
            for item in health.capabilities
        ),
        "dependencies_loaded": False,
        "network_called": False,
    }
