from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),

    # Student
    path('home/', views.student_index, name='student_index'),
    path('routes/', views.routes_page, name='routes'),
    path('drivers/', views.drivers_page, name='drivers'),
    path('stops/', views.stops_page, name='stops'),
    path('fees/', views.fees_page, name='fees'),
    path('live-tracker/', views.live_tracker_page, name='live-tracker'),

    # Driver
    path('driver-tracker/', views.driver_dashboard, name='driver_dashboard'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/manage-students/', views.manage_students, name='manage-students'),
    path('admin-panel/manage-drivers/', views.manage_drivers, name='manage-drivers'),
    path('admin-panel/manage-routes/', views.manage_routes, name='manage-routes'),
    path('admin-panel/manage-fees/', views.manage_fees, name='manage-fees'),

    path('logout/', views.logout_user, name='logout'),
]
