from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PAGE = (
    ROOT
    / "frontend/app/admin/execution-control/page.tsx"
)

SERVICE = (
    ROOT
    / "frontend/services/executionControlService.ts"
)

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


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_execution_control_page_is_authenticated_admin_surface() -> None:
    text = read(PAGE)

    assert '"use client"' in text
    assert "Execution control." in text
    assert "NeuroVest Administration" in text


def test_page_loads_server_authoritative_control_state() -> None:
    text = read(PAGE)

    assert "loadExecutionControl" in text
    assert "refreshControl" in text
    assert 'data-testid="execution-control-current-mode"' in text
    assert 'data-testid="execution-control-record"' in text


def test_page_supports_safe_simulation_and_locked_transitions() -> None:
    text = read(PAGE)

    assert "transitionExecutionControl" in text
    assert "SELECTABLE_EXECUTION_MODES" in text

    assert (
        "SAFE:" in text
        or '"SAFE"' in text
    )

    assert (
        "SIMULATION:" in text
        or '"SIMULATION"' in text
    )

    assert (
        "LOCKED:" in text
        or '"LOCKED"' in text
    )

    assert (
        'data-testid="execution-control-transition-button"'
        in text
    )


def test_emergency_stop_uses_dedicated_confirmed_action() -> None:
    text = read(PAGE)

    assert "activateExecutionEmergencyStop" in text
    assert '"EMERGENCY STOP"' in text
    assert 'data-testid="execution-control-emergency-confirmation"' in text
    assert 'data-testid="execution-control-emergency-button"' in text


def test_page_does_not_offer_live_execution() -> None:
    text = read(PAGE)

    assert "Live broker execution is not enabled" in text
    assert "enableLiveExecution" not in text
    assert "activateLiveTrading" not in text
    assert "brokerExecute" not in text


def test_frontend_service_targets_all_control_proxies() -> None:
    text = read(SERVICE)

    assert '"/api/v1/admin/execution-control"' in text

    assert (
        '"/api/v1/admin/execution-control/transition"'
        in text
    )

    assert (
        '"/api/v1/admin/execution-control/emergency-stop"'
        in text
    )


def test_all_control_proxies_use_authenticated_backend_fetch() -> None:
    for path in (
        STATUS_PROXY,
        TRANSITION_PROXY,
        EMERGENCY_PROXY,
    ):
        text = read(path)

        assert "backendFetch" in text
        assert "X-Neurovest-Source" in text


def test_transition_proxy_rejects_direct_emergency_stop_selection() -> None:
    text = read(TRANSITION_PROXY)

    allowed_block = text[
        text.index(
            "const ALLOWED_MODES"
        ):
        text.index(
            "function errorResponse"
        )
    ]

    assert '"SAFE"' in allowed_block
    assert '"SIMULATION"' in allowed_block
    assert '"LOCKED"' in allowed_block
    assert '"EMERGENCY_STOP"' not in allowed_block
