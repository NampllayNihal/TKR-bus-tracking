from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Driver, UserRole


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['hall_ticket', 'get_user_name', 'active_route', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'active_route', 'created_at']
    search_fields = ['hall_ticket', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['verify_students', 'unverify_students']
    
    fieldsets = (
        ('User Connection', {
            'fields': ('user',),
            'description': 'Connected Django user account'
        }),
        ('Student Info', {
            'fields': ('hall_ticket', 'phone', 'active_route'),
        }),
        ('Status', {
            'fields': ('is_verified',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_user_name.short_description = 'Name'
    
    def verify_students(self, request, queryset):
        """Mark selected students as verified."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} student(s) marked as verified.')
    verify_students.short_description = 'Verify selected students'
    
    def unverify_students(self, request, queryset):
        """Mark selected students as unverified."""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} student(s) marked as unverified.')
    unverify_students.short_description = 'Unverify selected students'


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['license_number', 'get_user_name', 'assigned_route', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified', 'assigned_route', 'created_at']
    search_fields = ['license_number', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['activate_drivers', 'deactivate_drivers', 'verify_drivers', 'unverify_drivers']
    
    fieldsets = (
        ('User Connection', {
            'fields': ('user',),
        }),
        ('License Info', {
            'fields': ('license_number', 'phone'),
        }),
        ('Route Assignment', {
            'fields': ('assigned_route',),
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_user_name.short_description = 'Name'
    
    def activate_drivers(self, request, queryset):
        """Activate selected drivers."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} driver(s) activated.')
    activate_drivers.short_description = 'Activate selected drivers'
    
    def deactivate_drivers(self, request, queryset):
        """Deactivate selected drivers."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} driver(s) deactivated.')
    deactivate_drivers.short_description = 'Deactivate selected drivers'
    
    def verify_drivers(self, request, queryset):
        """Verify selected drivers."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} driver(s) verified.')
    verify_drivers.short_description = 'Verify selected drivers'
    
    def unverify_drivers(self, request, queryset):
        """Unverify selected drivers."""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} driver(s) unverified.')
    unverify_drivers.short_description = 'Unverify selected drivers'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Role Assignment', {
            'fields': ('role',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

