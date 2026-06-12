from __future__ import annotations


class OrchestrationPlanner:
    def plan(self, objective: str) -> list[dict[str, str]]:
        normalized = objective.lower()
        steps: list[dict[str, str]] = []

        if any(word in normalized for word in ["code", "app", "software", "bug", "api"]):
            steps.append({"agent_name": "CodeForge", "task": objective})
        if any(word in normalized for word in ["write", "summary", "document", "email", "proposal"]):
            steps.append({"agent_name": "WordForge", "task": objective})
        if any(word in normalized for word in ["logo", "design", "brand", "visual", "image"]):
            steps.append({"agent_name": "VisionForge", "task": objective})
        if any(word in normalized for word in ["budget", "finance", "price", "cost", "projection"]):
            steps.append({"agent_name": "FinanceForge", "task": objective})
        if any(word in normalized for word in ["market", "stock", "crypto", "research", "trend"]):
            steps.append({"agent_name": "MarketForge", "task": objective})
        if any(word in normalized for word in ["video", "motion", "edit", "clip"]):
            steps.append({"agent_name": "MotionForge", "task": objective})

        if not steps:
            steps.append({"agent_name": "WordForge", "task": objective})

        return steps
