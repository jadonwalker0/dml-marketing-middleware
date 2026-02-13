"""
Azure Service Bus integration for queuing lead submissions.
"""

import os
import json
import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from django.conf import settings

logger = logging.getLogger(__name__)


def enqueue_lead(submission_id: str) -> bool:
    """
    Enqueue a lead submission to Azure Service Bus for async processing.
    
    Args:
        submission_id: UUID string of the LeadSubmission
        
    Returns:
        True if successfully enqueued, False otherwise
    """
    connection_string = settings.SERVICEBUS_CONNECTION_STRING
    queue_name = settings.SERVICEBUS_QUEUE_NAME
    
    # If not configured, log warning and return False
    if not connection_string:
        logger.warning("Service Bus not configured (SERVICEBUS_CONNECTION_STRING not set)")
        return False
    
    if not queue_name:
        logger.warning("Service Bus queue name not configured")
        return False
    
    try:
        # Prepare message payload
        payload = {
            "submission_id": submission_id,
            "action": "sync_to_crm",
        }
        
        # Send to Service Bus
        with ServiceBusClient.from_connection_string(connection_string) as client:
            with client.get_queue_sender(queue_name=queue_name) as sender:
                message = ServiceBusMessage(
                    json.dumps(payload),
                    content_type="application/json"
                )
                sender.send_messages(message)
        
        logger.info(f"Successfully enqueued lead {submission_id} to Service Bus")
        return True
        
    except Exception as e:
        logger.error(f"Failed to enqueue lead {submission_id} to Service Bus: {e}", exc_info=True)
        return False
