from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from functools import wraps

from .models import (
    Profile,
    Student,
    Driver,
    Route,
    BusLocation
)


# -----------------------------
# ROLE-BASED ACCESS DECORATOR
# -----------------------------
def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Allow superuser as admin
            if request.user.is_superuser and required_role == 'admin':
                return view_func(request, *args, **kwargs)
            
            try:
                profile = Profile.objects.get(user=request.user)
                if profile.role != required_role:
                    messages.error(request, f"Access denied. You must be logged in as a {required_role}.")
                    return redirect('login')
            except Profile.DoesNotExist:
                messages.error(request, "No role assigned to your account.")
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


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
@role_required('student')
def student_index(request):
    return render(request, "index.html")


# -------------------------
# DRIVER DASHBOARD
# -------------------------
@role_required('driver')
def driver_dashboard(request):
    try:
        from users.models import Driver
        driver = Driver.objects.select_related('assigned_route').get(user=request.user)
    except:
        driver = None
    
    bus_number = driver.assigned_route.bus_number if driver and driver.assigned_route else None
    
    context = {
        'user': request.user,
        'driver': driver,
        'bus_number': bus_number
    }
    
    return render(request, "driver_tracker.html", context)


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@role_required('admin')
def admin_dashboard(request):
    return render(request, "admin/home.html")


# -------------------------
# ADMIN - ADD STUDENTS
# -------------------------
@role_required('admin')
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

        Profile.objects.get_or_create(user=user, defaults={'role': 'student'})
        Student.objects.create(user=user, hall_ticket=username)

        messages.success(request, "Student added successfully!")
        return redirect("manage-students")

    return render(request, "admin/manage_students.html")


@role_required('admin')
def manage_drivers(request):
    return render(request, "admin/manage_drivers.html")


@role_required('admin')
def manage_routes(request):
    return render(request, "admin/manage_routes.html")


@role_required('admin')
def manage_fees(request):
    return render(request, "admin/manage_fees.html")


# -------------------------
# STUDENT PAGES
# -------------------------
@role_required('student')
def routes_page(request):
    return render(request, "routes.html")


@role_required('student')
def drivers_page(request):
    return render(request, "drivers.html")


@role_required('student')
def stops_page(request):
    return render(request, "stops.html")


@role_required('student')
def fees_page(request):
    return render(request, "fees.html")


@role_required('student')
def live_tracker_page(request):
    from transport.models import Route
    from users.models import Student
    
    routes = Route.objects.filter(is_active=True).order_by('name')
    
    # Get current student's route if logged in
    student_route = None
    if request.user.is_authenticated:
        try:
            student = Student.objects.select_related('active_route').get(user=request.user)
            student_route = student.active_route
        except:
            pass
    
    context = {
        'routes': routes,
        'student_route': student_route
    }
    return render(request, "live-tracker.html", context)


# =========================================================
# 🐛 DEBUG PAGE FOR LIVE TRACKING
# =========================================================
def live_tracker_debug(request):
    """Debug page for troubleshooting live tracking"""
    return render(request, "live-tracker-debug.html")


# =========================================================
# API: GET ALL ROUTES
# =========================================================
def api_get_routes(request):
    """API endpoint to get all active routes"""
    from transport.models import Route
    routes = Route.objects.filter(is_active=True).values('id', 'name', 'bus_number', 'is_active')
    return JsonResponse(list(routes), safe=False)



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

