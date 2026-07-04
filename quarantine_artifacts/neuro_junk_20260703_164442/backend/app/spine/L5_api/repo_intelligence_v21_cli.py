from __future__ import annotations

import json

from spine.L4_runtime.patch.patch_generator_engine import generate_patch_plan

def run():
    print(json.dumps(generate_patch_plan(), indent=2))

if __name__ == "__main__":
    run()
