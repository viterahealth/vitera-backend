from typing import Optional
import datetime

from sqlalchemy import CHAR, ForeignKeyConstraint, Index, String, TIMESTAMP, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class Consultations(Base):
    __tablename__ = 'consultations'
    __table_args__ = (
        ForeignKeyConstraint(['doctor_id'], ['users.id'], name='fk_consultations_doctor'),
        ForeignKeyConstraint(['registration_id'], ['camp_registrations.id'], name='fk_consultations_registration'),
        Index('idx_consultations_doctor', 'doctor_id'),
        Index('idx_consultations_registration', 'registration_id')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    registration_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    doctor_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    clinical_observations: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    diagnosis: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    doctor_notes: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    recommendations: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))

    doctor: Mapped['Users'] = relationship('Users', back_populates='consultations')
    registration: Mapped['CampRegistrations'] = relationship('CampRegistrations', back_populates='consultations')
    prescriptions: Mapped[list['Prescriptions']] = relationship('Prescriptions', back_populates='consultation')


class Prescriptions(Base):
    __tablename__ = 'prescriptions'
    __table_args__ = (
        ForeignKeyConstraint(['consultation_id'], ['consultations.id'], name='fk_prescriptions_consultation'),
        Index('idx_prescriptions_consultation', 'consultation_id')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    consultation_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    medicine_name: Mapped[str] = mapped_column(String(200, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    dosage: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_general_ci'))
    frequency: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_general_ci'))
    duration: Mapped[Optional[str]] = mapped_column(String(100, 'utf8mb4_general_ci'))
    instructions: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))

    consultation: Mapped['Consultations'] = relationship('Consultations', back_populates='prescriptions')