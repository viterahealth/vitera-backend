from typing import Optional
import datetime

from sqlalchemy import CHAR, ForeignKeyConstraint, Index, TIMESTAMP, Text, text, JSON
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class MedicalHistory(Base):
    __tablename__ = 'medical_history'
    __table_args__ = (
        ForeignKeyConstraint(['registration_id'], ['camp_registrations.id'], name='fk_medical_history_registration'),
        Index('idx_medical_history_registration', 'registration_id')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    registration_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    has_diabetes: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    has_hypertension: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    has_tb: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    has_asthma_copd: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    has_cardiac_disease: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    has_renal_disease: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    has_liver_disease: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"))
    existing_conditions: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    current_medications: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    allergies: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    past_surgeries: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    family_history: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    lifestyle_notes: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    other_major_illnesses: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    past_history_details: Mapped[Optional[dict]] = mapped_column(JSON, comment='previous similar illness, hospitalizations, transfusions, trauma, psychiatric history')
    drug_allergy_details: Mapped[Optional[dict]] = mapped_column(JSON, comment='recent meds, dose/duration, compliance, OTC/herbal, allergy reaction details')
    personal_history: Mapped[Optional[dict]] = mapped_column(JSON, comment='diet, sleep, bowel/bladder, smoking, alcohol, occupation, activity, sexual history')
    social_environmental: Mapped[Optional[dict]] = mapped_column(JSON, comment='living conditions, housing, sanitation, travel, sick contacts, pets, socioeconomic')
    menstrual_obstetric: Mapped[Optional[dict]] = mapped_column(JSON, comment='nullable -- only populated when clinically relevant')

    registration: Mapped['CampRegistrations'] = relationship('CampRegistrations', back_populates='medical_history')
