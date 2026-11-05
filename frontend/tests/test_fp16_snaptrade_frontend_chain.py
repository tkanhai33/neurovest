import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SERVICE = (
    ROOT
    / "frontend/services/snaptradeService.ts"
)

PAGE = (
    ROOT
    / "frontend/app/user/brokerage/page.tsx"
)

STATUS_ROUTE = (
    ROOT
    / "frontend/app/api/v1/snaptrade/status/route.ts"
)

REGISTER_ROUTE = (
    ROOT
    / "frontend/app/api/v1/snaptrade/register/route.ts"
)

PORTAL_ROUTE = (
    ROOT
    / "frontend/app/api/v1/snaptrade/connection-portal/route.ts"
)

SYNC_ROUTE = (
    ROOT
    / "frontend/app/api/v1/snaptrade/synchronize/route.ts"
)


def read(path: Path) -> str:
    assert path.exists(), (
        f"Missing required frontend file: {path}"
    )

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_frontend_service_calls_all_snaptrade_routes() -> None:
    text = read(SERVICE)

    assert '"/api/v1/snaptrade/status"' in text
    assert '"/api/v1/snaptrade/register"' in text

    assert (
        '"/api/v1/snaptrade/connection-portal"'
        in text
    )

    assert (
        '"/api/v1/snaptrade/synchronize"'
        in text
    )

    assert re.search(r'credentials\s*:\s*"include"', text)


def test_next_proxies_use_authenticated_backend_fetch() -> None:
    contracts = {
        STATUS_ROUTE: (
            "/api/v1/snaptrade/status",
            "GET",
        ),
        REGISTER_ROUTE: (
            "/api/v1/snaptrade/register",
            "POST",
        ),
        PORTAL_ROUTE: (
            "/api/v1/snaptrade/connection-portal",
            "POST",
        ),
        SYNC_ROUTE: (
            "/api/v1/snaptrade/synchronize",
            "POST",
        ),
    }

    for path, (
        endpoint,
        method,
    ) in contracts.items():
        text = read(path)

        assert "backendFetch" in text
        assert endpoint in text

        assert (
            f"export async function {method}"
            in text
        )


def test_brokerage_page_uses_authenticated_snaptrade_chain() -> None:
    page = read(PAGE)
    service = read(
        ROOT / "frontend/services/snaptradeService.ts"
    )

    assert 'from "../../../services/snaptradeService"' in page

    expected = {
        "getSnapTradeStatus": ("/api/v1/snaptrade/status", "GET"),
        "registerSnapTradeUser": ("/api/v1/snaptrade/register", "POST"),
        "createSnapTradeConnectionPortal": (
            "/api/v1/snaptrade/connection-portal", "POST"
        ),
        "synchronizeSnapTrade": (
            "/api/v1/snaptrade/synchronize", "POST"
        ),
    }

    for function, (route, method) in expected.items():
        assert f"await {function}(" in page

        marker = f"export async function {function}("
        start = service.find(marker)
        assert start >= 0

        next_export = service.find(
            "export ",
            start + len(marker),
        )

        body = (
            service[start:next_export]
            if next_export >= 0
            else service[start:]
        )

        assert f'"{route}"' in body
        assert f'"{method}"' in body
        assert '"include"' in body
        assert '"no-store"' in body
        assert "fetch(" in body


def test_frontend_explicitly_displays_no_trading_boundary() -> None:
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

    lowered_page = page.lower()
    lowered_combined = combined.lower()

    assert (
        "blocked" in lowered_page
        or "disabled" in lowered_page
        or "read-only" in lowered_page
        or "read only" in lowered_page
    )

    assert (
        "trading_enabled"
        in combined
    )

    assert (
        "read-only"
        in lowered_combined
        or "read_only"
        in combined
        or "read only"
        in lowered_combined
    )

    forbidden_routes = (
        "/api/v1/snaptrade/orders",
        "/api/v1/snaptrade/trade",
        "/api/v1/snaptrade/trading",
        "/api/v1/snaptrade/execute",
    )

    for route in forbidden_routes:
        assert (
            route not in combined
        )


def test_frontend_exposes_no_order_execution_request() -> None:
    combined = "\n".join(
        read(path)
        for path in (
            SERVICE,
            PAGE,
            STATUS_ROUTE,
            REGISTER_ROUTE,
            PORTAL_ROUTE,
            SYNC_ROUTE,
        )
    ).lower()

    forbidden_paths = (
        "/api/v1/snaptrade/orders",
        "/api/v1/snaptrade/trade",
        "/api/v1/snaptrade/execute",
    )

    for forbidden in forbidden_paths:
        assert forbidden not in combined
