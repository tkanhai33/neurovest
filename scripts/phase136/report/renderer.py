#!/usr/bin/env python3

"""
Console renderer for Phase 136.
"""

from __future__ import annotations

from typing import Any


def render_qualification(
    report: dict[str, Any],
) -> str:
    summary = report.get(
        "summary",
        {},
    )

    thermal = report.get(
        "thermal_qualification",
        {},
    )

    metrics = thermal.get(
        "metrics",
        {},
    )

    grade = thermal.get(
        "grade",
        {},
    )

    stress = thermal.get(
        "stress_result",
        {},
    )

    configuration = thermal.get(
        "configuration",
        {},
    )

    lines = []

    lines.append("=" * 80)
    lines.append("PHASE 136")
    lines.append("NEUROVEST INFRASTRUCTURE QUALIFICATION")
    lines.append("=" * 80)
    lines.append("")
    lines.append("STAGE 2")
    lines.append("Thermal Qualification")
    lines.append("")
    lines.append(
        "Inspection mode:             CONTROLLED NON-DESTRUCTIVE BENCHMARK"
    )
    lines.append(
        "Application executed:        NO"
    )
    lines.append(
        "CPU stress test executed:    YES"
    )
    lines.append(
        "GPU stress test executed:    NO"
    )
    lines.append(
        "Storage benchmark executed:  NO"
    )
    lines.append(
        "CPU governor modified:       NO"
    )
    lines.append(
        "Deployment approved:         NO"
    )
    lines.append(
        "Live trading approved:       NO"
    )

    lines.append("")
    lines.append("CPU")
    lines.append(
        "Model:                       "
        f"{summary.get('cpu_model')}"
    )
    lines.append(
        "Logical workers:             "
        f"{summary.get('logical_cpus')}"
    )
    lines.append(
        "Load duration:               "
        f"{configuration.get('load_duration_seconds')} seconds"
    )
    lines.append(
        "Abort threshold:             "
        f"{configuration.get('abort_temperature_celsius')}°C"
    )

    lines.append("")
    lines.append("THERMAL RESULTS")
    lines.append(
        "Idle average:                "
        f"{metrics.get('idle_average_celsius')}°C"
    )
    lines.append(
        "Load average:                "
        f"{metrics.get('load_average_celsius')}°C"
    )
    lines.append(
        "Load peak:                   "
        f"{metrics.get('load_peak_celsius')}°C"
    )
    lines.append(
        "Thermal rise:                "
        f"{metrics.get('thermal_rise_celsius')}°C"
    )
    lines.append(
        "Final cooldown:              "
        f"{metrics.get('cooldown_final_celsius')}°C"
    )
    lines.append(
        "Cooldown drop:               "
        f"{metrics.get('cooldown_drop_celsius')}°C"
    )
    lines.append(
        "Abort-threshold headroom:    "
        f"{metrics.get('abort_threshold_headroom_celsius')}°C"
    )
    lines.append(
        "Stable plateau detected:     "
        f"{str(metrics.get('stabilization_detected', False)).upper()}"
    )

    lines.append("")
    lines.append("STRESS RESULT")
    lines.append(
        "Return code:                 "
        f"{stress.get('returncode')}"
    )
    lines.append(
        "Stress passed:               "
        f"{str(stress.get('stress_passed', False)).upper()}"
    )
    lines.append(
        "Safety abort triggered:      "
        f"{str(stress.get('safety_abort_triggered', False)).upper()}"
    )

    lines.append("")
    lines.append("THERMAL GRADE")
    lines.append(
        "Grade:                       "
        f"{grade.get('thermal_grade')}"
    )
    lines.append(
        "Score:                       "
        f"{grade.get('score')}/{grade.get('maximum')}"
    )
    lines.append(
        "Stress stability:            "
        f"{grade.get('stress_stability')}"
    )
    lines.append(
        "Cooldown recovery:           "
        f"{grade.get('cooldown_recovery')}"
    )
    lines.append(
        "Qualified for Stage 3:       "
        f"{str(grade.get('qualified_for_next_stage', False)).upper()}"
    )

    if grade.get("deductions"):
        lines.append("")
        lines.append("DEDUCTIONS")

        for deduction in grade["deductions"]:
            lines.append(
                f"- {deduction}"
            )

    lines.append("")
    lines.append("OUTPUT")
    lines.append(
        "runtime/infrastructure_audits/latest.json"
    )
    lines.append(
        "runtime/infrastructure_audits/thermal/latest.json"
    )
    lines.append(
        "runtime/infrastructure_audits/history/<timestamp>.json"
    )
    lines.append(
        "runtime/infrastructure_audits/history/thermal/<timestamp>.json"
    )

    lines.append("")
    lines.append("NEXT")
    lines.append(
        "Implement Stage 3 — Storage Qualification"
    )

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)
