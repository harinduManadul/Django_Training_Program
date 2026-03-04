# devices/schemas.py
from ninja import Schema
from uuid import UUID
from typing import Optional
from datetime import datetime
from telemerty.schemas import DeviceTelemetryOutSchema

class UserSchema(Schema):
    id: int
    username: str
    name: str
    email: str
    role: str

class DeviceCreateSchema(Schema):
    name: str
    type: str
    location: Optional[str] = None
    organization_id: Optional[int] = None

class DeviceUpdateSchema(Schema):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceOutSchema(Schema):
    id: int
    device_id: UUID
    name: str
    type: str
    location: Optional[str]
    is_active: bool
    created_at: datetime
    owner: Optional[UserSchema] = None
    state: Optional[DeviceTelemetryOutSchema] = None
    
class DeviceOutSchemaMydevice(Schema):
    id: int
    device_id: UUID
    name: str
    type: str
    location: Optional[str]
    is_active: bool
    created_at: datetime
    state: Optional[DeviceTelemetryOutSchema] = None

class ErrorSchema(Schema):
    error: str