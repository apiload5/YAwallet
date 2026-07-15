from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from apps.accounts.models import User, KYCDocument
from apps.accounts.serializers import UserSerializer

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    
    list_display = [
        'full_name', 'phone', 'email', 'kyc_status', 
        'is_blocked', 'is_active', 'created_at'
    ]
    list_filter = ['kyc_status', 'is_blocked', 'is_active', 'created_at']
    search_fields = ['phone', 'full_name', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('phone', 'full_name', 'email', 'password')}),
        ('KYC Status', {'fields': ('kyc_status', 'kyc_rejection_reason')}),
        ('Security', {'fields': ('is_blocked', 'block_reason', 'is_active')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']
    
    actions = ['approve_kyc', 'reject_kyc', 'block_users', 'unblock_users']
    
    def approve_kyc(self, request, queryset):
        """Approve KYC for selected users"""
        for user in queryset:
            if user.kyc_status == 'PENDING':
                user.kyc_status = 'APPROVED'
                user.kyc_verified_at = timezone.now()
                user.save(update_fields=['kyc_status', 'kyc_verified_at'])
        self.message_user(request, f"{queryset.count()} users KYC approved.")
    approve_kyc.short_description = "Approve KYC for selected users"
    
    def reject_kyc(self, request, queryset):
        """Reject KYC for selected users"""
        for user in queryset:
            if user.kyc_status == 'PENDING':
                user.kyc_status = 'REJECTED'
                user.save(update_fields=['kyc_status'])
        self.message_user(request, f"{queryset.count()} users KYC rejected.")
    reject_kyc.short_description = "Reject KYC for selected users"
    
    def block_users(self, request, queryset):
        """Block selected users"""
        for user in queryset:
            user.block("Blocked by admin")
        self.message_user(request, f"{queryset.count()} users blocked.")
    block_users.short_description = "Block selected users"
    
    def unblock_users(self, request, queryset):
        """Unblock selected users"""
        for user in queryset:
            user.unblock()
        self.message_user(request, f"{queryset.count()} users unblocked.")
    unblock_users.short_description = "Unblock selected users"

@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    """Admin for KYC documents"""
    
    list_display = ['user', 'document_type', 'status', 'created_at']
    list_filter = ['status', 'document_type', 'created_at']
    search_fields = ['user__phone', 'user__full_name']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['verify_documents', 'reject_documents']
    
    def verify_documents(self, request, queryset):
        """Verify selected documents"""
        for doc in queryset:
            doc.status = 'VERIFIED'
            doc.verified_at = timezone.now()
            doc.save(update_fields=['status', 'verified_at'])
        self.message_user(request, f"{queryset.count()} documents verified.")
    verify_documents.short_description = "Verify selected documents"
    
    def reject_documents(self, request, queryset):
        """Reject selected documents"""
        for doc in queryset:
            doc.status = 'REJECTED'
            doc.save(update_fields=['status'])
        self.message_user(request, f"{queryset.count()} documents rejected.")
    reject_documents.short_description = "Reject selected documents"
