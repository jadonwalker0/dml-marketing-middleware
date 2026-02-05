import os
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage

SERVICEBUS_CONN_STR = os.getenv("AZURE_SERVICEBUS_CONNECTION_STRING", "")
QUEUE_NAME = os.getenv("AZURE_SERVICEBUS_QUEUE_NAME", "lead-te-upsert")

def enqueue_te_upsert(*, lead_submission_id: str, lo_slug: str) -> None:
    if not SERVICEBUS_CONN_STR:
        raise RuntimeError("Missing AZURE_SERVICEBUS_CONNECTION_STRING")

    body = {
        "action": "UPSERT_TE_CONTACT",
        "lead_submission_id": lead_submission_id,
        "lo_slug": lo_slug,
    }

    msg = ServiceBusMessage(json.dumps(body))

    with ServiceBusClient.from_connection_string(SERVICEBUS_CONN_STR) as client:
        with client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
            sender.send_messages(msg)
