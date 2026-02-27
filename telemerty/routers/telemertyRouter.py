from typing import Optional
from ninja import Router

from django.shortcuts import get_object_or_404
from devices.models import Device
from ..models import Alert, AlertRule, DeviceTelemetry
from ..schemas import AlertRuleSchema
from ..schemas import DeviceTelemetryOutSchema, AlertSchema, AlertUpdateSchema
from ..schemas import DeviceTelemetry as DeviceTelemetryCreateSchema
from ..services import evaluate_rules
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


@router.post("/evaluate-rules/{device_id}/", auth=JWTAuth())
def evaluate_device_rules(request, device_id: int, payload: AlertRuleSchema):
    device = get_object_or_404(Device, id=device_id, owner=request.auth)
    rule = AlertRule.objects.create(
        device=device,
        metric_type=payload.metric_type,
        operator=payload.operator,
        threshold=payload.threshold,
        offline_minutes=payload.offline_minutes,
        severity=payload.severity
    )
    return rule

@router.get("/alert-rules/{device_id}/", response=list[AlertRuleSchema], auth=JWTAuth())
@roles_allowed("admin", "user")
def get_alert_rules(request, device_id: int):
    user = request.auth
    device = get_object_or_404(Device, id=device_id, owner=user)
    rules = AlertRule.objects.filter(device=device, is_active=True)
    return rules

@router.delete("/alert-rules/{rule_id}/", auth=JWTAuth())
@roles_allowed("admin", "user")
def delete_alert_rule(request, rule_id: int):
    user = request.auth
    rule = get_object_or_404(AlertRule, id=rule_id, device__owner=user)
    rule.delete()
    return {"message": "Alert rule deleted successfully"}

@router.put("/alert-rules/{rule_id}/", response=AlertRuleSchema, auth=JWTAuth())
@roles_allowed("admin", "user")
def update_alert_rule(request, rule_id: int, payload: AlertRuleSchema):
    user = request.auth
    rule = get_object_or_404(AlertRule, id=rule_id, device__owner=user)
    rule.metric_type = payload.metric_type
    rule.operator = payload.operator
    rule.threshold = payload.threshold
    rule.offline_minutes = payload.offline_minutes
    rule.severity = payload.severity
    rule.save()
    return rule