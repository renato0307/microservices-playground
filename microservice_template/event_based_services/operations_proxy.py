import datetime
import json
import os
import uuid

import boto3
from fastapi import FastAPI
from mangum import Mangum

from events import DetailTypeEnum, EventEncoder, OperationTypeEnum, TenantEvent

app = FastAPI()


@app.delete("/tenant/{tenant_id}")
def delete_tenant(tenant_id: str):

    # sends the delete tenant main event
    event_id = str(uuid.uuid4())
    event = TenantEvent(
        uuid=event_id,
        correlation_id=event_id,  # the start of the chain
        source='OperationsProxy',
        detail_type=DetailTypeEnum.delete_tenant.value,
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        operation_uuid=str(uuid.uuid4()),
        operation_type=OperationTypeEnum.delete_tenant.value,
        termination_table=[
            DetailTypeEnum.delete_tenant_infrastructure_done.value,
            DetailTypeEnum.delete_license_done.value
        ],
        tenant_id=tenant_id)

    # sends the event to the bus
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

    print(response)

    return event


handler = Mangum(app)
