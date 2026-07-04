def build_plan(trace):

    steps = []

    for t in trace[:30]:

        steps.append({
            "action": "analyze_dependency",
            "source": t.source,
            "target": t.target,
            "risk": "unknown_coupling",
            "reason": t.issue
        })

    return {
        "goal": "stabilize architecture",
        "steps": steps,
        "approval_required": True
    }
