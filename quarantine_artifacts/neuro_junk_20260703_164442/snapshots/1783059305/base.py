"""
STACK: snaptrade

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class SnaptradeContract:
    """
    Base interface for snaptrade domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "snaptrade", "status": "unimplemented"}
