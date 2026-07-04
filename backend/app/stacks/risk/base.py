"""
STACK: risk

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class RiskContract:
    """
    Base interface for risk domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "risk", "status": "unimplemented"}
