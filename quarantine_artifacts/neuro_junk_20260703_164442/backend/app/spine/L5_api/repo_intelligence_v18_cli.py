from __future__ import annotations

import json

from spine.L4_runtime.orchestrator.intelligent_roadmap_engine import generate_intelligent_roadmap

def run():
    print(json.dumps(generate_intelligent_roadmap(), indent=2))

if __name__ == "__main__":
    run()
