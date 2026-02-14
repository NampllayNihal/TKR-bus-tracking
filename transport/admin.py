from django.contrib import admin
from .models import Route, Stop, RouteSchedule


class StopInline(admin.TabularInline):
    model = Stop
    extra = 0
    fields = ['order', 'name', 'arrival_time', 'latitude', 'longitude']
    ordering = ['order']


class RouteScheduleInline(admin.TabularInline):
    model = RouteSchedule
    extra = 0
    fields = ['day_of_week', 'departure_time', 'arrival_time', 'is_active']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'bus_number', 'get_stop_count', 'get_driver_count', 'get_student_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'bus_number', 'start_location', 'end_location']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [StopInline, RouteScheduleInline]
    
    fieldsets = (
        ('Route Info', {
            'fields': ('name', 'bus_number'),
        }),
        ('Route Path', {
            'fields': ('start_location', 'end_location'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_stop_count(self, obj):
        return obj.stops.count()
    get_stop_count.short_description = 'Stops'
    
    def get_driver_count(self, obj):
        return obj.drivers.filter(is_active=True).count()
    get_driver_count.short_description = 'Active Drivers'
    
    def get_student_count(self, obj):
        return obj.students.count()
    get_student_count.short_description = 'Students'


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['name', 'route', 'order', 'arrival_time', 'get_coordinates', 'get_map_link', 'created_at']
    list_filter = ['route', 'created_at']
    search_fields = ['name', 'route__name']
    readonly_fields = ['created_at', 'updated_at', 'get_map_link']
    ordering = ['route', 'order']
    
    fieldsets = (
        ('Route & Sequence', {
            'fields': ('route', 'order'),
        }),
        ('Stop Details', {
            'fields': ('name', 'arrival_time'),
        }),
        ('GPS Coordinates', {
            'fields': ('latitude', 'longitude', 'get_map_link'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_coordinates(self, obj):
        return f"{obj.latitude:.4f}, {obj.longitude:.4f}"
    get_coordinates.short_description = 'GPS'
    
    def get_map_link(self, obj):
        """Generate Google Maps link."""
        from django.utils.html import format_html
        url = f"https://maps.google.com/?q={obj.latitude},{obj.longitude}"
        return format_html(
            '<a href="{}" target="_blank">View on Map</a>',
            url
        )
    get_map_link.short_description = 'Map'


@admin.register(RouteSchedule)
class RouteScheduleAdmin(admin.ModelAdmin):
    list_display = ['route', 'day_of_week', 'departure_time', 'arrival_time', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'route']
    search_fields = ['route__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Route & Day', {
            'fields': ('route', 'day_of_week'),
        }),
        ('Schedule', {
            'fields': ('departure_time', 'arrival_time'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

