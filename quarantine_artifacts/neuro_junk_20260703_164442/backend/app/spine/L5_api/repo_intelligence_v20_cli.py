from __future__ import annotations

import json

from spine.L4_runtime.compiler.build_order_engine import compute_build_order

def run():
    print(json.dumps(compute_build_order(), indent=2))

if __name__ == "__main__":
    run()
