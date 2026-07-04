"""DOMAIN_LOGIC_V1 kill switch guard."""

_KILL_SWITCH = False


def set_kill_switch(active: bool) -> dict:
    global _KILL_SWITCH
    _KILL_SWITCH = bool(active)
    return {"kill_switch_active": _KILL_SWITCH}


def is_kill_switch_active() -> bool:
    return _KILL_SWITCH
