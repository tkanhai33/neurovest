from __future__ import annotations

import asyncio
import fcntl
import os
import stat
import time
from contextlib import asynccontextmanager
from pathlib import Path


class CommitBarrierBlocked(RuntimeError):
    pass


def _pending_marker(state_path: Path) -> Path:
    return state_path.with_name(
        state_path.name + ".stop.pending"
    )


def _barrier_path(state_path: Path) -> Path:
    return state_path.with_name(
        state_path.name + ".commit.lock"
    )


def assert_no_pending_stop(state_path: Path) -> None:
    marker = _pending_marker(state_path)

    try:
        info = marker.lstat()
    except FileNotFoundError:
        return

    # Any existing entry blocks execution, including an
    # unsafe symlink or unexpected filesystem object.
    raise CommitBarrierBlocked(
        "Emergency-stop intent is present"
    )


@asynccontextmanager
async def financial_commit_barrier(
    state_path: Path,
    *,
    timeout_seconds: float = 10.0,
):
    """
    Experimental commit barrier.

    This function does not authorize execution.
    The caller must also check the authoritative
    execution mode while the barrier is held.

    Emergency-stop finalization must acquire the
    same barrier before acknowledging completion.
    """

    state_path = Path(state_path)

    if (
        not state_path.is_absolute()
        or not state_path.parent.is_dir()
        or state_path.parent.is_symlink()
    ):
        raise CommitBarrierBlocked(
            "Unqualified execution-control directory"
        )

    assert_no_pending_stop(state_path)

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
                "Unsafe commit-barrier lock"
            )

        deadline = (
            time.monotonic() + timeout_seconds
        )

        while True:
            assert_no_pending_stop(state_path)

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
                        "Commit-barrier acquisition timed out"
                    )

                await asyncio.sleep(0.02)

        assert_no_pending_stop(state_path)

        yield

    finally:
        if locked:
            fcntl.flock(
                fd,
                fcntl.LOCK_UN,
            )

        os.close(fd)
