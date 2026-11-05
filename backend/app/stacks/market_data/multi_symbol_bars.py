"""Bounded, fail-closed multi-symbol daily OHLCV access."""

from __future__ import annotations

from collections.abc import Iterable

from backend.app.stacks.market_data.bars import get_bars

DEFAULT_HISTORY_LIMIT = 253
MAX_SYMBOLS_PER_REQUEST = 32


class MultiSymbolBarsContractError(ValueError):
    """The requested multi-symbol historical-bars contract is invalid."""


def _normalized_symbols(
    symbols: Iterable[object],
    *,
    max_symbols: int,
) -> tuple[str, ...]:
    if isinstance(symbols, (str, bytes)):
        raise MultiSymbolBarsContractError(
            "symbols must be an iterable of individual symbols"
        )

    if max_symbols < 1:
        raise MultiSymbolBarsContractError(
            "max_symbols must be at least one"
        )

    normalized: list[str] = []
    seen: set[str] = set()

    try:
        iterator = iter(symbols)
    except TypeError as exc:
        raise MultiSymbolBarsContractError(
            "symbols must be iterable"
        ) from exc

    for raw_symbol in iterator:
        symbol = str(raw_symbol).strip().upper()

        if not symbol:
            raise MultiSymbolBarsContractError(
                "multi-symbol request contains an empty symbol"
            )

        if symbol in seen:
            continue

        seen.add(symbol)
        normalized.append(symbol)

        if len(normalized) > max_symbols:
            raise MultiSymbolBarsContractError(
                "multi-symbol request exceeds configured symbol limit"
            )

    if not normalized:
        raise MultiSymbolBarsContractError(
            "multi-symbol request must include at least one symbol"
        )

    return tuple(normalized)


def get_daily_bars_for_symbols(
    symbols: Iterable[object],
    *,
    limit: int = DEFAULT_HISTORY_LIMIT,
    max_symbols: int = MAX_SYMBOLS_PER_REQUEST,
) -> dict[str, list[dict[str, object]]]:
    """Return exactly ``limit`` truthful daily bars for every requested symbol.

    The existing canonical ``get_bars`` contract remains the sole owner of
    provider routing, caching, normalization, and insufficient-history
    handling. This function is intentionally all-or-nothing: if any symbol
    cannot satisfy the request, it raises and returns no partial portfolio
    dataset.
    """

    normalized_symbols = _normalized_symbols(
        symbols,
        max_symbols=max_symbols,
    )

    result: dict[str, list[dict[str, object]]] = {}

    for symbol in normalized_symbols:
        result[symbol] = get_bars(
            symbol,
            limit=limit,
        )

    return result
