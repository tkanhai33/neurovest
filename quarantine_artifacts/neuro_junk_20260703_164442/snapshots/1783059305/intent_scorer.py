def score_intent(text: str):

    t = text.lower()

    score = {
        "inspect": 0,
        "roadmap": 0,
        "debug": 0,
        "build": 0
    }

    if "system" in t or "architecture" in t:
        score["inspect"] += 3

    if "roadmap" in t or "next" in t:
        score["roadmap"] += 3

    if "error" in t or "broken" in t:
        score["debug"] += 3

    if "build" in t or "create" in t:
        score["build"] += 2

    return score
