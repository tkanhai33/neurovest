import os
import ast
from pathlib import Path
from collections import defaultdict
ROOT = Path(__file__).resolve().parents[3]  # /backend/app
class RepoGraph:
    def __init__(self):
        self.forward = defaultdict(set)   # file -> imports
        self.reverse = defaultdict(set)   # import -> files
    def scan_py_file(self, path: Path):
        try:
            tree = ast.parse(path.read_text())
        except Exception:
            return
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    self._add(path, n.name)
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    self._add(path, node.module)
    def _add(self, file, module):
        file = str(file.relative_to(ROOT))
        self.forward[file].add(module)
        self.reverse[module].add(file)
    def build(self):
        for path in ROOT.rglob("*.py"):
            self.scan_py_file(path)
    def summary(self):
        return {
        }
def run_scan():
    g = RepoGraph()
    g.build()
    return g.summary(), g.forward, g.reverse
