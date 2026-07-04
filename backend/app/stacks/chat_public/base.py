"""
STACK: chat_public

CORE CONTRACT LAYER
DO NOT ADD BUSINESS LOGIC HERE
"""

class Chat_publicContract:
    """
    Base interface for chat_public domain.
    """

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def health(self):
        return {"stack": "chat_public", "status": "unimplemented"}
