def score_simulation(sim):

    risk = 0
    value = 0

    for level, step in sim["impacts"]:

        if level == "high_risk":
            risk += 3

        if level == "medium_risk":
            risk += 2

        if level == "low_risk":
            value += 1

    return {
        "risk_score": risk,
        "value_score": value,
        "safe_to_execute": risk <= 2
    }
