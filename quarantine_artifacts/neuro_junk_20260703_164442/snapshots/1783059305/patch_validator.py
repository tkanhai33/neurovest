def validate_patch(patch: dict):

    forbidden = [
        "delete spine",
        "remove security",
        "disable validation",
        "bypass risk",
        "execute shell"
    ]

    patch_str = str(patch).lower()

    for rule in forbidden:
        if rule in patch_str:
            return {
                "valid": False,
                "reason": f"forbidden operation detected: {rule}"
            }

    return {
        "valid": True,
        "reason": "safe patch"
    }
