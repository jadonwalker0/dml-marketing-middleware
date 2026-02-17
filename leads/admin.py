"""
Django admin configuration for leads app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import LeadSubmission, LeadStatus


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "submitted_at",
        "loan_officer_display",
        "name_display",
        "email",
        "phone",
        "status_badge",
        "attempt_count",
    )
    list_filter = ("status", "submitted_at", "loan_officer", "source")
    search_fields = ("first_name", "last_name", "email", "phone", "loan_officer__slug", "te_contact_id")
    readonly_fields = (
        "id",
        "submitted_at",
        "queued_at",
        "synced_at",
        "raw_payload_display",
        "ip_address",
        "user_agent",
    )
    date_hierarchy = "submitted_at"

    # so /admin shows the table by submitted at field!
    ordering = ("-submitted_at",)

    fieldsets = (
        ("Lead Information", {
            "fields": ("loan_officer", "source", "first_name", "last_name", "email", "phone")
        }),
        ("Sync Status", {
            "fields": ("status", "te_contact_id", "attempt_count", "last_error")
        }),
        ("Request Metadata", {
            "fields": ("page_url", "referrer", "ip_address", "user_agent"),
            "classes": ("collapse",)
        }),
        ("Raw Data", {
            "fields": ("raw_payload_display",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("id", "submitted_at", "queued_at", "synced_at"),
            "classes": ("collapse",)
        }),
    )
    
    def loan_officer_display(self, obj):
        """Display loan officer slug."""
        return obj.loan_officer.slug
    loan_officer_display.short_description = "Loan Officer"
    loan_officer_display.admin_order_field = "loan_officer__slug"
    
    def name_display(self, obj):
        """Display full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or "(no name)"
    name_display.short_description = "Name"
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            LeadStatus.RECEIVED: "#6c757d",  # Gray
            LeadStatus.QUEUED: "#0d6efd",    # Blue
            LeadStatus.SYNCED: "#198754",    # Green
            LeadStatus.FAILED: "#dc3545",    # Red
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"
    
    def raw_payload_display(self, obj):
        """Display formatted JSON payload."""
        import json
        if obj.raw_payload:
            return format_html(
                "<pre>{}</pre>",
                json.dumps(obj.raw_payload, indent=2)
            )
        return "(empty)"
    raw_payload_display.short_description = "Raw Payload"
