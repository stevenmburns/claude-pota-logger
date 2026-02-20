import uuid
from datetime import date, datetime

from pydantic import BaseModel


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
    timestamp: datetime


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
