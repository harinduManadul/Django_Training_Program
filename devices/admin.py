from django.contrib import admin
from devices.models import Device


class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_id', 'type', 'owner', 'location', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'device_id', 'owner__username']
    readonly_fields = ['device_id', 'created_at', 'get_telemetry_display']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('name', 'device_id', 'type', 'location')
        }),
        ('Owner & Status', {
            'fields': ('owner', 'is_active')
        }),
        ('Latest Telemetry', {
            'fields': ('get_telemetry_display',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description="Latest Telemetry")
    def get_telemetry_display(self, obj):
        """Display latest telemetry for this device"""
        latest = obj.device_telemetry.first()
        if latest:
            return f"Status: {latest.status} | CPU: {latest.cpu}% | Memory: {latest.memory}% | Temp: {latest.temperature}°C | Time: {latest.timestamp}"
        return "No telemetry data yet"


admin.site.register(Device, DeviceAdmin)