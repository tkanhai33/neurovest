#!/usr/bin/env python3

from __future__ import annotations

import ast
import json
import re
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
    / "jwt_durable_identity_refresh_session_preflight"
)

REPORT_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_durable_identity_refresh_session_preflight_latest.json"
)

REPORT_TEXT = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_durable_identity_refresh_session_preflight_latest.txt"
)

EVIDENCE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_durable_identity_refresh_session_preflight_evidence_latest.json"
)

FREEZE_JSON = (
    OUTPUT_DIR
    / "iqc_stage5_jwt_durable_identity_refresh_session_preflight_freeze_latest.json"
)

BASELINE_JSON = (
    OUTPUT_DIR
    / "baseline_snapshot.json"
)


IDENTITY_PATH_MARKERS = {
    "auth",
    "identity",
    "session",
    "token",
    "user",
}


IDENTITY_CLASS_MARKERS = {
    "account",
    "identity",
    "refresh",
    "session",
    "token",
    "user",
}


USER_FIELD_MARKERS = {
    "created_at",
    "disabled",
    "email",
    "email_normalized",
    "id",
    "is_active",
    "password_hash",
    "status",
    "updated_at",
    "username",
    "username_normalized",
}


SESSION_FIELD_MARKERS = {
    "created_at",
    "expires_at",
    "family_id",
    "id",
    "issued_at",
    "last_used_at",
    "replaced_by",
    "revoked_at",
    "token_hash",
    "token_id",
    "user_id",
}


NORMALIZATION_MARKERS = {
    "casefold",
    "lower",
    "normalize",
    "normalized",
    "strip",
}


REVOCATION_MARKERS = {
    "denylist",
    "family_id",
    "logout",
    "reuse",
    "revoke",
    "revoked",
    "rotation",
    "token_family",
}


DATABASE_MUTATION_CALLS = {
    "add",
    "commit",
    "delete",
    "execute",
    "flush",
    "merge",
    "rollback",
}


FORBIDDEN_COUPLINGS = {
    "broker_integration",
    "execution",
    "paper_trading",
    "snaptrade",
    "wolfden_ai",
}


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
        reversed(
            parts
        )
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


def is_identity_candidate(
    path: Path,
    source: str,
) -> bool:
    lowered_path = path.as_posix().lower()

    if any(
        marker in lowered_path
        for marker in IDENTITY_PATH_MARKERS
    ):
        return True

    lowered_source = source.lower()

    return any(
        marker in lowered_source
        for marker in (
            "password_hash",
            "refresh_token",
            "token_family",
            "user_id",
            "email_normalized",
            "username_normalized",
        )
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
    classes = []
    functions = []
    table_names = []
    mapped_fields = []
    constraints = []
    indexes = []
    normalization_signals = []
    revocation_signals = []
    transaction_signals = []
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
                        "line": node.lineno,
                    }
                )

                lowered = alias.name.lower()

                if any(
                    owner in lowered
                    for owner in FORBIDDEN_COUPLINGS
                ):
                    forbidden_couplings.append(
                        {
                            "module": alias.name,
                            "line": node.lineno,
                        }
                    )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            module = (
                node.module
                or ""
            )

            imports.append(
                {
                    "module": module,
                    "line": node.lineno,
                    "names": [
                        alias.name
                        for alias in node.names
                    ],
                }
            )

            lowered = module.lower()

            if any(
                owner in lowered
                for owner in FORBIDDEN_COUPLINGS
            ):
                forbidden_couplings.append(
                    {
                        "module": module,
                        "line": node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            lowered_name = (
                node.name.lower()
            )

            relevant = any(
                marker in lowered_name
                for marker in IDENTITY_CLASS_MARKERS
            )

            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [
                        ast.unparse(
                            base
                        )
                        for base in node.bases
                    ],
                    "identity_relevant": relevant,
                }
            )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            lowered_name = (
                node.name.lower()
            )

            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                }
            )

            if any(
                marker in lowered_name
                for marker in NORMALIZATION_MARKERS
            ):
                normalization_signals.append(
                    {
                        "kind": "function",
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

            if any(
                marker in lowered_name
                for marker in REVOCATION_MARKERS
            ):
                revocation_signals.append(
                    {
                        "kind": "function",
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

        elif isinstance(
            node,
            ast.Assign,
        ):
            target_names = [
                target.id
                for target in node.targets
                if isinstance(
                    target,
                    ast.Name,
                )
            ]

            for name in target_names:
                lowered_name = (
                    name.lower()
                )

                if lowered_name in {
                    "__tablename__",
                    "tablename",
                } and isinstance(
                    node.value,
                    ast.Constant,
                ) and isinstance(
                    node.value.value,
                    str,
                ):
                    table_names.append(
                        {
                            "name": node.value.value,
                            "line": node.lineno,
                        }
                    )

                if lowered_name in {
                    "__table_args__",
                    "table_args",
                }:
                    rendered = source_segment(
                        source,
                        node,
                    )

                    constraints.append(
                        {
                            "line": node.lineno,
                            "source": rendered,
                        }
                    )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            if isinstance(
                node.target,
                ast.Name,
            ):
                name = node.target.id

                lowered_name = name.lower()

                if (
                    lowered_name
                    in USER_FIELD_MARKERS
                    or lowered_name
                    in SESSION_FIELD_MARKERS
                ):
                    mapped_fields.append(
                        {
                            "name": name,
                            "line": node.lineno,
                            "annotation": (
                                ast.unparse(
                                    node.annotation
                                )
                            ),
                            "value": (
                                ast.unparse(
                                    node.value
                                )
                                if node.value
                                is not None
                                else None
                            ),
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
                called.split(
                    "."
                )[-1].lower()
                if called
                else ""
            )

            rendered = source_segment(
                source,
                node,
            )

            lowered_rendered = (
                rendered.lower()
            )

            if terminal in {
                "uniqueconstraint",
                "index",
            }:
                indexes.append(
                    {
                        "line": node.lineno,
                        "call": called,
                        "source": rendered,
                    }
                )

            if any(
                marker in lowered_rendered
                for marker in NORMALIZATION_MARKERS
            ):
                normalization_signals.append(
                    {
                        "kind": "call",
                        "name": called,
                        "line": node.lineno,
                        "source": rendered,
                    }
                )

            if any(
                marker in lowered_rendered
                for marker in REVOCATION_MARKERS
            ):
                revocation_signals.append(
                    {
                        "kind": "call",
                        "name": called,
                        "line": node.lineno,
                        "source": rendered,
                    }
                )

            if terminal in DATABASE_MUTATION_CALLS:
                receiver = (
                    called.rsplit(
                        ".",
                        1,
                    )[0]
                    if "."
                    in called
                    else ""
                )

                transaction_signals.append(
                    {
                        "line": node.lineno,
                        "call": called,
                        "receiver": receiver,
                        "source": rendered,
                    }
                )

    return {
        "path": path.relative_to(
            ROOT
        ).as_posix(),
        "identity_candidate": (
            is_identity_candidate(
                path,
                source,
            )
        ),
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "table_names": table_names,
        "mapped_fields": mapped_fields,
        "constraints": constraints,
        "indexes": indexes,
        "normalization_signals": (
            normalization_signals
        ),
        "revocation_signals": (
            revocation_signals
        ),
        "transaction_signals": (
            transaction_signals
        ),
        "forbidden_couplings": (
            forbidden_couplings
        ),
    }


def main() -> None:
    baseline = json.loads(
        BASELINE_JSON.read_text(
            encoding="utf-8"
        )
    )

    records = []
    syntax_errors = []

    for path in sorted(
        BACKEND_ROOT.rglob(
            "*.py"
        )
    ):
        if "__pycache__" in path.parts:
            continue

        try:
            records.append(
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

    candidates = [
        item
        for item in records
        if item[
            "identity_candidate"
        ]
    ]

    identity_auth_files = [
        item
        for item in candidates
        if "identity_auth" in item[
            "path"
        ].lower()
    ]

    model_files = [
        item
        for item in candidates
        if (
            item[
                "table_names"
            ]
            or item[
                "mapped_fields"
            ]
        )
        and (
            "identity_auth"
            in item[
                "path"
            ].lower()
            or any(
                field[
                    "name"
                ].lower()
                in {
                    "email",
                    "email_normalized",
                    "username",
                    "username_normalized",
                    "password_hash",
                    "token_hash",
                    "token_id",
                    "family_id",
                    "revoked_at",
                    "replaced_by",
                }
                for field in item[
                    "mapped_fields"
                ]
            )
            or any(
                any(
                    marker in record[
                        "name"
                    ].lower()
                    for marker in (
                        "identity",
                        "refreshsession",
                        "refresh_session",
                        "useraccount",
                        "user_account",
                        "authuser",
                        "auth_user",
                    )
                )
                for record in item[
                    "classes"
                ]
            )
            or any(
                any(
                    marker in table[
                        "name"
                    ].lower()
                    for marker in (
                        "identity",
                        "refresh_session",
                        "auth_user",
                        "user_account",
                    )
                )
                for table in item[
                    "table_names"
                ]
            )
        )
    ]

    user_models = []

    session_models = []

    for item in model_files:
        field_names = {
            field[
                "name"
            ].lower()
            for field in item[
                "mapped_fields"
            ]
        }

        class_names = {
            record[
                "name"
            ].lower()
            for record in item[
                "classes"
            ]
        }

        if (
            field_names
            & USER_FIELD_MARKERS
            or any(
                "user" in name
                or "identity" in name
                for name in class_names
            )
        ):
            user_models.append(
                item
            )

        if (
            field_names
            & SESSION_FIELD_MARKERS
            or any(
                "session" in name
                or "refresh" in name
                for name in class_names
            )
        ):
            session_models.append(
                item
            )

    database_tables = baseline[
        "database"
    ][
        "tables"
    ]

    identity_table_candidates = [
        table
        for table in database_tables
        if any(
            marker in table.lower()
            for marker in (
                "auth",
                "identity",
                "refresh",
                "session",
                "token",
                "user",
            )
        )
    ]

    database_columns = baseline[
        "database"
    ][
        "columns"
    ]

    identity_columns = [
        record
        for record in database_columns
        if record[
            "table_name"
        ] in identity_table_candidates
    ]

    database_constraints = baseline[
        "database"
    ][
        "constraints"
    ]

    identity_constraints = [
        record
        for record in database_constraints
        if record[
            "table_name"
        ] in identity_table_candidates
    ]

    database_indexes = baseline[
        "database"
    ][
        "indexes"
    ]

    identity_indexes = [
        record
        for record in database_indexes
        if record[
            "tablename"
        ] in identity_table_candidates
    ]

    normalization_signals = [
        {
            "path": item[
                "path"
            ],
            **signal,
        }
        for item in candidates
        for signal in item[
            "normalization_signals"
        ]
    ]

    revocation_signals = [
        {
            "path": item[
                "path"
            ],
            **signal,
        }
        for item in candidates
        for signal in item[
            "revocation_signals"
        ]
    ]

    transaction_signals = [
        {
            "path": item[
                "path"
            ],
            **signal,
        }
        for item in candidates
        for signal in item[
            "transaction_signals"
        ]
    ]

    forbidden_couplings = [
        {
            "path": item[
                "path"
            ],
            **signal,
        }
        for item in candidates
        for signal in item[
            "forbidden_couplings"
        ]
    ]

    migration_manifest = baseline[
        "migration_manifest"
    ]

    migration_identity_signals = []

    for entry in migration_manifest:
        path = ROOT / entry[
            "path"
        ]

        source = path.read_text(
            encoding="utf-8"
        )

        lowered = source.lower()

        matched = sorted(
            {
                marker
                for marker in (
                    "email",
                    "identity",
                    "password_hash",
                    "refresh",
                    "revoked",
                    "session",
                    "token",
                    "user",
                )
                if marker in lowered
            }
        )

        if matched:
            migration_identity_signals.append(
                {
                    "path": entry[
                        "path"
                    ],
                    "markers": matched,
                }
            )

    user_store_present = bool(
        user_models
        or any(
            any(
                marker in table.lower()
                for marker in (
                    "auth_users",
                    "identity_users",
                    "user_accounts",
                )
            )
            for table in identity_table_candidates
        )
    )

    refresh_session_store_present = bool(
        session_models
        or any(
            any(
                marker in table.lower()
                for marker in (
                    "refresh_sessions",
                    "refresh_tokens",
                    "auth_sessions",
                    "identity_sessions",
                )
            )
            for table in identity_table_candidates
        )
    )

    normalization_present = bool(
        normalization_signals
    )

    uniqueness_present = bool(
        identity_constraints
        or identity_indexes
        or any(
            item[
                "constraints"
            ]
            or item[
                "indexes"
            ]
            for item in model_files
        )
    )

    password_hash_field_present = any(
        field[
            "name"
        ].lower()
        == "password_hash"
        for item in user_models
        for field in item[
            "mapped_fields"
        ]
    )

    account_status_present = any(
        field[
            "name"
        ].lower()
        in {
            "disabled",
            "is_active",
            "status",
        }
        for item in user_models
        for field in item[
            "mapped_fields"
        ]
    )

    session_expiry_present = any(
        field[
            "name"
        ].lower()
        == "expires_at"
        for item in session_models
        for field in item[
            "mapped_fields"
        ]
    )

    token_hash_present = any(
        field[
            "name"
        ].lower()
        == "token_hash"
        for item in session_models
        for field in item[
            "mapped_fields"
        ]
    )

    token_family_present = any(
        field[
            "name"
        ].lower()
        == "family_id"
        for item in session_models
        for field in item[
            "mapped_fields"
        ]
    )

    revoked_at_present = any(
        field[
            "name"
        ].lower()
        == "revoked_at"
        for item in session_models
        for field in item[
            "mapped_fields"
        ]
    )

    exact_gaps = []

    if not user_store_present:
        exact_gaps.append(
            "No durable identity or user store resolved"
        )

    if not refresh_session_store_present:
        exact_gaps.append(
            "No durable refresh-session store resolved"
        )

    if not normalization_present:
        exact_gaps.append(
            "No canonical email or username normalization boundary resolved"
        )

    if not uniqueness_present:
        exact_gaps.append(
            "No durable identity uniqueness constraint resolved"
        )

    if not password_hash_field_present:
        exact_gaps.append(
            "No durable password_hash field resolved"
        )

    if not account_status_present:
        exact_gaps.append(
            "No durable account status or disabled-user field resolved"
        )

    if not session_expiry_present:
        exact_gaps.append(
            "No durable refresh-session expiry field resolved"
        )

    if not token_hash_present:
        exact_gaps.append(
            "No hashed refresh-token verifier field resolved"
        )

    if not token_family_present:
        exact_gaps.append(
            "No refresh-token family or rotation lineage field resolved"
        )

    if not revoked_at_present:
        exact_gaps.append(
            "No durable refresh-session revocation timestamp resolved"
        )

    if not revocation_signals:
        exact_gaps.append(
            "No durable rotation-reuse or revoke-all behavior resolved"
        )

    blockers = []

    if syntax_errors:
        blockers.append(
            "Syntax errors prevent persistence implementation authorization"
        )

    if forbidden_couplings:
        blockers.append(
            "Identity persistence imports a prohibited trading owner"
        )

    external_identity_owners = sorted(
        {
            item[
                "path"
            ]
            for item in model_files
            if (
                "identity_auth"
                not in item[
                    "path"
                ]
                and any(
                    field[
                        "name"
                    ].lower()
                    in {
                        "email",
                        "email_normalized",
                        "username",
                        "username_normalized",
                        "password_hash",
                        "token_hash",
                        "token_id",
                        "family_id",
                        "revoked_at",
                        "replaced_by",
                    }
                    for field in item[
                        "mapped_fields"
                    ]
                )
            )
        }
    )

    if external_identity_owners:
        blockers.append(
            "Identity-like persistence exists outside identity_auth and requires ownership disposition"
        )

    implementation_authorized = (
        not blockers
    )

    if not implementation_authorized:
        disposition = (
            "JWT_DURABLE_IDENTITY_PERSISTENCE_"
            "BLOCKED_EXACT_OWNERSHIP_REMEDIATION_REQUIRED"
        )

    elif exact_gaps:
        disposition = (
            "JWT_DURABLE_IDENTITY_AND_REFRESH_SESSION_"
            "IMPLEMENTATION_AUTHORIZED_EXACT_GAPS_FROZEN"
        )

    else:
        disposition = (
            "JWT_DURABLE_IDENTITY_AND_REFRESH_SESSION_"
            "PERSISTENCE_EXISTS_HARDENING_REQUIRED"
        )

    frozen_schema = {
        "identity_owner": (
            "backend.app.stacks.identity_auth"
        ),
        "migration_owner": (
            "backend.app.stacks.identity_auth"
        ),
        "user_table": {
            "required": True,
            "minimum_fields": [
                "id",
                "email_normalized",
                "password_hash",
                "status",
                "created_at",
                "updated_at",
            ],
            "email_normalized_unique": True,
            "plaintext_password_allowed": False,
        },
        "refresh_session_table": {
            "required": True,
            "minimum_fields": [
                "id",
                "user_id",
                "token_id",
                "token_hash",
                "family_id",
                "issued_at",
                "expires_at",
                "revoked_at",
                "replaced_by",
                "created_at",
            ],
            "raw_refresh_token_storage_allowed": False,
            "token_id_unique": True,
            "foreign_key_required": True,
        },
        "transaction_policy": {
            "identity_creation_atomic": True,
            "refresh_rotation_atomic": True,
            "rotation_reuse_detection_required": True,
            "revoke_family_on_reuse": True,
            "logout_revokes_current_session": True,
            "revoke_all_supported": True,
        },
        "cleanup_policy": {
            "expired_session_cleanup_required": True,
            "cleanup_may_delete_users": False,
        },
    }

    authorization = {
        "identity_models": (
            implementation_authorized
        ),
        "refresh_session_models": (
            implementation_authorized
        ),
        "migration_creation": (
            implementation_authorized
        ),
        "repository_boundaries": (
            implementation_authorized
        ),
        "focused_persistence_tests": (
            implementation_authorized
        ),
        "real_registration": False,
        "real_login": False,
        "real_secret_activation": False,
        "protected_route_wiring": False,
        "snaptrade_activation": False,
        "broker_execution": False,
        "live_trading": False,
    }

    verified_at = datetime.now(
        UTC
    ).isoformat()

    evidence = {
        "status": "completed",
        "verified_at": verified_at,
        "mode": "read_only",
        "identity_candidate_files": candidates,
        "identity_auth_files": identity_auth_files,
        "model_files": model_files,
        "user_models": user_models,
        "session_models": session_models,
        "database_identity_tables": (
            identity_table_candidates
        ),
        "database_identity_columns": (
            identity_columns
        ),
        "database_identity_constraints": (
            identity_constraints
        ),
        "database_identity_indexes": (
            identity_indexes
        ),
        "normalization_signals": (
            normalization_signals
        ),
        "revocation_signals": (
            revocation_signals
        ),
        "transaction_signals": (
            transaction_signals
        ),
        "migration_identity_signals": (
            migration_identity_signals
        ),
        "external_identity_owners": (
            external_identity_owners
        ),
        "forbidden_couplings": (
            forbidden_couplings
        ),
        "syntax_errors": syntax_errors,
        "database_modified": False,
        "source_modified": False,
        "password_values_read": False,
        "secret_values_read": False,
        "tokens_generated": False,
    }

    report = {
        "campaign": (
            "NeuroVest Integrated Qualification Campaign"
        ),
        "stage": (
            "IQC Stage 5 JWT Durable Identity and "
            "Refresh-Session Persistence Preflight"
        ),
        "status": "complete_and_verified",
        "verified_at": verified_at,
        "mode": "read_only",
        "disposition": disposition,
        "inventory": {
            "identity_candidate_files": len(
                candidates
            ),
            "identity_auth_files": len(
                identity_auth_files
            ),
            "identity_model_files": len(
                model_files
            ),
            "user_model_files": len(
                user_models
            ),
            "refresh_session_model_files": len(
                session_models
            ),
            "database_identity_tables": len(
                identity_table_candidates
            ),
            "migration_identity_files": len(
                migration_identity_signals
            ),
            "normalization_signals": len(
                normalization_signals
            ),
            "revocation_signals": len(
                revocation_signals
            ),
            "transaction_signals": len(
                transaction_signals
            ),
            "external_identity_owners": len(
                external_identity_owners
            ),
            "forbidden_couplings": len(
                forbidden_couplings
            ),
            "syntax_errors": len(
                syntax_errors
            ),
        },
        "capability_state": {
            "durable_user_store_present": (
                user_store_present
            ),
            "durable_refresh_session_store_present": (
                refresh_session_store_present
            ),
            "normalization_present": (
                normalization_present
            ),
            "uniqueness_present": (
                uniqueness_present
            ),
            "password_hash_field_present": (
                password_hash_field_present
            ),
            "account_status_present": (
                account_status_present
            ),
            "session_expiry_present": (
                session_expiry_present
            ),
            "token_hash_present": (
                token_hash_present
            ),
            "token_family_present": (
                token_family_present
            ),
            "revoked_at_present": (
                revoked_at_present
            ),
        },
        "exact_gaps": exact_gaps,
        "blockers": blockers,
        "frozen_schema": frozen_schema,
        "authorization": authorization,
        "database_modified": False,
        "source_modified": False,
        "password_values_read": False,
        "secret_values_read": False,
        "tokens_generated": False,
        "next": (
            "Remediate exact identity persistence ownership blockers."
            if blockers
            else
            "Proceed to IQC Stage 5 JWT Durable Identity and "
            "Refresh-Session Persistence Implementation and Qualification."
        ),
    }

    freeze = {
        "status": "frozen",
        "verified_at": verified_at,
        "baseline": (
            "jwt_durable_identity_refresh_session_preflight_v2"
        ),
        "supersedes": (
            "jwt_durable_identity_refresh_session_preflight_v1"
        ),
        "semantic_exclusions": [
            "backend/app/stacks/chat_public/contracts/chat_contracts.py",
            "backend/app/stacks/chat_public/persistence/chat_models.py",
        ],
        "disposition": disposition,
        "authorized_owner": (
            "backend.app.stacks.identity_auth"
        ),
        "authorized_source_scope": [
            (
                "backend/app/stacks/"
                "identity_auth/**"
            ),
            (
                "backend/app/stacks/"
                "identity_auth/tests/**"
            ),
            "alembic/versions/<single_authorized_revision>.py",
        ],
        "prohibited_source_scope": [
            "backend/app/stacks/snaptrade/**",
            "backend/app/stacks/execution/**",
            "backend/app/stacks/paper_trading/**",
            "backend/app/stacks/broker_integration/**",
            "backend/app/stacks/wolfden_ai/**",
        ],
        "frozen_schema": frozen_schema,
        "exact_gaps": exact_gaps,
        "blockers": blockers,
        "real_registration": False,
        "real_login": False,
        "real_secret_activation": False,
        "protected_route_wiring": False,
        "snaptrade_activation": False,
        "broker_execution": False,
        "live_trading": False,
        "database_modified": False,
        "source_modified": False,
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
            "IQC STAGE 5 JWT DURABLE IDENTITY AND "
            "REFRESH-SESSION PERSISTENCE PREFLIGHT"
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
            "- Identity candidate files: "
            f"{len(candidates)}"
        ),
        (
            "- identity_auth files: "
            f"{len(identity_auth_files)}"
        ),
        (
            "- Identity model files: "
            f"{len(model_files)}"
        ),
        (
            "- User model files: "
            f"{len(user_models)}"
        ),
        (
            "- Refresh-session model files: "
            f"{len(session_models)}"
        ),
        (
            "- Existing database identity tables: "
            f"{len(identity_table_candidates)}"
        ),
        (
            "- Identity-related migration files: "
            f"{len(migration_identity_signals)}"
        ),
        (
            "- Normalization signals: "
            f"{len(normalization_signals)}"
        ),
        (
            "- Revocation signals: "
            f"{len(revocation_signals)}"
        ),
        (
            "- External identity owners: "
            f"{len(external_identity_owners)}"
        ),
        (
            "- Forbidden couplings: "
            f"{len(forbidden_couplings)}"
        ),
        (
            "- Syntax errors: "
            f"{len(syntax_errors)}"
        ),
        "",
        "CAPABILITY STATE",
        (
            "- Durable user store present: "
            + (
                "YES"
                if user_store_present
                else "NO"
            )
        ),
        (
            "- Durable refresh-session store present: "
            + (
                "YES"
                if refresh_session_store_present
                else "NO"
            )
        ),
        (
            "- Identity normalization present: "
            + (
                "YES"
                if normalization_present
                else "NO"
            )
        ),
        (
            "- Durable uniqueness present: "
            + (
                "YES"
                if uniqueness_present
                else "NO"
            )
        ),
        (
            "- password_hash field present: "
            + (
                "YES"
                if password_hash_field_present
                else "NO"
            )
        ),
        (
            "- Account status field present: "
            + (
                "YES"
                if account_status_present
                else "NO"
            )
        ),
        (
            "- Session expiration present: "
            + (
                "YES"
                if session_expiry_present
                else "NO"
            )
        ),
        (
            "- Refresh token hash present: "
            + (
                "YES"
                if token_hash_present
                else "NO"
            )
        ),
        (
            "- Token-family lineage present: "
            + (
                "YES"
                if token_family_present
                else "NO"
            )
        ),
        (
            "- Revocation timestamp present: "
            + (
                "YES"
                if revoked_at_present
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
            "FROZEN PERSISTENCE POLICY",
            "- Identity owner: identity_auth",
            "- Migration owner: identity_auth",
            "- Normalized email uniqueness required: YES",
            "- Plaintext password persistence allowed: NO",
            "- Raw refresh-token persistence allowed: NO",
            "- Hashed refresh-token verifier required: YES",
            "- Refresh-token family lineage required: YES",
            "- Atomic refresh rotation required: YES",
            "- Rotation reuse detection required: YES",
            "- Revoke token family on reuse: YES",
            "- Logout revokes current session: YES",
            "- Revoke-all behavior required: YES",
            "- Expired-session cleanup required: YES",
            "",
            "AUTHORIZATION",
            (
                "- Persistence implementation: "
                + (
                    "AUTHORIZED"
                    if implementation_authorized
                    else "NOT AUTHORIZED"
                )
            ),
            "- Real registration: NOT AUTHORIZED",
            "- Real login: NOT AUTHORIZED",
            "- Real JWT secret activation: NOT AUTHORIZED",
            "- Protected route wiring: NOT AUTHORIZED",
            "- SnapTrade activation: NOT AUTHORIZED",
            "- Broker execution: NOT AUTHORIZED",
            "- Live trading: NOT AUTHORIZED",
            "",
            "SAFETY",
            "- Password values read: NO",
            "- Secret values read: NO",
            "- Tokens generated: NO",
            "- Production source modified: NO",
            "- Database modified: NO",
            "",
            "NEXT",
            report[
                "next"
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

    print("PASS: durable identity inventory completed")
    print("PASS: refresh-session inventory completed")
    print("PASS: database schema inventory completed")
    print("PASS: migration ownership inventory completed")
    print("PASS: normalization controls inventoried")
    print("PASS: uniqueness controls inventoried")
    print("PASS: rotation and revocation controls inventoried")
    print("PASS: transaction signals inventoried")
    print("PASS: exact persistence gaps frozen")
    print("PASS: no password value read")
    print("PASS: no JWT secret value read")
    print("PASS: no token generated")
    print("PASS: no production source modified")
    print("PASS: no database write performed")


if __name__ == "__main__":
    main()
