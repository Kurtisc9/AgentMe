import json
from pathlib import Path

from fastapi import APIRouter


router = APIRouter(prefix="/audit", tags=["audit"])
AUDIT_PATH = Path("logs/audit.jsonl")


@router.get("")
def list_audit_events() -> dict[str, list[dict[str, object]]]:
    if not AUDIT_PATH.exists():
        return {"events": []}

    events: list[dict[str, object]] = []
    with AUDIT_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                events.append(json.loads(stripped))

    return {"events": events}
