import uuid

from sqlalchemy.orm import Session

from database.models.camp_models import Camps, CampSlots
from database.models.society_models import Societies
from .camps_schema import CampCreate, CampSlotCreate, SocietyCreate


# ---------- Societies ----------

def create_society(db: Session, payload: SocietyCreate) -> Societies:
    society = Societies(
        id=str(uuid.uuid4()),
        name=payload.name,
        address=payload.address,
        area=payload.area,
        city=payload.city,
        contact_person=payload.contact_person,
        contact_phone=payload.contact_phone,
    )
    db.add(society)
    db.commit()
    db.refresh(society)
    return society


def list_societies(db: Session) -> list[Societies]:
    return db.query(Societies).order_by(Societies.name).all()


# ---------- Camps ----------

def create_camp(db: Session, payload: CampCreate) -> Camps:
    society = db.query(Societies).filter(Societies.id == payload.society_id).first()
    if not society:
        raise ValueError(f"Society {payload.society_id} not found")

    existing = db.query(Camps).filter(Camps.camp_code == payload.camp_code).first()
    if existing:
        raise ValueError(f"A camp with code {payload.camp_code} already exists")

    camp = Camps(
        id=str(uuid.uuid4()),
        society_id=payload.society_id,
        camp_code=payload.camp_code,
        camp_date=payload.camp_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    db.add(camp)
    db.commit()
    db.refresh(camp)
    return camp


def list_camps(db: Session) -> list[Camps]:
    return db.query(Camps).order_by(Camps.camp_date.desc()).all()


def get_camp_with_slots(db: Session, camp_id: str) -> Camps | None:
    camp = db.query(Camps).filter(Camps.id == camp_id).first()
    if not camp:
        return None
    camp.slots = db.query(CampSlots).filter(CampSlots.camp_id == camp_id).order_by(CampSlots.start_time).all()
    return camp


# ---------- Camp slots ----------

def create_camp_slot(db: Session, camp_id: str, payload: CampSlotCreate) -> CampSlots:
    camp = db.query(Camps).filter(Camps.id == camp_id).first()
    if not camp:
        raise ValueError(f"Camp {camp_id} not found")

    overlap_conflict = (
        db.query(CampSlots)
        .filter(CampSlots.camp_id == camp_id, CampSlots.start_time == payload.start_time)
        .first()
    )
    if overlap_conflict:
        raise ValueError("A slot already starts at that time for this camp")

    slot = CampSlots(
        id=str(uuid.uuid4()),
        camp_id=camp_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        max_capacity=payload.max_capacity,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def list_camp_slots(db: Session, camp_id: str) -> list[CampSlots]:
    return db.query(CampSlots).filter(CampSlots.camp_id == camp_id).order_by(CampSlots.start_time).all()