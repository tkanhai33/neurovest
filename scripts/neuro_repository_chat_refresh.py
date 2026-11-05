#!/usr/bin/env python3
"""NeuroVest developer-chat generation-first refresh wrapper.

Authorization is enforced by the existing authenticated chat route.
This script is an internal runner, not an authorization boundary.
"""
from __future__ import annotations

import fcntl
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/qualification/repository_intelligence_v1"
WRITER = ROOT / "scripts/neuro_repository_generation_refresh.py"
LOCK = ROOT / "runtime/qualification/repository_refresh.lock"

def main():
    if len(sys.argv) != 1:
        print("CHAT_REFRESH_STATUS=BLOCKED")
        return 2

    if not WRITER.is_file() or WRITER.is_symlink():
        print("CHAT_REFRESH_STATUS=WRITER_UNAVAILABLE")
        return 1

    try:
        fd = os.open(
            LOCK,
            os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
            0o600,
        )
    except OSError:
        print("CHAT_REFRESH_STATUS=LOCK_UNAVAILABLE")
        return 1

    try:
        try:
            fcntl.flock(
                fd,
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError:
            print("CHAT_REFRESH_STATUS=ALREADY_RUNNING")
            return 1

        try:
            result = subprocess.run(
                [sys.executable, "-B", str(WRITER)],
                cwd=ROOT,
                env={
                    "PATH": "/usr/bin:/bin",
                    "HOME": str(Path.home()),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                capture_output=True,
                text=True,
                timeout=210,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            print("CHAT_REFRESH_STATUS=WRITER_TIMEOUT_OR_FAILURE")
            return 1

        required = (
            "GENERATION_FIRST_WRITER=PASS",
            "REPOSITORY_REFRESH=PASS",
            "IMMUTABLE_SNAPSHOT=VERIFIED",
            "ATOMIC_ACTIVATION=PASS",
            "LEGACY_SNAPSHOT_WRITES=False",
        )

        if (
            result.returncode != 0
            or not all(
                marker in result.stdout
                for marker in required
            )
        ):
            print("CHAT_REFRESH_STATUS=FAILED")
            print("ACTIVE_SNAPSHOT_MUST_BE_VERIFIED")
            return 1

        # Check the currently active generation through
        # the same verified reader as developer queries.
        try:
            from neuro_repository_snapshot_reader import (
                read_active_pair,
            )
            index_raw, graph_raw = read_active_pair()

            import hashlib
            import json

            graph = json.loads(graph_raw)

            if graph.get("inventory_sha256") != (
                hashlib.sha256(index_raw).hexdigest()
            ):
                raise ValueError("GRAPH_INDEX_MISMATCH")
        except (OSError, ValueError, TypeError, KeyError):
            print("CHAT_REFRESH_STATUS=READER_VERIFY_FAILED")
            return 1

        allowed = (
            "SOURCE_FILES=",
            "FILE_DEPENDENCY_EDGES=",
            "BACKEND_STACKS=",
            "CROSS_STACK_RELATIONSHIPS=",
            "ACTIVE_GENERATION=",
            "IMMUTABLE_SNAPSHOT=",
            "ATOMIC_ACTIVATION=",
            "LEGACY_SNAPSHOT_WRITES=",
        )

        for line in result.stdout.splitlines():
            if line.startswith(allowed):
                print(line[:180])

        print("ACTIVE_GENERATION_READER=PASS")
        print("CHAT_REFRESH_STATUS=PASS")
        print("PATCH_APPLIED=False")
        return 0

    finally:
        os.close(fd)

if __name__ == "__main__":
    raise SystemExit(main())
