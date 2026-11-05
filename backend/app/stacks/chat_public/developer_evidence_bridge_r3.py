from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path

R2_SHA256 = (
    "78454f95ed182a8a422277559bc626388e2884927393522dd06971b855698a3c"
)


PINNED_REGISTRY_SHA256 = "aff7ade08f37f67283fb0085991696306a5255d6eacc07cbcbdbdbad14e453a1"

class EvidenceIntegrityError(ValueError):
    pass

IMPROVEMENT_RE = re.compile(
    r"(?:what\s+do\s+you\s+need\s+to\s+improve|"
    r"what\s+should\s+you\s+improve|"
    r"your\s+(?:development|engineering)\s+priorities|"
    r"assess\s+your\s+(?:development|engineering)\s+gaps)",
    re.IGNORECASE,
)

def load_adapter(path: Path):
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError("Trusted adapter missing")

    if hashlib.sha256(path.read_bytes()).hexdigest() != R2_SHA256:
        raise ValueError("Trusted adapter hash mismatch")

    spec = importlib.util.spec_from_file_location(
        "neurovest_trusted_evidence_adapter_r2",
        path,
    )
    if spec is None or spec.loader is None:
        raise ValueError("Adapter import unavailable")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def assess(
    *,
    message: str,
    principal: object,
    root: Path,
    adapter_path: Path,
    registry_path: Path,
    trusted_role_guard,
) -> dict:
    # These inputs are supplied by authenticated server code,
    # never from model output or client-provided developer flags.
    if not callable(trusted_role_guard):
        raise ValueError("Trusted role guard required")

    if not isinstance(message, str) or not IMPROVEMENT_RE.search(message):
        return {"status": "not_applicable", "answer": None}

    # Authorization precedes registry access.
    verified = trusted_role_guard(principal)

    if type(verified) is not bool or not verified:
        return {
            "status": "denied",
            "answer": None,
            "reason": "verified_developer_required",
        }

    # R11 — Reject modified evidence before loading or classifying it.
    registry_file = Path(registry_path)

    if registry_file.is_symlink() or not registry_file.is_file():
        raise EvidenceIntegrityError("Evidence file unavailable")

    registry_root = Path(root).resolve(strict=True)
    expected_registry = (
        registry_root
        / "runtime/qualification/"
        "neuro_evidence_registry_R1_20261015T235246Z/"
        "capability_registry.json"
    ).resolve(strict=True)

    if registry_file.resolve(strict=True) != expected_registry:
        raise EvidenceIntegrityError("Untrusted registry location")

    registry_bytes = registry_file.read_bytes()

    if not 0 < len(registry_bytes) <= 2_000_000:
        raise EvidenceIntegrityError("Invalid registry size")

    if hashlib.sha256(registry_bytes).hexdigest() != PINNED_REGISTRY_SHA256:
        raise EvidenceIntegrityError("Registry integrity mismatch")

    adapter = load_adapter(adapter_path)
    registry = adapter.load_registry(registry_file, root)
    classified = adapter.classify(registry, root)

    if not classified:
        return {
            "status": "evidence_unavailable",
            "answer": None,
        }

    result = adapter.generate_assessment(
        classified,
        verified_developer=True,
    )

    if result.get("status") != "ok":
        return {
            "status": "evidence_unavailable",
            "answer": None,
        }

    return {
        "status": "ok",
        "answer": result["answer"],
        "recommendations": result["recommendations"],
        "evidence_scope": "offline_qualification_registry",
        "read_only": True,
        "production_approval_granted": False,
        "broker_execution_allowed": False,
    }



# NeuroVest functional improvement intelligence F1.
# The original R24 bridge retains authority over the
# evidence-assessment result and developer-only routing.

_neuro_r24_assess = assess

def assess(**kwargs):
    """
    Developer evidence assessment with supplemental
    improvement intelligence.

    Authorization remains with the existing R24 caller.
    This function never upgrades a denied or unsuccessful
    result into a successful result.
    """
    original_result = _neuro_r24_assess(**kwargs)

    if not isinstance(original_result, dict):
        return original_result

    if original_result.get("status") != "ok":
        return original_result

    original_answer = original_result.get("answer")

    if not isinstance(original_answer, str):
        return original_result

    try:
        import importlib.util
        from pathlib import Path

        directory = Path(__file__).resolve().parent

        def load_component(filename, name):
            allowed = {
                "neuro_improvement_intelligence_v1.py",
                "neuro_improvement_backlog_v1.py",
            }

            if filename not in allowed:
                raise ValueError("Component not allowlisted")

            path = directory / filename

            if not path.is_file() or path.is_symlink():
                raise FileNotFoundError(
                    "Improvement component unavailable"
                )

            spec = importlib.util.spec_from_file_location(
                name, path
            )

            if spec is None or spec.loader is None:
                raise ImportError("Component loader unavailable")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        intelligence = load_component(
            "neuro_improvement_intelligence_v1.py",
            "neuro_f7_improvement_intelligence",
        )

        backlog_engine = load_component(
            "neuro_improvement_backlog_v1.py",
            "neuro_f7_improvement_backlog",
        )

        # Server-controlled application root.
        # Never accept this path from chat text or metadata.
        app_root = Path(kwargs["root"]).resolve(strict=True)

        assessment = intelligence.assess_developer_improvements(
            app_root
        )

        report = assessment["report"]

        plan = backlog_engine.reconcile(report)

        # Include the actual new priorities, not only the
        # historical F4 recommendation text.
        additional = [
            "NEURO SELF-IMPROVEMENT ASSESSMENT",
            "",
            assessment["answer"],
            "",
            "CURRENT DEVELOPMENT BACKLOG",
            backlog_engine.render(plan, limit=8),
        ]

        # Keep output bounded and avoid changing persistence
        # schemas or returning internal objects in API fields.
        extra = "\n".join(additional)

        if len(extra) > 24000:
            extra = extra[:24000] + (
                "\n[Additional improvement details omitted]"
            )

        result = dict(original_result)

        result["answer"] = (
            original_answer
            + "\n\n"
            + extra
        )

        return result

    except Exception:
        # Supplemental intelligence cannot bypass the
        # original evidence and authorization result.
        return original_result

