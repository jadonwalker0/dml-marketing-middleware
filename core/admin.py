# path to this file: "dml-marketing-middleware/core/>file<"

from django.contrib import admin
from .models import LoanOfficer

# Register your models here.

@admin.register(LoanOfficer)
class LoanOfficerAdmin(admin.ModelAdmin):
    list_display = ("slug", "first_name", "last_name", "email", "is_active", "te_owner_id")
    search_fields = ("slug", "first_name", "last_name", "email")
    list_filter = ("is_active",)
