from django.contrib import admin
from django.urls import path, include
from sportsApp.models import User

from django.contrib.auth.admin import UserAdmin

class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(User, UserAdmin)

urlpatters = [
    path('admin/',admin.site.urls),
    path('', include("sportsApp.urls"))
]