#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()

OUT_DIR = ROOT / "runtime" / "certifications"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "phase7g_graph_visualization_certification_latest.json"

FILES = {
    "wire_script": ROOT / "generate_wire_graph.py",
    "dependency_graph": ROOT / "runtime" / "repo_memory" / "dependency_graph_v1.json",
    "dependency_overlay": ROOT / "runtime" / "repo_memory" / "dependency_topology_overlay_v1.json",
    "topology_png": ROOT / "topology_wire_graph.png",
}


def run(cmd):
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "cmd": " ".join(cmd),
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def run_cli(*args):
    result = run(["./neuro_cli.py", *args])

    try:
        payload = json.loads(result["stdout"])
    except Exception:
        payload = {
            "parse_error": True,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }

    result["payload"] = payload
    return result


def response(step):
    return step.get("payload", {}).get("response", {})


def file_meta(path: Path):
    return {
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "path": str(path.relative_to(ROOT)),
    }


def main():
    print("🧠 PHASE 7G GRAPH VISUALIZATION CERTIFICATION")

    steps = {
        "compile_wire_script": run(["python3", "-m", "py_compile", "generate_wire_graph.py"]),
        "repo_index": run(["python3", "scripts/phase4_repo_memory_indexer_v2.py"]),
        "dependency_graph_export": run(["python3", "scripts/phase6c_dependency_graph_export.py"]),
        "dependency_overlay_export": run(["python3", "scripts/phase7a_dependency_topology_overlay_export.py"]),
        "generate_wire_graph": run(["python3", "generate_wire_graph.py"]),
        "graph_reset": run_cli("graph_reset"),
        "simulate_trade": run_cli("simulate_trade", "AAPL"),
        "graph_validate": run_cli("graph_validate"),
    }

    file_status = {
        name: file_meta(path)
        for name, path in FILES.items()
    }

    overlay = {}
    dep_graph = {}

    if FILES["dependency_overlay"].exists():
        overlay = json.loads(FILES["dependency_overlay"].read_text())

    if FILES["dependency_graph"].exists():
        dep_graph = json.loads(FILES["dependency_graph"].read_text())

    trade = response(steps["simulate_trade"])
    graph_validate = response(steps["graph_validate"])

    checks = {
        "wire_script_compiles": steps["compile_wire_script"]["returncode"] == 0,
        "repo_index_ok": steps["repo_index"]["returncode"] == 0,
        "dependency_graph_export_ok": steps["dependency_graph_export"]["returncode"] == 0,
        "dependency_overlay_export_ok": steps["dependency_overlay_export"]["returncode"] == 0,
        "generate_wire_graph_ok": steps["generate_wire_graph"]["returncode"] == 0,
        "wire_script_exists": file_status["wire_script"]["exists"],
        "dependency_graph_exists": file_status["dependency_graph"]["exists"],
        "dependency_overlay_exists": file_status["dependency_overlay"]["exists"],
        "topology_png_exists": file_status["topology_png"]["exists"],
        "topology_png_nonempty": file_status["topology_png"]["size_bytes"] > 10000,
        "dependency_graph_has_nodes": dep_graph.get("node_count", 0) > 0,
        "dependency_graph_has_edges": dep_graph.get("edge_count", 0) > 0,
        "overlay_has_edges": overlay.get("topology_overlay_edge_count", 0) > 0,
        "simulate_trade_ok": trade.get("status") == "trade_simulated",
        "simulate_trade_guard_ok": trade.get("graph_guard", {}).get("valid") is True,
        "graph_validate_ok": graph_validate.get("valid") is True,
    }

    certified = all(checks.values())

    report = {
        "phase": "7G_GRAPH_VISUALIZATION_CERTIFICATION",
        "generated_at": datetime.now(UTC).isoformat(),
        "certified": certified,
        "checks": checks,
        "file_status": file_status,
        "graph_summary": {
            "dependency_node_count": dep_graph.get("node_count"),
            "dependency_edge_count": dep_graph.get("edge_count"),
            "overlay_edge_count": overlay.get("topology_overlay_edge_count"),
            "raw_overlay_edge_count": overlay.get("raw_overlay_edge_count"),
            "skipped_overlay_edge_count": overlay.get("skipped_edge_count"),
        },
        "steps": steps,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "certified": certified,
        "checks": checks,
        "file_status": file_status,
        "graph_summary": report["graph_summary"],
        "output": str(OUT_JSON),
    }, indent=2))

    if not certified:
        sys.exit(1)


if __name__ == "__main__":
    main()
