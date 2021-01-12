import json
import os
import boto3

client = boto3.client('events')

EVENT_BUS_NAME = os.environ['EVENT_BUS_NAME']

def handler(event, context):
    response = client.put_events(
        Entries=[
            {
                'Source': 'ProducerLambda',
                'DetailType': 'DummyEvent',
                'Detail': json.dumps(event),
                'EventBusName': EVENT_BUS_NAME
            },
        ])

    print(response)
