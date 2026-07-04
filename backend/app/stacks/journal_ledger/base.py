"""
STACK: journal_ledger

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class Journal_ledgerContract:
    """
    Base interface for journal_ledger domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "journal_ledger", "status": "unimplemented"}
