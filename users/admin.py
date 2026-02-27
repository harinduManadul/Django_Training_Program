from django.contrib import admin

from users.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'username', 'email', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['name', 'username', 'email']
    readonly_fields = ['get_created_devices_display']
    fieldsets = (
        ('User Information', {
            'fields': ('name', 'username', 'email', 'role')
        }),
        ('Devices Created by User', {
            'fields': ('get_created_devices_display',)
        }),
    )
    
    @admin.display(description="Devices Created")
    def get_created_devices_display(self, obj):
        """Display only devices created by this user"""
        devices = obj.devices.all()
        if devices:
            return '\n'.join([f"• {device.name} - {device.device_id}" for device in devices])
        return "No devices created"

admin.site.register(User, UserAdmin)