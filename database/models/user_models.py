from typing import Optional
import datetime
import enum

from sqlalchemy import CHAR,  Enum, Index,  String, TIMESTAMP,  text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base

class UsersRole(str, enum.Enum):
    ADMIN = 'ADMIN'
    DOCTOR = 'DOCTOR'
    VOLUNTEER = 'VOLUNTEER'
    COORDINATOR = 'COORDINATOR'


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        Index('idx_users_phone', 'phone'),
        Index('idx_users_role', 'role'),
        Index('uq_users_email', 'email', unique=True)
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    name: Mapped[str] = mapped_column(String(150, 'utf8mb4_general_ci'), nullable=False)
    email: Mapped[str] = mapped_column(String(150, 'utf8mb4_general_ci'), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255, 'utf8mb4_general_ci'), nullable=False)
    role: Mapped[UsersRole] = mapped_column(Enum(UsersRole, values_callable=lambda cls: [member.value for member in cls]), nullable=False)
    is_active: Mapped[int] = mapped_column(TINYINT(1), nullable=False, server_default=text("'1'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    phone: Mapped[Optional[str]] = mapped_column(String(20, 'utf8mb4_general_ci'))

    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='user')
    consultations: Mapped[list['Consultations']] = relationship('Consultations', back_populates='doctor')
    vitals: Mapped[list['Vitals']] = relationship('Vitals', back_populates='users')