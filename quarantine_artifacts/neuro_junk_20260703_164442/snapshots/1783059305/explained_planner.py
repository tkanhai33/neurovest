def build_explained_plan(graph, trace):

    steps = []

    for file, imports in graph.items():
        for imp in imports:

            if "L5" in file and "L4" in imp:

                steps.append({
                    "source": file,
                    "target": imp,
                    "change": f"# TODO: refactor {file} to remove dependency on {imp}",
                    "reason": "Layer violation detected",
                    "impact": "Improves architecture boundaries"
                })

    return {
        "what_i_see": list(graph.keys())[:10],
        "steps": steps[:10],
        "approved": False,   # MUST be user-approved
        "why": "Fix cross-layer coupling and enforce architecture rules"
    }
