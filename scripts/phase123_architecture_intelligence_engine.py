#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict, deque
import ast, json, py_compile

ROOT = Path(".").resolve()
OUT = ROOT / "runtime" / "architecture_intelligence_engine"
OUT.mkdir(parents=True, exist_ok=True)

PHASE = "123_ARCHITECTURE_INTELLIGENCE_ENGINE"

IGNORE = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", ".next",
    "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".cache", ".idea", ".vscode", "coverage"
}

SCAN_ROOTS = [
    ROOT / "backend/app/stacks",
    ROOT / "backend/app/spine",
    ROOT / "scripts",
]

LAYER_ORDER = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
    "L7": 7,
}

FORBIDDEN_IMPORT_KEYWORDS = [
    "broker",
    "snaptrade",
    "execution",
    "live_execution",
]

def ignored(path: Path) -> bool:
    return any(part in IGNORE for part in path.parts)

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))

def module_name(path: Path) -> str:
    r = path.relative_to(ROOT).with_suffix("")
    return ".".join(r.parts)

def detect_stack(path: Path) -> str:
    parts = path.relative_to(ROOT).parts
    if "stacks" in parts:
        i = parts.index("stacks")
        if i + 1 < len(parts):
            return parts[i + 1]
    if "spine" in parts:
        return "spine"
    if parts and parts[0] == "scripts":
        return "scripts"
    return "unknown"

def detect_layer(path: Path) -> str | None:
    for part in path.parts:
        if part.startswith("L") and len(part) >= 2 and part[1].isdigit():
            return part.split("_")[0]
    return None

def import_to_possible_path(name: str, modules_by_name: dict[str, str]) -> str | None:
    if name in modules_by_name:
        return modules_by_name[name]
    for mod, file in modules_by_name.items():
        if mod.endswith("." + name) or mod.endswith(name):
            return file
    return None

py_files = []
for base in SCAN_ROOTS:
    if not base.exists():
        continue
    for p in base.rglob("*.py"):
        if not ignored(p):
            py_files.append(p)

py_files = sorted(set(py_files))

modules_by_name = {module_name(p): rel(p) for p in py_files}
files_by_rel = {rel(p): p for p in py_files}

nodes = {}
import_edges = []
call_edges = []
parse_errors = []
compile_errors = []

for p in py_files:
    r = rel(p)
    stack = detect_stack(p)
    layer = detect_layer(p)

    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as exc:
        compile_errors.append({"file": r, "error": str(exc)})

    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(text)
    except Exception as exc:
        parse_errors.append({"file": r, "error": str(exc)})
        continue

    funcs, classes, imports, calls, constants = [], [], [], [], []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name:
                calls.append(name)

        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    constants.append(t.id)

    nodes[r] = {
        "file": r,
        "module": module_name(p),
        "stack": stack,
        "layer": layer,
        "functions": sorted(set(funcs)),
        "classes": sorted(set(classes)),
        "constants": sorted(set(constants)),
        "imports_raw": sorted(set(imports)),
        "calls": sorted(set(calls)),
    }

    for imp in sorted(set(imports)):
        target = import_to_possible_path(imp, modules_by_name)
        import_edges.append({
            "source": r,
            "target": target,
            "import": imp,
            "resolved": target is not None,
            "source_stack": stack,
            "target_stack": detect_stack(files_by_rel[target]) if target else None,
            "source_layer": layer,
            "target_layer": detect_layer(files_by_rel[target]) if target else None,
        })

    for c in sorted(set(calls)):
        call_edges.append({
            "source": r,
            "call": c,
        })

incoming = defaultdict(list)
outgoing = defaultdict(list)

for e in import_edges:
    if e["resolved"] and e["target"]:
        outgoing[e["source"]].append(e["target"])
        incoming[e["target"]].append(e["source"])

producer_keywords = [
    "feature", "reward", "artifact", "knowledge", "graph",
    "profile", "regime", "equity", "curve", "strategy"
]

producer_consumer = []
unused_modules = []

for file, node in nodes.items():
    lower = file.lower()
    is_producer = any(k in lower for k in producer_keywords)
    consumers = sorted(set(incoming[file]))

    if is_producer:
        producer_consumer.append({
            "producer": file,
            "stack": node["stack"],
            "layer": node["layer"],
            "consumers": consumers,
            "consumer_count": len(consumers),
        })

    if not consumers and node["stack"] != "scripts":
        unused_modules.append({
            "file": file,
            "stack": node["stack"],
            "layer": node["layer"],
            "reason": "No internal imports detected",
        })

layer_violations = []

for e in import_edges:
    if not e["resolved"]:
        continue

    sl = e.get("source_layer")
    tl = e.get("target_layer")

    if sl in LAYER_ORDER and tl in LAYER_ORDER:
        # L3 importing L0 directly, L4 importing L0 directly, L6 importing backend execution, etc.
        if LAYER_ORDER[sl] - LAYER_ORDER[tl] > 1:
            layer_violations.append({
                "source": e["source"],
                "target": e["target"],
                "source_layer": sl,
                "target_layer": tl,
                "reason": "Layer skip/bypass detected",
            })

    src_lower = e["source"].lower()
    target_lower = (e["target"] or e["import"]).lower()

    if "frontend" in src_lower and any(k in target_lower for k in FORBIDDEN_IMPORT_KEYWORDS):
        layer_violations.append({
            "source": e["source"],
            "target": e["target"] or e["import"],
            "reason": "Frontend forbidden dependency",
        })

def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles = []
    visited = set()
    path = []
    on_path = set()

    def dfs(node):
        visited.add(node)
        path.append(node)
        on_path.add(node)

        for nxt in graph.get(node, []):
            if nxt not in visited:
                dfs(nxt)
            elif nxt in on_path:
                try:
                    idx = path.index(nxt)
                    cycles.append(path[idx:] + [nxt])
                except ValueError:
                    pass

        path.pop()
        on_path.remove(node)

    for n in graph:
        if n not in visited:
            dfs(n)

    unique = []
    seen = set()
    for c in cycles:
        key = tuple(c)
        if key not in seen:
            unique.append(c)
            seen.add(key)
    return unique[:100]

cycles = find_cycles(outgoing)

stack_scores = {}
stack_files = defaultdict(list)

for file, node in nodes.items():
    stack_files[node["stack"]].append(file)

for stack, files in stack_files.items():
    layers = {nodes[f]["layer"] for f in files if nodes[f]["layer"]}
    file_count = len(files)
    imports_resolved = sum(1 for e in import_edges if e["source"] in files and e["resolved"])
    imports_total = sum(1 for e in import_edges if e["source"] in files)
    orphan_count = sum(1 for u in unused_modules if u["stack"] == stack)
    violation_count = sum(1 for v in layer_violations if nodes.get(v.get("source", ""), {}).get("stack") == stack)

    layer_score = min(40, len(layers) * 6)
    import_score = 25 if imports_total == 0 else int(25 * (imports_resolved / max(1, imports_total)))
    file_score = min(20, file_count)
    penalty = min(50, orphan_count * 2 + violation_count * 5)

    total = max(0, min(100, layer_score + import_score + file_score + 15 - penalty))

    stack_scores[stack] = {
        "score": total,
        "python_files": file_count,
        "layers_present": sorted(layers),
        "resolved_imports": imports_resolved,
        "total_imports": imports_total,
        "unused_or_orphan_modules": orphan_count,
        "layer_violations": violation_count,
    }

missing_systems = []

expected_keywords = {
    "knowledge_object": ["knowledge_object"],
    "knowledge_graph": ["knowledge_graph"],
    "research_cross_reference": ["cross_reference"],
    "symbol_intelligence_profile": ["symbol_intelligence", "symbol_profile"],
    "market_regime_library": ["regime"],
    "equity_curve_analytics": ["equity_curve"],
    "learning_artifact_pipeline": ["learning_artifact_pipeline"],
}

all_paths_lower = "\n".join(nodes.keys()).lower()

for name, keys in expected_keywords.items():
    present = any(k in all_paths_lower for k in keys)
    if not present:
        missing_systems.append(name)

build_priority = []

if "learning_artifact_pipeline" in missing_systems:
    build_priority.append({
        "priority": 1,
        "component": "learning_artifact_pipeline",
        "reason": "Feature extractor, reward scorer, and artifact contract exist but are not wired into a pipeline.",
    })

if "knowledge_object" in missing_systems:
    build_priority.append({
        "priority": 2,
        "component": "strategy_knowledge_object",
        "reason": "Learning artifacts need a structured knowledge object consumer.",
    })

if "knowledge_graph" in missing_systems:
    build_priority.append({
        "priority": 3,
        "component": "knowledge_graph",
        "reason": "Research, strategies, indicators, symbols, and regimes need a shared relationship layer.",
    })

if "research_cross_reference" in missing_systems:
    build_priority.append({
        "priority": 4,
        "component": "research_cross_reference_graph",
        "reason": "Research documents need links to symbols, indicators, regimes, and strategies.",
    })

if "symbol_intelligence_profile" in missing_systems:
    build_priority.append({
        "priority": 5,
        "component": "symbol_intelligence_profile",
        "reason": "Symbols need persistent behavioral profiles.",
    })

if "market_regime_library" in missing_systems:
    build_priority.append({
        "priority": 6,
        "component": "market_regime_library",
        "reason": "Historical bars need year/month/day regime labels.",
    })

if "equity_curve_analytics" in missing_systems:
    build_priority.append({
        "priority": 7,
        "component": "equity_curve_analytics",
        "reason": "Replay/training outputs need performance curve metrics.",
    })

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "summary": {
        "python_files_scanned": len(py_files),
        "modules_indexed": len(nodes),
        "import_edges": len(import_edges),
        "resolved_import_edges": sum(1 for e in import_edges if e["resolved"]),
        "call_edges": len(call_edges),
        "producer_consumer_nodes": len(producer_consumer),
        "layer_violations": len(layer_violations),
        "circular_dependencies": len(cycles),
        "unused_modules": len(unused_modules),
        "parse_errors": len(parse_errors),
        "compile_errors": len(compile_errors),
    },
    "architecture_completeness": {
        "overall_score": int(sum(s["score"] for s in stack_scores.values()) / max(1, len(stack_scores))),
        "stack_scores": stack_scores,
    },
    "missing_systems": missing_systems,
    "build_priority": build_priority,
    "recommended_next_phase": "123B_LEARNING_ARTIFACT_PIPELINE_STUB",
    "certified": len(parse_errors) == 0,
}

outputs = {
    "123_import_graph.json": import_edges,
    "123_call_graph.json": call_edges,
    "123_producer_consumer_graph.json": producer_consumer,
    "123_layer_violations.json": layer_violations,
    "123_circular_dependencies.json": cycles,
    "123_unused_modules.json": unused_modules,
    "123_architecture_completeness.json": result["architecture_completeness"],
    "123_build_priority.json": build_priority,
    "123_summary.json": result,
}

for name, payload in outputs.items():
    (OUT / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")

lines = [
    PHASE,
    "",
    f"certified: {result['certified']}",
    f"python_files_scanned: {len(py_files)}",
    f"modules_indexed: {len(nodes)}",
    f"import_edges: {result['summary']['import_edges']}",
    f"resolved_import_edges: {result['summary']['resolved_import_edges']}",
    f"call_edges: {result['summary']['call_edges']}",
    f"producer_consumer_nodes: {result['summary']['producer_consumer_nodes']}",
    f"layer_violations: {result['summary']['layer_violations']}",
    f"circular_dependencies: {result['summary']['circular_dependencies']}",
    f"unused_modules: {result['summary']['unused_modules']}",
    f"overall_architecture_score: {result['architecture_completeness']['overall_score']}%",
    "",
    "Stack Scores:",
]

for stack, score in sorted(stack_scores.items(), key=lambda x: x[1]["score"], reverse=True):
    lines.append(
        f"- {stack}: {score['score']}% | files={score['python_files']} | layers={score['layers_present']} | unused={score['unused_or_orphan_modules']} | violations={score['layer_violations']}"
    )

lines.extend([
    "",
    "Missing Systems:",
])

if missing_systems:
    for m in missing_systems:
        lines.append(f"- {m}")
else:
    lines.append("- None detected")

lines.extend([
    "",
    "Build Priority:",
])

for item in build_priority:
    lines.append(f"{item['priority']}. {item['component']} — {item['reason']}")

lines.extend([
    "",
    "Outputs:",
    f"- {OUT / '123_import_graph.json'}",
    f"- {OUT / '123_call_graph.json'}",
    f"- {OUT / '123_producer_consumer_graph.json'}",
    f"- {OUT / '123_layer_violations.json'}",
    f"- {OUT / '123_circular_dependencies.json'}",
    f"- {OUT / '123_unused_modules.json'}",
    f"- {OUT / '123_architecture_completeness.json'}",
    f"- {OUT / '123_build_priority.json'}",
    f"- {OUT / '123_summary.json'}",
    "",
    "Next:",
    result["recommended_next_phase"],
])

(OUT / "123_report.txt").write_text("\n".join(lines), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "python_files_scanned": len(py_files),
    "modules_indexed": len(nodes),
    "import_edges": result["summary"]["import_edges"],
    "call_edges": result["summary"]["call_edges"],
    "layer_violations": result["summary"]["layer_violations"],
    "circular_dependencies": result["summary"]["circular_dependencies"],
    "unused_modules": result["summary"]["unused_modules"],
    "overall_architecture_score": result["architecture_completeness"]["overall_score"],
    "recommended_next_phase": result["recommended_next_phase"],
    "report": str(OUT / "123_report.txt"),
}, indent=2))
