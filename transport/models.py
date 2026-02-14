from django.db import models
from django.core.validators import RegexValidator


class Route(models.Model):
    """
    Bus route definition with GPS stops.
    
    Improvements:
    - Unique bus_number constraint
    - slug for URL routing
    - is_active for soft deletion
    - Timestamps for audit trail
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Route name (e.g., 'Hyderabad to Secunderabad')"
    )
    bus_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Bus registration number"
    )
    start_location = models.CharField(
        max_length=255,
        help_text="Starting point of route"
    )
    end_location = models.CharField(
        max_length=255,
        help_text="Ending point of route"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this route is currently operational"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When route was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last route update"
    )

    class Meta:
        app_label = 'transport'
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_active_stops(self):
        """Get all stops ordered by sequence."""
        return self.stops.all()

    def get_driver_count(self):
        """Count active drivers on this route."""
        return self.drivers.filter(is_active=True).count()

    def get_student_count(self):
        """Count students on this route."""
        return self.students.count()


class Stop(models.Model):
    """
    Individual stop on a route with GPS coordinates.
    
    Improvements:
    - GPS coordinates for actual location tracking
    - Arrival time for schedule management
    - Order for route sequencing
    - Timestamps for audit
    """
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='stops',
        help_text="Route this stop belongs to"
    )
    name = models.CharField(
        max_length=255,
        help_text="Stop name (e.g., 'Main Gate', 'Library')"
    )
    latitude = models.FloatField(
        help_text="GPS latitude coordinate"
    )
    longitude = models.FloatField(
        help_text="GPS longitude coordinate"
    )
    arrival_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Expected arrival time (HH:MM:SS format)"
    )
    order = models.PositiveIntegerField(
        help_text="Sequence of stop in route (1, 2, 3...)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When stop was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last stop update"
    )

    class Meta:
        app_label = 'transport'
        ordering = ['route', 'order']
        unique_together = [['route', 'order']]
        indexes = [
            models.Index(fields=['route', 'order']),
        ]

    def __str__(self):
        return f"{self.route.name} - Stop {self.order}: {self.name}"


class RouteSchedule(models.Model):
    """
    Recurring schedule for a route (day-wise timing).
    
    Enables:
    - Different schedules for different days
    - Flexible departure/arrival times
    - Future expansion to handle holidays
    """
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='schedules',
        help_text="Route this schedule applies to"
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        help_text="Day of week (0=Monday, 6=Sunday)"
    )
    departure_time = models.TimeField(
        help_text="Departure time from first stop (HH:MM:SS)"
    )
    arrival_time = models.TimeField(
        help_text="Arrival time at last stop (HH:MM:SS)"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this schedule is active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When schedule was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last schedule update"
    )

    class Meta:
        app_label = 'transport'
        ordering = ['route', 'day_of_week']
        unique_together = [['route', 'day_of_week']]

    def __str__(self):
        return f"{self.route.name} - {self.get_day_of_week_display()}"

