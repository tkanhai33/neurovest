#!/usr/bin/env python3

"""
Phase 136 Stage 2 — Thermal Qualification.

Procedure:

1. Load the Stage 1 hardware inventory.
2. Locate the AMD CPU Tctl sensor.
3. Record a 10-second idle baseline.
4. Run stress-ng across all logical CPUs for 120 seconds.
5. Record CPU temperature once per second.
6. Abort the workload if CPU temperature reaches 88°C.
7. Record a 60-second cooldown.
8. Grade thermal peak, stability, and recovery.

This stage does not:

- execute NeuroVest application code
- modify CPU governors
- overclock or undervolt hardware
- modify BIOS settings
- run GPU stress
- run destructive storage tests
- approve deployment
- approve live trading
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from scripts.phase136.utils.command_runner import (
    command_exists,
    run_json_command,
)


IDLE_DURATION_SECONDS = 10
LOAD_DURATION_SECONDS = 120
COOLDOWN_DURATION_SECONDS = 60
SAMPLE_INTERVAL_SECONDS = 1.0
ABORT_TEMPERATURE_C = 88.0


class ThermalQualificationFailure(RuntimeError):
    """
    Raised when thermal qualification cannot be completed safely.
    """


class ThermalQualifier:
    """
    Perform a controlled CPU thermal qualification.
    """

    def __init__(
        self,
        repository_root: Path,
        hardware_discovery: dict[str, Any],
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.hardware_discovery = hardware_discovery

        summary = hardware_discovery.get(
            "summary",
            {},
        )

        logical_cpus = summary.get(
            "logical_cpus",
            1,
        )

        try:
            self.logical_cpus = max(
                1,
                int(logical_cpus),
            )
        except (
            TypeError,
            ValueError,
        ):
            self.logical_cpus = 1

    def qualify(self) -> dict[str, Any]:
        started_at = datetime.now(UTC)

        self._validate_prerequisites()

        sensor_identity = self._locate_cpu_sensor()

        idle_samples = self._collect_samples(
            phase="idle",
            duration_seconds=IDLE_DURATION_SECONDS,
            sensor_identity=sensor_identity,
        )

        stress_result, load_samples = self._run_cpu_load(
            sensor_identity=sensor_identity,
        )

        cooldown_samples = self._collect_samples(
            phase="cooldown",
            duration_seconds=COOLDOWN_DURATION_SECONDS,
            sensor_identity=sensor_identity,
        )

        all_samples = (
            idle_samples
            + load_samples
            + cooldown_samples
        )

        metrics = self._calculate_metrics(
            idle_samples=idle_samples,
            load_samples=load_samples,
            cooldown_samples=cooldown_samples,
            stress_result=stress_result,
        )

        grade = self._grade(metrics)

        completed_at = datetime.now(UTC)

        return {
            "qualification_name": (
                "CPU Thermal Qualification"
            ),
            "qualification_mode": (
                "controlled_synthetic_cpu_load"
            ),
            "status": (
                "completed"
                if not stress_result[
                    "safety_abort_triggered"
                ]
                else "completed_with_safety_abort"
            ),
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": round(
                (
                    completed_at
                    - started_at
                ).total_seconds(),
                6,
            ),
            "configuration": {
                "logical_cpu_workers": self.logical_cpus,
                "idle_duration_seconds": (
                    IDLE_DURATION_SECONDS
                ),
                "load_duration_seconds": (
                    LOAD_DURATION_SECONDS
                ),
                "cooldown_duration_seconds": (
                    COOLDOWN_DURATION_SECONDS
                ),
                "sample_interval_seconds": (
                    SAMPLE_INTERVAL_SECONDS
                ),
                "abort_temperature_celsius": (
                    ABORT_TEMPERATURE_C
                ),
                "cpu_governor_modified": False,
                "overclock_modified": False,
                "voltage_modified": False,
            },
            "sensor": sensor_identity,
            "stress_result": stress_result,
            "metrics": metrics,
            "grade": grade,
            "samples": all_samples,
            "sample_counts": {
                "idle": len(idle_samples),
                "load": len(load_samples),
                "cooldown": len(cooldown_samples),
                "total": len(all_samples),
            },
            "safety": {
                "abort_threshold_celsius": (
                    ABORT_TEMPERATURE_C
                ),
                "abort_triggered": stress_result[
                    "safety_abort_triggered"
                ],
                "maximum_observed_celsius": metrics[
                    "maximum_temperature_celsius"
                ],
                "deployment_approved": False,
                "live_trading_approved": False,
            },
            "limitations": [
                (
                    "This qualification stresses CPU arithmetic only "
                    "and does not represent every NeuroVest workload."
                ),
                (
                    "The current CPU scaling governor is preserved."
                ),
                (
                    "GPU, storage, network, database, and application "
                    "load are not included in this stage."
                ),
            ],
        }

    def _validate_prerequisites(self) -> None:
        if not command_exists("sensors"):
            raise ThermalQualificationFailure(
                "The sensors command is not installed."
            )

        if not command_exists("stress-ng"):
            raise ThermalQualificationFailure(
                "The stress-ng command is not installed."
            )

        sensors = run_json_command(
            ["sensors", "-j"],
        )

        if sensors.get(
            "json_status"
        ) != "parsed":
            raise ThermalQualificationFailure(
                "Unable to read sensor data as JSON."
            )

    def _locate_cpu_sensor(
        self,
    ) -> dict[str, str]:
        payload = run_json_command(
            ["sensors", "-j"],
        ).get("json")

        candidates: list[dict[str, str]] = []

        if not isinstance(payload, dict):
            raise ThermalQualificationFailure(
                "Sensor payload is not a dictionary."
            )

        for chip_name, chip_data in payload.items():
            if not isinstance(chip_data, dict):
                continue

            for feature_name, feature_data in chip_data.items():
                if not isinstance(feature_data, dict):
                    continue

                for key, value in feature_data.items():
                    if not isinstance(
                        value,
                        (int, float),
                    ):
                        continue

                    if not str(key).endswith(
                        "_input"
                    ):
                        continue

                    identity = {
                        "chip": str(chip_name),
                        "feature": str(feature_name),
                        "input_key": str(key),
                    }

                    normalized = (
                        f"{chip_name} "
                        f"{feature_name} "
                        f"{key}"
                    ).lower()

                    if (
                        "k10temp" in normalized
                        and "tctl" in normalized
                    ):
                        return identity

                    if "tctl" in normalized:
                        candidates.insert(
                            0,
                            identity,
                        )
                    elif "package" in normalized:
                        candidates.append(identity)
                    elif (
                        "k10temp" in normalized
                        and "tccd" in normalized
                    ):
                        candidates.append(identity)

        if not candidates:
            raise ThermalQualificationFailure(
                "No suitable CPU temperature sensor was found."
            )

        return candidates[0]

    def _read_temperature(
        self,
        sensor_identity: dict[str, str],
    ) -> float:
        payload = run_json_command(
            ["sensors", "-j"],
        ).get("json")

        try:
            value = (
                payload[
                    sensor_identity["chip"]
                ][
                    sensor_identity["feature"]
                ][
                    sensor_identity["input_key"]
                ]
            )
        except (
            KeyError,
            TypeError,
        ) as exc:
            raise ThermalQualificationFailure(
                "The selected CPU sensor disappeared."
            ) from exc

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ThermalQualificationFailure(
                "CPU temperature was not numeric."
            ) from exc

    def _collect_samples(
        self,
        *,
        phase: str,
        duration_seconds: int,
        sensor_identity: dict[str, str],
    ) -> list[dict[str, Any]]:
        samples = []

        start_monotonic = time.monotonic()
        next_sample = start_monotonic

        while (
            time.monotonic()
            - start_monotonic
            < duration_seconds
        ):
            now = datetime.now(UTC)
            elapsed = (
                time.monotonic()
                - start_monotonic
            )

            temperature = self._read_temperature(
                sensor_identity
            )

            samples.append(
                {
                    "phase": phase,
                    "timestamp": now.isoformat(),
                    "elapsed_seconds": round(
                        elapsed,
                        3,
                    ),
                    "temperature_celsius": round(
                        temperature,
                        3,
                    ),
                }
            )

            next_sample += SAMPLE_INTERVAL_SECONDS

            sleep_duration = (
                next_sample
                - time.monotonic()
            )

            if sleep_duration > 0:
                time.sleep(sleep_duration)

        return samples

    def _run_cpu_load(
        self,
        *,
        sensor_identity: dict[str, str],
    ) -> tuple[
        dict[str, Any],
        list[dict[str, Any]],
    ]:
        command = [
            "stress-ng",
            "--cpu",
            str(self.logical_cpus),
            "--timeout",
            f"{LOAD_DURATION_SECONDS}s",
            "--metrics-brief",
        ]

        environment = dict(os.environ)

        process = subprocess.Popen(
            command,
            cwd=self.repository_root,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )

        samples = []
        safety_abort_triggered = False
        abort_temperature = None

        start_monotonic = time.monotonic()
        next_sample = start_monotonic

        try:
            while process.poll() is None:
                now = datetime.now(UTC)
                elapsed = (
                    time.monotonic()
                    - start_monotonic
                )

                temperature = self._read_temperature(
                    sensor_identity
                )

                samples.append(
                    {
                        "phase": "load",
                        "timestamp": now.isoformat(),
                        "elapsed_seconds": round(
                            elapsed,
                            3,
                        ),
                        "temperature_celsius": round(
                            temperature,
                            3,
                        ),
                    }
                )

                if (
                    temperature
                    >= ABORT_TEMPERATURE_C
                ):
                    safety_abort_triggered = True
                    abort_temperature = temperature

                    os.killpg(
                        process.pid,
                        signal.SIGTERM,
                    )

                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(
                            process.pid,
                            signal.SIGKILL,
                        )

                    break

                if (
                    elapsed
                    > LOAD_DURATION_SECONDS + 15
                ):
                    os.killpg(
                        process.pid,
                        signal.SIGTERM,
                    )

                    raise ThermalQualificationFailure(
                        "stress-ng exceeded the expected runtime."
                    )

                next_sample += (
                    SAMPLE_INTERVAL_SECONDS
                )

                sleep_duration = (
                    next_sample
                    - time.monotonic()
                )

                if sleep_duration > 0:
                    time.sleep(sleep_duration)

            stdout, stderr = process.communicate(
                timeout=15,
            )

        except Exception:
            if process.poll() is None:
                os.killpg(
                    process.pid,
                    signal.SIGTERM,
                )

            raise

        returncode = process.returncode

        stress_passed = (
            returncode == 0
            and not safety_abort_triggered
        )

        return (
            {
                "command": command,
                "returncode": returncode,
                "stdout": stdout.strip(),
                "stderr": stderr.strip(),
                "stress_passed": stress_passed,
                "safety_abort_triggered": (
                    safety_abort_triggered
                ),
                "abort_temperature_celsius": (
                    round(
                        abort_temperature,
                        3,
                    )
                    if abort_temperature is not None
                    else None
                ),
            },
            samples,
        )

    @staticmethod
    def _calculate_metrics(
        *,
        idle_samples: list[dict[str, Any]],
        load_samples: list[dict[str, Any]],
        cooldown_samples: list[dict[str, Any]],
        stress_result: dict[str, Any],
    ) -> dict[str, Any]:
        idle_values = [
            item["temperature_celsius"]
            for item in idle_samples
        ]

        load_values = [
            item["temperature_celsius"]
            for item in load_samples
        ]

        cooldown_values = [
            item["temperature_celsius"]
            for item in cooldown_samples
        ]

        if not idle_values:
            raise ThermalQualificationFailure(
                "No idle temperature samples were collected."
            )

        if not load_values:
            raise ThermalQualificationFailure(
                "No load temperature samples were collected."
            )

        if not cooldown_values:
            raise ThermalQualificationFailure(
                "No cooldown samples were collected."
            )

        idle_average = mean(idle_values)
        load_peak = max(load_values)
        load_average = mean(load_values)
        cooldown_final = cooldown_values[-1]
        cooldown_minimum = min(cooldown_values)

        tail_count = min(
            30,
            len(load_values),
        )

        load_tail = load_values[
            -tail_count:
        ]

        tail_range = (
            max(load_tail)
            - min(load_tail)
        )

        cooldown_drop = (
            load_peak
            - cooldown_final
        )

        thermal_rise = (
            load_peak
            - idle_average
        )

        threshold_headroom = (
            ABORT_TEMPERATURE_C
            - load_peak
        )

        stabilization_detected = (
            tail_range <= 2.0
        )

        cooldown_recovery_ratio = (
            cooldown_drop
            / thermal_rise
            if thermal_rise > 0
            else 0.0
        )

        return {
            "idle_average_celsius": round(
                idle_average,
                2,
            ),
            "idle_minimum_celsius": round(
                min(idle_values),
                2,
            ),
            "idle_maximum_celsius": round(
                max(idle_values),
                2,
            ),
            "load_average_celsius": round(
                load_average,
                2,
            ),
            "load_peak_celsius": round(
                load_peak,
                2,
            ),
            "maximum_temperature_celsius": round(
                max(
                    idle_values
                    + load_values
                    + cooldown_values
                ),
                2,
            ),
            "thermal_rise_celsius": round(
                thermal_rise,
                2,
            ),
            "load_tail_range_celsius": round(
                tail_range,
                2,
            ),
            "stabilization_detected": (
                stabilization_detected
            ),
            "cooldown_final_celsius": round(
                cooldown_final,
                2,
            ),
            "cooldown_minimum_celsius": round(
                cooldown_minimum,
                2,
            ),
            "cooldown_drop_celsius": round(
                cooldown_drop,
                2,
            ),
            "cooldown_recovery_ratio": round(
                cooldown_recovery_ratio,
                4,
            ),
            "abort_threshold_headroom_celsius": round(
                threshold_headroom,
                2,
            ),
            "stress_passed": stress_result[
                "stress_passed"
            ],
            "safety_abort_triggered": stress_result[
                "safety_abort_triggered"
            ],
        }

    @staticmethod
    def _grade(
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        peak = metrics[
            "load_peak_celsius"
        ]

        stable = metrics[
            "stabilization_detected"
        ]

        passed = metrics[
            "stress_passed"
        ]

        safety_abort = metrics[
            "safety_abort_triggered"
        ]

        recovery_ratio = metrics[
            "cooldown_recovery_ratio"
        ]

        if safety_abort or peak >= 88:
            grade = "CRITICAL"
            score = 0
        elif peak < 70:
            grade = "EXCELLENT"
            score = 100
        elif peak < 80:
            grade = "GOOD"
            score = 90
        elif peak < 85:
            grade = "ACCEPTABLE"
            score = 75
        else:
            grade = "POOR"
            score = 50

        deductions = []

        if not passed:
            score = max(
                0,
                score - 30,
            )

            deductions.append(
                "stress workload did not complete normally"
            )

        if not stable:
            score = max(
                0,
                score - 10,
            )

            deductions.append(
                "temperature did not form a stable load plateau"
            )

        if recovery_ratio < 0.60:
            score = max(
                0,
                score - 10,
            )

            deductions.append(
                "cooldown recovery was below 60 percent"
            )

        if score >= 90:
            final_grade = (
                "EXCELLENT"
                if score >= 95
                else "GOOD"
            )
        elif score >= 75:
            final_grade = "ACCEPTABLE"
        elif score >= 50:
            final_grade = "POOR"
        else:
            final_grade = "CRITICAL"

        return {
            "thermal_grade": final_grade,
            "score": score,
            "maximum": 100,
            "initial_peak_band": grade,
            "stress_stability": (
                "PASS"
                if passed and stable
                else "FAIL"
            ),
            "cooldown_recovery": (
                "PASS"
                if recovery_ratio >= 0.60
                else "FAIL"
            ),
            "safety_abort": (
                "PASS"
                if not safety_abort
                else "TRIGGERED"
            ),
            "deductions": deductions,
            "qualified_for_next_stage": (
                score >= 75
                and passed
                and not safety_abort
            ),
            "deployment_approved": False,
            "live_trading_approved": False,
        }
