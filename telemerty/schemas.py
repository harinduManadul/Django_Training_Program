from ninja import Schema
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field

class DeviceSchema(Schema):
    id: int
    device_id: UUID
    name: str
    type: str
    location: Optional[str] = None
    is_active: bool

class DeviceTelemetry(Schema):
    status: str
    cpu: float = Field(..., ge=0, le=100, description="CPU usage percentage (0-100)")
    memory: float = Field(..., ge=0, le=100, description="Memory usage percentage (0-100)")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius (optional)")

class DeviceTelemetryOutSchema(Schema):
    id: int
    #device: DeviceSchema
    timestamp: datetime
    status: str
    cpu: float
    memory: float
    temperature: Optional[float] = None
    
class AlertRuleSchema(Schema):
    id: int
    #device: DeviceSchema
    metric_type: str
    operator: Optional[str] = None
    threshold: Optional[float] = None
    offline_minutes: Optional[int] = None
    severity: str
    is_active: bool
    created_at: datetime
    
class AlertSchema(Schema):
    id: int
    rule: AlertRuleSchema
    device: DeviceSchema
    message: str
    severity: str
    state: str
    triggered_at: datetime

class AlertUpdateSchema(Schema):
    state: str

class ErrorSchema(Schema):
    error: str