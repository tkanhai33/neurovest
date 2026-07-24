#!/usr/bin/env python3

"""
Phase 135 Fintech Capability Grader.

This is the first grading stage.

It consumes only evidence produced by earlier Phase 135 stages:

- repository discovery
- layer mapping
- dependency mapping
- import graph normalization
- runtime graph discovery
- contract discovery

It does not:

- rescan the repository
- execute application code
- modify application code
- enforce the intended NeuroVest architecture
- assign production-readiness status
- assign production-blocker severity

The grader measures observable fintech capability independently across:

1. Market Data
2. Portfolio Management
3. Broker Integration
4. Strategy Engine
5. Risk Engine
6. Paper Trading
7. Research
8. Runtime Orchestration
9. Authentication and Identity
10. Database and Persistence
11. Audit, Journal, and Logging
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ARCHIVE_MARKERS = {
    "archive",
    "archives",
    "architecture_backup",
    "backup",
    "backups",
    "deprecated",
    "legacy",
    "old",
    "quarantine",
    "quarantine_artifacts",
}

GENERATED_MARKERS = {
    ".next",
    "build",
    "coverage",
    "dist",
    "generated",
    "htmlcov",
    "node_modules",
    "output",
    "outputs",
    "reports",
    "runtime",
}

TOOLING_MARKERS = {
    "bin",
    "script",
    "scripts",
    "tool",
    "tools",
}

TEST_MARKERS = {
    "__tests__",
    "spec",
    "specs",
    "test",
    "tests",
}


CAPABILITY_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "market_data",
        "category": "Market Data",
        "checks": [
            {
                "id": "market_data_source",
                "label": "Market data source or adapter",
                "points": 20,
                "keyword_groups": [
                    ["market", "data"],
                    ["quote"],
                    ["price"],
                    ["bars"],
                    ["historical", "bars"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                    "packages",
                },
            },
            {
                "id": "historical_data",
                "label": "Historical market data",
                "points": 20,
                "keyword_groups": [
                    ["historical"],
                    ["ohlc"],
                    ["ohlcv"],
                    ["candlestick"],
                    ["bar"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "live_or_realtime_data",
                "label": "Live or real-time market data",
                "points": 20,
                "keyword_groups": [
                    ["live", "price"],
                    ["realtime"],
                    ["real_time"],
                    ["stream"],
                    ["websocket"],
                    ["ticker"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                    "runtime_signals",
                },
            },
            {
                "id": "market_data_contracts",
                "label": "Market data contracts",
                "points": 20,
                "keyword_groups": [
                    ["market", "contract"],
                    ["quote", "contract"],
                    ["price", "contract"],
                    ["bar", "contract"],
                    ["candle"],
                    ["symbol"],
                ],
                "sources": {
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "market_data_tests",
                "label": "Market data tests",
                "points": 20,
                "keyword_groups": [
                    ["market"],
                    ["price"],
                    ["quote"],
                    ["bars"],
                    ["historical"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "portfolio",
        "category": "Portfolio Management",
        "checks": [
            {
                "id": "portfolio_domain",
                "label": "Portfolio domain",
                "points": 20,
                "keyword_groups": [
                    ["portfolio"],
                    ["position"],
                    ["holding"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "positions_api",
                "label": "Positions or holdings API",
                "points": 20,
                "keyword_groups": [
                    ["position"],
                    ["holding"],
                    ["portfolio"],
                ],
                "sources": {
                    "routes",
                },
            },
            {
                "id": "portfolio_valuation",
                "label": "Portfolio valuation or performance",
                "points": 20,
                "keyword_groups": [
                    ["valuation"],
                    ["performance"],
                    ["equity"],
                    ["cost_basis"],
                    ["market_value"],
                    ["profit"],
                    ["pnl"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "portfolio_persistence",
                "label": "Portfolio persistence",
                "points": 20,
                "keyword_groups": [
                    ["portfolio", "repository"],
                    ["position", "repository"],
                    ["portfolio", "model"],
                    ["position", "model"],
                    ["portfolio", "store"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "portfolio_tests",
                "label": "Portfolio tests",
                "points": 20,
                "keyword_groups": [
                    ["portfolio"],
                    ["position"],
                    ["holding"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "broker_integration",
        "category": "Broker Integration",
        "checks": [
            {
                "id": "broker_adapter",
                "label": "Broker adapter or integration",
                "points": 20,
                "keyword_groups": [
                    ["broker"],
                    ["snaptrade"],
                    ["brokerage"],
                    ["execution", "adapter"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                    "external_dependencies",
                },
            },
            {
                "id": "account_connectivity",
                "label": "Broker account connectivity",
                "points": 20,
                "keyword_groups": [
                    ["account"],
                    ["connection"],
                    ["connect"],
                    ["authorization"],
                    ["oauth"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
                "context_keywords": [
                    "broker",
                    "snaptrade",
                    "brokerage",
                ],
            },
            {
                "id": "order_model",
                "label": "Order model or contract",
                "points": 20,
                "keyword_groups": [
                    ["order"],
                    ["trade", "request"],
                    ["execution", "request"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "broker_runtime",
                "label": "Broker runtime path",
                "points": 20,
                "keyword_groups": [
                    ["broker"],
                    ["snaptrade"],
                    ["order"],
                    ["execution"],
                ],
                "sources": {
                    "runtime_signals",
                    "runtime_edges",
                    "reachable_paths",
                },
            },
            {
                "id": "broker_tests",
                "label": "Broker integration tests",
                "points": 20,
                "keyword_groups": [
                    ["broker"],
                    ["snaptrade"],
                    ["order"],
                    ["execution"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "strategy_engine",
        "category": "Strategy Engine",
        "checks": [
            {
                "id": "strategy_domain",
                "label": "Strategy domain",
                "points": 20,
                "keyword_groups": [
                    ["strategy"],
                    ["signal"],
                    ["indicator"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "technical_indicators",
                "label": "Technical indicators",
                "points": 20,
                "keyword_groups": [
                    ["rsi"],
                    ["macd"],
                    ["bollinger"],
                    ["atr"],
                    ["indicator"],
                    ["moving_average"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "strategy_decision",
                "label": "Strategy decision path",
                "points": 20,
                "keyword_groups": [
                    ["decision"],
                    ["entry_signal"],
                    ["exit_signal"],
                    ["buy_signal"],
                    ["sell_signal"],
                    ["recommendation"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                    "runtime_edges",
                },
                "context_keywords": [
                    "strategy",
                    "signal",
                ],
            },
            {
                "id": "backtest_or_simulation",
                "label": "Strategy backtest or simulation",
                "points": 20,
                "keyword_groups": [
                    ["backtest"],
                    ["simulation"],
                    ["simulate"],
                    ["historical", "strategy"],
                    ["candidate", "sandbox"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "strategy_tests",
                "label": "Strategy tests",
                "points": 20,
                "keyword_groups": [
                    ["strategy"],
                    ["signal"],
                    ["indicator"],
                    ["backtest"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "risk_engine",
        "category": "Risk Engine",
        "checks": [
            {
                "id": "risk_domain",
                "label": "Risk domain",
                "points": 20,
                "keyword_groups": [
                    ["risk"],
                    ["drawdown"],
                    ["exposure"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "risk_gate",
                "label": "Risk gate or approval control",
                "points": 20,
                "keyword_groups": [
                    ["risk", "gate"],
                    ["gate"],
                    ["approval"],
                    ["allow"],
                    ["deny"],
                    ["blocked"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                    "safety_signals",
                },
                "context_keywords": [
                    "risk",
                    "trade",
                    "order",
                ],
            },
            {
                "id": "position_sizing",
                "label": "Position sizing or exposure control",
                "points": 20,
                "keyword_groups": [
                    ["position", "size"],
                    ["position_sizing"],
                    ["exposure"],
                    ["allocation"],
                    ["capital", "limit"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "loss_controls",
                "label": "Loss, drawdown, or stop controls",
                "points": 20,
                "keyword_groups": [
                    ["drawdown"],
                    ["stop_loss"],
                    ["loss_limit"],
                    ["max_loss"],
                    ["emergency_stop"],
                    ["kill_switch"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "risk_tests",
                "label": "Risk tests",
                "points": 20,
                "keyword_groups": [
                    ["risk"],
                    ["drawdown"],
                    ["exposure"],
                    ["stop_loss"],
                    ["gate"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "paper_trading",
        "category": "Paper Trading",
        "checks": [
            {
                "id": "paper_broker",
                "label": "Paper broker",
                "points": 20,
                "keyword_groups": [
                    ["paper", "broker"],
                    ["paper_broker"],
                    ["simulated", "broker"],
                    ["mock", "broker"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "paper_orders",
                "label": "Paper order execution",
                "points": 20,
                "keyword_groups": [
                    ["paper", "order"],
                    ["simulated", "order"],
                    ["simulation", "order"],
                    ["execute", "paper"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_edges",
                },
            },
            {
                "id": "trade_simulation",
                "label": "Trade simulation",
                "points": 20,
                "keyword_groups": [
                    ["trade", "simulation"],
                    ["simulate", "trade"],
                    ["simulation"],
                    ["sandbox"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "paper_ledger",
                "label": "Paper trade ledger or journal",
                "points": 20,
                "keyword_groups": [
                    ["paper", "ledger"],
                    ["trade", "ledger"],
                    ["paper", "journal"],
                    ["simulation", "result"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "paper_trading_tests",
                "label": "Paper trading tests",
                "points": 20,
                "keyword_groups": [
                    ["paper"],
                    ["simulation"],
                    ["simulated"],
                    ["sandbox"],
                ],
                "sources": {
                    "tests",
                },
                "context_keywords": [
                    "trade",
                    "broker",
                    "order",
                    "strategy",
                ],
            },
        ],
    },
    {
        "id": "research",
        "category": "Research",
        "checks": [
            {
                "id": "research_domain",
                "label": "Research domain",
                "points": 20,
                "keyword_groups": [
                    ["research"],
                    ["analysis"],
                    ["learning"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "fundamental_or_macro_data",
                "label": "Fundamental or macroeconomic data",
                "points": 20,
                "keyword_groups": [
                    ["fundamental"],
                    ["fred"],
                    ["macro"],
                    ["economic"],
                    ["earnings"],
                    ["financial_statement"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "external_dependencies",
                },
            },
            {
                "id": "news_or_sentiment",
                "label": "News or sentiment analysis",
                "points": 20,
                "keyword_groups": [
                    ["news"],
                    ["sentiment"],
                    ["headline"],
                    ["social"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "research_persistence",
                "label": "Research persistence or datasets",
                "points": 20,
                "keyword_groups": [
                    ["research", "data"],
                    ["dataset"],
                    ["research", "store"],
                    ["research", "repository"],
                    ["metadata"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "research_tests",
                "label": "Research tests",
                "points": 20,
                "keyword_groups": [
                    ["research"],
                    ["analysis"],
                    ["sentiment"],
                    ["news"],
                    ["fred"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "runtime_orchestration",
        "category": "Runtime Orchestration",
        "checks": [
            {
                "id": "application_entrypoint",
                "label": "Active application entrypoint",
                "points": 20,
                "metric": "active_entrypoints",
                "minimum": 1,
            },
            {
                "id": "api_routes",
                "label": "Application API routes",
                "points": 20,
                "metric": "routes",
                "minimum": 1,
            },
            {
                "id": "runtime_reachability",
                "label": "Static runtime reachability",
                "points": 20,
                "metric": "reachable_files",
                "minimum": 10,
            },
            {
                "id": "event_or_task_runtime",
                "label": "Events, tasks, workers, or schedulers",
                "points": 20,
                "keyword_groups": [
                    ["event"],
                    ["publish"],
                    ["subscribe"],
                    ["scheduler"],
                    ["task"],
                    ["worker"],
                ],
                "sources": {
                    "runtime_signals",
                    "runtime_edges",
                },
            },
            {
                "id": "runtime_tests",
                "label": "Runtime or API tests",
                "points": 20,
                "keyword_groups": [
                    ["runtime"],
                    ["api"],
                    ["route"],
                    ["health"],
                    ["integration"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "authentication_identity",
        "category": "Authentication and Identity",
        "checks": [
            {
                "id": "identity_domain",
                "label": "Identity or authentication domain",
                "points": 20,
                "keyword_groups": [
                    ["auth"],
                    ["identity"],
                    ["user"],
                    ["session"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "authorization_controls",
                "label": "Authorization or permission controls",
                "points": 20,
                "keyword_groups": [
                    ["authorization"],
                    ["authorize"],
                    ["permission"],
                    ["role"],
                    ["access", "control"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "credential_or_token_handling",
                "label": "Credential or token handling",
                "points": 20,
                "keyword_groups": [
                    ["token"],
                    ["credential"],
                    ["secret"],
                    ["password"],
                    ["api_key"],
                    ["oauth"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
            },
            {
                "id": "protected_api",
                "label": "Authentication API or protected route evidence",
                "points": 20,
                "keyword_groups": [
                    ["auth"],
                    ["login"],
                    ["session"],
                    ["token"],
                    ["user"],
                ],
                "sources": {
                    "routes",
                    "functions",
                },
            },
            {
                "id": "auth_tests",
                "label": "Authentication tests",
                "points": 20,
                "keyword_groups": [
                    ["auth"],
                    ["identity"],
                    ["login"],
                    ["token"],
                    ["permission"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "database_persistence",
        "category": "Database and Persistence",
        "checks": [
            {
                "id": "database_runtime",
                "label": "Database initialization",
                "points": 20,
                "keyword_groups": [
                    ["database"],
                    ["create_engine"],
                    ["sessionmaker"],
                    ["postgres"],
                    ["sqlalchemy"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "functions",
                    "runtime_signals",
                    "external_dependencies",
                },
            },
            {
                "id": "persistent_models",
                "label": "Persistent models",
                "points": 20,
                "keyword_groups": [
                    ["db_model"],
                    ["database", "model"],
                    ["persistence", "model"],
                    ["sqlalchemy"],
                    ["mapped"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "repository_or_store",
                "label": "Repository or store abstraction",
                "points": 20,
                "keyword_groups": [
                    ["repository"],
                    ["store"],
                    ["persistence"],
                    ["ledger"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "migration_or_schema",
                "label": "Migration or database schema management",
                "points": 20,
                "keyword_groups": [
                    ["alembic"],
                    ["migration"],
                    ["schema"],
                    ["metadata"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "database",
                    "db",
                    "sql",
                    "postgres",
                    "model",
                ],
            },
            {
                "id": "database_tests",
                "label": "Database tests",
                "points": 20,
                "keyword_groups": [
                    ["database"],
                    ["db"],
                    ["repository"],
                    ["persistence"],
                    ["postgres"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "audit_logging",
        "category": "Audit, Journal, and Logging",
        "checks": [
            {
                "id": "journal_or_ledger",
                "label": "Journal or ledger domain",
                "points": 20,
                "keyword_groups": [
                    ["journal"],
                    ["ledger"],
                    ["audit"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "runtime_logging",
                "label": "Runtime logging or tracing",
                "points": 20,
                "keyword_groups": [
                    ["logging"],
                    ["logger"],
                    ["trace"],
                    ["telemetry"],
                    ["observability"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
            },
            {
                "id": "trade_history",
                "label": "Trade or order history",
                "points": 20,
                "keyword_groups": [
                    ["trade", "history"],
                    ["order", "history"],
                    ["execution", "history"],
                    ["transaction"],
                    ["ledger", "entry"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "immutable_or_append_only",
                "label": "Append-only or immutable audit evidence",
                "points": 20,
                "keyword_groups": [
                    ["append_only"],
                    ["append", "ledger"],
                    ["immutable"],
                    ["audit", "event"],
                    ["journal", "entry"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "audit_tests",
                "label": "Audit, ledger, or journal tests",
                "points": 20,
                "keyword_groups": [
                    ["audit"],
                    ["journal"],
                    ["ledger"],
                    ["logging"],
                    ["trace"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
]


class FintechCapabilityGrader:
    """
    Grade observable fintech capability from existing Phase 135 evidence.
    """

    def __init__(
        self,
        discovery: dict[str, Any],
        layer_mapping: dict[str, Any],
        dependency_mapping: dict[str, Any],
        import_graph: dict[str, Any],
        runtime_graph: dict[str, Any],
        contract_discovery: dict[str, Any],
    ) -> None:
        self.discovery = discovery
        self.layer_mapping = layer_mapping
        self.dependency_mapping = dependency_mapping
        self.import_graph = import_graph
        self.runtime_graph = runtime_graph
        self.contract_discovery = contract_discovery

        self.evidence = self._build_evidence_index()
        self.metrics = self._build_metric_index()

    def grade(self) -> dict[str, Any]:
        categories = [
            self._grade_category(definition)
            for definition in CAPABILITY_DEFINITIONS
        ]

        total_score = round(
            sum(category["score"] for category in categories),
            2,
        )

        total_maximum = sum(
            category["maximum"] for category in categories
        )

        percentage = round(
            (
                total_score
                / total_maximum
                * 100
            )
            if total_maximum
            else 0.0,
            2,
        )

        status = self._status_from_percentage(percentage)

        strongest = sorted(
            categories,
            key=lambda item: (
                -item["percentage"],
                item["category"],
            ),
        )[:5]

        weakest = sorted(
            categories,
            key=lambda item: (
                item["percentage"],
                item["category"],
            ),
        )[:5]

        capability_gaps = []

        for category in categories:
            for check in category["checks"]:
                if not check["passed"]:
                    capability_gaps.append(
                        {
                            "category_id": category["category_id"],
                            "category": category["category"],
                            "check_id": check["check_id"],
                            "check": check["check"],
                            "missing": check["missing"],
                            "points_available": check["maximum"],
                        }
                    )

        return {
            "grading_mode": "evidence_based_static_capability",
            "application_executed": False,
            "repository_rescanned": False,
            "architecture_assumed": False,
            "production_readiness_assessed": False,
            "production_blockers_assessed": False,
            "summary": {
                "category_count": len(categories),
                "total_score": total_score,
                "total_maximum": total_maximum,
                "percentage": percentage,
                "status": status,
                "checks_total": sum(
                    len(category["checks"])
                    for category in categories
                ),
                "checks_passed": sum(
                    category["checks_passed"]
                    for category in categories
                ),
                "checks_missing": sum(
                    category["checks_missing"]
                    for category in categories
                ),
                "capability_gaps": len(capability_gaps),
            },
            "categories": categories,
            "strongest_categories": [
                {
                    "category_id": item["category_id"],
                    "category": item["category"],
                    "score": item["score"],
                    "maximum": item["maximum"],
                    "percentage": item["percentage"],
                    "status": item["status"],
                }
                for item in strongest
            ],
            "weakest_categories": [
                {
                    "category_id": item["category_id"],
                    "category": item["category"],
                    "score": item["score"],
                    "maximum": item["maximum"],
                    "percentage": item["percentage"],
                    "status": item["status"],
                }
                for item in weakest
            ],
            "capability_gaps": sorted(
                capability_gaps,
                key=lambda item: (
                    item["category"],
                    item["check"],
                ),
            ),
            "evidence_inventory": {
                key: len(value)
                for key, value in sorted(self.evidence.items())
            },
            "scoring_contract": {
                "category_maximum": 100,
                "check_maximum": 20,
                "category_status_thresholds": {
                    "Absent": "0-19.99",
                    "Minimal": "20-39.99",
                    "Partial": "40-59.99",
                    "Substantial": "60-79.99",
                    "Strong": "80-100",
                },
                "overall_score_is": "fintech_capability_only",
                "overall_score_is_not": [
                    "production_readiness",
                    "production_safety",
                    "regulatory_compliance",
                    "deployment_approval",
                    "live_trading_approval",
                ],
            },
            "limitations": [
                (
                    "Capability scores are based on static repository evidence "
                    "and do not prove runtime correctness."
                ),
                (
                    "Keyword and structural evidence can identify implemented "
                    "capability surfaces but cannot prove completeness."
                ),
                (
                    "Tests are credited only when test-classified paths contain "
                    "capability-relevant evidence."
                ),
                (
                    "Production readiness, production blockers, security quality, "
                    "regulatory compliance, and live-trading safety are not graded "
                    "by this stage."
                ),
            ],
        }

    def _grade_category(
        self,
        definition: dict[str, Any],
    ) -> dict[str, Any]:
        checks = [
            self._grade_check(check)
            for check in definition["checks"]
        ]

        score = round(
            sum(check["score"] for check in checks),
            2,
        )

        maximum = sum(
            check["maximum"] for check in checks
        )

        percentage = round(
            (
                score
                / maximum
                * 100
            )
            if maximum
            else 0.0,
            2,
        )

        status = self._status_from_percentage(percentage)

        evidence = []

        for check in checks:
            evidence.extend(check["evidence"])

        evidence = self._unique_evidence(evidence)[:50]

        missing = [
            check["missing"]
            for check in checks
            if not check["passed"]
        ]

        return {
            "category_id": definition["id"],
            "category": definition["category"],
            "score": score,
            "maximum": maximum,
            "percentage": percentage,
            "status": status,
            "checks_passed": sum(
                1 for check in checks if check["passed"]
            ),
            "checks_missing": sum(
                1 for check in checks if not check["passed"]
            ),
            "checks": checks,
            "evidence": evidence,
            "missing": missing,
            "notes": [
                (
                    "Capability score reflects static evidence only and does "
                    "not represent production readiness."
                )
            ],
        }

    def _grade_check(
        self,
        check: dict[str, Any],
    ) -> dict[str, Any]:
        maximum = float(check["points"])

        if "metric" in check:
            metric_name = check["metric"]
            minimum = float(check.get("minimum", 1))
            actual = float(self.metrics.get(metric_name, 0))

            passed = actual >= minimum

            evidence = [
                {
                    "source_type": "metric",
                    "source": metric_name,
                    "value": actual,
                    "minimum": minimum,
                }
            ]

            return {
                "check_id": check["id"],
                "check": check["label"],
                "score": maximum if passed else 0.0,
                "maximum": maximum,
                "passed": passed,
                "evidence": evidence,
                "missing": (
                    None
                    if passed
                    else (
                        f"Expected metric {metric_name} >= {minimum}; "
                        f"observed {actual}."
                    )
                ),
            }

        matches = self._find_matches(
            keyword_groups=check.get("keyword_groups", []),
            source_types=check.get("sources", set()),
            context_keywords=check.get("context_keywords", []),
        )

        passed = bool(matches)

        return {
            "check_id": check["id"],
            "check": check["label"],
            "score": maximum if passed else 0.0,
            "maximum": maximum,
            "passed": passed,
            "evidence": matches[:12],
            "missing": (
                None
                if passed
                else (
                    "No active static evidence matched the required "
                    "capability signals."
                )
            ),
        }

    def _find_matches(
        self,
        keyword_groups: list[list[str]],
        source_types: Iterable[str],
        context_keywords: list[str],
    ) -> list[dict[str, Any]]:
        results = []

        normalized_groups = [
            [
                self._normalize(keyword)
                for keyword in group
            ]
            for group in keyword_groups
        ]

        normalized_context = [
            self._normalize(keyword)
            for keyword in context_keywords
        ]

        for source_type in sorted(source_types):
            for item in self.evidence.get(source_type, []):
                haystack = item["normalized"]

                matched_group = None

                for group in normalized_groups:
                    if all(keyword in haystack for keyword in group):
                        matched_group = group
                        break

                if matched_group is None:
                    continue

                if normalized_context:
                    if not any(
                        keyword in haystack
                        for keyword in normalized_context
                    ):
                        continue

                results.append(
                    {
                        "source_type": source_type,
                        "source": item["source"],
                        "text": item["text"][:500],
                        "matched_keywords": matched_group,
                    }
                )

        return self._unique_evidence(results)

    def _build_evidence_index(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)

        files = self.discovery.get("files", [])

        for record in files:
            path = record.get("path", "")

            if not path:
                continue

            classification = self._classify_path(path)

            item = self._evidence_item(
                source=path,
                text=path,
            )

            if classification == "active":
                evidence["paths"].append(item)

            if record.get("is_test"):
                evidence["tests"].append(item)

        for contract in self.contract_discovery.get(
            "active_contracts",
            [],
        ):
            text = " ".join(
                str(value)
                for value in [
                    contract.get("name"),
                    contract.get("contract_kind"),
                    contract.get("source"),
                    contract.get("bases"),
                    contract.get("decorators"),
                    contract.get("fields"),
                    contract.get("abstract_methods"),
                    contract.get("name_signal"),
                ]
                if value is not None
            )

            evidence["contracts"].append(
                self._evidence_item(
                    source=contract.get("source", ""),
                    text=text,
                )
            )

        for function in self.contract_discovery.get(
            "function_contracts",
            [],
        ):
            if function.get("classification") != "active":
                continue

            text = " ".join(
                str(value)
                for value in [
                    function.get("name"),
                    function.get("owner"),
                    function.get("source"),
                    function.get("parameters"),
                    function.get("parameters_text"),
                    function.get("return_annotation"),
                    function.get("declared_type"),
                ]
                if value is not None
            )

            evidence["functions"].append(
                self._evidence_item(
                    source=function.get("source", ""),
                    text=text,
                )
            )

        for route in self.runtime_graph.get("routes", []):
            if route.get("classification") != "active":
                continue

            text = " ".join(
                str(value)
                for value in [
                    route.get("framework"),
                    route.get("method"),
                    route.get("path"),
                    route.get("handler"),
                    route.get("source"),
                ]
                if value is not None
            )

            evidence["routes"].append(
                self._evidence_item(
                    source=route.get("source", ""),
                    text=text,
                )
            )

        for signal in self.runtime_graph.get(
            "runtime_signals",
            [],
        ):
            if signal.get("classification") != "active":
                continue

            text = " ".join(
                str(value)
                for value in [
                    signal.get("signal_type"),
                    signal.get("callable"),
                    signal.get("target"),
                    signal.get("command"),
                    signal.get("arguments"),
                    signal.get("source"),
                ]
                if value is not None
            )

            evidence["runtime_signals"].append(
                self._evidence_item(
                    source=signal.get("source", ""),
                    text=text,
                )
            )

        for edge in self.runtime_graph.get(
            "runtime_edges",
            [],
        ):
            if edge.get("classification") != "active":
                continue

            text = " ".join(
                str(value)
                for value in [
                    edge.get("edge_type"),
                    edge.get("source"),
                    edge.get("target"),
                    edge.get("evidence"),
                ]
                if value is not None
            )

            evidence["runtime_edges"].append(
                self._evidence_item(
                    source=edge.get("source", ""),
                    text=text,
                )
            )

        for path in self.runtime_graph.get(
            "reachability",
            {},
        ).get("reachable_files", []):
            evidence["reachable_paths"].append(
                self._evidence_item(
                    source=path,
                    text=path,
                )
            )

        for package in self.import_graph.get(
            "package_graph",
            {},
        ).get("nodes", []):
            classification_counts = package.get(
                "classification_counts",
                {},
            )

            if classification_counts.get("active", 0) <= 0:
                continue

            text = " ".join(
                str(value)
                for value in [
                    package.get("package"),
                    package.get("files"),
                    package.get("modules"),
                    package.get("languages"),
                ]
                if value is not None
            )

            evidence["packages"].append(
                self._evidence_item(
                    source=package.get("package", ""),
                    text=text,
                )
            )

        for dependency in self.dependency_mapping.get(
            "external_dependencies",
            [],
        ):
            text = " ".join(
                str(value)
                for value in [
                    dependency.get("language"),
                    dependency.get("package"),
                    dependency.get("reference_count"),
                ]
                if value is not None
            )

            evidence["external_dependencies"].append(
                self._evidence_item(
                    source=dependency.get("package", ""),
                    text=text,
                )
            )

        for signal in self.contract_discovery.get(
            "safety_signals",
            [],
        ):
            if signal.get("classification") != "active":
                continue

            text = " ".join(
                str(value)
                for value in [
                    signal.get("name"),
                    signal.get("signal_type"),
                    signal.get("matched_markers"),
                    signal.get("source"),
                ]
                if value is not None
            )

            evidence["safety_signals"].append(
                self._evidence_item(
                    source=signal.get("source", ""),
                    text=text,
                )
            )

        return {
            key: self._deduplicate_evidence_items(value)
            for key, value in evidence.items()
        }

    def _build_metric_index(
        self,
    ) -> dict[str, float]:
        runtime_summary = self.runtime_graph.get(
            "summary",
            {},
        )

        contract_summary = self.contract_discovery.get(
            "summary",
            {},
        )

        dependency_summary = self.dependency_mapping.get(
            "summary",
            {},
        )

        import_summary = self.import_graph.get(
            "summary",
            {},
        )

        return {
            "active_entrypoints": float(
                runtime_summary.get("active_entrypoints", 0)
            ),
            "routes": float(
                runtime_summary.get("routes", 0)
            ),
            "reachable_files": float(
                runtime_summary.get("reachable_files", 0)
            ),
            "runtime_signals": float(
                runtime_summary.get("runtime_signals", 0)
            ),
            "active_contracts": float(
                contract_summary.get("active_contracts", 0)
            ),
            "route_contracts": float(
                contract_summary.get("route_contracts", 0)
            ),
            "internal_dependency_edges": float(
                dependency_summary.get(
                    "internal_dependency_edges",
                    0,
                )
            ),
            "package_nodes": float(
                import_summary.get("package_nodes", 0)
            ),
        }

    @staticmethod
    def _evidence_item(
        source: str,
        text: str,
    ) -> dict[str, Any]:
        return {
            "source": source,
            "text": text,
            "normalized": FintechCapabilityGrader._normalize(text),
        }

    @staticmethod
    def _deduplicate_evidence_items(
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        unique = {}

        for item in items:
            key = (
                item.get("source", ""),
                item.get("text", ""),
            )
            unique[key] = item

        return sorted(
            unique.values(),
            key=lambda item: (
                item.get("source", ""),
                item.get("text", ""),
            ),
        )

    @staticmethod
    def _unique_evidence(
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        unique = {}

        for item in items:
            key = (
                item.get("source_type"),
                item.get("source"),
                item.get("text"),
                item.get("value"),
            )
            unique[key] = item

        return sorted(
            unique.values(),
            key=lambda item: (
                str(item.get("source_type", "")),
                str(item.get("source", "")),
                str(item.get("text", "")),
            ),
        )

    @staticmethod
    def _normalize(value: Any) -> str:
        text = str(value).lower()

        characters = []

        for character in text:
            if character.isalnum():
                characters.append(character)
            else:
                characters.append("_")

        normalized = "".join(characters)

        while "__" in normalized:
            normalized = normalized.replace("__", "_")

        return normalized.strip("_")

    @staticmethod
    def _status_from_percentage(
        percentage: float,
    ) -> str:
        if percentage < 20:
            return "Absent"

        if percentage < 40:
            return "Minimal"

        if percentage < 60:
            return "Partial"

        if percentage < 80:
            return "Substantial"

        return "Strong"

    @staticmethod
    def _classify_path(
        path_string: str,
    ) -> str:
        path = Path(path_string)

        parts = {
            part.lower()
            for part in path.parts
        }

        lowered = path.name.lower()

        if parts.intersection(ARCHIVE_MARKERS):
            return "archive_or_quarantine"

        if parts.intersection(GENERATED_MARKERS):
            return "generated_or_output"

        if parts.intersection(TOOLING_MARKERS):
            return "tooling"

        if (
            lowered.endswith(".bak")
            or ".backup" in lowered
            or ".phase" in lowered
            or ".generated." in lowered
        ):
            return "generated_or_backup"

        return "active"
