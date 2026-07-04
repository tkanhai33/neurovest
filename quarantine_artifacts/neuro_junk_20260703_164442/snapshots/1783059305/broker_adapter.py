"""
L0 BROKER ADAPTER

EXTERNAL SYSTEM INTERFACE ONLY
"""

class BrokerAdapter:

    def send_order(self, order: dict):
        raise RuntimeError("NOT IMPLEMENTED - EXTERNAL SYSTEM")
