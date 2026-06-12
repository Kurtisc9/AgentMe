from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent


class SpecialistAgent(BaseAgent):
    def __init__(
        self,
        *,
        name: str,
        description: str,
        capabilities: tuple[str, ...],
    ) -> None:
        self.name = name
        self.description = description
        self.capabilities = capabilities

    def execute(self, task: str) -> AgentResult:
        normalized = task.strip()
        if not normalized:
            return AgentResult(
                agent_name=self.name,
                task=task,
                output="Task cannot be empty.",
                success=False,
            )

        return AgentResult(
            agent_name=self.name,
            task=normalized,
            output=f"{self.name} accepted the task for specialist processing.",
            success=True,
        )


SPECIALIST_DEFINITIONS: tuple[dict[str, object], ...] = (
    {
        "name": "CodeForge",
        "description": "Software engineering, debugging, testing, and architecture.",
        "capabilities": ("code", "debug", "test", "architecture"),
    },
    {
        "name": "VisionForge",
        "description": "Graphic design, image concepts, branding, and visual direction.",
        "capabilities": ("design", "branding", "image", "logo"),
    },
    {
        "name": "PhotoForge",
        "description": "Photo correction, retouching, compositing, and Lightroom workflows.",
        "capabilities": ("photo", "retouch", "lightroom", "composite"),
    },
    {
        "name": "MotionForge",
        "description": "Video editing, motion design, sequencing, and export workflows.",
        "capabilities": ("video", "motion", "premiere", "editing"),
    },
    {
        "name": "WordForge",
        "description": "Writing, editing, documents, messages, and structured communication.",
        "capabilities": ("write", "edit", "document", "email"),
    },
    {
        "name": "FinanceForge",
        "description": "Budgets, cash-flow models, projections, and financial organization.",
        "capabilities": ("budget", "cash-flow", "forecast", "finance"),
    },
    {
        "name": "MarketForge",
        "description": "Market research, asset analysis, and risk-aware investing support.",
        "capabilities": ("market", "stock", "crypto", "research"),
    },
)


def build_specialists() -> dict[str, SpecialistAgent]:
    return {
        str(definition["name"]): SpecialistAgent(
            name=str(definition["name"]),
            description=str(definition["description"]),
            capabilities=tuple(definition["capabilities"]),
        )
        for definition in SPECIALIST_DEFINITIONS
    }
