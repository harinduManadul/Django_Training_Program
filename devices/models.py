from django.db import models

# Create your models here.

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from users.models import User as UserModel
#from organizations.models import Organization

User = get_user_model()

class Device(models.Model):
    DEVICE_TYPES = [
        ("sensor", "Sensor"),
        ("camera", "Camera"),
        ("kiosk", "Kiosk"),
    ]

    name: models.CharField = models.CharField(max_length=100)
    device_id: models.UUIDField = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    owner: models.ForeignKey = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="devices",
        null=True,
        blank=True
    )
    
    telemetry: models.ForeignKey = models.ForeignKey(
        'telemerty.DeviceTelemetry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices"
    )

    # organization = models.ForeignKey(
    #     Organization,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="devices"
    # )

    type: models.CharField = models.CharField(max_length=20, choices=DEVICE_TYPES)
    location: models.CharField = models.CharField(max_length=255, blank=True, null=True)
    is_active: models.BooleanField = models.BooleanField(default=True)

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.device_id}"