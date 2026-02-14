from django.contrib import admin
from django.utils.html import format_html
from .models import GPSLog, BusTracker, LocationError


@admin.register(GPSLog)
class GPSLogAdmin(admin.ModelAdmin):
    list_display = ['route', 'driver', 'get_coordinates', 'speed', 'accuracy', 'timestamp', 'created_at']
    list_filter = ['route', 'driver', 'timestamp', 'created_at']
    search_fields = ['route__name', 'driver__user__username']
    readonly_fields = ['created_at', 'get_map_link']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Route & Driver', {
            'fields': ('route', 'driver'),
        }),
        ('GPS Location', {
            'fields': ('latitude', 'longitude', 'accuracy', 'get_map_link'),
        }),
        ('Movement', {
            'fields': ('speed', 'heading'),
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_coordinates(self, obj):
        return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
    get_coordinates.short_description = 'GPS'
    
    def get_map_link(self, obj):
        """Generate Google Maps link."""
        url = f"https://maps.google.com/?q={obj.latitude},{obj.longitude}"
        return format_html(
            '<a href="{}" target="_blank">View on Google Maps</a>',
            url
        )
    get_map_link.short_description = 'Map'


@admin.register(BusTracker)
class BusTrackerAdmin(admin.ModelAdmin):
    list_display = ['route', 'driver', 'current_stop', 'is_active', 'speed', 'last_updated', 'get_map_link']
    list_filter = ['is_active', 'route', 'last_updated']
    search_fields = ['route__name', 'driver__user__username']
    readonly_fields = ['last_updated', 'get_map_link']
    actions = ['activate_trackers', 'deactivate_trackers']
    
    fieldsets = (
        ('Route & Driver', {
            'fields': ('route', 'driver'),
        }),
        ('Current Location', {
            'fields': ('latitude', 'longitude', 'get_map_link'),
        }),
        ('Stop & ETA', {
            'fields': ('current_stop',),
        }),
        ('Movement', {
            'fields': ('speed', 'heading'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',),
        }),
    )
    
    def get_map_link(self, obj):
        """Generate Google Maps link."""
        url = f"https://maps.google.com/?q={obj.latitude},{obj.longitude}"
        return format_html(
            '<a href="{}" target="_blank">View on Map</a>',
            url
        )
    get_map_link.short_description = 'Map'
    
    def activate_trackers(self, request, queryset):
        """Activate selected trackers."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} tracker(s) activated.')
    activate_trackers.short_description = 'Activate selected trackers'
    
    def deactivate_trackers(self, request, queryset):
        """Deactivate selected trackers."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} tracker(s) deactivated.')
    deactivate_trackers.short_description = 'Deactivate selected trackers'


@admin.register(LocationError)
class LocationErrorAdmin(admin.ModelAdmin):
    list_display = ['tracker', 'error_type', 'is_critical', 'timestamp', 'resolved_at']
    list_filter = ['error_type', 'is_critical', 'timestamp', ('resolved_at', admin.RelatedOnlyFieldListFilter)]
    search_fields = ['tracker__route__name', 'error_message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Bus Tracker', {
            'fields': ('tracker',),
        }),
        ('Error Info', {
            'fields': ('error_type', 'error_message', 'is_critical'),
        }),
        ('Status', {
            'fields': ('timestamp', 'resolved_at'),
        }),
    )
    
    actions = ['mark_as_critical', 'mark_as_resolved', 'mark_as_not_critical']
    
    def mark_as_critical(self, request, queryset):
        """Mark errors as critical."""
        updated = queryset.update(is_critical=True)
        self.message_user(request, f'{updated} error(s) marked as critical.')
    mark_as_critical.short_description = 'Mark as critical'
    
    def mark_as_resolved(self, request, queryset):
        """Mark errors as resolved."""
        from django.utils import timezone
        updated = queryset.filter(resolved_at__isnull=True).update(resolved_at=timezone.now())
        self.message_user(request, f'{updated} error(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark as resolved'
    
    def mark_as_not_critical(self, request, queryset):
        """Mark errors as not critical."""
        updated = queryset.update(is_critical=False)
        self.message_user(request, f'{updated} error(s) marked as not critical.')
    mark_as_not_critical.short_description = 'Mark as not critical'

