
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence

def get_repo_intelligence(limit=1000):
    # HARD SAFE BOUNDARY: no tracing, no wrappers, no recursion
    return build_repo_intelligence(limit=limit)
