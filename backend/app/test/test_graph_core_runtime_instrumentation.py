from pathlib import Path
import ast


MARKET = Path(
    "backend/app/stacks/market_data/"
    "market_data_service.py"
)

RISK = Path(
    "backend/app/stacks/risk/"
    "risk_service.py"
)

STRATEGY = Path(
    "backend/app/stacks/strategy/"
    "strategy_service.py"
)

DATABASE = Path(
    "backend/app/stacks/db_runtime/"
    "database.py"
)


def source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
    )


def function_source(
    path: Path,
    name: str,
) -> str:
    text = source(path)

    tree = ast.parse(
        text,
        filename=str(path),
    )

    matches = [
        node
        for node in ast.walk(tree)
        if (
            isinstance(
                node,
                ast.AsyncFunctionDef,
            )
            and node.name == name
        )
    ]

    assert len(matches) == 1

    segment = ast.get_source_segment(
        text,
        matches[0],
    )

    assert segment is not None

    return segment


def assert_trace_import(path: Path) -> None:
    text = source(path)

    assert (
        "from backend.app.core.runtime_trace import ("
        in text
    )

    assert "create_trace_id," in text
    assert "emit_runtime_step," in text


def test_market_api_runtime_chain_is_instrumented() -> None:
    assert_trace_import(MARKET)

    text = function_source(
        MARKET,
        "get_live_market_price_for_api",
    )

    for node in (
        "market_api",
        "market_data_facade",
        "market_runtime",
    ):
        assert f'node="{node}"' in text

    assert (
        'source="http_api"'
        in text
    )

    assert (
        'destination="market_api"'
        in text
    )

    assert (
        'destination="market_data_facade"'
        in text
    )

    assert (
        'destination="market_runtime"'
        in text
    )


def test_risk_api_runtime_chain_is_instrumented() -> None:
    assert_trace_import(RISK)

    text = function_source(
        RISK,
        "get_risk_gate_for_api",
    )

    for node in (
        "risk_api",
        "risk_facade",
        "risk_runtime",
    ):
        assert f'node="{node}"' in text

    assert (
        'destination="risk_api"'
        in text
    )

    assert (
        'destination="risk_facade"'
        in text
    )

    assert (
        'destination="risk_runtime"'
        in text
    )


def test_strategy_api_runtime_chain_is_instrumented() -> None:
    assert_trace_import(STRATEGY)

    text = function_source(
        STRATEGY,
        "get_strategy_decision_for_api",
    )

    for node in (
        "strategy_api",
        "strategy_facade",
        "strategy_runtime",
    ):
        assert f'node="{node}"' in text

    assert (
        'destination="strategy_api"'
        in text
    )

    assert (
        'destination="strategy_facade"'
        in text
    )

    assert (
        'destination="strategy_runtime"'
        in text
    )


def test_database_runtime_initialization_is_instrumented() -> None:
    assert_trace_import(DATABASE)

    text = function_source(
        DATABASE,
        "init_db",
    )

    assert (
        'event_type="DATABASE_RUNTIME_INITIALIZATION"'
        in text
    )

    assert 'node="db_runtime"' in text
    assert 'stack="db_runtime"' in text
    assert 'layer="L0"' in text


def test_instrumentation_uses_only_registered_nodes() -> None:
    combined = "\n".join(
        source(path)
        for path in (
            MARKET,
            RISK,
            STRATEGY,
            DATABASE,
        )
    )

    expected = {
        "market_api",
        "market_data_facade",
        "market_runtime",
        "risk_api",
        "risk_facade",
        "risk_runtime",
        "strategy_api",
        "strategy_facade",
        "strategy_runtime",
        "db_runtime",
    }

    for node in expected:
        assert f'node="{node}"' in combined


def test_instrumentation_does_not_enable_execution() -> None:
    combined = "\n".join(
        source(path)
        for path in (
            MARKET,
            RISK,
            STRATEGY,
            DATABASE,
        )
    )

    forbidden = (
        "live_execution_enabled = True",
        "live_execution_enabled=True",
        "paper_execution_enabled = True",
        "paper_execution_enabled=True",
        "OperatingMode.LIVE",
        "execute_trade(",
        "place_order(",
        "submit_order(",
    )

    for value in forbidden:
        assert value not in combined
