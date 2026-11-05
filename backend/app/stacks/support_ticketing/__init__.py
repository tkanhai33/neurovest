"""
Canonical NeuroVest support-ticketing stack.
"""

from backend.app.stacks.support_ticketing.models import (
    SupportTicket,
    SupportTicketMessage,
)

__all__ = [
    "SupportTicket",
    "SupportTicketMessage",
]
