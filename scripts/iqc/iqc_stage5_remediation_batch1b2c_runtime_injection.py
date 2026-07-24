#!/usr/bin/env python3

from __future__ import annotations

import ast
import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

WOLFDEN_ROOT = (
    BACKEND_ROOT
    / "stacks"
    / "wolfden_ai"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2c"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c_freeze_latest.json"
)

IMPORT_AUDIT = (
    ROOT
    / "runtime"
    / "hardening"
    / "workstream1"
    / "import_cycle_audit_latest.json"
)

TEST_LOG = (
    OUTPUT_DIR
    / "whole_backend_tests_latest.log"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@dataclass(frozen=True)
class ModuleRecord:
    module: str
    path: str
    imports: tuple[str, ...]


def module_name(
    path: Path,
) -> str:
    relative = path.relative_to(
        ROOT
    ).with_suffix("")

    parts = list(
        relative.parts
    )

    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def resolve_internal_module(
    imported: str,
    known_modules: set[str],
) -> str | None:
    if imported in known_modules:
        return imported

    pieces = imported.split(".")

    while len(pieces) > 1:
        pieces.pop()

        candidate = ".".join(
            pieces
        )

        if candidate in known_modules:
            return candidate

    aliases = (
        "backend.app.",
        "app.",
    )

    for prefix in aliases:
        if not imported.startswith(prefix):
            continue

        tail = imported[
            len(prefix):
        ]

        candidates = (
            f"backend.app.{tail}",
            f"app.{tail}",
        )

        for candidate in candidates:
            if candidate in known_modules:
                return candidate

    return None


def rendered_call(
    node: ast.Call,
) -> str:
    expression = node.func
    parts: list[str] = []

    while isinstance(
        expression,
        ast.Attribute,
    ):
        parts.append(
            expression.attr
        )

        expression = expression.value

    if isinstance(
        expression,
        ast.Name,
    ):
        parts.append(
            expression.id
        )

    if not parts:
        try:
            return ast.unparse(
                node.func
            )

        except Exception:
            return "<unresolved>"

    return ".".join(
        reversed(parts)
    )


def line_text(
    source: str,
    line: int,
) -> str:
    lines = source.splitlines()

    if not (
        1 <= line <= len(lines)
    ):
        return ""

    return lines[
        line - 1
    ].strip()


python_files = sorted(
    path
    for path in BACKEND_ROOT.rglob(
        "*.py"
    )
    if "__pycache__" not in path.parts
)

known_modules = {
    module_name(path)
    for path in python_files
}

path_by_module = {
    module_name(path): path
    for path in python_files
}

records: dict[str, ModuleRecord] = {}

syntax_errors: list[dict[str, Any]] = []

ast_by_module: dict[str, ast.AST] = {}

source_by_module: dict[str, str] = {}

for path in python_files:
    module = module_name(path)

    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    source_by_module[
        module
    ] = source

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as error:
        syntax_errors.append(
            {
                "module": module,
                "path": path.relative_to(
                    ROOT
                ).as_posix(),
                "line": error.lineno,
                "message": str(error),
            }
        )

        continue

    ast_by_module[
        module
    ] = tree

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                resolved = resolve_internal_module(
                    alias.name,
                    known_modules,
                )

                if resolved:
                    imports.add(
                        resolved
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imported = (
                node.module or ""
            )

            resolved = resolve_internal_module(
                imported,
                known_modules,
            )

            if resolved:
                imports.add(
                    resolved
                )

    records[module] = ModuleRecord(
        module=module,
        path=path.relative_to(
            ROOT
        ).as_posix(),
        imports=tuple(
            sorted(imports)
        ),
    )

assert syntax_errors == [], (
    "Active backend syntax errors prevent "
    "runtime-injection qualification"
)

graph = {
    module: set(
        record.imports
    )
    for module, record in records.items()
}

reverse_graph: dict[
    str,
    set[str],
] = defaultdict(set)

for source_module, targets in graph.items():
    for target in targets:
        reverse_graph[
            target
        ].add(
            source_module
        )

wolfden_modules = sorted(
    module
    for module, path in path_by_module.items()
    if WOLFDEN_ROOT in path.parents
    or path == WOLFDEN_ROOT
)

assert wolfden_modules, (
    "No Wolfden modules were resolved"
)

reachable: set[str] = set()
queue = deque(
    wolfden_modules
)

while queue:
    module = queue.popleft()

    if module in reachable:
        continue

    reachable.add(
        module
    )

    for target in graph.get(
        module,
        set(),
    ):
        if target not in reachable:
            queue.append(
                target
            )

candidate_markers = (
    "ollama",
    "local_model",
    "localmodel",
    "llm",
    "language_model",
    "inference",
    "model_client",
    "chat_client",
)

excluded_candidate_markers = (
    "test_",
    ".tests.",
    "contract",
    "migration",
)

candidate_modules = []

for module, path in path_by_module.items():
    lowered = (
        module
        + " "
        + path.as_posix()
    ).lower()

    if not any(
        marker in lowered
        for marker in candidate_markers
    ):
        continue

    if any(
        marker in lowered
        for marker in excluded_candidate_markers
    ):
        continue

    candidate_modules.append(
        module
    )

candidate_modules = sorted(
    set(candidate_modules)
)

candidate_evidence: list[
    dict[str, Any]
] = []

for module in candidate_modules:
    tree = ast_by_module.get(
        module
    )

    if tree is None:
        continue

    source = source_by_module[
        module
    ]

    functions = []

    classes = []

    calls = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.append(
                {
                    "name": node.name,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                    "line": node.lineno,
                    "parameters": [
                        argument.arg
                        for argument in (
                            list(
                                node.args.posonlyargs
                            )
                            + list(
                                node.args.args
                            )
                            + list(
                                node.args.kwonlyargs
                            )
                        )
                    ],
                    "return_annotation": (
                        ast.unparse(
                            node.returns
                        )
                        if node.returns
                        is not None
                        else None
                    ),
                }
            )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            rendered = rendered_call(
                node
            )

            lowered_call = rendered.lower()

            if any(
                marker in lowered_call
                for marker in (
                    "generate",
                    "chat",
                    "complete",
                    "invoke",
                    "infer",
                    "predict",
                    "ollama",
                )
            ):
                calls.append(
                    {
                        "call": rendered,
                        "line": node.lineno,
                        "source": line_text(
                            source,
                            node.lineno,
                        ),
                    }
                )

    candidate_evidence.append(
        {
            "module": module,
            "path": records[
                module
            ].path,
            "reachable_from_wolfden": (
                module in reachable
            ),
            "direct_wolfden_importers": sorted(
                source_module
                for source_module in reverse_graph.get(
                    module,
                    set(),
                )
                if source_module
                in wolfden_modules
            ),
            "all_importers": sorted(
                reverse_graph.get(
                    module,
                    set(),
                )
            ),
            "functions": sorted(
                functions,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "classes": sorted(
                classes,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "model_like_calls": sorted(
                calls,
                key=lambda item: (
                    item["line"],
                    item["call"],
                ),
            ),
        }
    )

injection_parameter_markers = {
    "client",
    "model",
    "llm",
    "adapter",
    "provider",
    "generator",
    "inference",
    "runtime",
    "invoke",
    "chat_client",
    "model_client",
}

injection_function_markers = (
    "set_",
    "configure",
    "register",
    "inject",
    "bind",
    "create",
    "build",
    "factory",
)

wolfden_injection_seams: list[
    dict[str, Any]
] = []

wolfden_forbidden_imports: list[
    dict[str, Any]
] = []

for module in wolfden_modules:
    tree = ast_by_module.get(
        module
    )

    if tree is None:
        continue

    source = source_by_module[
        module
    ]

    path = records[
        module
    ].path

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            parameters = [
                argument.arg
                for argument in (
                    list(
                        node.args.posonlyargs
                    )
                    + list(
                        node.args.args
                    )
                    + list(
                        node.args.kwonlyargs
                    )
                )
            ]

            injection_parameters = [
                parameter
                for parameter in parameters
                if any(
                    marker in parameter.lower()
                    for marker
                    in injection_parameter_markers
                )
            ]

            name_is_injection_like = any(
                node.name.lower().startswith(
                    marker
                )
                or marker in node.name.lower()
                for marker
                in injection_function_markers
            )

            if (
                injection_parameters
                or name_is_injection_like
            ):
                wolfden_injection_seams.append(
                    {
                        "module": module,
                        "path": path,
                        "kind": "function",
                        "name": node.name,
                        "line": node.lineno,
                        "async": isinstance(
                            node,
                            ast.AsyncFunctionDef,
                        ),
                        "parameters": parameters,
                        "injection_parameters": (
                            injection_parameters
                        ),
                        "source": line_text(
                            source,
                            node.lineno,
                        ),
                    }
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            initializers = [
                child
                for child in node.body
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and child.name == "__init__"
            ]

            for initializer in initializers:
                parameters = [
                    argument.arg
                    for argument in (
                        list(
                            initializer.args.posonlyargs
                        )
                        + list(
                            initializer.args.args
                        )
                        + list(
                            initializer.args.kwonlyargs
                        )
                    )
                    if argument.arg != "self"
                ]

                injection_parameters = [
                    parameter
                    for parameter in parameters
                    if any(
                        marker in parameter.lower()
                        for marker
                        in injection_parameter_markers
                    )
                ]

                if injection_parameters:
                    wolfden_injection_seams.append(
                        {
                            "module": module,
                            "path": path,
                            "kind": "constructor",
                            "name": (
                                f"{node.name}.__init__"
                            ),
                            "line": initializer.lineno,
                            "async": False,
                            "parameters": parameters,
                            "injection_parameters": (
                                injection_parameters
                            ),
                            "source": line_text(
                                source,
                                initializer.lineno,
                            ),
                        }
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imported_module = (
                node.module or ""
            )

            lowered = imported_module.lower()

            forbidden_markers = (
                ".execution",
                ".paper_trading",
                ".broker_integration",
                "snaptrade",
                "db_runtime",
                "journal_ledger",
                "sqlalchemy",
            )

            if any(
                marker in lowered
                for marker in forbidden_markers
            ):
                wolfden_forbidden_imports.append(
                    {
                        "module": module,
                        "path": path,
                        "line": node.lineno,
                        "imported_module": (
                            imported_module
                        ),
                        "names": [
                            alias.name
                            for alias in node.names
                        ],
                        "source": line_text(
                            source,
                            node.lineno,
                        ),
                    }
                )

        elif isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                lowered = alias.name.lower()

                forbidden_markers = (
                    ".execution",
                    ".paper_trading",
                    ".broker_integration",
                    "snaptrade",
                    "db_runtime",
                    "journal_ledger",
                    "sqlalchemy",
                )

                if any(
                    marker in lowered
                    for marker in forbidden_markers
                ):
                    wolfden_forbidden_imports.append(
                        {
                            "module": module,
                            "path": path,
                            "line": node.lineno,
                            "imported_module": (
                                alias.name
                            ),
                            "names": [],
                            "source": line_text(
                                source,
                                node.lineno,
                            ),
                        }
                    )

reachable_candidates = [
    item
    for item in candidate_evidence
    if item[
        "reachable_from_wolfden"
    ]
]

unreachable_candidates = [
    item
    for item in candidate_evidence
    if not item[
        "reachable_from_wolfden"
    ]
]

directly_imported_candidates = [
    item
    for item in candidate_evidence
    if item[
        "direct_wolfden_importers"
    ]
]

qualified_candidate_functions = []

for candidate in candidate_evidence:
    for function in candidate[
        "functions"
    ]:
        lowered_name = function[
            "name"
        ].lower()

        if any(
            marker in lowered_name
            for marker in (
                "generate",
                "chat",
                "complete",
                "invoke",
                "infer",
                "predict",
                "ask",
            )
        ):
            qualified_candidate_functions.append(
                {
                    "module": candidate[
                        "module"
                    ],
                    "path": candidate[
                        "path"
                    ],
                    **function,
                    "reachable_from_wolfden": (
                        candidate[
                            "reachable_from_wolfden"
                        ]
                    ),
                }
            )

runtime_injection_present = bool(
    wolfden_injection_seams
)

reachable_local_model_present = bool(
    reachable_candidates
)

direct_local_model_import_present = bool(
    directly_imported_candidates
)

forbidden_capability_count = len(
    wolfden_forbidden_imports
)

if forbidden_capability_count:
    disposition = (
        "WOLFDEN_FORBIDDEN_CAPABILITY_REMEDIATION_REQUIRED"
    )

    authorized_targets = sorted(
        {
            item["path"]
            for item in wolfden_forbidden_imports
        }
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C1 — "
        "Remove Confirmed Wolfden Forbidden Capability "
        "Dependencies Before Model Injection"
    )

elif (
    reachable_local_model_present
    and runtime_injection_present
):
    disposition = (
        "LOCAL_MODEL_INJECTION_PATH_PRESENT_REQUIRES_CONTRACT_QUALIFICATION"
    )

    authorized_targets = sorted(
        {
            item["path"]
            for item in wolfden_injection_seams
        }
        | {
            item["path"]
            for item in reachable_candidates
        }
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2D — "
        "Qualify the Existing Wolfden Local-Model "
        "Output Contract and Malformed-Output Behavior"
    )

elif (
    not reachable_local_model_present
    and runtime_injection_present
):
    disposition = (
        "INJECTION_SEAM_PRESENT_LOCAL_MODEL_BINDING_MISSING"
    )

    authorized_targets = sorted(
        {
            item["path"]
            for item in wolfden_injection_seams
        }
        | {
            item["path"]
            for item in candidate_evidence
            if item[
                "model_like_calls"
            ]
            or item[
                "functions"
            ]
        }
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C1 — "
        "Bind the Approved Local-Model Adapter Through "
        "the Existing Wolfden Injection Seam"
    )

elif (
    reachable_local_model_present
    and not runtime_injection_present
):
    disposition = (
        "LOCAL_MODEL_REACHABLE_WITHOUT_EXPLICIT_INJECTION_CONTRACT"
    )

    authorized_targets = sorted(
        {
            item["path"]
            for item in reachable_candidates
        }
        | {
            records[
                module
            ].path
            for module in wolfden_modules
        }
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C1 — "
        "Create an Explicit Immutable Wolfden "
        "Local-Model Injection Contract"
    )

else:
    disposition = (
        "LOCAL_MODEL_AND_INJECTION_PATH_BOTH_MISSING"
    )

    preferred_candidates = [
        item
        for item in candidate_evidence
        if any(
            marker in item[
                "module"
            ].lower()
            for marker in (
                "ollama",
                "local_model",
                "llm",
            )
        )
    ]

    authorized_targets = sorted(
        {
            records[
                module
            ].path
            for module in wolfden_modules
        }
        | {
            item["path"]
            for item in preferred_candidates
        }
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C1 — "
        "Create and Bind an Approved Wolfden "
        "Local-Model Runtime Injection Boundary"
    )

audit = json.loads(
    IMPORT_AUDIT.read_text(
        encoding="utf-8"
    )
)

audit_summary = audit[
    "summary"
]

assert audit_summary[
    "active_internal_unresolved"
] == 0

assert audit_summary[
    "tooling_or_relative_unresolved"
] == 0

assert audit_summary[
    "syntax_errors"
] == 0

assert audit_summary[
    "active_cycle_components"
] == 0

assert audit_summary[
    "self_cycles"
] == 0

test_text = TEST_LOG.read_text(
    encoding="utf-8",
    errors="replace",
)

import re

passed_matches = re.findall(
    r"(\d+)\s+passed",
    test_text,
)

failed_matches = re.findall(
    r"(\d+)\s+failed",
    test_text,
)

tests_passed = (
    int(
        passed_matches[-1]
    )
    if passed_matches
    else 0
)

tests_failed = (
    int(
        failed_matches[-1]
    )
    if failed_matches
    else 0
)

assert tests_passed >= 181
assert tests_failed == 0

source_manifest = []

for path in python_files:
    data = path.read_bytes()

    source_manifest.append(
        {
            "path": path.relative_to(
                ROOT
            ).as_posix(),
            "sha256": hashlib.sha256(
                data
            ).hexdigest(),
            "size_bytes": len(data),
        }
    )

evidence = {
    "status": "completed",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "mode": "read_only",
    "wolfden_modules": [
        {
            "module": module,
            "path": records[
                module
            ].path,
            "imports": list(
                records[
                    module
                ].imports
            ),
        }
        for module in wolfden_modules
    ],
    "wolfden_reachable_modules": sorted(
        reachable
    ),
    "candidate_modules": (
        candidate_evidence
    ),
    "reachable_candidates": (
        reachable_candidates
    ),
    "unreachable_candidates": (
        unreachable_candidates
    ),
    "directly_imported_candidates": (
        directly_imported_candidates
    ),
    "qualified_candidate_functions": (
        qualified_candidate_functions
    ),
    "wolfden_injection_seams": (
        sorted(
            wolfden_injection_seams,
            key=lambda item: (
                item["path"],
                item["line"],
                item["name"],
            ),
        )
    ),
    "wolfden_forbidden_imports": (
        sorted(
            wolfden_forbidden_imports,
            key=lambda item: (
                item["path"],
                item["line"],
                item[
                    "imported_module"
                ],
            ),
        )
    ),
    "source_manifest": source_manifest,
}

report = {
    "campaign": (
        "NeuroVest Integrated "
        "Qualification Campaign"
    ),
    "batch": (
        "IQC-STAGE5-REM-001B2C"
    ),
    "batch_name": (
        "Re-grade Reachable Capability Signals "
        "and Resolve Wolfden Local-Model "
        "Runtime Injection"
    ),
    "status": "completed",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "mode": "read_only",
    "disposition": disposition,
    "regrade": {
        "wolfden_forbidden_capability_imports": (
            forbidden_capability_count
        ),
        "wolfden_module_count": len(
            wolfden_modules
        ),
        "wolfden_reachable_module_count": len(
            reachable
        ),
        "local_model_candidate_count": len(
            candidate_evidence
        ),
        "reachable_local_model_candidates": len(
            reachable_candidates
        ),
        "unreachable_local_model_candidates": len(
            unreachable_candidates
        ),
        "directly_imported_local_model_candidates": len(
            directly_imported_candidates
        ),
        "qualified_model_functions": len(
            qualified_candidate_functions
        ),
        "wolfden_runtime_injection_seams": len(
            wolfden_injection_seams
        ),
    },
    "runtime_injection": {
        "present": (
            runtime_injection_present
        ),
        "reachable_local_model_present": (
            reachable_local_model_present
        ),
        "direct_local_model_import_present": (
            direct_local_model_import_present
        ),
        "binding_complete": (
            reachable_local_model_present
            and runtime_injection_present
        ),
    },
    "qualification": {
        "whole_backend_tests_passed": (
            tests_passed
        ),
        "whole_backend_tests_failed": (
            tests_failed
        ),
        "active_internal_unresolved": 0,
        "tooling_or_relative_unresolved": 0,
        "syntax_errors": 0,
        "active_dependency_cycles": 0,
        "self_cycles": 0,
    },
    "authorized_source_targets": (
        authorized_targets
    ),
    "source_modified": False,
    "database_modified": False,
    "auth_implemented": False,
    "snaptrade_connected": False,
    "broker_execution_enabled": False,
    "live_trading_enabled": False,
    "next_step": next_step,
}

freeze = {
    "status": "frozen",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "batch": (
        "IQC-STAGE5-REM-001B2C"
    ),
    "disposition": disposition,
    "authorized_source_targets": (
        authorized_targets
    ),
    "wolfden_forbidden_capability_imports": (
        forbidden_capability_count
    ),
    "reachable_local_model_candidates": len(
        reachable_candidates
    ),
    "wolfden_runtime_injection_seams": len(
        wolfden_injection_seams
    ),
    "source_modified": False,
    "database_modified": False,
    "broker_execution_enabled": False,
    "live_trading_enabled": False,
}

EVIDENCE_JSON.write_text(
    json.dumps(
        evidence,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

REPORT_JSON.write_text(
    json.dumps(
        report,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

FREEZE_JSON.write_text(
    json.dumps(
        freeze,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

text_lines = [
    "=" * 104,
    "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
    (
        "IQC STAGE 5 REMEDIATION BATCH 1B2C — "
        "RE-GRADE REACHABLE CAPABILITY SIGNALS AND "
        "RESOLVE WOLFDEN LOCAL-MODEL RUNTIME INJECTION"
    ),
    "=" * 104,
    "",
    "STATUS",
    "COMPLETE AND VERIFIED",
    "",
    "MODE",
    "READ ONLY",
    "",
    "DISPOSITION",
    disposition,
    "",
    "RE-GRADE",
    (
        "Wolfden forbidden capability imports: "
        f"{forbidden_capability_count}"
    ),
    (
        "Wolfden modules:                     "
        f"{len(wolfden_modules)}"
    ),
    (
        "Wolfden reachable modules:           "
        f"{len(reachable)}"
    ),
    (
        "Local-model candidates:              "
        f"{len(candidate_evidence)}"
    ),
    (
        "Reachable local-model candidates:    "
        f"{len(reachable_candidates)}"
    ),
    (
        "Unreachable local-model candidates:  "
        f"{len(unreachable_candidates)}"
    ),
    (
        "Directly imported model candidates:  "
        f"{len(directly_imported_candidates)}"
    ),
    (
        "Qualified model functions:           "
        f"{len(qualified_candidate_functions)}"
    ),
    (
        "Wolfden runtime injection seams:     "
        f"{len(wolfden_injection_seams)}"
    ),
    "",
    "RUNTIME INJECTION",
    (
        "Injection seam present:              "
        + (
            "YES"
            if runtime_injection_present
            else "NO"
        )
    ),
    (
        "Reachable local model present:       "
        + (
            "YES"
            if reachable_local_model_present
            else "NO"
        )
    ),
    (
        "Direct model import present:         "
        + (
            "YES"
            if direct_local_model_import_present
            else "NO"
        )
    ),
    (
        "Binding complete:                    "
        + (
            "YES"
            if (
                reachable_local_model_present
                and runtime_injection_present
            )
            else "NO"
        )
    ),
    "",
    "AUTHORIZED SOURCE TARGETS",
]

if authorized_targets:
    text_lines.extend(
        f"- {path}"
        for path in authorized_targets
    )

else:
    text_lines.append(
        "- None"
    )

text_lines.extend(
    [
        "",
        "QUALIFICATION",
        (
            "Whole-backend tests passed:       "
            f"{tests_passed}"
        ),
        (
            "Whole-backend tests failed:       "
            f"{tests_failed}"
        ),
        "Active unresolved imports:           0",
        "Dependency cycles:                   0",
        "Syntax errors:                       0",
        "",
        "SAFETY",
        "- Source modified: NO",
        "- Database modified: NO",
        "- Auth implemented: NO",
        "- SnapTrade connected: NO",
        "- Broker execution enabled: NO",
        "- Live trading enabled: NO",
        "",
        "NEXT",
        next_step,
        "",
        "=" * 104,
    ]
)

rendered = (
    "\n".join(
        text_lines
    )
    + "\n"
)

REPORT_TEXT.write_text(
    rendered,
    encoding="utf-8",
)

print(rendered)

print("REACHABLE LOCAL-MODEL CANDIDATES")

if reachable_candidates:
    for candidate in reachable_candidates:
        print(
            "- "
            + candidate["path"]
        )

else:
    print("- None")

print()
print("WOLFDEN INJECTION SEAMS")

if wolfden_injection_seams:
    for seam in sorted(
        wolfden_injection_seams,
        key=lambda item: (
            item["path"],
            item["line"],
            item["name"],
        ),
    ):
        print(
            f"- {seam['path']}:{seam['line']} "
            f"{seam['name']} "
            f"parameters={seam['injection_parameters']}"
        )

else:
    print("- None")

print()
print("WOLFDEN FORBIDDEN CAPABILITY IMPORTS")

if wolfden_forbidden_imports:
    for item in sorted(
        wolfden_forbidden_imports,
        key=lambda value: (
            value["path"],
            value["line"],
        ),
    ):
        print(
            f"- {item['path']}:{item['line']} "
            f"{item['imported_module']}"
        )

else:
    print("- None")

print()
print("PASS: Batch 1B2C evidence written")
print(REPORT_JSON)
print(EVIDENCE_JSON)
print(FREEZE_JSON)
