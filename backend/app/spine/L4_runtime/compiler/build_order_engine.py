from __future__ import annotations
from collections import defaultdict, deque
from spine.L4_runtime.dependency_graph_engine import build_dependency_graph
def compute_build_order(limit: int = 1000) -> dict:
    deps = build_dependency_graph(limit=limit)["graph"]
    indegree = defaultdict(int)
    reverse_graph = defaultdict(list)
    # Build reverse dependency graph
    for node, children in deps.items():
        for child in children:
            reverse_graph[child].append(node)
            indegree[node] += 1
    # Start with nodes that have no dependencies
    queue = deque([n for n in deps if indegree[n] == 0])
    order = []
    visited = set()
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for parent in reverse_graph[node]:
            indegree[parent] -= 1
            if indegree[parent] == 0:
                queue.append(parent)
    return {
    }
