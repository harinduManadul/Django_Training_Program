"""
Alert evaluation services for device telemetry monitoring.
Handles alert rule evaluation and alert creation logic.
"""

from django.utils import timezone
from datetime import timedelta
from .models import Alert, AlertRule, DeviceTelemetry
from devices.models import Device


def evaluate_rules(device: Device, telemetry: DeviceTelemetry) -> None:
    """
    Evaluate all active alert rules for a device against the latest telemetry.
    Creates an Alert if any rule is triggered.
    
    Args:
        device: Device instance
        telemetry: DeviceTelemetry instance to evaluate against
    """
    rules = AlertRule.objects.filter(device=device, is_active=True)

    for rule in rules:
        triggered = False
        message = ""

        if rule.metric_type == AlertRule.MetricType.CPU:
            value = telemetry.cpu
            triggered = _compare_metric(value, rule.operator, rule.threshold)
            message = f"CPU is {value}% (threshold {rule.operator} {rule.threshold})"

        elif rule.metric_type == AlertRule.MetricType.MEMORY:
            value = telemetry.memory
            triggered = _compare_metric(value, rule.operator, rule.threshold)
            message = f"Memory usage is {value}% (threshold {rule.operator} {rule.threshold})"

        elif rule.metric_type == AlertRule.MetricType.TEMPERATURE:
            if telemetry.temperature is not None:
                value = telemetry.temperature
                triggered = _compare_metric(value, rule.operator, rule.threshold)
                message = f"Temperature is {value}°C (threshold {rule.operator} {rule.threshold})"

        elif rule.metric_type == AlertRule.MetricType.OFFLINE:
            triggered = _check_offline_status(device, rule.offline_minutes)
            message = f"Device offline for {rule.offline_minutes}+ minutes"

        if triggered:
            # Prevent duplicate alerts for the same rule triggered in quick succession
            recent_alert = Alert.objects.filter(
                rule=rule,
                device=device,
                state=Alert.State.OPEN,
                triggered_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists()
            
            if not recent_alert:
                Alert.objects.create(
                    rule=rule,
                    device=device,
                    message=message,
                    severity=rule.severity,
                    state=Alert.State.OPEN,
                )


def _compare_metric(value: float, operator: str, threshold: float) -> bool:
    """
    Compare a metric value against a threshold using the specified operator.
    
    Args:
        value: The metric value to compare
        operator: Comparison operator (>, <, >=, <=, =)
        threshold: The threshold value to compare against
        
    Returns:
        True if condition is met, False otherwise
    """
    if value is None or threshold is None:
        return False
        
    try:
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "=":
            return value == threshold
        return False
    except (TypeError, ValueError):
        return False


def _check_offline_status(device: Device, offline_minutes: int) -> bool:
    """
    Check if a device is offline (no telemetry in the specified minutes).
    
    Args:
        device: Device instance to check
        offline_minutes: Number of minutes to check for offline status
        
    Returns:
        True if device is offline, False otherwise
    """
    if offline_minutes is None:
        return False
    
    from .models import DeviceTelemetry
    latest_telemetry: DeviceTelemetry | None = DeviceTelemetry.objects.filter(device=device).order_by("-timestamp").first()
    
    if not latest_telemetry:
        return True
    
    time_threshold = timezone.now() - timedelta(minutes=offline_minutes)
    return bool(latest_telemetry.timestamp < time_threshold)


def acknowledge_alert(alert: Alert) -> Alert:
    """
    Acknowledge an alert by changing its state to ACKNOWLEDGED.
    
    Args:
        alert: Alert instance to acknowledge
        
    Returns:
        Updated Alert instance
    """
    alert.state = Alert.State.ACKNOWLEDGED
    alert.save()
    return alert


def resolve_alert(alert: Alert) -> Alert:
    """
    Resolve an alert by changing its state to RESOLVED.
    
    Args:
        alert: Alert instance to resolve
        
    Returns:
        Updated Alert instance
    """
    alert.state = Alert.State.RESOLVED
    alert.save()
    return alert
