from typing import Optional
import datetime

from sqlalchemy import CHAR, ForeignKeyConstraint, Index, JSON, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_audit_logs_user'),
        Index('idx_audit_logs_created_at', 'created_at'),
        Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_logs_user', 'user_id')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    user_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    action: Mapped[str] = mapped_column(String(100, 'utf8mb4_general_ci'), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100, 'utf8mb4_general_ci'), nullable=False)
    entity_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    old_value: Mapped[Optional[dict]] = mapped_column(JSON)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON)

    user: Mapped['Users'] = relationship('Users', back_populates='audit_logs')