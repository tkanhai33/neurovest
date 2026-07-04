"""
STACK: portfolio

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class PortfolioContract:
    """
    Base interface for portfolio domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "portfolio", "status": "unimplemented"}
