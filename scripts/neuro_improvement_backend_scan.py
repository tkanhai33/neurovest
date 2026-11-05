
"""Run the bounded journal against the active NeuroVest backend DB.

Does not log database credentials, change backend configuration,
or modify the original journal database.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts/neuro_improvement_journal.py"
SERVICE = "neurovest-backend.service"


def backend_environment():
    result = subprocess.run(
        ["systemctl", "show", "-P", "MainPID", SERVICE],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )

    pid = result.stdout.strip()
    if not pid.isdecimal() or int(pid) <= 0:
        raise RuntimeError("Backend service is not running.")

    raw = Path("/proc") / pid / "environ"
    values = {}

    for item in raw.read_bytes().split(b"\0"):
        if not item or b"=" not in item:
            continue
        key, value = item.split(b"=", 1)
        values[key.decode()] = value.decode(
            errors="surrogateescape"
        )

    if not values.get("DATABASE_URL"):
        raise RuntimeError(
            "Active backend has no DATABASE_URL."
        )

    return values


def main():
    if not SCANNER.is_file():
        raise RuntimeError("Journal scanner missing.")

    # Resolve the current backend process on every run.
    # This handles backend restarts without saving DB credentials.
    source_env = backend_environment()

    env = os.environ.copy()
    env["DATABASE_URL"] = source_env["DATABASE_URL"]
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    print("JOURNAL_DATABASE_TARGET=ACTIVE_BACKEND", flush=True)

    env.pop("NEUROVEST_DATABASE_URL", None)
    os.execve(
        str(ROOT / ".venv/bin/python"),
        [
            str(ROOT / ".venv/bin/python"),
            str(SCANNER),
            "--scan",
        ],
        env,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            "JOURNAL_BACKEND_TARGET_ERROR=",
            type(exc).__name__,
        )
        sys.exit(1)
