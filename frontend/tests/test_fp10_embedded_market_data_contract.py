from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]

DASHBOARD_FILES = [
    ROOT / "frontend/app/dashboard/page.tsx",
    ROOT / "frontend/app/user/dashboard/page.tsx",
]

BACKEND_FILES = [
    ROOT / "backend/app/main.py",
    ROOT / "backend/app/stacks/market_data/api_router.py",
    ROOT / "backend/app/stacks/market_data/market_data_service.py",
]


def combined_source(paths: list[Path]) -> str:
    existing = [
        path
        for path in paths
        if path.exists()
    ]

    assert existing, "No required source files were found."

    return "\n".join(
        path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        for path in existing
    )


def test_dashboard_contains_market_or_price_surface() -> None:
    text = combined_source(DASHBOARD_FILES)

    assert re.search(
        r"\b(?:market data|live price|quote|ticker|symbol|price)\b",
        text,
        re.IGNORECASE,
    )


def test_backend_contains_market_data_provider_or_service() -> None:
    text = combined_source(BACKEND_FILES)

    assert re.search(
        r"\b(?:market_data|market data|provider|get_live_market_price|yfinance)\b",
        text,
        re.IGNORECASE,
    )


def test_dashboard_contains_market_data_consumption_context() -> None:
    text = combined_source(DASHBOARD_FILES)

    assert re.search(
        r"\b(?:dashboard|watchlist|portfolio|position|summary)\b",
        text,
        re.IGNORECASE,
    )
