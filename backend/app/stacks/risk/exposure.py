"""DOMAIN_LOGIC_V1 exposure calculation."""


def calculate_exposure(positions: list[dict]) -> dict:
    gross = 0.0
    for p in positions:
        gross += abs(float(p.get("quantity", 0)) * float(p.get("price", 0)))
    return {"gross_exposure": gross, "position_count": len(positions)}
