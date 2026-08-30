from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole
from .consultations_schema import (
    ConsultationCreate,
    ConsultationResponse,
    ConsultationUpdate,
    PrescriptionCreate,
)
from .consultations_services import add_prescription, create_consultation, get_consultation, update_consultation

router = APIRouter(prefix="/camps", tags=["consultations"])

_doctor_write = require_roles(UsersRole.DOCTOR, UsersRole.ADMIN)
_any_staff = require_roles(UsersRole.DOCTOR, UsersRole.VOLUNTEER, UsersRole.COORDINATOR, UsersRole.ADMIN)


@router.post(
    "/{camp_id}/registrations/{registration_id}/consultation",
    response_model=ConsultationResponse,
)
def add_consultation(
    camp_id: str,
    registration_id: str,
    payload: ConsultationCreate,
    db: Session = Depends(get_db),
    identity=Depends(_doctor_write),
):
    """Doctor-only: record Stall 5 diagnosis + prescriptions for a checked-in
    registration. Marks the registration COMPLETED. Fails if a consultation
    already exists — use PATCH to amend it instead."""
    try:
        result = create_consultation(db, camp_id, registration_id, identity.user_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ConsultationResponse(success=True, message="Consultation recorded", data=result)


@router.get(
    "/{camp_id}/registrations/{registration_id}/consultation",
    response_model=ConsultationResponse,
)
def read_consultation(
    camp_id: str,
    registration_id: str,
    db: Session = Depends(get_db),
    identity=Depends(_any_staff),
):
    """Any staff role: view the recorded diagnosis + prescriptions."""
    try:
        result = get_consultation(db, camp_id, registration_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ConsultationResponse(success=True, message="OK", data=result)


@router.patch(
    "/{camp_id}/registrations/{registration_id}/consultation",
    response_model=ConsultationResponse,
)
def edit_consultation(
    camp_id: str,
    registration_id: str,
    payload: ConsultationUpdate,
    db: Session = Depends(get_db),
    identity=Depends(_doctor_write),
):
    """Doctor-only: amend a previously recorded consultation (partial update)."""
    try:
        result = update_consultation(db, camp_id, registration_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ConsultationResponse(success=True, message="Consultation updated", data=result)


@router.post(
    "/{camp_id}/registrations/{registration_id}/consultation/prescriptions",
    response_model=ConsultationResponse,
)
def add_consultation_prescription(
    camp_id: str,
    registration_id: str,
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    identity=Depends(_doctor_write),
):
    """Doctor-only: add one more prescription to an existing consultation."""
    try:
        result = add_prescription(db, camp_id, registration_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ConsultationResponse(success=True, message="Prescription added", data=result)