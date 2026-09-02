from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.models.camp_models import CampRegistrations, Camps, CampSlots
from database.models.consultations_models import Consultations
from database.models.medical_history_models import MedicalHistory
from database.models.patient_models import Patients
from database.models.user_models import Users
from database.models.vitals_models import Vitals
from database.models.society_models import Buildings
from .patients_schema import (
    ConsultationDetail,
    MedicalHistoryDetail,
    PatientFullDetail,
    PrescriptionDetail,
    RegistrationDetail,
    VitalsDetail,
)


def full_name(p: Patients) -> str:
    return f"{p.first_name} {p.last_name}".strip() if p.last_name else p.first_name


def search_patients(db: Session, query: str, limit: int = 20) -> list[Patients]:
    """Cross-camp search -- every patient ever registered, not scoped to
    one camp like the stall search widgets are."""
    like = f"%{query.strip()}%"
    return (
        db.query(Patients)
        .filter(
            or_(
                Patients.first_name.ilike(like),
                Patients.last_name.ilike(like),
                Patients.phone.ilike(like),
                Patients.patient_code.ilike(like),
                Patients.email.ilike(like),
            )
        )
        .order_by(Patients.created_at.desc())
        .limit(limit)
        .all()
    )


def _slot_label(slot: CampSlots) -> str:
    def fmt(t) -> str:
        s = t.strftime("%I:%M %p")
        return s[1:] if s.startswith("0") else s

    return f"{fmt(slot.start_time)}-{fmt(slot.end_time)}"


def get_patient_full_detail(db: Session, patient_id: str) -> PatientFullDetail:
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    if not patient:
        raise ValueError("Patient not found")

    registrations = (
        db.query(CampRegistrations)
        .filter(CampRegistrations.patient_id == patient_id)
        .order_by(CampRegistrations.registered_at.desc())
        .all()
    )

    reg_details = []
    for reg in registrations:
        camp = db.query(Camps).filter(Camps.id == reg.camp_id).first()
        slot = db.query(CampSlots).filter(CampSlots.id == reg.slot_id).first() if reg.slot_id else None
        building = (
            db.query(Buildings).filter(Buildings.id == reg.building_id).first() if reg.building_id else None
        )
        vitals = db.query(Vitals).filter(Vitals.registration_id == reg.id).first()
        history = db.query(MedicalHistory).filter(MedicalHistory.registration_id == reg.id).first()
        consultation = db.query(Consultations).filter(Consultations.registration_id == reg.id).first()

        consultation_detail = None
        if consultation:
            doctor = db.query(Users).filter(Users.id == consultation.doctor_id).first()
            consultation_detail = ConsultationDetail(
                doctor_name=doctor.name if doctor else "Unknown",
                chief_complaint=consultation.chief_complaint,
                clinical_observations=consultation.clinical_observations,
                diagnosis=consultation.diagnosis,
                doctor_notes=consultation.doctor_notes,
                recommendations=consultation.recommendations,
                created_at=consultation.created_at,
                prescriptions=[PrescriptionDetail.model_validate(p) for p in consultation.prescriptions],
            )

        reg_details.append(
            RegistrationDetail(
                registration_id=reg.id,
                registration_code=reg.registration_code,
                camp_code=camp.camp_code if camp else None,
                camp_date=camp.camp_date if camp else None,
                status=reg.status,
                registration_source=reg.registration_source,
                slot_label=_slot_label(slot) if slot else None,
                building_name=building.name if building else None,
                service_interest=reg.service_interest,
                registered_at=reg.registered_at,
                checked_in_at=reg.checked_in_at,
                completed_at=reg.completed_at,
                vitals=VitalsDetail.model_validate(vitals) if vitals else None,
                medical_history=MedicalHistoryDetail.model_validate(history) if history else None,
                consultation=consultation_detail,
            )
        )

    return PatientFullDetail(
        id=patient.id,
        patient_code=patient.patient_code,
        name=full_name(patient),
        phone=patient.phone,
        email=patient.email,
        gender=patient.gender,
        dob_or_age=patient.dob_or_age,
        address=patient.address,
        emergency_contact_name=patient.emergency_contact_name,
        emergency_contact_phone=patient.emergency_contact_phone,
        flat_number=patient.flat_number,
        family_code=patient.family.family_code if patient.family else None,
        registrations=reg_details,
    )


def get_registration_report_data(
    db: Session, patient_id: str, registration_id: str
) -> tuple[PatientFullDetail, RegistrationDetail]:
    """Used by GET /patients/{patient_id}/registrations/{registration_id}/report.pdf.
    Reuses get_patient_full_detail rather than re-querying everything, then
    picks out the one registration the report is for."""
    patient = get_patient_full_detail(db, patient_id)
    reg = next((r for r in patient.registrations if r.registration_id == registration_id), None)
    if not reg:
        raise ValueError("Registration not found for this patient")
    return patient, reg