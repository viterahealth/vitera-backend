from typing import Optional
import datetime
import enum

from sqlalchemy import CHAR, Enum, ForeignKeyConstraint, Index, String, TIMESTAMP, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_session import Base


class NotificationsChannel(str, enum.Enum):
    WHATSAPP = 'WHATSAPP'
    SMS = 'SMS'
    EMAIL = 'EMAIL'


class NotificationsStatus(str, enum.Enum):
    PENDING = 'PENDING'
    SENT = 'SENT'
    FAILED = 'FAILED'
    DELIVERED = 'DELIVERED'


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_notifications_patient'),
        ForeignKeyConstraint(['registration_id'], ['camp_registrations.id'], name='fk_notifications_registration'),
        Index('idx_notifications_channel', 'channel'),
        Index('idx_notifications_patient', 'patient_id'),
        Index('idx_notifications_registration', 'registration_id'),
        Index('idx_notifications_status', 'status')
    )

    id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), primary_key=True)
    patient_id: Mapped[str] = mapped_column(CHAR(36, 'utf8mb4_general_ci'), nullable=False)
    channel: Mapped[NotificationsChannel] = mapped_column(Enum(NotificationsChannel, values_callable=lambda cls: [member.value for member in cls]), nullable=False)
    notification_type: Mapped[str] = mapped_column(String(100, 'utf8mb4_general_ci'), nullable=False)
    status: Mapped[NotificationsStatus] = mapped_column(Enum(NotificationsStatus, values_callable=lambda cls: [member.value for member in cls]), nullable=False, server_default=text("'PENDING'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    registration_id: Mapped[Optional[str]] = mapped_column(CHAR(36, 'utf8mb4_general_ci'))
    message: Mapped[Optional[str]] = mapped_column(Text(collation='utf8mb4_general_ci'))
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(150, 'utf8mb4_general_ci'))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP)

    patient: Mapped['Patients'] = relationship('Patients', back_populates='notifications')
    registration: Mapped[Optional['CampRegistrations']] = relationship('CampRegistrations', back_populates='notifications')