from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),    # Django admin
    path('', include('busapp.urls')),   # Your main app
]
