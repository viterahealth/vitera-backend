from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from database.models.camp_models import CampRegistrationsStatus
from database.models.patient_models import PatientsGender  
class MemberCreate(BaseModel):
    name: str
    phone: str | None = None
    gender: PatientsGender | None = None
    date_of_birth: date | None = None


class CampRegistrationCreate(BaseModel):
    """
    Matches a public registration-form submission, e.g.:

    {
        "slot": "11:00 AM – 12:00 PM",
        "email": "abc@gmail.com",
        "members": [{"name": "Jms 1", "phone": null, "gender": "MALE", "date_of_birth": null}, ...],
        "Flat Number": "G-602",
        "service_interest": "Lifestyle / nutrition guidance"
    }
    """
    model_config = ConfigDict(populate_by_name=True)

    slot: str
    email: EmailStr
    members: list[MemberCreate]
    flat_number: str | None = Field(default=None, alias="Flat Number")
    service_interest: str | None = None


class RegisteredMember(BaseModel):
    id: str
    name: str
    registration_id: str
    registration_code: str


class CampRegistrationResult(BaseModel):
    camp_id: str
    slot_id: str
    members: list[RegisteredMember]


class CampRegistrationResponse(BaseModel):
    success: bool
    message: str
    data: CampRegistrationResult


class RegistrationSearchResult(BaseModel):
    registration_id: str
    registration_code: str
    patient_id: str
    patient_name: str
    phone: str | None
    status: CampRegistrationsStatus
    slot_label: str | None


class RegistrationSearchResponse(BaseModel):
    success: bool
    message: str
    data: list[RegistrationSearchResult]


class CheckInResult(BaseModel):
    registration_id: str
    registration_code: str
    patient_name: str
    status: CampRegistrationsStatus
    checked_in_at: datetime


class CheckInResponse(BaseModel):
    success: bool
    message: str
    data: CheckInResult