from __future__ import annotations

import json
import fcntl
import threading
from contextlib import contextmanager
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

        with self._interprocess_lock():
            self._load_state()

    @property
    def mode(
        self,
    ) -> OperatingMode:
        return OperatingMode(self.snapshot().mode)

    @contextmanager
    def _interprocess_lock(self):
        lock_path = self._state_path.with_name(
            self._state_path.name + ".lock"
        )
        lock_path.parent.mkdir(parents=True, exist_ok=True)

        with lock_path.open("a+b") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def snapshot(self) -> ExecutionControlSnapshot:
        try:
            with self._lock, self._interprocess_lock():
                self._load_state()
                return self._snapshot_unlocked()
        except ExecutionControlError:
            raise
        except Exception as exc:
            raise ExecutionBlockedError(
                "Execution-control state cannot be verified"
            ) from exc

    def _snapshot_unlocked(
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

        with self._lock, self._interprocess_lock():
            self._load_state()
            if normalized_target is not OperatingMode.EMERGENCY_STOP:
                self._assert_pending_stop_absent()
            current = self._mode

            if normalized_target is current:
                return self._snapshot_unlocked()

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
                try:
                    self._load_state()
                except Exception:
                    self._mode = OperatingMode.LOCKED
                    self._revision = previous[1]
                    self._updated_at = utc_now()
                    self._reason = (
                        'Persistence reconciliation failed; '
                        'runtime locked fail closed'
                    )
                    self._actor = 'system'
                raise

            return self._snapshot_unlocked()

    def emergency_stop(
        self,
        *,
        actor: str,
        reason: str,
    ) -> ExecutionControlSnapshot:
        return self.transition(
            OperatingMode.EMERGENCY_STOP,
            actor=actor,
            reason=reason,
        )

    def _assert_pending_stop_absent(self) -> None:
        from backend.app.stacks.execution.emergency_commit_barrier import (
            CommitBarrierBlocked,
            assert_no_pending_stop,
        )

        try:
            assert_no_pending_stop(self._state_path)
        except CommitBarrierBlocked as exc:
            raise ExecutionBlockedError(
                'Emergency-stop intent blocks execution'
            ) from exc

    def assert_paper_execution_allowed(
        self,
    ) -> None:
        self._assert_pending_stop_absent()
        snapshot = self.snapshot()
        self._assert_pending_stop_absent()

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
        import tempfile

        parent = self._state_path.parent
        parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "mode": self._mode.value,
            "revision": self._revision,
            "updated_at": self._updated_at.isoformat(),
            "reason": self._reason,
            "actor": self._actor,
            "paper_execution_enabled": (
                self._mode is OperatingMode.SIMULATION
            ),
            "live_execution_enabled": False,
            "emergency_stop_active": (
                self._mode is OperatingMode.EMERGENCY_STOP
            ),
        }

        temporary = None

        try:
            fd, filename = tempfile.mkstemp(
                prefix=".operating-mode-",
                suffix=".tmp",
                dir=parent,
            )
            temporary = Path(filename)

            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                os.fchmod(stream.fileno(), 0o600)
                json.dump(
                    payload,
                    stream,
                    indent=2,
                    sort_keys=True,
                )
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())

            os.replace(temporary, self._state_path)
            temporary = None

            directory_fd = os.open(
                parent,
                os.O_RDONLY | os.O_DIRECTORY,
            )

            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)

        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


execution_control = ExecutionControl()
