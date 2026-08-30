import decimal
import uuid

from sqlalchemy.orm import Session

from database.models.camp_models import CampRegistrations, CampRegistrationsStatus
from database.models.vitals_models import Vitals
from .vitals_schema import VitalsBasicIn, VitalsScreeningIn


def _to_decimal(value: float | None) -> decimal.Decimal | None:
    """Convert via str() to avoid binary-float noise (e.g. 65.10000000000001)."""
    return decimal.Decimal(str(value)) if value is not None else None


def _get_registration_or_raise(db: Session, camp_id: str, registration_id: str) -> CampRegistrations:
    registration = (
        db.query(CampRegistrations)
        .filter(CampRegistrations.id == registration_id, CampRegistrations.camp_id == camp_id)
        .first()
    )
    if not registration:
        raise ValueError("Registration not found for this camp")
    return registration


def _get_or_create_vitals(db: Session, registration_id: str) -> Vitals:
    vitals = db.query(Vitals).filter(Vitals.registration_id == registration_id).first()
    if vitals:
        return vitals
    vitals = Vitals(id=str(uuid.uuid4()), registration_id=registration_id, measured_by="")
    db.add(vitals)
    return vitals


def _recompute_bmi(vitals: Vitals) -> None:
    if vitals.height_cm and vitals.weight_kg and vitals.height_cm > 0:
        height_m = vitals.height_cm / decimal.Decimal(100)
        vitals.bmi = round(vitals.weight_kg / (height_m * height_m), 2)


def _advance_status_if_needed(registration: CampRegistrations) -> None:
    """Any stall between check-in and the doctor moves the registration to
    IN_PROGRESS -- the schema doesn't have a per-stall status, just this
    catch-all for 'somewhere in the pipeline'."""
    if registration.status == CampRegistrationsStatus.CHECKED_IN:
        registration.status = CampRegistrationsStatus.IN_PROGRESS


def record_basic_vitals(
    db: Session, camp_id: str, registration_id: str, payload: VitalsBasicIn, measured_by: str
) -> Vitals:
    """Stall 2 -- height / weight, BMI computed here."""
    registration = _get_registration_or_raise(db, camp_id, registration_id)
    vitals = _get_or_create_vitals(db, registration_id)

    if payload.height_cm is not None:
        vitals.height_cm = _to_decimal(payload.height_cm)
    if payload.weight_kg is not None:
        vitals.weight_kg = _to_decimal(payload.weight_kg)
    vitals.measured_by = measured_by

    _recompute_bmi(vitals)
    _advance_status_if_needed(registration)

    db.commit()
    db.refresh(vitals)
    return vitals


def record_screening_vitals(
    db: Session, camp_id: str, registration_id: str, payload: VitalsScreeningIn, measured_by: str
) -> Vitals:
    """Stall 3 -- BP / blood sugar / bone density (DEXA)."""
    registration = _get_registration_or_raise(db, camp_id, registration_id)
    vitals = _get_or_create_vitals(db, registration_id)

    if payload.systolic_bp is not None:
        vitals.systolic_bp = payload.systolic_bp
    if payload.diastolic_bp is not None:
        vitals.diastolic_bp = payload.diastolic_bp
    if payload.blood_sugar is not None:
        vitals.blood_sugar = _to_decimal(payload.blood_sugar)
    if payload.blood_sugar_type is not None:
        vitals.blood_sugar_type = payload.blood_sugar_type
    if payload.temperature_celsius is not None:
        vitals.temperature_celsius = _to_decimal(payload.temperature_celsius)
    if payload.bone_density_bmd is not None:
        vitals.bone_density_bmd = _to_decimal(payload.bone_density_bmd)
    if payload.bone_density_t_score is not None:
        vitals.bone_density_t_score = _to_decimal(payload.bone_density_t_score)
    if payload.bone_density_z_score is not None:
        vitals.bone_density_z_score = _to_decimal(payload.bone_density_z_score)
    if payload.bone_density_site is not None:
        vitals.bone_density_site = payload.bone_density_site
    if payload.bone_density_raw is not None:
        vitals.bone_density_raw = payload.bone_density_raw
    vitals.measured_by = measured_by

    _advance_status_if_needed(registration)

    db.commit()
    db.refresh(vitals)
    return vitals


def get_vitals(db: Session, camp_id: str, registration_id: str) -> Vitals | None:
    _get_registration_or_raise(db, camp_id, registration_id)
    return db.query(Vitals).filter(Vitals.registration_id == registration_id).first()