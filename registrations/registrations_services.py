import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.models.camp_models import (
    Camps,
    CampSlots,
    CampSlotsStatus,
    CampRegistrations,
    CampRegistrationsRegistrationSource,
    CampRegistrationsStatus,
)
from database.models.patient_models import Patients
from database.models.families_models import  Families
from .registrations_schema import CampRegistrationCreate

_DASH_RE = re.compile(r"[\u2012\u2013\u2014\u2015-]")
_SPACE_RE = re.compile(r"\s+")


def _normalize_slot_text(text: str) -> str:
    """Lowercase, collapse whitespace, and fold every dash variant (-, –, —) to '-'
    so '11:00 AM – 12:00 PM' and '11:00am-12:00pm' compare equal."""
    text = _DASH_RE.sub("-", text.strip().lower())
    return _SPACE_RE.sub(" ", text)


def _slot_label(slot: CampSlots) -> str:
    def fmt(t) -> str:
        s = t.strftime("%I:%M %p")
        return s[1:] if s.startswith("0") else s

    return f"{fmt(slot.start_time)}-{fmt(slot.end_time)}"


def _find_matching_slot(db: Session, camp_id: str, slot_text: str) -> CampSlots | None:
    target = _normalize_slot_text(slot_text)
    slots = db.query(CampSlots).filter(CampSlots.camp_id == camp_id).all()
    for slot in slots:
        if _normalize_slot_text(_slot_label(slot)) == target:
            return slot
    return None


def create_family_registration(
    db: Session,
    camp_id: str,
    payload: CampRegistrationCreate,
    registration_source: CampRegistrationsRegistrationSource = CampRegistrationsRegistrationSource.GOOGLE_FORM,
) -> dict:
    camp = db.query(Camps).filter(Camps.id == camp_id).first()
    if not camp:
        raise ValueError(f"Camp {camp_id} not found")

    slot = _find_matching_slot(db, camp_id, payload.slot)
    if not slot:
        raise ValueError(f"No slot matching '{payload.slot}' found for this camp")
    if slot.status != CampSlotsStatus.OPEN:
        raise ValueError("This slot is not open for registration")
    if slot.current_count + len(payload.members) > slot.max_capacity:
        raise ValueError("Not enough capacity left in this slot for the whole group")

    family = Families(id=str(uuid.uuid4()), family_code=f"F-{uuid.uuid4().hex[:8].upper()}")
    db.add(family)
    db.flush()  # so family.id is usable below before the final commit

    created = []
    for index, member in enumerate(payload.members):
        first_name, *rest = member.name.strip().split(" ", 1)
        last_name = rest[0] if rest else None

        patient = Patients(
            id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            family_id=family.id,
            phone=member.phone,
            gender=member.gender,
            date_of_birth=member.date_of_birth,
            email=payload.email,
            flat_number=payload.flat_number,  # requires the flat_number column — see migration note
        )
        db.add(patient)
        db.flush()

        if index == 0:
            family.primary_patient_id = patient.id

        registration = CampRegistrations(
            id=str(uuid.uuid4()),
            registration_code=f"R-{uuid.uuid4().hex[:8].upper()}",
            patient_id=patient.id,
            camp_id=camp_id,
            slot_id=slot.id,
            registration_source=registration_source,
            status=CampRegistrationsStatus.REGISTERED,
            service_interest=payload.service_interest,  # requires the service_interest column — see migration note
        )
        db.add(registration)
        created.append((patient, registration))

    slot.current_count += len(payload.members)
    if slot.current_count >= slot.max_capacity:
        slot.status = CampSlotsStatus.FULL

    db.commit()
    for patient, registration in created:
        db.refresh(patient)
        db.refresh(registration)

    return {
        "camp_id": camp_id,
        "slot_id": slot.id,
        "members": [
            {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}".strip() if p.last_name else p.first_name,
                "registration_id": r.id,
                "registration_code": r.registration_code,
            }
            for p, r in created
        ],
    }


def _full_name(patient: Patients) -> str:
    return f"{patient.first_name} {patient.last_name}".strip() if patient.last_name else patient.first_name


def search_registrations(db: Session, camp_id: str, query: str) -> list[dict]:
    """Search registrations within one camp by patient first/last name or phone."""
    like = f"%{query.strip()}%"
    rows = (
        db.query(CampRegistrations, Patients, CampSlots)
        .join(Patients, CampRegistrations.patient_id == Patients.id)
        .outerjoin(CampSlots, CampRegistrations.slot_id == CampSlots.id)
        .filter(CampRegistrations.camp_id == camp_id)
        .filter(
            or_(
                Patients.first_name.ilike(like),
                Patients.last_name.ilike(like),
                Patients.phone.ilike(like),
            )
        )
        .all()
    )
    return [
        {
            "registration_id": reg.id,
            "registration_code": reg.registration_code,
            "patient_id": patient.id,
            "patient_name": _full_name(patient),
            "phone": patient.phone,
            "status": reg.status,
            "slot_label": _slot_label(slot) if slot else None,
        }
        for reg, patient, slot in rows
    ]


def check_in_registration(db: Session, camp_id: str, registration_id: str) -> dict:
    registration = (
        db.query(CampRegistrations)
        .filter(CampRegistrations.id == registration_id, CampRegistrations.camp_id == camp_id)
        .first()
    )
    if not registration:
        raise ValueError("Registration not found for this camp")
    if registration.status != CampRegistrationsStatus.REGISTERED:
        raise ValueError(f"Cannot check in a registration with status {registration.status.value}")

    registration.checked_in_at = datetime.now(timezone.utc)
    registration.status = CampRegistrationsStatus.CHECKED_IN
    db.commit()
    db.refresh(registration)

    patient = db.query(Patients).filter(Patients.id == registration.patient_id).first()

    return {
        "registration_id": registration.id,
        "registration_code": registration.registration_code,
        "patient_name": _full_name(patient),
        "status": registration.status,
        "checked_in_at": registration.checked_in_at,
    }