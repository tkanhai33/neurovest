from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

BACKEND_MODEL = (
    ROOT
    / "backend/app/stacks/notification/models.py"
)

BACKEND_SERVICE = (
    ROOT
    / "backend/app/stacks/notification/service.py"
)

BACKEND_ROUTER = (
    ROOT
    / "backend/app/stacks/notification/api_router.py"
)

BACKEND_MAIN = (
    ROOT
    / "backend/app/main.py"
)

LIST_PROXY = (
    ROOT
    / "frontend/app/api/v1/notifications/route.ts"
)

ACTION_PROXY = (
    ROOT
    / "frontend/app/api/v1/notifications/"
    "[notification_id]/[action]/route.ts"
)

SETTINGS_PAGE = (
    ROOT
    / "frontend/app/user/settings/page.tsx"
)


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_backend_exposes_notification_routes() -> None:
    text = read(
        BACKEND_ROUTER
    )

    assert (
        'prefix="/api/v1/notifications"'
        in text
    )

    assert '@router.get("")' in text
    assert "@router.post(" in text
    assert '"/{notification_id}/read"' in text
    assert (
        '"/{notification_id}/acknowledge"'
        in text
    )


def test_backend_has_creation_and_delivery_evidence() -> None:
    model = read(
        BACKEND_MODEL
    )

    service = read(
        BACKEND_SERVICE
    )

    router = read(
        BACKEND_ROUTER
    )

    assert "emit_notification" in service
    assert "delivery_status" in model
    assert "delivered_at" in model
    assert "delivery_evidence" in router


def test_backend_has_read_and_acknowledgement_behavior() -> None:
    model = read(
        BACKEND_MODEL
    )

    service = read(
        BACKEND_SERVICE
    )

    assert "list_notifications" in service
    assert "mark_read" in service
    assert (
        "acknowledge_notification"
        in service
    )
    assert "is_read" in model
    assert "read_at" in model
    assert "acknowledged_at" in model


def test_notification_router_is_mounted() -> None:
    text = read(
        BACKEND_MAIN
    )

    assert "notification_router" in text
    assert (
        "app.include_router(notification_router)"
        in text
    )


def test_frontend_list_proxy_uses_authenticated_backend_fetch() -> None:
    text = read(
        LIST_PROXY
    )

    assert "backendFetch" in text
    assert (
        "/api/v1/notifications"
        in text
    )
    assert 'method: "GET"' in text
    assert 'method: "POST"' in text


def test_frontend_action_proxy_forwards_read_and_acknowledge() -> None:
    text = read(
        ACTION_PROXY
    )

    assert "backendFetch" in text
    assert 'action !== "read"' in text
    assert (
        'action !== "acknowledge"'
        in text
    )
    assert 'method: "PATCH"' in text


def test_settings_page_requests_and_displays_notifications() -> None:
    text = read(
        SETTINGS_PAGE
    )

    assert (
        '"/api/v1/notifications?limit=100"'
        in text
    )
    assert "fetch(" in text
    assert (
        'data-testid="notification-records"'
        in text
    )
    assert "notifications.map" in text


def test_settings_page_performs_read_and_acknowledge_actions() -> None:
    text = read(
        SETTINGS_PAGE
    )

    assert '"read"' in text
    assert '"acknowledge"' in text
    assert 'method: "PATCH"' in text
    assert "Mark read" in text
    assert "Acknowledge" in text
