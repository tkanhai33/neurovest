#!/usr/bin/env python3

"""
Phase 136 Stage 8
Bottleneck Prediction and Upgrade Trigger Plan.

Consumes Stage 7 evidence and extends the safe read-path test to:

- 75 concurrent users
- 100 concurrent users
- 150 concurrent users
- 200 concurrent users

The ramp stops after the first failed level.

This stage:

- uses only previously approved safe GET routes
- keeps one bounded local Ollama background workload
- does not invoke mutating routes
- does not invoke broker execution
- does not enable live trading
- does not alter CPU governors
- does not modify NeuroVest
"""

from __future__ import annotations

import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )

from scripts.phase136.load.real_neurovest_load_qualifier import (
    BACKEND_BASE_URL,
    LOAD_DIRECTORY,
    determine_capacity,
    discover_safe_routes,
    render_text as render_stage7_text,
    run_load_level,
    validate_runtime,
)


AUDIT_ROOT = (
    ROOT
    / "runtime"
    / "infrastructure_audits"
)

STAGE7_REPORT = (
    AUDIT_ROOT
    / "load"
    / "latest.json"
)

OUTPUT_DIRECTORY = (
    AUDIT_ROOT
    / "bottleneck"
)

HISTORY_DIRECTORY = (
    AUDIT_ROOT
    / "history"
    / "bottleneck"
)

LATEST_JSON = (
    OUTPUT_DIRECTORY
    / "latest.json"
)

LATEST_TEXT = (
    OUTPUT_DIRECTORY
    / "latest.txt"
)

EXTENDED_LEVELS = [
    75,
    100,
    150,
    200,
]


class Stage8Failure(RuntimeError):
    pass


def write_json_atomic(
    destination: Path,
    payload: dict[str, Any],
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(destination)


def load_stage7() -> dict[str, Any]:
    if not STAGE7_REPORT.is_file():
        raise Stage8Failure(
            "Stage 7 report is missing."
        )

    payload = json.loads(
        STAGE7_REPORT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("phase") != 136:
        raise Stage8Failure(
            "Stage 7 report does not belong to Phase 136."
        )

    if payload.get("stage") != 7:
        raise Stage8Failure(
            "Latest load report is not Stage 7."
        )

    if payload.get("status") != "completed":
        raise Stage8Failure(
            "Stage 7 did not complete."
        )

    return payload


def predict_bottleneck(
    levels: list[dict[str, Any]],
) -> dict[str, Any]:
    passing = [
        level
        for level in levels
        if level["passed"]
    ]

    if not passing:
        return {
            "primary_bottleneck": "UNKNOWN",
            "confidence": "LOW",
            "reason": (
                "No passing load level was available."
            ),
        }

    highest = max(
        passing,
        key=lambda item: item["concurrency"],
    )

    request = highest["request_metrics"]
    system = highest["system_metrics"]
    ai = highest["ai_metrics"]

    scores = {
        "CPU": (
            system.get(
                "average_cpu_percent",
                0,
            )
            / 75.0
        ),
        "MEMORY": (
            max(
                0.0,
                8.0
                / max(
                    system.get(
                        "minimum_available_memory_gib",
                        0.01,
                    ),
                    0.01,
                ),
            )
        ),
        "API_LATENCY": (
            request.get(
                "p95_latency_ms",
                0,
            )
            / 1500.0
        ),
        "API_ERRORS": (
            request.get(
                "error_rate_percent",
                0,
            )
            / 1.0
        ),
        "AI_INFERENCE": (
            1.0
            if ai.get(
                "enabled",
                False,
            )
            else 0.0
        ),
    }

    primary = max(
        scores,
        key=scores.get,
    )

    if (
        ai.get("enabled")
        and ai.get(
            "average_latency_ms"
        ) is not None
    ):
        primary = "AI_INFERENCE"

    return {
        "primary_bottleneck": primary,
        "confidence": "MODERATE",
        "highest_passing_level": highest[
            "concurrency"
        ],
        "resource_pressure_scores": {
            key: round(
                value,
                4,
            )
            for key, value in scores.items()
        },
        "evidence": {
            "api_p95_latency_ms": request.get(
                "p95_latency_ms"
            ),
            "api_p99_latency_ms": request.get(
                "p99_latency_ms"
            ),
            "error_rate_percent": request.get(
                "error_rate_percent"
            ),
            "average_cpu_percent": system.get(
                "average_cpu_percent"
            ),
            "maximum_cpu_percent": system.get(
                "maximum_cpu_percent"
            ),
            "minimum_available_memory_gib": system.get(
                "minimum_available_memory_gib"
            ),
            "maximum_cpu_temperature_celsius": system.get(
                "maximum_cpu_temperature_celsius"
            ),
            "ai_average_latency_ms": ai.get(
                "average_latency_ms"
            ),
        },
        "reason": (
            "Read-only API traffic remains inexpensive. "
            "Local AI inference is expected to become the first "
            "meaningful scaling constraint."
        ),
    }


def build_upgrade_plan(
    *,
    bottleneck: dict[str, Any],
    capacity: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "priority": 1,
            "component": "AI inference routing",
            "action": (
                "Add a bounded Ollama queue, request deduplication, "
                "streaming responses, short-context fast paths, and "
                "strict per-user AI rate limits."
            ),
            "trigger": (
                "Average AI queue wait exceeds 10 seconds or "
                "p95 AI response time exceeds 30 seconds."
            ),
            "hardware_required": False,
        },
        {
            "priority": 2,
            "component": "Application fast paths",
            "action": (
                "Cache portfolio snapshots, analytics responses, "
                "market snapshots, and shared symbol calculations."
            ),
            "trigger": (
                "Read-route p95 exceeds 100 ms or average CPU "
                "exceeds 50 percent during peak traffic."
            ),
            "hardware_required": False,
        },
        {
            "priority": 3,
            "component": "GPU",
            "action": (
                "Upgrade or dedicate a GPU for Ollama inference."
            ),
            "trigger": (
                "Two or more AI requests must run simultaneously "
                "without queue delays, or model/context requirements "
                "exceed current VRAM."
            ),
            "hardware_required": True,
        },
        {
            "priority": 4,
            "component": "CPU",
            "action": (
                "Move to a higher-core-count CPU or dedicated "
                "application node."
            ),
            "trigger": (
                "Average CPU exceeds 70 percent for five minutes, "
                "or API workers become saturated under measured load."
            ),
            "hardware_required": True,
        },
        {
            "priority": 5,
            "component": "Availability infrastructure",
            "action": (
                "Add UPS protection, automated backups, reverse proxy, "
                "health monitoring, and a second machine."
            ),
            "trigger": (
                "Paying users depend on continuous availability or "
                "a single workstation outage becomes unacceptable."
            ),
            "hardware_required": True,
        },
        {
            "priority": 6,
            "component": "Database isolation",
            "action": (
                "Move PostgreSQL to a dedicated host or managed service."
            ),
            "trigger": (
                "Database p95 latency exceeds 50 ms, write queues form, "
                "or application and database workloads compete for IO."
            ),
            "hardware_required": True,
        },
    ]


def render_report(
    report: dict[str, Any],
) -> str:
    capacity = report[
        "measured_capacity"
    ]

    bottleneck = report[
        "bottleneck_prediction"
    ]

    lines = []

    lines.append("=" * 80)
    lines.append("PHASE 136")
    lines.append("BOTTLENECK PREDICTION AND UPGRADE TRIGGER PLAN")
    lines.append("=" * 80)

    lines.append("")
    lines.append("EXTENDED LOAD LEVELS")

    for level in report[
        "extended_load_levels"
    ]:
        request = level[
            "request_metrics"
        ]

        system = level[
            "system_metrics"
        ]

        lines.append(
            f"{level['concurrency']:>3} users "
            f"passed={str(level['passed']).upper()} "
            f"rps={request['requests_per_second']} "
            f"errors={request['error_rate_percent']}% "
            f"p95={request['p95_latency_ms']}ms "
            f"p99={request['p99_latency_ms']}ms "
            f"cpu_avg={system['average_cpu_percent']}% "
            f"ram_min={system['minimum_available_memory_gib']}GiB "
            f"temp_max={system['maximum_cpu_temperature_celsius']}°C"
        )

    lines.append("")
    lines.append("MEASURED CAPACITY")
    lines.append(
        "Highest passing concurrency: "
        f"{capacity['highest_tested_passing_concurrency']}"
    )
    lines.append(
        "First failing concurrency:   "
        f"{capacity['first_failing_concurrency']}"
    )
    lines.append(
        "Safe launch concurrency:     "
        f"{capacity['recommended_safe_launch_concurrency']}"
    )
    lines.append(
        "Registered-user estimate:    "
        f"{capacity['estimated_registered_user_range']['low']}"
        "-"
        f"{capacity['estimated_registered_user_range']['high']}"
    )
    lines.append(
        "Capacity status:             "
        f"{capacity['status']}"
    )

    lines.append("")
    lines.append("PREDICTED BOTTLENECK")
    lines.append(
        "Primary bottleneck:          "
        f"{bottleneck['primary_bottleneck']}"
    )
    lines.append(
        "Confidence:                  "
        f"{bottleneck['confidence']}"
    )
    lines.append(
        "Reason:                      "
        f"{bottleneck['reason']}"
    )

    lines.append("")
    lines.append("UPGRADE TRIGGERS")

    for item in report[
        "upgrade_plan"
    ]:
        lines.append("")
        lines.append(
            f"{item['priority']}. "
            f"{item['component']}"
        )
        lines.append(
            f"   Action:  {item['action']}"
        )
        lines.append(
            f"   Trigger: {item['trigger']}"
        )
        lines.append(
            "   Hardware required: "
            f"{str(item['hardware_required']).upper()}"
        )

    lines.append("")
    lines.append("SAFE-SCALING RULE")
    lines.append(
        "Do not upgrade hardware because users merely exist."
    )
    lines.append(
        "Upgrade only when measured latency, queueing, CPU, memory, "
        "availability, or model requirements cross a defined trigger."
    )

    lines.append("")
    lines.append("APPROVAL")
    lines.append("Deployment approved:         NO")
    lines.append("Live trading approved:       NO")

    lines.append("")
    lines.append("NEXT")
    lines.append(
        "Stage 9 — Infrastructure Readiness Grader"
    )

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    stage7 = load_stage7()
    runtime = validate_runtime()

    routes = stage7.get(
        "route_discovery",
        {},
    ).get(
        "routes",
        [],
    )

    if not routes:
        routes = discover_safe_routes()[
            "routes"
        ]

    existing_levels = list(
        stage7.get(
            "load_levels",
            [],
        )
    )

    extended_levels = []

    for concurrency in EXTENDED_LEVELS:
        level = run_load_level(
            concurrency=concurrency,
            routes=routes,
            ollama_enabled=runtime[
                "ollama_open"
            ],
        )

        extended_levels.append(level)

        if not level["passed"]:
            break

    all_levels = (
        existing_levels
        + extended_levels
    )

    capacity = determine_capacity(
        all_levels
    )

    bottleneck = predict_bottleneck(
        all_levels
    )

    upgrade_plan = build_upgrade_plan(
        bottleneck=bottleneck,
        capacity=capacity,
    )

    completed_at = datetime.now(
        UTC
    )

    report = {
        "phase": 136,
        "stage": 8,
        "stage_name": (
            "Bottleneck Prediction and Upgrade Trigger Plan"
        ),
        "status": "completed",
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": round(
            (
                completed_at
                - started_at
            ).total_seconds(),
            3,
        ),
        "completed_stages": [
            "hardware_and_platform_discovery",
            "thermal_qualification",
            "storage_qualification",
            "local_service_qualification",
            "ollama_throughput_qualification",
            "provisional_capacity_projection",
            "real_neurovest_load_qualification",
            "bottleneck_prediction_and_upgrade_plan",
        ],
        "application_executed": True,
        "application_modified": False,
        "mutating_routes_invoked": False,
        "broker_execution_invoked": False,
        "live_trading_invoked": False,
        "external_ai_provider_contacted": False,
        "cpu_governor_modified": False,
        "deployment_approved": False,
        "live_trading_approved": False,
        "runtime": runtime,
        "safe_routes": routes,
        "stage7_load_levels": existing_levels,
        "extended_load_levels": extended_levels,
        "all_load_levels": all_levels,
        "measured_capacity": capacity,
        "bottleneck_prediction": bottleneck,
        "upgrade_plan": upgrade_plan,
        "limitations": [
            (
                "The tested application workload remains limited "
                "to safe read-only API routes."
            ),
            (
                "Long-context AI, authenticated isolation, database "
                "writes, paper orders, WebSockets, and external market "
                "providers require scenario-specific tests."
            ),
            (
                "Registered-user projections assume approximately "
                "5 to 10 percent simultaneous activity."
            ),
        ],
    }

    timestamp = completed_at.strftime(
        "%Y%m%dT%H%M%S.%fZ"
    )

    history_json = (
        HISTORY_DIRECTORY
        / f"{timestamp}.json"
    )

    history_text = (
        HISTORY_DIRECTORY
        / f"{timestamp}.txt"
    )

    write_json_atomic(
        LATEST_JSON,
        report,
    )

    write_json_atomic(
        history_json,
        report,
    )

    text = render_report(
        report
    )

    LATEST_TEXT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    LATEST_TEXT.write_text(
        text + "\n",
        encoding="utf-8",
    )

    history_text.write_text(
        text + "\n",
        encoding="utf-8",
    )

    print(text)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except Stage8Failure as exc:
        print("=" * 80)
        print("PHASE 136 STAGE 8 BLOCKED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print("Deployment remains unapproved.")
        print("Live trading remains unapproved.")
        print("=" * 80)

        raise SystemExit(1)
