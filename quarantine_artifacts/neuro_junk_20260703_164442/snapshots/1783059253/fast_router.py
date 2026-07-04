def fast_path(user_input: str):

    q = user_input.lower()

    if "system tree" in q or "structure" in q:
        return {"type": "fast", "result": "Use cached graph view"}
    
    if "status" in q:
        return {"type": "fast", "result": "System OK (cached state)"}

    if "files" in q:
        return {"type": "fast", "result": "Use dependency graph only"}

    return None
