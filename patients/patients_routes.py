import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.dependencies import require_roles
from database.db_session import get_db
from database.models.user_models import UsersRole
from .patients_pdf import build_registration_pdf
from .patients_schema import PatientDetailResponse, PatientSearchResponse, PatientSearchResult
from .patients_services import full_name, get_patient_full_detail, get_registration_report_data, search_patients

router = APIRouter(prefix="/patients", tags=["patients"])

_any_staff = require_roles(UsersRole.DOCTOR, UsersRole.VOLUNTEER, UsersRole.COORDINATOR, UsersRole.ADMIN)


@router.get("/search", response_model=PatientSearchResponse)
def search_patients_route(
    q: str,
    db: Session = Depends(get_db),
    identity=Depends(_any_staff),
):
    """
    Search across ALL patients (every camp visit ever, not scoped to one
    camp like the stall search widgets are) by name, phone, email, or
    patient code. Follow up with GET /patients/{patient_id} for the full
    record of whichever one you pick.
    """
    patients = search_patients(db, q)
    return PatientSearchResponse(
        success=True,
        message="OK",
        data=[
            PatientSearchResult(
                id=p.id,
                patient_code=p.patient_code,
                name=full_name(p),
                phone=p.phone,
                email=p.email,
                gender=p.gender,
                dob_or_age=p.dob_or_age,
                family_code=p.family.family_code if p.family else None,
            )
            for p in patients
        ],
    )


@router.get("/{patient_id}", response_model=PatientDetailResponse)
def get_patient_route(
    patient_id: str,
    db: Session = Depends(get_db),
    identity=Depends(_any_staff),
):
    """Full patient record: bio details plus every camp visit, each with
    its vitals, medical history, and consultation (if recorded)."""
    try:
        result = get_patient_full_detail(db, patient_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PatientDetailResponse(success=True, message="OK", data=result)


@router.get("/{patient_id}/registrations/{registration_id}/report.pdf")
def download_registration_report(
    patient_id: str,
    registration_id: str,
    db: Session = Depends(get_db),
    identity=Depends(_any_staff),
):
    """Any staff role: a printable PDF summary of one camp visit — patient
    bio, vitals, medical history, and consultation + prescriptions.
    Powers the "Download PDF" button on patient-detail.html."""
    try:
        patient, reg = get_registration_report_data(db, patient_id, registration_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    pdf_bytes = build_registration_pdf(patient, reg)
    filename = f"report_{reg.registration_code}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )