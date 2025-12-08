from django.contrib import admin
from .models import Profile, Student, Driver, Route, Stop, FeeRecord

admin.site.register(Profile)
admin.site.register(Student)
admin.site.register(Driver)
admin.site.register(Route)
admin.site.register(Stop)
admin.site.register(FeeRecord)

