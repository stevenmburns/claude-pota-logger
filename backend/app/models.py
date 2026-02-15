import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Activation(Base):
    __tablename__ = "activations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    park_reference: Mapped[str] = mapped_column(String(20))
    operator_callsign: Mapped[str] = mapped_column(String(20))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    qsos: Mapped[list["QSO"]] = relationship(
        back_populates="activation", cascade="all, delete-orphan"
    )


class QSO(Base):
    __tablename__ = "qsos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    activation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activations.id")
    )
    callsign: Mapped[str] = mapped_column(String(20))
    frequency: Mapped[float] = mapped_column(Numeric(10, 4))
    band: Mapped[str] = mapped_column(String(10))
    mode: Mapped[str] = mapped_column(String(10))
    rst_sent: Mapped[str] = mapped_column(String(10))
    rst_received: Mapped[str] = mapped_column(String(10))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    activation: Mapped["Activation"] = relationship(back_populates="qsos")
