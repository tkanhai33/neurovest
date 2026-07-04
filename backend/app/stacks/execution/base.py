"""
STACK: execution

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class ExecutionContract:
    """
    Base interface for execution domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "execution", "status": "unimplemented"}
