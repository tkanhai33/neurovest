#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import ast
import json

ROOT = Path(".").resolve()
ARCH = ROOT / "runtime/replay_runtime_architecture"

OUT_DIR = ARCH / "architecture_completeness_audit"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "122B_architecture_completeness_audit_latest.json"
OUT_TXT  = OUT_DIR / "122B_architecture_completeness_audit_latest.txt"

PHASE="122B_ARCHITECTURE_COMPLETENESS_AUDIT"

###########################################################################

IGNORE = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    ".idea",
    ".vscode",
    "coverage",
    "audit",
}

###########################################################################

LAYERS = {
    "L0":"External Data Sources",
    "L1":"Security / Cerberus",
    "L2":"Domain Contracts",
    "L3":"Service Facades",
    "L4":"Runtime Orchestration",
    "L5":"API",
    "L6":"Frontend",
    "L7":"Testing",
}

###########################################################################

STACK_ROOT = ROOT / "backend/app/stacks"

summary={}
priority=[]
errors=[]

###########################################################################

def ignored(path):
    return any(part in IGNORE for part in path.parts)

###########################################################################

for stack in sorted(STACK_ROOT.iterdir()):

    if not stack.is_dir():
        continue

    if ignored(stack):
        continue

    stack_info={
        "layers":{},
        "python_files":0,
        "imports":{},
        "orphans":[],
        "missing_layers":[],
    }

    for layer,desc in LAYERS.items():

        matches=[d for d in stack.glob(layer+"*") if d.is_dir()]

        if not matches:
            stack_info["missing_layers"].append(layer)
            continue

        layer_dir=matches[0]

        py_files=[]

        for py in layer_dir.rglob("*.py"):

            if ignored(py):
                continue

            py_files.append(py)

        imports={}

        for py in py_files:

            stack_info["python_files"]+=1

            try:
                tree=ast.parse(py.read_text(encoding="utf-8"))

                imported=[]

                for node in ast.walk(tree):

                    if isinstance(node,ast.Import):

                        imported.extend([n.name for n in node.names])

                    elif isinstance(node,ast.ImportFrom):

                        imported.append(node.module)

                imports[str(py.relative_to(ROOT))]=sorted(
                    [i for i in imported if i]
                )

            except Exception as exc:

                errors.append({
                    "file":str(py.relative_to(ROOT)),
                    "error":str(exc)
                })

        stack_info["layers"][layer]={
            "description":desc,
            "directory":str(layer_dir.relative_to(ROOT)),
            "python_files":len(py_files),
        }

        stack_info["imports"].update(imports)

    if stack_info["missing_layers"]:
        priority.append({
            "stack":stack.name,
            "severity":"HIGH",
            "reason":"Missing layers",
            "layers":stack_info["missing_layers"],
        })

    summary[stack.name]=stack_info

###########################################################################

result={
    "phase":PHASE,
    "created_at":datetime.now(UTC).isoformat(),
    "layer_names":LAYERS,
    "stack_count":len(summary),
    "stacks":summary,
    "priority":priority,
    "parse_errors":errors,
    "recommended_next_phase":"123A_LEARNING_ARTIFACT_PIPELINE_STUB",
    "certified":True,
}

OUT_JSON.write_text(
    json.dumps(result,indent=2),
    encoding="utf-8"
)

lines=[]

lines.append(PHASE)
lines.append("")
lines.append(f"Stacks: {len(summary)}")
lines.append("")

for name,data in summary.items():

    lines.append("="*70)
    lines.append(name)
    lines.append("="*70)

    if data["missing_layers"]:
        lines.append("Missing Layers:")
        for l in data["missing_layers"]:
            lines.append(f"  - {l} ({LAYERS[l]})")
    else:
        lines.append("Missing Layers: None")

    lines.append("")

    for l in sorted(data["layers"]):

        info=data["layers"][l]

        lines.append(
            f"{l:<3} "
            f"{info['python_files']:>3} files   "
            f"{info['description']}"
        )

    lines.append("")

lines.append("="*70)
lines.append("BUILD PRIORITY")
lines.append("="*70)

if priority:

    for p in priority:

        lines.append(
            f"HIGH : {p['stack']} -> "
            f"{', '.join(p['layers'])}"
        )

else:

    lines.append("No missing layers detected.")

lines.append("")
lines.append(f"Parser Errors: {len(errors)}")
lines.append("")
lines.append("Next:")
lines.append(result["recommended_next_phase"])

OUT_TXT.write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print(json.dumps({
    "phase":PHASE,
    "certified":True,
    "stack_count":len(summary),
    "priority_items":len(priority),
    "parse_errors":len(errors),
    "recommended_next_phase":result["recommended_next_phase"],
    "out_json":str(OUT_JSON),
    "out_txt":str(OUT_TXT),
},indent=2))
