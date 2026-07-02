from app.stacks.research.contracts.research_contract import (
    BacktestRequestContract,
    IndicatorRequestContract,
    ResearchOutputContract,
    ResearchOutputType,
    ResearchSkeletonStatus,
    ScreenerRequestContract,
)


def test_indicator_request_contract_shape() -> None:
    request = IndicatorRequestContract(
        symbol="RY.TO",
        indicator_name="rsi",
        period="14",
    )

    assert request.symbol == "RY.TO"
    assert request.indicator_name == "rsi"
    assert request.period == "14"


def test_screener_request_contract_shape() -> None:
    request = ScreenerRequestContract(
        universe_name="tsx_core",
        filter_name="large_cap",
    )

    assert request.universe_name == "tsx_core"
    assert request.filter_name == "large_cap"


def test_backtest_request_contract_shape() -> None:
    request = BacktestRequestContract(
        strategy_name="placeholder_strategy",
        symbol="RY.TO",
        start_date=None,
        end_date=None,
    )

    assert request.strategy_name == "placeholder_strategy"
    assert request.symbol == "RY.TO"


def test_research_output_contract_shape() -> None:
    output = ResearchOutputContract(
        output_type=ResearchOutputType.INDICATOR,
        symbol="RY.TO",
        summary=None,
    )

    assert output.output_type == ResearchOutputType.INDICATOR
    assert output.symbol == "RY.TO"
    assert output.summary is None


def test_research_skeleton_status_locked() -> None:
    status = ResearchSkeletonStatus()

    assert status.stack == "research"
    assert status.phase == "phase_6_skeleton"
    assert status.indicators_implemented is False
    assert status.screeners_implemented is False
    assert status.backtests_implemented is False
    assert status.news_analysis_implemented is False
    assert status.market_data_calls_enabled is False
    assert status.strategy_logic_implemented is False
    assert status.trading_logic_implemented is False
    assert status.business_logic_implemented is False
