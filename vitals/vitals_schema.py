from typing import Optional

from pydantic import BaseModel

from database.models.vitals_models import VitalsBloodSugarType


# ---------- Stall 2: height / weight (BMI computed server-side) ----------
class VitalsBasicIn(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


# ---------- Stall 3: BP / blood sugar / bone density (DEXA) ----------
class VitalsScreeningIn(BaseModel):
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    blood_sugar: Optional[float] = None
    blood_sugar_type: Optional[VitalsBloodSugarType] = None
    temperature_celsius: Optional[float] = None
    bone_density_bmd: Optional[float] = None
    bone_density_t_score: Optional[float] = None
    bone_density_z_score: Optional[float] = None
    bone_density_site: Optional[str] = None
    bone_density_raw: Optional[dict] = None


# ---------- combined read model -- what Stall 5 (doctor) sees ----------
class VitalsData(BaseModel):
    id: str
    registration_id: str
    measured_by: str
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    blood_sugar: Optional[float]
    blood_sugar_type: Optional[VitalsBloodSugarType]
    temperature_celsius: Optional[float]
    bone_density_bmd: Optional[float]
    bone_density_t_score: Optional[float]
    bone_density_z_score: Optional[float]
    bone_density_site: Optional[str]
    bone_density_raw: Optional[dict]

    class Config:
        from_attributes = True


class VitalsResponse(BaseModel):
    success: bool
    message: str
    data: VitalsData