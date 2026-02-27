from django.contrib import admin
from telemerty.models import DeviceTelemetry, Alert, AlertRule


class DeviceTelemetryAdmin(admin.ModelAdmin):
    list_display = ['device', 'status', 'cpu', 'memory', 'temperature', 'timestamp']
    list_filter = ['status', 'timestamp', 'device']
    search_fields = ['device__name', 'device__device_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Device Info', {
            'fields': ('device',)
        }),
        ('Metrics', {
            'fields': ('cpu', 'memory', 'temperature', 'status')
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )


class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['device', 'metric_type', 'operator', 'threshold', 'severity', 'is_active', 'created_at']
    list_filter = ['metric_type', 'severity', 'is_active', 'created_at']
    search_fields = ['device__name', 'device__device_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Device & Rule Type', {
            'fields': ('device', 'metric_type')
        }),
        ('Threshold Configuration', {
            'fields': ('operator', 'threshold', 'offline_minutes'),
            'description': 'Configure when this rule should trigger'
        }),
        ('Alert Settings', {
            'fields': ('severity', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class AlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'rule', 'severity', 'state', 'triggered_at']
    list_filter = ['state', 'severity', 'triggered_at']
    search_fields = ['device__name', 'rule__metric_type', 'message']
    readonly_fields = ['triggered_at', 'rule', 'device']
    
    fieldsets = (
        ('Alert Details', {
            'fields': ('rule', 'device', 'message', 'severity')
        }),
        ('State Management', {
            'fields': ('state',)
        }),
        ('Metadata', {
            'fields': ('triggered_at',),
            'classes': ('collapse',)
        }),
    )


admin.site.register(DeviceTelemetry, DeviceTelemetryAdmin)
admin.site.register(AlertRule, AlertRuleAdmin)
admin.site.register(Alert, AlertAdmin)