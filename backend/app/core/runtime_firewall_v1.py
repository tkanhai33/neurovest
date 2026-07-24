import sys
import inspect
from pathlib import Path

ROOT = Path(".").resolve()

# ================================
# LAYER RULES (RUNTIME ENFORCEMENT)
# ================================

RUNTIME_RULES = {
    "L0": ["strategy", "risk", "portfolio"],
    "L1": ["execution", "broker", "snaptrade"],
    "L2": ["fastapi", "uvicorn"],
    "L3": ["strategy", "risk", "market_data"],
}


def detect_call_stack():
    stack = inspect.stack()
    return [frame.filename for frame in stack]


def classify_layer(path: str) -> str:
    p = path.lower()

    if "stacks" in p:
        return "L2"

    if "routers" in p or "api" in p:
        return "L3"

    if "core" in p:
        return "L1"

    return "L2"


def check_runtime_violation(caller_file: str, imported_module: str):

    layer = classify_layer(caller_file)

    forbidden = RUNTIME_RULES.get(layer, [])

    for f in forbidden:
        if f in imported_module:

            raise RuntimeError(
                f"""
🚨 RUNTIME ARCHITECTURE VIOLATION

File: {caller_file}
Layer: {layer}
Forbidden Access: {imported_module}

This violates NeuroVest architecture boundaries.
Execution halted.
"""
            )


# ================================
# SAFE IMPORT WRAPPER
# ================================

def safe_import(module_name: str):
    caller = inspect.stack()[1].filename
    check_runtime_violation(caller, module_name)
    return __import__(module_name)
