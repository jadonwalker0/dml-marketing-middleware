"""
API views for lead submissions.
"""

import json
import logging
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.models import LoanOfficer
from .models import LeadSubmission, LeadStatus
from .servicebus import enqueue_lead

logger = logging.getLogger(__name__)


@csrf_exempt  # Formidable posts from public pages without CSRF token
@require_http_methods(["POST"])
def webform_lead(request):
    """
    Receive lead submissions from Formidable webforms.
    
    Expected JSON payload:
    {
        "lo_slug": "john-smith",  # Required: loan officer slug
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "page_url": "https://directmortgageloans.com/john-smith",
        "referrer": "https://google.com"
    }
    
    Returns:
        201: Lead successfully received and queued
        400: Invalid request (bad JSON or missing lo_slug)
        404: Unknown loan officer slug
        500: Failed to queue lead to Service Bus
    """
    
    # Parse JSON payload
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in request: {e}")
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    
    # Get opt in status
    raw_opt_in = payload.get("comm_opt_in", "")
    ok_to_email = raw_opt_in in (True, 1, "1", "true", "True", "yes", "on")
    ok_to_call = raw_opt_in in (True, 1, "1", "true", "True", "yes", "on")
    
    # Extract and validate lo_slug
    lo_slug = (payload.get("lo_slug") or "").strip().lower()
    if not lo_slug:
        logger.warning("Request missing lo_slug")
        return JsonResponse({"error": "lo_slug is required"}, status=400)
    # DEBUG: Log the actual payload received
    logger.info(f"WEBHOOK PAYLOAD RECEIVED: {payload}")

    # Find the loan officer
    try:
        loan_officer = LoanOfficer.objects.get(slug__iexact=lo_slug, is_active=True)
    except LoanOfficer.DoesNotExist:
        logger.warning(f"Unknown or inactive loan officer slug: {lo_slug}")
        return JsonResponse({"error": f"Unknown loan officer: {lo_slug}"}, status=404)
    
    # Extract request metadata
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR")
    
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    
    # Create the lead submission
    submission = LeadSubmission.objects.create(
        loan_officer=loan_officer,
        source="webform",
        page_url=(payload.get("page_url") or "").strip()[:200],  # Limit to field max_length
        referrer=(payload.get("referrer") or "").strip()[:200],
        ip_address=ip_address or None,
        user_agent=user_agent,
        first_name=(payload.get("first_name") or "").strip(),
        last_name=(payload.get("last_name") or "").strip(),
        email=(payload.get("email") or "").strip(),
        phone=(payload.get("phone") or "").strip(),
        ok_to_email=ok_to_email,
        ok_to_call=ok_to_call,
        raw_payload=payload,
        status=LeadStatus.RECEIVED,
    )
    
    logger.info(f"Created lead submission {submission.id} for LO {loan_officer.slug}")
    
    # Attempt to enqueue to Service Bus
    if enqueue_lead(str(submission.id)):
        # Successfully queued
        submission.status = LeadStatus.QUEUED
        submission.queued_at = timezone.now()
        submission.save(update_fields=["status", "queued_at"])
        
        logger.info(f"Lead {submission.id} successfully queued to Service Bus")
        
        return JsonResponse(
            {
                "success": True,
                "id": str(submission.id),
                "status": "queued",
                "message": "Lead received and queued for processing"
            },
            status=201
        )
    else:
        # Failed to queue - keep as RECEIVED for manual retry
        submission.attempt_count += 1
        submission.last_error = "Failed to enqueue to Service Bus"
        submission.save(update_fields=["attempt_count", "last_error"])
        
        logger.error(f"Failed to queue lead {submission.id} to Service Bus")
        
        return JsonResponse(
            {
                "error": "Failed to queue lead for processing",
                "id": str(submission.id),
                "status": "received"
            },
            status=500
        )


@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint for Azure monitoring.
    """
    return JsonResponse({"status": "healthy", "service": "dml-marketing-middleware"})
