from django.shortcuts import render
import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from core.models import LoanOfficer
from .models import LeadSubmission, LeadStatus
from .servicebus import enqueue_te_upsert

# Create your views here.

logger = logging.getLogger(__name__)

# get payload, as a function to reuse
def _get_payload(request):
    # Content Type definition, saved as variable 'ctype'
    ctype = (request.content_type or "").lower()
    # if the content is type: "JSON"
    if "application/json" in ctype:
        # continue in this try clause, return the json object
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            return {}
    # else return the POST dictionary.
    return request.POST.dict()

@csrf_exempt
def webform_lead(request):
    # let's ensure that the method used is POST to access our endpoint, no other method is allowed
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # extract payload by calling & using our previous function with the request as argument
    payload = _get_payload(request)

    # search for "lo_slug" in the payload, normalize it by stripping spaces, slashes, and lowercasing
    lo_slug = (payload.get("lo_slug") or "").strip().strip("/").lower()
    if not lo_slug:
        ### (I may need to come back to this and log attempts without lo_slug, as well as consider not failing on this condition)
        logger.warning("Received lead without lo_slug")
        return JsonResponse({"error": "lo_slug is required"}, status=400)

    # look for the Loan Officer with the given slug, on the sqlite database, ensure it's active
    lo = LoanOfficer.objects.filter(slug__iexact=lo_slug, is_active=True).first()
    if not lo:
        return JsonResponse({"error": "Unknown or inactive loan officer"}, status=404)

    # extract lead details from payload, with some normalization
    # first name, last name, email, phone
    first_name = (payload.get("first_name") or payload.get("First Name") or "").strip()
    last_name  = (payload.get("last_name")  or payload.get("Last Name")  or "").strip()
    email      = (payload.get("email")      or payload.get("Email")      or "").strip().lower()
    phone      = (payload.get("phone")      or payload.get("Phone")      or "").strip()

    # capture page_url and referrer marketing data from payload
    page_url = (payload.get("page_url") or "").strip()
    referrer = (payload.get("referrer") or "").strip()

    # capture IP address and User-Agent from request metadata
    ip = request.META.get("REMOTE_ADDR")
    ua = request.META.get("HTTP_USER_AGENT", "")

    # create LeadSubmission record within a transaction
    with transaction.atomic():
        lead = LeadSubmission.objects.create(
            loan_officer=lo,
            page_url=page_url,
            referrer=referrer,
            ip_address=ip if ip else None,
            user_agent=ua,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            raw_payload=payload,
            status=LeadStatus.RECEIVED,
        )

        # enqueue the lead for TE upsert processing (put the lead data onto Azure Service Bus, into a queue)
        enqueue_te_upsert(lead_submission_id=str(lead.id), lo_slug=lo.slug)

        # update lead status to QUEUED and set queued_at timestamp
        lead.status = LeadStatus.QUEUED
        lead.queued_at = timezone.now()
        lead.save(update_fields=["status", "queued_at"])
    # log the queuing event
    logger.info("Lead queued %s for LO %s", lead.id, lo.slug)
    # respond with success, including the lead_submission_id
    return JsonResponse({"ok": True, "lead_submission_id": str(lead.id)}, status=202)
