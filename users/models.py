from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Student(models.Model):
    """
    Student profile extended from Django User model.
    
    Benefits of OneToOneField:
    - Direct access: student.user.email
    - Can delete student without deleting User
    - Extensible for future student-specific features
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="Link to Django User account"
    )
    hall_ticket = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique student ID/Hall ticket number"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', message='Phone must be 10 digits')]
    )
    active_route = models.ForeignKey(
        'transport.Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Currently assigned route"
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether student email/phone is verified"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When student profile was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update"
    )

    class Meta:
        app_label = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['active_route']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.hall_ticket} - {self.user.get_full_name() or self.user.username}"

    def get_full_name(self):
        return self.user.get_full_name()


class Driver(models.Model):
    """
    Driver profile extended from Django User model.
    
    Stores driver-specific information and route assignment.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        help_text="Link to Django User account"
    )
    license_number = models.CharField(
        max_length=25,
        unique=True,
        help_text="Driver license number"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10}$', message='Phone must be 10 digits')]
    )
    assigned_route = models.ForeignKey(
        'transport.Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers',
        help_text="Currently assigned route"
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether driver is verified"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether driver is currently active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When driver profile was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update"
    )

    class Meta:
        app_label = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_route']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.license_number} - {self.user.get_full_name() or self.user.username}"

    def get_full_name(self):
        return self.user.get_full_name()


class UserRole(models.Model):
    """
    DEPRECATION: This model replaces the old Profile model.
    Used for role-based access control before transitioning to permissions.
    
    Note: Consider using Django Groups instead for better scalability.
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_role',
        help_text="User this role is assigned to"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        db_index=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When role was assigned"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last role update"
    )

    class Meta:
        app_label = 'users'
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


def create_user_role(sender, instance, created, **kwargs):
    """Signal handler to auto-create UserRole when User is created."""
    if created:
        UserRole.objects.get_or_create(user=instance, defaults={'role': 'student'})


# Apply signal - SAFE: Only creates role if it doesn't exist
from django.db.models.signals import post_save
post_save.connect(create_user_role, sender=User, dispatch_uid='create_user_role')
