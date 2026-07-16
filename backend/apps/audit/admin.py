from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for Audit Logs"""
    
    list_display = ['action', 'user', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__phone', 'user__full_name', 'action']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'metadata', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
