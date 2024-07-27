import json
import boto3
import os

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    message = json.loads(event['body'])['message']
    paginator = dynamodb.get_paginator('scan')
    connectionIds = []

    apigatewaymanagementapi = boto3.client(
        'apigatewaymanagementapi', 
        endpoint_url = f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )

    for page in paginator.paginate(TableName=os.environ['WEBSOCKET_TABLE']):
        connectionIds.extend(page['Items'])

    for connectionId in connectionIds:
        try:
            apigatewaymanagementapi.post_to_connection(
                Data=message,
                ConnectionId=connectionId['connectionId']['S']
            )
        except apigatewaymanagementapi.exceptions.GoneException:
            print(f"Connection {connectionId['connectionId']['S']} is gone, cleaning up.")
            # Remove stale connection ID from the table here

    return {}
