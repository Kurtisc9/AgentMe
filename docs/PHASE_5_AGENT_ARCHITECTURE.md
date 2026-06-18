# Phase 5 Agent Architecture

Status: **PLANNING / NOT IMPLEMENTED**

Phase 5 starts the Sage executive-agent architecture. Phase 4.1 real-machine integration is intentionally skipped for now, so Phase 5 must avoid depending on unvalidated PC1/PC2 hardware services.

## Guardrails

- Do not add new UI until the agent contract is defined.
- Do not add new dashboards.
- Do not add mobile apps.
- Do not add voice assistants.
- Do not require OBS, NVIDIA telemetry, or LM Studio for initial Phase 5 work.
- Keep Ollama as the first validated local model path.
- Preserve existing safety policy: LOW may execute, MEDIUM requires KurtisC approval, HIGH remains blocked.

## Agent Roster

| Agent | Role | Initial Scope |
| --- | --- | --- |
| Sage | Commander and orchestrator | Routes work, enforces safety, maintains mission state |
| Christian | Strategy / executive operator | Turns goals into ordered operating plans |
| STANK | Builder / implementation operator | Handles code, scripts, and build tasks |
| Brian | Systems / infrastructure operator | Handles Docker, services, environment, and deployment checks |
| Dominic | Research / analysis operator | Summarizes evidence, risks, and options |
| Kristen | QA / validation operator | Owns checklists, test gates, and release readiness |

## Required Design Decisions

Before implementation, define:

1. Agent identity schema
2. Agent capability registry
3. Routing rules from user intent to agent
4. Approval boundaries per agent
5. Shared memory contract
6. Audit trail requirements
7. Failure and fallback behavior
8. How agents report status to Mission Control

## Proposed Minimal Contract

Each agent should expose:

```text
id
display_name
role
capabilities
risk_ceiling
input_contract
output_contract
requires_approval_for
enabled
```

## Phase 5 Entry Criteria

- Backend tests pass.
- Frontend build passes.
- Phase 4.1 skipped items are documented.
- Ollama local path is the preferred model path.
- No hardware-only service is required for initial agent architecture work.

## Phase 5 First Task

Create a detailed design for the agent registry and routing contract before touching application code.

Deliverable:

```text
docs/PHASE_5_AGENT_CONTRACT.md
```

The next implementation should only begin after that contract is reviewed.
