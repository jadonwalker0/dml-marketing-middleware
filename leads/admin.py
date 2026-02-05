from django.contrib import admin
from .models import LeadSubmission

# Register your models here.

@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    list_display = ("submitted_at", "loan_officer", "first_name", "last_name", "email", "phone", "status")
    search_fields = ("first_name", "last_name", "email", "phone", "loan_officer__slug")
    list_filter = ("status", "submitted_at")
    readonly_fields = ("raw_payload", "submitted_at", "queued_at", "synced_at")
