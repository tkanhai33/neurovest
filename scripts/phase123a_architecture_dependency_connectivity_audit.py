#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime, UTC
import ast
import json
from collections import defaultdict

ROOT = Path(".").resolve()

OUT_ROOT = ROOT / "runtime" / "architecture_intelligence"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_ROOT / "123A_dependency_graph.json"
OUT_STACK = OUT_ROOT / "123A_stack_health.json"
OUT_LAYER = OUT_ROOT / "123A_layer_health.json"
OUT_ORPHAN = OUT_ROOT / "123A_orphans.json"
OUT_PRIORITY = OUT_ROOT / "123A_build_priority.json"
OUT_ROADMAP = OUT_ROOT / "123A_master_roadmap.json"
OUT_REPORT = OUT_ROOT / "123A_report.txt"

STACK_ROOT = ROOT / "backend/app/stacks"

IGNORE = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
}

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

##########################################################

def ignored(path):
    return any(part in IGNORE for part in path.parts)

##########################################################

dependency_graph=[]
stack_health={}
layer_health=defaultdict(lambda:{
    "files":0,
    "functions":0,
    "classes":0,
    "imports":0,
})

orphans=[]
priority=[]
roadmap=[]

##########################################################

for stack in sorted(STACK_ROOT.iterdir()):

    if not stack.is_dir():
        continue

    stack_name=stack.name

    info={
        "layers":{},
        "functions":0,
        "classes":0,
        "imports":0,
        "python_files":0,
        "missing_layers":[],
    }

    for layer in LAYERS:

        dirs=[d for d in stack.glob(layer+"*") if d.is_dir()]

        if not dirs:
            info["missing_layers"].append(layer)
            continue

        d=dirs[0]

        pyfiles=[]

        for f in d.rglob("*.py"):

            if ignored(f):
                continue

            pyfiles.append(f)

        info["layers"][layer]=len(pyfiles)

        for py in pyfiles:

            info["python_files"]+=1
            layer_health[layer]["files"]+=1

            try:

                tree=ast.parse(py.read_text(encoding="utf-8"))

                imports=[]

                funcs=[]
                classes=[]

                for node in ast.walk(tree):

                    if isinstance(node,ast.FunctionDef):
                        funcs.append(node.name)

                    elif isinstance(node,ast.AsyncFunctionDef):
                        funcs.append(node.name)

                    elif isinstance(node,ast.ClassDef):
                        classes.append(node.name)

                    elif isinstance(node,ast.Import):
                        imports.extend([n.name for n in node.names])

                    elif isinstance(node,ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                info["functions"]+=len(funcs)
                info["classes"]+=len(classes)
                info["imports"]+=len(imports)

                layer_health[layer]["functions"]+=len(funcs)
                layer_health[layer]["classes"]+=len(classes)
                layer_health[layer]["imports"]+=len(imports)

                dependency_graph.append({
                    "stack":stack_name,
                    "layer":layer,
                    "file":str(py.relative_to(ROOT)),
                    "functions":funcs,
                    "classes":classes,
                    "imports":sorted(imports),
                })

            except Exception:
                pass

    score=max(
        0,
        100-len(info["missing_layers"])*12
    )

    info["completeness"]=score

    stack_health[stack_name]=info

##########################################################

producer_keywords=[
    "feature",
    "reward",
    "artifact",
    "knowledge",
    "graph",
    "profile",
    "regime",
]

consumer_lookup=defaultdict(list)

for node in dependency_graph:

    for imp in node["imports"]:
        consumer_lookup[imp].append(node["file"])

for node in dependency_graph:

    lower=node["file"].lower()

    if any(k in lower for k in producer_keywords):

        found=False

        stem=Path(node["file"]).stem

        for imports in consumer_lookup:

            if stem in imports:
                found=True

        if not found:

            orphans.append({
                "producer":node["file"],
                "reason":"No detected consumer",
            })

##########################################################

for stack,data in stack_health.items():

    if data["missing_layers"]:

        priority.append({
            "stack":stack,
            "severity":"HIGH",
            "reason":"Missing architectural layers",
            "missing":data["missing_layers"],
        })

##########################################################

roadmap.extend([
    "Knowledge Objects",
    "Knowledge Graph",
    "Research Cross Reference",
    "Symbol Intelligence Profiles",
    "Market Regime Library",
    "Equity Curve Analytics",
    "Execution Learning",
])

##########################################################

OUT_JSON.write_text(
    json.dumps(dependency_graph,indent=2),
    encoding="utf-8"
)

OUT_STACK.write_text(
    json.dumps(stack_health,indent=2),
    encoding="utf-8"
)

OUT_LAYER.write_text(
    json.dumps(layer_health,indent=2),
    encoding="utf-8"
)

OUT_ORPHAN.write_text(
    json.dumps(orphans,indent=2),
    encoding="utf-8"
)

OUT_PRIORITY.write_text(
    json.dumps(priority,indent=2),
    encoding="utf-8"
)

OUT_ROADMAP.write_text(
    json.dumps(roadmap,indent=2),
    encoding="utf-8"
)

lines=[]

lines.append("123A_ARCHITECTURE_DEPENDENCY_CONNECTIVITY_AUDIT")
lines.append("")
lines.append("===================================================")
lines.append("STACK HEALTH")
lines.append("===================================================")

for stack,data in stack_health.items():

    lines.append("")
    lines.append(stack)
    lines.append(f"Completeness : {data['completeness']}%")
    lines.append(f"Python Files : {data['python_files']}")
    lines.append(f"Functions    : {data['functions']}")
    lines.append(f"Classes      : {data['classes']}")
    lines.append(f"Imports      : {data['imports']}")

    if data["missing_layers"]:
        lines.append("Missing Layers:")
        for l in data["missing_layers"]:
            lines.append(f"  - {l} {LAYERS[l]}")

lines.append("")
lines.append("===================================================")
lines.append("ORPHANS")
lines.append("===================================================")

if orphans:
    for o in orphans:
        lines.append(f"{o['producer']}")
else:
    lines.append("None detected")

lines.append("")
lines.append("===================================================")
lines.append("NEXT BUILD ORDER")
lines.append("===================================================")

for r in roadmap:
    lines.append(r)

OUT_REPORT.write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print(json.dumps({
    "phase":"123A_ARCHITECTURE_DEPENDENCY_CONNECTIVITY_AUDIT",
    "stacks":len(stack_health),
    "layers":len(layer_health),
    "dependency_nodes":len(dependency_graph),
    "orphans":len(orphans),
    "priority_items":len(priority),
    "report":str(OUT_REPORT),
},indent=2))
