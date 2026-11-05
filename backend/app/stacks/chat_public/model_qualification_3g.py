from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
QUAL = ROOT / "runtime/qualification"
VERSION = "NEUROVEST_MODEL_QUALIFICATION_3G"

MODEL = "neuro-reason:latest"
ENDPOINT = "http://127.0.0.1:11434/api/chat"

CASES = [
    {
        "id": "quantum",
        "prompt": (
            "Explain quantum entanglement to a beginner. "
            "Does it transmit information faster than light?"
        ),
        "concepts": [
            ["entangle", "correlat"],
            ["measur", "observ"],
            ["light", "signal", "information"],
        ],
    },
    {
        "id": "manual_gearbox",
        "prompt": (
            "Explain a conventional driver-operated manual "
            "transmission, starting with pressing the clutch "
            "pedal and selecting a gear. Do not explain DCTs."
        ),
        "concepts": [
            ["clutch", "pedal"],
            ["gear", "shift"],
            ["shaft", "synchron", "engag", "disconnect"],
        ],
    },
    {
        "id": "black_holes",
        "prompt": (
            "Explain how stellar black holes form and why "
            "light cannot escape beyond the event horizon."
        ),
        "concepts": [
            ["star", "collaps", "stellar"],
            ["grav", "spacetime"],
            ["horizon", "light"],
        ],
    },
    {
        "id": "photosynthesis",
        "prompt": (
            "Explain how photosynthesis works in plants "
            "using simple language."
        ),
        "concepts": [
            ["sun", "light", "solar"],
            ["plant", "leaf", "chlorophyll"],
            ["carbon", "oxygen", "sugar", "glucose"],
        ],
    },
    {
        "id": "http",
        "prompt": (
            "Explain HTTP status codes 200, 404, and 500 "
            "to a beginner software developer."
        ),
        "concepts": [
            ["200", "success"],
            ["404", "not found"],
            ["500", "server", "error"],
        ],
    },
    {
        "id": "probability",
        "prompt": (
            "Explain the difference between independent "
            "and mutually exclusive events in probability."
        ),
        "concepts": [
            ["independen", "unaffect"],
            ["exclusiv", "cannot both", "can't both"],
            ["probabil", "event"],
        ],
    },
]


def grade(case, answer, done_reason):
    """
    This is a deterministic screening metric, NOT a
    semantic accuracy or factual-truth certification.
    """
    if not isinstance(answer, str) or not answer.strip():
        return {
            "coverage": 0,
            "complete": False,
            "passed_screen": False,
            "reason": "empty",
        }

    lower = answer.casefold()

    hits = [
        any(term in lower for term in group)
        for group in case["concepts"]
    ]

    coverage = sum(hits) / len(hits)

    tail = answer.rstrip()
    complete = (
        len(tail) >= 90
        and tail.endswith((".", "!", "?", '"', ")", "*"))
        and done_reason not in (
            "length", "timeout", "error"
        )
        and not tail.endswith(("...", "…"))
    )

    forbidden_topic = (
        case["id"] == "manual_gearbox"
        and (
            "dual-clutch transmission" in lower
            or "automated manual transmission" in lower
        )
        and not (
            "clutch pedal" in lower
            and (
                "synchron" in lower
                or "shift lever" in lower
                or "gear lever" in lower
            )
        )
    )

    return {
        "coverage": round(coverage, 3),
        "complete": complete,
        "passed_screen": (
            coverage >= 0.99
            and complete
            and not forbidden_topic
        ),
        "reason": (
            "topic_drift"
            if forbidden_topic
            else "screened"
        ),
    }


def ask_model(prompt):
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer only the user's question. "
                    "Use a concise, accurate explanation. "
                    "Do not copy encyclopedia introductions. "
                    "Finish your answer completely."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "options": {
            "num_predict": 320,
            "temperature": 0.2,
        },
    }

    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    started = time.monotonic()

    try:
        with urllib.request.urlopen(
            request,
            timeout=75,
        ) as response:
            data = json.loads(
                response.read(1_000_000)
            )

        message = data.get("message") or {}

        return {
            "answer": message.get("content") or "",
            "done_reason": data.get("done_reason"),
            "eval_count": data.get("eval_count"),
            "elapsed_seconds": round(
                time.monotonic() - started, 2
            ),
            "error": None,
        }

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        return {
            "answer": "",
            "done_reason": "error",
            "eval_count": None,
            "elapsed_seconds": round(
                time.monotonic() - started, 2
            ),
            "error": type(exc).__name__,
        }


def run_suite():
    cases = []

    for case in CASES:
        print(
            "PROBE_STARTED=" + case["id"],
            flush=True,
        )

        result = ask_model(case["prompt"])

        grade_result = grade(
            case,
            result["answer"],
            result["done_reason"],
        )

        # Do not persist user text, prompts or model answers.
        record = {
            "id": case["id"],
            "status": (
                "unavailable"
                if result["error"]
                else "completed"
            ),
            "done_reason": result["done_reason"],
            "eval_count": result["eval_count"],
            "answer_chars": len(result["answer"]),
            "elapsed_seconds": result["elapsed_seconds"],
            "error_type": result["error"],
            **grade_result,
        }

        cases.append(record)

        print(
            "PROBE_RESULT="
            + case["id"]
            + " "
            + (
                "PASS"
                if record["passed_screen"]
                else "NOT_PASSED"
            ),
            flush=True,
        )

    completed = [
        c for c in cases
        if c["status"] == "completed"
    ]

    passed = sum(
        c["passed_screen"] for c in completed
    )

    return {
        "schema_version": 1,
        "suite": VERSION,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "model": MODEL,
        "scope": "direct_local_ollama_only",
        "total_cases": len(cases),
        "completed_cases": len(completed),
        "passed_screens": passed,
        "cases": cases,
        "limitations": [
            "Not authenticated chat API testing",
            "Not a semantic or factual accuracy guarantee",
            "Does not inspect retrieval or persistence",
            "Does not measure production user experience",
            "No broker or financial execution performed",
        ],
    }


def latest_result():
    if not QUAL.is_dir():
        return None

    directories = sorted(
        (
            p for p in QUAL.iterdir()
            if p.is_dir()
            and not p.is_symlink()
            and p.name.startswith("neuro_model_3G_")
        ),
        key=lambda p: p.name,
        reverse=True,
    )[:20]

    for directory in directories:
        path = directory / "evidence/results.json"

        try:
            if (
                not path.is_file()
                or path.is_symlink()
                or path.stat().st_size > 100_000
            ):
                continue

            data = json.loads(
                path.read_text(encoding="utf-8")
            )

            if (
                data.get("suite") == VERSION
                and data.get("schema_version") == 1
                and isinstance(data.get("cases"), list)
            ):
                return data

        except (OSError, ValueError, TypeError):
            continue

    return None


def report_section():
    result = latest_result()

    if result is None:
        return [
            "## Measured local-model diagnostics",
            "",
            "- No 3G qualification evidence available.",
            "- Current model quality: unverified.",
        ]

    lines = [
        "## Measured local-model diagnostics",
        "",
        "- Scope: direct local Ollama inference, "
        "not the authenticated production chat pipeline.",
        "- Timestamp: "
        + str(result["timestamp_utc"]),
        "- Model: "
        + str(result["model"]),
        "- Completed probes: "
        + str(result["completed_cases"])
        + "/"
        + str(result["total_cases"]),
        "- Passed deterministic screens: "
        + str(result["passed_screens"])
        + "/"
        + str(result["completed_cases"]),
        "",
    ]

    for case in result["cases"]:
        lines.append(
            "- "
            + case["id"]
            + ": "
            + (
                "screen_pass"
                if case["passed_screen"]
                else "needs_review"
            )
            + "; topic_coverage="
            + str(case["coverage"])
            + "; completion="
            + str(case["complete"])
            + "; termination="
            + str(case["done_reason"])
        )

    lines.extend([
        "",
        "Interpretation: these are automated screening "
        "signals. A passing result does not establish "
        "scientific accuracy, semantic relevance, "
        "retrieval grounding, or end-to-end chat quality.",
        "",
    ])

    return lines
