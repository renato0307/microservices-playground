import os
import json 
import requests

PRODUCER_ENDPOINT = os.environ["PRODUCER_ENDPOINT"]

def handler(event, context):
    response = requests.get(PRODUCER_ENDPOINT)

    body = json.loads(response.text)
    print(body["field1"])

    response = {
        "statusCode": 200,
        "body": body["field1"]
    }

    return response
