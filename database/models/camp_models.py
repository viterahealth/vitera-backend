from typing import Optional
import datetime
import enum

from sqlalchemy import CHAR, Date, Enum, ForeignKeyConstraint, Index, Integer, String, TIMESTAMP, Time, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base

class CampRegistrationsRegistrationSource(str, enum.Enum):
    GOOGLE_FORM = 'GOOGLE_FORM'
    ON_SPOT = 'ON_SPOT'
    STAFF = 'STAFF'


class CampRegistrationsStatus(str, enum.Enum):
    REGISTERED = 'REGISTERED'
    CHECKED_IN = 'CHECKED_IN'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    NO_SHOW = 'NO_SHOW'


class CampSlotsStatus(str, enum.Enum):
    OPEN = 'OPEN'
    FULL = 'FULL'
    CLOSED = 'CLOSED'


class CampsStatus(str, enum.Enum):
    SCHEDULED = 'SCHEDULED'
    ONGOING = 'ONGOING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    

class Camps(Base):
    __tablename__ = 'camps'
    __table_args__ = (
        ForeignKeyConstraint(['society_id'], ['societies.id'], name='fk_camps_society'),
        Index('idx_camps_camp_date', 'camp_date'),
        Index('idx_camps_society', 'society_id'),
        Index('idx_camps_status', 'status'),
        Index('uq_camps_camp_code', 'camp_code', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    society_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    camp_code: Mapped[str] = mapped_column(String(30, 'utf8mb4_general_ci'), nullable=False)
    camp_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    status: Mapped[CampsStatus] = mapped_column(Enum(CampsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'SCHEDULED'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    society: Mapped['Societies'] = relationship('Societies', back_populates='camps')
    camp_slots: Mapped[list['CampSlots']] = relationship('CampSlots', back_populates='camp')
    camp_registrations: Mapped[list['CampRegistrations']] = relationship('CampRegistrations', back_populates='camp')


class CampSlots(Base):
    __tablename__ = 'camp_slots'
    __table_args__ = (
        ForeignKeyConstraint(['camp_id'], ['camps.id'], name='fk_camp_slots_camp'),
        Index('idx_camp_slots_camp', 'camp_id'),
        Index('idx_camp_slots_status', 'status'),
        Index('uq_camp_slots_camp_start', 'camp_id', 'start_time', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    camp_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("'0'"))
    current_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("'0'"))
    status: Mapped[CampSlotsStatus] = mapped_column(Enum(CampSlotsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'OPEN'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    camp: Mapped['Camps'] = relationship('Camps', back_populates='camp_slots')
    camp_registrations: Mapped[list['CampRegistrations']] = relationship('CampRegistrations', back_populates='slot')


class CampRegistrations(Base):
    __tablename__ = 'camp_registrations'
    __table_args__ = (
        ForeignKeyConstraint(['building_id'], ['buildings.id'], name='fk_camp_registrations_building'),
        ForeignKeyConstraint(['camp_id'], ['camps.id'], name='fk_camp_registrations_camp'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_camp_registrations_patient'),
        ForeignKeyConstraint(['slot_id'], ['camp_slots.id'], name='fk_camp_registrations_slot'),
        Index('idx_camp_registrations_building', 'building_id'),
        Index('idx_camp_registrations_camp', 'camp_id'),
        Index('idx_camp_registrations_patient', 'patient_id'),
        Index('idx_camp_registrations_slot', 'slot_id'),
        Index('idx_camp_registrations_status', 'status'),
        Index('uq_camp_registrations_code', 'registration_code', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    registration_code: Mapped[str] = mapped_column(String(30, 'utf8mb4_general_ci'), nullable=False)
    patient_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    camp_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    registration_source: Mapped[CampRegistrationsRegistrationSource] = mapped_column(Enum(CampRegistrationsRegistrationSource, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'ON_SPOT'"))
    status: Mapped[CampRegistrationsStatus] = mapped_column(Enum(CampRegistrationsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'REGISTERED'"))
    registered_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    building_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_general_ci'))
    slot_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_general_ci'))
    checked_in_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)
    service_interest: Mapped[Optional[str]] = mapped_column(String(200, 'utf8mb4_general_ci'))

    building: Mapped[Optional['Buildings']] = relationship('Buildings', back_populates='camp_registrations')
    camp: Mapped['Camps'] = relationship('Camps', back_populates='camp_registrations')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='camp_registrations')
    slot: Mapped[Optional['CampSlots']] = relationship('CampSlots', back_populates='camp_registrations')
    consultations: Mapped[list['Consultations']] = relationship('Consultations', back_populates='registration')
    followups: Mapped[list['Followups']] = relationship('Followups', back_populates='registration')
    medical_history: Mapped[list['MedicalHistory']] = relationship('MedicalHistory', back_populates='registration')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='registration')
    vitals: Mapped[list['Vitals']] = relationship('Vitals', back_populates='registration')