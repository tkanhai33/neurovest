from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import ast

import backend.app.main as main_module
from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[5]
MAIN_FILE = ROOT / "backend/app/main.py"


def test_backend_main_imports_fastapi_http_exception() -> None:
    source = MAIN_FILE.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(MAIN_FILE),
    )

    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "fastapi"
        and any(
            alias.name == "HTTPException"
            for alias in node.names
        )
    ]

    assert imports


def test_backend_main_http_exception_symbol_is_bound() -> None:
    assert main_module.HTTPException is HTTPException


def test_owned_portfolio_facade_never_raises_unbound_name() -> None:
    function = getattr(
        main_module,
        "_owned_portfolio_facade_for_principal",
    )

    principal = SimpleNamespace(
        subject="objective-5i-unbound-owner",
        email="objective-5i-unbound@neurovest.local",
    )

    try:
        function(
            principal
        )
    except HTTPException:
        # A missing owner binding may correctly produce an HTTP error.
        pass
    except NameError as exc:
        raise AssertionError(
            "Portfolio ownership rejection raised NameError "
            "instead of FastAPI HTTPException."
        ) from exc
