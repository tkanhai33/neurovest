from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Plan(StrEnum):
    FREE = "free"
    RESEARCH = "research"


class SubscriptionStatus(StrEnum):
    NONE = "none"
    INCOMPLETE = "incomplete"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    CANCELED = "canceled"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


FREE_FEATURES = frozenset({
    "chat",
    "universe.read",
    "universe.configure",
    "analysis.basic",
    "history.basic",
})

PAID_FEATURES = frozenset({
    "analysis.premium",
    "research.comparison",
    "research.extended_history",
    "research.saved_reports",
})

ALL_FEATURES = FREE_FEATURES | PAID_FEATURES

PAID_ELIGIBLE_STATUSES = frozenset({
    SubscriptionStatus.ACTIVE,
    SubscriptionStatus.TRIALING,
})


@dataclass(frozen=True)
class Entitlement:
    owner_subject: str
    plan: Plan = Plan.FREE
    status: SubscriptionStatus = SubscriptionStatus.NONE
    cancel_at_period_end: bool = False

    def __post_init__(self):
        if not isinstance(self.owner_subject, str):
            raise ValueError("owner_subject must be a string")
        if not self.owner_subject.strip():
            raise ValueError("owner_subject is required")
        if not isinstance(self.plan, Plan):
            raise ValueError("plan must be a verified Plan")
        if not isinstance(self.status, SubscriptionStatus):
            raise ValueError("status must be a verified status")

    @property
    def paid_active(self) -> bool:
        return (
            self.plan == Plan.RESEARCH
            and self.status in PAID_ELIGIBLE_STATUSES
        )

    def features(self) -> frozenset[str]:
        if self.paid_active:
            return ALL_FEATURES
        return FREE_FEATURES

    def allows(self, feature: str) -> bool:
        if not isinstance(feature, str):
            return False
        return feature in self.features()


def free_entitlement(owner_subject: str) -> Entitlement:
    return Entitlement(owner_subject=owner_subject)


def require_entitlement(
    entitlement: Entitlement,
    *,
    authenticated_owner_subject: str,
    feature: str,
) -> None:
    """
    Enforce server-side access from a trusted entitlement.

    The caller must load the entitlement from authoritative
    server-side storage, never browser-submitted plan claims.
    """
    if (
        not isinstance(authenticated_owner_subject, str)
        or not authenticated_owner_subject.strip()
        or entitlement.owner_subject != authenticated_owner_subject
    ):
        raise PermissionError("subscription_owner_mismatch")

    if not entitlement.allows(feature):
        raise PermissionError("subscription_feature_denied")
