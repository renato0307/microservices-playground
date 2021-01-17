import datetime
import os

import dateutil.parser
from pynamodb.attributes import (ListAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.models import Model

TABLE_NAME = os.environ["TABLE_NAME"]
TABLE_REGION = os.environ["TABLE_REGION"]


class EventModel(Model):
    """
    Event to store in DynamoDB
    """
    class Meta:
        table_name = TABLE_NAME
        region = TABLE_REGION

    event_uuid = UnicodeAttribute(hash_key=True)
    detail_type = UnicodeAttribute(range_key=True)

    operation_type = UnicodeAttribute()
    operation_uuid = UnicodeAttribute()

    source = UnicodeAttribute()
    correlation_id = UnicodeAttribute()
    event_timestamp = UTCDateTimeAttribute()

    termination_table = ListAttribute()


def handler(event, context):
    print(f"processing {event}")

    db_event = EventModel(event['detail']['uuid'], event['detail-type'])

    date_time_obj = dateutil.parser.isoparse(event['detail']['timestamp'])

    db_event.operation_uuid = event['detail']['operation_uuid']
    db_event.operation_type = event['detail']['operation_type']
    db_event.correlation_id = event['detail']['correlation_id']
    db_event.source = event['source']
    db_event.event_timestamp = date_time_obj
    db_event.termination_table = event['detail']['termination_table']

    db_event.save()

    print("event saved into dynamodb")
