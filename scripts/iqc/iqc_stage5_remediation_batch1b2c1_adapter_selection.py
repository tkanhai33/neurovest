#!/usr/bin/env python3

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
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
    / "remediation_batch1b2c1"
)

PRIOR_REPORT = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2c"
    / "iqc_stage5_remediation_batch1b2c_latest.json"
)

PRIOR_EVIDENCE = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "remediation_batch1b2c"
    / "iqc_stage5_remediation_batch1b2c_evidence_latest.json"
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

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c1_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c1_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c1_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_remediation_batch1b2c1_freeze_latest.json"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

CANDIDATE_PATHS = (
    Path(
        "backend/app/stacks/chat_public/"
        "ollama_chat_client.py"
    ),
    Path(
        "backend/app/stacks/strategy/"
        "llm_strategy_engine.py"
    ),
)

PAID_PROVIDER_MARKERS = {
    "openai",
    "anthropic",
    "gemini",
    "google.generativeai",
    "cohere",
    "mistralai",
    "groq",
    "together",
    "replicate",
    "bedrock",
    "azure.ai",
}

LOCAL_MODEL_MARKERS = {
    "ollama",
    "localhost",
    "127.0.0.1",
    "11434",
    "/api/chat",
    "/api/generate",
}

TRANSPORT_MARKERS = {
    "httpx",
    "requests",
    "aiohttp",
    "urllib",
    "urlopen",
    "post",
    "request",
}

MODEL_CALL_MARKERS = {
    "chat",
    "generate",
    "complete",
    "completion",
    "invoke",
    "infer",
    "inference",
    "predict",
    "ask",
}

INJECTION_PARAMETER_MARKERS = {
    "client",
    "model",
    "llm",
    "adapter",
    "provider",
    "generator",
    "inference",
    "invoke",
    "transport",
    "chat_client",
    "model_client",
    "model_callable",
}

OUTPUT_PARAMETER_MARKERS = {
    "response",
    "output",
    "model_output",
    "raw_output",
    "generated",
    "completion",
    "content",
    "text",
}

FORBIDDEN_WOLFDEN_MARKERS = {
    ".execution",
    ".paper_trading",
    ".broker_integration",
    "snaptrade",
    "db_runtime",
    "journal_ledger",
    "sqlalchemy",
}


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def module_name(
    path: Path,
) -> str:
    parts = list(
        path.relative_to(
            ROOT
        ).with_suffix("").parts
    )

    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def source_line(
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


def call_name(
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

    if parts:
        return ".".join(
            reversed(parts)
        )

    try:
        return ast.unparse(
            node.func
        )

    except Exception:
        return "<unresolved>"


def imported_modules(
    tree: ast.AST,
) -> list[dict[str, Any]]:
    records = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                records.append(
                    {
                        "line": node.lineno,
                        "module": alias.name,
                        "names": [],
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            records.append(
                {
                    "line": node.lineno,
                    "module": (
                        node.module or ""
                    ),
                    "names": [
                        alias.name
                        for alias in node.names
                    ],
                }
            )

    return sorted(
        records,
        key=lambda item: (
            item["line"],
            item["module"],
        ),
    )


def parameters(
    node: ast.FunctionDef
    | ast.AsyncFunctionDef,
) -> list[str]:
    return [
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


def function_record(
    node: ast.FunctionDef
    | ast.AsyncFunctionDef,
    source: str,
) -> dict[str, Any]:
    node_parameters = parameters(
        node
    )

    calls = []

    for child in ast.walk(node):
        if isinstance(
            child,
            ast.Call,
        ):
            calls.append(
                {
                    "line": child.lineno,
                    "call": call_name(
                        child
                    ),
                    "source": source_line(
                        source,
                        child.lineno,
                    ),
                }
            )

    return {
        "name": node.name,
        "line": node.lineno,
        "end_line": node.end_lineno,
        "async": isinstance(
            node,
            ast.AsyncFunctionDef,
        ),
        "parameters": node_parameters,
        "injection_parameters": [
            parameter
            for parameter in node_parameters
            if any(
                marker in parameter.lower()
                for marker
                in INJECTION_PARAMETER_MARKERS
            )
        ],
        "output_parameters": [
            parameter
            for parameter in node_parameters
            if any(
                marker == parameter.lower()
                or marker
                in parameter.lower()
                for marker
                in OUTPUT_PARAMETER_MARKERS
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
        "calls": sorted(
            calls,
            key=lambda item: (
                item["line"],
                item["call"],
            ),
        ),
        "source": source_line(
            source,
            node.lineno,
        ),
    }


prior_report = json.loads(
    PRIOR_REPORT.read_text(
        encoding="utf-8"
    )
)

prior_evidence = json.loads(
    PRIOR_EVIDENCE.read_text(
        encoding="utf-8"
    )
)

assert prior_report[
    "disposition"
] == (
    "INJECTION_SEAM_PRESENT_"
    "LOCAL_MODEL_BINDING_MISSING"
)

candidate_records = []

for relative_path in CANDIDATE_PATHS:
    path = ROOT / relative_path

    assert path.is_file(), (
        f"Candidate source is missing: {path}"
    )

    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = imported_modules(
        tree
    )

    functions = [
        function_record(
            node,
            source,
        )
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    calls = []

    string_literals = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Call,
        ):
            calls.append(
                {
                    "line": node.lineno,
                    "call": call_name(
                        node
                    ),
                    "source": source_line(
                        source,
                        node.lineno,
                    ),
                }
            )

        elif (
            isinstance(
                node,
                ast.Constant,
            )
            and isinstance(
                node.value,
                str,
            )
        ):
            string_literals.append(
                node.value
            )

    normalized_text = (
        source.lower()
    )

    import_text = " ".join(
        item["module"].lower()
        for item in imports
    )

    call_text = " ".join(
        item["call"].lower()
        for item in calls
    )

    literal_text = " ".join(
        literal.lower()
        for literal in string_literals
    )

    local_signals = sorted(
        marker
        for marker in LOCAL_MODEL_MARKERS
        if (
            marker in normalized_text
            or marker in import_text
            or marker in call_text
            or marker in literal_text
        )
    )

    paid_provider_signals = sorted(
        marker
        for marker in PAID_PROVIDER_MARKERS
        if (
            marker in normalized_text
            or marker in import_text
            or marker in call_text
            or marker in literal_text
        )
    )

    transport_signals = sorted(
        marker
        for marker in TRANSPORT_MARKERS
        if (
            marker in import_text
            or marker in call_text
        )
    )

    model_entrypoints = [
        function
        for function in functions
        if any(
            marker in function[
                "name"
            ].lower()
            for marker in MODEL_CALL_MARKERS
        )
    ]

    direct_local_transport = bool(
        local_signals
        and (
            transport_signals
            or any(
                "ollama" in item[
                    "call"
                ].lower()
                for item in calls
            )
        )
    )

    path_text = relative_path.as_posix().lower()

    ownership_score = 0
    score_reasons = []

    if "ollama" in path_text:
        ownership_score += 6
        score_reasons.append(
            "path explicitly identifies Ollama"
        )

    if local_signals:
        ownership_score += 5
        score_reasons.append(
            "local-model endpoint or runtime signals present"
        )

    if direct_local_transport:
        ownership_score += 5
        score_reasons.append(
            "direct local-model transport present"
        )

    if model_entrypoints:
        ownership_score += 3
        score_reasons.append(
            "model invocation entrypoint present"
        )

    if (
        "strategy" in path_text
        or "engine" in path_text
    ):
        ownership_score -= 2
        score_reasons.append(
            "domain-engine naming reduces adapter ownership"
        )

    if paid_provider_signals:
        ownership_score -= 20
        score_reasons.append(
            "paid-provider signal detected"
        )

    if paid_provider_signals:
        classification = (
            "REJECTED_PAID_OR_EXTERNAL_PROVIDER"
        )

    elif (
        local_signals
        and direct_local_transport
        and model_entrypoints
    ):
        classification = (
            "LOCAL_MODEL_TRANSPORT_ADAPTER"
        )

    elif model_entrypoints:
        classification = (
            "MODEL_DOMAIN_SERVICE_OR_ORCHESTRATOR"
        )

    else:
        classification = (
            "MODEL_RELATED_NON_ADAPTER"
        )

    candidate_records.append(
        {
            "path": relative_path.as_posix(),
            "module": module_name(
                path
            ),
            "classification": classification,
            "ownership_score": ownership_score,
            "score_reasons": score_reasons,
            "local_signals": local_signals,
            "paid_provider_signals": (
                paid_provider_signals
            ),
            "transport_signals": (
                transport_signals
            ),
            "direct_local_transport": (
                direct_local_transport
            ),
            "imports": imports,
            "functions": sorted(
                functions,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "model_entrypoints": sorted(
                model_entrypoints,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "calls": sorted(
                calls,
                key=lambda item: (
                    item["line"],
                    item["call"],
                ),
            ),
        }
    )

ranked_candidates = sorted(
    candidate_records,
    key=lambda item: (
        -item["ownership_score"],
        item["path"],
    ),
)

assert len(
    ranked_candidates
) == 2

approved_candidate = (
    ranked_candidates[0]
)

rejected_candidate = (
    ranked_candidates[1]
)

assert approved_candidate[
    "ownership_score"
] > rejected_candidate[
    "ownership_score"
], (
    "Adapter ownership could not be selected "
    "without a scoring tie"
)

assert approved_candidate[
    "classification"
] == "LOCAL_MODEL_TRANSPORT_ADAPTER", (
    "Highest-scored candidate is not a confirmed "
    "local-model transport adapter"
)

assert approved_candidate[
    "paid_provider_signals"
] == [], (
    "Approved adapter contains a paid-provider signal"
)

assert approved_candidate[
    "local_signals"
], (
    "Approved adapter contains no local-model evidence"
)

assert approved_candidate[
    "model_entrypoints"
], (
    "Approved adapter has no model invocation entrypoint"
)

wolfden_files = sorted(
    path
    for path in WOLFDEN_ROOT.rglob(
        "*.py"
    )
    if (
        "__pycache__"
        not in path.parts
        and "tests" not in path.parts
        and not path.name.startswith(
            "test_"
        )
    )
)

assert wolfden_files, (
    "No active Wolfden source files resolved"
)

wolfden_modules = {
    module_name(path): path
    for path in wolfden_files
}

wolfden_evidence = []

actual_injection_seams = []

output_consumers = []

false_positive_seams = []

wolfden_forbidden_imports = []

for module, path in sorted(
    wolfden_modules.items()
):
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = imported_modules(
        tree
    )

    functions = [
        function_record(
            node,
            source,
        )
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    file_calls = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Call,
        ):
            file_calls.append(
                {
                    "line": node.lineno,
                    "call": call_name(
                        node
                    ),
                    "source": source_line(
                        source,
                        node.lineno,
                    ),
                }
            )

    for item in imports:
        lowered = item[
            "module"
        ].lower()

        if any(
            marker in lowered
            for marker
            in FORBIDDEN_WOLFDEN_MARKERS
        ):
            wolfden_forbidden_imports.append(
                {
                    "path": relative(
                        path
                    ),
                    **item,
                }
            )

    for function in functions:
        injection_parameters = function[
            "injection_parameters"
        ]

        callable_parameter_calls = []

        for call in function[
            "calls"
        ]:
            root_name = call[
                "call"
            ].split(".")[0]

            if root_name in injection_parameters:
                callable_parameter_calls.append(
                    call
                )

        if injection_parameters:
            seam = {
                "path": relative(
                    path
                ),
                "module": module,
                "function": function[
                    "name"
                ],
                "line": function[
                    "line"
                ],
                "async": function[
                    "async"
                ],
                "parameters": function[
                    "parameters"
                ],
                "injection_parameters": (
                    injection_parameters
                ),
                "callable_parameter_calls": (
                    callable_parameter_calls
                ),
                "qualified": bool(
                    callable_parameter_calls
                ),
                "source": function[
                    "source"
                ],
            }

            actual_injection_seams.append(
                seam
            )

        if function[
            "output_parameters"
        ]:
            output_consumers.append(
                {
                    "path": relative(
                        path
                    ),
                    "module": module,
                    "function": function[
                        "name"
                    ],
                    "line": function[
                        "line"
                    ],
                    "async": function[
                        "async"
                    ],
                    "parameters": function[
                        "parameters"
                    ],
                    "output_parameters": function[
                        "output_parameters"
                    ],
                    "return_annotation": function[
                        "return_annotation"
                    ],
                    "calls": function[
                        "calls"
                    ],
                    "source": function[
                        "source"
                    ],
                }
            )

        prior_matches = [
            seam
            for seam in prior_evidence[
                "wolfden_injection_seams"
            ]
            if (
                seam["path"]
                == relative(path)
                and seam["name"]
                == function["name"]
            )
        ]

        if prior_matches:
            if not injection_parameters:
                false_positive_seams.append(
                    {
                        "path": relative(
                            path
                        ),
                        "module": module,
                        "function": function[
                            "name"
                        ],
                        "line": function[
                            "line"
                        ],
                        "reason": (
                            "Function was classified only "
                            "because its name contained an "
                            "injection-like verb; it accepts "
                            "no adapter, model, client, "
                            "provider, or callable parameter."
                        ),
                        "parameters": function[
                            "parameters"
                        ],
                        "source": function[
                            "source"
                        ],
                    }
                )

    wolfden_evidence.append(
        {
            "module": module,
            "path": relative(
                path
            ),
            "imports": imports,
            "functions": sorted(
                functions,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "calls": sorted(
                file_calls,
                key=lambda item: (
                    item["line"],
                    item["call"],
                ),
            ),
        }
    )

assert wolfden_forbidden_imports == [], (
    "Wolfden forbidden capability imports reappeared"
)

qualified_actual_seams = [
    seam
    for seam in actual_injection_seams
    if seam[
        "qualified"
    ]
]

unqualified_parameter_seams = [
    seam
    for seam in actual_injection_seams
    if not seam[
        "qualified"
    ]
]

assert len(
    false_positive_seams
) == 1, (
    "Expected exactly one prior false-positive seam; "
    f"found {len(false_positive_seams)}"
)

false_positive = (
    false_positive_seams[0]
)

assert false_positive[
    "path"
] == (
    "backend/app/stacks/wolfden_ai/"
    "portfolio_output_result_facade.py"
)

assert false_positive[
    "function"
] == "build_portfolio_output_result"

agent_router_candidates = [
    item
    for item in wolfden_evidence
    if item[
        "path"
    ].endswith(
        "/agent_router.py"
    )
]

assert len(
    agent_router_candidates
) == 1, (
    "Expected exactly one Wolfden agent_router.py"
)

agent_router = agent_router_candidates[
    0
]

agent_router_functions = [
    function
    for function in agent_router[
        "functions"
    ]
    if not function[
        "name"
    ].startswith("_")
]

assert agent_router_functions, (
    "Wolfden agent_router exposes no public "
    "orchestration function"
)

async_router_functions = [
    function
    for function in agent_router_functions
    if function[
        "async"
    ]
]

router_functions = (
    async_router_functions
    or agent_router_functions
)

router_functions = sorted(
    router_functions,
    key=lambda function: (
        0
        if any(
            marker in function[
                "name"
            ].lower()
            for marker in (
                "route",
                "run",
                "process",
                "handle",
                "agent",
                "portfolio",
            )
        )
        else 1,
        function["line"],
        function["name"],
    ),
)

binding_function = (
    router_functions[0]
)

binding_target = {
    "path": agent_router[
        "path"
    ],
    "module": agent_router[
        "module"
    ],
    "function": binding_function[
        "name"
    ],
    "line": binding_function[
        "line"
    ],
    "async": binding_function[
        "async"
    ],
    "parameters": binding_function[
        "parameters"
    ],
    "return_annotation": binding_function[
        "return_annotation"
    ],
    "calls": binding_function[
        "calls"
    ],
    "selection_reason": (
        "Wolfden agent_router is the existing "
        "orchestration owner. The immutable result "
        "facade is a downstream formatter and is not "
        "an adapter-injection boundary."
    ),
}

approved_entrypoints = (
    approved_candidate[
        "model_entrypoints"
    ]
)

approved_entrypoint = sorted(
    approved_entrypoints,
    key=lambda function: (
        0
        if function[
            "async"
        ] == binding_target[
            "async"
        ]
        else 1,
        function["line"],
        function["name"],
    ),
)[0]

adapter_contract = {
    "adapter_path": approved_candidate[
        "path"
    ],
    "adapter_module": approved_candidate[
        "module"
    ],
    "adapter_function": approved_entrypoint[
        "name"
    ],
    "adapter_line": approved_entrypoint[
        "line"
    ],
    "adapter_async": approved_entrypoint[
        "async"
    ],
    "adapter_parameters": approved_entrypoint[
        "parameters"
    ],
    "adapter_return_annotation": (
        approved_entrypoint[
            "return_annotation"
        ]
    ),
    "local_signals": approved_candidate[
        "local_signals"
    ],
    "paid_provider_signals": (
        approved_candidate[
            "paid_provider_signals"
        ]
    ),
}

if qualified_actual_seams:
    seam_disposition = (
        "EXISTING_CALLABLE_INJECTION_SEAM_PRESENT"
    )

elif unqualified_parameter_seams:
    seam_disposition = (
        "PARAMETER_SEAM_PRESENT_BUT_CALL_PATH_MISSING"
    )

else:
    seam_disposition = (
        "NO_ACTUAL_RUNTIME_INJECTION_SEAM"
    )

if (
    approved_candidate[
        "classification"
        ]
    == "LOCAL_MODEL_TRANSPORT_ADAPTER"
    and seam_disposition
    == "NO_ACTUAL_RUNTIME_INJECTION_SEAM"
):
    disposition = (
        "APPROVED_LOCAL_ADAPTER_SELECTED_"
        "ACTUAL_INJECTION_SEAM_MISSING_"
        "BINDING_TARGET_FROZEN"
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C2 — "
        "Create the Minimal Wolfden Local-Model "
        "Invocation Contract and Bind the Approved "
        "Ollama Adapter at the Frozen Agent-Router Target"
    )

elif (
    approved_candidate[
        "classification"
    ]
    == "LOCAL_MODEL_TRANSPORT_ADAPTER"
    and seam_disposition
    == "EXISTING_CALLABLE_INJECTION_SEAM_PRESENT"
):
    disposition = (
        "APPROVED_LOCAL_ADAPTER_AND_"
        "ACTUAL_INJECTION_SEAM_CONFIRMED"
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C2 — "
        "Bind the Approved Ollama Adapter Through "
        "the Confirmed Existing Injection Seam"
    )

else:
    disposition = (
        "ADAPTER_OR_BINDING_OWNERSHIP_"
        "REQUIRES_ADDITIONAL_DISPOSITION"
    )

    next_step = (
        "IQC Stage 5 Remediation Batch 1B2C1A — "
        "Focused Adapter or Binding Ownership "
        "Evidence Qualification"
    )

contract_target = (
    "backend/app/stacks/wolfden_ai/"
    "local_model_contract.py"
)

authorized_source_targets = sorted(
    {
        approved_candidate[
            "path"
        ],
        binding_target[
            "path"
        ],
        contract_target,
    }
)

explicitly_excluded_targets = sorted(
    {
        rejected_candidate[
            "path"
        ],
        false_positive[
            "path"
        ],
    }
)

audit = json.loads(
    IMPORT_AUDIT.read_text(
        encoding="utf-8"
    )
)

summary = audit[
    "summary"
]

assert summary[
    "active_internal_unresolved"
] == 0

assert summary[
    "tooling_or_relative_unresolved"
] == 0

assert summary[
    "syntax_errors"
] == 0

assert summary[
    "active_cycle_components"
] == 0

assert summary[
    "self_cycles"
] == 0

test_text = TEST_LOG.read_text(
    encoding="utf-8",
    errors="replace",
)

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

for path in sorted(
    BACKEND_ROOT.rglob(
        "*.py"
    )
):
    if "__pycache__" in path.parts:
        continue

    data = path.read_bytes()

    source_manifest.append(
        {
            "path": relative(
                path
            ),
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
    "candidate_records": (
        ranked_candidates
    ),
    "approved_candidate": (
        approved_candidate
    ),
    "rejected_candidate": (
        rejected_candidate
    ),
    "adapter_contract": (
        adapter_contract
    ),
    "wolfden_files": (
        wolfden_evidence
    ),
    "actual_injection_seams": (
        actual_injection_seams
    ),
    "qualified_actual_injection_seams": (
        qualified_actual_seams
    ),
    "unqualified_parameter_seams": (
        unqualified_parameter_seams
    ),
    "false_positive_seams": (
        false_positive_seams
    ),
    "output_consumers": (
        output_consumers
    ),
    "binding_target": (
        binding_target
    ),
    "wolfden_forbidden_imports": (
        wolfden_forbidden_imports
    ),
    "source_manifest": (
        source_manifest
    ),
}

report = {
    "campaign": (
        "NeuroVest Integrated "
        "Qualification Campaign"
    ),
    "batch": (
        "IQC-STAGE5-REM-001B2C1"
    ),
    "batch_name": (
        "Approved Local-Model Adapter Selection, "
        "Actual Injection-Seam Qualification, "
        "and Binding-Target Freeze"
    ),
    "status": "completed",
    "verified_at": datetime.now(
        UTC
    ).isoformat(),
    "mode": "read_only",
    "disposition": disposition,
    "adapter_selection": {
        "approved_path": (
            approved_candidate[
                "path"
            ]
        ),
        "approved_module": (
            approved_candidate[
                "module"
            ]
        ),
        "approved_classification": (
            approved_candidate[
                "classification"
            ]
        ),
        "approved_score": (
            approved_candidate[
                "ownership_score"
            ]
        ),
        "approved_entrypoint": (
            approved_entrypoint[
                "name"
            ]
        ),
        "approved_entrypoint_async": (
            approved_entrypoint[
                "async"
            ]
        ),
        "approved_entrypoint_return_annotation": (
            approved_entrypoint[
                "return_annotation"
            ]
        ),
        "rejected_path": (
            rejected_candidate[
                "path"
            ]
        ),
        "rejected_classification": (
            rejected_candidate[
                "classification"
            ]
        ),
        "rejected_score": (
            rejected_candidate[
                "ownership_score"
            ]
        ),
        "paid_provider_signals": (
            approved_candidate[
                "paid_provider_signals"
            ]
        ),
    },
    "seam_qualification": {
        "prior_reported_seams": 1,
        "prior_false_positive_seams": len(
            false_positive_seams
        ),
        "actual_parameter_seams": len(
            actual_injection_seams
        ),
        "qualified_callable_seams": len(
            qualified_actual_seams
        ),
        "unqualified_parameter_seams": len(
            unqualified_parameter_seams
        ),
        "disposition": (
            seam_disposition
        ),
    },
    "binding_target": (
        binding_target
    ),
    "contract_target": (
        contract_target
    ),
    "authorized_source_targets": (
        authorized_source_targets
    ),
    "explicitly_excluded_targets": (
        explicitly_excluded_targets
    ),
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
        "IQC-STAGE5-REM-001B2C1"
    ),
    "disposition": disposition,
    "approved_adapter": {
        "path": approved_candidate[
            "path"
        ],
        "module": approved_candidate[
            "module"
        ],
        "entrypoint": approved_entrypoint[
            "name"
        ],
        "async": approved_entrypoint[
            "async"
        ],
    },
    "seam_disposition": (
        seam_disposition
    ),
    "binding_target": {
        "path": binding_target[
            "path"
        ],
        "module": binding_target[
            "module"
        ],
        "function": binding_target[
            "function"
        ],
        "line": binding_target[
            "line"
        ],
        "async": binding_target[
            "async"
        ],
    },
    "contract_target": (
        contract_target
    ),
    "authorized_source_targets": (
        authorized_source_targets
    ),
    "explicitly_excluded_targets": (
        explicitly_excluded_targets
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
    "=" * 108,
    "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
    (
        "IQC STAGE 5 REMEDIATION BATCH 1B2C1 — "
        "APPROVED LOCAL-MODEL ADAPTER SELECTION, "
        "ACTUAL INJECTION-SEAM QUALIFICATION, "
        "AND BINDING-TARGET FREEZE"
    ),
    "=" * 108,
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
    "APPROVED LOCAL-MODEL ADAPTER",
    (
        "Path:                         "
        + approved_candidate[
            "path"
        ]
    ),
    (
        "Module:                       "
        + approved_candidate[
            "module"
        ]
    ),
    (
        "Classification:               "
        + approved_candidate[
            "classification"
        ]
    ),
    (
        "Ownership score:               "
        + str(
            approved_candidate[
                "ownership_score"
            ]
        )
    ),
    (
        "Entrypoint:                    "
        + approved_entrypoint[
            "name"
        ]
    ),
    (
        "Entrypoint async:              "
        + (
            "YES"
            if approved_entrypoint[
                "async"
            ]
            else "NO"
        )
    ),
    (
        "Paid-provider signals:         "
        + (
            ", ".join(
                approved_candidate[
                    "paid_provider_signals"
                ]
            )
            if approved_candidate[
                "paid_provider_signals"
            ]
            else "NONE"
        )
    ),
    "",
    "REJECTED MODEL CANDIDATE",
    (
        "Path:                         "
        + rejected_candidate[
            "path"
        ]
    ),
    (
        "Classification:               "
        + rejected_candidate[
            "classification"
        ]
    ),
    (
        "Ownership score:               "
        + str(
            rejected_candidate[
                "ownership_score"
            ]
        )
    ),
    "",
    "ACTUAL INJECTION-SEAM QUALIFICATION",
    (
        "Previously reported seams:     1"
    ),
    (
        "Prior false-positive seams:    "
        + str(
            len(
                false_positive_seams
            )
        )
    ),
    (
        "Actual parameter seams:        "
        + str(
            len(
                actual_injection_seams
            )
        )
    ),
    (
        "Qualified callable seams:      "
        + str(
            len(
                qualified_actual_seams
            )
        )
    ),
    (
        "Seam disposition:              "
        + seam_disposition
    ),
    "",
    "FALSE-POSITIVE SEAM",
    (
        "Path:                         "
        + false_positive[
            "path"
        ]
    ),
    (
        "Function:                     "
        + false_positive[
            "function"
        ]
    ),
    (
        "Reason:                       "
        + false_positive[
            "reason"
        ]
    ),
    "",
    "FROZEN BINDING TARGET",
    (
        "Path:                         "
        + binding_target[
            "path"
        ]
    ),
    (
        "Module:                       "
        + binding_target[
            "module"
        ]
    ),
    (
        "Function:                     "
        + binding_target[
            "function"
        ]
    ),
    (
        "Line:                         "
        + str(
            binding_target[
                "line"
            ]
        )
    ),
    (
        "Async:                        "
        + (
            "YES"
            if binding_target[
                "async"
            ]
            else "NO"
        )
    ),
    "",
    "FROZEN CONTRACT TARGET",
    (
        "Path:                         "
        + contract_target
    ),
    "",
    "AUTHORIZED SOURCE TARGETS",
]

text_lines.extend(
    f"- {path}"
    for path in authorized_source_targets
)

text_lines.extend(
    [
        "",
        "EXPLICITLY EXCLUDED TARGETS",
    ]
)

text_lines.extend(
    f"- {path}"
    for path in explicitly_excluded_targets
)

text_lines.extend(
    [
        "",
        "QUALIFICATION",
        (
            "Whole-backend tests passed:       "
            + str(
                tests_passed
            )
        ),
        (
            "Whole-backend tests failed:       "
            + str(
                tests_failed
            )
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
        "=" * 108,
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

print("APPROVED ADAPTER FUNCTIONS")

for function in approved_candidate[
    "model_entrypoints"
]:
    print(
        f"- {approved_candidate['path']}:"
        f"{function['line']} "
        f"{function['name']} "
        f"async={function['async']} "
        f"parameters={function['parameters']} "
        f"returns={function['return_annotation']}"
    )

print()
print("ACTUAL WOLFDEN INJECTION SEAMS")

if actual_injection_seams:
    for seam in actual_injection_seams:
        print(
            f"- {seam['path']}:{seam['line']} "
            f"{seam['function']} "
            f"parameters={seam['injection_parameters']} "
            f"qualified={seam['qualified']}"
        )

else:
    print("- None")

print()
print("FROZEN BINDING TARGET")

print(
    f"- {binding_target['path']}:"
    f"{binding_target['line']} "
    f"{binding_target['function']}"
)

print()
print("PASS: Batch 1B2C1 evidence written")
print(REPORT_JSON)
print(EVIDENCE_JSON)
print(FREEZE_JSON)
