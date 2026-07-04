from __future__ import annotations

import json

from spine.L4_runtime.behavior.behavior_roadmap_engine import generate_behavior_roadmap
from spine.L4_runtime.behavior.behavior_analyzer import analyze_behavior

def run():
    report = {
        "behavior_analysis": analyze_behavior(),
        "roadmap": generate_behavior_roadmap()
    }

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run()
