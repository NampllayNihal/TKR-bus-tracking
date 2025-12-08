from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from .models import Profile, Student


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

        # ✅ Superuser → Admin directly
        if user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")

        # ✅ Normal users MUST have Profile
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            messages.error(request, "No role assigned to this user. Contact Admin.")
            return render(request, "login.html")

        # ✅ Role Validation
        if profile.role != selected_role:
            messages.error(request, "Role mismatch!")
            return render(request, "login.html")

        # ✅ Login Success
        login(request, user)

        if profile.role == "student":
            return redirect("student_index")

        elif profile.role == "driver":
            return redirect("driver_dashboard")

        elif profile.role == "admin":
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

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name
        )

        # ✅ Assign student role
        Profile.objects.create(user=user, role="student")

        # ✅ Create student record
        Student.objects.create(user=user, hall_ticket=username)

        messages.success(request, "Student added successfully!")
        return redirect("manage-students")

    return render(request, "admin/manage_students.html")


def manage_drivers(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "admin/manage_drivers.html")


def manage_routes(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "admin/manage_routes.html")


def manage_fees(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "admin/manage_fees.html")


# -------------------------
# ✅ ✅ ✅ STUDENT FEATURE PAGES (FIXES YOUR ERROR)
# -------------------------
def routes_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "routes.html")


def drivers_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "drivers.html")


def stops_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "stops.html")


def fees_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "fees.html")


def live_tracker_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "live-tracker.html")


# -------------------------
# LOGOUT
# -------------------------
def logout_user(request):
    logout(request)
    return redirect("login")
