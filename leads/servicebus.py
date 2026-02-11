# path to this file: "dml-marketing-middleware/leads/>file<"

import os
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage

SERVICEBUS_CONNECTION_STRING = os.getenv("SERVICEBUS_CONNECTION_STRING", "")
SERVICEBUS_QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "webform-leads")

def enqueue_lead(submission_id: str) -> None:
    # If not configured, don't crash locally
    if not SERVICEBUS_CONNECTION_STRING:
        return

    body = {"submission_id": submission_id}

    with ServiceBusClient.from_connection_string(SERVICEBUS_CONNECTION_STRING) as client:
        with client.get_queue_sender(queue_name=SERVICEBUS_QUEUE_NAME) as sender:
            sender.send_messages(ServiceBusMessage(json.dumps(body)))
