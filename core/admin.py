"""
Django admin configuration for core app.
"""

from django.contrib import admin
from .models import LoanOfficer


@admin.register(LoanOfficer)
class LoanOfficerAdmin(admin.ModelAdmin):
    list_display = ("slug", "first_name", "last_name", "email", "phone", "is_active", "te_owner_id", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("slug", "first_name", "last_name", "email", "phone", "te_owner_id")
    readonly_fields = ("id", "created_at", "updated_at")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("slug", "first_name", "last_name", "email", "phone")
        }),
        ("CRM Integration", {
            "fields": ("te_owner_id",)
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Metadata", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
