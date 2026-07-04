from __future__ import annotations
import json
from spine.L4_runtime.roadmap_engine import generate_roadmap
def run():
    print(json.dumps(generate_roadmap(), indent=2))
if __name__ == "__main__":
    run()
