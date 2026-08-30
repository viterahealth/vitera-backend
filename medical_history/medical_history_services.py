import uuid

from sqlalchemy.orm import Session

from database.models.camp_models import CampRegistrations
from database.models.medical_history_models import MedicalHistory
from database.models.patient_models import Patients
from .medical_history_schema import MedicalHistoryCreate, MedicalHistoryResult, MedicalHistoryUpdate


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


def _to_result(history: MedicalHistory, patient_name: str) -> MedicalHistoryResult:
    return MedicalHistoryResult(
        id=history.id,
        registration_id=history.registration_id,
        patient_name=patient_name,
        created_at=history.created_at,
        updated_at=history.updated_at,
        has_diabetes=bool(history.has_diabetes),
        has_hypertension=bool(history.has_hypertension),
        has_tb=bool(history.has_tb),
        has_asthma_copd=bool(history.has_asthma_copd),
        has_cardiac_disease=bool(history.has_cardiac_disease),
        has_renal_disease=bool(history.has_renal_disease),
        has_liver_disease=bool(history.has_liver_disease),
        existing_conditions=history.existing_conditions,
        current_medications=history.current_medications,
        allergies=history.allergies,
        past_surgeries=history.past_surgeries,
        family_history=history.family_history,
        lifestyle_notes=history.lifestyle_notes,
        chief_complaint=history.chief_complaint,
        other_major_illnesses=history.other_major_illnesses,
        past_history_details=history.past_history_details,
        drug_allergy_details=history.drug_allergy_details,
        personal_history=history.personal_history,
        social_environmental=history.social_environmental,
        menstrual_obstetric=history.menstrual_obstetric,
    )


def get_medical_history(db: Session, camp_id: str, registration_id: str) -> MedicalHistoryResult:
    _, patient = _get_registration_and_patient(db, camp_id, registration_id)

    history = db.query(MedicalHistory).filter(MedicalHistory.registration_id == registration_id).first()
    if not history:
        raise ValueError("No medical history recorded for this registration yet")

    return _to_result(history, _full_name(patient))


def create_medical_history(
    db: Session, camp_id: str, registration_id: str, payload: MedicalHistoryCreate
) -> MedicalHistoryResult:
    _, patient = _get_registration_and_patient(db, camp_id, registration_id)

    existing = db.query(MedicalHistory).filter(MedicalHistory.registration_id == registration_id).first()
    if existing:
        raise ValueError("Medical history already recorded for this registration — use PATCH to update it")

    # model_dump() already turns the nested JSON sub-schemas into plain dicts,
    # which is exactly what the JSON columns expect.
    data = payload.model_dump()
    history = MedicalHistory(id=str(uuid.uuid4()), registration_id=registration_id, **data)
    db.add(history)
    db.commit()
    db.refresh(history)

    return _to_result(history, _full_name(patient))


def update_medical_history(
    db: Session, camp_id: str, registration_id: str, payload: MedicalHistoryUpdate
) -> MedicalHistoryResult:
    _, patient = _get_registration_and_patient(db, camp_id, registration_id)

    history = db.query(MedicalHistory).filter(MedicalHistory.registration_id == registration_id).first()
    if not history:
        raise ValueError("No medical history recorded for this registration yet — use POST to create it")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(history, field, value)

    db.commit()
    db.refresh(history)

    return _to_result(history, _full_name(patient))