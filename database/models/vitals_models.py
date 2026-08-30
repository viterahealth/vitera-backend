from typing import Optional
import datetime
import decimal
import enum

from sqlalchemy import CHAR, DECIMAL, Enum, ForeignKeyConstraint, Index, Integer, JSON, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class VitalsBloodSugarType(str, enum.Enum):
    FASTING = 'FASTING'
    RANDOM = 'RANDOM'
    POST_PRANDIAL = 'POST_PRANDIAL'


class Vitals(Base):
    __tablename__ = 'vitals'
    __table_args__ = (
        ForeignKeyConstraint(['measured_by'], ['users.id'], name='fk_vitals_measured_by'),
        ForeignKeyConstraint(['registration_id'], ['camp_registrations.id'], name='fk_vitals_registration'),
        Index('idx_vitals_measured_by', 'measured_by'),
        Index('idx_vitals_registration', 'registration_id')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    registration_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    measured_by: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    measured_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    height_cm: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2))
    weight_kg: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2))
    bmi: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 2))
    systolic_bp: Mapped[Optional[int]] = mapped_column(Integer)
    diastolic_bp: Mapped[Optional[int]] = mapped_column(Integer)
    blood_sugar: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(6, 2))
    blood_sugar_type: Mapped[Optional[VitalsBloodSugarType]] = mapped_column(Enum(VitalsBloodSugarType, values_callable=lambda cls: [member.value for member in cls]))
    temperature_celsius: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(4, 1))
    bone_density_bmd: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(5, 3), comment='g/cm^2, from DEXA scan')
    bone_density_t_score: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(4, 2), comment='DEXA T-score')
    bone_density_z_score: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(4, 2), comment='DEXA Z-score')
    bone_density_site: Mapped[Optional[str]] = mapped_column(String(50, 'utf8mb4_general_ci'), comment='e.g. LUMBAR_SPINE, FEMUR_NECK, HIP')
    bone_density_raw: Mapped[Optional[dict]] = mapped_column(JSON, comment='catch-all for any other fields the DEXA machine outputs')

    users: Mapped['Users'] = relationship('Users', back_populates='vitals')
    registration: Mapped['CampRegistrations'] = relationship('CampRegistrations', back_populates='vitals')

