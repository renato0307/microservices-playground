import base64
import json
import logging
import os
import uuid

from faker import Faker
from pynamodb.attributes import UnicodeAttribute
from pynamodb.connection import Connection
from pynamodb.exceptions import TransactWriteError
from pynamodb.models import Model
from pynamodb.transactions import TransactWrite

TASK_TABLE_NAME = os.environ["TASK_TABLE_NAME"]
OUTBOX_TABLE_NAME = os.environ["OUTBOX_TABLE_NAME"]

logging.basicConfig()
log = logging.getLogger("pynamodb")
log.setLevel(logging.INFO)
log.propagate = True


class BaseModel(Model):
    def to_dict(self):
        rval = {}
        for key in self.attribute_values:
            rval[key] = self.__getattribute__(key)
        return rval


class TaskData(BaseModel):
    """
    Task data model 
    """
    class Meta:
        table_name = TASK_TABLE_NAME
        region = "eu-west-1"

    task_id = UnicodeAttribute(hash_key=True)
    field1 = UnicodeAttribute()
    field2 = UnicodeAttribute()


class OutboxEvent(BaseModel):
    """
    Outbox event data model 
    """
    class Meta:
        table_name = OUTBOX_TABLE_NAME
        region = "eu-west-1"

    event_id = UnicodeAttribute(hash_key=True)
    event_content = UnicodeAttribute()


def handler(event, context) -> None:
    connection = Connection("eu-west-1")
    fake = Faker()

    task_data = TaskData(
        task_id=str(uuid.uuid4()),
        field1=fake.name(),
        field2=fake.address())

    event = OutboxEvent(
        event_id=str(uuid.uuid4()),
        event_content=json.dumps(task_data.to_dict()))

    print(f"saving {task_data.task_id} and "
          f"sending event {event.event_content} ")
    try:
        with TransactWrite(connection=connection) as transaction:
            transaction.save(task_data)
            transaction.save(event)
    except TransactWriteError as e:
        print(e.cause)
        print(e.cause_response_code)
        raise e
