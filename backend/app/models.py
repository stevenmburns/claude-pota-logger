import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class HuntSession(Base):
    __tablename__ = "hunt_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_date: Mapped[date] = mapped_column(Date, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    qsos: Mapped[list["QSO"]] = relationship(
        back_populates="hunt_session", cascade="all, delete-orphan"
    )


class QSO(Base):
    __tablename__ = "qsos"
    __table_args__ = (
        UniqueConstraint(
            "hunt_session_id", "callsign", "park_reference", "band",
            name="uq_qso_session_call_park_band",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hunt_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunt_sessions.id")
    )
    park_reference: Mapped[str] = mapped_column(String(20))
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

    hunt_session: Mapped["HuntSession"] = relationship(back_populates="qsos")


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    operator_callsign: Mapped[str] = mapped_column(String(20), default="")
    flrig_host: Mapped[str] = mapped_column(String(100), default="host.docker.internal")
    flrig_port: Mapped[int] = mapped_column(Integer, default=12345)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
