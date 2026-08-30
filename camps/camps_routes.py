from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole  # adjust import path if this enum lives elsewhere
from .camps_schema import (
    CampCreate,
    CampDetailResponse,
    CampListResponse,
    CampResponse,
    CampSlotCreate,
    CampSlotListResponse,
    CampSlotResponse,
    SocietyCreate,
    SocietyData,
    SocietyListResponse,
    SocietyResponse,
    CampData,
    CampDetailData,
    CampSlotData,
)
from .camps_services import (
    create_camp,
    create_camp_slot,
    create_society,
    get_camp_with_slots,
    list_camp_slots,
    list_camps,
    list_societies,
)

router = APIRouter(tags=["camps"])

_manage_camps = require_roles(UsersRole.ADMIN, UsersRole.COORDINATOR)
_view_camps = require_roles(UsersRole.ADMIN, UsersRole.COORDINATOR, UsersRole.VOLUNTEER, UsersRole.DOCTOR)


# ---------- Societies ----------

@router.post("/societies", response_model=SocietyResponse)
def create_society_route(payload: SocietyCreate, db: Session = Depends(get_db), identity=Depends(_manage_camps)):
    society = create_society(db, payload)
    return SocietyResponse(success=True, message="Society created", data=SocietyData.model_validate(society))


@router.get("/societies", response_model=SocietyListResponse)
def list_societies_route(db: Session = Depends(get_db), identity=Depends(_view_camps)):
    societies = list_societies(db)
    return SocietyListResponse(
        success=True, message="OK", data=[SocietyData.model_validate(s) for s in societies]
    )


# ---------- Camps ----------

@router.post("/camps", response_model=CampResponse)
def create_camp_route(payload: CampCreate, db: Session = Depends(get_db), identity=Depends(_manage_camps)):
    try:
        camp = create_camp(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CampResponse(success=True, message="Camp created", data=CampData.model_validate(camp))


@router.get("/camps", response_model=CampListResponse)
def list_camps_route(db: Session = Depends(get_db), identity=Depends(_view_camps)):
    camps = list_camps(db)
    return CampListResponse(success=True, message="OK", data=[CampData.model_validate(c) for c in camps])


@router.get("/camps/{camp_id}", response_model=CampDetailResponse)
def get_camp_route(camp_id: str, db: Session = Depends(get_db), identity=Depends(_view_camps)):
    camp = get_camp_with_slots(db, camp_id)
    if not camp:
        raise HTTPException(status_code=404, detail="Camp not found")
    data = CampDetailData(
        **CampData.model_validate(camp).model_dump(),
        slots=[CampSlotData.model_validate(s) for s in camp.slots],
    )
    return CampDetailResponse(success=True, message="OK", data=data)


# ---------- Camp slots ----------

@router.post("/camps/{camp_id}/slots", response_model=CampSlotResponse)
def create_camp_slot_route(
    camp_id: str, payload: CampSlotCreate, db: Session = Depends(get_db), identity=Depends(_manage_camps)
):
    try:
        slot = create_camp_slot(db, camp_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CampSlotResponse(success=True, message="Slot created", data=CampSlotData.model_validate(slot))


@router.get("/camps/{camp_id}/slots", response_model=CampSlotListResponse)
def list_camp_slots_route(camp_id: str, db: Session = Depends(get_db), identity=Depends(_view_camps)):
    slots = list_camp_slots(db, camp_id)
    return CampSlotListResponse(
        success=True, message="OK", data=[CampSlotData.model_validate(s) for s in slots]
    )