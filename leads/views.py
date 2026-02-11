# path to this file: "dml-marketing-middleware/leads/>file<"

import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.models import LoanOfficer
from .models import LeadSubmission, LeadStatus
from .servicebus import enqueue_lead


@csrf_exempt  # Formidable posts from public pages
def webform_lead(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # Parse JSON
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Required
    lo_slug = (payload.get("lo_slug") or "").strip().lower()
    if not lo_slug:
        return JsonResponse({"error": "lo_slug is required"}, status=400)

    # Find LO
    lo = LoanOfficer.objects.filter(slug__iexact=lo_slug, is_active=True).first()
    if not lo:
        return JsonResponse({"error": f"Unknown lo_slug: {lo_slug}"}, status=404)

    # Capture basic request metadata (nice to have)
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    # Create submission using YOUR model fields
    submission = LeadSubmission.objects.create(
        loan_officer=lo,
        source="webform",
        page_url=(payload.get("page_url") or "").strip(),
        referrer=(payload.get("referrer") or "").strip(),
        ip_address=ip_address,
        user_agent=user_agent,

        first_name=(payload.get("first_name") or "").strip(),
        last_name=(payload.get("last_name") or "").strip(),
        email=(payload.get("email") or "").strip(),
        phone=(payload.get("phone") or "").strip(),

        raw_payload=payload,
        status=LeadStatus.RECEIVED,
    )

    # Enqueue to Service Bus and mark queued
    try:
        enqueue_lead(submission_id=str(submission.id))
        submission.queued_at = timezone.now()
        submission.status = LeadStatus.QUEUED
        submission.save(update_fields=["queued_at", "status"])
    except Exception as e:
        # If queue fails, keep it received and store error for retry
        submission.last_error = str(e)
        submission.attempt_count = submission.attempt_count + 1
        submission.save(update_fields=["last_error", "attempt_count"])
        return JsonResponse({"error": "Failed to enqueue lead"}, status=500)

    return JsonResponse({"ok": True, "id": str(submission.id)})

