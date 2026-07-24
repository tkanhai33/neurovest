def redact_secret(
    value: str | None,
) -> str:

    if not value:
        return "<missing>"

    return "<redacted>"
