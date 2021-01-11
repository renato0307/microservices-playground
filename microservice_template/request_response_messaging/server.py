import logging

import boto3

logger = logging.getLogger(__name__)
sqs = boto3.client('sqs')

def handler(event, context):

    try:
        for record in event['Records']:
            queue_url = record['messageAttributes']['ResponseQueueUrl']['stringValue']
            print(f"responding to {queue_url}")
            response_queue = queue_url
            sqs.send_message(
                QueueUrl=response_queue,
                MessageBody="Response OK"
            )

    except Exception as e:
        # Send some context about this error to Lambda Logs
        print(e)
        # throw exception, do not handle. Lambda will make message visible again.
        raise e


