#!/usr/bin/env python3

"""
Phase 135 AI Capability Grader.

Consumes only evidence produced by earlier Phase 135 stages:

- repository discovery
- layer mapping
- dependency mapping
- import graph normalization
- runtime graph discovery
- contract discovery
- fintech capability grading

It does not:

- rescan the repository
- execute application code
- modify application code
- assume the intended NeuroVest architecture
- assign production-readiness status
- assign production-blocker severity

The grader measures observable AI capability independently across:

1. Local Model Integration
2. Model Provider Abstraction
3. Chat and Conversation Runtime
4. Prompt Orchestration
5. Memory and Persistence
6. Tool and Function Invocation
7. Retrieval and Research Grounding
8. Strategy Generation and Composition
9. Learning and Feedback
10. Confidence and Explainability
11. AI Safety and Risk Governance
12. AI Observability and Testing
"""

from __future__ import annotations

from collections import defaultdict
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


CAPABILITY_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "local_model_integration",
        "category": "Local Model Integration",
        "checks": [
            {
                "id": "local_llm_provider",
                "label": "Local LLM provider",
                "points": 20,
                "keyword_groups": [
                    ["ollama"],
                    ["local", "llm"],
                    ["local", "model"],
                    ["llama"],
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
                "id": "model_request_runtime",
                "label": "Model request runtime",
                "points": 20,
                "keyword_groups": [
                    ["generate"],
                    ["chat"],
                    ["completion"],
                    ["invoke", "model"],
                    ["model", "request"],
                ],
                "sources": {
                    "functions",
                    "runtime_signals",
                    "runtime_edges",
                    "reachable_paths",
                },
                "context_keywords": [
                    "ollama",
                    "llm",
                    "model",
                    "chat",
                    "ai",
                ],
            },
            {
                "id": "model_configuration",
                "label": "Model configuration",
                "points": 20,
                "keyword_groups": [
                    ["model", "name"],
                    ["model_name"],
                    ["temperature"],
                    ["context_window"],
                    ["max_tokens"],
                    ["base_url"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
            },
            {
                "id": "local_model_health",
                "label": "Local model health or availability",
                "points": 20,
                "keyword_groups": [
                    ["ollama", "health"],
                    ["model", "health"],
                    ["availability"],
                    ["is_available"],
                    ["healthcheck"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "routes",
                    "runtime_signals",
                },
                "context_keywords": [
                    "ollama",
                    "llm",
                    "model",
                    "ai",
                ],
            },
            {
                "id": "local_model_tests",
                "label": "Local model integration tests",
                "points": 20,
                "keyword_groups": [
                    ["ollama"],
                    ["llm"],
                    ["model"],
                    ["completion"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "provider_abstraction",
        "category": "Model Provider Abstraction",
        "checks": [
            {
                "id": "provider_interface",
                "label": "Provider interface or contract",
                "points": 20,
                "keyword_groups": [
                    ["provider"],
                    ["model", "adapter"],
                    ["llm", "adapter"],
                    ["client", "protocol"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
                "context_keywords": [
                    "ai",
                    "llm",
                    "model",
                    "chat",
                ],
            },
            {
                "id": "provider_selection",
                "label": "Provider selection or routing",
                "points": 20,
                "keyword_groups": [
                    ["provider", "select"],
                    ["provider", "route"],
                    ["model", "router"],
                    ["fallback"],
                    ["provider_name"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_edges",
                },
            },
            {
                "id": "provider_configuration",
                "label": "Provider configuration",
                "points": 20,
                "keyword_groups": [
                    ["provider", "config"],
                    ["model", "config"],
                    ["endpoint"],
                    ["base_url"],
                    ["api_key"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
                "context_keywords": [
                    "provider",
                    "model",
                    "llm",
                    "ollama",
                    "ai",
                ],
            },
            {
                "id": "provider_failure_handling",
                "label": "Provider failure handling",
                "points": 20,
                "keyword_groups": [
                    ["retry"],
                    ["timeout"],
                    ["fallback"],
                    ["provider", "error"],
                    ["model", "unavailable"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "contracts",
                },
                "context_keywords": [
                    "provider",
                    "model",
                    "llm",
                    "ollama",
                    "ai",
                ],
            },
            {
                "id": "provider_tests",
                "label": "Provider abstraction tests",
                "points": 20,
                "keyword_groups": [
                    ["provider"],
                    ["adapter"],
                    ["fallback"],
                    ["ollama"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "chat_runtime",
        "category": "Chat and Conversation Runtime",
        "checks": [
            {
                "id": "chat_domain",
                "label": "Chat or conversation domain",
                "points": 20,
                "keyword_groups": [
                    ["chat"],
                    ["conversation"],
                    ["message"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "chat_api",
                "label": "Chat API",
                "points": 20,
                "keyword_groups": [
                    ["chat"],
                    ["conversation"],
                    ["message"],
                ],
                "sources": {
                    "routes",
                },
            },
            {
                "id": "chat_runtime_path",
                "label": "Chat runtime path",
                "points": 20,
                "keyword_groups": [
                    ["chat", "runtime"],
                    ["conversation", "runtime"],
                    ["process", "message"],
                    ["handle", "message"],
                    ["respond"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "runtime_edges",
                    "reachable_paths",
                },
            },
            {
                "id": "chat_contracts",
                "label": "Chat and message contracts",
                "points": 20,
                "keyword_groups": [
                    ["chat", "message"],
                    ["chat", "request"],
                    ["chat", "response"],
                    ["conversation"],
                    ["role"],
                ],
                "sources": {
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "chat_tests",
                "label": "Chat runtime tests",
                "points": 20,
                "keyword_groups": [
                    ["chat"],
                    ["conversation"],
                    ["message"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "prompt_orchestration",
        "category": "Prompt Orchestration",
        "checks": [
            {
                "id": "prompt_templates",
                "label": "Prompt templates or builders",
                "points": 20,
                "keyword_groups": [
                    ["prompt"],
                    ["system_message"],
                    ["instruction"],
                    ["template"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "ai",
                    "llm",
                    "chat",
                    "model",
                    "prompt",
                ],
            },
            {
                "id": "system_prompt",
                "label": "System prompt support",
                "points": 20,
                "keyword_groups": [
                    ["system", "prompt"],
                    ["system_message"],
                    ["persona"],
                    ["guard", "dog"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "context_assembly",
                "label": "Context assembly",
                "points": 20,
                "keyword_groups": [
                    ["context", "builder"],
                    ["context", "assembly"],
                    ["build", "context"],
                    ["conversation", "context"],
                    ["prompt", "context"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "prompt_modes",
                "label": "Prompt modes, personas, or policies",
                "points": 20,
                "keyword_groups": [
                    ["persona"],
                    ["mode"],
                    ["stoic"],
                    ["canary"],
                    ["guard_dog"],
                    ["policy", "prompt"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "chat",
                    "ai",
                    "prompt",
                    "neuro",
                    "wolf",
                ],
            },
            {
                "id": "prompt_tests",
                "label": "Prompt orchestration tests",
                "points": 20,
                "keyword_groups": [
                    ["prompt"],
                    ["persona"],
                    ["context"],
                    ["system_message"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "memory_persistence",
        "category": "Memory and Persistence",
        "checks": [
            {
                "id": "conversation_store",
                "label": "Conversation store",
                "points": 20,
                "keyword_groups": [
                    ["conversation", "store"],
                    ["chat", "store"],
                    ["message", "store"],
                    ["conversation_store"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "memory_domain",
                "label": "AI memory domain",
                "points": 20,
                "keyword_groups": [
                    ["memory"],
                    ["long_term_memory"],
                    ["short_term_memory"],
                    ["recall"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "ai",
                    "chat",
                    "conversation",
                    "learning",
                    "neuro",
                ],
            },
            {
                "id": "conversation_persistence",
                "label": "Persistent conversation models",
                "points": 20,
                "keyword_groups": [
                    ["chat", "model"],
                    ["conversation", "model"],
                    ["message", "model"],
                    ["persistence", "chat"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "memory_retrieval",
                "label": "Memory retrieval or recall",
                "points": 20,
                "keyword_groups": [
                    ["recall"],
                    ["retrieve", "memory"],
                    ["memory", "search"],
                    ["conversation", "history"],
                    ["load", "conversation"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "runtime_edges",
                },
            },
            {
                "id": "memory_tests",
                "label": "Memory and persistence tests",
                "points": 20,
                "keyword_groups": [
                    ["memory"],
                    ["conversation_store"],
                    ["chat_models"],
                    ["conversation"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "tool_invocation",
        "category": "Tool and Function Invocation",
        "checks": [
            {
                "id": "tool_registry",
                "label": "Tool registry",
                "points": 20,
                "keyword_groups": [
                    ["tool", "registry"],
                    ["function", "registry"],
                    ["tool_registry"],
                    ["registered_tools"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "tool_contract",
                "label": "Tool or function-call contract",
                "points": 20,
                "keyword_groups": [
                    ["tool", "contract"],
                    ["function", "call"],
                    ["tool", "schema"],
                    ["tool", "request"],
                    ["tool", "result"],
                ],
                "sources": {
                    "contracts",
                    "functions",
                    "paths",
                },
            },
            {
                "id": "tool_dispatch",
                "label": "Tool dispatch or execution",
                "points": 20,
                "keyword_groups": [
                    ["dispatch", "tool"],
                    ["execute", "tool"],
                    ["invoke", "tool"],
                    ["call", "tool"],
                    ["tool", "handler"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "runtime_edges",
                    "runtime_signals",
                },
            },
            {
                "id": "tool_authorization",
                "label": "Tool authorization or safety checks",
                "points": 20,
                "keyword_groups": [
                    ["tool", "allow"],
                    ["tool", "deny"],
                    ["tool", "permission"],
                    ["tool", "policy"],
                    ["tool", "risk"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "tool_tests",
                "label": "Tool invocation tests",
                "points": 20,
                "keyword_groups": [
                    ["tool"],
                    ["function_call"],
                    ["dispatch"],
                    ["registry"],
                ],
                "sources": {
                    "tests",
                },
                "context_keywords": [
                    "ai",
                    "chat",
                    "llm",
                    "model",
                    "tool",
                ],
            },
        ],
    },
    {
        "id": "retrieval_grounding",
        "category": "Retrieval and Research Grounding",
        "checks": [
            {
                "id": "retrieval_domain",
                "label": "Retrieval or grounding domain",
                "points": 20,
                "keyword_groups": [
                    ["retrieval"],
                    ["rag"],
                    ["grounding"],
                    ["search"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "ai",
                    "chat",
                    "research",
                    "document",
                    "knowledge",
                    "context",
                ],
            },
            {
                "id": "research_context",
                "label": "Research context integration",
                "points": 20,
                "keyword_groups": [
                    ["research", "context"],
                    ["market", "context"],
                    ["news", "context"],
                    ["evidence"],
                    ["source", "context"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_edges",
                },
            },
            {
                "id": "document_or_data_retrieval",
                "label": "Document or data retrieval",
                "points": 20,
                "keyword_groups": [
                    ["document"],
                    ["dataset"],
                    ["retrieve"],
                    ["search"],
                    ["lookup"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "packages",
                },
                "context_keywords": [
                    "research",
                    "knowledge",
                    "context",
                    "rag",
                    "ai",
                    "chat",
                ],
            },
            {
                "id": "citation_or_source_tracking",
                "label": "Citation or source tracking",
                "points": 20,
                "keyword_groups": [
                    ["citation"],
                    ["source"],
                    ["reference"],
                    ["provenance"],
                    ["evidence"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "research",
                    "answer",
                    "chat",
                    "context",
                    "ground",
                    "evidence",
                ],
            },
            {
                "id": "retrieval_tests",
                "label": "Retrieval and grounding tests",
                "points": 20,
                "keyword_groups": [
                    ["retrieval"],
                    ["rag"],
                    ["grounding"],
                    ["citation"],
                    ["context"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "strategy_generation",
        "category": "Strategy Generation and Composition",
        "checks": [
            {
                "id": "strategy_generation",
                "label": "AI strategy generation",
                "points": 20,
                "keyword_groups": [
                    ["generate", "strategy"],
                    ["strategy", "generator"],
                    ["create", "strategy"],
                    ["strategy_generation"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_edges",
                },
            },
            {
                "id": "strategy_composition",
                "label": "Strategy composition or combination",
                "points": 20,
                "keyword_groups": [
                    ["combine", "strategy"],
                    ["strategy", "composition"],
                    ["compose", "strategy"],
                    ["multi_strategy"],
                    ["consensus"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "candidate_sandbox",
                "label": "Strategy candidate sandbox",
                "points": 20,
                "keyword_groups": [
                    ["strategy_candidate_sandbox"],
                    ["candidate", "sandbox"],
                    ["strategy", "candidate"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "strategy_validation",
                "label": "Generated strategy validation",
                "points": 20,
                "keyword_groups": [
                    ["validate", "strategy"],
                    ["strategy", "validation"],
                    ["strategy", "gate"],
                    ["strategy", "simulation"],
                    ["strategy", "approval"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "strategy_generation_tests",
                "label": "Strategy generation tests",
                "points": 20,
                "keyword_groups": [
                    ["strategy", "generation"],
                    ["strategy", "candidate"],
                    ["combine", "strategy"],
                    ["strategy", "generator"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "learning_feedback",
        "category": "Learning and Feedback",
        "checks": [
            {
                "id": "learning_domain",
                "label": "Learning domain",
                "points": 20,
                "keyword_groups": [
                    ["learning"],
                    ["learn"],
                    ["training"],
                    ["feedback"],
                ],
                "sources": {
                    "paths",
                    "packages",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "ai",
                    "strategy",
                    "research",
                    "model",
                    "neuro",
                ],
            },
            {
                "id": "feedback_capture",
                "label": "Feedback capture",
                "points": 20,
                "keyword_groups": [
                    ["feedback"],
                    ["outcome"],
                    ["reward"],
                    ["result", "capture"],
                    ["user", "rating"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
            },
            {
                "id": "learning_state",
                "label": "Persistent learning state",
                "points": 20,
                "keyword_groups": [
                    ["learning", "state"],
                    ["learning_state"],
                    ["training", "state"],
                    ["memory", "state"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "packages",
                },
            },
            {
                "id": "performance_feedback",
                "label": "Performance-based feedback",
                "points": 20,
                "keyword_groups": [
                    ["performance", "feedback"],
                    ["trade", "outcome"],
                    ["strategy", "performance"],
                    ["win", "loss"],
                    ["evaluation"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
            },
            {
                "id": "learning_tests",
                "label": "Learning and feedback tests",
                "points": 20,
                "keyword_groups": [
                    ["learning"],
                    ["feedback"],
                    ["training"],
                    ["outcome"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "confidence_explainability",
        "category": "Confidence and Explainability",
        "checks": [
            {
                "id": "confidence_score",
                "label": "Confidence scoring",
                "points": 20,
                "keyword_groups": [
                    ["confidence"],
                    ["certainty"],
                    ["probability"],
                    ["score"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                },
                "context_keywords": [
                    "ai",
                    "strategy",
                    "decision",
                    "signal",
                    "recommendation",
                    "model",
                ],
            },
            {
                "id": "explanation_generation",
                "label": "Explanation generation",
                "points": 20,
                "keyword_groups": [
                    ["explain"],
                    ["explanation"],
                    ["reason"],
                    ["rationale"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "routes",
                },
                "context_keywords": [
                    "decision",
                    "strategy",
                    "risk",
                    "chat",
                    "ai",
                    "recommendation",
                ],
            },
            {
                "id": "evidence_trace",
                "label": "Evidence or reasoning trace",
                "points": 20,
                "keyword_groups": [
                    ["evidence"],
                    ["trace"],
                    ["decision", "record"],
                    ["reasoning"],
                    ["provenance"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
                "context_keywords": [
                    "ai",
                    "decision",
                    "strategy",
                    "risk",
                    "chat",
                    "model",
                ],
            },
            {
                "id": "uncertainty_handling",
                "label": "Uncertainty handling",
                "points": 20,
                "keyword_groups": [
                    ["uncertainty"],
                    ["low_confidence"],
                    ["confidence", "threshold"],
                    ["abstain"],
                    ["insufficient", "evidence"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "explainability_tests",
                "label": "Confidence and explainability tests",
                "points": 20,
                "keyword_groups": [
                    ["confidence"],
                    ["explain"],
                    ["rationale"],
                    ["uncertainty"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "ai_safety_governance",
        "category": "AI Safety and Risk Governance",
        "checks": [
            {
                "id": "ai_safety_gate",
                "label": "AI safety gate",
                "points": 20,
                "keyword_groups": [
                    ["ai", "safety"],
                    ["model", "gate"],
                    ["chat", "gate"],
                    ["safety", "policy"],
                    ["guardrail"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "trade_action_restriction",
                "label": "AI trade-action restriction",
                "points": 20,
                "keyword_groups": [
                    ["live", "trading", "disabled"],
                    ["paper", "only"],
                    ["execution", "disabled"],
                    ["trade", "permission"],
                    ["broker", "disabled"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "prompt_injection_or_input_validation",
                "label": "Prompt or input validation",
                "points": 20,
                "keyword_groups": [
                    ["prompt", "injection"],
                    ["input", "validation"],
                    ["sanitize"],
                    ["validate", "message"],
                    ["unsafe", "prompt"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "safety_signals",
                },
            },
            {
                "id": "risk_integration",
                "label": "AI and risk-engine integration",
                "points": 20,
                "keyword_groups": [
                    ["ai", "risk"],
                    ["chat", "risk"],
                    ["strategy", "risk"],
                    ["risk", "gate"],
                    ["risk", "approval"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_edges",
                    "safety_signals",
                },
            },
            {
                "id": "ai_safety_tests",
                "label": "AI safety tests",
                "points": 20,
                "keyword_groups": [
                    ["ai", "safety"],
                    ["guardrail"],
                    ["prompt", "injection"],
                    ["risk", "gate"],
                    ["paper", "only"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
    {
        "id": "ai_observability_testing",
        "category": "AI Observability and Testing",
        "checks": [
            {
                "id": "ai_logging",
                "label": "AI logging",
                "points": 20,
                "keyword_groups": [
                    ["ai", "logging"],
                    ["chat", "logging"],
                    ["model", "logging"],
                    ["llm", "logging"],
                    ["prompt", "logging"],
                ],
                "sources": {
                    "paths",
                    "functions",
                    "runtime_signals",
                },
            },
            {
                "id": "token_or_latency_metrics",
                "label": "Token, latency, or usage metrics",
                "points": 20,
                "keyword_groups": [
                    ["token", "usage"],
                    ["latency"],
                    ["duration"],
                    ["model", "metrics"],
                    ["usage", "metrics"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
                "context_keywords": [
                    "ai",
                    "llm",
                    "model",
                    "chat",
                    "prompt",
                ],
            },
            {
                "id": "ai_trace",
                "label": "AI runtime trace",
                "points": 20,
                "keyword_groups": [
                    ["runtime", "trace"],
                    ["ai", "trace"],
                    ["chat", "trace"],
                    ["model", "trace"],
                    ["decision", "trace"],
                ],
                "sources": {
                    "paths",
                    "contracts",
                    "functions",
                    "runtime_signals",
                },
            },
            {
                "id": "ai_health",
                "label": "AI health or diagnostics",
                "points": 20,
                "keyword_groups": [
                    ["ai", "health"],
                    ["model", "health"],
                    ["ollama", "health"],
                    ["chat", "health"],
                    ["diagnostic"],
                ],
                "sources": {
                    "paths",
                    "routes",
                    "functions",
                    "runtime_signals",
                },
            },
            {
                "id": "ai_tests",
                "label": "AI integration tests",
                "points": 20,
                "keyword_groups": [
                    ["ai"],
                    ["llm"],
                    ["ollama"],
                    ["chat"],
                    ["model"],
                ],
                "sources": {
                    "tests",
                },
            },
        ],
    },
]


class AICapabilityGrader:
    """
    Grade observable AI capability from existing Phase 135 evidence.
    """

    def __init__(
        self,
        discovery: dict[str, Any],
        layer_mapping: dict[str, Any],
        dependency_mapping: dict[str, Any],
        import_graph: dict[str, Any],
        runtime_graph: dict[str, Any],
        contract_discovery: dict[str, Any],
        fintech_capability: dict[str, Any],
    ) -> None:
        self.discovery = discovery
        self.layer_mapping = layer_mapping
        self.dependency_mapping = dependency_mapping
        self.import_graph = import_graph
        self.runtime_graph = runtime_graph
        self.contract_discovery = contract_discovery
        self.fintech_capability = fintech_capability

        self.evidence = self._build_evidence_index()

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
            "fintech_score_modified": False,
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
                "overall_score_is": "ai_capability_only",
                "overall_score_is_not": [
                    "production_readiness",
                    "production_safety",
                    "model_quality",
                    "financial_advice_quality",
                    "regulatory_compliance",
                    "deployment_approval",
                    "live_trading_approval",
                ],
            },
            "limitations": [
                (
                    "AI capability scores are based on static repository "
                    "evidence and do not prove model quality or runtime behavior."
                ),
                (
                    "The grader does not send prompts, invoke tools, contact "
                    "providers, or execute AI workflows."
                ),
                (
                    "Keyword and structural evidence may identify capability "
                    "surfaces without proving they are complete or correct."
                ),
                (
                    "Production readiness, production blockers, financial "
                    "safety, and regulatory compliance remain ungraded."
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

        evidence = []

        for check in checks:
            evidence.extend(check["evidence"])

        return {
            "category_id": definition["id"],
            "category": definition["category"],
            "score": score,
            "maximum": maximum,
            "percentage": percentage,
            "status": self._status_from_percentage(percentage),
            "checks_passed": sum(
                1
                for check in checks
                if check["passed"]
            ),
            "checks_missing": sum(
                1
                for check in checks
                if not check["passed"]
            ),
            "checks": checks,
            "evidence": self._unique_evidence(evidence)[:50],
            "missing": [
                check["missing"]
                for check in checks
                if not check["passed"]
            ],
            "notes": [
                (
                    "Capability score reflects static evidence only and does "
                    "not represent production readiness or model quality."
                )
            ],
        }

    def _grade_check(
        self,
        check: dict[str, Any],
    ) -> dict[str, Any]:
        maximum = float(check["points"])

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
                    "AI capability signals."
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
                    if all(
                        keyword in haystack
                        for keyword in group
                    ):
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
        evidence: dict[
            str,
            list[dict[str, Any]],
        ] = defaultdict(list)

        for record in self.discovery.get("files", []):
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
                    contract.get("methods"),
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

    @staticmethod
    def _evidence_item(
        source: str,
        text: str,
    ) -> dict[str, Any]:
        return {
            "source": source,
            "text": text,
            "normalized": AICapabilityGrader._normalize(text),
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
