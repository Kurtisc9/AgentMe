from dataclasses import dataclass
from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(slots=True)
class RoutedTask:
    description: str
    assigned_agent: str
    risk_level: RiskLevel
    approval_required: bool
    blocked: bool
    reason: str


class SageCommander:
    """Minimal first-pass task router for Sage."""

    def route_task(self, description: str) -> RoutedTask:
        text = description.strip().lower()

        if not text:
            raise ValueError("Task description cannot be empty.")

        if any(term in text for term in ("trade", "transfer money", "share password", "delete critical")):
            return RoutedTask(
                description=description,
                assigned_agent="Sage Commander",
                risk_level=RiskLevel.HIGH,
                approval_required=False,
                blocked=True,
                reason="High-risk action is blocked.",
            )

        if any(term in text for term in ("edit file", "run script", "send email", "modify database")):
            return RoutedTask(
                description=description,
                assigned_agent=self._select_agent(text),
                risk_level=RiskLevel.MEDIUM,
                approval_required=True,
                blocked=False,
                reason="Medium-risk action requires KurtisC approval.",
            )

        return RoutedTask(
            description=description,
            assigned_agent=self._select_agent(text),
            risk_level=RiskLevel.LOW,
            approval_required=False,
            blocked=False,
            reason="Safe planning or analysis task.",
        )

    @staticmethod
    def _select_agent(text: str) -> str:
        if any(term in text for term in ("code", "python", "react", "software", "debug")):
            return "CodeForge"
        if any(term in text for term in ("design", "logo", "graphic", "image")):
            return "VisionForge"
        if any(term in text for term in ("photo", "retouch", "lightroom")):
            return "PhotoForge"
        if any(term in text for term in ("video", "premiere", "edit clip")):
            return "MotionForge"
        if any(term in text for term in ("write", "email", "document", "grammar")):
            return "WordForge"
        if any(term in text for term in ("budget", "finance", "cash flow")):
            return "FinanceForge"
        if any(term in text for term in ("stock", "crypto", "market", "investment")):
            return "MarketForge"
        return "Sage Commander"
