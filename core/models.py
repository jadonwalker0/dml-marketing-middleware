"""
Core models for DML Marketing Middleware.
"""

import uuid
from django.db import models


class LoanOfficer(models.Model):
    """
    Represents a loan officer at Direct Mortgage Loans.
    Each LO has a unique slug used in their website URL.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Slug is the URL path component (e.g., "john-smith" from directmortgageloans.com/john-smith)
    slug = models.CharField(max_length=120, unique=True, db_index=True)
    
    # Basic contact information
    first_name = models.CharField(max_length=80, blank=True, default="")
    last_name = models.CharField(max_length=80, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    
    # Total Expert Owner ID (for CRM integration)
    te_owner_id = models.CharField(max_length=120, blank=True, default="", help_text="Total Expert owner/user ID")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Whether this LO is currently accepting leads")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    """
    class Meta:
        verbose_name = "Loan Officer"
        verbose_name_plural = "Loan Officers"
        ordering = ["slug"]
        db_table = "loan_officers"
    """
    
    def save(self, *args, **kwargs):
        """Normalize slug to lowercase before saving."""
        if self.slug:
            self.slug = self.slug.strip().strip("/").lower()
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.slug})"
        return self.slug
