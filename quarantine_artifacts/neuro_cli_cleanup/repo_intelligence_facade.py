from __future__ import annotations

from spine.L4_runtime.repo_intelligence_engine import (
    build_repo_intelligence,
    recommend_next_file,
)

def get_repo_architecture_report(limit: int = 1000) -> dict:
    intel = build_repo_intelligence(limit=limit)
    intel["recommendation"] = recommend_next_file(intel)
    return intel
