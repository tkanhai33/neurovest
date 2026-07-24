#!/usr/bin/env python3

"""
Safe read-only command execution utilities for Phase 136.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(
    command: list[str],
    *,
    timeout: int = 20,
) -> dict[str, Any]:
    executable = command[0]

    if not command_exists(executable):
        return {
            "command": command,
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "status": "command_not_found",
        }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

        return {
            "command": command,
            "available": True,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "status": (
                "success"
                if result.returncode == 0
                else "command_failed"
            ),
        }

    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "available": True,
            "returncode": None,
            "stdout": (
                exc.stdout.decode()
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            ),
            "stderr": (
                exc.stderr.decode()
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            ),
            "status": "timeout",
        }

    except OSError as exc:
        return {
            "command": command,
            "available": True,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "status": "os_error",
        }


def run_json_command(
    command: list[str],
    *,
    timeout: int = 20,
) -> dict[str, Any]:
    result = run_command(
        command,
        timeout=timeout,
    )

    if result["status"] != "success":
        return {
            **result,
            "json": None,
            "json_status": "not_parsed",
        }

    try:
        parsed = json.loads(result["stdout"])

        return {
            **result,
            "json": parsed,
            "json_status": "parsed",
        }

    except json.JSONDecodeError as exc:
        return {
            **result,
            "json": None,
            "json_status": "invalid_json",
            "json_error": str(exc),
        }


def version_command(
    name: str,
    candidates: list[list[str]],
) -> dict[str, Any]:
    attempts = []

    for command in candidates:
        result = run_command(command)
        attempts.append(result)

        if result["status"] == "success":
            output = (
                result["stdout"]
                or result["stderr"]
            ).splitlines()

            return {
                "name": name,
                "available": True,
                "version": (
                    output[0].strip()
                    if output
                    else "available"
                ),
                "command": command,
                "attempts": attempts,
            }

    return {
        "name": name,
        "available": False,
        "version": None,
        "command": None,
        "attempts": attempts,
    }
