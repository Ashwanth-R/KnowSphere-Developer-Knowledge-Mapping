import boto3, os, json, datetime

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

def extract_jira_summary_and_domains(summary):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"""You are a smart project assistant.

                    Below is a Confluence page. Your task is to:
                    1. Write a 1–2 line summary of what the developer is working on.
                    2. List the technical domains involved in the page where the developer worked on and give appropriate domain suitable for the content in list.

                    Confluence Summary:
                    {summary}

                    Respond in JSON format like this:
                    {{
                    "domains": ["...", "..."]
                    }}"""
                }
            ]
        }
    ]

    response = bedrock.converse(
        modelId="amazon.nova-micro-v1:0",  # or "us.amazon.nova-lite-v1:0"
        messages=messages
    )
     
    output_text = response["output"]["message"]["content"][0]["text"].strip()
    
    try:
        parsed = json.loads(output_text)
        print(f'Parsed \n {parsed}')
        return parsed.get("domains", [])
    except json.JSONDecodeError:
        return []

def lambda_handler(event, context):
    # TODO implement
    print(event)
    author = event['content_author']
    title = event['title']
    content = event['content']
    pageId =   event['pageId']
    
    domains = extract_jira_summary_and_domains(content)

    table.put_item(Item={
        'PK': f'DEV#{author}',
        'SK': f'SOURCE#Confluence#{pageId}',
        'title': title,
        'content': content,
        'domains': domains,
        'timestamp': str(datetime.datetime.utcnow())
    })

    # map developer and domain
    invoke_aggregation_lambda()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Confluence processed successfully')
    }
