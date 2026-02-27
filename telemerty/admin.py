from django.contrib import admin

from telemerty.models import DeviceTelemetry, Alert, AlertRule

# Register your models here.
admin.site.register(DeviceTelemetry)
admin.site.register(Alert)
admin.site.register(AlertRule)