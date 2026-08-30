from typing import Optional
import datetime
import enum


from sqlalchemy import CHAR, ForeignKeyConstraint, Index, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base

class Families(Base):
    __tablename__ = 'families'
    __table_args__ = (
        ForeignKeyConstraint(['primary_patient_id'], ['patients.id'], name='fk_families_primary_patient'),
        Index('idx_families_primary_patient', 'primary_patient_id'),
        Index('uq_families_family_code', 'family_code', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    family_code: Mapped[str] = mapped_column(String(30, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    primary_patient_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_general_ci'))

    primary_patient: Mapped[Optional['Patients']] = relationship('Patients', foreign_keys=[primary_patient_id], back_populates='families_primary_patient')
    patients_family: Mapped[list['Patients']] = relationship('Patients', foreign_keys='[Patients.family_id]', back_populates='family')

