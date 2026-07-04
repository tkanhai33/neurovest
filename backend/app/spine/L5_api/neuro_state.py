from dataclasses import dataclass
@dataclass
class NeuroState:
    last_plan: dict | None = None
    last_action: dict | None = None
    awaiting_approval: bool = False
STATE = NeuroState()
