"""
STACK: strategy

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class StrategyContract:
    """
    Base interface for strategy domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "strategy", "status": "unimplemented"}
