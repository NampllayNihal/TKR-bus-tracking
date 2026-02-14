from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class GPSLog(models.Model):
    """
    HISTORICAL GPS location data for buses.
    
    Enables:
    - Complete tracking history
    - Route analysis
    - Driver performance metrics
    - Debugging route issues
    
    Design: Fast inserts, optimized for time-series queries
    """
    route = models.ForeignKey(
        'transport.Route',
        on_delete=models.CASCADE,
        related_name='location_logs',
        help_text="Route being tracked"
    )
    driver = models.ForeignKey(
        'users.Driver',
        on_delete=models.CASCADE,
        related_name='location_logs',
        help_text="Driver operating the bus"
    )
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="GPS latitude (-90 to 90)"
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="GPS longitude (-180 to 180)"
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    speed = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Speed in km/h"
    )
    heading = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Direction in degrees (0-360)"
    )
    timestamp = models.DateTimeField(
        help_text="When location was recorded (device time)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When record was stored in database"
    )

    class Meta:
        app_label = 'tracking'
        ordering = ['-timestamp']
        verbose_name_plural = "GPS Logs"
        indexes = [
            models.Index(fields=['driver', 'timestamp']),
            models.Index(fields=['route', 'timestamp']),
            models.Index(fields=['created_at']),
        ]
        get_latest_by = 'timestamp'

    def __str__(self):
        return f"{self.route.name} - {self.timestamp}"

    def distance_from(self, other):
        """
        Calculate approximate distance to another location in meters.
        Uses simple Haversine approximation.
        """
        import math
        
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        delta_lat = math.radians(other.latitude - self.latitude)
        delta_lon = math.radians(other.longitude - self.longitude)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * 
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c  # Distance in meters


class BusTracker(models.Model):
    """
    LIVE BUS STATE - replaces old BusLocation model.
    
    Improvements:
    - Tracks current stop
    - Includes next stop ETA
    - is_active flag for operational status
    - Better timestamp handling
    
    Design: Single record per route, updated frequently
    """
    route = models.OneToOneField(
        'transport.Route',
        on_delete=models.CASCADE,
        related_name='bus_tracker',
        help_text="Route being tracked"
    )
    driver = models.ForeignKey(
        'users.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_tracking',
        help_text="Driver currently operating this route"
    )
    current_stop = models.ForeignKey(
        'transport.Stop',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_at',
        help_text="Stop bus is currently at or near"
    )
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Current GPS latitude"
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Current GPS longitude"
    )
    speed = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Current speed in km/h"
    )
    heading = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Current direction (0-360 degrees)"
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether bus is currently active/running"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="When location was last updated"
    )

    class Meta:
        app_label = 'tracking'
        verbose_name_plural = "Bus Trackers"

    def __str__(self):
        return f"{self.route.name} - Live Location"

    def update_location(self, lat, lon, speed=None, heading=None):
        """Update bus location and create GPS log."""
        from django.utils import timezone
        
        # Update live tracker
        self.latitude = lat
        self.longitude = lon
        if speed is not None:
            self.speed = speed
        if heading is not None:
            self.heading = heading
        self.save()
        
        # Create history log
        if self.driver:
            GPSLog.objects.create(
                route=self.route,
                driver=self.driver,
                latitude=lat,
                longitude=lon,
                speed=speed,
                heading=heading,
                timestamp=timezone.now()
            )


class LocationError(models.Model):
    """
    ERROR TRACKING for GPS signal and coordinate validity.
    
    Enables:
    - Monitoring of GPS signal issues
    - Data quality tracking
    - Driver notification of tech issues
    """
    ERROR_TYPES = (
        ('signal_lost', 'GPS Signal Lost'),
        ('invalid_coords', 'Invalid Coordinates'),
        ('accuracy_low', 'Low Accuracy'),
        ('timeout', 'Location Timeout'),
        ('permission_denied', 'Permission Denied'),
        ('unknown', 'Unknown Error'),
    )
    
    tracker = models.ForeignKey(
        BusTracker,
        on_delete=models.CASCADE,
        related_name='errors',
        help_text="Bus tracker that had issue"
    )
    error_type = models.CharField(
        max_length=20,
        choices=ERROR_TYPES,
        help_text="Type of error"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Detailed error message"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When error occurred"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When issue was resolved"
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Whether this error needs immediate attention"
    )

    class Meta:
        app_label = 'tracking'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tracker', 'timestamp']),
            models.Index(fields=['is_critical', 'resolved_at']),
        ]

    def __str__(self):
        return f"{self.tracker.route.name} - {self.get_error_type_display()}"

    def mark_resolved(self):
        """Mark this error as resolved."""
        from django.utils import timezone
        
        self.resolved_at = timezone.now()
        self.save()

