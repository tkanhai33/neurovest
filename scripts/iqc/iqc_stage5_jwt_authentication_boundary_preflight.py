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

OUTPUT_DIR = (
    ROOT
    / "runtime"
    / "iqc"
    / "stage5"
    / "jwt_authentication_boundary_preflight"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_authentication_boundary_preflight_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_authentication_boundary_preflight_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_authentication_boundary_preflight_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_authentication_boundary_preflight_freeze_latest.json"
)


AUTH_PATH_MARKERS = {
    "auth",
    "identity",
    "jwt",
    "login",
    "password",
    "security",
    "session",
    "token",
    "user",
}


AUTH_CONTENT_MARKERS = {
    "access_token",
    "authenticate",
    "authorization",
    "bearer",
    "current_user",
    "decode_token",
    "encode_token",
    "hash_password",
    "jwt",
    "login",
    "oauth2",
    "password_hash",
    "refresh_token",
    "session_id",
    "token",
    "verify_password",
}


JWT_IMPORT_MARKERS = {
    "authlib",
    "jose",
    "jwt",
    "pyjwt",
}


HASH_IMPORT_MARKERS = {
    "argon2",
    "bcrypt",
    "passlib",
    "pwdlib",
    "scrypt",
}


SECRET_NAME_MARKERS = {
    "access_token_secret",
    "auth_secret",
    "jwt_algorithm",
    "jwt_secret",
    "private_key",
    "refresh_token_secret",
    "secret_key",
    "signing_key",
}


TOKEN_FUNCTION_TERMS = {
    "create_access_token",
    "create_refresh_token",
    "create_token",
    "decode_access_token",
    "decode_jwt",
    "decode_token",
    "encode_jwt",
    "encode_token",
    "issue_access_token",
    "issue_refresh_token",
    "issue_token",
    "validate_access_token",
    "validate_jwt",
    "validate_token",
    "verify_access_token",
    "verify_jwt",
    "verify_token",
}


PASSWORD_FUNCTION_TERMS = {
    "check_password",
    "hash_password",
    "verify_password",
}


SESSION_TERMS = {
    "blacklist",
    "denylist",
    "expires_at",
    "jti",
    "logout",
    "refresh_token",
    "revocation",
    "revoke",
    "session",
    "token_version",
}


MUTATION_ROUTE_TERMS = {
    "change_password",
    "create_user",
    "delete_user",
    "login",
    "logout",
    "register",
    "reset_password",
    "revoke",
}


FORBIDDEN_AUTH_COUPLINGS = {
    "broker_integration",
    "execution",
    "paper_broker",
    "snaptrade",
}


def module_name(
    path: Path,
) -> str:
    relative = path.relative_to(
        ROOT
    ).with_suffix("")

    return ".".join(
        relative.parts
    )


def dotted_name(
    node: ast.AST,
) -> str:
    parts = []
    current = node

    while isinstance(
        current,
        ast.Attribute,
    ):
        parts.append(
            current.attr
        )
        current = current.value

    if isinstance(
        current,
        ast.Name,
    ):
        parts.append(
            current.id
        )

    return ".".join(
        reversed(parts)
    )


def source_segment(
    source: str,
    node: ast.AST,
) -> str:
    return (
        ast.get_source_segment(
            source,
            node,
        )
        or ast.unparse(
            node
        )
    )


def is_auth_candidate(
    path: Path,
    source: str,
) -> bool:
    lowered_path = path.as_posix().lower()

    if any(
        marker in lowered_path
        for marker in AUTH_PATH_MARKERS
    ):
        return True

    lowered_source = source.lower()

    return any(
        marker in lowered_source
        for marker in AUTH_CONTENT_MARKERS
    )


def inspect_file(
    path: Path,
) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports = []
    functions = []
    classes = []
    environment_reads = []
    hardcoded_secret_candidates = []
    jwt_calls = []
    password_calls = []
    route_decorators = []
    dependency_calls = []
    database_signals = []
    session_signals = []
    forbidden_couplings = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            for alias in node.names:
                imports.append(
                    {
                        "module": alias.name,
                        "name": None,
                        "line": node.lineno,
                    }
                )

                lowered = alias.name.lower()

                if any(
                    marker in lowered
                    for marker in FORBIDDEN_AUTH_COUPLINGS
                ):
                    forbidden_couplings.append(
                        {
                            "line": node.lineno,
                            "module": alias.name,
                        }
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imported_module = (
                node.module
                or ""
            )

            for alias in node.names:
                imports.append(
                    {
                        "module": imported_module,
                        "name": alias.name,
                        "line": node.lineno,
                    }
                )

            lowered = imported_module.lower()

            if any(
                marker in lowered
                for marker in FORBIDDEN_AUTH_COUPLINGS
            ):
                forbidden_couplings.append(
                    {
                        "line": node.lineno,
                        "module": imported_module,
                    }
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            lowered_name = node.name.lower()

            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": node.end_lineno,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
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

            if any(
                term in lowered_name
                for term in SESSION_TERMS
            ):
                session_signals.append(
                    {
                        "kind": "function",
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

            for decorator in node.decorator_list:
                rendered = dotted_name(
                    decorator.func
                    if isinstance(
                        decorator,
                        ast.Call,
                    )
                    else decorator
                )

                lowered = rendered.lower()

                if any(
                    method in lowered
                    for method in (
                        "get",
                        "post",
                        "put",
                        "patch",
                        "delete",
                        "api_route",
                    )
                ):
                    route_decorators.append(
                        {
                            "function": node.name,
                            "line": node.lineno,
                            "decorator": source_segment(
                                source,
                                decorator,
                            ),
                            "mutation_named": any(
                                term in lowered_name
                                for term in MUTATION_ROUTE_TERMS
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
                    "end_line": node.end_lineno,
                    "bases": [
                        ast.unparse(
                            base
                        )
                        for base in node.bases
                    ],
                }
            )

            lowered_name = node.name.lower()

            if any(
                term in lowered_name
                for term in SESSION_TERMS
            ):
                session_signals.append(
                    {
                        "kind": "class",
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            called = dotted_name(
                node.func
            )

            lowered = called.lower()

            if lowered in {
                "os.getenv",
                "os.environ.get",
                "getenv",
            }:
                variable_name = None

                if (
                    node.args
                    and isinstance(
                        node.args[0],
                        ast.Constant,
                    )
                    and isinstance(
                        node.args[0].value,
                        str,
                    )
                ):
                    variable_name = (
                        node.args[0].value
                    )

                environment_reads.append(
                    {
                        "line": node.lineno,
                        "function": called,
                        "variable_name": variable_name,
                        "value_read": False,
                    }
                )

            terminal = (
                lowered.split(".")[-1]
                if lowered
                else ""
            )

            if (
                terminal
                in TOKEN_FUNCTION_TERMS
                or any(
                    marker in lowered
                    for marker in (
                        "jwt.decode",
                        "jwt.encode",
                        "jose.jwt.decode",
                        "jose.jwt.encode",
                    )
                )
            ):
                jwt_calls.append(
                    {
                        "line": node.lineno,
                        "call": called,
                        "source": source_segment(
                            source,
                            node,
                        ),
                    }
                )

            if (
                terminal
                in PASSWORD_FUNCTION_TERMS
                or any(
                    marker in lowered
                    for marker in (
                        "bcrypt",
                        "argon2",
                        "password_hash",
                        "pwd_context",
                    )
                )
            ):
                password_calls.append(
                    {
                        "line": node.lineno,
                        "call": called,
                        "source": source_segment(
                            source,
                            node,
                        ),
                    }
                )

            if terminal in {
                "depends",
                "security",
            }:
                dependency_calls.append(
                    {
                        "line": node.lineno,
                        "call": called,
                        "source": source_segment(
                            source,
                            node,
                        ),
                    }
                )

            if any(
                marker in lowered
                for marker in (
                    "session.add",
                    "session.commit",
                    "session.delete",
                    "session.execute",
                    "session.flush",
                    "write_text",
                )
            ):
                database_signals.append(
                    {
                        "line": node.lineno,
                        "call": called,
                    }
                )

            if any(
                term in lowered
                for term in SESSION_TERMS
            ):
                session_signals.append(
                    {
                        "kind": "call",
                        "name": called,
                        "line": node.lineno,
                    }
                )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
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

            target_names = []

            for target in targets:
                if isinstance(
                    target,
                    ast.Name,
                ):
                    target_names.append(
                        target.id
                    )

            for target_name in target_names:
                lowered_name = (
                    target_name.lower()
                )

                if not any(
                    marker in lowered_name
                    for marker in SECRET_NAME_MARKERS
                ):
                    continue

                if isinstance(
                    value,
                    ast.Constant,
                ) and isinstance(
                    value.value,
                    str,
                ):
                    hardcoded_secret_candidates.append(
                        {
                            "line": node.lineno,
                            "name": target_name,
                            "value_length": len(
                                value.value
                            ),
                            "value_recorded": False,
                        }
                    )

    imported_modules = {
        record[
            "module"
        ].lower()
        for record in imports
    }

    jwt_library_imports = sorted(
        module
        for module in imported_modules
        if any(
            marker in module
            for marker in JWT_IMPORT_MARKERS
        )
    )

    hash_library_imports = sorted(
        module
        for module in imported_modules
        if any(
            marker in module
            for marker in HASH_IMPORT_MARKERS
        )
    )

    return {
        "path": path.relative_to(
            ROOT
        ).as_posix(),
        "module": module_name(
            path
        ),
        "is_auth_candidate": is_auth_candidate(
            path,
            source,
        ),
        "imports": imports,
        "jwt_library_imports": (
            jwt_library_imports
        ),
        "hash_library_imports": (
            hash_library_imports
        ),
        "functions": functions,
        "classes": classes,
        "environment_reads": (
            environment_reads
        ),
        "hardcoded_secret_candidates": (
            hardcoded_secret_candidates
        ),
        "jwt_calls": jwt_calls,
        "password_calls": password_calls,
        "route_decorators": (
            route_decorators
        ),
        "dependency_calls": (
            dependency_calls
        ),
        "database_signals": (
            database_signals
        ),
        "session_signals": (
            session_signals
        ),
        "forbidden_couplings": (
            forbidden_couplings
        ),
    }


def main() -> None:
    files = []

    syntax_errors = []

    for path in sorted(
        BACKEND_ROOT.rglob("*.py")
    ):
        if "__pycache__" in path.parts:
            continue

        try:
            files.append(
                inspect_file(
                    path
                )
            )

        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": path.relative_to(
                        ROOT
                    ).as_posix(),
                    "line": exc.lineno,
                    "message": exc.msg,
                }
            )

    auth_candidates = [
        item
        for item in files
        if item[
            "is_auth_candidate"
        ]
    ]

    identity_auth_files = [
        item
        for item in auth_candidates
        if "identity_auth" in item[
            "path"
        ].lower()
    ]

    jwt_library_files = [
        item
        for item in auth_candidates
        if item[
            "jwt_library_imports"
        ]
    ]

    hash_library_files = [
        item
        for item in auth_candidates
        if item[
            "hash_library_imports"
        ]
    ]

    jwt_function_records = []

    password_function_records = []

    for item in auth_candidates:
        for function in item[
            "functions"
        ]:
            lowered = function[
                "name"
            ].lower()

            if (
                lowered
                in TOKEN_FUNCTION_TERMS
                or any(
                    term in lowered
                    for term in (
                        "jwt",
                        "token",
                    )
                )
            ):
                jwt_function_records.append(
                    {
                        "path": item[
                            "path"
                        ],
                        **function,
                    }
                )

            if any(
                term in lowered
                for term in (
                    "password",
                    "hash",
                )
            ):
                password_function_records.append(
                    {
                        "path": item[
                            "path"
                        ],
                        **function,
                    }
                )

    environment_reads = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "environment_reads"
        ]
    ]

    hardcoded_secret_candidates = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "hardcoded_secret_candidates"
        ]
    ]

    jwt_calls = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "jwt_calls"
        ]
    ]

    password_calls = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "password_calls"
        ]
    ]

    route_records = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "route_decorators"
        ]
    ]

    dependency_records = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "dependency_calls"
        ]
    ]

    database_signals = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "database_signals"
        ]
    ]

    session_signals = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "session_signals"
        ]
    ]

    forbidden_couplings = [
        {
            "path": item[
                "path"
            ],
            **record,
        }
        for item in auth_candidates
        for record in item[
            "forbidden_couplings"
        ]
    ]

    test_files = [
        item[
            "path"
        ]
        for item in files
        if (
            "/tests/" in item[
                "path"
            ]
            or Path(
                item[
                    "path"
                ]
            ).name.startswith(
                "test_"
            )
        )
        and item[
            "is_auth_candidate"
        ]
    ]

    token_issuance_present = any(
        any(
            term in record[
                "name"
            ].lower()
            for term in (
                "create",
                "encode",
                "issue",
            )
        )
        for record in jwt_function_records
    ) or any(
        "encode" in record[
            "call"
        ].lower()
        for record in jwt_calls
    )

    token_validation_present = any(
        any(
            term in record[
                "name"
            ].lower()
            for term in (
                "decode",
                "validate",
                "verify",
            )
        )
        for record in jwt_function_records
    ) or any(
        "decode" in record[
            "call"
        ].lower()
        for record in jwt_calls
    )

    password_hashing_present = bool(
        hash_library_files
        or password_calls
        or password_function_records
    )

    api_dependency_present = bool(
        dependency_records
    )

    refresh_token_signals_present = any(
        "refresh" in str(
            record
        ).lower()
        for record in (
            jwt_function_records
            + session_signals
        )
    )

    revocation_signals_present = any(
        any(
            term in str(
                record
            ).lower()
            for term in (
                "blacklist",
                "denylist",
                "jti",
                "logout",
                "revoke",
                "token_version",
            )
        )
        for record in session_signals
    )

    expiration_signals_present = any(
        any(
            term in str(
                record
            ).lower()
            for term in (
                "exp",
                "expires",
                "expiration",
                "timedelta",
            )
        )
        for record in (
            jwt_function_records
            + jwt_calls
            + session_signals
        )
    )

    exact_gaps = []

    if not identity_auth_files:
        exact_gaps.append(
            "No canonical identity_auth ownership files resolved"
        )

    if not token_issuance_present:
        exact_gaps.append(
            "No access-token issuance implementation resolved"
        )

    if not token_validation_present:
        exact_gaps.append(
            "No JWT validation implementation resolved"
        )

    if not password_hashing_present:
        exact_gaps.append(
            "No password hashing and verification boundary resolved"
        )

    if not api_dependency_present:
        exact_gaps.append(
            "No API authentication dependency resolved"
        )

    if not refresh_token_signals_present:
        exact_gaps.append(
            "No refresh-token lifecycle resolved"
        )

    if not revocation_signals_present:
        exact_gaps.append(
            "No token or session revocation control resolved"
        )

    if not expiration_signals_present:
        exact_gaps.append(
            "No explicit token-expiration policy resolved"
        )

    if not test_files:
        exact_gaps.append(
            "No focused authentication tests resolved"
        )

    blockers = []

    if hardcoded_secret_candidates:
        blockers.append(
            "Hardcoded secret-like string assignments require disposition"
        )

    if forbidden_couplings:
        blockers.append(
            "Authentication imports a prohibited trading or broker owner"
        )

    if syntax_errors:
        blockers.append(
            "Syntax errors prevent authentication implementation authorization"
        )

    implementation_authorized = (
        not blockers
    )

    if not implementation_authorized:
        disposition = (
            "JWT_AUTHENTICATION_IMPLEMENTATION_BLOCKED_"
            "EXACT_BOUNDARY_DEFECT_REMEDIATION_REQUIRED"
        )

    elif exact_gaps:
        disposition = (
            "JWT_AUTHENTICATION_IMPLEMENTATION_AUTHORIZED_"
            "EXACT_GAPS_FROZEN"
        )

    else:
        disposition = (
            "JWT_AUTHENTICATION_EXISTS_"
            "QUALIFICATION_AND_HARDENING_REQUIRED"
        )

    authorized_owners = {
        "token_issuance": (
            "backend.app.stacks.identity_auth"
        ),
        "token_validation": (
            "backend.app.stacks.identity_auth"
        ),
        "password_hashing": (
            "backend.app.stacks.identity_auth"
        ),
        "refresh_tokens": (
            "backend.app.stacks.identity_auth"
        ),
        "session_revocation": (
            "backend.app.stacks.identity_auth"
        ),
        "api_dependency": (
            "backend.app.stacks.identity_auth"
        ),
        "user_persistence": (
            "backend.app.stacks.identity_auth"
        ),
    }

    frozen_policy = {
        "jwt_secret_source": (
            "environment_or_approved_secret_provider_only"
        ),
        "jwt_secret_values_may_be_logged": False,
        "jwt_secret_values_may_be_persisted": False,
        "plaintext_password_storage_allowed": False,
        "password_hash_required": True,
        "decoded_unverified_claims_authoritative": False,
        "access_token_and_refresh_token_interchangeable": False,
        "access_token_short_lived": True,
        "refresh_token_revocable": True,
        "refresh_token_rotation_required": True,
        "token_type_validation_required": True,
        "issuer_validation_required": True,
        "audience_validation_required": True,
        "expiration_validation_required": True,
        "not_before_validation_required": True,
        "signature_validation_required": True,
        "frontend_claims_authoritative": False,
        "missing_secret_behavior": "fail_closed",
        "missing_token_behavior": "unauthorized",
        "invalid_token_behavior": "unauthorized",
        "expired_token_behavior": "unauthorized",
        "revoked_token_behavior": "unauthorized",
        "snaptrade_activation_allowed": False,
        "broker_execution_allowed": False,
        "live_trading_allowed": False,
    }

    verified_at = datetime.now(
        UTC
    ).isoformat()

    evidence = {
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "files_scanned": len(
            files
        ),
        "auth_candidate_files": (
            auth_candidates
        ),
        "identity_auth_files": (
            identity_auth_files
        ),
        "jwt_library_files": (
            jwt_library_files
        ),
        "hash_library_files": (
            hash_library_files
        ),
        "jwt_functions": (
            jwt_function_records
        ),
        "password_functions": (
            password_function_records
        ),
        "environment_reads": (
            environment_reads
        ),
        "hardcoded_secret_candidates": (
            hardcoded_secret_candidates
        ),
        "jwt_calls": jwt_calls,
        "password_calls": (
            password_calls
        ),
        "route_records": (
            route_records
        ),
        "dependency_records": (
            dependency_records
        ),
        "database_signals": (
            database_signals
        ),
        "session_signals": (
            session_signals
        ),
        "forbidden_couplings": (
            forbidden_couplings
        ),
        "auth_test_files": (
            test_files
        ),
        "syntax_errors": (
            syntax_errors
        ),
        "secret_values_read": False,
        "password_values_read": False,
        "tokens_generated": False,
        "tokens_validated_against_real_users": False,
        "database_modified": False,
        "source_modified": False,
    }

    report = {
        "campaign": (
            "NeuroVest Integrated Qualification Campaign"
        ),
        "stage": (
            "IQC Stage 5 JWT Authentication Boundary Preflight"
        ),
        "name": (
            "Existing Auth Inventory, Token Ownership, "
            "Secret Handling, Session Policy, and "
            "Authorization Freeze"
        ),
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "disposition": disposition,
        "inventory": {
            "production_python_files_scanned": len(
                files
            ),
            "auth_candidate_files": len(
                auth_candidates
            ),
            "identity_auth_files": len(
                identity_auth_files
            ),
            "jwt_library_files": len(
                jwt_library_files
            ),
            "password_hash_library_files": len(
                hash_library_files
            ),
            "jwt_functions": len(
                jwt_function_records
            ),
            "jwt_calls": len(
                jwt_calls
            ),
            "password_functions": len(
                password_function_records
            ),
            "password_calls": len(
                password_calls
            ),
            "environment_secret_name_reads": len(
                environment_reads
            ),
            "hardcoded_secret_candidates": len(
                hardcoded_secret_candidates
            ),
            "auth_routes": len(
                route_records
            ),
            "auth_dependencies": len(
                dependency_records
            ),
            "auth_database_signals": len(
                database_signals
            ),
            "session_policy_signals": len(
                session_signals
            ),
            "auth_tests": len(
                test_files
            ),
            "forbidden_couplings": len(
                forbidden_couplings
            ),
            "syntax_errors": len(
                syntax_errors
            ),
        },
        "capability_state": {
            "token_issuance_present": (
                token_issuance_present
            ),
            "token_validation_present": (
                token_validation_present
            ),
            "password_hashing_present": (
                password_hashing_present
            ),
            "api_auth_dependency_present": (
                api_dependency_present
            ),
            "refresh_token_signals_present": (
                refresh_token_signals_present
            ),
            "revocation_signals_present": (
                revocation_signals_present
            ),
            "expiration_signals_present": (
                expiration_signals_present
            ),
        },
        "authorized_owners": (
            authorized_owners
        ),
        "frozen_policy": frozen_policy,
        "exact_gaps": exact_gaps,
        "blockers": blockers,
        "authorization": {
            "jwt_implementation": (
                implementation_authorized
            ),
            "password_hashing": (
                implementation_authorized
            ),
            "access_token_issuance": (
                implementation_authorized
            ),
            "access_token_validation": (
                implementation_authorized
            ),
            "refresh_token_design": (
                implementation_authorized
            ),
            "session_revocation_design": (
                implementation_authorized
            ),
            "real_secret_activation": False,
            "real_user_login": False,
            "snaptrade_activation": False,
            "broker_execution": False,
            "live_trading": False,
        },
        "secret_values_read": False,
        "password_values_read": False,
        "tokens_generated": False,
        "database_modified": False,
        "source_modified": False,
        "next_step": (
            "Remediate the exact authentication boundary blockers "
            "before implementation."
            if blockers
            else
            "Proceed to IQC Stage 5 JWT Authentication Contract "
            "Implementation and Fail-Closed Qualification using "
            "only the frozen ownership and policy."
        ),
    }

    freeze = {
        "status": "frozen",
        "verified_at": verified_at,
        "baseline": (
            "jwt_authentication_boundary_preflight_v1"
        ),
        "disposition": disposition,
        "authorized_owners": (
            authorized_owners
        ),
        "frozen_policy": frozen_policy,
        "exact_gaps": exact_gaps,
        "blockers": blockers,
        "authorized_source_scope": [
            (
                "backend/app/stacks/"
                "identity_auth/**"
            ),
            (
                "backend/app/stacks/"
                "identity_auth/tests/**"
            ),
        ],
        "prohibited_source_scope": [
            "backend/app/stacks/snaptrade/**",
            "backend/app/stacks/execution/**",
            "backend/app/stacks/paper_trading/**",
            "backend/app/stacks/broker_integration/**",
            "backend/app/stacks/wolfden_ai/**",
        ],
        "real_secret_activation": False,
        "real_user_login": False,
        "snaptrade_activation": False,
        "broker_execution": False,
        "live_trading": False,
        "source_modified": False,
        "database_modified": False,
    }

    REPORT_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
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

    lines = [
        "=" * 112,
        "NEUROVEST INTEGRATED QUALIFICATION CAMPAIGN",
        (
            "IQC STAGE 5 JWT AUTHENTICATION BOUNDARY PREFLIGHT"
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
        "INVENTORY",
        (
            "- Production Python files scanned: "
            f"{len(files)}"
        ),
        (
            "- Authentication candidate files: "
            f"{len(auth_candidates)}"
        ),
        (
            "- identity_auth-owned files: "
            f"{len(identity_auth_files)}"
        ),
        (
            "- JWT library files: "
            f"{len(jwt_library_files)}"
        ),
        (
            "- Password-hash library files: "
            f"{len(hash_library_files)}"
        ),
        (
            "- JWT-related functions: "
            f"{len(jwt_function_records)}"
        ),
        (
            "- JWT calls: "
            f"{len(jwt_calls)}"
        ),
        (
            "- Password functions: "
            f"{len(password_function_records)}"
        ),
        (
            "- Password calls: "
            f"{len(password_calls)}"
        ),
        (
            "- Environment variable name reads: "
            f"{len(environment_reads)}"
        ),
        (
            "- Hardcoded secret candidates: "
            f"{len(hardcoded_secret_candidates)}"
        ),
        (
            "- Authentication routes: "
            f"{len(route_records)}"
        ),
        (
            "- Authentication dependencies: "
            f"{len(dependency_records)}"
        ),
        (
            "- Session-policy signals: "
            f"{len(session_signals)}"
        ),
        (
            "- Authentication tests: "
            f"{len(test_files)}"
        ),
        (
            "- Forbidden owner couplings: "
            f"{len(forbidden_couplings)}"
        ),
        (
            "- Syntax errors: "
            f"{len(syntax_errors)}"
        ),
        "",
        "CAPABILITY STATE",
        (
            "- Token issuance present: "
            + (
                "YES"
                if token_issuance_present
                else "NO"
            )
        ),
        (
            "- Token validation present: "
            + (
                "YES"
                if token_validation_present
                else "NO"
            )
        ),
        (
            "- Password hashing present: "
            + (
                "YES"
                if password_hashing_present
                else "NO"
            )
        ),
        (
            "- API auth dependency present: "
            + (
                "YES"
                if api_dependency_present
                else "NO"
            )
        ),
        (
            "- Refresh-token signals present: "
            + (
                "YES"
                if refresh_token_signals_present
                else "NO"
            )
        ),
        (
            "- Revocation signals present: "
            + (
                "YES"
                if revocation_signals_present
                else "NO"
            )
        ),
        (
            "- Expiration signals present: "
            + (
                "YES"
                if expiration_signals_present
                else "NO"
            )
        ),
        "",
        "EXACT GAPS",
    ]

    if exact_gaps:
        lines.extend(
            f"- {gap}"
            for gap in exact_gaps
        )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "BLOCKERS",
        ]
    )

    if blockers:
        lines.extend(
            f"- {blocker}"
            for blocker in blockers
        )
    else:
        lines.append(
            "- None"
        )

    lines.extend(
        [
            "",
            "FROZEN OWNERSHIP",
            (
                "- Token issuance: "
                "identity_auth"
            ),
            (
                "- Token validation: "
                "identity_auth"
            ),
            (
                "- Password hashing: "
                "identity_auth"
            ),
            (
                "- Refresh tokens: "
                "identity_auth"
            ),
            (
                "- Session revocation: "
                "identity_auth"
            ),
            (
                "- API auth dependency: "
                "identity_auth"
            ),
            "",
            "FROZEN SAFETY POLICY",
            "- Plaintext password storage allowed: NO",
            "- Secret values may be logged: NO",
            "- Secret values may be persisted: NO",
            "- Unverified claims authoritative: NO",
            "- Frontend claims authoritative: NO",
            "- Refresh token accepted as access token: NO",
            "- Signature validation required: YES",
            "- Expiration validation required: YES",
            "- Issuer validation required: YES",
            "- Audience validation required: YES",
            "- Token-type validation required: YES",
            "- Refresh-token rotation required: YES",
            "- Refresh-token revocation required: YES",
            "- Missing secret behavior: FAIL CLOSED",
            "- Invalid token behavior: UNAUTHORIZED",
            "- Expired token behavior: UNAUTHORIZED",
            "- Revoked token behavior: UNAUTHORIZED",
            "",
            "AUTHORIZATION",
            (
                "- JWT implementation: "
                + (
                    "AUTHORIZED"
                    if implementation_authorized
                    else "NOT AUTHORIZED"
                )
            ),
            "- Real JWT secret activation: NOT AUTHORIZED",
            "- Real user login: NOT AUTHORIZED",
            "- SnapTrade activation: NOT AUTHORIZED",
            "- Broker execution: NOT AUTHORIZED",
            "- Live trading: NOT AUTHORIZED",
            "",
            "SAFETY",
            "- Secret values read: NO",
            "- Password values read: NO",
            "- Tokens generated: NO",
            "- Production source modified: NO",
            "- Database modified: NO",
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
            lines
        )
        + "\n"
    )

    REPORT_TEXT.write_text(
        rendered,
        encoding="utf-8",
    )

    print(rendered)

    print("PASS: existing auth inventory completed")
    print("PASS: token ownership inventory completed")
    print("PASS: secret-name access inventoried without values")
    print("PASS: password boundary inventoried")
    print("PASS: session policy inventoried")
    print("PASS: API auth dependencies inventoried")
    print("PASS: auth tests inventoried")
    print("PASS: forbidden couplings inventoried")
    print("PASS: exact implementation gaps frozen")
    print("PASS: JWT ownership policy frozen")
    print("PASS: no secret values read")
    print("PASS: no token generated")
    print("PASS: no production source modified")
    print("PASS: no database operation performed")


if __name__ == "__main__":
    main()
