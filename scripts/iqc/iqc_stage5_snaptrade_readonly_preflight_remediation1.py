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

STACK_ROOT = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "snaptrade"
)

BACKEND_ROOT = (
    ROOT
    / "backend"
    / "app"
)

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "snaptrade_readonly_preflight_remediation1"
)

ORIGINAL_REPORT_PATH = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "snaptrade_readonly_authorization_preflight"
    / "iqc_stage5_snaptrade_readonly_authorization_preflight_latest.json"
)

ORIGINAL_EVIDENCE_PATH = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "snaptrade_readonly_authorization_preflight"
    / "iqc_stage5_snaptrade_readonly_authorization_preflight_evidence_latest.json"
)

ORIGINAL_FREEZE_PATH = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "snaptrade_readonly_authorization_preflight"
    / "iqc_stage5_snaptrade_readonly_scope_freeze_latest.json"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_preflight_remediation1_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_preflight_remediation1_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_preflight_remediation1_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_preflight_remediation1_freeze_latest.json"
)

SUPERSESSION_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_preflight_v1_supersession_latest.json"
)


LOCAL_CONTAINER_TERMINALS = {
    "add",
    "append",
    "clear",
    "discard",
    "extend",
    "insert",
    "pop",
    "remove",
    "reverse",
    "sort",
    "update",
}


CONFIRMED_EXTERNAL_MUTATION_TERMINALS = {
    "authorize",
    "cancel",
    "cancel_order",
    "close_account",
    "connect",
    "create",
    "create_connection",
    "delete",
    "delete_user",
    "disconnect",
    "execute",
    "execute_order",
    "execute_trade",
    "generate_secret",
    "login",
    "logout",
    "modify",
    "open_account",
    "place_order",
    "place_trade",
    "preview_order",
    "register",
    "register_user",
    "remove_connection",
    "revoke",
    "submit",
    "submit_order",
    "trade",
    "update_account",
}


CREDENTIAL_TERMS = {
    "api_key",
    "client_id",
    "client_secret",
    "consumer_key",
    "secret",
    "user_secret",
    "authorization_id",
    "connection_id",
}


PERSISTENCE_MODULE_MARKERS = {
    "sqlalchemy",
    "db_runtime",
    "journal_ledger",
}


NETWORK_MODULE_MARKERS = {
    "aiohttp",
    "httpx",
    "requests",
    "snaptrade",
    "snaptrade_client",
    "urllib",
    "urllib3",
    "websockets",
}


PROHIBITED_OWNER_MARKERS = {
    "execution",
    "paper_trading",
    "strategy",
    "wolfden_ai",
}


READ_ONLY_NAME_TERMS = {
    "account",
    "accounts",
    "balance",
    "balances",
    "connection_status",
    "details",
    "fetch",
    "get",
    "holdings",
    "list",
    "lookup",
    "performance",
    "positions",
    "read",
    "status",
    "transactions",
}


def load_json(
    path: Path,
) -> dict[str, Any]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert isinstance(
        payload,
        dict,
    )

    return payload


def dotted_name(
    node: ast.AST,
) -> str:
    parts = []

    expression = node

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

    return ".".join(
        reversed(parts)
    )


def module_name_for_path(
    path: Path,
) -> str:
    relative = path.relative_to(
        ROOT
    ).with_suffix("")

    return ".".join(
        relative.parts
    )


def source_line(
    lines: list[str],
    line: int | None,
) -> str:
    if line is None:
        return ""

    if not (
        1 <= line <= len(lines)
    ):
        return ""

    return lines[
        line - 1
    ].strip()


def enclosing_scope(
    tree: ast.AST,
    target: ast.AST,
) -> str:
    scopes = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            continue

        if not hasattr(
            node,
            "lineno",
        ):
            continue

        if not hasattr(
            node,
            "end_lineno",
        ):
            continue

        target_line = getattr(
            target,
            "lineno",
            None,
        )

        if target_line is None:
            continue

        if (
            node.lineno
            <= target_line
            <= (
                node.end_lineno
                or node.lineno
            )
        ):
            scopes.append(
                (
                    node.end_lineno
                    - node.lineno,
                    node.name,
                )
            )

    if not scopes:
        return "<module>"

    return sorted(
        scopes
    )[0][1]


def collect_local_bindings(
    function: (
        ast.FunctionDef
        | ast.AsyncFunctionDef
        | None
    ),
) -> dict[str, str]:
    if function is None:
        return {}

    bindings: dict[str, str] = {}

    for argument in (
        list(
            function.args.posonlyargs
        )
        + list(
            function.args.args
        )
        + list(
            function.args.kwonlyargs
        )
    ):
        bindings[
            argument.arg
        ] = "ARGUMENT"

    for node in ast.walk(
        function
    ):
        if not isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

        if isinstance(
            node,
            ast.Assign,
        ):
            targets = node.targets
            value = node.value

        else:
            targets = [
                node.target
            ]
            value = node.value

        binding_type = "LOCAL_VALUE"

        if isinstance(
            value,
            ast.List,
        ):
            binding_type = "LOCAL_LIST"

        elif isinstance(
            value,
            ast.Dict,
        ):
            binding_type = "LOCAL_DICT"

        elif isinstance(
            value,
            ast.Set,
        ):
            binding_type = "LOCAL_SET"

        elif isinstance(
            value,
            ast.Call,
        ):
            called = dotted_name(
                value.func
            )

            if called in {
                "dict",
                "list",
                "set",
                "defaultdict",
            }:
                binding_type = (
                    "LOCAL_CONTAINER"
                )

            else:
                binding_type = (
                    "LOCAL_CONSTRUCTED_OBJECT"
                )

        for target in targets:
            if isinstance(
                target,
                ast.Name,
            ):
                bindings[
                    target.id
                ] = binding_type

    return bindings


def receiver_root(
    call: ast.Call,
) -> str | None:
    function = call.func

    if not isinstance(
        function,
        ast.Attribute,
    ):
        return None

    expression = function.value

    while isinstance(
        expression,
        ast.Attribute,
    ):
        expression = expression.value

    if isinstance(
        expression,
        ast.Name,
    ):
        return expression.id

    return None


def import_aliases(
    tree: ast.AST,
) -> dict[str, str]:
    aliases = {}

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                local = (
                    alias.asname
                    or alias.name.split(".")[0]
                )

                aliases[
                    local
                ] = alias.name

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = node.module or ""

            for alias in node.names:
                local = (
                    alias.asname
                    or alias.name
                )

                aliases[
                    local
                ] = (
                    module
                    + "."
                    + alias.name
                ).strip(".")

    return aliases


def function_for_node(
    tree: ast.AST,
    target: ast.AST,
) -> (
    ast.FunctionDef
    | ast.AsyncFunctionDef
    | None
):
    candidates = []

    target_line = getattr(
        target,
        "lineno",
        None,
    )

    if target_line is None:
        return None

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if (
            node.lineno
            <= target_line
            <= (
                node.end_lineno
                or node.lineno
            )
        ):
            candidates.append(
                node
            )

    if not candidates:
        return None

    return sorted(
        candidates,
        key=lambda item: (
            item.end_lineno
            or item.lineno
        )
        - item.lineno,
    )[0]


def collect_incoming_references(
    target_module: str,
    target_symbols: set[str],
) -> dict[str, Any]:
    module_importers = []
    symbol_importers: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    function_call_references: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        if STACK_ROOT in path.parents:
            continue

        try:
            source = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(
                source,
                filename=str(path),
            )

        except Exception:
            continue

        for node in ast.walk(
            tree
        ):
            if isinstance(
                node,
                ast.Import,
            ):
                for alias in node.names:
                    if (
                        alias.name
                        == target_module
                        or alias.name.startswith(
                            target_module
                            + "."
                        )
                    ):
                        module_importers.append(
                            {
                                "path": path.relative_to(
                                    ROOT
                                ).as_posix(),
                                "line": node.lineno,
                                "module": alias.name,
                            }
                        )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                module = node.module or ""

                if (
                    module == target_module
                    or module.startswith(
                        target_module
                        + "."
                    )
                ):
                    module_importers.append(
                        {
                            "path": path.relative_to(
                                ROOT
                            ).as_posix(),
                            "line": node.lineno,
                            "module": module,
                        }
                    )

                    for alias in node.names:
                        if alias.name in (
                            target_symbols
                        ):
                            symbol_importers[
                                alias.name
                            ].append(
                                {
                                    "path": path.relative_to(
                                        ROOT
                                    ).as_posix(),
                                    "line": node.lineno,
                                    "module": module,
                                }
                            )

            elif isinstance(
                node,
                ast.Call,
            ):
                called = dotted_name(
                    node.func
                )

                terminal = (
                    called.split(".")[-1]
                    if called
                    else ""
                )

                if terminal in target_symbols:
                    function_call_references[
                        terminal
                    ].append(
                        {
                            "path": path.relative_to(
                                ROOT
                            ).as_posix(),
                            "line": getattr(
                                node,
                                "lineno",
                                None,
                            ),
                            "call": called,
                        }
                    )

    return {
        "module_importers": module_importers,
        "symbol_importers": dict(
            symbol_importers
        ),
        "function_call_references": dict(
            function_call_references
        ),
    }


def classify_call(
    *,
    node: ast.Call,
    tree: ast.AST,
    aliases: dict[str, str],
) -> dict[str, Any]:
    rendered = dotted_name(
        node.func
    )

    terminal = (
        rendered.split(".")[-1].lower()
        if rendered
        else ""
    )

    root = receiver_root(
        node
    )

    scope_function = function_for_node(
        tree,
        node,
    )

    local_bindings = collect_local_bindings(
        scope_function
    )

    root_binding = (
        local_bindings.get(
            root,
            "UNRESOLVED",
        )
        if root
        else "NO_RECEIVER"
    )

    imported_owner = (
        aliases.get(
            root,
        )
        if root
        else None
    )

    classification = (
        "UNKNOWN_REQUIRES_REVIEW"
    )

    side_effect = (
        "UNRESOLVED"
    )

    remediation_required = True

    reason = (
        "The call could not be proven local and harmless."
    )

    if (
        terminal
        in LOCAL_CONTAINER_TERMINALS
        and root_binding
        in {
            "LOCAL_LIST",
            "LOCAL_DICT",
            "LOCAL_SET",
            "LOCAL_CONTAINER",
        }
    ):
        classification = (
            "LOCAL_CONTAINER_OPERATION"
        )

        side_effect = (
            "LOCAL_MEMORY_ONLY"
        )

        remediation_required = False

        reason = (
            "The receiver is created as a local in-memory "
            "container inside the enclosing function."
        )

    elif (
        terminal
        in LOCAL_CONTAINER_TERMINALS
        and root_binding
        == "LOCAL_CONSTRUCTED_OBJECT"
        and imported_owner is None
    ):
        classification = (
            "LOCAL_OBJECT_OPERATION_REQUIRES_SCOPE_REVIEW"
        )

        side_effect = (
            "LOCAL_OBJECT_STATE_POSSIBLE"
        )

        remediation_required = True

        reason = (
            "The receiver is locally constructed, but its "
            "method implementation is not proven side-effect free."
        )

    elif imported_owner and any(
        marker in imported_owner.lower()
        for marker in NETWORK_MODULE_MARKERS
    ):
        classification = (
            "CONFIRMED_EXTERNAL_NETWORK_CAPABILITY"
        )

        side_effect = (
            "EXTERNAL_NETWORK_POSSIBLE"
        )

        remediation_required = True

        reason = (
            "The receiver resolves to an imported network "
            "or SnapTrade module."
        )

    elif imported_owner and any(
        marker in imported_owner.lower()
        for marker in PERSISTENCE_MODULE_MARKERS
    ):
        classification = (
            "CONFIRMED_PERSISTENCE_CAPABILITY"
        )

        side_effect = (
            "DATABASE_OR_LEDGER_POSSIBLE"
        )

        remediation_required = True

        reason = (
            "The receiver resolves to an imported persistence module."
        )

    elif terminal in (
        CONFIRMED_EXTERNAL_MUTATION_TERMINALS
    ):
        classification = (
            "CAPABILITY_MUTATION_NAME_REQUIRES_OWNER_REVIEW"
        )

        side_effect = (
            "EXTERNAL_OR_DOMAIN_MUTATION_POSSIBLE"
        )

        remediation_required = True

        reason = (
            "The terminal name denotes registration, connection, "
            "credential, account, order, trade, or external mutation."
        )

    elif root_binding == "ARGUMENT":
        classification = (
            "ARGUMENT_RECEIVER_MUTATION_REQUIRES_REVIEW"
        )

        side_effect = (
            "CALLER_OWNED_STATE_POSSIBLE"
        )

        remediation_required = True

        reason = (
            "The receiver is supplied by the caller and its ownership "
            "cannot be proven local."
        )

    return {
        "call": rendered,
        "terminal": terminal,
        "receiver_root": root,
        "receiver_binding": root_binding,
        "imported_owner": imported_owner,
        "classification": classification,
        "side_effect": side_effect,
        "remediation_required": remediation_required,
        "reason": reason,
    }


def main() -> None:
    original_report = load_json(
        ORIGINAL_REPORT_PATH
    )

    original_evidence = load_json(
        ORIGINAL_EVIDENCE_PATH
    )

    original_freeze = load_json(
        ORIGINAL_FREEZE_PATH
    )

    assert original_report[
        "capability_disposition"
    ][
        "mutation_capability_present"
    ] is True

    mutation_function_records = (
        original_evidence[
            "capabilities"
        ][
            "mutation_functions"
        ]
    )

    mutation_call_records = (
        original_evidence[
            "capabilities"
        ][
            "mutation_calls"
        ]
    )

    assert (
        mutation_function_records
        or mutation_call_records
    )

    production_files = sorted(
        path
        for path in STACK_ROOT.rglob(
            "*.py"
        )
        if "__pycache__" not in path.parts
        and "tests" not in path.parts
        and not path.name.startswith(
            "test_"
        )
    )

    file_context = {}

    all_function_names = set()

    for path in production_files:
        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

        file_context[
            path.relative_to(
                ROOT
            ).as_posix()
        ] = {
            "path": path,
            "source": source,
            "lines": source.splitlines(),
            "tree": tree,
            "aliases": import_aliases(
                tree
            ),
            "module": module_name_for_path(
                path
            ),
        }

        all_function_names.update(
            node.name
            for node in ast.walk(
                tree
            )
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
        )

    resolved_functions = []

    for record in mutation_function_records:
        relative = record[
            "path"
        ]

        context = file_context.get(
            relative
        )

        assert context is not None, (
            f"Mutation function source missing: {relative}"
        )

        matches = [
            node
            for node in ast.walk(
                context[
                    "tree"
                ]
            )
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == record[
                "name"
            ]
            and node.lineno
            == record[
                "line"
            ]
        ]

        assert len(matches) == 1, (
            "Expected exactly one matching mutation function: "
            f"{relative}:{record['line']} {record['name']}"
        )

        function = matches[0]

        calls = [
            node
            for node in ast.walk(
                function
            )
            if isinstance(
                node,
                ast.Call,
            )
        ]

        call_dispositions = [
            {
                "line": node.lineno,
                "source": source_line(
                    context[
                        "lines"
                    ],
                    node.lineno,
                ),
                **classify_call(
                    node=node,
                    tree=context[
                        "tree"
                    ],
                    aliases=context[
                        "aliases"
                    ],
                ),
            }
            for node in calls
        ]

        confirmed_effects = [
            item
            for item in call_dispositions
            if item[
                "classification"
            ] in {
                "CONFIRMED_EXTERNAL_NETWORK_CAPABILITY",
                "CONFIRMED_PERSISTENCE_CAPABILITY",
                "CAPABILITY_MUTATION_NAME_REQUIRES_OWNER_REVIEW",
                "ARGUMENT_RECEIVER_MUTATION_REQUIRES_REVIEW",
                "LOCAL_OBJECT_OPERATION_REQUIRES_SCOPE_REVIEW",
                "UNKNOWN_REQUIRES_REVIEW",
            }
        ]

        function_classification = (
            "NAME_ONLY_FALSE_POSITIVE"
            if not confirmed_effects
            else
            "FUNCTION_REQUIRES_BOUNDARY_REVIEW"
        )

        resolved_functions.append(
            {
                "path": relative,
                "module": context[
                    "module"
                ],
                "line": function.lineno,
                "end_line": function.end_lineno,
                "name": function.name,
                "async": isinstance(
                    function,
                    ast.AsyncFunctionDef,
                ),
                "source": ast.get_source_segment(
                    context[
                        "source"
                    ],
                    function,
                )
                or ast.unparse(
                    function
                ),
                "incoming_reference_count": 0,
                "call_dispositions": (
                    call_dispositions
                ),
                "classification": (
                    function_classification
                ),
                "remediation_required": bool(
                    confirmed_effects
                ),
            }
        )

    resolved_calls = []

    for record in mutation_call_records:
        relative = record[
            "path"
        ]

        context = file_context.get(
            relative
        )

        assert context is not None, (
            f"Mutation call source missing: {relative}"
        )

        candidate_calls = [
            node
            for node in ast.walk(
                context[
                    "tree"
                ]
            )
            if isinstance(
                node,
                ast.Call,
            )
            and node.lineno
            == record[
                "line"
            ]
        ]

        exact = [
            node
            for node in candidate_calls
            if dotted_name(
                node.func
            )
            == record[
                "call"
            ]
        ]

        if len(exact) == 1:
            node = exact[0]

        elif len(candidate_calls) == 1:
            node = candidate_calls[0]

        else:
            raise AssertionError(
                "Could not resolve mutation call exactly: "
                f"{relative}:{record['line']} "
                f"{record['call']}"
            )

        resolved_calls.append(
            {
                "path": relative,
                "module": context[
                    "module"
                ],
                "line": node.lineno,
                "scope": enclosing_scope(
                    context[
                        "tree"
                    ],
                    node,
                ),
                "source": source_line(
                    context[
                        "lines"
                    ],
                    node.lineno,
                ),
                **classify_call(
                    node=node,
                    tree=context[
                        "tree"
                    ],
                    aliases=context[
                        "aliases"
                    ],
                ),
            }
        )

    modules = {
        item["module"]
        for item in (
            resolved_functions
            + resolved_calls
        )
    }

    incoming_by_module = {}

    for module in modules:
        incoming_by_module[
            module
        ] = collect_incoming_references(
            module,
            all_function_names,
        )

    for item in resolved_functions:
        incoming = incoming_by_module[
            item[
                "module"
            ]
        ]

        symbol_refs = incoming[
            "symbol_importers"
        ].get(
            item[
                "name"
            ],
            [],
        )

        call_refs = incoming[
            "function_call_references"
        ].get(
            item[
                "name"
            ],
            [],
        )

        item[
            "incoming_symbol_imports"
        ] = symbol_refs

        item[
            "incoming_call_references"
        ] = call_refs

        item[
            "incoming_reference_count"
        ] = (
            len(symbol_refs)
            + len(call_refs)
        )

        item[
            "reachable_outside_snaptrade"
        ] = (
            item[
                "incoming_reference_count"
            ]
            > 0
        )

    for item in resolved_calls:
        incoming = incoming_by_module[
            item[
                "module"
            ]
        ]

        item[
            "module_importers"
        ] = incoming[
            "module_importers"
        ]

        item[
            "module_reachable_outside_snaptrade"
        ] = bool(
            incoming[
                "module_importers"
            ]
        )

    unique_signal_keys = {
        (
            item[
                "path"
            ],
            item[
                "line"
            ],
            "FUNCTION",
            item[
                "name"
            ],
        )
        for item in resolved_functions
    }

    unique_signal_keys.update(
        (
            item[
                "path"
            ],
            item[
                "line"
            ],
            "CALL",
            item[
                "call"
            ],
        )
        for item in resolved_calls
    )

    expected_signal_count = (
        len(
            mutation_function_records
        )
        + len(
            mutation_call_records
        )
    )

    assert len(
        unique_signal_keys
    ) <= expected_signal_count

    all_call_dispositions = list(
        resolved_calls
    )

    for function in resolved_functions:
        for call in function[
            "call_dispositions"
        ]:
            all_call_dispositions.append(
                {
                    "path": function[
                        "path"
                    ],
                    "module": function[
                        "module"
                    ],
                    "scope": function[
                        "name"
                    ],
                    **call,
                }
            )

    confirmed_external = [
        item
        for item in all_call_dispositions
        if item[
            "classification"
        ] in {
            "CONFIRMED_EXTERNAL_NETWORK_CAPABILITY",
            "CONFIRMED_PERSISTENCE_CAPABILITY",
        }
    ]

    capability_mutations = [
        item
        for item in all_call_dispositions
        if item[
            "classification"
        ] == (
            "CAPABILITY_MUTATION_NAME_REQUIRES_OWNER_REVIEW"
        )
    ]

    unresolved_mutations = [
        item
        for item in all_call_dispositions
        if item[
            "classification"
        ] in {
            "ARGUMENT_RECEIVER_MUTATION_REQUIRES_REVIEW",
            "LOCAL_OBJECT_OPERATION_REQUIRES_SCOPE_REVIEW",
            "UNKNOWN_REQUIRES_REVIEW",
        }
    ]

    local_memory_only = [
        item
        for item in all_call_dispositions
        if item[
            "classification"
        ] == "LOCAL_CONTAINER_OPERATION"
    ]

    reachable_confirmed_external = [
        item
        for item in confirmed_external
        if item.get(
            "module_reachable_outside_snaptrade",
            False,
        )
        or any(
            function[
                "reachable_outside_snaptrade"
            ]
            for function in resolved_functions
            if function[
                "module"
            ] == item[
                "module"
            ]
        )
    ]

    hardcoded_credentials = original_report[
        "credential_boundary"
    ][
        "hardcoded_credentials_present"
    ]

    direct_database_access = original_report[
        "capability_disposition"
    ][
        "direct_database_access_present"
    ]

    cross_owner_import = original_report[
        "capability_disposition"
    ][
        "cross_owner_import_present"
    ]

    order_capability = original_report[
        "capability_disposition"
    ][
        "order_capability_present"
    ]

    exact_mutation_blockers = []

    if confirmed_external:
        exact_mutation_blockers.append(
            "Confirmed external network or persistence "
            "mutation capability exists"
        )

    if capability_mutations:
        exact_mutation_blockers.append(
            "Capability-named mutation requires ownership "
            "and boundary remediation"
        )

    if unresolved_mutations:
        exact_mutation_blockers.append(
            "One or more mutation signals remain unresolved"
        )

    if hardcoded_credentials:
        exact_mutation_blockers.append(
            "Hardcoded credential-like literal detected"
        )

    if direct_database_access:
        exact_mutation_blockers.append(
            "Direct persistence access detected"
        )

    if cross_owner_import:
        exact_mutation_blockers.append(
            "Prohibited cross-owner import detected"
        )

    if order_capability:
        exact_mutation_blockers.append(
            "Order-capable path detected"
        )

    adapter_scaffolding_authorized = not any(
        (
            hardcoded_credentials,
            direct_database_access,
            cross_owner_import,
            order_capability,
            bool(
                reachable_confirmed_external
            ),
        )
    )

    read_only_implementation_authorized = (
        adapter_scaffolding_authorized
        and not confirmed_external
        and not capability_mutations
        and not unresolved_mutations
    )

    if read_only_implementation_authorized:
        disposition = (
            "MUTATION_SIGNALS_LOCAL_AND_NON_EXTERNAL_"
            "READ_ONLY_IMPLEMENTATION_AUTHORIZED"
        )

    elif adapter_scaffolding_authorized:
        disposition = (
            "ADAPTER_SCAFFOLDING_AUTHORIZED_"
            "READ_ONLY_IMPLEMENTATION_BLOCKED_"
            "PENDING_MUTATION_REMEDIATION"
        )

    else:
        disposition = (
            "SNAPTRADE_READ_ONLY_WORK_BLOCKED_"
            "CONFIRMED_BOUNDARY_DEFECT"
        )

    authorization = {
        "adapter_scaffolding": (
            adapter_scaffolding_authorized
        ),
        "read_only_implementation": (
            read_only_implementation_authorized
        ),
        "credential_activation": False,
        "network_connection": False,
        "user_registration": False,
        "brokerage_connection": False,
        "order_preview": False,
        "broker_order_submission": False,
        "order_cancellation": False,
        "live_trading": False,
    }

    verified_at = datetime.now(
        UTC
    ).isoformat()

    original_freeze_hash = hashlib.sha256(
        ORIGINAL_FREEZE_PATH.read_bytes()
    ).hexdigest()

    evidence = {
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "canonical_stack": "snaptrade",
        "original_mutation_function_records": (
            mutation_function_records
        ),
        "original_mutation_call_records": (
            mutation_call_records
        ),
        "resolved_functions": (
            resolved_functions
        ),
        "resolved_calls": (
            resolved_calls
        ),
        "classification_counts": {
            "local_memory_only": len(
                local_memory_only
            ),
            "confirmed_external": len(
                confirmed_external
            ),
            "capability_mutations": len(
                capability_mutations
            ),
            "unresolved_mutations": len(
                unresolved_mutations
            ),
            "reachable_confirmed_external": len(
                reachable_confirmed_external
            ),
        },
        "incoming_reachability": (
            incoming_by_module
        ),
        "credential_values_read": False,
        "network_request_performed": False,
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    report = {
        "campaign": (
            "NeuroVest Integrated Qualification Campaign"
        ),
        "stage": (
            "IQC Stage 5 SnapTrade Read-Only Preflight "
            "Remediation 1"
        ),
        "name": (
            "Exact Mutation Signal Ownership, Side-Effect, "
            "Reachability, and Read-Only Boundary Disposition"
        ),
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "canonical_stack": "snaptrade",
        "disposition": disposition,
        "authorization": authorization,
        "mutation_disposition": {
            "original_function_signal_count": len(
                mutation_function_records
            ),
            "original_call_signal_count": len(
                mutation_call_records
            ),
            "local_memory_only_count": len(
                local_memory_only
            ),
            "confirmed_external_count": len(
                confirmed_external
            ),
            "capability_mutation_count": len(
                capability_mutations
            ),
            "unresolved_mutation_count": len(
                unresolved_mutations
            ),
            "reachable_confirmed_external_count": len(
                reachable_confirmed_external
            ),
        },
        "exact_blockers": exact_mutation_blockers,
        "supersedes": {
            "baseline": (
                "snaptrade_readonly_scope_preflight_v1"
            ),
            "freeze_path": (
                ORIGINAL_FREEZE_PATH.relative_to(
                    ROOT
                ).as_posix()
            ),
            "freeze_sha256": (
                original_freeze_hash
            ),
            "reason": (
                "The original preflight reported mutation "
                "capability but authorized read-only implementation "
                "without exact mutation ownership and side-effect "
                "disposition."
            ),
            "original_authorization_must_not_be_used": True,
        },
        "credential_values_read": False,
        "network_request_performed": False,
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "Proceed to IQC Stage 5 SnapTrade Read-Only "
            "Contract and Adapter Boundary Design."
            if read_only_implementation_authorized
            else
            "Remediate or quarantine only the exact mutation "
            "signals listed in this report before beginning "
            "the SnapTrade read-only adapter implementation."
        ),
    }

    freeze = {
        "status": "frozen",
        "verified_at": verified_at,
        "canonical_stack": "snaptrade",
        "baseline": (
            "snaptrade_readonly_scope_preflight_v2"
        ),
        "supersedes_baseline": (
            "snaptrade_readonly_scope_preflight_v1"
        ),
        "superseded_freeze_sha256": (
            original_freeze_hash
        ),
        "disposition": disposition,
        "authorization": authorization,
        "resolved_functions": (
            resolved_functions
        ),
        "resolved_calls": (
            resolved_calls
        ),
        "exact_blockers": (
            exact_mutation_blockers
        ),
        "credential_values_read": False,
        "network_request_performed": False,
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    supersession = {
        "status": "completed",
        "verified_at": verified_at,
        "superseded_baseline": (
            "snaptrade_readonly_scope_preflight_v1"
        ),
        "replacement_baseline": (
            "snaptrade_readonly_scope_preflight_v2"
        ),
        "superseded_freeze_sha256": (
            original_freeze_hash
        ),
        "defect": (
            "Mutation capability was reported, but the "
            "authorization calculation did not block read-only "
            "implementation on the mutation blocker."
        ),
        "original_authorization_authoritative": False,
        "replacement_authorization": (
            authorization
        ),
        "source_modified": False,
        "database_modified": False,
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

    SUPERSESSION_JSON.write_text(
        json.dumps(
            supersession,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    text_lines = [
        "=" * 112,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 SNAPTRADE READ-ONLY PREFLIGHT "
            "REMEDIATION 1 — EXACT MUTATION DISPOSITION"
        ),
        "=" * 112,
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
        "ORIGINAL SIGNALS",
        (
            "- Mutation-classified functions: "
            f"{len(mutation_function_records)}"
        ),
        (
            "- Mutation-classified calls: "
            f"{len(mutation_call_records)}"
        ),
        "",
        "EXACT CLASSIFICATION",
        (
            "- Local memory-only operations: "
            f"{len(local_memory_only)}"
        ),
        (
            "- Confirmed external capabilities: "
            f"{len(confirmed_external)}"
        ),
        (
            "- Capability mutation signals: "
            f"{len(capability_mutations)}"
        ),
        (
            "- Unresolved mutation signals: "
            f"{len(unresolved_mutations)}"
        ),
        (
            "- Reachable confirmed external capabilities: "
            f"{len(reachable_confirmed_external)}"
        ),
        "",
        "FUNCTION DISPOSITIONS",
    ]

    if resolved_functions:
        for index, item in enumerate(
            resolved_functions,
            start=1,
        ):
            text_lines.extend(
                [
                    (
                        f"{index}. {item['path']}:"
                        f"{item['line']}"
                    ),
                    (
                        "   Function: "
                        f"{item['name']}"
                    ),
                    (
                        "   Classification: "
                        f"{item['classification']}"
                    ),
                    (
                        "   Reachable outside snaptrade: "
                        + (
                            "YES"
                            if item[
                                "reachable_outside_snaptrade"
                            ]
                            else "NO"
                        )
                    ),
                    (
                        "   Remediation required: "
                        + (
                            "YES"
                            if item[
                                "remediation_required"
                            ]
                            else "NO"
                        )
                    ),
                ]
            )

    else:
        text_lines.append(
            "- None"
        )

    text_lines.extend(
        [
            "",
            "CALL DISPOSITIONS",
        ]
    )

    if resolved_calls:
        for index, item in enumerate(
            resolved_calls,
            start=1,
        ):
            text_lines.extend(
                [
                    (
                        f"{index}. {item['path']}:"
                        f"{item['line']}"
                    ),
                    (
                        "   Scope: "
                        f"{item['scope']}"
                    ),
                    (
                        "   Call: "
                        f"{item['call']}"
                    ),
                    (
                        "   Source: "
                        f"{item['source']}"
                    ),
                    (
                        "   Receiver ownership: "
                        f"{item['receiver_binding']}"
                    ),
                    (
                        "   Classification: "
                        f"{item['classification']}"
                    ),
                    (
                        "   Side effect: "
                        f"{item['side_effect']}"
                    ),
                    (
                        "   Remediation required: "
                        + (
                            "YES"
                            if item[
                                "remediation_required"
                            ]
                            else "NO"
                        )
                    ),
                    (
                        "   Reason: "
                        f"{item['reason']}"
                    ),
                ]
            )

    else:
        text_lines.append(
            "- None"
        )

    text_lines.extend(
        [
            "",
            "CORRECTED AUTHORIZATION",
            (
                "- Adapter scaffolding: "
                + (
                    "AUTHORIZED"
                    if authorization[
                        "adapter_scaffolding"
                    ]
                    else "NOT AUTHORIZED"
                )
            ),
            (
                "- Read-only implementation: "
                + (
                    "AUTHORIZED"
                    if authorization[
                        "read_only_implementation"
                    ]
                    else "NOT AUTHORIZED"
                )
            ),
            "- Credential activation: NOT AUTHORIZED",
            "- Network connection: NOT AUTHORIZED",
            "- User registration: NOT AUTHORIZED",
            "- Brokerage connection: NOT AUTHORIZED",
            "- Order preview: NOT AUTHORIZED",
            "- Broker order submission: NOT AUTHORIZED",
            "- Order cancellation: NOT AUTHORIZED",
            "- Live trading: NOT AUTHORIZED",
            "",
            "EXACT BLOCKERS",
        ]
    )

    if exact_mutation_blockers:
        text_lines.extend(
            f"- {item}"
            for item in exact_mutation_blockers
        )

    else:
        text_lines.append(
            "- None"
        )

    text_lines.extend(
        [
            "",
            "BASELINE REPLACEMENT",
            (
                "- Superseded: "
                "snaptrade_readonly_scope_preflight_v1"
            ),
            (
                "- Replacement: "
                "snaptrade_readonly_scope_preflight_v2"
            ),
            "- Original authorization authoritative: NO",
            "",
            "SAFETY",
            "- Credential values read: NO",
            "- Network request performed: NO",
            "- Production source modified: NO",
            "- Database modified: NO",
            "- SnapTrade connected: NO",
            "- Broker execution enabled: NO",
            "- Live trading enabled: NO",
            "",
            "NEXT",
            report[
                "next_step"
            ],
            "",
            "=" * 112,
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

    print(
        "PASS: all original mutation signals resolved"
    )

    print(
        "PASS: exact source ownership recorded"
    )

    print(
        "PASS: receiver ownership classified"
    )

    print(
        "PASS: local memory operations separated"
    )

    print(
        "PASS: external side effects classified"
    )

    print(
        "PASS: module and symbol reachability inspected"
    )

    print(
        "PASS: authorization decision corrected"
    )

    print(
        "PASS: original preflight freeze superseded"
    )

    print(
        "PASS: corrected v2 preflight baseline frozen"
    )


if __name__ == "__main__":
    main()
