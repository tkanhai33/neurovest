from __future__ import annotations
from spine.L3_facade.repo_intelligence_facade import get_repo_intelligence
from spine.L4_runtime.stack_gap_analyzer import analyze_stack_gaps
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
from spine.L4_runtime.patch_memory import _load
def check_convergence(limit: int = 1000) -> dict:
    intel = get_repo_intelligence(limit=limit)
    gaps = analyze_stack_gaps(limit=limit)
    deps = build_dependency_graph(limit=limit)
    applied = _load()
    has_remaining_real_gaps = any(len(v) > 0 for v in gaps["gaps"].values())
    has_missing_deps = len(deps["missing_links"]) > 0
    # 🔥 FIX — convergence now depends on:
    # - no gaps OR only already-applied paths exist
    converged = (
        not has_remaining_real_gaps
        and not has_missing_deps
    )
    return {
    }
