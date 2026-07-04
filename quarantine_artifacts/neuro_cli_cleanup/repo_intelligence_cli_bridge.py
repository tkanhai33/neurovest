from __future__ import annotations

import json
from spine.L3_facade.repo_intelligence_facade import get_repo_architecture_report

def print_repo_architecture_report(limit: int = 1000) -> None:
    report = get_repo_architecture_report(limit=limit)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    print_repo_architecture_report()
