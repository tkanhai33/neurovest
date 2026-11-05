from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from backend.app.stacks.market_data.dto import (
    HistoricalBar,
    HistoricalBarsResult,
)
from backend.app.stacks.market_data import bars as bars_module


def make_result(
    *,
    request,
    count: int,
) -> HistoricalBarsResult:
    base = datetime(
        2026,
        1,
        1,
        tzinfo=UTC,
    )

    bars = tuple(
        HistoricalBar(
            symbol=request.symbol,
            timestamp=(
                base +
                timedelta(
                    days=index
                )
            ),
            interval=request.interval,
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.5 + index,
            volume=1000.0 + index,
            provider="fixture",
        )
        for index in range(count)
    )

    return HistoricalBarsResult(
        request=request,
        provider="fixture",
        bars=bars,
        fetched_at=datetime(
            2026,
            8,
            1,
            tzinfo=UTC,
        ),
        complete=True,
        warnings=(),
    )


class FixtureRouter:
    def __init__(
        self,
        *,
        returned_count: int,
    ):
        self.returned_count = (
            returned_count
        )
        self.requests = []

    def get_historical_bars(
        self,
        request,
    ):
        self.requests.append(
            request
        )

        return make_result(
            request=request,
            count=self.returned_count,
        )


class FailingRouter:
    def get_historical_bars(
        self,
        request,
    ):
        raise RuntimeError(
            "fixture provider unavailable"
        )


@pytest.mark.parametrize(
    "limit",
    [
        5,
        20,
        50,
        200,
        253,
    ],
)
def test_get_bars_returns_exact_real_normalized_limit(
    monkeypatch,
    limit,
):
    router = FixtureRouter(
        returned_count=limit + 4
    )

    runtime = SimpleNamespace(
        router=router
    )

    monkeypatch.setattr(
        bars_module,
        "get_market_data_runtime",
        lambda: runtime,
    )

    result = bars_module.get_bars(
        " aapl ",
        limit=limit,
    )

    assert len(result) == limit
    assert len(router.requests) == 1

    request = router.requests[0]

    assert request.symbol == "AAPL"
    assert request.interval == "1d"
    assert request.adjusted is True
    assert request.limit == limit
    assert request.start.tzinfo is not None
    assert request.end.tzinfo is not None
    assert request.start < request.end

    assert result[0]["symbol"] == "AAPL"
    assert result[0]["provider"] == "fixture"
    assert result[0]["interval"] == "1d"

    assert set(result[0]) == {
        "symbol",
        "timestamp",
        "interval",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "provider",
    }

    assert all(
        record["provider"] == "fixture"
        for record in result
    )


def test_get_bars_fails_closed_on_provider_error(
    monkeypatch,
):
    runtime = SimpleNamespace(
        router=FailingRouter()
    )

    monkeypatch.setattr(
        bars_module,
        "get_market_data_runtime",
        lambda: runtime,
    )

    with pytest.raises(
        bars_module.HistoricalBarsUnavailableError,
        match="truthful historical bars are unavailable",
    ):
        bars_module.get_bars(
            "AAPL",
            limit=20,
        )


def test_get_bars_fails_closed_on_insufficient_data(
    monkeypatch,
):
    router = FixtureRouter(
        returned_count=19
    )

    runtime = SimpleNamespace(
        router=router
    )

    monkeypatch.setattr(
        bars_module,
        "get_market_data_runtime",
        lambda: runtime,
    )

    with pytest.raises(
        bars_module.HistoricalBarsInsufficientDataError,
        match=(
            "requested 20, received 19"
        ),
    ):
        bars_module.get_bars(
            "AAPL",
            limit=20,
        )


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        5001,
        1.5,
        True,
    ],
)
def test_get_bars_rejects_invalid_limit(
    value,
):
    with pytest.raises(
        ValueError
    ):
        bars_module.get_bars(
            "AAPL",
            limit=value,
        )


def test_get_bars_rejects_empty_symbol():
    with pytest.raises(
        ValueError,
        match="symbol must not be empty",
    ):
        bars_module.get_bars(
            "   ",
            limit=5,
        )


def test_healthcheck_is_network_free():
    result = bars_module.healthcheck()

    assert result == {
        "component":
            "truthful_historical_bars_compatibility",

        "healthy":
            True,

        "provider_owner":
            "canonical_market_data_runtime",

        "interval":
            "1d",

        "fabricated_fallback":
            False,

        "network_called":
            False,
    }


def test_source_contains_no_legacy_fabricated_values():
    source = (
        bars_module.__file__
    )

    text = open(
        source,
        encoding="utf-8",
    ).read()

    forbidden = (
        '{"close": 150.0}',
        '{"close": 150.5}',
        '{"close": 151.0}',
        '{"close": 149.5}',
        '{"close": 150.2}',
        "np.random",
        "random.random",
    )

    assert all(
        token not in text
        for token in forbidden
    )
