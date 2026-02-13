"""
Django admin configuration for core app.
"""

from django.contrib import admin
from .models import LoanOfficer


def activate_loan_officers(modeladmin, request, queryset):
    """Bulk action to activate selected loan officers"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} loan officer(s) marked as active.")
activate_loan_officers.short_description = "Mark selected as active"


def deactivate_loan_officers(modeladmin, request, queryset):
    """Bulk action to deactivate selected loan officers"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} loan officer(s) marked as inactive.")
deactivate_loan_officers.short_description = "Mark selected as inactive"


@admin.register(LoanOfficer)
class LoanOfficerAdmin(admin.ModelAdmin):
    list_display = ("slug", "first_name", "last_name", "email", "phone", "is_active", "te_owner_id", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("slug", "first_name", "last_name", "email", "phone", "te_owner_id")
    readonly_fields = ("id", "created_at", "updated_at")
    actions = [activate_loan_officers, deactivate_loan_officers]
    
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