from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from backend.app.stacks.snaptrade.application.automatic_sync_scheduler import (
    _market_window_open,
    _owner_due,
    automatic_sync_enabled,
)


def test_market_window_accepts_weekday_market_time():

    now = datetime(
        2026,
        9,
        22,
        10,
        0,
        tzinfo=ZoneInfo(
            "America/Toronto"
        ),
    )

    assert _market_window_open(
        now
    ) is True


def test_market_window_rejects_weekend_and_closed_time():

    weekend = datetime(
        2026,
        9,
        20,
        10,
        0,
        tzinfo=ZoneInfo(
            "America/Toronto"
        ),
    )

    before_open = datetime(
        2026,
        9,
        22,
        9,
        0,
        tzinfo=ZoneInfo(
            "America/Toronto"
        ),
    )

    assert _market_window_open(
        weekend
    ) is False

    assert _market_window_open(
        before_open
    ) is False


def test_owner_due_requires_two_hour_cooldown():

    now = datetime(
        2026,
        9,
        22,
        16,
        0,
        tzinfo=UTC,
    )

    assert _owner_due(
        last_synced_at=None,
        now=now,
    ) is True

    assert _owner_due(
        last_synced_at=(
            now
            -
            timedelta(
                hours=1,
                minutes=59,
            )
        ),
        now=now,
    ) is False

    assert _owner_due(
        last_synced_at=(
            now
            -
            timedelta(
                hours=2,
            )
        ),
        now=now,
    ) is True


def test_automatic_sync_is_opt_in(
    monkeypatch,
):

    monkeypatch.delenv(
        "SNAPTRADE_AUTOMATIC_SYNC_ENABLED",
        raising=False,
    )

    assert automatic_sync_enabled() is False

    monkeypatch.setenv(
        "SNAPTRADE_AUTOMATIC_SYNC_ENABLED",
        "true",
    )

    assert automatic_sync_enabled() is True
