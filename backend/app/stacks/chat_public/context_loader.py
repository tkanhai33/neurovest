from pathlib import Path
import json

ROOT = Path(".").resolve()

REPO_INDEX = ROOT / "runtime" / "repo_memory" / "repo_index.json"
RESEARCH_SEED = ROOT / "runtime" / "research_db" / "research_seed.json"
SYMBOL_REGISTRY = ROOT / "runtime" / "market_warehouse" / "symbol_registry.json"


def _load_json(path: Path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception as e:
        return {"error": str(e), "path": str(path)}
    return fallback


def load_repo_context(limit: int = 12):
    data = _load_json(REPO_INDEX, {"files": []})
    files = data.get("files", [])[:limit]

    return {
        "file_count": data.get("file_count", 0),
        "sample_files": files,
    }


def load_research_context():
    data = _load_json(RESEARCH_SEED, {"categories": {}})
    return data.get("categories", {})


def load_market_context():
    data = _load_json(SYMBOL_REGISTRY, {"symbols": []})
    return data.get("symbols", [])


def build_chat_context():
    return {
        "repo_memory": load_repo_context(),
        "research_db": load_research_context(),
        "market_warehouse": load_market_context(),
    }


def _symbol_to_file(symbol: str) -> str:
    return symbol.upper().replace(".", "_")


def load_live_price(symbol: str):
    symbol = symbol.upper()
    path = ROOT / "runtime" / "market_warehouse" / "live" / f"{_symbol_to_file(symbol)}_live.json"
    return _load_json(path, {"error": "live price not found", "symbol": symbol})


def load_history_status(symbol: str):
    symbol = symbol.upper()
    path = ROOT / "runtime" / "market_warehouse" / "history" / f"{_symbol_to_file(symbol)}_history.csv"

    if not path.exists():
        return {
            "symbol": symbol,
            "history_found": False,
            "rows": 0,
            "path": str(path),
        }

    try:
        with path.open("r", errors="ignore") as f:
            rows = max(0, sum(1 for _ in f) - 1)
    except Exception as e:
        return {
            "symbol": symbol,
            "history_found": False,
            "error": str(e),
            "path": str(path),
        }

    return {
        "symbol": symbol,
        "history_found": True,
        "rows": rows,
        "path": str(path),
    }


def load_warehouse_status():
    registry = _load_json(SYMBOL_REGISTRY, {"symbols": []})
    symbols = registry.get("symbols", [])

    history_dir = ROOT / "runtime" / "market_warehouse" / "history"
    live_dir = ROOT / "runtime" / "market_warehouse" / "live"

    history_files = list(history_dir.glob("*_history.csv")) if history_dir.exists() else []
    live_files = list(live_dir.glob("*_live.json")) if live_dir.exists() else []

    total_rows = 0
    per_symbol_rows = {}

    for path in history_files:
        try:
            rows = max(0, sum(1 for _ in path.open("r", errors="ignore")) - 1)
            per_symbol_rows[path.name.replace("_history.csv", "").replace("_", ".")] = rows
            total_rows += rows
        except Exception:
            pass

    return {
        "symbol_count": len(symbols),
        "history_file_count": len(history_files),
        "live_file_count": len(live_files),
        "total_history_rows": total_rows,
        "per_symbol_rows": per_symbol_rows,
        "updated_at": registry.get("updated_at"),
    }


def load_candles(symbol: str, limit: int = 5):
    symbol = symbol.upper()
    limit = max(1, min(int(limit), 50))

    path = ROOT / "runtime" / "market_warehouse" / "history" / f"{_symbol_to_file(symbol)}_history.csv"

    if not path.exists():
        return {
            "symbol": symbol,
            "found": False,
            "candles": [],
            "path": str(path),
        }

    lines = path.read_text(errors="ignore").splitlines()

    if len(lines) <= 1:
        return {
            "symbol": symbol,
            "found": True,
            "candles": [],
            "path": str(path),
        }

    header = lines[0].split(",")
    rows = lines[-limit:]

    candles = []
    for row in rows:
        values = row.split(",")
        item = {}
        for i, col in enumerate(header):
            if i < len(values):
                item[col] = values[i]
        candles.append(item)

    return {
        "symbol": symbol,
        "found": True,
        "limit": limit,
        "candles": candles,
        "path": str(path),
    }


REPO_INDEX_V2 = ROOT / "runtime" / "repo_memory" / "repo_index_v2.json"


def load_repo_index_v2():
    return _load_json(REPO_INDEX_V2, {
        "files": [],
        "by_stack": {},
        "by_layer": {},
        "symbol_lookup": {},
    })


def repo_summary():
    data = load_repo_index_v2()
    return {
        "file_count": data.get("file_count", 0),
        "stack_count": data.get("stack_count", 0),
        "layer_count": data.get("layer_count", 0),
        "symbol_count": data.get("symbol_count", 0),
        "stacks": sorted(data.get("by_stack", {}).keys()),
        "layers": sorted(data.get("by_layer", {}).keys()),
    }


def repo_find(term: str):
    term = term.strip().lower()
    data = load_repo_index_v2()
    symbols = data.get("symbol_lookup", {})

    matches = []

    for name, hits in symbols.items():
        if term in name.lower():
            matches.append({
                "symbol": name,
                "hits": hits[:10],
            })

    for item in data.get("files", []):
        if term in item.get("file", "").lower():
            matches.append({
                "file": item.get("file"),
                "stack": item.get("stack"),
                "layer": item.get("layer"),
                "functions": item.get("functions", [])[:10],
                "classes": item.get("classes", [])[:10],
            })

    return {
        "term": term,
        "match_count": len(matches),
        "matches": matches[:25],
    }


def repo_stack(stack: str):
    stack = stack.strip()
    data = load_repo_index_v2()
    files = data.get("by_stack", {}).get(stack, [])

    return {
        "stack": stack,
        "file_count": len(files),
        "files": files[:100],
    }


def repo_unknowns():
    data = load_repo_index_v2()
    files = data.get("files", [])

    unknown = [
        {
            "file": item.get("file"),
            "stack": item.get("stack"),
            "layer": item.get("layer"),
            "functions": item.get("functions", [])[:5],
            "classes": item.get("classes", [])[:5],
        }
        for item in files
        if item.get("stack") == "unknown" or item.get("layer") == "unknown"
    ]

    loose_root = [
        item
        for item in unknown
        if "/" not in item.get("file", "")
    ]

    return {
        "unknown_count": len(unknown),
        "loose_root_count": len(loose_root),
        "loose_root_files": loose_root,
        "unknown_files": unknown[:100],
    }


def repo_file(path_text: str):
    path_text = path_text.strip()
    data = load_repo_index_v2()

    for item in data.get("files", []):
        if item.get("file") == path_text:
            return {
                "found": True,
                "file": item,
            }

    return {
        "found": False,
        "file": path_text,
    }


def repo_symbol(name: str):
    name = name.strip()
    data = load_repo_index_v2()
    hits = data.get("symbol_lookup", {}).get(name, [])

    return {
        "symbol": name,
        "found": bool(hits),
        "hit_count": len(hits),
        "hits": hits[:25],
    }


def repo_imports(path_text: str):
    path_text = path_text.strip()
    data = load_repo_index_v2()

    for item in data.get("files", []):
        if item.get("file") == path_text:
            return {
                "found": True,
                "file": path_text,
                "stack": item.get("stack"),
                "layer": item.get("layer"),
                "imports": item.get("imports", []),
                "import_count": len(item.get("imports", [])),
            }

    return {
        "found": False,
        "file": path_text,
        "imports": [],
        "import_count": 0,
    }


def _safe_repo_path(path_text: str):
    path_text = path_text.strip()

    if not path_text or path_text.startswith("/") or ".." in Path(path_text).parts:
        return None

    path = ROOT / path_text

    if not path.exists() or not path.is_file():
        return None

    return path


def repo_head(path_text: str, limit: int = 80):
    limit = max(1, min(int(limit), 200))
    path = _safe_repo_path(path_text)

    if not path:
        return {
            "found": False,
            "file": path_text,
            "lines": [],
        }

    lines = path.read_text(errors="ignore").splitlines()[:limit]

    return {
        "found": True,
        "file": path_text,
        "line_count": len(lines),
        "lines": [
            {
                "line": i + 1,
                "text": line,
            }
            for i, line in enumerate(lines)
        ],
    }


def repo_grep(term: str, limit: int = 50):
    term = term.strip()
    limit = max(1, min(int(limit), 100))

    data = load_repo_index_v2()
    matches = []

    for item in data.get("files", []):
        file_path = item.get("file")
        path = _safe_repo_path(file_path)

        if not path:
            continue

        try:
            for i, line in enumerate(path.read_text(errors="ignore").splitlines(), start=1):
                if term.lower() in line.lower():
                    matches.append({
                        "file": file_path,
                        "line": i,
                        "text": line.strip(),
                    })

                    if len(matches) >= limit:
                        return {
                            "term": term,
                            "match_count": len(matches),
                            "matches": matches,
                        }
        except Exception:
            pass

    return {
        "term": term,
        "match_count": len(matches),
        "matches": matches,
    }


def repo_recent(limit: int = 20):
    limit = max(1, min(int(limit), 100))
    data = load_repo_index_v2()

    files = []
    for item in data.get("files", []):
        path = _safe_repo_path(item.get("file", ""))
        if not path:
            continue

        try:
            stat = path.stat()
            files.append({
                "file": item.get("file"),
                "stack": item.get("stack"),
                "layer": item.get("layer"),
                "modified_epoch": stat.st_mtime,
                "size_bytes": stat.st_size,
            })
        except Exception:
            pass

    files.sort(key=lambda x: x["modified_epoch"], reverse=True)

    return {
        "limit": limit,
        "file_count": len(files),
        "recent_files": files[:limit],
    }


def repo_functions(path_text: str):
    data = load_repo_index_v2()

    for item in data.get("files", []):
        if item.get("file") == path_text.strip():
            return {
                "found": True,
                "file": item.get("file"),
                "stack": item.get("stack"),
                "layer": item.get("layer"),
                "function_count": len(item.get("functions", [])),
                "class_count": len(item.get("classes", [])),
                "functions": item.get("functions", []),
                "classes": item.get("classes", []),
            }

    return {
        "found": False,
        "file": path_text,
        "functions": [],
        "classes": [],
    }


def repo_stack_map():
    data = load_repo_index_v2()
    by_stack = data.get("by_stack", {})

    return {
        "stack_count": len(by_stack),
        "stacks": [
            {
                "stack": stack,
                "file_count": len(files),
                "files": files[:50],
            }
            for stack, files in sorted(by_stack.items())
        ],
    }


def repo_deps(path_text: str):
    path_text = path_text.strip()
    data = load_repo_index_v2()

    target = None
    for item in data.get("files", []):
        if item.get("file") == path_text:
            target = item
            break

    if not target:
        return {
            "found": False,
            "file": path_text,
            "imports": [],
            "imported_by": [],
        }

    imports = target.get("imports", [])

    imported_by = []
    module_hint = path_text.replace("/", ".").replace(".py", "")

    for item in data.get("files", []):
        if item.get("file") == path_text:
            continue

        item_imports = item.get("imports", [])

        if module_hint in item_imports or any(path_text.endswith(x.replace(".", "/") + ".py") for x in item_imports):
            imported_by.append({
                "file": item.get("file"),
                "stack": item.get("stack"),
                "layer": item.get("layer"),
            })

    return {
        "found": True,
        "file": path_text,
        "stack": target.get("stack"),
        "layer": target.get("layer"),
        "imports": imports,
        "import_count": len(imports),
        "imported_by": imported_by,
        "imported_by_count": len(imported_by),
    }


DEPENDENCY_GRAPH_V1 = ROOT / "runtime" / "repo_memory" / "dependency_graph_v1.json"


def load_dependency_graph_v1():
    return _load_json(DEPENDENCY_GRAPH_V1, {
        "nodes": [],
        "edges": [],
        "top_imported": [],
        "top_importers": [],
    })


def repo_hotspots(limit: int = 15):
    limit = max(1, min(int(limit), 50))
    graph = load_dependency_graph_v1()

    hotspots = []

    for node in graph.get("nodes", []):
        in_degree = int(node.get("in_degree", 0))
        out_degree = int(node.get("out_degree", 0))
        total_degree = in_degree + out_degree

        if total_degree <= 0:
            continue

        if in_degree >= 5 and out_degree >= 5:
            risk = "HIGH_BIDIRECTIONAL_HUB"
        elif out_degree >= 8:
            risk = "HIGH_ORCHESTRATOR_COUPLING"
        elif in_degree >= 8:
            risk = "HIGH_SHARED_DEPENDENCY"
        elif total_degree >= 6:
            risk = "MEDIUM_COUPLING"
        else:
            risk = "LOW"

        hotspots.append({
            "file": node.get("id"),
            "stack": node.get("stack"),
            "layer": node.get("layer"),
            "in_degree": in_degree,
            "out_degree": out_degree,
            "total_degree": total_degree,
            "function_count": node.get("function_count", 0),
            "class_count": node.get("class_count", 0),
            "risk": risk,
        })

    hotspots.sort(
        key=lambda x: (
            x["total_degree"],
            x["out_degree"],
            x["in_degree"],
        ),
        reverse=True,
    )

    return {
        "limit": limit,
        "hotspot_count": len(hotspots),
        "hotspots": hotspots[:limit],
    }


COMPONENT_OVERLAY_V1 = ROOT / "runtime" / "repo_memory" / "component_overlay_v1.json"

def load_component_overlay_v1():
    return _load_json(COMPONENT_OVERLAY_V1, {"components": {}, "component_edges": {}})

def repo_component_hotspots(limit: int = 15):
    limit = max(1, min(int(limit), 50))
    data = load_component_overlay_v1()
    rows = []
    for name, meta in data.get("components", {}).items():
        in_degree = int(meta.get("in_degree", 0))
        out_degree = int(meta.get("out_degree", 0))
        total = in_degree + out_degree
        if total <= 0:
            continue
        rows.append({
            "component": name,
            "stack": meta.get("stack"),
            "canonical_layer": meta.get("canonical_layer"),
            "file_count": len(meta.get("files", [])),
            "in_degree": in_degree,
            "out_degree": out_degree,
            "total_degree": total,
            "risk": "HIGH" if total >= 8 else "MEDIUM" if total >= 4 else "LOW",
        })
    rows.sort(key=lambda x: (x["total_degree"], x["out_degree"], x["in_degree"]), reverse=True)
    return {"limit": limit, "hotspot_count": len(rows), "hotspots": rows[:limit]}


DIFF_CLASSIFICATION_V1 = ROOT / "runtime" / "repo_memory" / "runtime_static_diff_classification_v1.json"


def load_diff_classification_v1():
    return _load_json(DIFF_CLASSIFICATION_V1, {
        "runtime_only_count": 0,
        "static_only_count": 0,
        "shared_count": 0,
        "drift_count": 0,
        "drift_edges": [],
    })


def architecture_drift():
    data = load_diff_classification_v1()
    drift_count = int(data.get("drift_count", 0))
    return {
        "status": "pass" if drift_count == 0 else "fail",
        "drift_count": drift_count,
        "runtime_only_count": data.get("runtime_only_count", 0),
        "static_only_count": data.get("static_only_count", 0),
        "shared_count": data.get("shared_count", 0),
        "drift_edges": data.get("drift_edges", []),
    }


ARCHITECTURE_DASHBOARD_TXT = ROOT / "runtime" / "repo_memory" / "architecture_drift_dashboard_v1.txt"
ARCHITECTURE_DASHBOARD_JSON = ROOT / "runtime" / "repo_memory" / "architecture_drift_dashboard_v1.json"


def architecture_dashboard():
    data = _load_json(ARCHITECTURE_DASHBOARD_JSON, {})
    text = ARCHITECTURE_DASHBOARD_TXT.read_text(errors="ignore") if ARCHITECTURE_DASHBOARD_TXT.exists() else ""

    return {
        "found": bool(data) or bool(text),
        "status": data.get("architecture_health", {}).get("status"),
        "drift_count": data.get("architecture_health", {}).get("drift_count"),
        "summary_text": text,
        "dashboard": data,
    }
