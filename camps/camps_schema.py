from datetime import date, time

from pydantic import BaseModel

from database.models.camp_models import CampsStatus, CampSlotsStatus  
from database.models.society_models import SocietiesStatus


# ---------- Societies ----------

class SocietyCreate(BaseModel):
    name: str
    address: str | None = None
    area: str | None = None
    city: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None


class SocietyData(BaseModel):
    id: str
    name: str
    status: SocietiesStatus
    address: str | None
    area: str | None
    city: str | None
    contact_person: str | None
    contact_phone: str | None

    class Config:
        from_attributes = True


class SocietyResponse(BaseModel):
    success: bool
    message: str
    data: SocietyData


class SocietyListResponse(BaseModel):
    success: bool
    message: str
    data: list[SocietyData]


# ---------- Camps ----------

class CampCreate(BaseModel):
    society_id: str
    camp_code: str
    camp_date: date
    start_time: time
    end_time: time


class CampData(BaseModel):
    id: str
    society_id: str
    camp_code: str
    camp_date: date
    start_time: time
    end_time: time
    status: CampsStatus

    class Config:
        from_attributes = True


class CampResponse(BaseModel):
    success: bool
    message: str
    data: CampData


class CampListResponse(BaseModel):
    success: bool
    message: str
    data: list[CampData]


# ---------- Camp slots ----------

class CampSlotCreate(BaseModel):
    start_time: time
    end_time: time
    max_capacity: int


class CampSlotData(BaseModel):
    id: str
    camp_id: str
    start_time: time
    end_time: time
    max_capacity: int
    current_count: int
    status: CampSlotsStatus

    class Config:
        from_attributes = True


class CampSlotResponse(BaseModel):
    success: bool
    message: str
    data: CampSlotData


class CampSlotListResponse(BaseModel):
    success: bool
    message: str
    data: list[CampSlotData]


# ---------- Camp detail (camp + its slots together) ----------

class CampDetailData(CampData):
    slots: list[CampSlotData]


class CampDetailResponse(BaseModel):
    success: bool
    message: str
    data: CampDetailData