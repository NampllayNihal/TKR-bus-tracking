from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from .models import (
    Profile,
    Student,
    Driver,
    Route,
    BusLocation
)


# -------------------------
# LOGIN PAGE
# -------------------------
@csrf_protect
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        selected_role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return render(request, "login.html")

        # Superuser → Admin
        if user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            messages.error(request, "No role assigned to this user.")
            return render(request, "login.html")

        if profile.role != selected_role:
            messages.error(request, "Role mismatch!")
            return render(request, "login.html")

        login(request, user)

        if profile.role == "student":
            return redirect("student_index")
        elif profile.role == "driver":
            return redirect("driver_dashboard")
        else:
            return redirect("admin_dashboard")

    return render(request, "login.html")


# -------------------------
# STUDENT DASHBOARD
# -------------------------
def student_index(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "index.html")


# -------------------------
# DRIVER DASHBOARD
# -------------------------
def driver_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "driver_tracker.html")


# -------------------------
# ADMIN DASHBOARD
# -------------------------
def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "admin/home.html")


# -------------------------
# ADMIN - ADD STUDENTS
# -------------------------
@csrf_protect
def manage_students(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        username = request.POST.get("username")
        name = request.POST.get("name")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("manage-students")

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name
        )

        Profile.objects.filter(user=user).update(role="student")
        Student.objects.create(user=user, hall_ticket=username)

        messages.success(request, "Student added successfully!")
        return redirect("manage-students")

    return render(request, "admin/manage_students.html")


def manage_drivers(request):
    return render(request, "admin/manage_drivers.html")


def manage_routes(request):
    return render(request, "admin/manage_routes.html")


def manage_fees(request):
    return render(request, "admin/manage_fees.html")


# -------------------------
# STUDENT PAGES
# -------------------------
def routes_page(request):
    return render(request, "routes.html")


def drivers_page(request):
    return render(request, "drivers.html")


def stops_page(request):
    return render(request, "stops.html")


def fees_page(request):
    return render(request, "fees.html")


def live_tracker_page(request):
    return render(request, "live-tracker.html")


# ==========================================================
# 🔴 LIVE TRACKING API — DRIVER SENDS LOCATION
# ==========================================================
@require_POST
def update_bus_location(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        driver = Driver.objects.get(user=request.user)
    except Driver.DoesNotExist:
        return JsonResponse({"error": "Not a driver"}, status=403)

    lat = request.POST.get("latitude")
    lon = request.POST.get("longitude")

    if not lat or not lon:
        return JsonResponse({"error": "Invalid data"}, status=400)

    BusLocation.objects.update_or_create(
        route=driver.route,
        defaults={
            "latitude": lat,
            "longitude": lon
        }
    )

    return JsonResponse({"status": "Location updated"})


# ==========================================================
# 🟢 LIVE TRACKING API — STUDENT GETS LOCATION BY ROUTE
# ==========================================================
def get_bus_location(request, route_id):
    try:
        bus = BusLocation.objects.get(route_id=route_id)
        return JsonResponse({
            "latitude": bus.latitude,
            "longitude": bus.longitude,
            "updated_at": bus.updated_at
        })
    except BusLocation.DoesNotExist:
        return JsonResponse({"error": "Bus not started yet"})
    

# -------------------------
# LOGOUT
# -------------------------
def logout_user(request):
    logout(request)
    return redirect("login")

