from typing import Optional
import datetime
import enum

from sqlalchemy import CHAR, Date, Enum, ForeignKeyConstraint, Index, String, TIMESTAMP, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class FollowupsStatus(str, enum.Enum):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


class Followups(Base):
    __tablename__ = 'followups'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_followups_patient'),
        ForeignKeyConstraint(['registration_id'], ['camp_registrations.id'], name='fk_followups_registration'),
        Index('idx_followups_patient', 'patient_id'),
        Index('idx_followups_registration', 'registration_id'),
        Index('idx_followups_scheduled_date', 'scheduled_date'),
        Index('idx_followups_status', 'status')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    patient_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    followup_type: Mapped[str] = mapped_column(String(100, 'utf8mb4_general_ci'), nullable=False)
    status: Mapped[FollowupsStatus] = mapped_column(Enum(FollowupsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'PENDING'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    registration_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_general_ci'))
    scheduled_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)

    patient: Mapped['Patients'] = relationship('Patients', back_populates='followups')
    registration: Mapped[Optional['CampRegistrations']] = relationship('CampRegistrations', back_populates='followups')