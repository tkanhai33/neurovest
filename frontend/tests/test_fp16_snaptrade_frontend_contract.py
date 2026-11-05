from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

STATUS_PROXY = (
    ROOT
    / "frontend/app/api/v1/snaptrade/status/route.ts"
)

REGISTER_PROXY = (
    ROOT
    / "frontend/app/api/v1/snaptrade/register/route.ts"
)

PORTAL_PROXY = (
    ROOT
    / "frontend/app/api/v1/snaptrade/"
    "connection-portal/route.ts"
)

SYNC_PROXY = (
    ROOT
    / "frontend/app/api/v1/snaptrade/"
    "synchronize/route.ts"
)

PAGE = (
    ROOT
    / "frontend/app/user/brokerage/page.tsx"
)

BACKEND_ROUTER = (
    ROOT
    / "backend/app/stacks/snaptrade/api_router.py"
)

BACKEND_SERVICE = (
    ROOT
    / "backend/app/stacks/snaptrade/application/"
    "connection_service.py"
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
    assert '"/api/v1/snaptrade/status"' in text
    assert 'method: "GET"' in text


def test_registration_proxy_uses_authenticated_backend_fetch() -> None:
    text = read(
        REGISTER_PROXY
    )

    assert "backendFetch" in text
    assert '"/api/v1/snaptrade/register"' in text
    assert 'method: "POST"' in text


def test_portal_proxy_uses_authenticated_backend_fetch() -> None:
    text = read(
        PORTAL_PROXY
    )

    assert "backendFetch" in text

    assert (
        '"/api/v1/snaptrade/connection-portal"'
        in text
    )

    assert 'method: "POST"' in text


def test_synchronization_proxy_uses_authenticated_backend_fetch() -> None:
    text = read(
        SYNC_PROXY
    )

    assert "backendFetch" in text

    assert (
        '"/api/v1/snaptrade/synchronize"'
        in text
    )

    assert 'method: "POST"' in text


def test_frontend_page_requests_complete_snaptrade_chain() -> None:
    page = read(PAGE)
    service = read(
        ROOT / "frontend/services/snaptradeService.ts"
    )

    expected = {
        "getSnapTradeStatus": "/api/v1/snaptrade/status",
        "registerSnapTradeUser": "/api/v1/snaptrade/register",
        "createSnapTradeConnectionPortal": "/api/v1/snaptrade/connection-portal",
        "synchronizeSnapTrade": "/api/v1/snaptrade/synchronize",
    }

    assert 'from "../../../services/snaptradeService"' in page

    for function, route in expected.items():
        assert f"await {function}(" in page
        assert f"export async function {function}(" in service
        assert f'"{route}"' in service


def test_frontend_page_exposes_user_controls() -> None:
    text = read(
        PAGE
    )

    assert (
        'data-testid="snaptrade-register"'
        in text
    )

    assert (
        'data-testid="snaptrade-connect"'
        in text
    )

    assert (
        'data-testid="snaptrade-synchronize"'
        in text
    )

    assert (
        'data-testid="snaptrade-connection-status"'
        in text
    )


def test_frontend_explicitly_enforces_read_only_presentation() -> None:
    text = read(
        PAGE
    )

    assert "Read only" in text
    assert "Trading" in text
    assert "Disabled" in text
    assert "Live broker orders" in text
    assert "Blocked" in text

    forbidden = (
        "placeOrder",
        "submitOrder",
        "executeTrade",
        "/orders",
        "/trading",
        "enable-live",
    )

    for marker in forbidden:
        assert marker not in text


def test_backend_routes_exist_for_frontend_contract() -> None:
    text = read(
        BACKEND_ROUTER
    )

    assert '"/status"' in text
    assert '"/register"' in text
    assert '"/connection-portal"' in text
    assert '"/synchronize"' in text


def test_backend_service_remains_read_only() -> None:
    text = read(
        BACKEND_SERVICE
    )

    assert '"read"' in text
    assert "trading_enabled" in text
    assert "False" in text

    assert "trade-if-available" not in text
