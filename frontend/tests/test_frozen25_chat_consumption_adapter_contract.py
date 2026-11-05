from pathlib import Path
import re


ROOT = Path(
    __file__
).resolve().parents[2]


TARGET = (
    ROOT
    /
    "frontend/app/api/v1/chat/frozen25/route.ts"
)


def source() -> str:
    return TARGET.read_text(
        encoding="utf-8"
    )


def test_frozen25_chat_adapter_exists():
    assert TARGET.is_file()


def test_adapter_uses_existing_backend_auth_helper():
    text = source()

    assert (
        'import { backendFetch } '
        'from "../../../../../lib/backendAuth";'
        in text
    )

    assert "backendFetch(" in text


def test_adapter_targets_only_persisted_frozen25_endpoint():
    text = source()

    target = (
        "/api/v1/strategy/"
        "model-inference/frozen25"
    )

    assert target in text

    api_paths = re.findall(
        r'["\'](/api/[^"\']+)["\']',
        text,
    )

    assert api_paths == [
        target
    ]


def test_adapter_is_post_only():
    text = source()

    assert (
        "export async function POST"
        in text
    )

    for method in (
        "GET",
        "PUT",
        "PATCH",
        "DELETE",
    ):
        assert (
            f"export async function {method}"
            not in text
        )


def test_adapter_preserves_authenticated_backend_fetch_boundary():
    text = source()

    assert (
        "await backendFetch("
        in text
    )

    assert (
        'method: "POST"'
        in text
    )

    assert (
        '"Content-Type": "application/json"'
        in text
    )

    assert (
        "JSON.stringify(payload)"
        in text
    )


def test_adapter_preserves_backend_status():
    text = source()

    assert (
        "status: response.status"
        in text
    )


def test_adapter_is_no_store():
    text = source()

    assert (
        'cache: "no-store"'
        in text
    )

    assert (
        '"Cache-Control": "no-store"'
        in text
    )


def test_adapter_contains_no_execution_or_broker_integration():
    text = source().lower()

    prohibited = (
        "snaptrade",
        "paper_execution",
        "broker_execution",
        "live_execution",
        "place_order",
        "submit_order",
        "execute_order",
        "runtime_activation_enabled",
        "training_mode=true",
    )

    for token in prohibited:
        assert token not in text


def test_adapter_does_not_import_model_or_database():
    text = source().lower()

    prohibited = (
        "joblib",
        "sqlalchemy",
        "async_session",
        "identityuserrepository",
        "frozen25read-onlyinferenceservice",
        "frozen25readonlyinferenceservice",
    )

    for token in prohibited:
        assert token not in text


def test_existing_chat_route_not_replaced():
    chat_route = (
        ROOT
        /
        "frontend/app/api/v1/chat/route.ts"
    )

    assert chat_route.is_file()

    text = chat_route.read_text(
        encoding="utf-8"
    )

    assert (
        '"/api/v1/chat"'
        in text
    )
