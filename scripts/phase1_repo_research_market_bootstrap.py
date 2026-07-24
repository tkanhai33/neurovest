from pathlib import Path
import ast
import json
from datetime import datetime

ROOT = Path(".").resolve()
RUNTIME = ROOT / "runtime"
REPO_INDEX_DIR = RUNTIME / "repo_memory"
RESEARCH_DIR = RUNTIME / "research_db"
MARKET_DIR = RUNTIME / "market_warehouse"

for d in [REPO_INDEX_DIR, RESEARCH_DIR, MARKET_DIR]:
    d.mkdir(parents=True, exist_ok=True)

IGNORE = {".venv", "venv", "__pycache__", ".git", "node_modules", ".next", "quarantine_artifacts"}

def allowed(path: Path):
    return not any(part in IGNORE for part in path.parts)

def index_python_file(path: Path):
    rel = str(path.relative_to(ROOT))
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except Exception as e:
        return {"file": rel, "error": str(e), "functions": [], "classes": [], "imports": []}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    stack = "unknown"
    parts = path.parts
    if "stacks" in parts:
        i = parts.index("stacks")
        if i + 1 < len(parts):
            stack = parts[i + 1]

    return {
        "file": rel,
        "stack": stack,
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "imports": sorted(set(i for i in imports if i)),
    }

def build_repo_memory():
    files = [
        index_python_file(p)
        for p in ROOT.rglob("*.py")
        if allowed(p) and ("backend/app" in str(p) or str(p).startswith(str(ROOT / "generate_wire_graph.py")))
    ]

    out = {
        "generated_at": datetime.utcnow().isoformat(),
        "file_count": len(files),
        "files": files,
    }

    (REPO_INDEX_DIR / "repo_index.json").write_text(json.dumps(out, indent=2))
    print(f"✔ Repo memory index written: {REPO_INDEX_DIR / 'repo_index.json'}")

def seed_research_db():
    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "categories": {
            "math_algebra": [
                {
                    "title": "Linear equation",
                    "formula": "ax + b = 0",
                    "use_case": "simple price relationship modeling"
                },
                {
                    "title": "Slope",
                    "formula": "m = (y2 - y1) / (x2 - x1)",
                    "use_case": "trend direction and rate of change"
                }
            ],
            "math_statistics": [
                {
                    "title": "Mean",
                    "formula": "mean = sum(x) / n",
                    "use_case": "average price and return estimation"
                },
                {
                    "title": "Variance",
                    "formula": "variance = sum((x - mean)^2) / n",
                    "use_case": "volatility measurement"
                }
            ],
            "finance_models": [
                {
                    "title": "Return",
                    "formula": "return = (current_price - previous_price) / previous_price",
                    "use_case": "strategy performance scoring"
                },
                {
                    "title": "Drawdown",
                    "formula": "drawdown = (peak - current_value) / peak",
                    "use_case": "risk guard supervision"
                }
            ],
            "trading_research": []
        }
    }

    (RESEARCH_DIR / "research_seed.json").write_text(json.dumps(data, indent=2))
    print(f"✔ Research seed written: {RESEARCH_DIR / 'research_seed.json'}")

def seed_market_warehouse():
    symbols = ["AAPL", "NVDA", "TSLA", "MSFT", "RY.TO", "TD.TO", "VFV.TO", "VUN.TO"]

    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "source": "yfinance",
        "symbols": [
            {
                "symbol": s,
                "enabled": True,
                "history_status": "pending",
                "live_status": "pending"
            }
            for s in symbols
        ]
    }

    (MARKET_DIR / "symbol_registry.json").write_text(json.dumps(data, indent=2))
    print(f"✔ Market symbol registry written: {MARKET_DIR / 'symbol_registry.json'}")

def main():
    print("🧠 PHASE 1 BOOTSTRAP: repo memory + research db + market warehouse")
    build_repo_memory()
    seed_research_db()
    seed_market_warehouse()
    print("✔ Phase 1 bootstrap complete")

if __name__ == "__main__":
    main()
