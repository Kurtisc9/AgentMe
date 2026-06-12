from app.core.commander import RiskLevel, SageCommander


def test_routes_code_task_to_codeforge() -> None:
    result = SageCommander().route_task("Review this Python code")

    assert result.assigned_agent == "CodeForge"
    assert result.risk_level == RiskLevel.LOW
    assert result.approval_required is False
    assert result.blocked is False


def test_medium_task_requires_approval() -> None:
    result = SageCommander().route_task("Edit file for the React dashboard")

    assert result.assigned_agent == "CodeForge"
    assert result.risk_level == RiskLevel.MEDIUM
    assert result.approval_required is True
    assert result.blocked is False


def test_high_risk_task_is_blocked() -> None:
    result = SageCommander().route_task("Transfer money to another account")

    assert result.risk_level == RiskLevel.HIGH
    assert result.blocked is True
    assert result.approval_required is False
