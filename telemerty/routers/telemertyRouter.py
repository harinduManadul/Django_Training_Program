from typing import Optional
from ninja import Router

from django.shortcuts import get_object_or_404
from devices.models import Device
from ..models import Alert, AlertRule, DeviceTelemetry
from ..schemas import DeviceTelemetryOutSchema, AlertSchema, AlertUpdateSchema
from ..schemas import DeviceTelemetry as DeviceTelemetryCreateSchema
from users.auth import JWTAuth, roles_allowed

router = Router()

@router.post("/device/{device_id}/status/", response=DeviceTelemetryOutSchema)
def device_status(request, device_id: int, payload: Optional[DeviceTelemetryCreateSchema] = None):

    limit: int = 50
    device = get_object_or_404(Device, id=device_id)
    
    if payload:
        telemetry = DeviceTelemetry.objects.create(
            device=device,
            status=payload.status,
            cpu=payload.cpu,
            memory=payload.memory,
            temperature=payload.temperature
        )
        # Evaluate alert rules after creating telemetry
        evaluate_rules(device, telemetry)
        return telemetry
    
    qs = DeviceTelemetry.objects.filter(device=device)\
        .order_by("-timestamp")

    if qs.count() > 50:
        ids_to_delete = qs.values_list("id", flat=True)[50:]
        DeviceTelemetry.objects.filter(id__in=ids_to_delete).delete()
    
    telemetry_data = DeviceTelemetry.objects.filter(device=device).order_by('-timestamp')[:limit]
    return telemetry_data[0] if telemetry_data else None

@router.get("/device/{device_id}/status/", response=list[DeviceTelemetryOutSchema], auth=JWTAuth())
@roles_allowed("admin", "user")
def get_device_status(request, device_id: int):
    limit: int = 50
    user = request.auth
    device = get_object_or_404(Device, id=device_id, owner=user)
    
    telemetry_data = DeviceTelemetry.objects.filter(device=device).order_by('-timestamp')[:limit]
    return telemetry_data

@router.get("/device/{device_id}/status/latest/", response=DeviceTelemetryOutSchema, auth=JWTAuth())
@roles_allowed("admin", "user")
def get_latest_device_status(request, device_id: int):
    user = request.auth
    device = get_object_or_404(Device, id=device_id, owner=user)
    latest_telemetry = DeviceTelemetry.objects.filter(device=device).order_by('-timestamp').first()
    return latest_telemetry

@router.get("/alerts", response=list[AlertSchema])
def list_alerts(request, state: Optional[str] = None, device_id: Optional[int] = None):
    qs = Alert.objects.all()

    if state:
        qs = qs.filter(state=state)

    if device_id:
        qs = qs.filter(device_id=device_id)

    return qs


@router.patch("/alerts/{alert_id}", response=AlertSchema)
def update_alert(request, alert_id: int, payload: AlertUpdateSchema):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.state = payload.state
    alert.save()
    return alert


# Alert evaluation logic (can be called after saving new telemetry)

def evaluate_rules(device, telemetry):
    from django.utils import timezone
    from datetime import timedelta

    rules = AlertRule.objects.filter(device=device, is_active=True)

    for rule in rules:

        triggered = False
        message = ""

        if rule.metric_type == AlertRule.MetricType.CPU:
            value = telemetry.cpu
            triggered = compare(value, rule.operator, rule.threshold)
            message = f"CPU is {value}% (threshold {rule.operator} {rule.threshold})"

        elif rule.metric_type == AlertRule.MetricType.TEMPERATURE:
            value = telemetry.temperature
            triggered = compare(value, rule.operator, rule.threshold)
            message = f"Temperature is {value}°C"

        elif rule.metric_type == AlertRule.MetricType.OFFLINE:
            latest = device.telemetry.order_by("-timestamp").first()
            if not latest or latest.timestamp < timezone.now() - timedelta(minutes=rule.offline_minutes):
                triggered = True
                message = f"Device offline for {rule.offline_minutes}+ minutes"
                
        elif rule.metric_type == AlertRule.MetricType.MEMORY:
            value = telemetry.memory
            triggered = compare(value, rule.operator, rule.threshold)
            message = f"Memory usage is {value}% (threshold {rule.operator} {rule.threshold})"

        if triggered:
            Alert.objects.create(
                rule=rule,
                device=device,
                message=message,
                severity=rule.severity,
            )


def compare(value, operator, threshold):
    if operator == ">":
        return value > threshold
    if operator == "<":
        return value < threshold
    if operator == ">=":
        return value >= threshold
    if operator == "<=":
        return value <= threshold
    if operator == "=":
        return value == threshold
    return False