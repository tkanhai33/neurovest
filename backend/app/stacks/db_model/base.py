"""
STACK: db_model

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class Db_modelContract:
    """
    Base interface for db_model domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "db_model", "status": "unimplemented"}
