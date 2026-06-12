import json
from datetime import UTC, datetime
from pathlib import Path

from app.models.approval_record import ApprovalRecord, ApprovalStatus


class ApprovalService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("Inbox/approvals.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def create(self, *, task_id: str, task_description: str) -> ApprovalRecord:
        record = ApprovalRecord.create(
            task_id=task_id,
            task_description=task_description,
        )
        self._append(record)
        return record

    def list_all(self) -> list[dict[str, object]]:
        records = self._read_all()
        changed = False
        now = datetime.now(UTC)

        for record in records:
            if record["status"] == ApprovalStatus.PENDING and now >= datetime.fromisoformat(str(record["expires_at"])):
                record["status"] = ApprovalStatus.EXPIRED
                changed = True

        if changed:
            self._rewrite(records)
        return records

    def get_verified_approval(self, *, approval_id: str, task_description: str) -> dict[str, object]:
        record = next(
            (item for item in self.list_all() if item["approval_id"] == approval_id),
            None,
        )
        if record is None:
            raise KeyError("Approval not found.")
        if record["status"] != ApprovalStatus.APPROVED:
            raise PermissionError("Approval is not approved.")
        if str(record["task_description"]).strip() != task_description.strip():
            raise PermissionError("Approval does not match this automation request.")
        return record

    def decide(
        self,
        *,
        approval_id: str,
        approver_role: str,
        approve: bool,
        note: str | None = None,
    ) -> dict[str, object]:
        records = self.list_all()
        target = next((record for record in records if record["approval_id"] == approval_id), None)

        if target is None:
            raise KeyError("Approval not found.")
        if target["status"] != ApprovalStatus.PENDING:
            raise ValueError(f"Approval is already {target['status']}.")
        if approver_role != "KurtisC":
            raise PermissionError("Only KurtisC may decide MEDIUM-risk approvals.")

        target["status"] = ApprovalStatus.APPROVED if approve else ApprovalStatus.DENIED
        target["decided_at"] = datetime.now(UTC).isoformat()
        target["decision_note"] = note
        self._rewrite(records)
        return target

    def _append(self, record: ApprovalRecord) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), default=str) + "\n")

    def _read_all(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []

        records: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records

    def _rewrite(self, records: list[dict[str, object]]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, default=str) + "\n")
