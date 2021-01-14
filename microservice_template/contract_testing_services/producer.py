import json

def handler(event, context):
    
    print(event)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "field1": "Some value for this testing field",
        "input": event
    }
    
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
