from backend.app.stacks.strategy.evaluators.aggregation import QUALIFIED_AGGREGATION_NAME_SET
from backend.app.stacks.strategy.evaluators.multi_symbol_family_v1 import MULTI_SYMBOL_STRATEGY_NAMES
from backend.app.stacks.strategy.evaluators.registry import ALLOWLISTED_EVALUATORS

def test_exact_one_hundred_thirty_three_capabilities():
    assert len(ALLOWLISTED_EVALUATORS) == 133
    assert len(QUALIFIED_AGGREGATION_NAME_SET) == 133
    assert tuple(ALLOWLISTED_EVALUATORS)[-4:] == MULTI_SYMBOL_STRATEGY_NAMES
