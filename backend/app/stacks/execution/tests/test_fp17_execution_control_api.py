from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute

from backend.app.main import app
from backend.app.stacks.execution.execution_control import (
    OperatingMode,
)
from backend.app.stacks.identity_auth.admin_read_router import (
    activate_execution_emergency_stop,
    get_execution_control_status,
    transition_execution_control,
)


ROOT = Path(__file__).resolve().parents[5]

ROUTER = (
    ROOT
    / "backend/app/stacks/identity_auth/admin_read_router.py"
)


def read_router() -> str:
    assert ROUTER.exists()

    return ROUTER.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def application_paths() -> dict[str, set[str]]:
    schema = app.openapi()

    return {
        path: {
            method.upper()
            for method in operations
            if method.lower()
            in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
            }
        }
        for path, operations in schema.get(
            "paths",
            {}
        ).items()
    }


def test_execution_control_routes_exist_in_openapi() -> None:
    paths = application_paths()

    assert paths[
        "/api/v1/admin/execution-control"
    ] == {
        "GET",
    }

    assert paths[
        "/api/v1/admin/execution-control/transition"
    ] == {
        "POST",
    }

    assert paths[
        "/api/v1/admin/execution-control/emergency-stop"
    ] == {
        "POST",
    }


def test_execution_control_routes_require_admin_dependency() -> None:
    target_paths = {
        "/api/v1/admin/execution-control",
        "/api/v1/admin/execution-control/transition",
        "/api/v1/admin/execution-control/emergency-stop",
    }

    schema = app.openapi()

    for path in target_paths:
        assert path in schema["paths"]


def test_router_uses_central_execution_control() -> None:
    text = read_router()

    assert "execution_control.snapshot_dict()" in text
    assert "execution_control.transition(" in text
    assert "execution_control.emergency_stop(" in text


def test_transition_contract_uses_operating_mode_enum() -> None:
    text = read_router()

    assert "mode: OperatingMode" in text

    assert {
        mode.value
        for mode in OperatingMode
    } == {
        "SAFE",
        "SIMULATION",
        "LOCKED",
        "EMERGENCY_STOP",
    }


def test_route_functions_are_importable() -> None:
    assert callable(
        get_execution_control_status
    )

    assert callable(
        transition_execution_control
    )

    assert callable(
        activate_execution_emergency_stop
    )


def test_no_live_execution_enable_route_exists() -> None:
    paths = application_paths()

    forbidden = {
        path
        for path in paths
        if (
            "live-execution" in path
            or "enable-live" in path
            or "broker-execute" in path
        )
    }

    assert forbidden == set()
