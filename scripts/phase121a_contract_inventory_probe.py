#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

PHASE = "121A_CONTRACT_INVENTORY_PROBE"

OUT_DIR = ARCH / "contract_inventory_probe"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "121A_contract_inventory_probe_latest.json"
OUT_TXT = OUT_DIR / "121A_contract_inventory_probe_latest.txt"

SEARCH_ROOTS = [
    ROOT / "backend/app/stacks/strategy_candidate_sandbox",
    ROOT / "backend/app/stacks/learning_research",
    ROOT / "backend/app/stacks/strategy",
    ROOT / "backend/app/stacks/runtime",
    ROOT / "backend/app/spine",
]

KEYWORDS = [
    "artifact",
    "contract",
    "replay",
    "training",
    "decision",
    "reward",
    "feature",
    "strategy",
    "candidate",
    "manifest",
]

files = []

for base in SEARCH_ROOTS:
    if not base.exists():
        continue

    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".json", ".txt", ".md"}:
            continue

        rel = str(path.relative_to(ROOT))
        name_hit = any(k in path.name.lower() for k in KEYWORDS)

        text = ""
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

        content_hits = [k for k in KEYWORDS if k in text.lower()]
        if name_hit or content_hits:
            files.append({
                "path": rel,
                "suffix": path.suffix,
                "name_hit": name_hit,
                "content_hits": content_hits[:20],
                "size_bytes": path.stat().st_size,
            })

files = sorted(files, key=lambda x: x["path"])

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "search_roots": [str(p) for p in SEARCH_ROOTS],
    "keywords": KEYWORDS,
    "files_found": len(files),
    "files": files,
    "recommended_next_phase": "121B_CONTRACT_SHAPE_INSPECTION",
    "certified": len(files) > 0,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"files_found: {len(files)}",
        "",
        "Top matches:",
        *[f"- {f['path']} :: {','.join(f['content_hits'][:8])}" for f in files[:80]],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "files_found": len(files),
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
    "recommended_next_phase": result["recommended_next_phase"],
}, indent=2))
