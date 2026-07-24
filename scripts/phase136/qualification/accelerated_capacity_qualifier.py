#!/usr/bin/env python3

"""
Phase 136 Accelerated Qualification — Stages 3 through 6.

Stage 3:
    Non-destructive storage qualification.

Stage 4:
    Local platform and service qualification.

Stage 5:
    Local Ollama throughput and concurrency qualification.

Stage 6:
    Conservative provisional capacity projection.

Important:

- Uses a temporary benchmark file only.
- Deletes the benchmark file after completion.
- Does not start NeuroVest.
- Does not alter PostgreSQL data.
- Does not alter Ollama models.
- Does not change CPU governors.
- Does not perform an external network test.
- User-capacity estimates remain provisional until the actual
  NeuroVest API receives end-to-end load testing.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

AUDIT_ROOT = (
    ROOT
    / "runtime"
    / "infrastructure_audits"
)

STAGE2_REPORT = (
    AUDIT_ROOT
    / "latest.json"
)

CAPACITY_DIRECTORY = (
    AUDIT_ROOT
    / "capacity"
)

CAPACITY_HISTORY = (
    AUDIT_ROOT
    / "history"
    / "capacity"
)

BENCHMARK_DIRECTORY = (
    AUDIT_ROOT
    / "benchmark_tmp"
)

BENCHMARK_FILE = (
    BENCHMARK_DIRECTORY
    / "phase136_fio_test.bin"
)

LATEST_REPORT = (
    CAPACITY_DIRECTORY
    / "latest.json"
)

LATEST_TEXT = (
    CAPACITY_DIRECTORY
    / "latest.txt"
)

FIO_SIZE = "512M"
FIO_RUNTIME_SECONDS = 12

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_PREDICT_TOKENS = 48
OLLAMA_TIMEOUT_SECONDS = 180


class QualificationFailure(RuntimeError):
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


def run_command(
    command: list[str],
    *,
    timeout: int,
) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "passed": result.returncode == 0,
        }

    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
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
            "passed": False,
            "timeout": True,
        }


def load_stage2() -> dict[str, Any]:
    if not STAGE2_REPORT.is_file():
        raise QualificationFailure(
            "Phase 136 Stage 2 report is missing."
        )

    payload = json.loads(
        STAGE2_REPORT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("phase") != 136:
        raise QualificationFailure(
            "Latest infrastructure report is not Phase 136."
        )

    if payload.get("stage") != 2:
        raise QualificationFailure(
            "Latest infrastructure report is not Stage 2."
        )

    if not payload.get(
        "summary",
        {},
    ).get(
        "qualified_for_next_stage",
        False,
    ):
        raise QualificationFailure(
            "Stage 2 did not qualify the machine for Stage 3."
        )

    return payload


def run_fio_job(
    *,
    name: str,
    readwrite: str,
    block_size: str,
    runtime_seconds: int,
    direct: int,
) -> dict[str, Any]:
    command = [
        "fio",
        f"--name={name}",
        f"--filename={BENCHMARK_FILE}",
        f"--size={FIO_SIZE}",
        f"--rw={readwrite}",
        f"--bs={block_size}",
        "--ioengine=libaio",
        "--iodepth=16",
        "--numjobs=1",
        f"--runtime={runtime_seconds}",
        "--time_based=1",
        f"--direct={direct}",
        "--group_reporting=1",
        "--output-format=json",
    ]

    result = run_command(
        command,
        timeout=runtime_seconds + 45,
    )

    parsed = None

    if result["passed"]:
        try:
            parsed = json.loads(
                result["stdout"]
            )
        except json.JSONDecodeError:
            result["passed"] = False
            result["parse_error"] = True

    return {
        **result,
        "json": parsed,
    }


def extract_fio_metrics(
    result: dict[str, Any],
) -> dict[str, Any]:
    payload = result.get("json")

    if not isinstance(payload, dict):
        return {
            "available": False,
        }

    jobs = payload.get("jobs", [])

    if not jobs:
        return {
            "available": False,
        }

    job = jobs[0]
    read = job.get("read", {})
    write = job.get("write", {})

    return {
        "available": True,
        "read_mib_per_second": round(
            float(read.get("bw_bytes", 0))
            / 1024
            / 1024,
            2,
        ),
        "write_mib_per_second": round(
            float(write.get("bw_bytes", 0))
            / 1024
            / 1024,
            2,
        ),
        "read_iops": round(
            float(read.get("iops", 0)),
            2,
        ),
        "write_iops": round(
            float(write.get("iops", 0)),
            2,
        ),
        "read_latency_ms": round(
            float(
                read.get(
                    "clat_ns",
                    {},
                ).get("mean", 0)
            )
            / 1_000_000,
            3,
        ),
        "write_latency_ms": round(
            float(
                write.get(
                    "clat_ns",
                    {},
                ).get("mean", 0)
            )
            / 1_000_000,
            3,
        ),
    }


def storage_qualification() -> dict[str, Any]:
    if shutil.which("fio") is None:
        raise QualificationFailure(
            "fio is not installed."
        )

    BENCHMARK_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    jobs = {}

    try:
        jobs["sequential_write"] = run_fio_job(
            name="phase136_seq_write",
            readwrite="write",
            block_size="1M",
            runtime_seconds=FIO_RUNTIME_SECONDS,
            direct=1,
        )

        jobs["sequential_read"] = run_fio_job(
            name="phase136_seq_read",
            readwrite="read",
            block_size="1M",
            runtime_seconds=FIO_RUNTIME_SECONDS,
            direct=1,
        )

        jobs["random_mixed"] = run_fio_job(
            name="phase136_random_mixed",
            readwrite="randrw",
            block_size="4k",
            runtime_seconds=FIO_RUNTIME_SECONDS,
            direct=1,
        )

        metrics = {
            name: extract_fio_metrics(result)
            for name, result in jobs.items()
        }

        passed = all(
            result.get("passed", False)
            for result in jobs.values()
        )

        seq_read = metrics[
            "sequential_read"
        ].get(
            "read_mib_per_second",
            0,
        )

        seq_write = metrics[
            "sequential_write"
        ].get(
            "write_mib_per_second",
            0,
        )

        random_read_iops = metrics[
            "random_mixed"
        ].get(
            "read_iops",
            0,
        )

        random_write_iops = metrics[
            "random_mixed"
        ].get(
            "write_iops",
            0,
        )

        if (
            passed
            and seq_read >= 500
            and seq_write >= 300
            and random_read_iops >= 5000
        ):
            grade = "EXCELLENT"
            score = 100
        elif (
            passed
            and seq_read >= 250
            and seq_write >= 150
            and random_read_iops >= 2000
        ):
            grade = "GOOD"
            score = 90
        elif (
            passed
            and seq_read >= 100
            and seq_write >= 75
            and random_read_iops >= 500
        ):
            grade = "ACCEPTABLE"
            score = 75
        elif passed:
            grade = "LIMITED"
            score = 55
        else:
            grade = "FAILED"
            score = 0

        return {
            "passed": passed,
            "temporary_file": str(
                BENCHMARK_FILE
            ),
            "temporary_file_deleted": False,
            "benchmark_size": FIO_SIZE,
            "jobs": jobs,
            "metrics": metrics,
            "summary": {
                "sequential_read_mib_per_second": (
                    seq_read
                ),
                "sequential_write_mib_per_second": (
                    seq_write
                ),
                "random_read_iops": (
                    random_read_iops
                ),
                "random_write_iops": (
                    random_write_iops
                ),
                "grade": grade,
                "score": score,
            },
            "destructive_test_executed": False,
        }

    finally:
        try:
            BENCHMARK_FILE.unlink(
                missing_ok=True
            )
        except OSError:
            pass


def port_open(
    host: str,
    port: int,
    timeout: float = 1.0,
) -> bool:
    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            return True
    except OSError:
        return False


def service_qualification() -> dict[str, Any]:
    probes = {
        "frontend_3001": 3001,
        "fastapi_8000": 8000,
        "postgres_5432": 5432,
        "ollama_11434": 11434,
        "redis_6379": 6379,
    }

    results = {
        name: {
            "port": port,
            "open": port_open(
                "127.0.0.1",
                port,
            ),
        }
        for name, port in probes.items()
    }

    return {
        "host": "127.0.0.1",
        "probes": results,
        "open_count": sum(
            1
            for item in results.values()
            if item["open"]
        ),
        "services_started": False,
        "services_stopped": False,
        "application_executed": False,
    }


def http_json(
    *,
    url: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> tuple[
    int,
    dict[str, Any],
    float,
]:
    data = None
    headers = {}

    if payload is not None:
        data = json.dumps(
            payload
        ).encode("utf-8")

        headers[
            "Content-Type"
        ] = "application/json"

    request = urllib.request.Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    started = time.perf_counter()

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        body = response.read()

        elapsed = (
            time.perf_counter()
            - started
        )

        parsed = json.loads(
            body.decode("utf-8")
        )

        return (
            response.status,
            parsed,
            elapsed,
        )


def select_ollama_model() -> str | None:
    try:
        status, payload, _ = http_json(
            url=f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10,
        )
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return None

    if status != 200:
        return None

    models = payload.get(
        "models",
        [],
    )

    if not models:
        return None

    return str(
        models[0].get(
            "name",
            "",
        )
    ) or None


def ollama_request(
    model: str,
    request_number: int,
) -> dict[str, Any]:
    prompt = (
        "Return one concise sentence confirming that "
        f"local infrastructure test {request_number} completed."
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": OLLAMA_PREDICT_TOKENS,
        },
    }

    started = time.perf_counter()

    try:
        status, response, wall_seconds = http_json(
            url=f"{OLLAMA_BASE_URL}/api/generate",
            method="POST",
            payload=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )

        elapsed = (
            time.perf_counter()
            - started
        )

        eval_count = int(
            response.get(
                "eval_count",
                0,
            )
            or 0
        )

        eval_duration_ns = int(
            response.get(
                "eval_duration",
                0,
            )
            or 0
        )

        tokens_per_second = 0.0

        if (
            eval_count > 0
            and eval_duration_ns > 0
        ):
            tokens_per_second = (
                eval_count
                / (
                    eval_duration_ns
                    / 1_000_000_000
                )
            )

        return {
            "passed": status == 200,
            "status_code": status,
            "wall_seconds": round(
                wall_seconds,
                3,
            ),
            "total_elapsed_seconds": round(
                elapsed,
                3,
            ),
            "eval_count": eval_count,
            "tokens_per_second": round(
                tokens_per_second,
                3,
            ),
            "done": response.get(
                "done",
                False,
            ),
            "error": None,
        }

    except Exception as exc:
        return {
            "passed": False,
            "status_code": None,
            "wall_seconds": None,
            "total_elapsed_seconds": round(
                time.perf_counter()
                - started,
                3,
            ),
            "eval_count": 0,
            "tokens_per_second": 0.0,
            "done": False,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def run_ollama_batch(
    model: str,
    concurrency: int,
) -> dict[str, Any]:
    started = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:
        futures = [
            executor.submit(
                ollama_request,
                model,
                index + 1,
            )
            for index in range(concurrency)
        ]

        results = [
            future.result()
            for future in futures
        ]

    elapsed = (
        time.perf_counter()
        - started
    )

    successful = [
        item
        for item in results
        if item["passed"]
    ]

    latencies = [
        item["wall_seconds"]
        for item in successful
        if item["wall_seconds"] is not None
    ]

    token_rates = [
        item["tokens_per_second"]
        for item in successful
        if item["tokens_per_second"] > 0
    ]

    return {
        "concurrency": concurrency,
        "passed": len(successful) == concurrency,
        "successful_requests": len(
            successful
        ),
        "total_requests": concurrency,
        "batch_seconds": round(
            elapsed,
            3,
        ),
        "average_latency_seconds": round(
            mean(latencies),
            3,
        ) if latencies else None,
        "maximum_latency_seconds": round(
            max(latencies),
            3,
        ) if latencies else None,
        "average_tokens_per_second": round(
            mean(token_rates),
            3,
        ) if token_rates else 0.0,
        "requests_per_minute": round(
            (
                len(successful)
                / elapsed
                * 60
            )
            if elapsed > 0
            else 0,
            3,
        ),
        "results": results,
    }


def ollama_qualification() -> dict[str, Any]:
    model = select_ollama_model()

    if model is None:
        return {
            "available": False,
            "model": None,
            "batches": [],
            "maximum_qualified_concurrency": 0,
            "requests_per_minute": 0.0,
            "reason": (
                "No reachable local Ollama model was found."
            ),
        }

    batches = []

    for concurrency in [
        1,
        2,
    ]:
        batch = run_ollama_batch(
            model,
            concurrency,
        )

        batches.append(batch)

        if not batch["passed"]:
            break

        if (
            batch[
                "maximum_latency_seconds"
            ] is not None
            and batch[
                "maximum_latency_seconds"
            ] > 60
        ):
            break

    qualified = [
        batch
        for batch in batches
        if batch["passed"]
        and (
            batch[
                "maximum_latency_seconds"
            ] is not None
        )
        and batch[
            "maximum_latency_seconds"
        ] <= 60
    ]

    maximum_concurrency = max(
        (
            batch["concurrency"]
            for batch in qualified
        ),
        default=0,
    )

    best_rpm = max(
        (
            batch["requests_per_minute"]
            for batch in qualified
        ),
        default=0.0,
    )

    return {
        "available": True,
        "model": model,
        "predict_tokens": (
            OLLAMA_PREDICT_TOKENS
        ),
        "batches": batches,
        "maximum_qualified_concurrency": (
            maximum_concurrency
        ),
        "requests_per_minute": round(
            best_rpm,
            3,
        ),
        "external_provider_contacted": False,
    }


def memory_available_gib(
    stage2: dict[str, Any],
) -> float:
    return float(
        stage2.get(
            "hardware_discovery",
            {},
        ).get(
            "hardware",
            {},
        ).get(
            "memory",
            {},
        ).get(
            "available_gib",
            0,
        )
        or 0
    )


def capacity_projection(
    *,
    stage2: dict[str, Any],
    storage: dict[str, Any],
    ollama: dict[str, Any],
) -> dict[str, Any]:
    logical_cpus = int(
        stage2.get(
            "summary",
            {},
        ).get(
            "logical_cpus",
            1,
        )
        or 1
    )

    available_memory = (
        memory_available_gib(
            stage2
        )
    )

    thermal_score = float(
        stage2.get(
            "summary",
            {},
        ).get(
            "thermal_score",
            0,
        )
        or 0
    )

    random_iops = float(
        storage.get(
            "summary",
            {},
        ).get(
            "random_read_iops",
            0,
        )
        or 0
    )

    cpu_capacity = (
        logical_cpus * 8
    )

    memory_capacity = (
        available_memory * 2
    )

    storage_capacity = max(
        10,
        min(
            300,
            random_iops / 100,
        ),
    )

    thermal_factor = max(
        0.50,
        min(
            1.0,
            thermal_score / 100,
        ),
    )

    safe_non_ai_concurrent = math.floor(
        min(
            cpu_capacity,
            memory_capacity,
            storage_capacity,
        )
        * 0.60
        * thermal_factor
    )

    safe_non_ai_concurrent = max(
        10,
        safe_non_ai_concurrent,
    )

    ai_concurrency = int(
        ollama.get(
            "maximum_qualified_concurrency",
            0,
        )
        or 0
    )

    ai_requests_per_minute = float(
        ollama.get(
            "requests_per_minute",
            0,
        )
        or 0
    )

    safe_ai_simultaneous = max(
        0,
        math.floor(
            ai_concurrency * 0.75
        ),
    )

    if (
        ai_concurrency > 0
        and safe_ai_simultaneous == 0
    ):
        safe_ai_simultaneous = 1

    estimated_active_ai_users = math.floor(
        ai_requests_per_minute
        * 5
        * 0.50
    )

    if ollama.get("available"):
        safe_mixed_concurrent = min(
            safe_non_ai_concurrent,
            max(
                10,
                estimated_active_ai_users,
            ),
        )
    else:
        safe_mixed_concurrent = min(
            safe_non_ai_concurrent,
            10,
        )

    safe_mixed_concurrent = max(
        5,
        safe_mixed_concurrent,
    )

    estimated_registered_users_low = (
        safe_mixed_concurrent * 10
    )

    estimated_registered_users_high = (
        safe_mixed_concurrent * 20
    )

    assumptions = {
        "concurrency_ratio_low": 0.05,
        "concurrency_ratio_high": 0.10,
        "ai_request_frequency": (
            "one short AI request per active AI user "
            "approximately every five minutes"
        ),
        "safety_reserve": (
            "approximately 40 percent capacity reserve"
        ),
        "model_context": (
            "short benchmark prompt; real long-context "
            "prompts will reduce capacity"
        ),
    }

    return {
        "status": "PROVISIONAL",
        "safe_non_ai_simultaneous_users": (
            safe_non_ai_concurrent
        ),
        "safe_ai_simultaneous_requests": (
            safe_ai_simultaneous
        ),
        "estimated_active_ai_users": (
            estimated_active_ai_users
        ),
        "safe_mixed_simultaneous_users": (
            safe_mixed_concurrent
        ),
        "estimated_registered_user_range": {
            "low": (
                estimated_registered_users_low
            ),
            "high": (
                estimated_registered_users_high
            ),
        },
        "assumptions": assumptions,
        "confidence": (
            "LOW_TO_MODERATE"
        ),
        "upgrade_trigger_conditions": [
            (
                "Sustained CPU usage exceeds 70 percent "
                "during normal peak periods."
            ),
            (
                "Ollama queue wait exceeds 30 seconds."
            ),
            (
                "AI request latency exceeds 60 seconds "
                "at expected concurrency."
            ),
            (
                "Available RAM repeatedly falls below 16 GiB."
            ),
            (
                "NVMe latency or database latency increases "
                "under the real NeuroVest workload."
            ),
            (
                "More than one outage-sensitive production "
                "service depends on this single workstation."
            ),
        ],
        "not_a_production_guarantee": True,
        "requires_real_application_load_test": True,
    }


def render_text(
    report: dict[str, Any],
) -> str:
    storage = report["storage_qualification"]
    services = report["service_qualification"]
    ollama = report["ollama_qualification"]
    capacity = report["capacity_projection"]

    lines = []

    lines.append("=" * 80)
    lines.append("PHASE 136")
    lines.append("ACCELERATED INFRASTRUCTURE CAPACITY QUALIFICATION")
    lines.append("=" * 80)
    lines.append("")
    lines.append("COMPLETED")
    lines.append("Stage 3 — Storage Qualification")
    lines.append("Stage 4 — Local Service Qualification")
    lines.append("Stage 5 — Ollama Throughput Qualification")
    lines.append("Stage 6 — Provisional Capacity Projection")

    lines.append("")
    lines.append("STORAGE")
    lines.append(
        "Grade:                       "
        f"{storage['summary']['grade']}"
    )
    lines.append(
        "Sequential read:             "
        f"{storage['summary']['sequential_read_mib_per_second']} MiB/s"
    )
    lines.append(
        "Sequential write:            "
        f"{storage['summary']['sequential_write_mib_per_second']} MiB/s"
    )
    lines.append(
        "Random read IOPS:            "
        f"{storage['summary']['random_read_iops']}"
    )
    lines.append(
        "Random write IOPS:           "
        f"{storage['summary']['random_write_iops']}"
    )
    lines.append(
        "Temporary test file exists:  "
        f"{str(BENCHMARK_FILE.exists()).upper()}"
    )

    lines.append("")
    lines.append("LOCAL SERVICES")

    for name, probe in services[
        "probes"
    ].items():
        lines.append(
            f"- {name:<24} "
            f"port={probe['port']} "
            f"open={str(probe['open']).upper()}"
        )

    lines.append("")
    lines.append("OLLAMA")
    lines.append(
        "Available:                   "
        f"{str(ollama.get('available', False)).upper()}"
    )
    lines.append(
        "Model:                       "
        f"{ollama.get('model')}"
    )
    lines.append(
        "Qualified concurrency:       "
        f"{ollama.get('maximum_qualified_concurrency', 0)}"
    )
    lines.append(
        "Measured requests/minute:    "
        f"{ollama.get('requests_per_minute', 0)}"
    )

    lines.append("")
    lines.append("PROVISIONAL SAFE CAPACITY")
    lines.append(
        "Non-AI simultaneous users:   "
        f"{capacity['safe_non_ai_simultaneous_users']}"
    )
    lines.append(
        "AI requests at once:         "
        f"{capacity['safe_ai_simultaneous_requests']}"
    )
    lines.append(
        "Mixed simultaneous users:    "
        f"{capacity['safe_mixed_simultaneous_users']}"
    )
    lines.append(
        "Estimated registered users:  "
        f"{capacity['estimated_registered_user_range']['low']}"
        "–"
        f"{capacity['estimated_registered_user_range']['high']}"
    )
    lines.append(
        "Confidence:                  "
        f"{capacity['confidence']}"
    )

    lines.append("")
    lines.append("IMPORTANT")
    lines.append(
        "These numbers are provisional infrastructure estimates."
    )
    lines.append(
        "The real safe-user count requires Stage 7 to load-test "
        "the actual NeuroVest API and mixed workload."
    )

    lines.append("")
    lines.append("APPROVAL")
    lines.append("Deployment approved:         NO")
    lines.append("Live trading approved:       NO")

    lines.append("")
    lines.append("NEXT")
    lines.append(
        "Stage 7 — Real NeuroVest Bottleneck and Load Qualification"
    )

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main() -> int:
    started_at = datetime.now(UTC)

    stage2 = load_stage2()

    storage = storage_qualification()

    storage[
        "temporary_file_deleted"
    ] = not BENCHMARK_FILE.exists()

    services = service_qualification()
    ollama = ollama_qualification()

    capacity = capacity_projection(
        stage2=stage2,
        storage=storage,
        ollama=ollama,
    )

    completed_at = datetime.now(UTC)

    report = {
        "phase": 136,
        "stage": 6,
        "stage_name": (
            "Accelerated Capacity Projection"
        ),
        "completed_stages": [
            "hardware_and_platform_discovery",
            "thermal_qualification",
            "storage_qualification",
            "local_service_qualification",
            "ollama_throughput_qualification",
            "provisional_capacity_projection",
        ],
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
        "application_executed": False,
        "application_modified": False,
        "temporary_storage_benchmark_executed": True,
        "destructive_storage_test_executed": False,
        "external_network_test_executed": False,
        "cpu_governor_modified": False,
        "services_started": False,
        "services_stopped": False,
        "deployment_approved": False,
        "live_trading_approved": False,
        "stage2_baseline": {
            "thermal_grade": (
                stage2["summary"][
                    "thermal_grade"
                ]
            ),
            "thermal_score": (
                stage2["summary"][
                    "thermal_score"
                ]
            ),
            "load_peak_celsius": (
                stage2["summary"][
                    "load_peak_celsius"
                ]
            ),
        },
        "storage_qualification": storage,
        "service_qualification": services,
        "ollama_qualification": ollama,
        "capacity_projection": capacity,
    }

    timestamp = completed_at.strftime(
        "%Y%m%dT%H%M%S.%fZ"
    )

    history_json = (
        CAPACITY_HISTORY
        / f"{timestamp}.json"
    )

    history_text = (
        CAPACITY_HISTORY
        / f"{timestamp}.txt"
    )

    write_json_atomic(
        LATEST_REPORT,
        report,
    )

    write_json_atomic(
        history_json,
        report,
    )

    text = render_text(report)

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
    raise SystemExit(main())
