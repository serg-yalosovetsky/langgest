from __future__ import annotations

import logging
from dataclasses import dataclass

from app.nlu.intent import Intent, RiskLevel

logger = logging.getLogger(__name__)

# Intent id prefix -> RiskLevel (evaluated in order, longest prefix wins)
_RISK_TABLE: list[tuple[str, RiskLevel]] = [
    # Forbidden
    ("system.format", RiskLevel.FORBIDDEN),
    ("system.destroy", RiskLevel.FORBIDDEN),
    # Dangerous
    ("shell.execute", RiskLevel.DANGEROUS),
    ("system.", RiskLevel.DANGEROUS),
    # Medium
    ("shell.insert", RiskLevel.MEDIUM),
    ("browser.close", RiskLevel.MEDIUM),
    ("clipboard.", RiskLevel.MEDIUM),
    ("window.close", RiskLevel.MEDIUM),
    # Safe
    ("volume.", RiskLevel.SAFE),
    ("media.", RiskLevel.SAFE),
    ("browser.", RiskLevel.SAFE),
    ("window.", RiskLevel.SAFE),
    ("action.", RiskLevel.SAFE),
    ("macro.", RiskLevel.SAFE),
    ("gesture.", RiskLevel.SAFE),
    ("shell.clear", RiskLevel.SAFE),
    ("shell.stop", RiskLevel.SAFE),
    ("shell.last", RiskLevel.SAFE),
]

MEDIUM_CONFIDENCE_THRESHOLD = 0.80


@dataclass
class PolicyDecision:
    allowed: bool
    requires_confirmation: bool
    risk_level: RiskLevel
    reason: str = ""


class SafetyPolicy:
    def __init__(self, require_confirmation_for_dangerous: bool = True) -> None:
        self._require_confirmation = require_confirmation_for_dangerous

    def evaluate(self, intent: Intent) -> PolicyDecision:
        risk = self._classify_risk(intent.id)

        if risk == RiskLevel.FORBIDDEN:
            return PolicyDecision(
                allowed=False,
                requires_confirmation=False,
                risk_level=risk,
                reason=f"Intent {intent.id!r} is forbidden",
            )

        if risk == RiskLevel.DANGEROUS:
            if self._require_confirmation:
                return PolicyDecision(
                    allowed=False,
                    requires_confirmation=True,
                    risk_level=risk,
                    reason="Dangerous command requires confirmation",
                )
            return PolicyDecision(allowed=True, requires_confirmation=False, risk_level=risk)

        if risk == RiskLevel.MEDIUM:
            if intent.confidence < MEDIUM_CONFIDENCE_THRESHOLD:
                return PolicyDecision(
                    allowed=False,
                    requires_confirmation=True,
                    risk_level=risk,
                    reason=f"Low confidence ({intent.confidence:.2f}) for medium-risk command",
                )
            return PolicyDecision(allowed=True, requires_confirmation=False, risk_level=risk)

        # SAFE
        return PolicyDecision(allowed=True, requires_confirmation=False, risk_level=risk)

    @staticmethod
    def _classify_risk(intent_id: str) -> RiskLevel:
        for prefix, level in _RISK_TABLE:
            if intent_id.startswith(prefix):
                return level
        return RiskLevel.MEDIUM
