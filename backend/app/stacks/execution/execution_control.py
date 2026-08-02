from __future__ import annotations

import json
import os
from dataclasses import (
    asdict,
    dataclass,
)
from datetime import (
    UTC,
    datetime,
)
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any


class OperatingMode(
    str,
    Enum,
):
    SAFE = "SAFE"
    SIMULATION = "SIMULATION"
    LOCKED = "LOCKED"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class ExecutionControlError(
    RuntimeError
):
    pass


class InvalidOperatingModeTransition(
    ExecutionControlError
):
    pass


class ExecutionBlockedError(
    ExecutionControlError
):
    pass


def utc_now() -> datetime:
    return datetime.now(
        UTC
    )


def default_state_path() -> Path:
    configured = os.getenv(
        "NEUROVEST_EXECUTION_CONTROL_STATE_PATH",
        "",
    ).strip()

    if configured:
        return Path(
            configured
        )

    return Path(
        "runtime/execution_control/"
        "operating_mode.json"
    )


@dataclass(
    frozen=True,
)
class ExecutionControlSnapshot:
    mode: str
    revision: int
    updated_at: str
    reason: str
    actor: str
    paper_execution_enabled: bool
    live_execution_enabled: bool
    emergency_stop_active: bool


_ALLOWED_TRANSITIONS: dict[
    OperatingMode,
    frozenset[OperatingMode],
] = {
    OperatingMode.SAFE: frozenset(
        {
            OperatingMode.SIMULATION,
            OperatingMode.LOCKED,
            OperatingMode.EMERGENCY_STOP,
        }
    ),
    OperatingMode.SIMULATION: frozenset(
        {
            OperatingMode.SAFE,
            OperatingMode.LOCKED,
            OperatingMode.EMERGENCY_STOP,
        }
    ),
    OperatingMode.LOCKED: frozenset(
        {
            OperatingMode.SAFE,
            OperatingMode.EMERGENCY_STOP,
        }
    ),
    OperatingMode.EMERGENCY_STOP: frozenset(
        {
            OperatingMode.LOCKED,
        }
    ),
}


class ExecutionControl:
    """
    Central fail-closed execution-mode authority.

    SAFE:
        Read-only operation. No paper or live execution.

    SIMULATION:
        Paper execution only. Live broker execution remains disabled.

    LOCKED:
        No execution. Used for administrative lockout and recovery.

    EMERGENCY_STOP:
        Immediate execution denial. Recovery must first transition to
        LOCKED before any other mode can be selected.
    """

    def __init__(
        self,
        *,
        state_path: Path | None = None,
    ) -> None:
        self._state_path = (
            state_path
            or default_state_path()
        )

        self._lock = RLock()

        self._mode = (
            OperatingMode.SAFE
        )

        self._revision = 0
        self._updated_at = (
            utc_now()
        )

        self._reason = (
            "Fail-closed startup default"
        )

        self._actor = "system"

        self._load_state()

    @property
    def mode(
        self,
    ) -> OperatingMode:
        with self._lock:
            return self._mode

    def snapshot(
        self,
    ) -> ExecutionControlSnapshot:
        with self._lock:
            mode = self._mode

            return ExecutionControlSnapshot(
                mode=mode.value,
                revision=self._revision,
                updated_at=(
                    self._updated_at.isoformat()
                ),
                reason=self._reason,
                actor=self._actor,
                paper_execution_enabled=(
                    mode
                    is OperatingMode.SIMULATION
                ),
                live_execution_enabled=False,
                emergency_stop_active=(
                    mode
                    is OperatingMode.EMERGENCY_STOP
                ),
            )

    def snapshot_dict(
        self,
    ) -> dict[str, Any]:
        return asdict(
            self.snapshot()
        )

    def transition(
        self,
        target: OperatingMode | str,
        *,
        actor: str,
        reason: str,
    ) -> ExecutionControlSnapshot:
        normalized_target = (
            target
            if isinstance(
                target,
                OperatingMode,
            )
            else OperatingMode(
                str(target)
                .strip()
                .upper()
            )
        )

        normalized_actor = str(
            actor
        ).strip()

        normalized_reason = str(
            reason
        ).strip()

        if not normalized_actor:
            raise InvalidOperatingModeTransition(
                "Operating-mode transition actor is required"
            )

        if not normalized_reason:
            raise InvalidOperatingModeTransition(
                "Operating-mode transition reason is required"
            )

        with self._lock:
            current = self._mode

            if normalized_target is current:
                return self.snapshot()

            allowed = (
                _ALLOWED_TRANSITIONS[
                    current
                ]
            )

            if normalized_target not in allowed:
                raise InvalidOperatingModeTransition(
                    "Operating-mode transition "
                    f"{current.value} -> "
                    f"{normalized_target.value} "
                    "is not permitted"
                )

            previous = (
                self._mode,
                self._revision,
                self._updated_at,
                self._reason,
                self._actor,
            )

            self._mode = (
                normalized_target
            )

            self._revision += 1
            self._updated_at = (
                utc_now()
            )

            self._reason = (
                normalized_reason
            )

            self._actor = (
                normalized_actor
            )

            try:
                self._persist_state()

            except Exception:
                (
                    self._mode,
                    self._revision,
                    self._updated_at,
                    self._reason,
                    self._actor,
                ) = previous

                raise

            return self.snapshot()

    def emergency_stop(
        self,
        *,
        actor: str,
        reason: str,
    ) -> ExecutionControlSnapshot:
        with self._lock:
            if (
                self._mode
                is OperatingMode.EMERGENCY_STOP
            ):
                return self.snapshot()

        return self.transition(
            OperatingMode.EMERGENCY_STOP,
            actor=actor,
            reason=reason,
        )

    def assert_paper_execution_allowed(
        self,
    ) -> None:
        snapshot = self.snapshot()

        if not (
            snapshot.mode
            == OperatingMode.SIMULATION.value
            and snapshot.paper_execution_enabled
            and not snapshot.live_execution_enabled
            and not snapshot.emergency_stop_active
        ):
            raise ExecutionBlockedError(
                "Paper execution is blocked while "
                f"NeuroVest is in {snapshot.mode} mode"
            )

    def assert_live_execution_allowed(
        self,
    ) -> None:
        raise ExecutionBlockedError(
            "Live broker execution is not enabled"
        )

    def _load_state(
        self,
    ) -> None:
        with self._lock:
            if not self._state_path.exists():
                self._persist_state()
                return

            try:
                payload = json.loads(
                    self._state_path.read_text(
                        encoding="utf-8",
                    )
                )

                mode = OperatingMode(
                    str(
                        payload.get(
                            "mode",
                            "",
                        )
                    )
                    .strip()
                    .upper()
                )

                revision = int(
                    payload.get(
                        "revision",
                        0,
                    )
                )

                updated_at = (
                    datetime.fromisoformat(
                        str(
                            payload.get(
                                "updated_at",
                                "",
                            )
                        )
                    )
                )

                reason = str(
                    payload.get(
                        "reason",
                        "",
                    )
                ).strip()

                actor = str(
                    payload.get(
                        "actor",
                        "",
                    )
                ).strip()

                if (
                    revision < 0
                    or not reason
                    or not actor
                ):
                    raise ValueError(
                        "Persisted execution-control state is invalid"
                    )

                self._mode = mode
                self._revision = revision
                self._updated_at = updated_at
                self._reason = reason
                self._actor = actor

            except Exception:
                self._mode = (
                    OperatingMode.LOCKED
                )

                self._revision = 0
                self._updated_at = (
                    utc_now()
                )

                self._reason = (
                    "Invalid persisted state; "
                    "runtime locked fail closed"
                )

                self._actor = "system"

                self._persist_state()

    def _persist_state(
        self,
    ) -> None:
        self._state_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = (
            self._state_path.with_suffix(
                self._state_path.suffix
                + ".tmp"
            )
        )

        payload = {
            "mode": self._mode.value,
            "revision": self._revision,
            "updated_at": (
                self._updated_at.isoformat()
            ),
            "reason": self._reason,
            "actor": self._actor,
            "paper_execution_enabled": (
                self._mode
                is OperatingMode.SIMULATION
            ),
            "live_execution_enabled": False,
            "emergency_stop_active": (
                self._mode
                is OperatingMode.EMERGENCY_STOP
            ),
        }

        temporary.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

        temporary.replace(
            self._state_path
        )


execution_control = ExecutionControl()
