from fastapi import APIRouter, HTTPException, status

from app.schemas.approvals import ApprovalDecision, ApprovalListResponse, ApprovalResponse
from app.services.approval_service import ApprovalService


router = APIRouter(prefix="/approvals", tags=["approvals"])
service = ApprovalService()


@router.get("", response_model=ApprovalListResponse)
def list_approvals() -> ApprovalListResponse:
    return ApprovalListResponse(approvals=service.list_all())


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve_request(approval_id: str, payload: ApprovalDecision) -> ApprovalResponse:
    try:
        result = service.decide(
            approval_id=approval_id,
            approver_role=payload.approver_role,
            approve=True,
            note=payload.note,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ApprovalResponse(**result)


@router.post("/{approval_id}/deny", response_model=ApprovalResponse)
def deny_request(approval_id: str, payload: ApprovalDecision) -> ApprovalResponse:
    try:
        result = service.decide(
            approval_id=approval_id,
            approver_role=payload.approver_role,
            approve=False,
            note=payload.note,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ApprovalResponse(**result)
