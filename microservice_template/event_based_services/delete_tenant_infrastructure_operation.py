import datetime
import json
import os
import uuid

import boto3

from events import DetailTypeEnum, EventEncoder, TenantEvent


def handler(event, context):
    print(f"processing {event}")

    if not event['detail-type'] == 'delete_tenant':
        raise Exception("I don't know what to do with this event")

    print(f"deleting tenant infrastructure: {event}")
    pass  # DO THE REAL WORK
    print(f"tenant infrastructure deleted: {event}")

    # send operation completion event
    event = TenantEvent(
        uuid=str(uuid.uuid4()),
        correlation_id=event['detail']['uuid'],
        source='DeleteTenatInfrastructureOperation',
        detail_type=DetailTypeEnum.delete_tenant_infrastructure_done.value,
        timestamp=datetime.datetime.utcnow(),
        operation_uuid=event['detail']['operation_uuid'],
        operation_type=event['detail']['operation_type'],
        termination_table=event['detail']['termination_table'],
        tenant_id=event['detail']['tenant_id'])

    print(f"sending event {event}")
    json_event = json.dumps(event.dict(), cls=EventEncoder)
    client = boto3.client('events')
    response = client.put_events(
        Entries=[
            {
                'Source': event.source,
                'DetailType': event.detail_type,
                'Detail': json_event,
                'EventBusName': os.environ["EVENT_BUS_NAME"]
            },
        ])

    print(f"event sent: {response}")
