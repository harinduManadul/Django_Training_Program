from django.db import models
from devices.models import Device
from django.utils import timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import ForeignKey
    from devices.models import Device

class DeviceTelemetry(models.Model):
    STATUS_CHOICES = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
        ("DEGRADED", "Degraded"),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_telemetry', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    cpu = models.FloatField(default=0.0)
    memory = models.FloatField(default=0.0)
    temperature = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        db_table = 'device_telemetry'

    def __str__(self):
        return f"{self.device.name} - {self.status} at {self.timestamp}"


class AlertRule(models.Model):
    class MetricType(models.TextChoices):
        CPU = "CPU"
        MEMORY = "MEMORY"
        TEMPERATURE = "TEMPERATURE"
        OFFLINE = "OFFLINE"

    class Operator(models.TextChoices):
        GT = ">"
        LT = "<"
        GTE = ">="
        LTE = "<="
        EQ = "="

    class Severity(models.TextChoices):
        LOW = "LOW"
        MEDIUM = "MEDIUM"
        HIGH = "HIGH"

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=20, choices=MetricType.choices)
    operator = models.CharField(max_length=5, choices=Operator.choices, blank=True, null=True)
    threshold = models.FloatField(blank=True, null=True)

    offline_minutes = models.IntegerField(blank=True, null=True)

    severity = models.CharField(max_length=10, choices=Severity.choices)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alert_rule'

class Alert(models.Model):
    class State(models.TextChoices):
        OPEN = "OPEN"
        ACKNOWLEDGED = "ACKNOWLEDGED"
        RESOLVED = "RESOLVED"

    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    triggered_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    severity = models.CharField(max_length=10, choices=AlertRule.Severity.choices)
    state = models.CharField(max_length=20, choices=State.choices, default=State.OPEN)

    def __str__(self):
        return f"{self.device} - {self.severity} - {self.state}"