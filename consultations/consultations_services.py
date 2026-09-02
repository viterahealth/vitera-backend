import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.models.camp_models import Camps, CampRegistrations, CampRegistrationsStatus
from database.models.consultations_models import Consultations, Prescriptions
from database.models.patient_models import Patients
from database.models.user_models import Users
from .consultations_schema import (
    ConsultationCreate,
    ConsultationResult,
    ConsultationUpdate,
    PrescriptionCreate,
    PrescriptionResult,
)


def _full_name(patient: Patients) -> str:
    return f"{patient.first_name} {patient.last_name}".strip() if patient.last_name else patient.first_name


def _get_registration_and_patient(db: Session, camp_id: str, registration_id: str) -> tuple[CampRegistrations, Patients]:
    registration = (
        db.query(CampRegistrations)
        .filter(CampRegistrations.id == registration_id, CampRegistrations.camp_id == camp_id)
        .first()
    )
    if not registration:
        raise ValueError("Registration not found for this camp")

    patient = db.query(Patients).filter(Patients.id == registration.patient_id).first()
    if not patient:
        raise ValueError("Patient not found for this registration")

    return registration, patient


def _to_result(consultation: Consultations, patient_name: str, doctor_name: str) -> ConsultationResult:
    return ConsultationResult(
        id=consultation.id,
        registration_id=consultation.registration_id,
        patient_name=patient_name,
        doctor_name=doctor_name,
        created_at=consultation.created_at,
        updated_at=consultation.updated_at,
        chief_complaint=consultation.chief_complaint,
        clinical_observations=consultation.clinical_observations,
        diagnosis=consultation.diagnosis,
        doctor_notes=consultation.doctor_notes,
        recommendations=consultation.recommendations,
        prescriptions=[
            PrescriptionResult(
                id=p.id,
                medicine_name=p.medicine_name,
                dosage=p.dosage,
                frequency=p.frequency,
                duration=p.duration,
                instructions=p.instructions,
            )
            for p in consultation.prescriptions
        ],
    )


def get_consultation(db: Session, camp_id: str, registration_id: str) -> ConsultationResult:
    _, patient = _get_registration_and_patient(db, camp_id, registration_id)

    consultation = db.query(Consultations).filter(Consultations.registration_id == registration_id).first()
    if not consultation:
        raise ValueError("No consultation recorded for this registration yet")

    doctor = db.query(Users).filter(Users.id == consultation.doctor_id).first()
    return _to_result(consultation, _full_name(patient), doctor.name if doctor else "Unknown")


def create_consultation(
    db: Session, camp_id: str, registration_id: str, doctor_id: str, payload: ConsultationCreate
) -> ConsultationResult:
    registration, patient = _get_registration_and_patient(db, camp_id, registration_id)

    existing = db.query(Consultations).filter(Consultations.registration_id == registration_id).first()
    if existing:
        raise ValueError("A consultation already exists for this registration — use PATCH to update it")

    doctor = db.query(Users).filter(Users.id == doctor_id).first()
    if not doctor:
        raise ValueError("Doctor account not found")

    consultation = Consultations(
        id=str(uuid.uuid4()),
        registration_id=registration_id,
        doctor_id=doctor_id,
        chief_complaint=payload.chief_complaint,
        clinical_observations=payload.clinical_observations,
        diagnosis=payload.diagnosis,
        doctor_notes=payload.doctor_notes,
        recommendations=payload.recommendations,
    )
    db.add(consultation)
    db.flush()  # so consultation.id is usable for the prescriptions below

    for item in payload.prescriptions:
        db.add(
            Prescriptions(
                id=str(uuid.uuid4()),
                consultation_id=consultation.id,
                medicine_name=item.medicine_name,
                dosage=item.dosage,
                frequency=item.frequency,
                duration=item.duration,
                instructions=item.instructions,
            )
        )

    # A consultation is the last clinical step of a camp visit — mark the
    # registration COMPLETED unless it's already in a terminal state.
    if registration.status not in (CampRegistrationsStatus.COMPLETED, CampRegistrationsStatus.CANCELLED):
        registration.status = CampRegistrationsStatus.COMPLETED
        registration.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(consultation)

    return _to_result(consultation, _full_name(patient), doctor.name)


def update_consultation(
    db: Session, camp_id: str, registration_id: str, payload: ConsultationUpdate
) -> ConsultationResult:
    _, patient = _get_registration_and_patient(db, camp_id, registration_id)

    consultation = db.query(Consultations).filter(Consultations.registration_id == registration_id).first()
    if not consultation:
        raise ValueError("No consultation recorded for this registration yet — use POST to create it")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(consultation, field, value)

    db.commit()
    db.refresh(consultation)

    doctor = db.query(Users).filter(Users.id == consultation.doctor_id).first()
    return _to_result(consultation, _full_name(patient), doctor.name if doctor else "Unknown")


def add_prescription(db: Session, camp_id: str, registration_id: str, payload: PrescriptionCreate) -> ConsultationResult:
    _, patient = _get_registration_and_patient(db, camp_id, registration_id)

    consultation = db.query(Consultations).filter(Consultations.registration_id == registration_id).first()
    if not consultation:
        raise ValueError("No consultation recorded for this registration yet — create one before adding prescriptions")

    db.add(
        Prescriptions(
            id=str(uuid.uuid4()),
            consultation_id=consultation.id,
            medicine_name=payload.medicine_name,
            dosage=payload.dosage,
            frequency=payload.frequency,
            duration=payload.duration,
            instructions=payload.instructions,
        )
    )
    db.commit()
    db.refresh(consultation)

    doctor = db.query(Users).filter(Users.id == consultation.doctor_id).first()
    return _to_result(consultation, _full_name(patient), doctor.name if doctor else "Unknown")


def get_consultation_pdf_data(db: Session, camp_id: str, registration_id: str) -> dict:
    registration, patient = _get_registration_and_patient(db, camp_id, registration_id)

    consultation = db.query(Consultations).filter(Consultations.registration_id == registration_id).first()
    if not consultation:
        raise ValueError("No consultation recorded for this registration yet")

    doctor = db.query(Users).filter(Users.id == consultation.doctor_id).first()
    camp = db.query(Camps).filter(Camps.id == camp_id).first()

    return {
        "patient_name": _full_name(patient),
        "patient_code": patient.patient_code,
        "gender": patient.gender.value if patient.gender else None,
        "dob_or_age": getattr(patient, "dob_or_age", None),
        "camp_code": camp.camp_code if camp else None,
        "camp_date": camp.camp_date.isoformat() if camp and camp.camp_date else None,
        "registration_code": registration.registration_code,
        "doctor_name": doctor.name if doctor else "Unknown",
        "consultation_date": consultation.updated_at.strftime("%d %b %Y, %I:%M %p"),
        "chief_complaint": consultation.chief_complaint,
        "clinical_observations": consultation.clinical_observations,
        "diagnosis": consultation.diagnosis,
        "doctor_notes": consultation.doctor_notes,
        "recommendations": consultation.recommendations,
        "prescriptions": [
            {
                "medicine_name": p.medicine_name,
                "dosage": p.dosage,
                "frequency": p.frequency,
                "duration": p.duration,
                "instructions": p.instructions,
            }
            for p in consultation.prescriptions
        ],
    }