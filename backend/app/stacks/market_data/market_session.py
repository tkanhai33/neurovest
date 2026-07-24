"""
Deterministic North American equity-market session classification.

This service performs timezone-aware weekday and clock classification.
Exchange-holiday calendar integration is intentionally deferred to a
later provider/session integration stage.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

from backend.app.stacks.market_data.dto import (
    MarketSessionState,
)


NEW_YORK = ZoneInfo(
    "America/New_York"
)


@dataclass(
    frozen=True,
    slots=True,
)
class MarketSessionSnapshot:
    state: MarketSessionState
    observed_at: datetime
    exchange_time: datetime
    exchange_timezone: str
    regular_open: time
    regular_close: time
    holiday_calendar_applied: bool


class MarketSessionService:
    """
    Classify US and Canadian equity-style sessions using New York time.

    Holiday awareness is explicitly false until an exchange calendar is
    added and verified.
    """

    PRE_MARKET_OPEN = time(
        hour=4,
        minute=0,
    )

    REGULAR_OPEN = time(
        hour=9,
        minute=30,
    )

    REGULAR_CLOSE = time(
        hour=16,
        minute=0,
    )

    AFTER_HOURS_CLOSE = time(
        hour=20,
        minute=0,
    )

    def state_at(
        self,
        observed_at: datetime,
    ) -> MarketSessionState:
        return self.snapshot_at(
            observed_at
        ).state

    def snapshot_at(
        self,
        observed_at: datetime,
    ) -> MarketSessionSnapshot:
        if observed_at.tzinfo is None:
            raise ValueError(
                "observed_at must be timezone-aware"
            )

        normalized = (
            observed_at.astimezone(
                UTC
            )
        )

        exchange_time = (
            normalized.astimezone(
                NEW_YORK
            )
        )

        current_time = (
            exchange_time.time()
            .replace(
                tzinfo=None
            )
        )

        if exchange_time.weekday() >= 5:
            state = (
                MarketSessionState.CLOSED
            )

        elif (
            self.PRE_MARKET_OPEN
            <= current_time
            < self.REGULAR_OPEN
        ):
            state = (
                MarketSessionState.PRE_MARKET
            )

        elif (
            self.REGULAR_OPEN
            <= current_time
            < self.REGULAR_CLOSE
        ):
            state = (
                MarketSessionState.OPEN
            )

        elif (
            self.REGULAR_CLOSE
            <= current_time
            < self.AFTER_HOURS_CLOSE
        ):
            state = (
                MarketSessionState.AFTER_HOURS
            )

        else:
            state = (
                MarketSessionState.CLOSED
            )

        return MarketSessionSnapshot(
            state=state,
            observed_at=normalized,
            exchange_time=exchange_time,
            exchange_timezone=(
                NEW_YORK.key
            ),
            regular_open=(
                self.REGULAR_OPEN
            ),
            regular_close=(
                self.REGULAR_CLOSE
            ),
            holiday_calendar_applied=False,
        )

    def now(
        self,
    ) -> MarketSessionSnapshot:
        return self.snapshot_at(
            datetime.now(
                UTC
            )
        )


def healthcheck() -> dict[str, object]:
    snapshot = (
        MarketSessionService()
        .now()
    )

    return {
        "component": "market_session",
        "healthy": True,
        "state": snapshot.state.value,
        "holiday_calendar_applied": False,
        "network_called": False,
    }
