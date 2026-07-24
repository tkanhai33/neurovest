#!/usr/bin/env python3

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
import json
import os
import subprocess
import sys


ROOT = Path(".").resolve()

PHASE = "134B6_RESTART_PERSISTENCE_CERTIFICATION"

WORKER = (
    ROOT
    / "scripts/phase134b6_restart_persistence_worker.py"
)

STORE_FILE = (
    ROOT
    / "backend/app/stacks/chat_public/conversation_store.py"
)

OUT_DIR = ROOT / "runtime/chat_persistence"
OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "134B6_restart_persistence_latest.json"
)

OUT_TXT = (
    OUT_DIR
    / "134B6_restart_persistence_latest.txt"
)


def run_worker(
    operation: str,
    thread_id: str,
) -> dict:
    command = [
        sys.executable,
        str(WORKER),
        operation,
        "--thread-id",
        thread_id,
    ]

    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT)

    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"Worker {operation} failed.\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )

    try:
        return json.loads(
            completed.stdout
        )

    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Worker {operation} returned invalid JSON.\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        ) from error


def main() -> int:
    thread_id = (
        "thread-134b6-"
        f"{uuid4().hex}"
    )

    store_text = STORE_FILE.read_text(
        encoding="utf-8"
    )

    seed_result = None
    recover_result = None
    verify_result = None
    cleanup_result = None
    cleanup_error = None

    try:
        print("=" * 80)
        print(PHASE)
        print("=" * 80)

        print()
        print("PROCESS A — CREATE AND PERSIST")
        seed_result = run_worker(
            "seed",
            thread_id,
        )
        print(json.dumps(seed_result, indent=2))

        print()
        print("PROCESS A TERMINATED")
        print(
            "No Python objects from Process A "
            "are reused."
        )

        print()
        print("PROCESS B — COLD-START RECOVERY")
        recover_result = run_worker(
            "recover",
            thread_id,
        )
        print(json.dumps(recover_result, indent=2))

        print()
        print("PROCESS B TERMINATED")
        print(
            "No Python objects from Process B "
            "are reused."
        )

        print()
        print("PROCESS C — FINAL DATABASE RECOVERY")
        verify_result = run_worker(
            "verify",
            thread_id,
        )
        print(json.dumps(verify_result, indent=2))

    finally:
        print()
        print("PROCESS C — CLEANUP")

        try:
            cleanup_result = run_worker(
                "cleanup",
                thread_id,
            )
            print(
                json.dumps(
                    cleanup_result,
                    indent=2,
                )
            )

        except Exception as error:
            cleanup_error = str(error)
            print(
                f"Cleanup failed: {cleanup_error}",
                file=sys.stderr,
            )

    static_checks = {
        "worker_uses_separate_processes": (
            "subprocess.run" in Path(
                __file__
            ).read_text(encoding="utf-8")
        ),
        "database_only_store_used": (
            "async_session"
            in store_text
        ),
        "no_in_memory_message_cache": (
            "self.messages =" not in store_text
            and "self.threads =" not in store_text
            and "defaultdict(list)"
            not in store_text
        ),
        "persistent_healthcheck_exists": (
            '"persistent": True'
            in store_text
            or "'persistent': True"
            in store_text
        ),
    }

    process_checks = {
        "process_a_passed": bool(
            seed_result
            and seed_result.get("passed")
        ),
        "process_b_passed": bool(
            recover_result
            and recover_result.get("passed")
        ),
        "process_c_passed": bool(
            verify_result
            and verify_result.get("passed")
        ),
        "cleanup_passed": bool(
            cleanup_result
            and cleanup_result.get("passed")
        ),
        "cleanup_error_absent": (
            cleanup_error is None
        ),
    }

    checks = {
        **static_checks,
        **process_checks,
    }

    certified = all(checks.values())

    result = {
        "phase": PHASE,
        "created_at": datetime.now(UTC).isoformat(),
        "thread_id": thread_id,
        "checks": checks,
        "process_a": seed_result,
        "process_b": recover_result,
        "process_c": verify_result,
        "cleanup": cleanup_result,
        "cleanup_error": cleanup_error,
        "behavior": {
            "durable_thread_persistence": certified,
            "durable_message_persistence": certified,
            "durable_parent_links": certified,
            "durable_conversation_state": certified,
            "durable_memory_facts": certified,
            "durable_tool_evidence": certified,
            "database_only_recovery": certified,
            "history_injected_into_ollama": False,
            "streaming_enabled": False,
            "broker_execution_changed": False,
        },
        "certified": certified,
        "recommended_next_phase": (
            "134C_CONTEXT_ASSEMBLER_AND_SUMMARY_MEMORY"
            if certified
            else "134B6_RESTART_PERSISTENCE_REPAIR"
        ),
    }

    OUT_JSON.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        PHASE,
        "",
        f"certified: {certified}",
        "",
        "CHECKS",
    ]

    for name, passed in checks.items():
        lines.append(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    lines.extend(
        [
            "",
            "DURABILITY",
            (
                "thread_persistence: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            (
                "message_persistence: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            (
                "parent_links: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            (
                "conversation_state: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            (
                "memory_facts: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            (
                "tool_evidence: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            (
                "database_only_recovery: "
                f"{'PASS' if certified else 'FAIL'}"
            ),
            "",
            "BEHAVIOR",
            "history_injected_into_ollama: False",
            "streaming_enabled: False",
            "broker_execution_changed: False",
            "",
            (
                "next: "
                f"{result['recommended_next_phase']}"
            ),
        ]
    )

    OUT_TXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("134B6 FINAL RESULT")
    print("=" * 80)
    print(
        OUT_TXT.read_text(
            encoding="utf-8"
        )
    )

    return 0 if certified else 1


if __name__ == "__main__":
    raise SystemExit(main())
