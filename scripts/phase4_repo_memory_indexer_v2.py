#!/usr/bin/env python3
import ast
import json
from datetime import datetime, UTC
from pathlib import Path
from collections import defaultdict

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "runtime" / "repo_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "repo_index_v2.json"

IGNORE = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".next",
    "quarantine_artifacts",
    "runtime",
}


def allowed(path: Path) -> bool:
    return not any(part in IGNORE for part in path.parts)


def classify_stack(path: Path) -> str:
    parts = path.parts
    rel = str(path.relative_to(ROOT))

    if path.name in {"generate_wire_graph.py", "neuro_cli.py", "neuro_engineer.py"}:
        return "root_tooling"

    if rel.startswith("scripts/"):
        return "dev_scripts"

    if "/test/" in f"/{rel}/" or rel.startswith("backend/app/test/"):
        return "tests"

    if rel.startswith("architecture_backup/"):
        return "architecture_backup"

    if "stacks" in parts:
        i = parts.index("stacks")
        if i + 1 < len(parts):
            return parts[i + 1]

    if "core" in parts:
        return "core"

    if "schemas" in parts:
        return "schemas"

    if rel.startswith("backend/app/api/"):
        return "api_support"

    if rel.startswith("backend/app/services/"):
        return "legacy_services"

    if rel.startswith("backend/app/routers/"):
        return "legacy_routers"

    if rel.startswith("backend/app/analysis/"):
        return "analysis"

    if rel.startswith("backend/app/snaptrade/"):
        return "snaptrade_legacy"

    if path.name == "main.py":
        return "api_gateway"

    if path.name == "__init__.py":
        return "package_marker"

    return "unknown"


def classify_layer(path: Path) -> str:
    rel = str(path.relative_to(ROOT))

    if path.name in {"generate_wire_graph.py", "neuro_cli.py", "neuro_engineer.py"}:
        return "tooling"

    if rel.startswith("scripts/"):
        return "script"

    if "/test/" in f"/{rel}/" or rel.startswith("backend/app/test/"):
        return "test"

    if rel.startswith("architecture_backup/"):
        return "legacy_archive"

    if "/stacks/" in f"/{rel}":
        return "stack"

    if "/core/" in f"/{rel}":
        return "core"

    if "/schemas/" in f"/{rel}":
        return "schema"

    if rel.endswith("main.py"):
        return "api_presentation"

    if rel.startswith("backend/app/api/"):
        return "api_support"

    if rel.startswith("backend/app/services/") or rel.startswith("backend/app/routers/"):
        return "legacy_support"

    if rel.startswith("backend/app/analysis/"):
        return "analysis"

    if rel.startswith("backend/app/snaptrade/"):
        return "legacy_adapter"

    if path.name == "__init__.py":
        return "package_marker"

    return "unknown"




def classify_canonical_layer(path: Path) -> str:
    rel = str(path.relative_to(ROOT))

    if rel.startswith("backend/app/main.py"):
        return "L5_api_presentation"

    if rel.startswith("backend/app/api/") or rel.startswith("backend/app/routers/"):
        return "L5_api_presentation"

    if rel.startswith("backend/app/test/") or "/test/" in f"/{rel}/":
        return "L7_tests"

    if rel.startswith("scripts/"):
        if any(x in rel for x in ["certification", "phase", "audit", "repair", "quarantine", "migration", "normalization", "relocator", "enforcement"]):
            return "L9_devops"
        return "L8_tooling"

    if rel.startswith("architecture_backup/"):
        return "L9_devops"

    if path.name in {"generate_wire_graph.py", "neuro_cli.py", "neuro_engineer.py", "neuro"}:
        return "L8_tooling"

    if path.name == "__init__.py":
        return "L8_tooling"

    if rel.startswith("backend/app/services/") or rel.startswith("backend/app/routers/"):
        return "L5_api_presentation"

    if rel.startswith("backend/app/analysis/"):
        return "L7_tests"

    if rel.startswith("backend/app/snaptrade/"):
        return "L0_external_adapter"

    if rel.startswith("backend/app/schemas/"):
        return "L2_domain"

    if rel.startswith("backend/app/core/global_firewall") or rel.startswith("backend/app/core/runtime_firewall"):
        return "L1_security_auth_safety"

    if rel.startswith("backend/app/core/"):
        return "L4_runtime_orchestration"

    if "/stacks/auth_identity/" in f"/{rel}":
        return "L1_security_auth_safety"

    if "/stacks/snaptrade/" in f"/{rel}":
        return "L0_external_adapter"

    if "/stacks/market_data/yfinance" in f"/{rel}" or "/stacks/market_data/provider" in f"/{rel}":
        return "L0_external_adapter"

    if "/stacks/market_data/" in f"/{rel}":
        if any(x in rel for x in ["feed", "price", "bars", "market_session", "market_data_service", "provider_cache"]):
            return "L2_domain"
        return "L0_external_adapter"

    if "/stacks/notification/" in f"/{rel}":
        return "L0_external_adapter"

    if "/stacks/execution/" in f"/{rel}":
        if any(x in rel for x in ["broker.py", "paper_broker.py", "sandbox", "runtime", "executor"]):
            return "L4_runtime_orchestration"
        return "L2_domain"

    if "/stacks/chat_public/" in f"/{rel}":
        if rel.endswith("chat_api.py"):
            return "L5_api_presentation"
        return "L4_runtime_orchestration"

    if "/stacks/wolfden_ai/" in f"/{rel}":
        return "L4_runtime_orchestration"

    if "/stacks/events/" in f"/{rel}":
        return "L4_runtime_orchestration"

    if "/stacks/journal_ledger/" in f"/{rel}":
        return "L3_service_facade"

    if "/stacks/portfolio/" in f"/{rel}":
        return "L2_domain"

    if "/stacks/risk/" in f"/{rel}":
        if any(x in rel for x in ["kill_switch", "drawdown_guard", "loss_streak_guard"]):
            return "L1_security_auth_safety"
        return "L2_domain"

    if "/stacks/strategy/" in f"/{rel}":
        return "L2_domain"

    if "/stacks/learning_research/" in f"/{rel}":
        return "L2_domain"

    if "/stacks/db_model/" in f"/{rel}":
        return "L2_domain"

    return "L7_tests"


def classify_component(path: Path) -> str:
    rel = str(path.relative_to(ROOT))
    name = path.stem

    if "paper_broker" in rel:
        return "sandbox_paper_broker"

    if "sandbox" in rel:
        return "sandbox_runtime"

    if "regime" in rel:
        return "regime_simulation"

    if "fill_engine" in rel:
        return "execution_fill_engine"

    if "accounting_engine" in rel:
        return "execution_accounting"

    if "drawdown_guard" in rel:
        return "risk_drawdown_guard"

    if "kill_switch" in rel:
        return "risk_kill_switch"

    if "chat_runtime" in rel:
        return "chat_runtime"

    if "context_loader" in rel:
        return "chat_context_loader"

    if "cognitive_graph_state" in rel:
        return "runtime_graph_state"

    if "broker.py" in rel and "/events/" in rel:
        return "event_bus_broker"

    return name


def parse_python(path: Path):
    rel = str(path.relative_to(ROOT))

    try:
        source = path.read_text(errors="ignore")
        tree = ast.parse(source)
    except Exception as e:
        return {
            "file": rel,
            "error": str(e),
            "stack": classify_stack(path),
            "layer": classify_layer(path),
            "canonical_layer": classify_canonical_layer(path),
            "component": classify_component(path),
            "functions": [],
            "classes": [],
            "imports": [],
        }

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "async": isinstance(node, ast.AsyncFunctionDef),
            })

        elif isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno,
            })

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {
        "file": rel,
        "stack": classify_stack(path),
        "layer": classify_layer(path),
        "canonical_layer": classify_canonical_layer(path),
        "component": classify_component(path),
        "functions": functions,
        "classes": classes,
        "imports": sorted(set(imports)),
    }


def main():
    files = [
        parse_python(p)
        for p in ROOT.rglob("*.py")
        if allowed(p)
    ]

    by_stack = defaultdict(list)
    by_layer = defaultdict(list)
    symbol_lookup = defaultdict(list)

    for item in files:
        by_stack[item["stack"]].append(item["file"])
        by_layer[item["layer"]].append(item["file"])

        for fn in item.get("functions", []):
            symbol_lookup[fn["name"]].append({
                "type": "function",
                "file": item["file"],
                "line": fn["line"],
                "stack": item["stack"],
                "layer": item["layer"],
                "canonical_layer": item.get("canonical_layer"),
                "component": item.get("component"),
            })

        for cls in item.get("classes", []):
            symbol_lookup[cls["name"]].append({
                "type": "class",
                "file": item["file"],
                "line": cls["line"],
                "stack": item["stack"],
                "layer": item["layer"],
                "canonical_layer": item.get("canonical_layer"),
                "component": item.get("component"),
            })

    report = {
        "phase": "4_REPO_MEMORY_INDEXER_V2",
        "generated_at": datetime.now(UTC).isoformat(),
        "file_count": len(files),
        "stack_count": len(by_stack),
        "layer_count": len(by_layer),
        "symbol_count": len(symbol_lookup),
        "files": files,
        "by_stack": dict(by_stack),
        "by_layer": dict(by_layer),
        "symbol_lookup": dict(symbol_lookup),
    }

    OUT_JSON.write_text(json.dumps(report, indent=2))

    print(json.dumps({
        "phase": report["phase"],
        "file_count": report["file_count"],
        "stack_count": report["stack_count"],
        "layer_count": report["layer_count"],
        "symbol_count": report["symbol_count"],
        "output": str(OUT_JSON),
    }, indent=2))


if __name__ == "__main__":
    main()
