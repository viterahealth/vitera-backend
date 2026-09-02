from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole
from .medical_history_schema import MedicalHistoryCreate, MedicalHistoryResponse, MedicalHistoryUpdate
from .medical_history_services import create_medical_history, get_medical_history, update_medical_history

router = APIRouter(prefix="/camps", tags=["medical-history"])

_staff_only = require_roles(UsersRole.VOLUNTEER, UsersRole.COORDINATOR, UsersRole.DOCTOR, UsersRole.ADMIN)


@router.post(
    "/{camp_id}/registrations/{registration_id}/medical-history",
    response_model=MedicalHistoryResponse,
)
def add_medical_history(
    camp_id: str,
    registration_id: str,
    payload: MedicalHistoryCreate,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Staff-only: record Stall 4 history-taking for a checked-in registration.
    Fails if a history record already exists for this registration — use
    PATCH to amend it instead."""
    try:
        result = create_medical_history(db, camp_id, registration_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MedicalHistoryResponse(success=True, message="Medical history recorded", data=result)


@router.get(
    "/{camp_id}/registrations/{registration_id}/medical-history",
    response_model=MedicalHistoryResponse,
)
def read_medical_history(
    camp_id: str,
    registration_id: str,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Staff-only: fetch the recorded history for a registration, e.g. for the
    doctor to review at Stall 5."""
    try:
        result = get_medical_history(db, camp_id, registration_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MedicalHistoryResponse(success=True, message="OK", data=result)


@router.patch(
    "/{camp_id}/registrations/{registration_id}/medical-history",
    response_model=MedicalHistoryResponse,
)
def edit_medical_history(
    camp_id: str,
    registration_id: str,
    payload: MedicalHistoryUpdate,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Staff-only: amend a previously recorded history (partial update — only
    fields included in the request body are changed)."""
    try:
        result = update_medical_history(db, camp_id, registration_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MedicalHistoryResponse(success=True, message="Medical history updated", data=result)