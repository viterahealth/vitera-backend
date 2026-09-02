from typing import Optional
import datetime
import enum

from sqlalchemy import CHAR, Computed, Enum, ForeignKeyConstraint, Index, String, TIMESTAMP, text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class PatientsGender(str, enum.Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class Patients(Base):
    __tablename__ = 'patients'
    __table_args__ = (
        ForeignKeyConstraint(['family_id'], ['families.id'], name='fk_patients_family'),
        Index('idx_patients_dob_or_age', 'dob_or_age'),
        Index('idx_patients_family', 'family_id'),
        Index('idx_patients_name', 'first_name', 'last_name'),
        Index('idx_patients_phone', 'phone'),
        Index('uq_patients_patient_code', 'patient_code', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True, server_default=text('(uuid())'))
    first_name: Mapped[str] = mapped_column(String(100, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    patient_seq_num: Mapped[int] = mapped_column(BIGINT(unsigned=True), nullable=False, server_default=text('(nextval(`vitera`.`patient_seq`))'))
    family_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_general_ci'))
    last_name: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_general_ci'))
    dob_or_age: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='exact DOB as ISO date (2006-12-29) or a plain age number (45) when only age is known')
    gender: Mapped[Optional[PatientsGender]] = mapped_column(Enum(PatientsGender, values_callable=lambda cls: [member.value for member in cls]))
    phone: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb4_general_ci'))
    email: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb4_general_ci'))
    address: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb4_general_ci'))
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb4_general_ci'))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb4_general_ci'))
    # generated (VIRTUAL) column -- never set this from application code, MySQL/TiDB computes it
    patient_code: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb4_general_ci'), Computed("(concat(_utf8mb4'P-', lpad(`patient_seq_num`, 4, _utf8mb4'0')))", persisted=False))
    flat_number: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb4_general_ci'))

    families_primary_patient: Mapped[list['Families']] = relationship('Families', foreign_keys='[Families.primary_patient_id]', back_populates='primary_patient')
    family: Mapped[Optional['Families']] = relationship('Families', foreign_keys=[family_id], back_populates='patients_family')
    camp_registrations: Mapped[list['CampRegistrations']] = relationship('CampRegistrations', back_populates='patient')
    followups: Mapped[list['Followups']] = relationship('Followups', back_populates='patient')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='patient')