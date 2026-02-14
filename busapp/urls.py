from django.urls import path
from . import views

urlpatterns = [
    # -------------------------
    # AUTH
    # -------------------------
    path('', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # -------------------------
    # STUDENT
    # -------------------------
    path('home/', views.student_index, name='student_index'),
    path('routes/', views.routes_page, name='routes'),
    path('drivers/', views.drivers_page, name='drivers'),
    path('stops/', views.stops_page, name='stops'),
    path('fees/', views.fees_page, name='fees'),
    path('live-tracker/', views.live_tracker_page, name='live-tracker'),
    path('live-tracker/debug/', views.live_tracker_debug, name='live-tracker-debug'),

    # -------------------------
    # DRIVER
    # -------------------------
    path('driver-tracker/', views.driver_dashboard, name='driver_dashboard'),

    # -------------------------
    # ADMIN
    # -------------------------
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/manage-students/', views.manage_students, name='manage-students'),
    path('admin-panel/manage-drivers/', views.manage_drivers, name='manage-drivers'),
    path('admin-panel/manage-routes/', views.manage_routes, name='manage-routes'),
    path('admin-panel/manage-fees/', views.manage_fees, name='manage-fees'),

    # ==================================================
    # 🔴 DRIVER → SEND LIVE LOCATION
    # ==================================================
    path(
        'api/driver/update-location/',
        views.update_bus_location,
        name='update_bus_location'
    ),

    # ==================================================
    # 🟢 STUDENT → GET BUS LOCATION BY ROUTE
    # ==================================================
    path(
        'api/student/bus-location/<int:route_id>/',
        views.get_bus_location,
        name='get_bus_location'
    ),

    # ==================================================
    # 📡 API ROUTES
    # ==================================================
    path('api/student/routes/', views.api_get_routes, name='api_get_routes'),
]


