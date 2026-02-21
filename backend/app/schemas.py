import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, field_validator


class HuntSessionResponse(BaseModel):
    id: uuid.UUID
    session_date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class HuntSessionDetail(HuntSessionResponse):
    qsos: list["QSOResponse"] = []


class QSOCreate(BaseModel):
    park_reference: str
    callsign: str
    frequency: float
    band: str
    mode: str
    rst_sent: str
    rst_received: str


class QSOResponse(BaseModel):
    id: uuid.UUID
    hunt_session_id: uuid.UUID
    park_reference: str
    callsign: str
    frequency: float
    band: str
    mode: str
    rst_sent: str
    rst_received: str
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("timestamp", "created_at", mode="before")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class SettingsCreate(BaseModel):
    operator_callsign: str
    flrig_host: str = "localhost"
    flrig_port: int = 12345


class SettingsResponse(BaseModel):
    id: uuid.UUID
    operator_callsign: str
    flrig_host: str
    flrig_port: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
