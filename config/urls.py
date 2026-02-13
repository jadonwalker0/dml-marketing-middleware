"""
URL configuration for DML Marketing Middleware project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("leads.urls")),
]
