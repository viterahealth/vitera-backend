import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from database.models.camp_models import CampRegistrationsStatus
from database.models.patient_models import PatientsGender

_AGE_RE = re.compile(r"\d{1,3}")


def _normalize_dob_or_age(raw) -> str | None:
    """
    The source form field is labeled 'DOB / Age' -- it can contain either
    an exact birthdate or a plain age number. We don't fabricate an exact
    date out of an age (that would be false precision), so this just
    normalizes whichever was given into one honest string:
      - a real date  -> ISO format, e.g. '2006-12-29'
      - a plain age  -> the digits as a string, e.g. '45'
      - empty/None   -> None
    Anything else raises a clear validation error rather than silently
    storing garbage.
    """
    if raw is None:
        return None
    if isinstance(raw, int):
        if 0 < raw < 130:
            return str(raw)
        raise ValueError(f"Age out of plausible range: {raw}")
    if not isinstance(raw, str):
        return None

    raw = raw.strip()
    if raw == "" or raw.lower() in ("none", "null"):
        return None

    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue

    match = _AGE_RE.search(raw)
    if match:
        age = int(match.group())
        if 0 < age < 130:  # sanity bound against obvious garbage
            return str(age)

    raise ValueError(f"Could not interpret DOB/Age value: '{raw}'")


class MemberCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    phone: str | None = None
    gender: PatientsGender | None = None
    # incoming JSON key stays "date_of_birth" (alias) so the Make.com
    # scenario doesn't need to change -- internally it's dob_or_age,
    # matching the patients.dob_or_age column
    dob_or_age: str | None = Field(default=None, alias="date_of_birth")

    @field_validator("dob_or_age", mode="before")
    @classmethod
    def normalize_dob_or_age(cls, v):
        return _normalize_dob_or_age(v)

    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, v):
        """Make.com sends 'Male'/'Female' -- our enum is 'MALE'/'FEMALE'/'OTHER'."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == "" or v.lower() in ("none", "null"):
                return None
            return v.upper()
        return v


class CampRegistrationCreate(BaseModel):
    """
    Matches a public registration-form submission relayed through Make.com.
    email is optional -- Make.com sends the literal string "None" (not
    JSON null) when the source field is empty, which this schema
    normalizes to a real None.
    """
    model_config = ConfigDict(populate_by_name=True)

    slot: str
    email: EmailStr | None = None
    members: list[MemberCreate]
    flat_number: str | None = Field(default=None, alias="Flat Number")
    service_interest: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v == "" or v.lower() in ("none", "null"):
                return None
        return v


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