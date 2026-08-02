from __future__ import annotations

from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4
import json


ROOT = Path(".").resolve()
GRAPH_DIR = ROOT / "runtime" / "graph_history"
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

SNAPSHOT_FILE = GRAPH_DIR / "current_snapshot.json"
EVENT_FILE = GRAPH_DIR / "events.jsonl"


# Explicitly known architecture ownership only.
# Unknown nodes remain UNASSIGNED rather than being guessed.
NODE_ARCHITECTURE: dict[str, dict[str, str]] = {
    "chat_public": {
        "layer": "L5",
        "stack": "chat_public",
    },
    "repo_memory": {
        "layer": "L2",
        "stack": "memory",
    },
    "research_db": {
        "layer": "L2",
        "stack": "research",
    },
    "market_data": {
        "layer": "L2",
        "stack": "market_data",
    },
    "strategy": {
        "layer": "L2",
        "stack": "strategy",
    },
    "risk": {
        "layer": "L2",
        "stack": "risk",
    },
    "execution": {
        "layer": "L4",
        "stack": "execution",
    },
    "events_broker": {
        "layer": "L3",
        "stack": "events",
    },
    "journal_ledger": {
        "layer": "L2",
        "stack": "journal_ledger",
    },
    "portfolio_accounting": {
        "layer": "L2",
        "stack": "portfolio",
    },
    "portfolio_reconciliation": {
        "layer": "L4",
        "stack": "portfolio",
    },
    "graph_live": {
        "layer": "L5",
        "stack": "admin_control",
    },
}


NODE_ARCHITECTURE.update(
    {
        "frontend_chat": {
            "layer": "L6",
            "stack": "frontend",
        },
        "http_api": {
            "layer": "L5",
            "stack": "api",
        },
        "chat_api": {
            "layer": "L5",
            "stack": "chat_public",
        },
        "graph_api": {
            "layer": "L5",
            "stack": "admin_control",
        },
        "route_authorization": {
            "layer": "L1",
            "stack": "identity_auth",
        },
        "jwt_validation": {
            "layer": "L1",
            "stack": "identity_auth",
        },
        "authenticated_principal": {
            "layer": "L1",
            "stack": "identity_auth",
        },
        "chat_runtime": {
            "layer": "L4",
            "stack": "chat_public",
        },
        "conversation_store": {
            "layer": "L3",
            "stack": "chat_public",
        },
        "intent_classifier": {
            "layer": "L2",
            "stack": "chat_public",
        },
        "context_assembler": {
            "layer": "L2",
            "stack": "chat_public",
        },
        "memory_context": {
            "layer": "L2",
            "stack": "memory",
        },
        "response_validation": {
            "layer": "L3",
            "stack": "chat_public",
        },
        "conversation_persistence": {
            "layer": "L3",
            "stack": "chat_public",
        },
        "postgresql_adapter": {
            "layer": "L0",
            "stack": "db_runtime",
        },
        "ollama_adapter": {
            "layer": "L0",
            "stack": "chat_public",
        },
        "yfinance_adapter": {
            "layer": "L0",
            "stack": "market_data",
        },
    }
)


# Stage 8F approved architecture topology.
#
# Declared nodes and edges describe repository structure only.
# They do not represent runtime activity, increment metrics, or
# create trace records.
NODE_ARCHITECTURE.update(
    {
        # --------------------------------------------------
        # L7 — Qualification, tests, evidence, and freezes
        # --------------------------------------------------
        "iqc_qualification": {
            "layer": "L7",
            "stack": "iqc",
            "component_type": "qualification",
            "source_file": "runtime/iqc",
        },
        "backend_test_suite": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "test_suite",
            "source_file": "backend/app",
        },
        "frontend_typecheck": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "typecheck",
            "source_file": "frontend/tsconfig.json",
        },
        "qualification_evidence": {
            "layer": "L7",
            "stack": "iqc",
            "component_type": "evidence",
            "source_file": "runtime/iqc",
        },
        "freeze_evidence": {
            "layer": "L7",
            "stack": "iqc",
            "component_type": "freeze",
            "source_file": "runtime/iqc",
        },

        # --------------------------------------------------
        # L6 — Frontend workspaces, clients, and proxies
        # --------------------------------------------------
        "dashboard_shell": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace_shell",
            "source_file": (
                "frontend/app/components/layout/"
                "DashboardShell.tsx"
            ),
        },
        "overview_workspace": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace",
            "source_file": (
                "frontend/app/components/workspaces/"
                "OverviewWorkspace.tsx"
            ),
        },
        "market_workspace": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace",
            "source_file": (
                "frontend/app/components/workspaces/"
                "MarketWorkspace.tsx"
            ),
        },
        "graph_workspace": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace",
            "source_file": (
                "frontend/app/components/workspaces/"
                "GraphWorkspacePanel.tsx"
            ),
        },
        "observability_workspace": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace",
            "source_file": (
                "frontend/app/components/workspaces/"
                "ObservabilityWorkspacePanel.tsx"
            ),
        },
        "learning_workspace": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace",
            "source_file": (
                "frontend/app/components/workspaces/"
                "LearningWorkspacePanel.tsx"
            ),
        },
        "neuro_workspace": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "workspace",
            "source_file": (
                "frontend/app/components/workspaces/"
                "NeuroWorkspace.tsx"
            ),
        },
        "floating_chat_widget": {
            "layer": "L6",
            "stack": "frontend",
            "component_type": "client",
            "source_file": (
                "frontend/app/components/chat/"
                "FloatingChatWidget.tsx"
            ),
        },
        "analytics_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/analytics/route.ts"
            ),
        },
        "chat_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/chat/route.ts"
            ),
        },
        "graph_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/graph/live/route.ts"
            ),
        },
        "market_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/market/"
                "live-price/[symbol]/route.ts"
            ),
        },
        "portfolio_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/portfolio/"
                "positions/route.ts"
            ),
        },
        "risk_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/risk/"
                "gate/[symbol]/route.ts"
            ),
        },
        "strategy_proxy": {
            "layer": "L6",
            "stack": "frontend_proxy",
            "component_type": "server_proxy",
            "source_file": (
                "frontend/app/api/v1/strategy/"
                "decision/[symbol]/route.ts"
            ),
        },

        # --------------------------------------------------
        # L5 — API route entry points
        # --------------------------------------------------
        "analytics_api": {
            "layer": "L5",
            "stack": "api",
            "component_type": "api_route",
            "source_file": "backend/app/main.py",
        },
        "market_api": {
            "layer": "L5",
            "stack": "market_data",
            "component_type": "api_route",
            "source_file": "backend/app/main.py",
        },
        "portfolio_api": {
            "layer": "L5",
            "stack": "portfolio",
            "component_type": "api_route",
            "source_file": "backend/app/main.py",
        },
        "risk_api": {
            "layer": "L5",
            "stack": "risk",
            "component_type": "api_route",
            "source_file": "backend/app/main.py",
        },
        "strategy_api": {
            "layer": "L5",
            "stack": "strategy",
            "component_type": "api_route",
            "source_file": "backend/app/main.py",
        },
        "auth_api": {
            "layer": "L5",
            "stack": "identity_auth",
            "component_type": "api_router",
            "source_file": (
                "backend/app/stacks/identity_auth/"
                "api_router.py"
            ),
        },

        # --------------------------------------------------
        # L4 — Runtime orchestration
        # --------------------------------------------------
        "authentication_runtime": {
            "layer": "L4",
            "stack": "identity_auth",
            "component_type": "runtime",
            "source_file": (
                "backend/app/stacks/identity_auth/"
                "runtime_adapter.py"
            ),
        },
        "market_runtime": {
            "layer": "L4",
            "stack": "market_data",
            "component_type": "runtime",
            "source_file": (
                "backend/app/stacks/market_data/"
                "market_data_service.py"
            ),
        },
        "portfolio_runtime": {
            "layer": "L4",
            "stack": "portfolio",
            "component_type": "runtime",
            "source_file": (
                "backend/app/stacks/portfolio/"
                "dashboard_service.py"
            ),
        },
        "risk_runtime": {
            "layer": "L4",
            "stack": "risk",
            "component_type": "runtime",
            "source_file": (
                "backend/app/stacks/risk/"
                "risk_runtime_service.py"
            ),
        },
        "strategy_runtime": {
            "layer": "L4",
            "stack": "strategy",
            "component_type": "runtime",
            "source_file": (
                "backend/app/stacks/strategy/"
                "strategy_service.py"
            ),
        },

        # --------------------------------------------------
        # L3 — Facades and approved service boundaries
        # --------------------------------------------------
        "authentication_facade": {
            "layer": "L3",
            "stack": "identity_auth",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/identity_auth/"
                "api_dependencies.py"
            ),
        },
        "registration_service": {
            "layer": "L3",
            "stack": "identity_auth",
            "component_type": "service",
            "source_file": (
                "backend/app/stacks/identity_auth/"
                "registration_service.py"
            ),
        },
        "login_service": {
            "layer": "L3",
            "stack": "identity_auth",
            "component_type": "service",
            "source_file": (
                "backend/app/stacks/identity_auth/"
                "login_service.py"
            ),
        },
        "session_lifecycle_service": {
            "layer": "L3",
            "stack": "identity_auth",
            "component_type": "service",
            "source_file": (
                "backend/app/stacks/identity_auth/"
                "session_lifecycle_service.py"
            ),
        },
        "chat_facade": {
            "layer": "L3",
            "stack": "chat_public",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/chat_public/"
                "chat_service.py"
            ),
        },
        "conversation_facade": {
            "layer": "L3",
            "stack": "chat_public",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/chat_public/"
                "conversation_service.py"
            ),
        },
        "market_data_facade": {
            "layer": "L3",
            "stack": "market_data",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/market_data/"
                "market_data_service.py"
            ),
        },
        "portfolio_facade": {
            "layer": "L3",
            "stack": "portfolio",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/portfolio/"
                "portfolio_service.py"
            ),
        },
        "risk_facade": {
            "layer": "L3",
            "stack": "risk",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/risk/"
                "risk_service.py"
            ),
        },
        "strategy_facade": {
            "layer": "L3",
            "stack": "strategy",
            "component_type": "service_boundary",
            "source_file": (
                "backend/app/stacks/strategy/"
                "strategy_service.py"
            ),
        },
        "decision_audit_query_facade": {
            "layer": "L3",
            "stack": "journal_ledger",
            "component_type": "facade",
            "source_file": (
                "backend/app/stacks/journal_ledger/"
                "decision_audit_query_facade.py"
            ),
        },
        "snaptrade_readonly_facade": {
            "layer": "L3",
            "stack": "snaptrade",
            "component_type": "readonly_facade",
            "source_file": (
                "backend/app/stacks/snaptrade/facade/"
                "snaptrade_readonly_facade.py"
            ),
        },
        "portfolio_output_result_facade": {
            "layer": "L3",
            "stack": "wolfden_ai",
            "component_type": "facade",
            "source_file": (
                "backend/app/stacks/wolfden_ai/"
                "portfolio_output_result_facade.py"
            ),
        },

        # --------------------------------------------------
        # Additional approved L0 adapters
        # --------------------------------------------------
        "filesystem_adapter": {
            "layer": "L0",
            "stack": "runtime",
            "component_type": "adapter",
            "source_file": "runtime",
        },
    }
)



# Stage 8F historical runtime-node ownership correction.
#
# These nodes already exist in persisted runtime history. This
# assignment supplies architecture ownership only and does not
# create activity, metrics, traces, or synthetic activations.
NODE_ARCHITECTURE.update(
    {
        "external_client": {
            "layer": "L6",
            "stack": "external",
            "component_type": "external_client",
        },
        "chat_public": {
            "layer": "L5",
            "stack": "chat_public",
            "component_type": "api_boundary",
            "source_file": (
                "backend/app/stacks/chat_public/"
                "chat_api.py"
            ),
        },
        "events_broker": {
            "layer": "L4",
            "stack": "events",
            "component_type": "runtime_broker",
            "source_file": (
                "backend/app/stacks/events/"
                "broker.py"
            ),
        },
        "portfolio_reconciliation": {
            "layer": "L2",
            "stack": "portfolio",
            "component_type": "domain_service",
            "source_file": (
                "backend/app/stacks/portfolio/"
                "reconciliation.py"
            ),
        },
        "repo_memory": {
            "layer": "L2",
            "stack": "memory",
            "component_type": "domain_memory",
            "source_file": (
                "backend/app/stacks/chat_public/"
                "context_loader.py"
            ),
        },
        "research_db": {
            "layer": "L0",
            "stack": "research",
            "component_type": "persistence_adapter",
            "source_file": (
                "backend/app/stacks/chat_public/"
                "context_loader.py"
            ),
        },
    }
)


DECLARED_GRAPH_EDGES: tuple[
    tuple[
        str,
        str,
        str,
    ],
    ...,
] = (
    # L7 qualification relationships
    (
        "backend_test_suite",
        "iqc_qualification",
        "qualifies",
    ),
    (
        "frontend_typecheck",
        "iqc_qualification",
        "qualifies",
    ),
    (
        "iqc_qualification",
        "qualification_evidence",
        "produces",
    ),
    (
        "qualification_evidence",
        "freeze_evidence",
        "freezes",
    ),

    # L6 workspace and proxy entry paths
    (
        "dashboard_shell",
        "overview_workspace",
        "renders",
    ),
    (
        "dashboard_shell",
        "market_workspace",
        "renders",
    ),
    (
        "dashboard_shell",
        "graph_workspace",
        "renders",
    ),
    (
        "dashboard_shell",
        "observability_workspace",
        "renders",
    ),
    (
        "dashboard_shell",
        "learning_workspace",
        "renders",
    ),
    (
        "dashboard_shell",
        "neuro_workspace",
        "renders",
    ),
    (
        "floating_chat_widget",
        "chat_proxy",
        "requests",
    ),
    (
        "neuro_workspace",
        "chat_proxy",
        "requests",
    ),
    (
        "overview_workspace",
        "analytics_proxy",
        "requests",
    ),
    (
        "overview_workspace",
        "portfolio_proxy",
        "requests",
    ),
    (
        "market_workspace",
        "market_proxy",
        "requests",
    ),
    (
        "market_workspace",
        "strategy_proxy",
        "requests",
    ),
    (
        "market_workspace",
        "risk_proxy",
        "requests",
    ),
    (
        "graph_workspace",
        "graph_proxy",
        "requests",
    ),
    (
        "observability_workspace",
        "graph_proxy",
        "requests",
    ),

    # Frontend proxies to L5 APIs
    (
        "analytics_proxy",
        "analytics_api",
        "forwards",
    ),
    (
        "chat_proxy",
        "chat_api",
        "forwards",
    ),
    (
        "graph_proxy",
        "graph_api",
        "forwards",
    ),
    (
        "market_proxy",
        "market_api",
        "forwards",
    ),
    (
        "portfolio_proxy",
        "portfolio_api",
        "forwards",
    ),
    (
        "risk_proxy",
        "risk_api",
        "forwards",
    ),
    (
        "strategy_proxy",
        "strategy_api",
        "forwards",
    ),

    # Shared HTTP and security boundary
    (
        "http_api",
        "route_authorization",
        "authorizes",
    ),
    (
        "route_authorization",
        "jwt_validation",
        "validates",
    ),
    (
        "jwt_validation",
        "authenticated_principal",
        "resolves",
    ),

    # L5 API to runtime/facade boundaries
    (
        "auth_api",
        "authentication_runtime",
        "dispatches",
    ),
    (
        "authentication_runtime",
        "authentication_facade",
        "binds",
    ),
    (
        "authentication_facade",
        "registration_service",
        "calls",
    ),
    (
        "authentication_facade",
        "login_service",
        "calls",
    ),
    (
        "authentication_facade",
        "session_lifecycle_service",
        "calls",
    ),

    (
        "chat_api",
        "chat_runtime",
        "dispatches",
    ),
    (
        "chat_runtime",
        "chat_facade",
        "calls",
    ),
    (
        "chat_facade",
        "conversation_facade",
        "calls",
    ),
    (
        "conversation_facade",
        "conversation_store",
        "uses",
    ),
    (
        "conversation_store",
        "postgresql_adapter",
        "persists",
    ),
    (
        "chat_runtime",
        "context_assembler",
        "assembles",
    ),
    (
        "context_assembler",
        "memory_context",
        "reads",
    ),
    (
        "chat_runtime",
        "intent_classifier",
        "classifies",
    ),
    (
        "intent_classifier",
        "ollama_adapter",
        "invokes",
    ),
    (
        "ollama_adapter",
        "response_validation",
        "returns",
    ),
    (
        "response_validation",
        "conversation_persistence",
        "persists",
    ),

    (
        "market_api",
        "market_runtime",
        "dispatches",
    ),
    (
        "market_runtime",
        "market_data_facade",
        "calls",
    ),
    (
        "market_data_facade",
        "market_data",
        "reads",
    ),
    (
        "market_data",
        "yfinance_adapter",
        "queries",
    ),

    (
        "portfolio_api",
        "portfolio_runtime",
        "dispatches",
    ),
    (
        "portfolio_runtime",
        "portfolio_facade",
        "calls",
    ),
    (
        "portfolio_facade",
        "portfolio_accounting",
        "reads",
    ),
    (
        "portfolio_accounting",
        "postgresql_adapter",
        "queries",
    ),

    (
        "strategy_api",
        "strategy_runtime",
        "dispatches",
    ),
    (
        "strategy_runtime",
        "strategy_facade",
        "calls",
    ),
    (
        "strategy_facade",
        "strategy",
        "evaluates",
    ),
    (
        "strategy",
        "decision_audit_query_facade",
        "audits",
    ),
    (
        "decision_audit_query_facade",
        "journal_ledger",
        "reads",
    ),

    (
        "risk_api",
        "risk_runtime",
        "dispatches",
    ),
    (
        "risk_runtime",
        "risk_facade",
        "calls",
    ),
    (
        "risk_facade",
        "risk",
        "evaluates",
    ),
    (
        "risk",
        "decision_audit_query_facade",
        "reads",
    ),

    # Existing runtime-domain relationships
    (
        "events_broker",
        "chat_runtime",
        "routes",
    ),
    (
        "events_broker",
        "strategy_runtime",
        "routes",
    ),
    (
        "portfolio_reconciliation",
        "portfolio_facade",
        "calls",
    ),
    (
        "execution",
        "portfolio_output_result_facade",
        "reports",
    ),
    (
        "portfolio_output_result_facade",
        "journal_ledger",
        "records",
    ),
    (
        "snaptrade_readonly_facade",
        "portfolio_facade",
        "provides_readonly_data",
    ),
)


def now() -> str:
    return datetime.now(UTC).isoformat()


def new_trace_id() -> str:
    return f"trace-{uuid4().hex}"


_SUCCESS_STATES = {
    "ok",
    "ready",
    "active",
    "completed",
    "complete",
    "executed",
    "success",
    "allowed",
    "authenticated",
}

_FAILURE_STATES = {
    "error",
    "failed",
    "failure",
    "blocked",
    "rejected",
    "unauthorized",
    "forbidden",
    "timeout",
    "unavailable",
}


def optional_float(
    value: Any,
) -> float | None:
    if value is None:
        return None

    try:
        normalized = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ):
        return None

    if normalized < 0:
        return None

    return normalized


def optional_int(
    value: Any,
) -> int | None:
    if value is None:
        return None

    try:
        normalized = int(
            value
        )
    except (
        TypeError,
        ValueError,
    ):
        return None

    if normalized < 0:
        return None

    return normalized


def percentile_95(
    values: list[float],
) -> float | None:
    if not values:
        return None

    ordered = sorted(
        values
    )

    index = max(
        0,
        min(
            len(
                ordered
            ) - 1,
            int(
                round(
                    0.95
                    * (
                        len(
                            ordered
                        )
                        - 1
                    )
                )
            ),
        ),
    )

    return round(
        ordered[
            index
        ],
        3,
    )


def update_metric_contract(
    meta: dict[str, Any],
    *,
    status: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(
        meta
    )

    request_count = int(
        normalized.get(
            "request_count",
            normalized.get(
                "event_count",
                0,
            ),
        )
    )

    normalized[
        "request_count"
    ] = request_count

    success_count = int(
        normalized.get(
            "success_count",
            0,
        )
    )

    failure_count = int(
        normalized.get(
            "failure_count",
            0,
        )
    )

    status_lower = status.strip().lower()

    explicit_success = payload.get(
        "success"
    )

    if explicit_success is True:
        success_count += 1
    elif explicit_success is False:
        failure_count += 1
    elif status_lower in _SUCCESS_STATES:
        success_count += 1
    elif status_lower in _FAILURE_STATES:
        failure_count += 1

    normalized[
        "success_count"
    ] = success_count

    normalized[
        "failure_count"
    ] = failure_count

    http_status = optional_int(
        payload.get(
            "http_status",
            payload.get(
                "status_code",
            ),
        )
    )

    if http_status is not None:
        normalized[
            "last_http_status"
        ] = http_status

        if http_status == 401:
            normalized[
                "unauthorized_count"
            ] = int(
                normalized.get(
                    "unauthorized_count",
                    0,
                )
            ) + 1

        if http_status == 403:
            normalized[
                "forbidden_count"
            ] = int(
                normalized.get(
                    "forbidden_count",
                    0,
                )
            ) + 1

        if http_status >= 400:
            normalized[
                "http_error_count"
            ] = int(
                normalized.get(
                    "http_error_count",
                    0,
                )
            ) + 1

    latency = optional_float(
        payload.get(
            "latency_ms",
            payload.get(
                "duration_ms",
            ),
        )
    )

    if latency is not None:
        samples = [
            float(
                value
            )
            for value in normalized.get(
                "latency_samples_ms",
                [],
            )
            if optional_float(
                value
            )
            is not None
        ]

        samples.append(
            latency
        )

        samples = samples[
            -200:
        ]

        normalized[
            "latency_samples_ms"
        ] = samples

        normalized[
            "latency_count"
        ] = len(
            samples
        )

        normalized[
            "average_latency_ms"
        ] = round(
            sum(
                samples
            )
            / len(
                samples
            ),
            3,
        )

        normalized[
            "minimum_latency_ms"
        ] = round(
            min(
                samples
            ),
            3,
        )

        normalized[
            "maximum_latency_ms"
        ] = round(
            max(
                samples
            ),
            3,
        )

        normalized[
            "p95_latency_ms"
        ] = percentile_95(
            samples
        )

        normalized[
            "last_latency_ms"
        ] = round(
            latency,
            3,
        )

    payload_bytes = optional_int(
        payload.get(
            "payload_bytes",
            payload.get(
                "bytes_in",
            ),
        )
    )

    if payload_bytes is not None:
        normalized[
            "bytes_in"
        ] = int(
            normalized.get(
                "bytes_in",
                0,
            )
        ) + payload_bytes

    response_bytes = optional_int(
        payload.get(
            "response_bytes",
            payload.get(
                "bytes_out",
            ),
        )
    )

    if response_bytes is not None:
        normalized[
            "bytes_out"
        ] = int(
            normalized.get(
                "bytes_out",
                0,
            )
        ) + response_bytes

    active_requests = optional_int(
        payload.get(
            "active_requests"
        )
    )

    if active_requests is not None:
        normalized[
            "active_requests"
        ] = active_requests

    normalized[
        "health"
    ] = (
        "degraded"
        if failure_count > 0
        and failure_count >= success_count
        else "healthy"
    )

    return normalized




# Objective 5G — canonical ownership for
# runtime, frontend, and qualification nodes.
NODE_ARCHITECTURE.update(
    {
        "model_runtime": {
            "layer": "L4",
            "stack": "chat_public",
            "component_type": "runtime",
            "source_file": "backend/app/stacks/chat_public/chat_runtime.py",
        },
        "authenticated_gpu_chat_qualification": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "qualification",
            "source_file": "runtime/launch_candidate",
        },
        "backend_launcher_completion": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "qualification",
            "source_file": "runtime/launch_candidate",
        },
        "backend_launcher_qualification": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "qualification",
            "source_file": "runtime/launch_candidate",
        },
        "frontend_notifications": {
            "layer": "L6",
            "stack": "notification",
            "component_type": "frontend_proxy",
            "source_file": "frontend/app/api/v1/notifications",
        },
        "jwt_launch_source_recovery": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "recovery",
            "source_file": "runtime/launch_candidate",
        },
        "objective_5c_backup_restore": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "backup_restore_qualification",
            "source_file": "runtime/launch_candidate",
        },
        "registration_503_diagnosis": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "diagnosis",
            "source_file": "runtime/launch_candidate",
        },
        "route_probe": {
            "layer": "L7",
            "stack": "tests",
            "component_type": "probe",
            "source_file": "runtime/launch_candidate",
        },
    }
)

class CognitiveGraphState:
    def __init__(self) -> None:
        self._lock = RLock()

        self.node_state: defaultdict[str, str] = defaultdict(
            lambda: "idle"
        )
        self.node_meta: dict[str, dict[str, Any]] = {}

        self.edge_activity: defaultdict[tuple[str, str], int] = (
            defaultdict(int)
        )
        self.edge_meta: dict[str, dict[str, Any]] = {}

        self.last_events: list[dict[str, Any]] = []
        self.recent_flows: list[dict[str, Any]] = []

        self.sequence = 0

        self.load_snapshot()

    def _next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def _architecture_for(
        self,
        node: str,
        payload: dict[str, Any],
    ) -> dict[str, str]:
        known = NODE_ARCHITECTURE.get(node, {})

        return {
            "layer": str(
                payload.get("layer")
                or known.get("layer")
                or "UNASSIGNED"
            ),
            "stack": str(
                payload.get("stack")
                or known.get("stack")
                or "UNASSIGNED"
            ),
        }

    def save_snapshot(self) -> None:
        temporary = SNAPSHOT_FILE.with_suffix(".json.tmp")

        temporary.write_text(
            json.dumps(
                self.snapshot(),
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        temporary.replace(SNAPSHOT_FILE)

    def load_snapshot(self) -> None:
        if not SNAPSHOT_FILE.exists():
            return

        try:
            data = json.loads(
                SNAPSHOT_FILE.read_text(encoding="utf-8")
            )

            self.node_state = defaultdict(
                lambda: "idle",
                data.get("nodes", {}),
            )

            self.node_meta = data.get("node_meta", {})
            self.last_events = data.get("events", [])
            self.recent_flows = data.get("recent_flows", [])

            self.sequence = int(
                data.get(
                    "sequence",
                    max(
                        [
                            int(event.get("sequence", 0))
                            for event in self.last_events
                        ]
                        or [0]
                    ),
                )
            )

            self.edge_activity = defaultdict(int)

            for key, count in data.get("edges", {}).items():
                if "->" not in key:
                    continue

                source, destination = key.split("->", 1)
                self.edge_activity[(source, destination)] = int(
                    count
                )

            self.edge_meta = data.get("edge_meta", {})

            print(
                "🧠 Graph restored "
                f"nodes={len(self.node_state)} "
                f"edges={len(self.edge_activity)} "
                f"sequence={self.sequence}"
            )

        except Exception as error:
            print(f"⚠ graph restore failed: {error}")

    def append_event(self, event: dict[str, Any]) -> None:
        with EVENT_FILE.open(
            "a",
            encoding="utf-8",
        ) as event_file:
            event_file.write(
                json.dumps(
                    event,
                    sort_keys=True,
                )
                + "\n"
            )

    def _store_event(self, event: dict[str, Any]) -> None:
        self.last_events.append(event)

        if len(self.last_events) > 500:
            self.last_events = self.last_events[-500:]

        self.append_event(event)

    def _store_flow_step(
        self,
        event: dict[str, Any],
    ) -> None:
        self.recent_flows.append(event)

        if len(self.recent_flows) > 300:
            self.recent_flows = self.recent_flows[-300:]

    def activate_node(
        self,
        node: str,
        event_type: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = dict(payload or {})

        with self._lock:
            timestamp = now()
            trace_id = str(
                payload.get("trace_id") or new_trace_id()
            )
            status = str(
                payload.get("status") or "active"
            )

            architecture = self._architecture_for(
                node,
                payload,
            )

            self.node_state[node] = status

            meta = dict(
                self.node_meta.get(
                    node,
                    {
                        "event_count": 0,
                        "first_seen": timestamp,
                    },
                )
            )

            meta["status"] = status
            meta["event_count"] = int(
                meta.get("event_count", 0)
            ) + 1

            meta = update_metric_contract(
                meta,
                status=status,
                payload=payload,
            )

            meta["request_count"] = int(
                meta.get(
                    "event_count",
                    0,
                )
            )

            meta["last_seen"] = timestamp
            meta["last_event_type"] = event_type
            meta["last_trace_id"] = trace_id
            meta["symbol"] = payload.get("symbol")
            meta["message"] = payload.get("message")
            meta["layer"] = architecture["layer"]
            meta["stack"] = architecture["stack"]
            meta["declared"] = (
                node in NODE_ARCHITECTURE
            )
            meta["observed"] = True
            meta["materialization_state"] = "observed"

            known_ownership = NODE_ARCHITECTURE.get(
                node,
                {},
            )

            if known_ownership.get(
                "component_type"
            ):
                meta[
                    "component_type"
                ] = known_ownership[
                    "component_type"
                ]

            if known_ownership.get(
                "source_file"
            ):
                meta[
                    "source_file"
                ] = known_ownership[
                    "source_file"
                ]

            self.node_meta[node] = meta

            event = {
                "sequence": self._next_sequence(),
                "record_type": "node_activation",
                "trace_id": trace_id,
                "node": node,
                "event_type": event_type,
                "status": status,
                "layer": architecture["layer"],
                "stack": architecture["stack"],
                "symbol": payload.get("symbol"),
                "message": payload.get("message"),
                "http_status": payload.get(
                    "http_status",
                    payload.get(
                        "status_code"
                    ),
                ),
                "latency_ms": payload.get(
                    "latency_ms",
                    payload.get(
                        "duration_ms"
                    ),
                ),
                "request_id": payload.get(
                    "request_id"
                ),
                "user_id": payload.get(
                    "user_id"
                ),
                "payload_bytes": payload.get(
                    "payload_bytes",
                    payload.get(
                        "bytes_in"
                    ),
                ),
                "response_bytes": payload.get(
                    "response_bytes",
                    payload.get(
                        "bytes_out"
                    ),
                ),
                "error": payload.get(
                    "error"
                ),
                "timestamp": timestamp,
            }

            self._store_event(event)
            self._store_flow_step(event)
            self.save_snapshot()

            return event

    def _materialize_edge_endpoint(
        self,
        node: str,
        *,
        status: str,
        timestamp: str,
    ) -> None:
        """
        Materialize an endpoint reached by genuine edge traffic.

        This does not create a node-activation event and does not
        increment request, success, failure, or latency metrics.
        """

        architecture = self._architecture_for(
            node,
            {},
        )

        current_meta = dict(
            self.node_meta.get(
                node,
                {},
            )
        )

        current_meta.setdefault(
            "event_count",
            0,
        )
        current_meta.setdefault(
            "request_count",
            0,
        )
        current_meta.setdefault(
            "success_count",
            0,
        )
        current_meta.setdefault(
            "failure_count",
            0,
        )
        current_meta.setdefault(
            "first_seen",
            timestamp,
        )

        current_meta[
            "status"
        ] = status

        current_meta[
            "last_seen"
        ] = timestamp

        current_meta[
            "layer"
        ] = architecture[
            "layer"
        ]

        current_meta[
            "stack"
        ] = architecture[
            "stack"
        ]

        current_meta[
            "declared"
        ] = (
            node
            in NODE_ARCHITECTURE
        )

        current_meta[
            "observed"
        ] = True

        current_meta[
            "materialized_from_edge"
        ] = True

        current_meta[
            "materialization_state"
        ] = "observed"

        known_ownership = NODE_ARCHITECTURE.get(
            node,
            {},
        )

        if known_ownership.get(
            "component_type"
        ):
            current_meta[
                "component_type"
            ] = known_ownership[
                "component_type"
            ]

        if known_ownership.get(
            "source_file"
        ):
            current_meta[
                "source_file"
            ] = known_ownership[
                "source_file"
            ]

        self.node_state[
            node
        ] = status

        self.node_meta[
            node
        ] = current_meta

    def activate_edge(
        self,
        src: str,
        dst: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = dict(payload or {})

        with self._lock:
            timestamp = now()
            trace_id = str(
                payload.get("trace_id") or new_trace_id()
            )
            status = str(
                payload.get("status") or "active"
            )

            self._materialize_edge_endpoint(
                src,
                status=status,
                timestamp=timestamp,
            )

            self._materialize_edge_endpoint(
                dst,
                status=status,
                timestamp=timestamp,
            )

            key = (src, dst)
            edge_id = f"{src}->{dst}"

            self.edge_activity[key] += 1

            source_architecture = self._architecture_for(
                src,
                {},
            )
            destination_architecture = self._architecture_for(
                dst,
                {},
            )

            edge_metrics = update_metric_contract(
                dict(
                    self.edge_meta.get(
                        edge_id,
                        {},
                    )
                ),
                status=status,
                payload=payload,
            )

            edge_metrics.update(
                {
                    "id": edge_id,
                    "from": src,
                    "to": dst,
                    "count": self.edge_activity[key],
                    "request_count": self.edge_activity[key],
                    "status": status,
                    "last_seen": timestamp,
                    "last_trace_id": trace_id,
                    "symbol": payload.get("symbol"),
                    "source_layer": source_architecture["layer"],
                    "destination_layer": (
                        destination_architecture["layer"]
                    ),
                    "declared": (
                        any(
                            declared_source == src
                            and declared_destination == dst
                            for (
                                declared_source,
                                declared_destination,
                                _,
                            )
                            in DECLARED_GRAPH_EDGES
                        )
                    ),
                    "observed": True,
                    "materialization_state": "observed",
                }
            )

            self.edge_meta[
                edge_id
            ] = edge_metrics

            event = {
                "sequence": self._next_sequence(),
                "record_type": "edge_activation",
                "trace_id": trace_id,
                "edge_id": edge_id,
                "from": src,
                "to": dst,
                "event_type": payload.get("event_type"),
                "status": status,
                "symbol": payload.get("symbol"),
                "source_layer": source_architecture["layer"],
                "destination_layer": (
                    destination_architecture["layer"]
                ),
                "http_status": payload.get(
                    "http_status",
                    payload.get(
                        "status_code"
                    ),
                ),
                "latency_ms": payload.get(
                    "latency_ms",
                    payload.get(
                        "duration_ms"
                    ),
                ),
                "request_id": payload.get(
                    "request_id"
                ),
                "user_id": payload.get(
                    "user_id"
                ),
                "payload_bytes": payload.get(
                    "payload_bytes",
                    payload.get(
                        "bytes_in"
                    ),
                ),
                "response_bytes": payload.get(
                    "response_bytes",
                    payload.get(
                        "bytes_out"
                    ),
                ),
                "error": payload.get(
                    "error"
                ),
                "timestamp": timestamp,
            }

            self._store_event(event)
            self._store_flow_step(event)
            self.save_snapshot()

            return event

    def recent_trace_groups(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}

        for event in self.recent_flows:
            trace_id = str(
                event.get("trace_id") or "unknown"
            )
            grouped.setdefault(trace_id, []).append(event)

        traces = []

        for trace_id, steps in grouped.items():
            ordered_steps = sorted(
                steps,
                key=lambda item: int(
                    item.get("sequence", 0)
                ),
            )

            traces.append(
                {
                    "trace_id": trace_id,
                    "symbol": next(
                        (
                            step.get("symbol")
                            for step in ordered_steps
                            if step.get("symbol")
                        ),
                        None,
                    ),
                    "started_at": (
                        ordered_steps[0].get("timestamp")
                        if ordered_steps
                        else None
                    ),
                    "last_seen": (
                        ordered_steps[-1].get("timestamp")
                        if ordered_steps
                        else None
                    ),
                    "step_count": len(ordered_steps),
                    "steps": ordered_steps,
                }
            )

        traces.sort(
            key=lambda trace: str(
                trace.get("last_seen") or ""
            ),
            reverse=True,
        )

        return traces[:limit]


    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            timestamp = now()

            materialized_nodes: dict[
                str,
                str,
            ] = {
                node: "declared"
                for node in NODE_ARCHITECTURE
            }

            materialized_node_meta: dict[
                str,
                dict[str, Any],
            ] = {}

            for node, ownership in NODE_ARCHITECTURE.items():
                materialized_node_meta[
                    node
                ] = {
                    "status": "declared",
                    "event_count": 0,
                    "request_count": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "health": "unobserved",
                    "layer": ownership.get(
                        "layer",
                        "UNASSIGNED",
                    ),
                    "stack": ownership.get(
                        "stack",
                        "UNASSIGNED",
                    ),
                    "component_type": ownership.get(
                        "component_type",
                        "component",
                    ),
                    "source_file": ownership.get(
                        "source_file"
                    ),
                    "declared": True,
                    "observed": False,
                    "materialization_state": "declared",
                }

            for node, status in self.node_state.items():
                materialized_nodes[
                    node
                ] = status

            for node, meta in self.node_meta.items():
                existing = dict(
                    materialized_node_meta.get(
                        node,
                        {},
                    )
                )

                existing.update(
                    meta
                )

                existing[
                    "observed"
                ] = bool(
                    meta.get(
                        "observed",
                        int(
                            meta.get(
                                "event_count",
                                0,
                            )
                        )
                        > 0
                        or bool(
                            meta.get(
                                "materialized_from_edge"
                            )
                        ),
                    )
                )

                existing[
                    "declared"
                ] = (
                    node
                    in NODE_ARCHITECTURE
                )

                existing[
                    "materialization_state"
                ] = (
                    "observed"
                    if existing[
                        "observed"
                    ]
                    else "declared"
                )

                materialized_node_meta[
                    node
                ] = existing

            materialized_edges: dict[
                str,
                int,
            ] = {}

            materialized_edge_meta: dict[
                str,
                dict[str, Any],
            ] = {}

            for (
                source,
                destination,
                relation,
            ) in DECLARED_GRAPH_EDGES:
                edge_id = (
                    f"{source}->{destination}"
                )

                source_ownership = (
                    NODE_ARCHITECTURE.get(
                        source,
                        {},
                    )
                )

                destination_ownership = (
                    NODE_ARCHITECTURE.get(
                        destination,
                        {},
                    )
                )

                materialized_edges[
                    edge_id
                ] = 0

                materialized_edge_meta[
                    edge_id
                ] = {
                    "id": edge_id,
                    "from": source,
                    "to": destination,
                    "type": relation,
                    "relation": relation,
                    "count": 0,
                    "request_count": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "status": "declared",
                    "health": "unobserved",
                    "source_layer": (
                        source_ownership.get(
                            "layer",
                            "UNASSIGNED",
                        )
                    ),
                    "destination_layer": (
                        destination_ownership.get(
                            "layer",
                            "UNASSIGNED",
                        )
                    ),
                    "declared": True,
                    "observed": False,
                    "materialization_state": "declared",
                }

            for key, count in self.edge_activity.items():
                edge_id = (
                    f"{key[0]}->{key[1]}"
                )

                materialized_edges[
                    edge_id
                ] = count

            for edge_id, meta in self.edge_meta.items():
                existing = dict(
                    materialized_edge_meta.get(
                        edge_id,
                        {},
                    )
                )

                existing.update(
                    meta
                )

                existing[
                    "observed"
                ] = True

                existing[
                    "materialization_state"
                ] = "observed"

                materialized_edge_meta[
                    edge_id
                ] = existing

            return {
                "status": "ok",
                "sequence": self.sequence,
                "nodes": materialized_nodes,
                "node_meta": materialized_node_meta,
                "edges": materialized_edges,
                "edge_meta": materialized_edge_meta,
                "events": self.last_events[-100:],
                "recent_flows": self.recent_flows[-150:],
                "traces": self.recent_trace_groups(
                    limit=20
                ),
                "topology": {
                    "declared_node_count": len(
                        NODE_ARCHITECTURE
                    ),
                    "observed_node_count": sum(
                        1
                        for meta
                        in materialized_node_meta.values()
                        if meta.get(
                            "observed"
                        )
                    ),
                    "declared_edge_count": len(
                        DECLARED_GRAPH_EDGES
                    ),
                    "observed_edge_count": len(
                        self.edge_activity
                    ),
                    "layers": [
                        "L7",
                        "L6",
                        "L5",
                        "L4",
                        "L3",
                        "L2",
                        "L1",
                        "L0",
                    ],
                    "generated_at": timestamp,
                },
                "contract": {
                    "phase": '133B_ACTIVE_NODE_FLOW_GRAPH',
                    "version": 2,
                    "event_driven": True,
                    "synthetic_activations": False,
                    "metric_aggregation": True,
                    "declared_topology": True,
                    "edge_endpoint_materialization": True,
                    "declared_edges_are_runtime_activity": False,
                    "layers": [
                        "L7",
                        "L6",
                        "L5",
                        "L4",
                        "L3",
                        "L2",
                        "L1",
                        "L0",
                    ],
                    "supported_metrics": [
                        "request_count",
                        "success_count",
                        "failure_count",
                        "unauthorized_count",
                        "forbidden_count",
                        "http_error_count",
                        "average_latency_ms",
                        "minimum_latency_ms",
                        "maximum_latency_ms",
                        "p95_latency_ms",
                        "bytes_in",
                        "bytes_out",
                        "active_requests",
                        "health",
                    ],
                },
            }


graph_state = CognitiveGraphState()
