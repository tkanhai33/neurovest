from __future__ import annotations

import ast
from pathlib import Path


LEDGER = (
    Path(__file__).resolve().parents[2]
    / "journal_ledger" / "ledger.py"
)


def test_financial_ledger_uses_source_bar_quotes():
    text = LEDGER.read_text()
    assert (
        "from backend.app.stacks.market_data.risk_valuation_quotes import ("
        in text
    )
    assert "get_risk_valuation_quote" in text
    assert (
        "transaction_quote_loader = make_transaction_quote_loader("
        in text
    )
    assert "quote_loader=transaction_quote_loader" in text
    assert "execution_quote = await transaction_quote_loader(" in text
    assert "quote_loader=get_live_price_quote" not in text


def test_risk_quote_loader_is_transaction_scoped():
    tree = ast.parse(LEDGER.read_text())
    save = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef)
        and n.name == "save_log"
    )
    calls = [
        n for n in ast.walk(save)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "read_transaction_verified_equity"
    ]
    assert len(calls) == 1
    kwargs = {
        kw.arg: ast.unparse(kw.value)
        for kw in calls[0].keywords
    }
    assert kwargs["session"] == "session"
    assert kwargs["user_id"] == "normalized_user_id"
    assert kwargs["quote_loader"] == "transaction_quote_loader"

    factories = [
        node for node in ast.walk(save)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "make_transaction_quote_loader"
    ]
    assert len(factories) == 1
    assert len(factories[0].args) == 1
    assert ast.unparse(factories[0].args[0]) == (
        "get_risk_valuation_quote"
    )

    fill_calls = [
        node for node in ast.walk(save)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "transaction_quote_loader"
    ]
    assert len(fill_calls) == 1


def test_execution_blockade_preserved():
    text = LEDGER.read_text()
    assert text.index("transaction_risk_decision = (") < text.index(
        "paper_execution_financial_risk_not_qualified"
    ) < text.index("new_order = OrderHistory(")
    assert text.count("paper_execution_financial_risk_not_qualified") == 1
