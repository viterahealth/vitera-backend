from datetime import datetime

from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    medicine_name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None


class ConsultationCreate(BaseModel):
    """All fields optional — a doctor fills in whatever's clinically relevant.
    Prescriptions can be attached in the same call, or added later via
    POST .../consultation/prescriptions."""

    chief_complaint: str | None = None
    clinical_observations: str | None = None
    diagnosis: str | None = None
    doctor_notes: str | None = None
    recommendations: str | None = None
    prescriptions: list[PrescriptionCreate] = []


class ConsultationUpdate(BaseModel):
    """Partial update — only fields included in the request body are changed.
    Prescriptions aren't touched here; use POST .../prescriptions to add more."""

    chief_complaint: str | None = None
    clinical_observations: str | None = None
    diagnosis: str | None = None
    doctor_notes: str | None = None
    recommendations: str | None = None


class PrescriptionResult(BaseModel):
    id: str
    medicine_name: str
    dosage: str | None
    frequency: str | None
    duration: str | None
    instructions: str | None


class ConsultationResult(BaseModel):
    id: str
    registration_id: str
    patient_name: str
    doctor_name: str
    created_at: datetime
    updated_at: datetime
    chief_complaint: str | None
    clinical_observations: str | None
    diagnosis: str | None
    doctor_notes: str | None
    recommendations: str | None
    prescriptions: list[PrescriptionResult]


class ConsultationResponse(BaseModel):
    success: bool
    message: str
    data: ConsultationResult