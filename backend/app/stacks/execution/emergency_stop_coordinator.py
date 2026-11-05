from __future__ import annotations

import asyncio
import fcntl
import os
import stat
import time
from pathlib import Path

from backend.app.stacks.execution.emergency_commit_barrier import (
    CommitBarrierBlocked,
    _barrier_path,
    _pending_marker,
)


def publish_stop_intent(state_path: Path) -> Path:
    """Publish a durable, monotonic stop-intent marker."""
    state_path = Path(state_path)

    if not state_path.is_absolute():
        raise CommitBarrierBlocked("Absolute state path required")

    parent = state_path.parent
    info = parent.lstat()

    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) & 0o022
    ):
        raise CommitBarrierBlocked(
            "Unsafe emergency-control directory"
        )

    marker = _pending_marker(state_path)

    try:
        fd = os.open(
            marker,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
            0o600,
        )
    except FileExistsError:
        fd = None

    if fd is not None:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(b"EMERGENCY_STOP_PENDING\n")
            stream.flush()
            os.fsync(stream.fileno())

    marker_info = marker.lstat()

    if (
        not stat.S_ISREG(marker_info.st_mode)
        or marker_info.st_uid != os.getuid()
        or stat.S_IMODE(marker_info.st_mode) != 0o600
    ):
        raise CommitBarrierBlocked(
            "Unsafe emergency-stop marker"
        )

    directory_fd = os.open(
        parent, os.O_RDONLY | os.O_DIRECTORY
    )

    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)

    return marker


async def finalize_emergency_stop(
    control,
    state_path: Path,
    *,
    actor: str,
    reason: str,
    timeout_seconds: float = 10.0,
):
    """
    Offline-qualified stop finalization coordinator.

    Stop intent is published before acquiring the commit
    barrier. Existing commits may finish before stop
    acknowledgment. New barrier users reject pending intent.

    This does not establish independent OS authority.
    """
    state_path = Path(state_path)

    if not state_path.is_absolute():
        raise CommitBarrierBlocked("Absolute state path required")

    if Path(control._state_path).absolute() != state_path:
        raise CommitBarrierBlocked(
            "Controller/state path mismatch"
        )

    publish_stop_intent(state_path)

    fd = os.open(
        _barrier_path(state_path),
        os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
        0o600,
    )

    locked = False

    try:
        info = os.fstat(fd)

        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600
        ):
            raise CommitBarrierBlocked(
                "Unsafe commit lock"
            )

        deadline = time.monotonic() + timeout_seconds

        while True:
            try:
                fcntl.flock(
                    fd,
                    fcntl.LOCK_EX | fcntl.LOCK_NB,
                )
                locked = True
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise CommitBarrierBlocked(
                        "Stop finalization timed out; "
                        "pending marker retained"
                    )
                await asyncio.sleep(0.02)

        # Hold the commit barrier until the actual
        # controller transition returns.
        snapshot = control.emergency_stop(
            actor=actor,
            reason=reason,
        )

        if (
            snapshot.mode != "EMERGENCY_STOP"
            or snapshot.paper_execution_enabled
            or snapshot.live_execution_enabled
        ):
            raise CommitBarrierBlocked(
                "Emergency-stop acknowledgment invalid"
            )

        return snapshot

    finally:
        if locked:
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
