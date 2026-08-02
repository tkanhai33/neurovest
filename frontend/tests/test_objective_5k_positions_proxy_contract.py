from pathlib import Path


ROUTE = Path(
    "frontend/app/api/v1/portfolio/positions/route.ts"
)

SERVICE = Path(
    "frontend/services/portfolioService.ts"
)

BACKEND = Path(
    "backend/app/main.py"
)


def test_portfolio_service_uses_portfolio_positions_proxy() -> None:
    source = SERVICE.read_text(
        encoding="utf-8",
    )

    assert (
        '"/api/v1/portfolio/positions"'
        in source
    )


def test_proxy_calls_owner_scoped_database_positions() -> None:
    source = ROUTE.read_text(
        encoding="utf-8",
    )

    assert (
        '"/api/v1/positions"'
        in source
    )

    assert (
        '"/api/v1/portfolio/readonly/positions"'
        not in source
    )


def test_proxy_accepts_real_backend_position_shape() -> None:
    source = ROUTE.read_text(
        encoding="utf-8",
    )

    assert "active_exposure_count" in source
    assert "Array.isArray(value.positions)" in source
    assert "isBackendPositionsResponse(payload)" in source


def test_proxy_returns_valid_payload_without_empty_substitution() -> None:
    source = ROUTE.read_text(
        encoding="utf-8",
    )

    assert (
        "NextResponse.json(\n"
        "      payload,"
        in source
    )

    assert "controlledEmpty" not in source
    assert "portfolio_unavailable" not in source
    assert '"positions": []' not in source
    assert "positions: []" not in source


def test_backend_positions_are_filtered_by_principal() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert '@app.get("/api/v1/positions")' in source

    assert (
        "PortfolioInventory.user_id"
        in source
    )

    assert "principal.subject" in source


def test_proxy_preserves_authentication_statuses() -> None:
    source = ROUTE.read_text(
        encoding="utf-8",
    )

    assert "response.status === 401" in source
    assert "response.status === 403" in source
