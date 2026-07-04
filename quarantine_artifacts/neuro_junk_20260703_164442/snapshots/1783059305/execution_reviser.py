def revise(plan, score):

    if score["safe_to_execute"]:
        return plan

    revised = []

    for step in plan:
        if "delete" not in step.lower():
            revised.append(step)

    return revised
