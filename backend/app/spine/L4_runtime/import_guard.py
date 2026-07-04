from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_PATTERNS = [
    ("L4_runtime", "L3_facade"),
    ("L4_runtime", "L5_api"),
    ("L3_facade", "L5_api")
]
def scan():
    violations = []
    for f in ROOT.rglob("*.py"):
        text = f.read_text(errors="ignore")
        for a, b in FORBIDDEN_PATTERNS:
            if a in str(f) and b in text:
                violations.append(str(f))
    return violations
def assert_clean_import_graph():
    v = scan()
    if v:
        msg = "\n".join(v)
        raise ImportError(f"ARCHITECTURE LOCK VIOLATION:\n{msg}")
if __name__ == "__main__":
    assert_clean_import_graph()
    print("IMPORT GRAPH CLEAN")
