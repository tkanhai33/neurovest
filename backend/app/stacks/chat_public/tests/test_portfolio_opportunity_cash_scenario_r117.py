from backend.app.stacks.chat_public import (
    portfolio_opportunity_research_r117 as research,
)


START = "2026-08-04"
END = "2026-11-03"


def _candidate(symbol, currency, start_price, end_price):
    return {
        "chosen": {"symbol": symbol, "currency": currency},
        "history": {
            "prices": {
                START: start_price,
                END: end_price,
            },
        },
    }


def test_cash_scenarios_keep_currencies_separate_and_use_endpoint_fx():
    lines = research._cash_scenario_lines(
        balance_snapshot={
            "balances": [
                {"currency": "CAD", "cash_amount": "100"},
                {"currency": "USD", "cash_amount": "300"},
                {"currency": "CAD", "cash_amount": "-20"},
                {"currency": "EUR", "cash_amount": "50"},
                {"currency": "", "cash_amount": "10"},
            ],
        },
        balance_error=None,
        candidates=[
            _candidate("CADWIN", "CAD", 100.0, 110.0),
            # History prices are CAD-normalized: 100 USD * 1.30,
            # then 110 USD * 1.40.
            _candidate("USDWIN", "USD", 130.0, 154.0),
        ],
        start_day=START,
        end_day=END,
        fx_rates={START: 1.30, END: 1.40},
    )
    report = "\n".join(lines)

    assert "Stored positive CAD cash used for scenarios: 100.00 CAD." in report
    assert "Stored positive USD cash used for scenarios: 300.00 USD." in report
    assert "hypothetical 100.00 CAD" in report
    assert "becomes 110.00 CAD" in report
    assert "hypothetical 300.00 USD" in report
    assert "becomes 330.00 USD" in report
    assert "Ignored 3 balance row(s)" in report


def test_cash_scenario_reports_balance_read_failure():
    lines = research._cash_scenario_lines(
        balance_snapshot=None,
        balance_error="RuntimeError",
        candidates=[],
        start_day=START,
        end_day=END,
        fx_rates={},
    )

    assert any("balances could not be read (RuntimeError)" in line for line in lines)


def test_cash_scenario_handles_missing_price_endpoint():
    lines = research._cash_scenario_lines(
        balance_snapshot={
            "balances": [{"currency": "CAD", "cash_amount": "25"}],
        },
        balance_error=None,
        candidates=[{
            "chosen": {"symbol": "GAP", "currency": "CAD"},
            "history": {"prices": {START: 100.0}},
        }],
        start_day=START,
        end_day=END,
        fx_rates={},
    )
    report = "\n".join(lines)

    assert "a price is missing on" in report
    assert "GAP: same-currency CAD cash scenario unavailable;" in report
    assert "a price is missing on" in report
