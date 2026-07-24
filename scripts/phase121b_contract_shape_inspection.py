#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, UTC
import ast
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime" / "replay_runtime_architecture"

SOURCE = ARCH / "contract_inventory_probe/121A_contract_inventory_probe_latest.json"

OUT_DIR = ARCH / "contract_shape_inspection"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "121B_contract_shape_inspection_latest.json"
OUT_TXT = OUT_DIR / "121B_contract_shape_inspection_latest.txt"

PHASE = "121B_CONTRACT_SHAPE_INSPECTION"

def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

source = read_json(SOURCE)

code_files = []
for item in source.get("files", []):
    path = ROOT / item["path"]
    if path.suffix != ".py":
        continue
    if "/research_data/" in item["path"]:
        continue
    code_files.append(path)

shapes = []
errors = []

for path in sorted(code_files):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(text)

        classes = []
        functions = []
        constants = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants.append(target.id)

        shapes.append({
            "path": str(path.relative_to(ROOT)),
            "classes": classes,
            "functions": functions,
            "constants": constants,
            "has_contract_name": "contract" in path.name.lower() or "contract" in text.lower(),
            "has_artifact_name": "artifact" in path.name.lower() or "artifact" in text.lower(),
            "has_reward_name": "reward" in path.name.lower() or "reward" in text.lower(),
            "has_feature_name": "feature" in path.name.lower() or "feature" in text.lower(),
            "has_training_name": "training" in path.name.lower() or "training" in text.lower(),
            "has_replay_name": "replay" in path.name.lower() or "replay" in text.lower(),
        })

    except Exception as exc:
        errors.append({
            "path": str(path.relative_to(ROOT)),
            "error": str(exc),
        })

high_value = [
    s for s in shapes
    if s["has_contract_name"]
    or s["has_artifact_name"]
    or s["has_reward_name"]
    or s["has_feature_name"]
    or s["has_training_name"]
    or s["has_replay_name"]
]

checks = {
    "source_exists": SOURCE.exists(),
    "source_certified": source.get("certified") is True,
    "code_files_found": len(code_files) > 0,
    "shapes_extracted": len(shapes) > 0,
    "high_value_shapes_found": len(high_value) > 0,
    "parse_errors_low_or_zero": len(errors) == 0,
    "db_write_blocked": True,
    "training_blocked": True,
    "broker_live_blocked": True,
}

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "code_files_scanned": len(code_files),
    "shapes_extracted": len(shapes),
    "high_value_count": len(high_value),
    "high_value_shapes": high_value,
    "all_shapes": shapes,
    "errors": errors,
    "checks": checks,
    "recommended_next_phase": "121C_LEARNING_ARTIFACT_CONTRACT_REPLICATION_PLAN",
    "certified": all(checks.values()),
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_TXT.write_text(
    "\n".join([
        PHASE,
        "",
        f"certified: {result['certified']}",
        f"code_files_scanned: {len(code_files)}",
        f"shapes_extracted: {len(shapes)}",
        f"high_value_count: {len(high_value)}",
        f"errors: {len(errors)}",
        "",
        "High-value shapes:",
        *[
            f"- {s['path']} :: classes={s['classes']} functions={s['functions'][:10]} constants={s['constants'][:10]}"
            for s in high_value[:80]
        ],
        "",
        "Next:",
        result["recommended_next_phase"],
    ]),
    encoding="utf-8",
)

print(json.dumps({
    "phase": PHASE,
    "certified": result["certified"],
    "code_files_scanned": len(code_files),
    "shapes_extracted": len(shapes),
    "high_value_count": len(high_value),
    "errors": len(errors),
    "recommended_next_phase": result["recommended_next_phase"],
    "out_json": str(OUT_JSON),
    "out_txt": str(OUT_TXT),
}, indent=2))
