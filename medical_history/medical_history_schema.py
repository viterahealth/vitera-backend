from datetime import datetime

from pydantic import BaseModel


# ============================
# JSON sub-schemas
# (mirror the `comment=` on each JSON column in medical_history_models.py)
# ============================


class PastHistoryDetails(BaseModel):
    """previous similar illness, hospitalizations, transfusions, trauma, psychiatric history"""

    previous_similar_illness: str | None = None
    hospitalizations: str | None = None
    transfusions: str | None = None
    trauma: str | None = None
    psychiatric_history: str | None = None


class DrugAllergyDetails(BaseModel):
    """recent meds, dose/duration, compliance, OTC/herbal, allergy reaction details"""

    recent_medications: str | None = None
    dose_duration: str | None = None
    compliance: str | None = None
    otc_herbal: str | None = None
    allergy_reaction_details: str | None = None


class PersonalHistory(BaseModel):
    """diet, sleep, bowel/bladder, smoking, alcohol, occupation, activity, sexual history"""

    diet: str | None = None
    appetite: str | None = None
    sleep: str | None = None
    bowel_bladder: str | None = None
    smoking: str | None = None
    alcohol: str | None = None
    other_substance_use: str | None = None
    occupation: str | None = None
    occupational_exposure: str | None = None
    activity: str | None = None
    sexual_history: str | None = None


class SocialEnvironmental(BaseModel):
    """living conditions, housing, sanitation, travel, sick contacts, pets, socioeconomic"""

    living_conditions: str | None = None
    housing: str | None = None
    sanitation: str | None = None
    travel: str | None = None
    sick_contacts: str | None = None
    pets: str | None = None
    socioeconomic: str | None = None


class MenstrualObstetric(BaseModel):
    """nullable -- only populated when clinically relevant"""

    # Menstrual
    menarche_age: int | None = None
    last_menstrual_period: str | None = None
    cycle_regularity: str | None = None
    bleeding_duration_and_amount: str | None = None
    dysmenorrhea: bool | None = None
    menopause: bool | None = None
    # Obstetric
    gravida: int | None = None
    para: int | None = None
    abortions: int | None = None
    living_children: int | None = None
    previous_pregnancy_outcomes: str | None = None
    pregnancy_complications: str | None = None
    contraception: str | None = None
    # Free-text complaints specific to this section
    complaints: str | None = None


# ============================
# Request schemas
# ============================


class MedicalHistoryFields(BaseModel):
    """Shared field set between create and update. All optional — a volunteer
    fills in whatever the patient reports; nothing here is mandatory."""

    has_diabetes: bool = False
    has_hypertension: bool = False
    has_tb: bool = False
    has_asthma_copd: bool = False
    has_cardiac_disease: bool = False
    has_renal_disease: bool = False
    has_liver_disease: bool = False
    existing_conditions: str | None = None
    current_medications: str | None = None
    allergies: str | None = None
    past_surgeries: str | None = None
    family_history: str | None = None
    lifestyle_notes: str | None = None
    chief_complaint: str | None = None
    other_major_illnesses: str | None = None
    past_history_details: PastHistoryDetails | None = None
    drug_allergy_details: DrugAllergyDetails | None = None
    personal_history: PersonalHistory | None = None
    social_environmental: SocialEnvironmental | None = None
    menstrual_obstetric: MenstrualObstetric | None = None


class MedicalHistoryCreate(MedicalHistoryFields):
    pass


class MedicalHistoryUpdate(BaseModel):
    """Same fields as create, but every one is truly optional/unset-aware so
    PATCH only touches what the caller sends."""

    has_diabetes: bool | None = None
    has_hypertension: bool | None = None
    has_tb: bool | None = None
    has_asthma_copd: bool | None = None
    has_cardiac_disease: bool | None = None
    has_renal_disease: bool | None = None
    has_liver_disease: bool | None = None
    existing_conditions: str | None = None
    current_medications: str | None = None
    allergies: str | None = None
    past_surgeries: str | None = None
    family_history: str | None = None
    lifestyle_notes: str | None = None
    chief_complaint: str | None = None
    other_major_illnesses: str | None = None
    past_history_details: PastHistoryDetails | None = None
    drug_allergy_details: DrugAllergyDetails | None = None
    personal_history: PersonalHistory | None = None
    social_environmental: SocialEnvironmental | None = None
    menstrual_obstetric: MenstrualObstetric | None = None


# ============================
# Response schemas
# ============================


class MedicalHistoryResult(BaseModel):
    id: str
    registration_id: str
    patient_name: str
    created_at: datetime
    updated_at: datetime
    has_diabetes: bool
    has_hypertension: bool
    has_tb: bool
    has_asthma_copd: bool
    has_cardiac_disease: bool
    has_renal_disease: bool
    has_liver_disease: bool
    existing_conditions: str | None
    current_medications: str | None
    allergies: str | None
    past_surgeries: str | None
    family_history: str | None
    lifestyle_notes: str | None
    chief_complaint: str | None
    other_major_illnesses: str | None
    past_history_details: PastHistoryDetails | None
    drug_allergy_details: DrugAllergyDetails | None
    personal_history: PersonalHistory | None
    social_environmental: SocialEnvironmental | None
    menstrual_obstetric: MenstrualObstetric | None


class MedicalHistoryResponse(BaseModel):
    success: bool
    message: str
    data: MedicalHistoryResult