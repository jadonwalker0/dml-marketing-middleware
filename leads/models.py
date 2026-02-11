# path to this file: "dml-marketing-middleware/leads/>file<"

import uuid
from django.db import models
from core.models import LoanOfficer

# Create your models here.

class LeadStatus(models.TextChoices):
    RECEIVED = "received"
    QUEUED = "queued"
    SYNCED = "synced"
    FAILED = "failed"

class LeadSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    loan_officer = models.ForeignKey(LoanOfficer, on_delete=models.PROTECT, related_name="leads")
    source = models.CharField(max_length=50, default="webform")
    submitted_at = models.DateTimeField(auto_now_add=True)

    page_url = models.URLField(blank=True, default="")
    referrer = models.URLField(blank=True, default="")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")

    first_name = models.CharField(max_length=80, blank=True, default="")
    last_name = models.CharField(max_length=80, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")

    raw_payload = models.JSONField(default=dict)

    status = models.CharField(max_length=20, choices=LeadStatus.choices, default=LeadStatus.RECEIVED)
    te_contact_id = models.CharField(max_length=120, blank=True, default="")
    attempt_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True, default="")

    queued_at = models.DateTimeField(blank=True, null=True)
    synced_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["submitted_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email or self.phone})"
