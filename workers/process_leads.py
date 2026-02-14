"""
Service Bus worker to process lead submissions and sync to Total Expert.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.utils import timezone
from azure.servicebus import ServiceBusClient
from leads.models import LeadSubmission, LeadStatus
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Total Expert configuration
TE_CLIENT_ID = os.getenv("TE_CLIENT_ID", "")
TE_CLIENT_SECRET = os.getenv("TE_CLIENT_SECRET", "")
TE_API_URL = os.getenv("TE_API_URL", "https://api.totalexpert.net")

# Service Bus configuration
SERVICEBUS_CONNECTION_STRING = os.getenv("SERVICEBUS_CONNECTION_STRING", "")
SERVICEBUS_QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "webform-leads")

# Cache for access token
_access_token = None
_token_expires_at = None


def get_te_access_token():
    """Get Total Expert OAuth access token."""
    global _access_token, _token_expires_at
    
    # Return cached token if still valid
    if _access_token and _token_expires_at and datetime.now() < _token_expires_at:
        return _access_token
    
    logger.info("Requesting new Total Expert access token...")
    
    try:
        response = requests.post(
            f"{TE_API_URL}/v1/token",
            data={
                "grant_type": "client_credentials",
                "client_id": TE_CLIENT_ID,
                "client_secret": TE_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        
        data = response.json()
        _access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        _token_expires_at = datetime.now() + timezone.timedelta(seconds=expires_in - 300)  # 5 min buffer
        
        logger.info("Successfully obtained Total Expert access token")
        return _access_token
        
    except Exception as e:
        logger.error(f"Failed to get Total Expert access token: {e}")
        raise


def sync_lead_to_total_expert(submission):
    """Sync a lead submission to Total Expert CRM."""
    logger.info(f"Syncing lead {submission.id} to Total Expert...")
    
    try:
        # Get access token
        access_token = get_te_access_token()
        
        # Prepare contact data
        contact_data = {
            "first_name": submission.first_name,
            "last_name": submission.last_name,
            "email": submission.email,
            "phoneNumbers": [{"phoneNumber": submission.phone, "primary": True}],
            "owner": {
                "external_id": submission.loan_officer.te_owner_id,
                "email": submission.loan_officer.email
            }
        }
        
        # Create/update contact in Total Expert
        response = requests.post(
            f"{TE_API_URL}/v1/contacts",
            json=contact_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        
        result = response.json()
        te_contact_id = result.get("id") or result.get("contactId")
        
        # Update submission status
        submission.status = LeadStatus.SYNCED
        submission.te_contact_id = str(te_contact_id)
        submission.synced_at = timezone.now()
        submission.last_error = ""
        submission.save()
        
        logger.info(f"Successfully synced lead {submission.id} to Total Expert (contact ID: {te_contact_id})")
        return True
        
    except requests.HTTPError as e:
        error_msg = f"Total Expert API error: {e.response.status_code} - {e.response.text}"
        logger.error(f"Failed to sync lead {submission.id}: {error_msg}")
        
        submission.status = LeadStatus.FAILED
        submission.attempt_count += 1
        submission.last_error = error_msg[:500]  # Truncate if too long
        submission.save()
        
        return False
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Failed to sync lead {submission.id}: {error_msg}")
        
        submission.status = LeadStatus.FAILED
        submission.attempt_count += 1
        submission.last_error = error_msg[:500]
        submission.save()
        
        return False


def process_message(message):
    """Process a single Service Bus message."""
    try:
        # Parse message body
        message_body = json.loads(str(message))
        submission_id = message_body.get("submission_id")
        
        if not submission_id:
            logger.warning("Message missing submission_id")
            return False
        
        logger.info(f"Processing message for submission {submission_id}")
        
        # Get submission from database
        try:
            submission = LeadSubmission.objects.get(id=submission_id)
        except LeadSubmission.DoesNotExist:
            logger.error(f"Submission {submission_id} not found in database")
            return False
        
        # Skip if already synced
        if submission.status == LeadStatus.SYNCED:
            logger.info(f"Submission {submission_id} already synced, skipping")
            return True
        
        # Sync to Total Expert
        return sync_lead_to_total_expert(submission)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return False


def main():
    """Main worker loop."""
    logger.info("Starting Lead Processing Worker...")
    logger.info(f"Service Bus Queue: {SERVICEBUS_QUEUE_NAME}")
    logger.info(f"Total Expert API: {TE_API_URL}")
    
    if not SERVICEBUS_CONNECTION_STRING:
        logger.error("SERVICEBUS_CONNECTION_STRING not configured")
        sys.exit(1)
    
    if not TE_CLIENT_ID or not TE_CLIENT_SECRET:
        logger.error("Total Expert credentials not configured")
        sys.exit(1)
    
    # Connect to Service Bus
    with ServiceBusClient.from_connection_string(SERVICEBUS_CONNECTION_STRING) as client:
        with client.get_queue_receiver(queue_name=SERVICEBUS_QUEUE_NAME) as receiver:
            logger.info("Connected to Service Bus, waiting for messages...")
            
            while True:
                try:
                    # Receive messages (wait up to 60 seconds)
                    messages = receiver.receive_messages(max_message_count=10, max_wait_time=60)
                    
                    if not messages:
                        logger.debug("No messages received, continuing...")
                        continue
                    
                    logger.info(f"Received {len(messages)} message(s)")
                    
                    for message in messages:
                        try:
                            success = process_message(message)
                            
                            if success:
                                # Complete the message (remove from queue)
                                receiver.complete_message(message)
                                logger.info("Message completed successfully")
                            else:
                                # Abandon the message (will retry later)
                                receiver.abandon_message(message)
                                logger.warning("Message abandoned, will retry")
                                
                        except Exception as e:
                            logger.error(f"Error handling message: {e}", exc_info=True)
                            receiver.abandon_message(message)
                    
                except KeyboardInterrupt:
                    logger.info("Shutting down worker...")
                    break
                    
                except Exception as e:
                    logger.error(f"Worker error: {e}", exc_info=True)
                    time.sleep(5)  # Wait before retrying


if __name__ == "__main__":
    main()