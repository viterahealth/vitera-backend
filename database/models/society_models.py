from typing import Optional
import datetime
import enum


from sqlalchemy import CHAR, Enum, Index, String, TIMESTAMP, text,ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base

class SocietiesStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class Societies(Base):
    __tablename__ = 'societies'
    __table_args__ = (
        Index('idx_societies_city', 'city'),
        Index('idx_societies_status', 'status')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    name: Mapped[str] = mapped_column(String(200, 'utf8mb4_general_ci'), nullable=False)
    status: Mapped[SocietiesStatus] = mapped_column(Enum(SocietiesStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    address: Mapped[Optional[str]] = mapped_column(String(500, 'utf8mb4_general_ci'))
    area: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb4_general_ci'))
    city: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb4_general_ci'))
    contact_person: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb4_general_ci'))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb4_general_ci'))

    buildings: Mapped[list['Buildings']] = relationship('Buildings', back_populates='society')
    camps: Mapped[list['Camps']] = relationship('Camps', back_populates='society')    



class Buildings(Base):
    __tablename__ = 'buildings'
    __table_args__ = (
        ForeignKeyConstraint(['society_id'], ['societies.id'], name='fk_buildings_society'),
        Index('idx_buildings_society', 'society_id'),
        Index('uq_buildings_society_name', 'society_id', 'name', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    society_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    name: Mapped[str] = mapped_column(String(150, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    society: Mapped['Societies'] = relationship('Societies', back_populates='buildings')
    camp_registrations: Mapped[list['CampRegistrations']] = relationship('CampRegistrations', back_populates='building')

