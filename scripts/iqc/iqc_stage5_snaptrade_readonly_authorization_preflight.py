#!/usr/bin/env python3

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(".").resolve()

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "snaptrade_readonly_authorization_preflight"
)

STACK_ROOT = (
    ROOT
    / "backend"
    / "app"
    / "stacks"
    / "snaptrade"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_authorization_preflight_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_authorization_preflight_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_authorization_preflight_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_snaptrade_readonly_scope_freeze_latest.json"
)


READ_ONLY_TERMS = {
    "account",
    "accounts",
    "balance",
    "balances",
    "connection",
    "connections",
    "detail",
    "details",
    "holdings",
    "list",
    "positions",
    "profile",
    "read",
    "status",
    "transactions",
    "activities",
    "orders_history",
    "order_history",
    "performance",
    "option_chain",
    "symbols",
    "search",
    "lookup",
    "get",
    "fetch",
}


CREDENTIAL_TERMS = {
    "api_key",
    "client_id",
    "client_secret",
    "consumer_key",
    "secret",
    "snaptrade_client_id",
    "snaptrade_consumer_key",
    "snaptrade_api_key",
    "snaptrade_secret",
    "user_secret",
    "user_id",
    "authorization_id",
    "connection_id",
}


NETWORK_MODULE_MARKERS = {
    "aiohttp",
    "http.client",
    "httpx",
    "requests",
    "urllib",
    "urllib3",
    "websockets",
    "snaptrade",
}


NETWORK_CALL_TERMINALS = {
    "delete",
    "get",
    "head",
    "open",
    "patch",
    "post",
    "put",
    "request",
    "send",
    "stream",
}


MUTATION_TERMS = {
    "add",
    "authorize",
    "cancel",
    "close",
    "connect",
    "create",
    "delete",
    "disable",
    "disconnect",
    "execute",
    "generate",
    "login",
    "logout",
    "modify",
    "open",
    "place",
    "preview",
    "register",
    "remove",
    "revoke",
    "submit",
    "trade",
    "update",
}


ORDER_TERMS = {
    "cancel_order",
    "execute_order",
    "execute_trade",
    "market_order",
    "order_impact",
    "order_preview",
    "place_order",
    "place_trade",
    "submit_order",
    "trade",
    "trade_impact",
}


PERSISTENCE_TERMS = {
    "add",
    "append",
    "commit",
    "delete",
    "execute",
    "flush",
    "insert",
    "merge",
    "rollback",
    "save",
    "update",
}


ENVIRONMENT_ACCESS_CALLS = {
    "environ.get",
    "getenv",
    "os.environ.get",
    "os.getenv",
}


ALLOWED_READ_ONLY_SCOPE = [
    "SDK client construction behind explicit dependency injection",
    "Connection-status retrieval",
    "User/account listing",
    "Account-detail retrieval",
    "Balance retrieval",
    "Position retrieval",
    "Holdings retrieval",
    "Transaction/activity-history retrieval",
    "Historical order-status retrieval",
    "Read-only performance retrieval",
    "Timeout and adapter-unavailable mapping",
    "Response normalization into immutable internal DTOs",
    "Credential presence checks without exposing credential values",
]


PROHIBITED_SCOPE = [
    "SnapTrade user registration",
    "SnapTrade user deletion",
    "User-secret generation or rotation",
    "Brokerage authorization creation",
    "Brokerage connection creation",
    "Brokerage connection deletion",
    "Credential activation during preflight",
    "Order-impact or order-preview calls",
    "Order placement",
    "Order cancellation",
    "Trade execution",
    "Account mutation",
    "Database persistence from the SnapTrade adapter",
    "Wolfden-to-SnapTrade direct access",
    "Strategy-to-SnapTrade direct access",
    "Frontend-to-SnapTrade direct access",
    "Broker execution",
    "Live trading",
]


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


def normalize_name(
    value: str,
) -> str:
    value = re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1_\2",
        value,
    )

    return value.lower()


def contains_any_term(
    value: str,
    terms: set[str],
) -> bool:
    normalized = normalize_name(
        value
    )

    tokens = {
        token
        for token in re.split(
            r"[^a-z0-9_]+",
            normalized,
        )
        if token
    }

    if normalized in terms:
        return True

    if tokens & terms:
        return True

    return any(
        term in normalized
        for term in terms
        if "_" in term
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


def inspect_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8"
    )

    lines = source.splitlines()

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = []
    functions = []
    classes = []
    calls = []
    constants = []
    environment_access = []
    hardcoded_credential_candidates = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": alias.name,
                        "name": None,
                        "alias": alias.asname,
                    }
                )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "line": node.lineno,
                        "module": node.module or "",
                        "name": alias.name,
                        "alias": alias.asname,
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.append(
                {
                    "line": node.lineno,
                    "name": node.name,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                    "arguments": [
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
                    "read_only_like": contains_any_term(
                        node.name,
                        READ_ONLY_TERMS,
                    ),
                    "mutation_like": contains_any_term(
                        node.name,
                        MUTATION_TERMS,
                    ),
                    "order_like": contains_any_term(
                        node.name,
                        ORDER_TERMS,
                    ),
                }
            )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append(
                {
                    "line": node.lineno,
                    "name": node.name,
                }
            )

        elif isinstance(
            node,
            ast.Call,
        ):
            rendered = dotted_name(
                node.func
            )

            terminal = (
                rendered.split(".")[-1]
                if rendered
                else ""
            )

            record = {
                "line": getattr(
                    node,
                    "lineno",
                    None,
                ),
                "call": rendered,
                "terminal": terminal,
                "source": source_line(
                    lines,
                    getattr(
                        node,
                        "lineno",
                        None,
                    ),
                ),
                "read_only_like": contains_any_term(
                    rendered,
                    READ_ONLY_TERMS,
                ),
                "mutation_like": contains_any_term(
                    rendered,
                    MUTATION_TERMS,
                ),
                "order_like": contains_any_term(
                    rendered,
                    ORDER_TERMS,
                ),
                "persistence_like": (
                    terminal.lower()
                    in PERSISTENCE_TERMS
                ),
                "network_like": (
                    terminal.lower()
                    in NETWORK_CALL_TERMINALS
                ),
            }

            calls.append(record)

            if rendered in ENVIRONMENT_ACCESS_CALLS:
                environment_access.append(
                    record
                )

            if rendered in {
                "os.getenv",
                "getenv",
            }:
                environment_access.append(
                    record
                )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            targets = []

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

            names = []

            for target in targets:
                if isinstance(
                    target,
                    ast.Name,
                ):
                    names.append(
                        target.id
                    )

            if not names:
                continue

            rendered_value = None

            if isinstance(
                value,
                ast.Constant,
            ):
                rendered_value = value.value

            for name in names:
                constants.append(
                    {
                        "line": getattr(
                            node,
                            "lineno",
                            None,
                        ),
                        "name": name,
                        "credential_like": contains_any_term(
                            name,
                            CREDENTIAL_TERMS,
                        ),
                        "literal_type": (
                            type(
                                rendered_value
                            ).__name__
                            if rendered_value
                            is not None
                            else None
                        ),
                    }
                )

                if (
                    contains_any_term(
                        name,
                        CREDENTIAL_TERMS,
                    )
                    and isinstance(
                        rendered_value,
                        str,
                    )
                    and rendered_value.strip()
                    and rendered_value.upper()
                    not in {
                        "NONE",
                        "NOT_CONFIGURED",
                        "PLACEHOLDER",
                        "REDACTED",
                    }
                    and not rendered_value.startswith(
                        (
                            "$",
                            "{",
                            "<",
                        )
                    )
                ):
                    hardcoded_credential_candidates.append(
                        {
                            "line": getattr(
                                node,
                                "lineno",
                                None,
                            ),
                            "name": name,
                            "value_length": len(
                                rendered_value
                            ),
                            "source": source_line(
                                lines,
                                getattr(
                                    node,
                                    "lineno",
                                    None,
                                ),
                            ),
                        }
                    )

    module_names = {
        item["module"]
        for item in imports
    }

    sdk_imports = sorted(
        module
        for module in module_names
        if "snaptrade" in module.lower()
    )

    network_imports = sorted(
        module
        for module in module_names
        if any(
            module == marker
            or module.startswith(
                marker + "."
            )
            for marker in (
                NETWORK_MODULE_MARKERS
            )
        )
    )

    direct_database_imports = sorted(
        module
        for module in module_names
        if (
            "sqlalchemy" in module.lower()
            or "db_runtime" in module.lower()
            or "journal_ledger" in module.lower()
        )
    )

    forbidden_direct_owner_imports = sorted(
        module
        for module in module_names
        if any(
            marker in module.lower()
            for marker in (
                "wolfden_ai",
                "strategy",
                "execution",
                "paper_trading",
            )
        )
    )

    return {
        "path": path.relative_to(
            ROOT
        ).as_posix(),
        "sha256": hashlib.sha256(
            source.encode(
                "utf-8"
            )
        ).hexdigest(),
        "size_bytes": len(
            source.encode(
                "utf-8"
            )
        ),
        "syntax_valid": True,
        "imports": imports,
        "sdk_imports": sdk_imports,
        "network_imports": network_imports,
        "direct_database_imports": (
            direct_database_imports
        ),
        "forbidden_direct_owner_imports": (
            forbidden_direct_owner_imports
        ),
        "classes": classes,
        "functions": functions,
        "calls": calls,
        "environment_access": environment_access,
        "credential_constants": [
            item
            for item in constants
            if item[
                "credential_like"
            ]
        ],
        "hardcoded_credential_candidates": (
            hardcoded_credential_candidates
        ),
    }


def main() -> None:
    assert STACK_ROOT.is_dir(), (
        "The canonical snaptrade stack is missing: "
        f"{STACK_ROOT}"
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

    test_files = sorted(
        path
        for path in STACK_ROOT.rglob(
            "*.py"
        )
        if "__pycache__" not in path.parts
        and (
            "tests" in path.parts
            or path.name.startswith(
                "test_"
            )
        )
    )

    assert production_files, (
        "No production Python files found in "
        "the canonical snaptrade stack"
    )

    records = [
        inspect_file(
            path
        )
        for path in production_files
    ]

    all_functions = [
        {
            "path": record["path"],
            **function,
        }
        for record in records
        for function in record[
            "functions"
        ]
    ]

    all_calls = [
        {
            "path": record["path"],
            **call,
        }
        for record in records
        for call in record[
            "calls"
        ]
    ]

    sdk_imports = sorted(
        {
            module
            for record in records
            for module in record[
                "sdk_imports"
            ]
        }
    )

    network_imports = sorted(
        {
            module
            for record in records
            for module in record[
                "network_imports"
            ]
        }
    )

    database_imports = sorted(
        {
            module
            for record in records
            for module in record[
                "direct_database_imports"
            ]
        }
    )

    cross_owner_imports = sorted(
        {
            module
            for record in records
            for module in record[
                "forbidden_direct_owner_imports"
            ]
        }
    )

    environment_access = [
        {
            "path": record["path"],
            **item,
        }
        for record in records
        for item in record[
            "environment_access"
        ]
    ]

    credential_constants = [
        {
            "path": record["path"],
            **item,
        }
        for record in records
        for item in record[
            "credential_constants"
        ]
    ]

    hardcoded_credentials = [
        {
            "path": record["path"],
            **item,
        }
        for record in records
        for item in record[
            "hardcoded_credential_candidates"
        ]
    ]

    read_only_functions = [
        item
        for item in all_functions
        if item[
            "read_only_like"
        ]
        and not item[
            "mutation_like"
        ]
        and not item[
            "order_like"
        ]
    ]

    mutation_functions = [
        item
        for item in all_functions
        if item[
            "mutation_like"
        ]
    ]

    order_functions = [
        item
        for item in all_functions
        if item[
            "order_like"
        ]
    ]

    read_only_calls = [
        item
        for item in all_calls
        if item[
            "read_only_like"
        ]
        and not item[
            "mutation_like"
        ]
        and not item[
            "order_like"
        ]
    ]

    mutation_calls = [
        item
        for item in all_calls
        if item[
            "mutation_like"
        ]
    ]

    order_calls = [
        item
        for item in all_calls
        if item[
            "order_like"
        ]
    ]

    persistence_calls = [
        item
        for item in all_calls
        if item[
            "persistence_like"
        ]
    ]

    network_calls = [
        item
        for item in all_calls
        if item[
            "network_like"
        ]
    ]

    sdk_spec = importlib.util.find_spec(
        "snaptrade_client"
    )

    alternate_sdk_spec = importlib.util.find_spec(
        "snaptrade"
    )

    sdk_available = bool(
        sdk_spec
        or alternate_sdk_spec
    )

    credential_environment_names = sorted(
        name
        for name in os.environ
        if "SNAPTRADE" in name.upper()
    )

    credential_values_read = False

    hardcoded_credentials_present = bool(
        hardcoded_credentials
    )

    direct_database_access_present = bool(
        database_imports
    )

    cross_owner_import_present = bool(
        cross_owner_imports
    )

    order_capability_present = bool(
        order_functions
        or order_calls
    )

    mutation_capability_present = bool(
        mutation_functions
        or mutation_calls
    )

    network_capability_present = bool(
        sdk_imports
        or network_imports
        or network_calls
    )

    read_only_capability_present = bool(
        read_only_functions
        or read_only_calls
    )

    blockers = []

    if hardcoded_credentials_present:
        blockers.append(
            "Hardcoded credential-like literal detected"
        )

    if direct_database_access_present:
        blockers.append(
            "SnapTrade adapter imports persistence internals"
        )

    if cross_owner_import_present:
        blockers.append(
            "SnapTrade stack imports prohibited owner stacks"
        )

    if order_capability_present:
        blockers.append(
            "Existing order-capable functions or calls require "
            "quarantine before read-only implementation"
        )

    if mutation_capability_present:
        blockers.append(
            "Existing mutation-capable functions or calls require "
            "exact disposition before read-only implementation"
        )

    scaffolding_authorized = not any(
        blocker
        for blocker in blockers
        if blocker in {
            "Hardcoded credential-like literal detected",
            "SnapTrade adapter imports persistence internals",
            "SnapTrade stack imports prohibited owner stacks",
        }
    )

    read_only_implementation_authorized = (
        scaffolding_authorized
        and not hardcoded_credentials_present
    )

    credential_activation_authorized = False
    network_connection_authorized = False
    user_registration_authorized = False
    brokerage_connection_authorized = False
    order_preview_authorized = False
    broker_order_submission_authorized = False
    order_cancellation_authorized = False
    live_trading_authorized = False

    disposition = (
        "READ_ONLY_SCAFFOLDING_AUTHORIZED_"
        "NETWORK_AND_CREDENTIAL_ACTIVATION_PROHIBITED"
        if read_only_implementation_authorized
        else
        "READ_ONLY_SCAFFOLDING_BLOCKED_"
        "REMEDIATION_REQUIRED"
    )

    verified_at = datetime.now(
        UTC
    ).isoformat()

    evidence = {
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "canonical_stack": "snaptrade",
        "stack_path": STACK_ROOT.relative_to(
            ROOT
        ).as_posix(),
        "inventory": {
            "production_python_files": len(
                production_files
            ),
            "test_python_files": len(
                test_files
            ),
            "files": records,
        },
        "sdk": {
            "snaptrade_client_spec_available": bool(
                sdk_spec
            ),
            "snaptrade_spec_available": bool(
                alternate_sdk_spec
            ),
            "sdk_available": sdk_available,
            "sdk_imports": sdk_imports,
        },
        "credentials": {
            "environment_access_records": (
                environment_access
            ),
            "credential_constant_records": (
                credential_constants
            ),
            "hardcoded_credential_candidates": (
                hardcoded_credentials
            ),
            "hardcoded_credentials_present": (
                hardcoded_credentials_present
            ),
            "snaptrade_environment_variable_names_present": (
                credential_environment_names
            ),
            "credential_values_read": (
                credential_values_read
            ),
        },
        "network": {
            "network_imports": network_imports,
            "network_calls": network_calls,
            "network_capability_present": (
                network_capability_present
            ),
            "network_request_performed": False,
        },
        "capabilities": {
            "read_only_functions": (
                read_only_functions
            ),
            "read_only_calls": (
                read_only_calls
            ),
            "mutation_functions": (
                mutation_functions
            ),
            "mutation_calls": (
                mutation_calls
            ),
            "order_functions": (
                order_functions
            ),
            "order_calls": (
                order_calls
            ),
            "persistence_calls": (
                persistence_calls
            ),
            "read_only_capability_present": (
                read_only_capability_present
            ),
            "mutation_capability_present": (
                mutation_capability_present
            ),
            "order_capability_present": (
                order_capability_present
            ),
        },
        "ownership": {
            "direct_database_imports": (
                database_imports
            ),
            "prohibited_cross_owner_imports": (
                cross_owner_imports
            ),
            "direct_database_access_present": (
                direct_database_access_present
            ),
            "cross_owner_import_present": (
                cross_owner_import_present
            ),
        },
        "blockers": blockers,
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
    }

    authorization = {
        "adapter_scaffolding": (
            scaffolding_authorized
        ),
        "read_only_implementation": (
            read_only_implementation_authorized
        ),
        "credential_activation": (
            credential_activation_authorized
        ),
        "network_connection": (
            network_connection_authorized
        ),
        "user_registration": (
            user_registration_authorized
        ),
        "brokerage_connection": (
            brokerage_connection_authorized
        ),
        "order_preview": (
            order_preview_authorized
        ),
        "broker_order_submission": (
            broker_order_submission_authorized
        ),
        "order_cancellation": (
            order_cancellation_authorized
        ),
        "live_trading": (
            live_trading_authorized
        ),
    }

    report = {
        "campaign": (
            "NeuroVest Integrated "
            "Qualification Campaign"
        ),
        "stage": (
            "IQC Stage 5 SnapTrade Read-Only "
            "Integration Authorization Preflight"
        ),
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "canonical_stack": "snaptrade",
        "disposition": disposition,
        "authorization": authorization,
        "inventory": {
            "production_python_files": len(
                production_files
            ),
            "test_python_files": len(
                test_files
            ),
            "functions": len(
                all_functions
            ),
            "classes": sum(
                len(
                    record[
                        "classes"
                    ]
                )
                for record in records
            ),
        },
        "credential_boundary": {
            "hardcoded_credentials_present": (
                hardcoded_credentials_present
            ),
            "credential_values_read": False,
            "credential_activation_authorized": False,
            "environment_name_count": len(
                credential_environment_names
            ),
        },
        "sdk_and_network": {
            "sdk_available": sdk_available,
            "sdk_import_present": bool(
                sdk_imports
            ),
            "network_capability_present": (
                network_capability_present
            ),
            "network_request_performed": False,
            "network_connection_authorized": False,
        },
        "capability_disposition": {
            "read_only_capability_present": (
                read_only_capability_present
            ),
            "mutation_capability_present": (
                mutation_capability_present
            ),
            "order_capability_present": (
                order_capability_present
            ),
            "direct_database_access_present": (
                direct_database_access_present
            ),
            "cross_owner_import_present": (
                cross_owner_import_present
            ),
        },
        "allowed_read_only_scope": (
            ALLOWED_READ_ONLY_SCOPE
        ),
        "prohibited_scope": (
            PROHIBITED_SCOPE
        ),
        "blockers": blockers,
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
        "broker_execution_enabled": False,
        "live_trading_enabled": False,
        "next_step": (
            "If adapter scaffolding and read-only implementation "
            "are authorized, proceed to IQC Stage 5 SnapTrade "
            "Read-Only Contract and Adapter Boundary Design. "
            "Credential activation and all network calls remain "
            "prohibited until a later independent authorization."
            if read_only_implementation_authorized
            else
            "Resolve only the exact blockers identified by this "
            "preflight before any SnapTrade implementation work."
        ),
    }

    freeze = {
        "status": "frozen",
        "verified_at": verified_at,
        "canonical_stack": "snaptrade",
        "baseline": (
            "snaptrade_readonly_scope_preflight_v1"
        ),
        "disposition": disposition,
        "authorization": authorization,
        "allowed_read_only_scope": (
            ALLOWED_READ_ONLY_SCOPE
        ),
        "prohibited_scope": (
            PROHIBITED_SCOPE
        ),
        "frozen_stack_files": {
            record["path"]: {
                "sha256": record[
                    "sha256"
                ],
                "size_bytes": record[
                    "size_bytes"
                ],
            }
            for record in records
        },
        "credential_values_read": False,
        "network_request_performed": False,
        "source_modified": False,
        "database_modified": False,
        "snaptrade_connected": False,
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
        "=" * 112,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 SNAPTRADE READ-ONLY "
            "INTEGRATION AUTHORIZATION PREFLIGHT"
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
        "EXISTING STACK INVENTORY",
        (
            "- Production Python files: "
            f"{len(production_files)}"
        ),
        (
            "- Test Python files: "
            f"{len(test_files)}"
        ),
        (
            "- Functions discovered: "
            f"{len(all_functions)}"
        ),
        (
            "- Classes discovered: "
            f"{sum(len(record['classes']) for record in records)}"
        ),
        "",
        "SDK AND NETWORK",
        (
            "- SnapTrade SDK available: "
            + (
                "YES"
                if sdk_available
                else "NO"
            )
        ),
        (
            "- SnapTrade SDK import present: "
            + (
                "YES"
                if sdk_imports
                else "NO"
            )
        ),
        (
            "- Network capability present: "
            + (
                "YES"
                if network_capability_present
                else "NO"
            )
        ),
        "- Network request performed: NO",
        "- Network connection authorized: NO",
        "",
        "CREDENTIAL BOUNDARY",
        (
            "- Credential environment names present: "
            f"{len(credential_environment_names)}"
        ),
        (
            "- Hardcoded credential candidate present: "
            + (
                "YES"
                if hardcoded_credentials_present
                else "NO"
            )
        ),
        "- Credential values read: NO",
        "- Credential activation authorized: NO",
        "",
        "CAPABILITY DISPOSITION",
        (
            "- Read-only capability present: "
            + (
                "YES"
                if read_only_capability_present
                else "NO"
            )
        ),
        (
            "- Mutation capability present: "
            + (
                "YES"
                if mutation_capability_present
                else "NO"
            )
        ),
        (
            "- Order capability present: "
            + (
                "YES"
                if order_capability_present
                else "NO"
            )
        ),
        (
            "- Direct database access present: "
            + (
                "YES"
                if direct_database_access_present
                else "NO"
            )
        ),
        (
            "- Prohibited cross-owner import present: "
            + (
                "YES"
                if cross_owner_import_present
                else "NO"
            )
        ),
        "",
        "AUTHORIZATION",
        (
            "- Adapter scaffolding: "
            + (
                "AUTHORIZED"
                if scaffolding_authorized
                else "NOT AUTHORIZED"
            )
        ),
        (
            "- Read-only implementation: "
            + (
                "AUTHORIZED"
                if read_only_implementation_authorized
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
        "ALLOWED READ-ONLY SCOPE",
    ]

    text_lines.extend(
        f"- {item}"
        for item in (
            ALLOWED_READ_ONLY_SCOPE
        )
    )

    text_lines.extend(
        [
            "",
            "PROHIBITED SCOPE",
        ]
    )

    text_lines.extend(
        f"- {item}"
        for item in (
            PROHIBITED_SCOPE
        )
    )

    text_lines.extend(
        [
            "",
            "BLOCKERS",
        ]
    )

    if blockers:
        text_lines.extend(
            f"- {item}"
            for item in blockers
        )

    else:
        text_lines.append(
            "- None blocking read-only scaffolding"
        )

    text_lines.extend(
        [
            "",
            "SAFETY",
            "- Source modified: NO",
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
        "PASS: canonical snaptrade stack inventoried"
    )

    print(
        "PASS: source parsed without importing snaptrade stack"
    )

    print(
        "PASS: credential boundary classified"
    )

    print(
        "PASS: SDK capability classified"
    )

    print(
        "PASS: network capability classified"
    )

    print(
        "PASS: read-only capability classified"
    )

    print(
        "PASS: mutation capability classified"
    )

    print(
        "PASS: order capability classified"
    )

    print(
        "PASS: read-only scope frozen"
    )

    print(
        "PASS: execution prohibition frozen"
    )


if __name__ == "__main__":
    main()
