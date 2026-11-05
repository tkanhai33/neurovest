"""Regression tests for the approved credential-filter refactor."""

import ast
import runpy
from pathlib import Path

import pytest

ROOT = Path.home() / "Neurovest"
RELATIVE = (
    "backend/app/stacks/chat_public/"
    "developer_repository_inspection.py"
)
TEST_RELATIVE = (
    "backend/app/stacks/chat_public/tests/"
    "test_developer_sensitive_filter_regression.py"
)

EXPECTED_TERMS = (
    "password=", "secret=", "api_key=", "token=",
    "authorization:", "bearer ",
)


@pytest.fixture(scope="module")
def module():
    return runpy.run_path(str(ROOT / RELATIVE))


@pytest.mark.parametrize("term", EXPECTED_TERMS)
def test_sensitive_terms(module, term):
    check = module["_is_sensitive_term"]
    assert check(term + "example")
    assert check(term.upper() + "EXAMPLE")
    assert check("prefix " + term + "value")


@pytest.mark.parametrize("value", (
    "", "hello world", "normal application source",
    "def calculate_total():", "return amount * quantity",
    "a harmless comment", "regular variable assignment",
    "authentication middleware", "password", "token",
    "authorization", "bearer",
))
def test_non_sensitive_lines(module, value):
    assert module["_is_sensitive_term"](value) is False


def test_exact_sensitive_term_contract():
    tree = ast.parse((ROOT / RELATIVE).read_text("utf-8"))
    helper = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and n.name == "_is_sensitive_term"
    )
    returns = [
        n for n in helper.body
        if isinstance(n, ast.Return)
    ]
    assert len(returns) == 1
    expression = returns[0].value
    assert isinstance(expression, ast.Call)
    assert isinstance(expression.func, ast.Name)
    assert expression.func.id == "any"
    gen = expression.args[0]
    assert isinstance(gen, ast.GeneratorExp)
    iterator = gen.generators[0].iter
    assert tuple(ast.literal_eval(n) for n in iterator.elts) == EXPECTED_TERMS


def test_inspection_uses_helper_with_continue():
    tree = ast.parse((ROOT / RELATIVE).read_text("utf-8"))
    function = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef)
        and n.name == "inspect_repository"
    )
    assert any(
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Call)
        and isinstance(node.test.func, ast.Name)
        and node.test.func.id == "_is_sensitive_term"
        and len(node.test.args) == 1
        and isinstance(node.test.args[0], ast.Name)
        and node.test.args[0].id == "stripped"
        and node.body
        and isinstance(node.body[0], ast.Continue)
        for node in ast.walk(function)
    )


def test_approval_pipeline_includes_regression_tests():
    namespace = runpy.run_path(
        str(ROOT / "scripts/neuro_developer_patch_apply.py")
    )
    assert TEST_RELATIVE in namespace["ALLOWED"][RELATIVE]
