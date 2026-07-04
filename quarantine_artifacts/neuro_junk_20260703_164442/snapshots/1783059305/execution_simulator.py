def simulate(plan: list):

    impacts = []

    for step in plan:

        if "system" in step.lower():
            impacts.append(("low_risk", step))

        if "delete" in step.lower() or "modify" in step.lower():
            impacts.append(("high_risk", step))

        if "execution" in step.lower():
            impacts.append(("medium_risk", step))

    return {
        "simulated_steps": len(plan),
        "impacts": impacts
    }
