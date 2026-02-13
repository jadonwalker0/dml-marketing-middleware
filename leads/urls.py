"""
URL configuration for leads app.
"""
from django.urls import path
from .views import webform_lead, health_check

urlpatterns = [
    path("api/v1/leads/webform", webform_lead, name="webform_lead"),
    path("health", health_check, name="health_check"),
]
