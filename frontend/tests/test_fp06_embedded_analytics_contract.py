from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]

DASHBOARD_FILES = [
    ROOT / "frontend/app/dashboard/page.tsx",
    ROOT / "frontend/app/user/dashboard/page.tsx",
]


def combined_dashboard_source() -> str:
    existing = [
        path
        for path in DASHBOARD_FILES
        if path.exists()
    ]

    assert existing, "No authenticated dashboard source file was found."

    return "\n".join(
        path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        for path in existing
    )


def test_dashboard_contains_analytics_or_performance_surface() -> None:
    text = combined_dashboard_source()

    assert re.search(
        r"\b(?:analytics?|performance|return|profit|loss|pnl|drawdown)\b",
        text,
        re.IGNORECASE,
    )


def test_dashboard_contains_portfolio_measurements() -> None:
    text = combined_dashboard_source()

    assert re.search(
        r"\b(?:equity|allocation|exposure|valuation|cash|position)\b",
        text,
        re.IGNORECASE,
    )


def test_dashboard_contains_metric_or_summary_presentation() -> None:
    text = combined_dashboard_source()

    assert re.search(
        r"\b(?:chart|metric|summary|stat|trend|history)\b",
        text,
        re.IGNORECASE,
    )
