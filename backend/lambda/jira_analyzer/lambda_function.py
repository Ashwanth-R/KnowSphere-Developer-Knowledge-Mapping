import boto3
import os
import json
import datetime

# AWS clients
ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['RAW_TABLE'])
bedrock = boto3.client('bedrock-runtime')
lambda_client = boto3.client('lambda')
lambda_dev_domain_name = os.environ['DEV_DOMAIN_LAMBDA']

def invoke_aggregation_lambda():
    response = lambda_client.invoke(
        FunctionName=lambda_dev_domain_name,  
        InvocationType='Event',  
        Payload=json.dumps({})  
    )

#=== LLM Analysis Function ===
def extract_jira_summary_and_domains(summary, description):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"""You are a smart project assistant.

                    Below is a Jira ticket. Your task is to:
                    1. Write a brief summary of what the developer is working on.
                    2. List the technical domains involvedin the ticket and give appropriate domain suitable for the ticket in list.

                    Jira Summary:
                    {summary}

                    Jira Description:
                    {description}

                    Respond in JSON format like this:
                    {{
                    "summary": "...",
                    "domains": ["...", "..."]
                    }}"""
                }
            ]
        }
    ]

    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",  # Or "us.amazon.nova-lite-v1:0"
        messages=messages
    )

    output_text = response["output"]["message"]["content"][0]["text"].strip()

    try:
        parsed = json.loads(output_text)
        print(f'Parsed \n {parsed}')
        return parsed.get("summary", summary), parsed.get("domains", [])
    except json.JSONDecodeError:
        return summary, []

# === Lambda Handler ===
def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # Parse event body (API Gateway style or direct)
    body = json.loads(event['body']) if 'body' in event else event
    issue = body['issue']
    fields = issue['fields']

    summary = fields.get('summary', '')
    description = fields.get('description', '')
    dev = fields.get('assignee', {}).get('displayName', 'Unassigned')
    issue_key = issue['key']

    # Use Bedrock LLM to analyze ticket
    task_summary, domains = extract_jira_summary_and_domains(summary, description)

    # Store to DynamoDB
    table.put_item(Item={
        'PK': f'DEV#{dev}',
        'SK': f'SOURCE#Jira#{issue_key}',
        'content': task_summary,
        'domains': domains,
        'timestamp': str(datetime.datetime.utcnow())
    })

    # map developer and domain
    invoke_aggregation_lambda()

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Jira ticket processed'})
    }
