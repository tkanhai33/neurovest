from __future__ import annotations

import json

from spine.L4_runtime.compiler.staging_engine import build_staged_plan
from spine.L4_runtime.compiler.execution_gate import validate_stage

def run():
    plan = build_staged_plan()

    validated = []
    rejected = []

    for stage in plan["stages"]:
        result = validate_stage(stage)

        if result["approved"]:
            validated.append(result)
        else:
            rejected.append(result)

    print(json.dumps({
        "staged_plan": plan,
        "validated": validated,
        "rejected": rejected
    }, indent=2))

if __name__ == "__main__":
    run()
