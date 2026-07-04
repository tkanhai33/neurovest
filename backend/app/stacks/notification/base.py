"""
STACK: notification

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class NotificationContract:
    """
    Base interface for notification domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "notification", "status": "unimplemented"}
