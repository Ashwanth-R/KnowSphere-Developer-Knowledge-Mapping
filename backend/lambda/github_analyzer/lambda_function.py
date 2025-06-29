import json, boto3, os, uuid, datetime, urllib.request

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['RAW_TABLE'])
bedrock = boto3.client('bedrock-runtime')
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
lambda_client = boto3.client('lambda')
lambda_dev_domain_name = os.environ['DEV_DOMAIN_LAMBDA']

def invoke_aggregation_lambda():
    response = lambda_client.invoke(
        FunctionName=lambda_dev_domain_name,  
        InvocationType='Event',  
        Payload=json.dumps({})  
    )

def fetch_file_content(repo_full_name, file_path, commit_id):
    print(f'Fetching file content for {file_path}')
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}?ref={commit_id}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3.raw"
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode()
    except Exception as e:
        return f"Error fetching {file_path}: {e}"


def extract_summary_and_domain(commit_msg, file_contents_summary):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"""You are a code review assistant.

                    Below is a commit message and the actual code changes across multiple files. Write a brief summary describing what the developer worked on.

                    Commit message:
                    {commit_msg}

                    Code changes:
                    {file_contents_summary}

                    Respond in JSON format like this:
                    {{
                    "summary" : ...,
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
        print(f'Parsed - {parsed}')
        return parsed.get("summary", file_contents_summary), parsed.get("domains", [])
    except json.JSONDecodeError:
        return file_contents_summary, []


def lambda_handler(event, context):
    print(f'Event - \n{event}')
    dev = event['pusher']['name']
    repo_name = event['repository']['name']
    repo_full_name = event['repository']['full_name']

    for commit in event['commits']:
        commit_msg = commit['message']
        commit_id = commit['id']
        file_summary = ""

        # Fetch the contents of each modified or added file
        for file_path in commit.get('added', []) + commit.get('modified', []) + commit.get('removed', []):
            content = fetch_file_content(repo_full_name, file_path, commit_id)
            file_summary += f"\n\nFile: {file_path}\n{content[:1000]}"  # Limit to 1000 chars per file

        print(f'File Summary - {file_summary}')
        summary, domains = extract_summary_and_domain(commit_msg, file_summary)
        print(f'Summary - {summary}')
        print(f'Domains - {domains}')

        # Store in DynamoDB
        table.put_item(Item={
            'PK': f'DEV#{dev}',
            'SK': f'SOURCE#GitHub#{str(uuid.uuid4())}',
            'domains': domains,
            'repo': repo_name,
            'commit_message': commit_msg,
            'summary': summary,
            'timestamp': str(datetime.datetime.utcnow())
        })

    # map developer and domain
    print("Invoking Lambda aggregation")
    invoke_aggregation_lambda()

    return {'statusCode': 200, 'body': 'GitHub processed'}
