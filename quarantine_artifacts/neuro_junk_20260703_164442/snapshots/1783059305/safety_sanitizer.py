def sanitize_script(script: str):

    banned_patterns = [
        "curl http://localhost",
        "curl http://127.0.0.1",
        "requests.post(http",
        "rm -rf",
        "os.system",
    ]

    cleaned = script

    for pattern in banned_patterns:
        if pattern in cleaned:
            cleaned = cleaned.replace(pattern, "# REMOVED UNSAFE OPERATION")

    return cleaned
