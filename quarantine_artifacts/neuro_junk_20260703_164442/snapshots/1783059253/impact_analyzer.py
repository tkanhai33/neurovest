def analyze_impact(diff):

    impact = {
        "risk_level": "low",
        "critical_changes": []
    }

    for item in diff["removed"]:
        if "L4" in item or "execution" in item:
            impact["risk_level"] = "high"
            impact["critical_changes"].append(item)

        if "L1" in item or "security" in item:
            impact["risk_level"] = "critical"
            impact["critical_changes"].append(item)

    for item in diff["added"]:
        if "runtime" in item:
            impact["risk_level"] = "medium"

    return impact
