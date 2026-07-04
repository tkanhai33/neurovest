from __future__ import annotations

import json

from spine.L4_runtime.compiler.contract_patch_engine import generate_contract_patch_plan
from spine.L4_runtime.compiler.contract_diff_engine import compute_contract_diff

def run():
    report = {
        "diff": compute_contract_diff(),
        "patch_plan": generate_contract_patch_plan()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
