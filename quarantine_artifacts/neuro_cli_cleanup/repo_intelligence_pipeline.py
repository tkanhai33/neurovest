from __future__ import annotations

import json

from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff
from spine.L4_runtime.compiler.execution_order_engine import compute_execution_order
from spine.L4_runtime.compiler.staging_engine import build_staged_plan
from spine.L4_runtime.compiler.execution_gate import validate_stage


def run_pipeline(limit: int = 200) -> dict:

    # 1. CONTRACT DIFF
    diff = compute_contract_diff(limit=limit)

    # 2. EXECUTION ORDER
    order = compute_execution_order(limit=limit)

    # 3. STAGING
    staged = build_staged_plan(limit=limit)

    # 4. GATE FILTER
    approved = []
    rejected = []

    for stage in staged["stages"]:
        result = validate_stage(stage)

        if result["approved"]:
            approved.append(stage)
        else:
            rejected.append(stage)

    # 5. FINAL REPORT
    return {
        "diff_summary": {
            "missing": len(diff["missing"]),
            "extra": len(diff["extra"])
        },
        "execution_order_count": len(order["order"]),
        "stages_total": len(staged["stages"]),
        "approved_stages": len(approved),
        "rejected_stages": len(rejected),
        "system_state": "STABLE" if len(rejected) == 0 else "DEGRADED"
    }


if __name__ == "__main__":
    print(json.dumps(run_pipeline(), indent=2))
