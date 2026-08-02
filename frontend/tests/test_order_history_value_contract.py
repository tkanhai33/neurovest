from pathlib import Path


BACKEND = Path("backend/app/main.py")
DASHBOARD = Path(
    "frontend/app/user/dashboard/page.tsx"
)
ACTIVITY = Path(
    "frontend/app/user/components/"
    "RecentOrderActivity.tsx"
)


def test_orders_endpoint_exposes_execution_values() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    required = {
        '"allocated_capital"',
        '"slippage_price"',
        '"commission_paid"',
        '"shares_quantity"',
        "float(o.allocated_capital)",
        "float(o.slippage_price)",
    }

    missing = sorted(
        value
        for value in required
        if value not in source
    )

    assert not missing, missing


def test_quantity_is_derived_without_schema_migration() -> None:
    source = BACKEND.read_text(
        encoding="utf-8",
    )

    assert (
        "float(o.allocated_capital)"
        in source
    )

    assert (
        "/ float(o.slippage_price)"
        in source
    )

    assert (
        "float(o.slippage_price) != 0.0"
        in source
    )


def test_dashboard_order_contract_accepts_values() -> None:
    source = DASHBOARD.read_text(
        encoding="utf-8",
    )

    for field in (
        "shares_quantity?: number | null",
        "allocated_capital?: number | null",
        "slippage_price?: number | null",
        "commission_paid?: number | null",
    ):
        assert field in source


def test_recent_activity_reads_execution_values() -> None:
    source = ACTIVITY.read_text(
        encoding="utf-8",
    )

    for field in (
        '"shares_quantity"',
        '"slippage_price"',
        '"allocated_capital"',
        '"commission_paid"',
    ):
        assert field in source
