#!/usr/bin/env python3

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import sys
import time


ROOT = Path(".").resolve()

PHASE = "133B-D_REAL_FLOW_SMOKE_VALIDATION"
BASE_URL = "http://127.0.0.1:8000"

OUT_DIR = ROOT / "runtime" / "graph_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "133B_d_real_flow_smoke_latest.json"
OUT_TXT = OUT_DIR / "133B_d_real_flow_smoke_latest.txt"


def request_json(
    method: str,
    path: str,
    *,
    query: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"

    if query:
        url = f"{url}?{urlencode(query)}"

    request = Request(
        url,
        method=method,
        headers={
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            data = json.loads(payload)

            if not isinstance(data, dict):
                raise RuntimeError(
                    f"Expected JSON object from {method} {path}"
                )

            return data

    except HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"{method} {url} returned HTTP {error.code}: {body}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            "NeuroVest backend is not reachable at "
            f"{BASE_URL}. Start the backend before running 133B-D. "
            f"Original error: {error}"
        ) from error


def trace_steps(
    snapshot: dict[str, Any],
    trace_id: str,
) -> list[dict[str, Any]]:
    traces = snapshot.get("traces") or []

    for trace in traces:
        if trace.get("trace_id") == trace_id:
            steps = trace.get("steps") or []

            return sorted(
                steps,
                key=lambda step: int(
                    step.get("sequence", 0)
                ),
            )

    recent_flows = snapshot.get("recent_flows") or []

    return sorted(
        [
            step
            for step in recent_flows
            if step.get("trace_id") == trace_id
        ],
        key=lambda step: int(
            step.get("sequence", 0)
        ),
    )


def event_types(
    steps: list[dict[str, Any]],
) -> list[str]:
    return [
        str(step.get("event_type") or "UNKNOWN")
        for step in steps
    ]


def statuses(
    steps: list[dict[str, Any]],
) -> list[str]:
    return [
        str(step.get("status") or "unknown")
        for step in steps
    ]


def validate_trace(
    trace_id: str,
    symbol: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    sequences = [
        int(step.get("sequence", 0))
        for step in steps
    ]

    ordered = (
        bool(sequences)
        and sequences == sorted(sequences)
        and len(sequences) == len(set(sequences))
    )

    step_event_types = event_types(steps)
    step_statuses = statuses(steps)

    required_prefix = {
        "STRATEGY_EVALUATION_STARTED",
        "STRATEGY_DECISION_COMPLETE",
        "PORTFOLIO_ACCOUNTING_REQUEST",
        "PORTFOLIO_ACCOUNTING_COMPLETE",
        "RISK_EVALUATION_STARTED",
        "RISK_DECISION",
    }

    prefix_present = required_prefix.issubset(
        set(step_event_types)
    )

    risk_blocked = any(
        step.get("event_type") == "RISK_DECISION"
        and step.get("status") == "blocked"
        for step in steps
    )

    execution_started = (
        "PAPER_EXECUTION_STARTED" in step_event_types
    )

    execution_result = (
        "PAPER_EXECUTION_RESULT" in step_event_types
    )

    ledger_recorded = (
        "LEDGER_WRITE_COMPLETE" in step_event_types
    )

    inventory_recorded = (
        "PORTFOLIO_INVENTORY_UPDATED"
        in step_event_types
    )

    node_records = [
        step
        for step in steps
        if step.get("record_type") == "node_activation"
    ]

    edge_records = [
        step
        for step in steps
        if step.get("record_type") == "edge_activation"
    ]

    all_trace_ids_match = all(
        step.get("trace_id") == trace_id
        for step in steps
    )

    all_symbols_match = all(
        step.get("symbol") in (None, symbol)
        for step in steps
    )

    terminal_branch_valid = (
        (
            risk_blocked
            and ledger_recorded
            and inventory_recorded
        )
        or (
            execution_started
            and execution_result
            and ledger_recorded
            and inventory_recorded
        )
    )

    certified = all(
        [
            bool(steps),
            ordered,
            prefix_present,
            bool(node_records),
            bool(edge_records),
            all_trace_ids_match,
            all_symbols_match,
            terminal_branch_valid,
        ]
    )

    return {
        "trace_id": trace_id,
        "symbol": symbol,
        "step_count": len(steps),
        "sequences": sequences,
        "event_types": step_event_types,
        "statuses": step_statuses,
        "ordered": ordered,
        "prefix_present": prefix_present,
        "risk_blocked": risk_blocked,
        "execution_started": execution_started,
        "execution_result": execution_result,
        "ledger_recorded": ledger_recorded,
        "inventory_recorded": inventory_recorded,
        "node_record_count": len(node_records),
        "edge_record_count": len(edge_records),
        "all_trace_ids_match": all_trace_ids_match,
        "all_symbols_match": all_symbols_match,
        "terminal_branch_valid": terminal_branch_valid,
        "certified": certified,
        "steps": steps,
    }


def main() -> int:
    created_at = datetime.now(UTC).isoformat()

    print("=" * 80)
    print(PHASE)
    print("=" * 80)

    baseline = request_json(
        "GET",
        "/api/v1/graph/live",
    )

    baseline_sequence = int(
        baseline.get("sequence") or 0
    )

    print(
        f"Baseline graph sequence: {baseline_sequence}"
    )

    override_enabled = False
    summary: dict[str, Any] = {}
    reset_response: dict[str, Any] | None = None

    try:
        print(
            "Enabling controlled BUY sandbox signal "
            "for the existing paper path..."
        )

        enable_response = request_json(
            "POST",
            "/api/v1/sandbox/signal",
            query={"action": "buy"},
        )

        override_enabled = True

        print(
            "Calling the existing dashboard summary flow..."
        )

        summary = request_json(
            "GET",
            "/api/v1/dashboard/summary",
            timeout=120.0,
        )

    finally:
        if override_enabled:
            print(
                "Resetting sandbox override to HOLD..."
            )

            try:
                reset_response = request_json(
                    "POST",
                    "/api/v1/sandbox/signal",
                    query={"action": "hold"},
                )

            except Exception as reset_error:
                reset_response = {
                    "status": "reset_failed",
                    "error": str(reset_error),
                }

    results = summary.get("results") or []

    trace_targets: list[dict[str, str]] = []

    for item in results:
        trace_id = item.get("trace_id")
        symbol = item.get("symbol")

        if trace_id and symbol:
            trace_targets.append(
                {
                    "trace_id": str(trace_id),
                    "symbol": str(symbol),
                }
            )

    if not trace_targets:
        raise RuntimeError(
            "Dashboard summary returned no trace IDs. "
            "The running backend may not have been restarted "
            "after installing Phase 133B-B."
        )

    time.sleep(0.5)

    snapshot = request_json(
        "GET",
        "/api/v1/graph/live",
    )

    final_sequence = int(
        snapshot.get("sequence") or 0
    )

    validations = []

    for target in trace_targets:
        steps = trace_steps(
            snapshot,
            target["trace_id"],
        )

        validation = validate_trace(
            target["trace_id"],
            target["symbol"],
            steps,
        )

        validations.append(validation)

        print()
        print(
            f"{target['symbol']} "
            f"{target['trace_id']}"
        )
        print(
            f"  steps={validation['step_count']}"
        )
        print(
            f"  ordered={validation['ordered']}"
        )
        print(
            f"  prefix={validation['prefix_present']}"
        )
        print(
            f"  branch_valid="
            f"{validation['terminal_branch_valid']}"
        )
        print(
            f"  certified={validation['certified']}"
        )

    graph_contract = snapshot.get("contract") or {}

    contract_valid = (
        graph_contract.get("phase")
        == "133B_ACTIVE_NODE_FLOW_GRAPH"
        and graph_contract.get("event_driven") is True
        and graph_contract.get(
            "synthetic_activations"
        )
        is False
    )

    sequence_advanced = (
        final_sequence > baseline_sequence
    )

    all_traces_certified = (
        bool(validations)
        and all(
            validation["certified"]
            for validation in validations
        )
    )

    reset_succeeded = (
        reset_response is not None
        and reset_response.get("status")
        != "reset_failed"
    )

    certified = all(
        [
            contract_valid,
            sequence_advanced,
            all_traces_certified,
            reset_succeeded,
        ]
    )

    report = {
        "phase": PHASE,
        "created_at": created_at,
        "backend": BASE_URL,
        "baseline_sequence": baseline_sequence,
        "final_sequence": final_sequence,
        "sequence_advanced": sequence_advanced,
        "graph_contract": graph_contract,
        "contract_valid": contract_valid,
        "dashboard_summary": summary,
        "sandbox_reset": reset_response,
        "sandbox_reset_succeeded": reset_succeeded,
        "trace_count": len(validations),
        "trace_validations": validations,
        "all_traces_certified": all_traces_certified,
        "safety": {
            "live_broker_used": False,
            "paper_path_used": True,
            "risk_controls_bypassed": False,
            "sandbox_override_reset_to_hold": reset_succeeded,
        },
        "certified": certified,
        "recommended_next_phase": (
            "133B-E_GRAPH_WEBSOCKET_TRANSPORT"
            if certified
            else "133B-D_REAL_FLOW_SMOKE_REPAIR"
        ),
    }

    OUT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        PHASE,
        "",
        f"certified: {certified}",
        "",
        "SUMMARY",
        f"baseline_sequence: {baseline_sequence}",
        f"final_sequence: {final_sequence}",
        f"sequence_advanced: {sequence_advanced}",
        f"contract_valid: {contract_valid}",
        f"trace_count: {len(validations)}",
        f"all_traces_certified: {all_traces_certified}",
        f"sandbox_reset_succeeded: {reset_succeeded}",
        "",
        "TRACES",
    ]

    for validation in validations:
        lines.extend(
            [
                (
                    f"{validation['symbol']} "
                    f"{validation['trace_id']}"
                ),
                (
                    f"  steps: "
                    f"{validation['step_count']}"
                ),
                (
                    f"  ordered: "
                    f"{validation['ordered']}"
                ),
                (
                    f"  node_records: "
                    f"{validation['node_record_count']}"
                ),
                (
                    f"  edge_records: "
                    f"{validation['edge_record_count']}"
                ),
                (
                    f"  risk_blocked: "
                    f"{validation['risk_blocked']}"
                ),
                (
                    f"  execution_started: "
                    f"{validation['execution_started']}"
                ),
                (
                    f"  ledger_recorded: "
                    f"{validation['ledger_recorded']}"
                ),
                (
                    f"  inventory_recorded: "
                    f"{validation['inventory_recorded']}"
                ),
                (
                    f"  certified: "
                    f"{validation['certified']}"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "SAFETY",
            "live_broker_used: False",
            "paper_path_used: True",
            "risk_controls_bypassed: False",
            (
                "sandbox_override_reset_to_hold: "
                f"{reset_succeeded}"
            ),
            "",
            (
                "next: "
                f"{report['recommended_next_phase']}"
            ),
        ]
    )

    OUT_TXT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("133B-D RESULT")
    print("=" * 80)
    print(
        OUT_TXT.read_text(
            encoding="utf-8"
        )
    )

    return 0 if certified else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except Exception as error:
        print(
            f"133B-D failed: {error}",
            file=sys.stderr,
        )
        raise
