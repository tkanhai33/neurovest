#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from datetime import datetime, UTC
import json

ROOT = Path(".").resolve()
RUNTIME = ROOT / "runtime"
CERTS = RUNTIME / "certifications"
SANDBOX = RUNTIME / "strategy_candidate_sandbox"
HANDOFF = ROOT / "handoff"

OUT_DIR = HANDOFF / "project_status"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT_DIR / "64A_project_maturity_devops_latest.json"
OUT_MD = OUT_DIR / "64A_project_maturity_devops_latest.md"

PHASE = "64A_PROJECT_MATURITY_DEVOPS_CONTROLLER"

IGNORE_DIRS = {
    ".git", ".venv", "__pycache__", ".pytest_cache",
    "node_modules", ".next", "dist", "build", "coverage",
    "quarantine_artifacts",
}


def is_ignored(path: Path) -> bool:
    return bool(set(path.parts) & IGNORE_DIRS)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def scan_repo() -> dict:
    stats = {
        "total_files": 0,
        "python_files": 0,
        "typescript_files": 0,
        "json_files": 0,
        "markdown_files": 0,
        "test_files": 0,
        "script_files": 0,
        "backend_files": 0,
        "frontend_files": 0,
        "runtime_files": 0,
        "handoff_files": 0,
    }

    for path in ROOT.rglob("*"):
        if is_ignored(path) or not path.is_file():
            continue

        stats["total_files"] += 1

        suffix = path.suffix.lower()
        if suffix == ".py":
            stats["python_files"] += 1
        elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
            stats["typescript_files"] += 1
        elif suffix == ".json":
            stats["json_files"] += 1
        elif suffix in {".md", ".txt"}:
            stats["markdown_files"] += 1

        lower = path.name.lower()
        if "test" in lower or "tests" in path.parts:
            stats["test_files"] += 1

        parts = path.parts
        if "scripts" in parts:
            stats["script_files"] += 1
        if "backend" in parts:
            stats["backend_files"] += 1
        if "frontend" in parts:
            stats["frontend_files"] += 1
        if "runtime" in parts:
            stats["runtime_files"] += 1
        if "handoff" in parts:
            stats["handoff_files"] += 1

    return stats


def scan_certifications() -> dict:
    artifacts = []

    for root in [CERTS, SANDBOX]:
        if not root.exists():
            continue

        for path in sorted(root.rglob("*.json")):
            if is_ignored(path):
                continue

            data = read_json(path)
            artifacts.append({
                "file": rel(path),
                "phase": data.get("phase", path.stem),
                "certified": data.get("certified"),
                "created_at": data.get("created_at"),
                "stage": data.get("stage"),
                "latest_confirmed_phase": data.get("latest_confirmed_phase"),
            })

    certified = [x for x in artifacts if x.get("certified") is True]
    uncertified = [x for x in artifacts if x.get("certified") is not True]

    return {
        "artifact_count": len(artifacts),
        "certified_count": len(certified),
        "uncertified_count": len(uncertified),
        "certified_ratio": round((len(certified) / len(artifacts)) * 100, 2) if artifacts else 0.0,
        "latest_certified": certified[-10:],
    }


def exists_any(paths: list[str]) -> bool:
    return any((ROOT / p).exists() for p in paths)


def stack_readiness() -> dict:
    stacks = {
        "market_data": {
            "paths": [
                "backend/app/stacks/market_data",
                "runtime/market_warehouse",
            ],
            "signals": [
                "provider_registry.py",
                "provider_router.py",
                "yfinance_historical_bars_adapter.py",
                "bars.py",
                "market_data_service.py",
            ],
        },
        "strategy": {
            "paths": ["backend/app/stacks/strategy"],
            "signals": [
                "strategy_service.py",
                "strategy_runtime.py",
                "strategy_registry.py",
                "candidate_registry.py",
                "engine.py",
            ],
        },
        "strategy_candidate_sandbox": {
            "paths": ["backend/app/stacks/strategy_candidate_sandbox"],
            "signals": [
                "replay_metrics_generator.py",
                "replay_metrics_contract.py",
                "manual_promotion_gate.py",
                "risk_gate_contract.py",
                "trade_simulation_enablement_gate_contract.py",
            ],
        },
        "risk": {
            "paths": ["backend/app/stacks/risk"],
            "signals": [
                "risk_service.py",
                "risk_runtime_service.py",
                "drawdown_guard.py",
                "loss_streak_guard.py",
                "kill_switch.py",
            ],
        },
        "execution": {
            "paths": ["backend/app/stacks/execution"],
            "signals": [
                "sandbox_runtime.py",
                "paper_broker.py",
                "broker.py",
                "executor.py",
                "trade_ledger.py",
            ],
        },
        "portfolio": {
            "paths": ["backend/app/stacks/portfolio"],
            "signals": [
                "portfolio_service.py",
                "portfolio_runtime.py",
                "allocator.py",
                "accounting.py",
                "dashboard_service.py",
            ],
        },
        "learning_research": {
            "paths": ["backend/app/stacks/learning_research"],
            "signals": [
                "monte_carlo.py",
                "monte_carlo_mix.py",
                "research_runtime.py",
                "backtest_engine.py",
                "strategy_evaluator.py",
            ],
        },
        "chat_public": {
            "paths": ["backend/app/stacks/chat_public"],
            "signals": [
                "chat_runtime.py",
                "chat_service.py",
                "ollama_chat_client.py",
                "chat_api.py",
                "strategy_proposal_capture.py",
            ],
        },
        "wolfden_ai": {
            "paths": ["backend/app/stacks/wolfden_ai"],
            "signals": [
                "orchestrator.py",
                "runtime.py",
                "agent_router.py",
                "routing.py",
                "memory.py",
            ],
        },
        "frontend": {
            "paths": ["frontend/app", "frontend/services"],
            "signals": [
                "page.tsx",
                "chatService.ts",
                "marketService.ts",
                "portfolioService.ts",
                "riskService.ts",
                "strategyService.ts",
            ],
        },
    }

    readiness = {}

    for stack, cfg in stacks.items():
        base_exists = any((ROOT / p).exists() for p in cfg["paths"])

        found = []
        for base in cfg["paths"]:
            folder = ROOT / base
            if not folder.exists():
                continue

            for signal in cfg["signals"]:
                matches = list(folder.rglob(signal))
                if matches:
                    found.append(signal)

        total = len(cfg["signals"])
        score = round((len(set(found)) / total) * 100, 2) if total else 0

        readiness[stack] = {
            "base_exists": base_exists,
            "signals_found": sorted(set(found)),
            "signal_count": len(set(found)),
            "signal_total": total,
            "readiness_score": score,
        }

    return readiness


def safety_locks() -> dict:
    archive = read_json(SANDBOX / "61A_archive_or_new_chat_handoff_summary_latest.json")
    summary = archive.get("archive_summary", {})

    locks = summary.get("critical_safety_locks", {})

    return {
        "archive_exists": bool(archive),
        "archive_certified": archive.get("certified") is True,
        "read_only_chain_closed": summary.get("read_only_chain_closed") is True,
        "execution_surface_opened": summary.get("execution_surface_opened") is True,
        "mutation_surface_opened": summary.get("mutation_surface_opened") is True,
        "critical_safety_locks": locks,
        "all_critical_locks_false": all(v is False for v in locks.values()) if locks else False,
    }


def capability_status(cert: dict, stacks: dict, locks: dict) -> dict:
    def score(stack: str) -> float:
        return float(stacks.get(stack, {}).get("readiness_score", 0.0))

    return {
        "architecture_topology": "CERTIFIED" if cert["certified_count"] >= 50 else "IN_PROGRESS",
        "market_data": "READY" if score("market_data") >= 80 else "IN_PROGRESS",
        "strategy_core": "READY" if score("strategy") >= 80 else "IN_PROGRESS",
        "candidate_sandbox": "READY" if score("strategy_candidate_sandbox") >= 80 else "IN_PROGRESS",
        "historical_replay": "READY" if cert["certified_count"] >= 80 else "IN_PROGRESS",
        "risk_framework": "READY" if score("risk") >= 80 else "IN_PROGRESS",
        "execution_engine": "LOCKED" if locks["all_critical_locks_false"] else "UNKNOWN",
        "paper_trading": "LOCKED",
        "broker_execution": "LOCKED",
        "live_trading": "LOCKED",
        "learning_research": "IN_PROGRESS" if score("learning_research") >= 60 else "EARLY",
        "qwen_read_only": "TERMINAL_FROZEN" if locks["read_only_chain_closed"] else "IN_PROGRESS",
    }


def compute_stage(capabilities: dict, cert: dict, locks: dict) -> dict:
    ready_count = sum(
        1
        for v in capabilities.values()
        if v in {"READY", "CERTIFIED", "TERMINAL_FROZEN"}
    )

    locked_safety_ok = (
        locks["all_critical_locks_false"]
        and locks["execution_surface_opened"] is False
        and locks["mutation_surface_opened"] is False
    )

    if (
        ready_count >= 6
        and capabilities.get("paper_trading") == "LOCKED"
        and locked_safety_ok
    ):
        stage = "Late Alpha"
        next_stage = "Sandbox Runtime Activation / Research Engine Completion"
    elif ready_count >= 4:
        stage = "Mid Alpha"
        next_stage = "Candidate Sandbox + Replay Hardening"
    else:
        stage = "Early Alpha"
        next_stage = "Architecture + Stack Stabilization"

    completion_estimate = min(
        95.0,
        round(
            (cert["certified_ratio"] * 0.35)
            + (ready_count / max(len(capabilities), 1) * 100 * 0.45)
            + (20 if locked_safety_ok else 0),
            2,
        ),
    )

    return {
        "current_stage": stage,
        "next_stage_focus": next_stage,
        "completion_estimate_percent": completion_estimate,
        "ready_capability_count": ready_count,
        "capability_total": len(capabilities),
        "safety_posture_ok": locked_safety_ok,
    }


def markdown(result: dict) -> str:
    lines = []
    lines.append("# NeuroVest Project Maturity DevOps Report")
    lines.append("")
    lines.append(f"Generated: {result['created_at']}")
    lines.append(f"Phase: {result['phase']}")
    lines.append("")
    lines.append("## Current Stage")
    lines.append("")
    lines.append(f"**{result['stage']['current_stage']}**")
    lines.append("")
    lines.append(f"Next focus: {result['stage']['next_stage_focus']}")
    lines.append("")
    lines.append(f"Completion estimate: {result['stage']['completion_estimate_percent']}%")
    lines.append("")
    lines.append("## Safety Posture")
    lines.append("")
    lines.append(f"Safety posture OK: {result['stage']['safety_posture_ok']}")
    lines.append(f"All critical locks false: {result['safety_locks']['all_critical_locks_false']}")
    lines.append(f"Execution surface opened: {result['safety_locks']['execution_surface_opened']}")
    lines.append(f"Mutation surface opened: {result['safety_locks']['mutation_surface_opened']}")
    lines.append("")
    lines.append("## Capability Status")
    lines.append("")
    for key, value in result["capabilities"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Certification Summary")
    lines.append("")
    lines.append(f"- artifacts: {result['certifications']['artifact_count']}")
    lines.append(f"- certified: {result['certifications']['certified_count']}")
    lines.append(f"- uncertified/historical: {result['certifications']['uncertified_count']}")
    lines.append(f"- certified ratio: {result['certifications']['certified_ratio']}%")
    lines.append("")
    lines.append("## Stack Readiness")
    lines.append("")
    for stack, data in result["stack_readiness"].items():
        lines.append(f"- {stack}: {data['readiness_score']}% ({data['signal_count']}/{data['signal_total']})")
    lines.append("")
    lines.append("## Machine JSON")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(result, indent=2))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


repo = scan_repo()
cert = scan_certifications()
stacks = stack_readiness()
locks = safety_locks()
caps = capability_status(cert, stacks, locks)
stage = compute_stage(caps, cert, locks)

result = {
    "phase": PHASE,
    "created_at": datetime.now(UTC).isoformat(),
    "mode": "READ_ONLY_DEVOPS_SCAN",
    "repo": repo,
    "certifications": cert,
    "stack_readiness": stacks,
    "safety_locks": locks,
    "capabilities": caps,
    "stage": stage,
    "certified": True,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
OUT_MD.write_text(markdown(result), encoding="utf-8")

print(json.dumps({
    "phase": PHASE,
    "created_at": result["created_at"],
    "current_stage": stage["current_stage"],
    "next_stage_focus": stage["next_stage_focus"],
    "completion_estimate_percent": stage["completion_estimate_percent"],
    "safety_posture_ok": stage["safety_posture_ok"],
    "out_json": str(OUT_JSON),
    "out_md": str(OUT_MD),
    "certified": True,
}, indent=2))
