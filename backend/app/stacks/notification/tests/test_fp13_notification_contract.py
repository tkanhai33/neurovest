from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]

MODEL = (
    ROOT
    / "backend/app/stacks/notification/models.py"
)

SERVICE = (
    ROOT
    / "backend/app/stacks/notification/service.py"
)

ROUTER = (
    ROOT
    / "backend/app/stacks/notification/api_router.py"
)

MAIN = ROOT / "backend/app/main.py"

REGISTRY = (
    ROOT
    / "backend/app/stacks/db_runtime/model_registry.py"
)


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_notification_model_has_delivery_and_read_state() -> None:
    text = read(MODEL)

    assert "delivery_status" in text
    assert "delivered_at" in text
    assert "is_read" in text
    assert "read_at" in text
    assert "acknowledged_at" in text
    assert "user_id" in text


def test_notification_service_supports_full_lifecycle() -> None:
    text = read(SERVICE)

    assert "emit_notification" in text
    assert "list_notifications" in text
    assert "mark_read" in text
    assert "acknowledge_notification" in text


def test_notification_routes_are_decorated() -> None:
    text = read(ROUTER)

    assert '@router.get("")' in text
    assert '@router.post(' in text
    assert '"/{notification_id}/read"' in text
    assert '"/{notification_id}/acknowledge"' in text


def test_notification_routes_require_authentication() -> None:
    text = read(ROUTER)

    assert "require_authenticated_principal" in text
    assert "principal_subject" in text


def test_notification_route_is_mounted() -> None:
    text = read(MAIN)

    assert "notification_router" in text
    assert "app.include_router(" in text


def test_notification_model_is_registered() -> None:
    text = read(REGISTRY)

    assert "notification_models" in text
