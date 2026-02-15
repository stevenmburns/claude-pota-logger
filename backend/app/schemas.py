import uuid
from datetime import datetime

from pydantic import BaseModel


class ActivationCreate(BaseModel):
    park_reference: str
    operator_callsign: str
    start_time: datetime


class ActivationResponse(BaseModel):
    id: uuid.UUID
    park_reference: str
    operator_callsign: str
    start_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivationDetail(ActivationResponse):
    qsos: list["QSOResponse"] = []


class QSOCreate(BaseModel):
    callsign: str
    frequency: float
    band: str
    mode: str
    rst_sent: str
    rst_received: str
    timestamp: datetime


class QSOResponse(BaseModel):
    id: uuid.UUID
    activation_id: uuid.UUID
    callsign: str
    frequency: float
    band: str
    mode: str
    rst_sent: str
    rst_received: str
    timestamp: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
