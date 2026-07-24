#!/usr/bin/env python3
import json
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(".").resolve()
REPO_INDEX = ROOT / "runtime" / "repo_memory" / "repo_index_v2.json"
OUT_DIR = ROOT / "runtime" / "repo_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "dependency_graph_v1.json"


def load_index():
    if not REPO_INDEX.exists():
        raise FileNotFoundError(f"Missing repo index: {REPO_INDEX}")
    return json.loads(REPO_INDEX.read_text())


def module_name(file_path: str) -> str:
    return file_path.replace("/", ".").replace(".py", "")


def resolve_import(import_name: str, files_by_module: dict):
    if import_name in files_by_module:
        return files_by_module[import_name]

    # handle imports that point to package/module prefix
    candidates = [
        file_path
        for mod, file_path in files_by_module.items()
        if mod == import_name or mod.endswith("." + import_name)
    ]

    if len(candidates) == 1:
        return candidates[0]

    return None


def main():
    data = load_index()
    files = data.get("files", [])

    files_by_module = {
        module_name(item["file"]): item["file"]
        for item in files
        if item.get("file", "").endswith(".py")
    }

    nodes = []
    edges = []

    for item in files:
        file_path = item.get("file")

        nodes.append({
            "id": file_path,
            "module": module_name(file_path),
            "stack": item.get("stack"),
            "layer": item.get("layer"),
            "function_count": len(item.get("functions", [])),
            "class_count": len(item.get("classes", [])),
            "import_count": len(item.get("imports", [])),
        })

    seen_edges = set()

    for item in files:
        src = item.get("file")

        for imp in item.get("imports", []):
            dst = resolve_import(imp, files_by_module)

            if not dst:
                continue

            key = (src, dst, imp)
            if key in seen_edges:
                continue

            seen_edges.add(key)

            edges.append({
                "from": src,
                "to": dst,
                "import": imp,
                "from_stack": item.get("stack"),
                "from_layer": item.get("layer"),
            })

    in_degree = {}
    out_degree = {}

    for node in nodes:
        in_degree[node["id"]] = 0
        out_degree[node["id"]] = 0

    for edge in edges:
        out_degree[edge["from"]] = out_degree.get(edge["from"], 0) + 1
        in_degree[edge["to"]] = in_degree.get(edge["to"], 0) + 1

    for node in nodes:
        node["in_degree"] = in_degree.get(node["id"], 0)
        node["out_degree"] = out_degree.get(node["id"], 0)

    report = {
        "phase": "6C_DEPENDENCY_GRAPH_EXPORT",
        "generated_at": datetime.now(UTC).isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "top_imported": sorted(
            [
                {
                    "file": file,
                    "in_degree": degree,
                }
                for file, degree in in_degree.items()
            ],
            key=lambda x: x["in_degree"],
            reverse=True,
        )[:25],
        "top_importers": sorted(
            [
                {
                    "file": file,
                    "out_degree": degree,
                }
                for file, degree in out_degree.items()
            ],
            key=lambda x: x["out_degree"],
            reverse=True,
        )[:25],
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "node_count": report["node_count"],
        "edge_count": report["edge_count"],
        "output": str(OUT_JSON),
        "top_imported": report["top_imported"][:5],
        "top_importers": report["top_importers"][:5],
    }, indent=2))


if __name__ == "__main__":
    main()
