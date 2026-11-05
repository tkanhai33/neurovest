from __future__ import annotations

import argparse
import asyncio
import json
import os
import stat
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "NeuroVest stop-only local emergency operator. "
            "Does not use PostgreSQL or broker APIs."
        )
    )

    parser.add_argument(
        "--state-path",
        required=True,
        type=Path,
        help="Explicit absolute execution-control state path",
    )
    parser.add_argument("--actor", required=True)
    parser.add_argument("--reason", required=True)

    parser.add_argument(
        "--confirm-emergency-stop",
        action="store_true",
        help="Required to publish persistent stop intent",
    )

    return parser


async def perform_stop(args) -> dict:
    from backend.app.stacks.execution.execution_control import (
        ExecutionControl,
    )
    from backend.app.stacks.execution.emergency_stop_coordinator import (
        finalize_emergency_stop,
    )

    path = args.state_path

    if not path.is_absolute():
        raise ValueError("State path must be absolute")

    if path.name != "operating_mode.json":
        raise ValueError(
            "Expected explicit operating_mode.json state file"
        )

    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("Symlink state paths are prohibited")

    directory = path.parent.lstat()

    if not stat.S_ISDIR(directory.st_mode):
        raise ValueError("State parent is not a directory")

    if directory.st_uid != os.getuid():
        raise ValueError(
            "Current implementation requires state-directory ownership"
        )

    if stat.S_IMODE(directory.st_mode) & 0o022:
        raise ValueError(
            "Unsafe state-directory permissions; "
            "group/other write access must be disabled"
        )

    actor = args.actor.strip()
    reason = args.reason.strip()

    if not actor or not reason:
        raise ValueError("Actor and reason are required")

    # Constructing this controller must not authorize paper
    # or live execution. This command only calls stop.
    control = ExecutionControl(state_path=path)

    snapshot = await finalize_emergency_stop(
        control,
        path,
        actor=actor,
        reason=reason,
    )

    if snapshot.mode != "EMERGENCY_STOP":
        raise RuntimeError("Emergency stop not confirmed")

    if (
        snapshot.paper_execution_enabled
        or snapshot.live_execution_enabled
    ):
        raise RuntimeError("Execution remains enabled")

    return {
        "result": "EMERGENCY_STOP_CONFIRMED",
        "mode": snapshot.mode,
        "revision": snapshot.revision,
        "paper_execution_enabled": False,
        "live_execution_enabled": False,
    }


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.confirm_emergency_stop:
        print(
            "ERROR=Explicit --confirm-emergency-stop required",
            file=sys.stderr,
        )
        return 2

    try:
        result = asyncio.run(perform_stop(args))
    except BaseException as exc:
        # The stop intent may already have been published.
        # Never report a failed call as proof of no stop.
        print(
            "RESULT=EMERGENCY_STOP_COMPLETION_UNCONFIRMED",
            file=sys.stderr,
        )
        print(
            "ERROR_TYPE=" + type(exc).__name__,
            file=sys.stderr,
        )
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
