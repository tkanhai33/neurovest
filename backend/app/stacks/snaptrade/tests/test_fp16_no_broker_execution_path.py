from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]

SNAPTRADE_ROOT = (
    ROOT
    / "backend/app/stacks/snaptrade"
)

PAPER_BROKER = (
    ROOT
    / "backend/app/stacks/execution/paper_broker.py"
)

FORBIDDEN_IMPORT_SEGMENTS = (
    ".trading",
    ".orders",
    ".order_placement",
    ".trade_execution",
)

FORBIDDEN_FUNCTION_NAMES = {
    "place_order",
    "submit_order",
    "execute_order",
    "execute_trade",
    "send_order",
    "create_order",
    "cancel_order",
    "replace_order",
    "preview_order",
    "place_force_order",
}

FORBIDDEN_ROUTE_MARKERS = (
    "/orders",
    "/trade",
    "/trading",
    "/execute",
)


def production_python_files() -> list[Path]:
    return sorted(
        path
        for path in SNAPTRADE_ROOT.rglob("*.py")
        if "tests" not in path.parts
        and "__pycache__" not in path.parts
    )


def dotted_name(
    node: ast.AST,
) -> str | None:
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    if not isinstance(
        node,
        ast.Attribute,
    ):
        return None

    parts: list[str] = []
    current: ast.AST = node

    while isinstance(
        current,
        ast.Attribute,
    ):
        parts.append(
            current.attr
        )

        current = current.value

    if isinstance(
        current,
        ast.Name,
    ):
        parts.append(
            current.id
        )

    return ".".join(
        reversed(parts)
    )


def test_snaptrade_stack_imports_no_trading_namespace() -> None:
    violations: list[str] = []

    for path in production_python_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(
            text,
            filename=str(path),
        )

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.ImportFrom,
            ):
                module = (
                    node.module
                    or ""
                ).lower()

                if any(
                    segment in module
                    for segment in FORBIDDEN_IMPORT_SEGMENTS
                ):
                    violations.append(
                        f"{path.relative_to(ROOT)}:"
                        f"{node.lineno}: "
                        f"from {module} import ..."
                    )

            elif isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    module = (
                        alias.name.lower()
                    )

                    if any(
                        segment in module
                        for segment in FORBIDDEN_IMPORT_SEGMENTS
                    ):
                        violations.append(
                            f"{path.relative_to(ROOT)}:"
                            f"{node.lineno}: "
                            f"import {module}"
                        )

    assert violations == [], "\n".join(
        violations
    )


def test_snaptrade_stack_calls_no_order_execution_function() -> None:
    violations: list[str] = []

    for path in production_python_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        tree = ast.parse(
            text,
            filename=str(path),
        )

        for node in ast.walk(tree):
            if not isinstance(
                node,
                ast.Call,
            ):
                continue

            name = dotted_name(
                node.func
            )

            if not name:
                continue

            final_name = (
                name.split(".")[-1]
                .lower()
            )

            if (
                final_name
                in FORBIDDEN_FUNCTION_NAMES
            ):
                violations.append(
                    f"{path.relative_to(ROOT)}:"
                    f"{node.lineno}: {name}"
                )

    assert violations == [], "\n".join(
        violations
    )


def test_snaptrade_router_exposes_no_order_or_trading_route() -> None:
    router = (
        SNAPTRADE_ROOT
        / "api_router.py"
    )

    text = router.read_text(
        encoding="utf-8",
        errors="ignore",
    ).lower()

    violations = [
        marker
        for marker in FORBIDDEN_ROUTE_MARKERS
        if marker in text
    ]

    assert violations == [], (
        "Forbidden SnapTrade route markers: "
        + ", ".join(
            violations
        )
    )


def test_snaptrade_service_forces_read_only_connection_mode() -> None:
    service = (
        SNAPTRADE_ROOT
        / "application/connection_service.py"
    )

    text = service.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    tree = ast.parse(
        text,
        filename=str(service),
    )

    string_constants = {
        node.value.lower()
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.Constant,
        )
        and isinstance(
            node.value,
            str,
        )
    }

    read_mode_detected = (
        "read" in string_constants
    )

    forbidden_modes = {
        "trade",
        "trade-if-available",
    }.intersection(
        string_constants
    )

    trading_disabled_assignment = False

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Assign,
        ):
            continue

        if not isinstance(
            node.value,
            ast.Constant,
        ) or node.value.value is not False:
            continue

        for assignment_target in node.targets:
            if not isinstance(
                assignment_target,
                ast.Subscript,
            ):
                continue

            slice_node = (
                assignment_target.slice
            )

            if (
                isinstance(
                    slice_node,
                    ast.Constant,
                )
                and slice_node.value
                == "trading_enabled"
            ):
                trading_disabled_assignment = True

    assert read_mode_detected, (
        "The SnapTrade connection service does not contain "
        "a read-only connection-mode constant."
    )

    assert forbidden_modes == set(), (
        "Forbidden SnapTrade connection modes detected: "
        + ", ".join(
            sorted(
                forbidden_modes
            )
        )
    )

    assert trading_disabled_assignment, (
        "The SnapTrade public connection state does not "
        "explicitly set trading_enabled to False."
    )


def test_detected_execute_trade_calls_belong_only_to_paper_broker() -> None:
    assert PAPER_BROKER.exists()

    paper_text = PAPER_BROKER.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    assert "execute_trade" in paper_text

    snaptrade_hits: list[str] = []

    for path in production_python_files():
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if "execute_trade" in text:
            snaptrade_hits.append(
                path.relative_to(ROOT).as_posix()
            )

    assert snaptrade_hits == []
