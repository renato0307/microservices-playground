import datetime
import json
import os
import uuid

import boto3
from python_dynamodb_lock.python_dynamodb_lock import *

from events import DetailTypeEnum, EventEncoder, TenantEvent


def handler(event, context):
    print(f"processing {event}")
