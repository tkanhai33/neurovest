from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

STATUS_PROXY = (
    ROOT
    / "frontend/app/api/v1/admin/"
    "execution-control/route.ts"
)

TRANSITION_PROXY = (
    ROOT
    / "frontend/app/api/v1/admin/"
    "execution-control/transition/route.ts"
)

EMERGENCY_PROXY = (
    ROOT
    / "frontend/app/api/v1/admin/"
    "execution-control/emergency-stop/route.ts"
)

PAGE = (
    ROOT
    / "frontend/app/admin/"
    "execution-control/page.tsx"
)

SERVICE = (
    ROOT
    / "frontend/services/"
    "executionControlService.ts"
)

BACKEND_ROUTER = (
    ROOT
    / "backend/app/stacks/identity_auth/"
    "admin_read_router.py"
)

CONTROL = (
    ROOT
    / "backend/app/stacks/execution/"
    "execution_control.py"
)

BROKER = (
    ROOT
    / "backend/app/stacks/execution/"
    "paper_broker.py"
)


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_status_proxy_uses_authenticated_backend_fetch() -> None:
    text = read(
        STATUS_PROXY
    )

    assert "backendFetch" in text

    assert (
        '"/api/v1/admin/execution-control"'
        in text
    )

    assert 'method: "GET"' in text


def test_transition_proxy_calls_backend_transition_route() -> None:
    text = read(
        TRANSITION_PROXY
    )

    assert "backendFetch" in text

    assert (
        '"/api/v1/admin/execution-control/transition"'
        in text
    )

    assert 'method: "POST"' in text


def test_emergency_proxy_calls_backend_emergency_route() -> None:
    text = read(
        EMERGENCY_PROXY
    )

    assert "backendFetch" in text

    assert (
        '"/api/v1/admin/execution-control/emergency-stop"'
        in text
    )

    assert 'method: "POST"' in text


def test_admin_page_requests_all_control_routes() -> None:
    page = read(
        PAGE
    )

    service = read(
        SERVICE
    )

    assert (
        "loadExecutionControl"
        in page
    )

    assert (
        "transitionExecutionControl"
        in page
    )

    assert (
        "activateExecutionEmergencyStop"
        in page
    )

    assert (
        '"/api/v1/admin/execution-control"'
        in service
    )

    assert (
        '"/api/v1/admin/execution-control/transition"'
        in service
    )

    assert (
        '"/api/v1/admin/execution-control/emergency-stop"'
        in service
    )


def test_admin_page_exposes_safe_simulation_and_locked_modes() -> None:
    page = read(
        PAGE
    )

    service = read(
        SERVICE
    )

    for mode in (
        "SAFE",
        "SIMULATION",
        "LOCKED",
        "EMERGENCY_STOP",
    ):
        assert (
            mode in page
            or mode in service
        )

    selectable = service[
        service.index(
            "SELECTABLE_EXECUTION_MODES"
        ):
        service.index(
            "function isOperatingMode"
        )
    ]

    assert "SAFE" in selectable
    assert "SIMULATION" in selectable
    assert "LOCKED" in selectable
    assert "EMERGENCY_STOP" not in selectable


def test_admin_page_never_offers_live_execution() -> None:
    page = read(
        PAGE
    )

    service = read(
        SERVICE
    )

    combined = (
        page
        + "\n"
        + service
    )

    assert (
        "Live broker execution is not enabled"
        in page
        or "Live broker execution remains blocked"
        in page
        or "live execution remains technically disabled"
        in page.lower()
    )

    assert (
        "live_execution_enabled"
        in service
    )

    forbidden = (
        "ENABLE_LIVE",
        "enable-live",
        "live-execution",
        "activateLiveExecution",
    )

    for marker in forbidden:
        assert marker not in combined


def test_backend_routes_use_central_control() -> None:
    text = read(
        BACKEND_ROUTER
    )

    assert (
        "execution_control.snapshot_dict()"
        in text
    )

    assert (
        "execution_control.transition("
        in text
    )

    assert (
        "execution_control.emergency_stop("
        in text
    )


def test_execution_control_persists_and_fails_closed() -> None:
    text = read(
        CONTROL
    )

    assert "OperatingMode.SAFE" in text
    assert "OperatingMode.LOCKED" in text
    assert "OperatingMode.EMERGENCY_STOP" in text
    assert "_load_state" in text
    assert "_persist_state" in text
    assert "live_execution_enabled=False" in text


def test_paper_broker_uses_central_gate() -> None:
    text = read(
        BROKER
    )

    assert (
        "execution_control.assert_paper_execution_allowed()"
        in text
    )
