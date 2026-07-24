import sys
import importlib.abc
import importlib.util
from pathlib import Path

ROOT = Path(".").resolve()


# ============================
# LAYER RULES (GLOBAL ENFORCEMENT)
# ============================

RULES = {
    "L0": ["strategy", "risk", "portfolio"],
    "L1": ["execution", "snaptrade", "broker"],
    "L2": ["fastapi", "uvicorn"],
    "L3": ["strategy", "risk", "market_data"],
}


def detect_layer(import_name: str) -> str:

    name = import_name.lower()

    if "stacks" in name:
        return "L2"

    if "routers" in name or "api" in name:
        return "L3"

    if "core" in name:
        return "L1"

    return "L2"


def check_violation(layer: str, module: str):

    forbidden = RULES.get(layer, [])

    for f in forbidden:
        if f in module:
            raise ImportError(
                f"""
🚨 GLOBAL ARCHITECTURE VIOLATION

Layer: {layer}
Module: {module}
Violation: forbidden cross-layer dependency

System halted by Global Firewall.
"""
            )


# ============================
# IMPORT HOOK
# ============================

class ArchitectureImportHook(importlib.abc.MetaPathFinder):

    def find_spec(self, fullname, path, target=None):
        # PHASE136_EXTERNAL_DEPENDENCY_BYPASS
        # The architecture firewall governs NeuroVest imports only.
        # Standard-library and third-party packages must remain outside
        # the internal L0-L7 dependency graph.
        internal_roots = {
            "backend",
            "app",
            "spine",
            "stacks",
            "core",
            "llm_bridge",
            "services",
            "domain",
            "adapters",
            "repositories",
            "facades",
            "models",
            "security",
            "tests",
        }
        module_root = fullname.split(".", 1)[0]
        if module_root not in internal_roots:
            return None


        layer = detect_layer(fullname)

        check_violation(layer, fullname)

        return None  # allow normal import to continue


# ============================
# INSTALL FIREWALL
# ============================

def install_global_firewall():
    sys.meta_path.insert(0, ArchitectureImportHook())
    print("🧠 GLOBAL ARCHITECTURE FIREWALL ACTIVE")
