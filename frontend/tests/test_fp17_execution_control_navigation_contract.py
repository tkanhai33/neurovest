from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

ADMIN_PAGE = (
    ROOT
    / "frontend/app/admin/page.tsx"
)

CONTROL_PAGE = (
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
        f"Missing required FP17 file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_admin_directory_links_execution_control() -> None:
    text = read(ADMIN_PAGE)

    assert 'title: "Execution Control"' in text
    assert 'href: "/admin/execution-control"' in text
    assert 'status: "Safety control"' in text
    assert "workspaces.map" in text
    assert "href={workspace.href}" in text


def test_execution_control_page_exists() -> None:
    text = read(CONTROL_PAGE)

    assert "loadExecutionControl" in text
    assert "transitionExecutionControl" in text
    assert "activateExecutionEmergencyStop" in text


def test_page_displays_authoritative_control_state() -> None:
    page = read(
        CONTROL_PAGE
    )

    service = read(
        SERVICE
    )

    assert (
        'data-testid="execution-control-current-mode"'
        in page
    )

    assert (
        "paper_execution_enabled"
        in page
    )

    assert (
        "emergency_stop_active"
        in page
    )

    assert (
        "live_execution_enabled"
        in service
    )

    assert (
        "Live broker execution is not enabled"
        in page
    )


def test_page_supports_selectable_modes() -> None:
    text = read(CONTROL_PAGE)

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


def test_emergency_stop_is_dedicated() -> None:
    text = read(CONTROL_PAGE)

    assert (
        'data-testid="execution-control-emergency-button"'
        in text
    )

    assert '"EMERGENCY STOP"' in text

    assert (
        "activateExecutionEmergencyStop"
        in text
    )


def test_live_execution_cannot_be_selected() -> None:
    page = read(CONTROL_PAGE)
    service = read(SERVICE)

    assert (
        "Live broker execution is not enabled"
        in page
    )

    selectable = service[
        service.index(
            "SELECTABLE_EXECUTION_MODES"
        ):
        service.index(
            "function isOperatingMode"
        )
    ]

    assert "EMERGENCY_STOP" not in selectable
    assert '"LIVE"' not in selectable


def test_status_proxy_targets_backend() -> None:
    text = read(STATUS_PROXY)

    assert "backendFetch" in text

    assert (
        '"/api/v1/admin/execution-control"'
        in text
    )

    assert 'method: "GET"' in text


def test_transition_proxy_is_restricted() -> None:
    text = read(TRANSITION_PROXY)

    selectable = text[
        text.index(
            "const ALLOWED_MODES"
        ):
        text.index(
            "function errorResponse"
        )
    ]

    assert "SAFE" in selectable
    assert "SIMULATION" in selectable
    assert "LOCKED" in selectable
    assert "EMERGENCY_STOP" not in selectable

    assert (
        '"/api/v1/admin/execution-control/transition"'
        in text
    )


def test_emergency_proxy_uses_dedicated_route() -> None:
    text = read(EMERGENCY_PROXY)

    assert "backendFetch" in text

    assert (
        '"/api/v1/admin/execution-control/emergency-stop"'
        in text
    )

    assert 'method: "POST"' in text
