def create_plan(issues):

    steps = []

    for i in issues:

        steps.append({
            "action": "refactor",
            "target": i["file"],
            "reason": i["type"],
            "impact": "reduce coupling",
            "risk": i["severity"]
        })

    return {
        "goal": "stabilize architecture",
        "steps": steps,
        "approved": False
    }
