import string
import random
import os
import logging

import boto3

logger = logging.getLogger(__name__)
sqs = boto3.client('sqs')

REQUEST_QUEUE_URL = os.environ['REQUEST_QUEUE']

def handler(event, context):

    # Create temporary response queue
    response_queue_name = 'temporary-' + (''.join(random.choices(string.ascii_uppercase + string.digits, k = 20)))
    response = sqs.create_queue(
        QueueName=response_queue_name,
        Attributes={
            'VisibilityTimeout': '300',
            'Policy': '{ "Version": "2012-10-17", "Statement": ['
                       '{ "Effect": "Allow", "Action": "sqs:SendMessage", "Resource": "*", "Principal": "*" }, '
                       '{ "Effect": "Allow", "Action": "sqs:DeleteQueue", "Resource": "*", "Principal": "*" }, '
                       '{ "Effect": "Allow", "Action": "sqs:ReceiveMessage", "Resource": "*", "Principal": "*" }]}'
        }
    )
    
    print(f"create queue response: {response}")
    response_queue_url = response['QueueUrl']

    try:
        # Sends request        
        print("sending message")
        response = sqs.send_message(
            QueueUrl=REQUEST_QUEUE_URL,
            DelaySeconds=0,
            MessageAttributes={
                'ResponseQueueUrl': {
                    'DataType': 'String',
                    'StringValue': response_queue_url
                },
            },
            MessageBody='This a message from a client'
        )
    
        print(response['MessageId'])
    
        # Receives response
        for _ in range(30):
            print("waiting for response")
            response = sqs.receive_message(
                QueueUrl=response_queue_url,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=0,
                WaitTimeSeconds=1
            )
            messages = response.get('Messages', [])
            if len(messages) > 0:
                print("response found")
                print(f"response is {messages[0]}")
                break
    
    except Exception as e:
        print(e)
        raise(e)
    finally:
        # Deletes temporary response queue
        response = sqs.delete_queue(QueueUrl=response_queue_url)
        pass

