# path to this file: "dml-marketing-middleware/workers/process_leads.py"

import os
import sys
import django
import json
import time
import logging
from azure.servicebus import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusError

# Setup Django environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django models
from leads.models import LeadSubmission, LeadStatus
from django.utils import timezone
from integrations.total_expert import TotalExpertClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Service Bus configuration
SERVICEBUS_CONNECTION_STRING = os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING")
SERVICEBUS_QUEUE_NAME = os.getenv("AZURE_SERVICEBUS_QUEUE_NAME", "webform-leads")

if not SERVICEBUS_CONNECTION_STRING:
    raise ValueError("AZURE_SERVICEBUS_CONNECTION_STRING environment variable is required")


def process_lead(submission_id):
    """
    Process a single lead submission by posting it to Total Expert.
    
    Args:
        submission_id (str): UUID of the LeadSubmission
    
    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Get the submission with related LoanOfficer
        submission = LeadSubmission.objects.select_related('loan_officer').get(id=submission_id)
        
        logger.info(f"Processing lead {submission_id}: {submission.first_name} {submission.last_name}")
        
        # Check if already synced
        if submission.status == LeadStatus.SYNCED:
            logger.warning(f"Lead {submission_id} already synced, skipping")
            return True
        
        # Validate LO has TE owner ID
        if not submission.loan_officer.te_owner_id:
            error_msg = f"Loan Officer {submission.loan_officer.slug} has no te_owner_id"
            logger.error(error_msg)
            submission.status = LeadStatus.FAILED
            submission.last_error = error_msg
            submission.attempt_count += 1
            submission.save()
            return False
        
        # Create Total Expert client
        te_client = TotalExpertClient()
        
        # Prepare lead data for Total Expert
        lead_data = {
            'first_name': submission.first_name,
            'last_name': submission.last_name,
            'email': submission.email,
            'phone': submission.phone,
            'te_owner_id': submission.loan_officer.te_owner_id,
            'source': f'Web Form - {submission.loan_officer.slug}',
        }
        
        # Add optional metadata if available
        if submission.page_url:
            lead_data['landingPageUrl'] = submission.page_url
        if submission.referrer:
            lead_data['referrer'] = submission.referrer
        
        # Post to Total Expert
        logger.info(f"Posting lead to Total Expert for LO: {submission.loan_officer.slug}")
        result = te_client.create_contact(lead_data)
        
        # Update submission as synced
        submission.status = LeadStatus.SYNCED
        submission.synced_at = timezone.now()
        submission.te_contact_id = result.get('id', '')
        submission.save()
        
        logger.info(f"✓ Successfully synced lead {submission_id} to TE contact {submission.te_contact_id}")
        return True
    
    except LeadSubmission.DoesNotExist:
        logger.error(f"Lead submission {submission_id} not found in database")
        return False
    
    except Exception as e:
        logger.error(f"✗ Error processing lead {submission_id}: {e}", exc_info=True)
        
        # Update submission with error
        try:
            submission = LeadSubmission.objects.get(id=submission_id)
            submission.status = LeadStatus.FAILED
            submission.last_error = str(e)[:500]  # Truncate long errors
            submission.attempt_count += 1
            submission.save()
        except Exception as save_error:
            logger.error(f"Failed to update submission status: {save_error}")
        
        return False


def process_message(message):
    try:
        # Parse message body - CORRECT way for Azure Service Bus
        body_bytes = b''.join(message.body)  # ← Changed
        body = body_bytes.decode('utf-8')
        
        logger.info(f"Raw message body: {body}")  # Debug
        
        data = json.loads(body)
        
        submission_id = data.get('submission_id')
        if not submission_id:
            logger.error("Message missing submission_id")
            logger.error(f"Parsed data: {data}")
            return False
        
        # Process the lead
        return process_lead(submission_id)
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse message JSON: {e}")
        logger.error(f"Body was: {body}")
        return False
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return False


def main():
    """
    Main worker loop that listens to Service Bus queue and processes lead submissions.
    """
    logger.info("="*60)
    logger.info("Starting DML Lead Processing Worker")
    logger.info(f"Queue: {SERVICEBUS_QUEUE_NAME}")
    logger.info("="*60)
    
    # Validate Total Expert credentials before starting
    try:
        te_client = TotalExpertClient()
        te_client.get_access_token()
        logger.info("✓ Total Expert credentials validated")
    except Exception as e:
        logger.error(f"✗ Failed to validate Total Expert credentials: {e}")
        logger.error("Please check TE_CLIENT_ID and TE_CLIENT_SECRET environment variables")
        return
    
    # Start Service Bus receiver
    with ServiceBusClient.from_connection_string(SERVICEBUS_CONNECTION_STRING) as client:
        with client.get_queue_receiver(queue_name=SERVICEBUS_QUEUE_NAME, max_wait_time=5) as receiver:
            logger.info(f"✓ Connected to Service Bus queue: {SERVICEBUS_QUEUE_NAME}")
            logger.info("Waiting for messages... (Press Ctrl+C to stop)")
            
            try:
                while True:
                    # Receive messages in batches
                    messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                    
                    if messages:
                        logger.info(f"Received {len(messages)} message(s)")
                    
                    for message in messages:
                        try:
                            # Process the message
                            success = process_message(message)
                            
                            if success:
                                # Mark message as complete (removes from queue)
                                receiver.complete_message(message)
                            else:
                                # Abandon message (will be retried)
                                receiver.abandon_message(message)
                        
                        except Exception as e:
                            logger.error(f"Error handling message: {e}", exc_info=True)
                            try:
                                receiver.abandon_message(message)
                            except:
                                pass
                    
                    # Small delay between polling
                    time.sleep(1)
            
            except KeyboardInterrupt:
                logger.info("\nShutting down worker...")
            except ServiceBusError as e:
                logger.error(f"Service Bus error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
    
    logger.info("Worker stopped")


if __name__ == '__main__':
    main()
