"""
Lead submission models for DML Marketing Middleware.
"""

import uuid
from django.db import models
from core.models import LoanOfficer


class LeadStatus(models.TextChoices):
    """Status choices for lead submissions."""
    RECEIVED = "received", "Received"
    QUEUED = "queued", "Queued"
    SYNCED = "synced", "Synced"
    FAILED = "failed", "Failed"


class LeadSubmission(models.Model):
    """
    Represents a lead submission from a webform.
    Tracks the submission from receipt through CRM sync.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationship
    loan_officer = models.ForeignKey(
        LoanOfficer,
        on_delete=models.PROTECT,
        related_name="leads",
        help_text="The loan officer this lead is assigned to"
    )
    
    # Source information
    source = models.CharField(max_length=50, default="webform", help_text="Source of the lead (e.g., webform, api)")
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Request metadata
    page_url = models.URLField(max_length=200, blank=True, default="", help_text="URL of the page where the form was submitted")
    referrer = models.URLField(max_length=200, blank=True, default="", help_text="HTTP referrer URL")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="Submitter's IP address")
    user_agent = models.TextField(blank=True, default="", help_text="Submitter's browser user agent")
    
    # Lead data
    first_name = models.CharField(max_length=80, blank=True, default="")
    last_name = models.CharField(max_length=80, blank=True, default="")
    email = models.EmailField(blank=True, default="", db_index=True)
    phone = models.CharField(max_length=30, blank=True, default="", db_index=True)
    ok_to_email = models.BooleanField(default=False)
    ok_to_call = models.BooleanField(default=False)
    
    # Raw payload (store everything we received)
    raw_payload = models.JSONField(default=dict, help_text="Complete JSON payload from the form submission")
    
    # Sync status
    status = models.CharField(
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.RECEIVED,
        db_index=True,
        help_text="Current processing status"
    )
    te_contact_id = models.CharField(max_length=120, blank=True, default="", help_text="Total Expert contact ID after sync")
    attempt_count = models.PositiveIntegerField(default=0, help_text="Number of sync attempts")
    last_error = models.TextField(blank=True, default="", help_text="Last error message if sync failed")
    
    # Timestamps
    queued_at = models.DateTimeField(blank=True, null=True, help_text="When this lead was queued to Service Bus")
    synced_at = models.DateTimeField(blank=True, null=True, help_text="When this lead was successfully synced to Total Expert")
    
    """
    class Meta:
        verbose_name = "Lead Submission"
        verbose_name_plural = "Lead Submissions"
        ordering = ["-submitted_at"]
        db_table = "lead_submissions"
        indexes = [
            models.Index(fields=["-submitted_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]
        """
    
    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        contact = self.email or self.phone or "no contact"
        return f"{name or 'Unknown'} ({contact}) - {self.get_status_display()}"
