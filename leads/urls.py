from django.urls import path
from .views import webform_lead

urlpatterns = [
    path("api/v1/leads/webform", webform_lead),
]
