from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from backend.app.stacks.db_model.strategy_knowledge import StrategyKnowledge
from backend.app.stacks.strategy_candidate_sandbox.legacy_frozen25_identity import (
    LEGACY_FROZEN25_IDENTITY_TYPE,
    legacy_frozen25_strategy_fingerprint,
    validate_legacy_frozen25_identity,
)
PROVEN_DIRECT_FIELDS = {'asset_class', 'created_at', 'name', 'strategy_family', 'symbols'}

def map_runtime_candidate_to_strategy_knowledge(candidate: Mapping[str, Any]) -> StrategyKnowledge:
    if candidate.get("identity_type") == LEGACY_FROZEN25_IDENTITY_TYPE:
        if not validate_legacy_frozen25_identity(candidate):
            raise ValueError("Invalid legacy Frozen25 identity.")

        values = {
            name: candidate[name]
            for name in PROVEN_DIRECT_FIELDS
            if name in candidate
            and name != "name"
        }

        values["strategy_id"] = str(
            candidate["candidate_id"]
        )

        values["strategy_fingerprint"] = (
            legacy_frozen25_strategy_fingerprint(
                candidate
            )
        )

        return StrategyKnowledge(
            **values,
            name=str(
                candidate["strategy_name"]
            ),
            strategy_name=str(
                candidate["strategy_name"]
            ).strip(),
        )

    required = ('candidate_id', 'contract_hash', 'strategy_name')
    missing = [name for name in required if not candidate.get(name)]
    if missing:
        raise ValueError('Runtime candidate missing required identity fields: ' + repr(missing))
    values = {name: candidate[name] for name in PROVEN_DIRECT_FIELDS if name in candidate}
    values['strategy_id'] = str(candidate['candidate_id'])
    values['strategy_fingerprint'] = str(candidate['contract_hash'])
    return StrategyKnowledge(**values, name=candidate['strategy_name'],
        strategy_name=(
            str(
                candidate.get("strategy_name")
                or ""
            ).strip()
        ),
    )
