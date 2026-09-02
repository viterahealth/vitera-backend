from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole  # adjust import path if this enum lives elsewhere
from .registrations_schema import (
    CampRegistrationCreate,
    CampRegistrationResponse,
    CheckInResponse,
    RegistrationSearchResponse,
)
from .registrations_services import check_in_registration, create_family_registration, search_registrations

router = APIRouter(prefix="/camps", tags=["registrations"])

_staff_only = require_roles(UsersRole.VOLUNTEER, UsersRole.COORDINATOR, UsersRole.DOCTOR, UsersRole.ADMIN)


@router.post("/{camp_id}/registrations", response_model=CampRegistrationResponse)
def register_family(camp_id: str, payload: CampRegistrationCreate, db: Session = Depends(get_db)):
    """
    Public self-registration endpoint — linked from a QR code / Google Form at
    the camp itself. No auth required: registers a whole family/group for one
    camp + slot in a single call.
    """
    try:
        result = create_family_registration(db, camp_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CampRegistrationResponse(success=True, message="Registered successfully", data=result)


@router.get("/{camp_id}/registrations/search", response_model=RegistrationSearchResponse)
def search_camp_registrations(
    camp_id: str,
    q: str,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Staff-only: find a registration in this camp by patient name or phone,
    e.g. to pull it up before checking someone in."""
    results = search_registrations(db, camp_id, q)
    return RegistrationSearchResponse(success=True, message="OK", data=results)


@router.patch("/{camp_id}/registrations/{registration_id}/check-in", response_model=CheckInResponse)
def check_in(
    camp_id: str,
    registration_id: str,
    db: Session = Depends(get_db),
    identity=Depends(_staff_only),
):
    """Staff-only: mark a REGISTERED registration as CHECKED_IN. Rejects
    registrations that are already checked in, cancelled, or a no-show."""
    try:
        result = check_in_registration(db, camp_id, registration_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CheckInResponse(success=True, message="Checked in", data=result)


# --- Later, when volunteers need to add walk-ins on-site, reuse the same
# service with registration_source=ON_SPOT/STAFF and put it behind auth:
#
# from core.dependencies import require_roles
# from database.models.models_generated import UsersRole, CampRegistrationsRegistrationSource
#
# @router.post("/{camp_id}/registrations/manual", response_model=CampRegistrationResponse)
# def register_family_manual(
#     camp_id: str,
#     payload: CampRegistrationCreate,
#     db: Session = Depends(get_db),
#     identity=Depends(require_roles(UsersRole.VOLUNTEER, UsersRole.COORDINATOR, UsersRole.DOCTOR, UsersRole.ADMIN)),
# ):
#     try:
#         result = create_family_registration(
#             db, camp_id, payload, registration_source=CampRegistrationsRegistrationSource.ON_SPOT
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     return CampRegistrationResponse(success=True, message="Registered successfully", data=result)