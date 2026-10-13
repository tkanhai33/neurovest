from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUAL = ROOT / "runtime/qualification"
INDEX = QUAL / "neuro_awareness_v37_active/evidence_index.json"

FOUNDATION = QUAL / (
    "neuro_v48_v411_evidence_foundation_20261013T022317Z"
)
EXECUTION = QUAL / (
    "neuro_v417_v422_execution_20261013T023557Z"
)
REAL = QUAL / (
    "neuro_v429_v434_real_qualification_20261013T024243Z"
)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + "\n"
    ).encode()

def require(condition, message):
    if not condition:
        raise RuntimeError("STOP: " + message)

def evidence(folder):
    require(folder.is_dir(), f"Missing evidence: {folder}")
    manifest = json.loads(
        (folder / "artifact_hashes.json").read_bytes()
    )
    result = {}

    for name, expected in manifest.items():
        require(
            isinstance(name, str)
            and name.endswith(".json")
            and Path(name).name == name,
            "Unsafe evidence manifest entry",
        )
        path = folder / name
        require(
            path.is_file()
            and not path.is_symlink()
            and sha(path.read_bytes()) == expected,
            "Evidence hash mismatch: " + name,
        )
        result[name] = json.loads(path.read_bytes())

    return result


def atomic(path, value):
    """Atomically write a JSON qualification artifact."""
    raw = encode(value)

    fd, temporary = tempfile.mkstemp(
        prefix=".neuro_v440_r2_",
        dir=path.parent,
    )

    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())

        os.chmod(temporary, 0o600)
        os.replace(temporary, path)

    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

checks = {}
details = {}

def check(name, success, description=""):
    checks[name] = bool(success)
    print(
        f"{name}={'PASS' if success else 'FAIL'}",
        description,
        flush=True,
    )

print("=" * 76)
print("NEURO V4.35–V4.40 — FINAL OFFLINE QUALIFICATION")
print("=" * 76)

# V4.35: Frozen source verification.

fingerprints = json.loads(
    INDEX.read_bytes()
)["source_fingerprints"]

require(len(fingerprints) == 419, "Source count changed")

for relative, expected in fingerprints.items():
    path = ROOT / relative
    require(
        path.is_file()
        and not path.is_symlink()
        and sha(path.read_bytes()) == expected,
        "Source mismatch: " + relative,
    )

check("FROZEN_SOURCE_419", True)

foundation = evidence(FOUNDATION)
previous = evidence(EXECUTION)
real = evidence(REAL)

check("PREVIOUS_EVIDENCE_HASHES", True)

fixture = foundation["market_fixtures.json"]

require(
    fixture["provenance"] == "SYNTHETIC_OFFLINE",
    "Unexpected fixture provenance",
)

# V4.36: Actual DTO construction and actual evaluator execution.
# Runs in a separate interpreter with network socket connections
# disabled before application imports.

worker = r'''
import contextlib
import importlib
import io
import json
import math
import socket
import sys
from datetime import datetime, timedelta, timezone

payload = json.load(sys.stdin)
out = {
    "dto": {},
    "registry": {},
    "evaluators": [],
    "aggregation": {},
}

def no_network(*args, **kwargs):
    raise RuntimeError("NEURO_OFFLINE_NETWORK_FORBIDDEN")

socket.socket.connect = no_network
socket.socket.connect_ex = no_network
socket.socket.connect = no_network
socket.create_connection = no_network

try:
    import urllib.request
    urllib.request.urlopen = no_network
except ImportError:
    pass

def safe_import(name):
    with contextlib.redirect_stdout(io.StringIO()):
        return importlib.import_module(name)

def failure(exc):
    return {
        "type": type(exc).__name__,
        "message": str(exc)[:180],
    }

symbol = "NVTESTA"
base = payload["symbols"]["NVTEST_A"]
now = datetime.now(timezone.utc)

# Actual production DTOs. Use a validator-compatible symbol.

try:
    dto = safe_import("backend.app.stacks.market_data.dto")
    Bar = dto.HistoricalBar
    Request = dto.HistoricalBarsRequest
    Result = dto.HistoricalBarsResult

    request = Request(
        symbol=symbol,
        start=datetime(2026, 9, 1, tzinfo=timezone.utc),
        end=datetime(2026, 10, 5, tzinfo=timezone.utc),
        interval="1d",
        adjusted=True,
        limit=5,
    )

    import inspect

    allowed = set(inspect.signature(Bar).parameters)
    rows = []

    for item in base:
        options = {
            "symbol": symbol,
            "timestamp": datetime.fromisoformat(
                item["date"] + "T00:00:00+00:00"
            ),
            "interval": "1d",
            "open": item["open"],
            "high": item["high"],
            "low": item["low"],
            "close": item["close"],
            "volume": item["volume"],
            "provider": "offline_fixture",
            "adjusted": True,
        }
        rows.append(
            Bar(**{
                k: v for k, v in options.items()
                if k in allowed
            })
        )

    result = Result(
        request=request,
        provider="offline_fixture",
        bars=tuple(rows),
        fetched_at=now,
    )

    out["dto"]["positive"] = (
        isinstance(request, Request)
        and len(result.bars) == 5
        and all(isinstance(x, Bar) for x in result.bars)
    )

    out["dto"]["normalized_symbol"] = request.symbol

    negatives = {}

    for name, bad in (
        ("empty", ""),
        ("underscore", "NVTEST_A"),
    ):
        try:
            Request(
                symbol=bad,
                start=datetime(
                    2026, 9, 1, tzinfo=timezone.utc
                ),
                end=datetime(
                    2026, 10, 5, tzinfo=timezone.utc
                ),
            )
            negatives[name] = False
        except ValueError:
            negatives[name] = True

    out["dto"]["negative_cases"] = negatives

    try:
        Result(
            request=request,
            provider="wrong_provider",
            bars=tuple(rows),
            fetched_at=now,
        )
        out["dto"]["provider_mismatch_rejected"] = False
    except ValueError:
        out["dto"]["provider_mismatch_rejected"] = True

except Exception as exc:
    out["dto"]["error"] = failure(exc)

# Actual registered V4 evaluators on 260 synthetic bars.
# Check deterministic output structure across two executions.

try:
    family = safe_import(
        "backend.app.stacks.strategy.evaluators."
        "bulk_indicator_family_v4"
    )
    aggregate_module = safe_import(
        "backend.app.stacks.strategy.evaluators."
        "bulk_indicator_aggregation_v4"
    )

    registry = family.BULK_OFFLINE_EVALUATORS_V4
    out["registry"]["count"] = len(registry)

    bars = []

    for i in range(260):
        source = base[i % len(base)]
        close = float(source["close"]) * (1 + i * 0.0001)

        bars.append({
            "symbol": symbol,
            "timestamp": (
                datetime(2025, 1, 1, tzinfo=timezone.utc)
                + timedelta(days=i)
            ).isoformat(),
            "open": close - 0.3,
            "high": close + 1.2,
            "low": close - 1.4,
            "close": close,
            "volume": 100000 + i * 10,
            "interval": "1d",
            "provider": "offline_fixture",
        })

    data = tuple(bars)

    def invoke(func):
        with contextlib.redirect_stdout(io.StringIO()):
            return func(data)

    for name, func in registry.items():
        entry = {"name": str(name)}

        try:
            first = invoke(func)
            second = invoke(func)

            entry["returned_twice"] = True
            entry["result_type"] = type(first).__name__
            entry["repeatable"] = (
                type(first) is type(second)
                and repr(first) == repr(second)
            )
            entry["result_repr_length"] = len(repr(first))

            # Repr equivalence is repeatability evidence,
            # not a correctness oracle.
        except Exception as exc:
            entry["returned_twice"] = False
            entry["repeatable"] = False
            entry["error"] = failure(exc)

        out["evaluators"].append(entry)

    try:
        first = invoke(
            aggregate_module.evaluate_and_aggregate_v4
        )
        second = invoke(
            aggregate_module.evaluate_and_aggregate_v4
        )

        out["aggregation"] = {
            "returned_twice": True,
            "repeatable": repr(first) == repr(second),
            "result_type": type(first).__name__,
            "result_repr_length": len(repr(first)),
        }
    except Exception as exc:
        out["aggregation"] = {
            "returned_twice": False,
            "error": failure(exc),
        }

except Exception as exc:
    out["registry"]["error"] = failure(exc)

print(json.dumps(out, sort_keys=True))
'''

environment = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "HOME": str(ROOT),
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONNOUSERSITE": "1",
    "PYTHONPATH": str(ROOT),
}

try:
    completed = subprocess.run(
        [sys.executable, "-B", "-c", worker],
        input=json.dumps({
            "symbols": fixture["symbols"],
        }),
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        env=environment,
        timeout=90,
        check=False,
    )

    require(
        completed.returncode == 0,
        "Worker failed: " + completed.stderr[-300:],
    )

    runtime = json.loads(completed.stdout)

except (
    subprocess.TimeoutExpired,
    json.JSONDecodeError,
) as exc:
    runtime = {
        "dto": {"error": type(exc).__name__},
        "registry": {"error": type(exc).__name__},
        "evaluators": [],
        "aggregation": {},
    }

dto = runtime["dto"]
registry = runtime["registry"]
evaluators = runtime["evaluators"]
aggregation = runtime["aggregation"]

check("REAL_DTO_INSTANCES", dto.get("positive") is True)

check(
    "DTO_INVALID_SYMBOL_REJECTION",
    dto.get("negative_cases", {}).get("empty") is True
    and dto.get("negative_cases", {}).get("underscore") is True,
)

check(
    "DTO_PROVIDER_MISMATCH_REJECTION",
    dto.get("provider_mismatch_rejected") is True,
)

check(
    "REAL_V4_REGISTRY_15",
    registry.get("count") == 15,
)

check(
    "REAL_V4_ALL_RETURN_TWICE",
    len(evaluators) == 15
    and all(
        item.get("returned_twice") is True
        for item in evaluators
    ),
)

check(
    "REAL_V4_REPEATABILITY",
    len(evaluators) == 15
    and all(
        item.get("repeatable") is True
        for item in evaluators
    ),
)

check(
    "REAL_V4_AGGREGATION_REPEATABILITY",
    aggregation.get("returned_twice") is True
    and aggregation.get("repeatable") is True,
)

# V4.37: Verify historical numerical agreement.

previous_probes = previous["probes.json"]["observations"]
zero = previous_probes["ALLOCATION_ZERO_COST"]["value"]
fee = previous_probes["ALLOCATION_WITH_COST"]["value"]

oracle = real["numerical_comparison.json"]

expected = oracle["reference_daily_rebalanced_zero_cost"]
observed = zero.get("ending_value")

check(
    "INDEPENDENT_ZERO_COST_MATH",
    type(observed) in (int, float)
    and math.isclose(
        observed,
        expected,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ),
)

check(
    "POSITIVE_COST_REDUCES_OR_PRESERVES_VALUE",
    type(fee.get("ending_value")) in (int, float)
    and fee["ending_value"] <= zero["ending_value"] + 1e-12,
)

check(
    "PAPER_EXECUTION_REMAINS_DISABLED",
    all(
        result.get("execution_enabled") is False
        and result.get("broker_order_generation_enabled") is False
        for result in (zero, fee)
    ),
)

# V4.38: Document actual limits of evidence.
# No self-assessment capability is silently closed.

capabilities = {
    "real_dto_offline": all(
        checks.get(name, False)
        for name in (
            "REAL_DTO_INSTANCES",
            "DTO_INVALID_SYMBOL_REJECTION",
            "DTO_PROVIDER_MISMATCH_REJECTION",
        )
    ),
    "real_v4_evaluators_repeatable_offline": all(
        checks.get(name, False)
        for name in (
            "REAL_V4_REGISTRY_15",
            "REAL_V4_ALL_RETURN_TWICE",
            "REAL_V4_REPEATABILITY",
            "REAL_V4_AGGREGATION_REPEATABILITY",
        )
    ),
    "portfolio_zero_cost_reference_matched":
        checks.get("INDEPENDENT_ZERO_COST_MATH", False),
    "external_market_provider_success": False,
    "actual_evaluator_numerical_correctness": False,
    "complete_portfolio_integration": False,
    "live_broker_execution_approved": False,
}

# V4.39: Write and validate a nonapproved evidence package.

stamp = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)
out = QUAL / f"neuro_v435_v440_finalization_{stamp}"

require(not out.exists(), "Evidence directory collision")
out.mkdir(parents=True, mode=0o700)

passed = sum(checks.values())
failed = len(checks) - passed

documents = {
    "runtime_observations.json": runtime,
    "checks.json": checks,
    "capabilities.json": capabilities,
    "qualification.json": {
        "schema": "neuro_v435_v440_finalization_v1",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "scope": "OFFLINE_SYNTHETIC",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks_failed": failed,
        "source_files_verified": 419,
        "real_market_provider_qualified": False,
        "full_portfolio_integration_qualified": False,
        "actual_evaluator_correctness_qualified": False,
        "feedback_registered": False,
        "developer_reviewed": False,
        "production_approved": False,
        "live_trading_approved": False,
        "limitations": [
            "Only synthetic historical prices were tested",
            "DTO runtime imports were executed in a child process",
            "Evaluator repeatability is not mathematical correctness",
            "Full provider-to-portfolio workflow remains untested",
            "No approved improvement feedback was registered",
        ],
    },
    "source_provenance.json": {
        "source_index_sha256": sha(INDEX.read_bytes()),
        "qualification_script_sha256": sha(
            Path(__file__).read_bytes()
        ),
        "historical_evidence": [
            str(FOUNDATION.relative_to(ROOT)),
            str(EXECUTION.relative_to(ROOT)),
            str(REAL.relative_to(ROOT)),
        ],
    },
}

for filename, document in documents.items():
    atomic(out / filename, document)

hashes = {
    name: sha((out / name).read_bytes())
    for name in documents
}

atomic(out / "artifact_hashes.json", hashes)

require(
    all(
        sha((out / name).read_bytes()) == expected
        for name, expected in hashes.items()
    ),
    "Generated evidence verification failed",
)

print()
print("=" * 76)
print("NEURO V4.35–V4.40 — RESULTS")
print("=" * 76)
print("CHECKS_PASSED=", passed)
print("CHECKS_TOTAL=", len(checks))
print("CHECKS_FAILED=", failed)
print("EVIDENCE_ROOT=", out)
print("ARTIFACT_HASHES=VERIFIED")
print("REAL_PROVIDER_SUCCESS=NOT_TESTED")
print("EVALUATOR_CORRECTNESS=NOT_FULLY_QUALIFIED")
print("FULL_PORTFOLIO_INTEGRATION=NOT_QUALIFIED")
print("FEEDBACK_REGISTERED=NO")
print("LIVE_TRADING_APPROVED=NO")
print("Terminal remains open.")

if failed:
    print("RELEASE_GATE=BLOCKED")
    raise SystemExit(1)

print("OFFLINE_QUALIFICATION_GATE=PASS")
