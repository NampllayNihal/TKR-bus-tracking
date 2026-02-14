from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# -----------------------------
# USER ROLE MODEL
# -----------------------------
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# -----------------------------
# ROUTE MODEL
# -----------------------------
class Route(models.Model):
    name = models.CharField(max_length=50)
    bus_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


# -----------------------------
# DRIVER MODEL
# -----------------------------
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    driver_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.driver_id or f"Driver {self.id}"


# -----------------------------
# STOP MODEL
# -----------------------------
class Stop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop_name = models.CharField(max_length=50)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.stop_name} ({self.route.name})"


# -----------------------------
# STUDENT MODEL
# -----------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hall_ticket = models.CharField(max_length=20, unique=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.hall_ticket


# -----------------------------
# FEE RECORD MODEL
# -----------------------------
class FeeRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.IntegerField()
    paid_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.hall_ticket} - ₹{self.amount}"


# -----------------------------
# 🚌 LIVE BUS LOCATION MODEL
# -----------------------------
class BusLocation(models.Model):
    route = models.OneToOneField(Route, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.route.name} - {self.latitude},{self.longitude}"


# -----------------------------
# AUTO CREATE PROFILE (SAFE)
# -----------------------------
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role='student')
