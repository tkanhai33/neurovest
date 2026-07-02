from app.stacks.market_data.contracts.market_data_contract import (
    CandleContract,
    ExchangeStatus,
    MarketDataProvider,
    MarketDataSkeletonStatus,
    QuoteContract,
    SymbolContract,
)


def test_symbol_contract_shape() -> None:
    symbol = SymbolContract(symbol="RY.TO", exchange="TSX", currency="CAD")

    assert symbol.symbol == "RY.TO"
    assert symbol.exchange == "TSX"
    assert symbol.currency == "CAD"


def test_quote_contract_shape() -> None:
    quote = QuoteContract(
        symbol="RY.TO",
        provider=MarketDataProvider.YFINANCE,
        price=None,
        currency="CAD",
    )

    assert quote.symbol == "RY.TO"
    assert quote.provider == MarketDataProvider.YFINANCE
    assert quote.price is None
    assert quote.currency == "CAD"


def test_candle_contract_shape() -> None:
    candle = CandleContract(
        symbol="RY.TO",
        provider=MarketDataProvider.YFINANCE,
        timestamp="2026-07-01T00:00:00Z",
    )

    assert candle.symbol == "RY.TO"
    assert candle.provider == MarketDataProvider.YFINANCE
    assert candle.timestamp == "2026-07-01T00:00:00Z"


def test_exchange_status_contract_shape() -> None:
    assert ExchangeStatus.UNKNOWN == "unknown"
    assert ExchangeStatus.OPEN == "open"
    assert ExchangeStatus.CLOSED == "closed"


def test_market_data_skeleton_status_locked() -> None:
    status = MarketDataSkeletonStatus()

    assert status.stack == "market_data"
    assert status.phase == "phase_4_skeleton"
    assert status.yfinance_adapter_implemented is False
    assert status.finnhub_adapter_implemented is False
    assert status.live_provider_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.risk_logic_implemented is False
    assert status.business_logic_implemented is False
