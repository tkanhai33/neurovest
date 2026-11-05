from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]

ROUTER = (
    ROOT
    / "backend/app/stacks/identity_auth/admin_read_router.py"
)

PROXY = (
    ROOT
    / "frontend/app/api/v1/admin/audit/route.ts"
)

FRONTEND = (
    ROOT
    / "frontend/app/admin/audit/page.tsx"
)


def read(path: Path) -> str:
    assert path.exists(), f"Missing required file: {path}"

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def test_admin_router_contains_audit_endpoint() -> None:
    text = read(ROUTER)

    assert '"/audit"' in text
    assert "list_administrative_audit_records" in text


def test_router_uses_read_only_decision_audit_facade() -> None:
    text = read(ROUTER)

    assert "DecisionAuditQueryFacade" in text
    assert "build_decision_audit_service" in text
    assert "list_recent" in text
    assert '"mutations_enabled": False' in text


def test_router_requires_administrative_principal() -> None:
    text = read(ROUTER)

    route_start = text.index(
        "async def list_administrative_audit_records"
    )

    route_text = text[
        route_start:
        route_start + 1500
    ]

    assert "require_administrative_principal" in route_text


def test_frontend_proxy_uses_authenticated_backend_fetch() -> None:
    text = read(PROXY)

    assert "backendFetch" in text
    assert "/api/v1/admin/audit" in text
    assert 'method: "GET"' in text


def test_frontend_page_requests_admin_audit_api() -> None:
    text = read(FRONTEND)

    assert '"/api/v1/admin/audit?limit=100"' in text
    assert "fetch(" in text
    assert 'credentials: "include"' in text


def test_frontend_page_displays_returned_records() -> None:
    text = read(FRONTEND)

    assert 'data-testid="admin-audit-records"' in text
    assert "records.map" in text
    assert "Immutable boundary" in text
