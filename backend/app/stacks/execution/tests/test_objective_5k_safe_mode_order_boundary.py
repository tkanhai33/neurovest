from __future__ import annotations

from pathlib import Path
import ast


MAIN = Path(
    "backend/app/main.py"
)

CONTROL = Path(
    "backend/app/stacks/execution/execution_control.py"
)


def _function_source(
    path: Path,
    function_name: str,
) -> str:
    source = path.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == function_name
    ]

    assert len(matches) == 1

    return (
        ast.get_source_segment(
            source,
            matches[0],
        )
        or ""
    )


def test_safe_mode_execution_guard_remains_enforced() -> None:
    source = _function_source(
        CONTROL,
        "assert_paper_execution_allowed",
    )

    assert (
        "OperatingMode.SIMULATION.value"
        in source
    )

    assert (
        "snapshot.paper_execution_enabled"
        in source
    )

    assert (
        "not snapshot.live_execution_enabled"
        in source
    )

    assert (
        "not snapshot.emergency_stop_active"
        in source
    )

    assert (
        "raise ExecutionBlockedError"
        in source
    )


def test_paper_order_route_catches_execution_block() -> None:
    source = _function_source(
        MAIN,
        "submit_authenticated_paper_order",
    )

    assert (
        "except ExecutionBlockedError as error"
        in source
    )

    assert (
        "status_code=409"
        in source
    )

    assert (
        '"reason": '
        '"paper_execution_not_allowed"'
        in source
    )


def test_blocked_response_remains_paper_only() -> None:
    source = _function_source(
        MAIN,
        "submit_authenticated_paper_order",
    )

    assert (
        '"execution_mode": "paper"'
        in source
    )

    assert (
        '"live_execution": False'
        in source
    )

    assert (
        '"owner_scope": '
        '"authenticated_account"'
        in source
    )


def test_success_response_remains_paper_only() -> None:
    source = _function_source(
        MAIN,
        "submit_authenticated_paper_order",
    )

    assert (
        '"status": "processed"'
        in source
    )

    assert (
        '"execution_mode": "paper"'
        in source
    )

    assert (
        '"live_execution": False'
        in source
    )


def test_route_does_not_change_execution_mode() -> None:
    source = _function_source(
        MAIN,
        "submit_authenticated_paper_order",
    )

    assert (
        "set_mode(" not in source
    )

    assert (
        "enable_paper_execution(" not in source
    )

    assert (
        "enable_live_execution(" not in source
    )

    assert (
        "disable_emergency_stop(" not in source
    )
