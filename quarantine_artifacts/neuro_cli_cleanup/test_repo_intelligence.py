from spine.L2_domain.repo_intelligence.repo_scanner import scan_repo, find_repo_root
from spine.L4_runtime.repo_intelligence_engine import build_repo_intelligence, recommend_next_file
from spine.L3_facade.repo_intelligence_facade import get_repo_architecture_report

def test_repo_scanner_excludes_venv():
    root = find_repo_root()
    files = scan_repo(root, limit=1000)
    assert files
    assert not any(".venv" in path for path in files)
    assert not any("site-packages" in path for path in files)

def test_repo_intelligence_builds_summary():
    intel = build_repo_intelligence(limit=1000)
    assert "summary" in intel
    assert "structure" in intel
    assert "unknown" in intel["structure"]

def test_repo_intelligence_recommends_safely():
    intel = build_repo_intelligence(limit=1000)
    recommendation = recommend_next_file(intel)
    assert "next_file" in recommendation
    assert "reason" in recommendation

def test_repo_intelligence_facade_report():
    report = get_repo_architecture_report(limit=1000)
    assert "recommendation" in report
    assert "summary" in report
