from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole
from .vitals_schema import VitalsBasicIn, VitalsData, VitalsResponse, VitalsScreeningIn
from .vitals_services import get_vitals, record_basic_vitals, record_screening_vitals

router = APIRouter(prefix="/camps", tags=["vitals"])

_staff_only = require_roles(UsersRole.VOLUNTEER, UsersRole.COORDINATOR, UsersRole.ADMIN, UsersRole.DOCTOR)


@router.get("/{camp_id}/registrations/{registration_id}/vitals", response_model=VitalsResponse)
def get_vitals_route(
    camp_id: str,
    registration_id: str,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    try:
        vitals = get_vitals(db, camp_id, registration_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not vitals:
        raise HTTPException(status_code=404, detail="No vitals recorded yet for this registration")
    return VitalsResponse(success=True, message="OK", data=VitalsData.model_validate(vitals))


@router.put("/{camp_id}/registrations/{registration_id}/vitals/basic", response_model=VitalsResponse)
def record_basic_vitals_route(
    camp_id: str,
    registration_id: str,
    payload: VitalsBasicIn,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Stall 2 -- height / weight. BMI is computed and stored automatically."""
    try:
        vitals = record_basic_vitals(db, camp_id, registration_id, payload, measured_by=identity.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return VitalsResponse(success=True, message="Vitals saved", data=VitalsData.model_validate(vitals))


@router.put("/{camp_id}/registrations/{registration_id}/vitals/screening", response_model=VitalsResponse)
def record_screening_vitals_route(
    camp_id: str,
    registration_id: str,
    payload: VitalsScreeningIn,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Stall 3 -- BP / blood sugar / bone density (DEXA)."""
    try:
        vitals = record_screening_vitals(db, camp_id, registration_id, payload, measured_by=identity.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return VitalsResponse(success=True, message="Screening saved", data=VitalsData.model_validate(vitals))