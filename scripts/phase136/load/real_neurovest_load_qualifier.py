#!/usr/bin/env python3

"""
Phase 136 Stage 7
Real NeuroVest Bottleneck and Load Qualification.

This stage load-tests the running local NeuroVest stack.

It does not:

- start NeuroVest automatically
- modify application code
- submit orders
- enable broker execution
- enable live trading
- invoke mutating API routes
- modify CPU governors
- contact external AI providers

Test profile:

- Discover safe GET routes through FastAPI OpenAPI.
- Skip path-parameter routes.
- Skip routes with required parameters.
- Deny execution, broker, order, admin-mutation, and live-trading routes.
- Test 10, 20, 30, 40, and 50 simultaneous virtual users.
- Run one bounded local Ollama worker during each level.
- Stop ramping after the first failed level.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
import os
import random
import shutil
import socket
import statistics
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]

AUDIT_ROOT = (
    ROOT
    / "runtime"
    / "infrastructure_audits"
)

CAPACITY_REPORT = (
    AUDIT_ROOT
    / "capacity"
    / "latest.json"
)

LOAD_DIRECTORY = (
    AUDIT_ROOT
    / "load"
)

LOAD_HISTORY_DIRECTORY = (
    AUDIT_ROOT
    / "history"
    / "load"
)

LATEST_JSON = (
    LOAD_DIRECTORY
    / "latest.json"
)

LATEST_TEXT = (
    LOAD_DIRECTORY
    / "latest.txt"
)

BACKEND_BASE_URL = os.environ.get(
    "NEUROVEST_BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

FRONTEND_BASE_URL = os.environ.get(
    "NEUROVEST_FRONTEND_URL",
    "http://127.0.0.1:3001",
).rstrip("/")

OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
).rstrip("/")

CONCURRENCY_LEVELS = [
    10,
    20,
    30,
    40,
    50,
]

LEVEL_DURATION_SECONDS = 15
REQUEST_TIMEOUT_SECONDS = 10
THINK_TIME_MIN_SECONDS = 0.10
THINK_TIME_MAX_SECONDS = 0.35

MAX_SAFE_ERROR_RATE_PERCENT = 1.0
MAX_SAFE_P95_MS = 1500.0
MAX_SAFE_P99_MS = 3000.0
MAX_SAFE_CPU_PERCENT = 75.0
MIN_SAFE_AVAILABLE_MEMORY_GIB = 8.0
MAX_SAFE_CPU_TEMPERATURE_C = 85.0

MAX_DISCOVERED_ROUTES = 10
AI_CONCURRENCY = 1
AI_OUTPUT_TOKENS = 32
AI_REQUEST_INTERVAL_SECONDS = 5.0

DENIED_ROUTE_KEYWORDS = {
    "live",
    "execute",
    "execution",
    "submit",
    "order",
    "broker",
    "trade",
    "admin",
    "delete",
    "remove",
    "shutdown",
    "restart",
    "reconcile",
    "mutation",
    "emergency",
    "unlock",
    "enable",
    "disable",
    "connect",
    "disconnect",
    "oauth",
    "token",
}

PREFERRED_ROUTE_KEYWORDS = [
    "health",
    "status",
    "readiness",
    "market",
    "quote",
    "portfolio",
    "position",
    "analytics",
    "research",
    "strategy",
    "risk",
    "watchlist",
    "journal",
]


class LoadQualificationFailure(RuntimeError):
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


def percentile(
    values: list[float],
    percent: float,
) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)

    position = (
        len(ordered) - 1
    ) * percent

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    lower_value = ordered[lower]
    upper_value = ordered[upper]

    return (
        lower_value
        + (
            upper_value
            - lower_value
        )
        * (
            position
            - lower
        )
    )


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


def http_request(
    *,
    url: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/json",
        "User-Agent": "Phase136-Load-Qualifier/1.0",
    }

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

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            body = response.read(
                2 * 1024 * 1024
            )

            elapsed_ms = (
                time.perf_counter()
                - started
            ) * 1000

            return {
                "passed": (
                    200
                    <= response.status
                    < 400
                ),
                "status_code": response.status,
                "latency_ms": round(
                    elapsed_ms,
                    3,
                ),
                "bytes_received": len(body),
                "error": None,
            }

    except urllib.error.HTTPError as exc:
        elapsed_ms = (
            time.perf_counter()
            - started
        ) * 1000

        return {
            "passed": False,
            "status_code": exc.code,
            "latency_ms": round(
                elapsed_ms,
                3,
            ),
            "bytes_received": 0,
            "error": (
                f"HTTPError: {exc}"
            ),
        }

    except Exception as exc:
        elapsed_ms = (
            time.perf_counter()
            - started
        ) * 1000

        return {
            "passed": False,
            "status_code": None,
            "latency_ms": round(
                elapsed_ms,
                3,
            ),
            "bytes_received": 0,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def get_json(
    url: str,
    timeout: int = 10,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": "Phase136-Discovery/1.0",
        },
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        return json.loads(
            response.read().decode(
                "utf-8"
            )
        )


def load_capacity_baseline() -> dict[str, Any]:
    if not CAPACITY_REPORT.is_file():
        raise LoadQualificationFailure(
            "Phase 136 Stage 6 capacity report is missing."
        )

    payload = json.loads(
        CAPACITY_REPORT.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("phase") != 136:
        raise LoadQualificationFailure(
            "Capacity report does not belong to Phase 136."
        )

    if payload.get("stage") != 6:
        raise LoadQualificationFailure(
            "Latest capacity report is not Stage 6."
        )

    return payload


def validate_runtime() -> dict[str, Any]:
    backend = urllib.parse.urlparse(
        BACKEND_BASE_URL
    )

    frontend = urllib.parse.urlparse(
        FRONTEND_BASE_URL
    )

    backend_port = (
        backend.port
        or (
            443
            if backend.scheme == "https"
            else 80
        )
    )

    frontend_port = (
        frontend.port
        or (
            443
            if frontend.scheme == "https"
            else 80
        )
    )

    backend_open = port_open(
        backend.hostname or "127.0.0.1",
        backend_port,
    )

    frontend_open = port_open(
        frontend.hostname or "127.0.0.1",
        frontend_port,
    )

    if not backend_open:
        raise LoadQualificationFailure(
            "NeuroVest backend is not reachable at "
            f"{BACKEND_BASE_URL}. Start the existing backend "
            "using the repository's established startup command, "
            "then rerun this Stage 7 command."
        )

    return {
        "backend_url": BACKEND_BASE_URL,
        "backend_open": backend_open,
        "frontend_url": FRONTEND_BASE_URL,
        "frontend_open": frontend_open,
        "ollama_open": port_open(
            "127.0.0.1",
            11434,
        ),
    }


def route_denied(
    path: str,
    operation: dict[str, Any],
) -> bool:
    text = " ".join(
        [
            path,
            str(operation.get("summary", "")),
            str(operation.get("operationId", "")),
            " ".join(
                str(item)
                for item in operation.get(
                    "tags",
                    [],
                )
            ),
        ]
    ).lower()

    return any(
        keyword in text
        for keyword in DENIED_ROUTE_KEYWORDS
    )


def route_has_path_parameters(
    path: str,
) -> bool:
    return (
        "{"
        in path
        or "}"
        in path
    )


def route_has_required_parameters(
    operation: dict[str, Any],
) -> bool:
    parameters = operation.get(
        "parameters",
        [],
    )

    for parameter in parameters:
        if parameter.get(
            "required",
            False,
        ):
            return True

    return False


def discover_safe_routes() -> dict[str, Any]:
    openapi_url = (
        f"{BACKEND_BASE_URL}/openapi.json"
    )

    try:
        schema = get_json(
            openapi_url
        )
    except Exception as exc:
        fallback_routes = [
            "/health",
            "/status",
        ]

        working = []

        for route in fallback_routes:
            result = http_request(
                url=(
                    f"{BACKEND_BASE_URL}"
                    f"{route}"
                )
            )

            if result["passed"]:
                working.append(route)

        if not working:
            raise LoadQualificationFailure(
                "OpenAPI discovery failed and no safe fallback "
                f"route responded. Discovery error: {exc}"
            )

        return {
            "openapi_available": False,
            "openapi_url": openapi_url,
            "routes": working,
            "candidate_count": len(
                fallback_routes
            ),
            "selected_count": len(
                working
            ),
            "discovery_error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }

    paths = schema.get(
        "paths",
        {},
    )

    candidates = []

    for path, methods in paths.items():
        if not isinstance(
            methods,
            dict,
        ):
            continue

        operation = methods.get(
            "get"
        )

        if not isinstance(
            operation,
            dict,
        ):
            continue

        if route_has_path_parameters(
            path
        ):
            continue

        if route_has_required_parameters(
            operation
        ):
            continue

        if route_denied(
            path,
            operation,
        ):
            continue

        priority = 100

        lowered = path.lower()

        for index, keyword in enumerate(
            PREFERRED_ROUTE_KEYWORDS
        ):
            if keyword in lowered:
                priority = index
                break

        candidates.append(
            {
                "path": path,
                "priority": priority,
                "summary": operation.get(
                    "summary"
                ),
                "operation_id": operation.get(
                    "operationId"
                ),
            }
        )

    candidates.sort(
        key=lambda item: (
            item["priority"],
            item["path"],
        )
    )

    working = []

    for candidate in candidates:
        route = candidate["path"]

        result = http_request(
            url=(
                f"{BACKEND_BASE_URL}"
                f"{route}"
            )
        )

        if result["passed"]:
            working.append(
                {
                    **candidate,
                    "probe": result,
                }
            )

        if len(working) >= (
            MAX_DISCOVERED_ROUTES
        ):
            break

    if not working:
        raise LoadQualificationFailure(
            "OpenAPI was available, but no safe parameter-free "
            "GET route passed its initial probe."
        )

    return {
        "openapi_available": True,
        "openapi_url": openapi_url,
        "candidate_count": len(
            candidates
        ),
        "selected_count": len(
            working
        ),
        "routes": [
            item["path"]
            for item in working
        ],
        "route_details": working,
    }


def read_cpu_snapshot() -> tuple[
    int,
    int,
]:
    text = Path(
        "/proc/stat"
    ).read_text(
        encoding="utf-8"
    )

    first = text.splitlines()[0]
    parts = first.split()[1:]

    values = [
        int(value)
        for value in parts
    ]

    idle = (
        values[3]
        + (
            values[4]
            if len(values) > 4
            else 0
        )
    )

    total = sum(values)

    return (
        idle,
        total,
    )


def calculate_cpu_percent(
    before: tuple[int, int],
    after: tuple[int, int],
) -> float:
    idle_delta = (
        after[0]
        - before[0]
    )

    total_delta = (
        after[1]
        - before[1]
    )

    if total_delta <= 0:
        return 0.0

    active_delta = (
        total_delta
        - idle_delta
    )

    return max(
        0.0,
        min(
            100.0,
            active_delta
            / total_delta
            * 100,
        ),
    )


def available_memory_gib() -> float:
    meminfo = Path(
        "/proc/meminfo"
    ).read_text(
        encoding="utf-8"
    )

    for line in meminfo.splitlines():
        if line.startswith(
            "MemAvailable:"
        ):
            kilobytes = int(
                line.split()[1]
            )

            return (
                kilobytes
                / 1024
                / 1024
            )

    return 0.0


def cpu_temperature_c() -> float | None:
    if shutil.which("sensors") is None:
        return None

    try:
        result = subprocess.run(
            [
                "sensors",
                "-j",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )

        if result.returncode != 0:
            return None

        payload = json.loads(
            result.stdout
        )

        for chip_name, chip_data in payload.items():
            if not isinstance(
                chip_data,
                dict,
            ):
                continue

            normalized_chip = (
                str(chip_name).lower()
            )

            if "k10temp" not in normalized_chip:
                continue

            for feature_name, feature_data in chip_data.items():
                if (
                    str(feature_name).lower()
                    != "tctl"
                ):
                    continue

                if not isinstance(
                    feature_data,
                    dict,
                ):
                    continue

                for key, value in feature_data.items():
                    if (
                        str(key).endswith(
                            "_input"
                        )
                        and isinstance(
                            value,
                            (int, float),
                        )
                    ):
                        return float(value)

    except Exception:
        return None

    return None


class SystemMonitor:
    def __init__(
        self,
    ) -> None:
        self.stop_event = threading.Event()
        self.samples: list[
            dict[str, Any]
        ] = []
        self.thread: (
            threading.Thread
            | None
        ) = None

    def start(self) -> None:
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

        if self.thread is not None:
            self.thread.join(
                timeout=5
            )

    def _run(self) -> None:
        previous_cpu = read_cpu_snapshot()

        while not self.stop_event.wait(
            1.0
        ):
            current_cpu = read_cpu_snapshot()

            cpu_percent = calculate_cpu_percent(
                previous_cpu,
                current_cpu,
            )

            previous_cpu = current_cpu

            self.samples.append(
                {
                    "timestamp": (
                        datetime.now(
                            UTC
                        ).isoformat()
                    ),
                    "cpu_percent": round(
                        cpu_percent,
                        2,
                    ),
                    "available_memory_gib": round(
                        available_memory_gib(),
                        2,
                    ),
                    "cpu_temperature_celsius": (
                        cpu_temperature_c()
                    ),
                }
            )


def select_ollama_model() -> str | None:
    try:
        payload = get_json(
            f"{OLLAMA_BASE_URL}/api/tags"
        )
    except Exception:
        return None

    models = payload.get(
        "models",
        [],
    )

    if not models:
        return None

    return (
        models[0].get("name")
        or None
    )


def run_ollama_request(
    model: str,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": (
            "Reply with one short sentence confirming "
            "the NeuroVest load test is active."
        ),
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": (
                AI_OUTPUT_TOKENS
            ),
        },
    }

    result = http_request(
        url=(
            f"{OLLAMA_BASE_URL}"
            "/api/generate"
        ),
        method="POST",
        payload=payload,
        timeout=120,
    )

    return result


class AIBackgroundLoad:
    def __init__(
        self,
        enabled: bool,
    ) -> None:
        self.enabled = enabled
        self.model = (
            select_ollama_model()
            if enabled
            else None
        )

        self.stop_event = threading.Event()
        self.thread: (
            threading.Thread
            | None
        ) = None

        self.results: list[
            dict[str, Any]
        ] = []

    def start(self) -> None:
        if not self.model:
            return

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

        if self.thread is not None:
            self.thread.join(
                timeout=125
            )

    def _run(self) -> None:
        while not self.stop_event.is_set():
            result = run_ollama_request(
                self.model
            )

            self.results.append(result)

            if self.stop_event.wait(
                AI_REQUEST_INTERVAL_SECONDS
            ):
                break


def virtual_user(
    *,
    routes: list[str],
    stop_event: threading.Event,
    user_id: int,
) -> list[dict[str, Any]]:
    random_generator = random.Random(
        user_id
    )

    results = []

    while not stop_event.is_set():
        route = random_generator.choice(
            routes
        )

        result = http_request(
            url=(
                f"{BACKEND_BASE_URL}"
                f"{route}"
            )
        )

        result["route"] = route
        result["user_id"] = user_id

        results.append(result)

        sleep_duration = (
            random_generator.uniform(
                THINK_TIME_MIN_SECONDS,
                THINK_TIME_MAX_SECONDS,
            )
        )

        if stop_event.wait(
            sleep_duration
        ):
            break

    return results


def summarize_system_samples(
    samples: list[dict[str, Any]],
) -> dict[str, Any]:
    cpu_values = [
        sample["cpu_percent"]
        for sample in samples
    ]

    memory_values = [
        sample[
            "available_memory_gib"
        ]
        for sample in samples
    ]

    temperature_values = [
        sample[
            "cpu_temperature_celsius"
        ]
        for sample in samples
        if sample[
            "cpu_temperature_celsius"
        ] is not None
    ]

    return {
        "sample_count": len(samples),
        "average_cpu_percent": round(
            statistics.mean(
                cpu_values
            ),
            2,
        ) if cpu_values else 0.0,
        "maximum_cpu_percent": round(
            max(cpu_values),
            2,
        ) if cpu_values else 0.0,
        "minimum_available_memory_gib": round(
            min(memory_values),
            2,
        ) if memory_values else 0.0,
        "maximum_cpu_temperature_celsius": (
            round(
                max(
                    temperature_values
                ),
                2,
            )
            if temperature_values
            else None
        ),
    }


def run_load_level(
    *,
    concurrency: int,
    routes: list[str],
    ollama_enabled: bool,
) -> dict[str, Any]:
    stop_event = threading.Event()

    monitor = SystemMonitor()
    ai_load = AIBackgroundLoad(
        enabled=ollama_enabled
    )

    started = time.perf_counter()

    monitor.start()
    ai_load.start()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:
        futures = [
            executor.submit(
                virtual_user,
                routes=routes,
                stop_event=stop_event,
                user_id=user_id,
            )
            for user_id in range(
                1,
                concurrency + 1,
            )
        ]

        time.sleep(
            LEVEL_DURATION_SECONDS
        )

        stop_event.set()

        worker_results = [
            future.result(
                timeout=REQUEST_TIMEOUT_SECONDS
                + 5
            )
            for future in futures
        ]

    ai_load.stop()
    monitor.stop()

    elapsed = (
        time.perf_counter()
        - started
    )

    requests = [
        item
        for worker in worker_results
        for item in worker
    ]

    passed_requests = [
        item
        for item in requests
        if item["passed"]
    ]

    failed_requests = [
        item
        for item in requests
        if not item["passed"]
    ]

    latencies = [
        item["latency_ms"]
        for item in requests
    ]

    total_requests = len(
        requests
    )

    error_rate = (
        len(failed_requests)
        / total_requests
        * 100
        if total_requests
        else 100.0
    )

    system_summary = (
        summarize_system_samples(
            monitor.samples
        )
    )

    p50 = percentile(
        latencies,
        0.50,
    )

    p95 = percentile(
        latencies,
        0.95,
    )

    p99 = percentile(
        latencies,
        0.99,
    )

    ai_passed = sum(
        1
        for item in ai_load.results
        if item["passed"]
    )

    ai_failed = (
        len(ai_load.results)
        - ai_passed
    )

    checks = {
        "requests_completed": (
            total_requests > 0
        ),
        "error_rate": (
            error_rate
            <= MAX_SAFE_ERROR_RATE_PERCENT
        ),
        "p95_latency": (
            p95
            <= MAX_SAFE_P95_MS
        ),
        "p99_latency": (
            p99
            <= MAX_SAFE_P99_MS
        ),
        "cpu_reserve": (
            system_summary[
                "average_cpu_percent"
            ]
            <= MAX_SAFE_CPU_PERCENT
        ),
        "memory_reserve": (
            system_summary[
                "minimum_available_memory_gib"
            ]
            >= MIN_SAFE_AVAILABLE_MEMORY_GIB
        ),
        "temperature": (
            system_summary[
                "maximum_cpu_temperature_celsius"
            ] is None
            or system_summary[
                "maximum_cpu_temperature_celsius"
            ]
            <= MAX_SAFE_CPU_TEMPERATURE_C
        ),
        "ai_background": (
            not ollama_enabled
            or ai_failed == 0
        ),
    }

    passed = all(
        checks.values()
    )

    route_counts: dict[str, int] = {}

    for item in requests:
        route = item["route"]

        route_counts[route] = (
            route_counts.get(
                route,
                0,
            )
            + 1
        )

    error_samples = [
        {
            "route": item["route"],
            "status_code": item[
                "status_code"
            ],
            "error": item["error"],
            "latency_ms": item[
                "latency_ms"
            ],
        }
        for item in failed_requests[:20]
    ]

    return {
        "concurrency": concurrency,
        "duration_seconds": round(
            elapsed,
            3,
        ),
        "passed": passed,
        "checks": checks,
        "request_metrics": {
            "total_requests": total_requests,
            "successful_requests": len(
                passed_requests
            ),
            "failed_requests": len(
                failed_requests
            ),
            "error_rate_percent": round(
                error_rate,
                3,
            ),
            "requests_per_second": round(
                total_requests
                / elapsed
                if elapsed > 0
                else 0,
                3,
            ),
            "average_latency_ms": round(
                statistics.mean(
                    latencies
                ),
                3,
            ) if latencies else 0.0,
            "p50_latency_ms": round(
                p50,
                3,
            ),
            "p95_latency_ms": round(
                p95,
                3,
            ),
            "p99_latency_ms": round(
                p99,
                3,
            ),
            "maximum_latency_ms": round(
                max(latencies),
                3,
            ) if latencies else 0.0,
            "bytes_received": sum(
                item["bytes_received"]
                for item in requests
            ),
        },
        "system_metrics": system_summary,
        "ai_metrics": {
            "enabled": ollama_enabled,
            "model": ai_load.model,
            "total_requests": len(
                ai_load.results
            ),
            "successful_requests": (
                ai_passed
            ),
            "failed_requests": ai_failed,
            "average_latency_ms": (
                round(
                    statistics.mean(
                        item["latency_ms"]
                        for item in ai_load.results
                    ),
                    3,
                )
                if ai_load.results
                else None
            ),
        },
        "route_request_counts": dict(
            sorted(
                route_counts.items()
            )
        ),
        "error_samples": error_samples,
    }


def determine_capacity(
    levels: list[dict[str, Any]],
) -> dict[str, Any]:
    passed_levels = [
        level
        for level in levels
        if level["passed"]
    ]

    failed_levels = [
        level
        for level in levels
        if not level["passed"]
    ]

    highest_passed = max(
        (
            level["concurrency"]
            for level in passed_levels
        ),
        default=0,
    )

    first_failed = min(
        (
            level["concurrency"]
            for level in failed_levels
        ),
        default=None,
    )

    safe_launch_concurrency = math.floor(
        highest_passed * 0.70
    )

    if (
        highest_passed > 0
        and safe_launch_concurrency < 5
    ):
        safe_launch_concurrency = 5

    if safe_launch_concurrency > 0:
        registered_low = (
            safe_launch_concurrency
            * 10
        )

        registered_high = (
            safe_launch_concurrency
            * 20
        )
    else:
        registered_low = 0
        registered_high = 0

    if highest_passed >= 50:
        confidence = "MODERATE"
        status = (
            "QUALIFIED_TO_TEST_ABOVE_50"
        )
    elif highest_passed >= 30:
        confidence = "MODERATE"
        status = (
            "QUALIFIED_FOR_SMALL_BETA"
        )
    elif highest_passed >= 10:
        confidence = (
            "LOW_TO_MODERATE"
        )
        status = (
            "QUALIFIED_FOR_CONTROLLED_ALPHA"
        )
    else:
        confidence = "LOW"
        status = "NOT_QUALIFIED"

    return {
        "status": status,
        "confidence": confidence,
        "highest_tested_passing_concurrency": (
            highest_passed
        ),
        "first_failing_concurrency": (
            first_failed
        ),
        "recommended_safe_launch_concurrency": (
            safe_launch_concurrency
        ),
        "estimated_registered_user_range": {
            "low": registered_low,
            "high": registered_high,
        },
        "safety_reserve_percent": 30,
        "qualification_scope": (
            "read-only NeuroVest GET routes with one bounded "
            "local Ollama background stream"
        ),
        "not_a_production_guarantee": True,
    }


def render_text(
    report: dict[str, Any],
) -> str:
    capacity = report[
        "measured_capacity"
    ]

    lines = []

    lines.append("=" * 80)
    lines.append("PHASE 136")
    lines.append("REAL NEUROVEST BOTTLENECK AND LOAD QUALIFICATION")
    lines.append("=" * 80)

    lines.append("")
    lines.append("RUNTIME")
    lines.append(
        "Backend:                     "
        f"{report['runtime']['backend_url']}"
    )
    lines.append(
        "Frontend open:               "
        f"{str(report['runtime']['frontend_open']).upper()}"
    )
    lines.append(
        "Ollama open:                 "
        f"{str(report['runtime']['ollama_open']).upper()}"
    )

    lines.append("")
    lines.append("SAFE ROUTES")

    for route in report[
        "route_discovery"
    ]["routes"]:
        lines.append(
            f"- {route}"
        )

    lines.append("")
    lines.append("LOAD LEVELS")

    for level in report[
        "load_levels"
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
            f"ram_min={system['minimum_available_memory_gib']}GiB"
        )

    lines.append("")
    lines.append("MEASURED CAPACITY")
    lines.append(
        "Status:                      "
        f"{capacity['status']}"
    )
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
        "Confidence:                  "
        f"{capacity['confidence']}"
    )

    lines.append("")
    lines.append("SAFETY THRESHOLDS")
    lines.append(
        "Maximum error rate:          "
        f"{MAX_SAFE_ERROR_RATE_PERCENT}%"
    )
    lines.append(
        "Maximum p95 latency:         "
        f"{MAX_SAFE_P95_MS}ms"
    )
    lines.append(
        "Maximum average CPU:         "
        f"{MAX_SAFE_CPU_PERCENT}%"
    )
    lines.append(
        "Minimum available memory:    "
        f"{MIN_SAFE_AVAILABLE_MEMORY_GIB}GiB"
    )
    lines.append(
        "Maximum CPU temperature:     "
        f"{MAX_SAFE_CPU_TEMPERATURE_C}°C"
    )

    lines.append("")
    lines.append("APPROVAL")
    lines.append("Deployment approved:         NO")
    lines.append("Live trading approved:       NO")

    lines.append("")
    lines.append("NEXT")
    lines.append(
        "Stage 8 — Bottleneck Prediction and Upgrade Trigger Plan"
    )

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main() -> int:
    started_at = datetime.now(
        UTC
    )

    baseline = load_capacity_baseline()
    runtime = validate_runtime()
    discovery = discover_safe_routes()

    routes = discovery["routes"]

    load_levels = []

    for concurrency in (
        CONCURRENCY_LEVELS
    ):
        level = run_load_level(
            concurrency=concurrency,
            routes=routes,
            ollama_enabled=runtime[
                "ollama_open"
            ],
        )

        load_levels.append(level)

        if not level["passed"]:
            break

    measured_capacity = (
        determine_capacity(
            load_levels
        )
    )

    completed_at = datetime.now(
        UTC
    )

    report = {
        "phase": 136,
        "stage": 7,
        "stage_name": (
            "Real NeuroVest Bottleneck and Load Qualification"
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
        "configuration": {
            "concurrency_levels": (
                CONCURRENCY_LEVELS
            ),
            "level_duration_seconds": (
                LEVEL_DURATION_SECONDS
            ),
            "request_timeout_seconds": (
                REQUEST_TIMEOUT_SECONDS
            ),
            "ai_concurrency": (
                AI_CONCURRENCY
            ),
            "maximum_error_rate_percent": (
                MAX_SAFE_ERROR_RATE_PERCENT
            ),
            "maximum_p95_latency_ms": (
                MAX_SAFE_P95_MS
            ),
            "maximum_p99_latency_ms": (
                MAX_SAFE_P99_MS
            ),
            "maximum_average_cpu_percent": (
                MAX_SAFE_CPU_PERCENT
            ),
            "minimum_available_memory_gib": (
                MIN_SAFE_AVAILABLE_MEMORY_GIB
            ),
            "maximum_cpu_temperature_celsius": (
                MAX_SAFE_CPU_TEMPERATURE_C
            ),
        },
        "stage6_baseline": {
            "provisional_safe_mixed_users": (
                baseline[
                    "capacity_projection"
                ][
                    "safe_mixed_simultaneous_users"
                ]
            ),
            "provisional_registered_users": (
                baseline[
                    "capacity_projection"
                ][
                    "estimated_registered_user_range"
                ]
            ),
            "storage_grade": (
                baseline[
                    "storage_qualification"
                ][
                    "summary"
                ][
                    "grade"
                ]
            ),
            "ollama_concurrency": (
                baseline[
                    "ollama_qualification"
                ][
                    "maximum_qualified_concurrency"
                ]
            ),
        },
        "runtime": runtime,
        "route_discovery": discovery,
        "load_levels": load_levels,
        "measured_capacity": measured_capacity,
        "limitations": [
            (
                "Only safe parameter-free GET routes were tested."
            ),
            (
                "Authenticated per-user routes may have different performance."
            ),
            (
                "Database writes, paper orders, WebSockets, streaming "
                "market data, and long-context AI prompts require later "
                "scenario-specific tests."
            ),
            (
                "Registered-user estimates assume approximately "
                "5 to 10 percent simultaneous activity."
            ),
        ],
    }

    timestamp = completed_at.strftime(
        "%Y%m%dT%H%M%S.%fZ"
    )

    history_json = (
        LOAD_HISTORY_DIRECTORY
        / f"{timestamp}.json"
    )

    history_text = (
        LOAD_HISTORY_DIRECTORY
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

    text = render_text(
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

    except LoadQualificationFailure as exc:
        print("=" * 80)
        print("PHASE 136 STAGE 7 BLOCKED")
        print("=" * 80)
        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )
        print()
        print(
            "No load qualification result was generated."
        )
        print(
            "Deployment remains unapproved."
        )
        print(
            "Live trading remains unapproved."
        )
        print("=" * 80)

        raise SystemExit(1)
