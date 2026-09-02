from datetime import date, datetime

from pydantic import BaseModel

from database.models.camp_models import CampRegistrationsRegistrationSource, CampRegistrationsStatus
from database.models.patient_models import PatientsGender
from database.models.vitals_models import VitalsBloodSugarType


# ---------- search ----------
class PatientSearchResult(BaseModel):
    id: str
    patient_code: str
    name: str
    phone: str | None
    email: str | None
    gender: PatientsGender | None
    dob_or_age: str | None
    family_code: str | None


class PatientSearchResponse(BaseModel):
    success: bool
    message: str
    data: list[PatientSearchResult]


# ---------- full detail (nested inside each camp visit) ----------
class VitalsDetail(BaseModel):
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    systolic_bp: int | None
    diastolic_bp: int | None
    blood_sugar: float | None
    blood_sugar_type: VitalsBloodSugarType | None
    temperature_celsius: float | None
    bone_density_bmd: float | None
    bone_density_t_score: float | None
    bone_density_z_score: float | None
    bone_density_site: str | None
    measured_at: datetime

    model_config = {"from_attributes": True}


class MedicalHistoryDetail(BaseModel):
    chief_complaint: str | None
    has_diabetes: bool
    has_hypertension: bool
    has_tb: bool
    has_asthma_copd: bool
    has_cardiac_disease: bool
    has_renal_disease: bool
    has_liver_disease: bool
    other_major_illnesses: str | None
    existing_conditions: str | None
    current_medications: str | None
    allergies: str | None
    past_surgeries: str | None
    family_history: str | None
    lifestyle_notes: str | None
    past_history_details: dict | None
    drug_allergy_details: dict | None
    personal_history: dict | None
    social_environmental: dict | None
    menstrual_obstetric: dict | None

    model_config = {"from_attributes": True}


class PrescriptionDetail(BaseModel):
    medicine_name: str
    dosage: str | None
    frequency: str | None
    duration: str | None
    instructions: str | None

    model_config = {"from_attributes": True}


class ConsultationDetail(BaseModel):
    doctor_name: str
    chief_complaint: str | None
    clinical_observations: str | None
    diagnosis: str | None
    doctor_notes: str | None
    recommendations: str | None
    created_at: datetime
    prescriptions: list[PrescriptionDetail]


class RegistrationDetail(BaseModel):
    registration_id: str
    registration_code: str
    camp_code: str | None
    camp_date: date | None
    status: CampRegistrationsStatus
    registration_source: CampRegistrationsRegistrationSource
    slot_label: str | None
    building_name: str | None
    service_interest: str | None
    registered_at: datetime
    checked_in_at: datetime | None
    completed_at: datetime | None
    vitals: VitalsDetail | None
    medical_history: MedicalHistoryDetail | None
    consultation: ConsultationDetail | None


class PatientFullDetail(BaseModel):
    id: str
    patient_code: str
    name: str
    phone: str | None
    email: str | None
    gender: PatientsGender | None
    dob_or_age: str | None
    address: str | None
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    flat_number: str | None
    family_code: str | None
    registrations: list[RegistrationDetail]


class PatientDetailResponse(BaseModel):
    success: bool
    message: str
    data: PatientFullDetail