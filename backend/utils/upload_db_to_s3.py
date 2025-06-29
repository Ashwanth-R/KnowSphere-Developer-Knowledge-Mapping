import os
import boto3
import json
from dotenv import load_dotenv
load_dotenv()

REGION = 'us-east-1'
boto3.setup_default_session(profile_name='achu')

ddb = boto3.resource('dynamodb', region_name=REGION)
raw_table = ddb.Table(os.getenv('RAW_TABLE'))
alias_table = ddb.Table(os.getenv('DEV_IDENTITY_TABLE'))
s3 = boto3.client('s3', region_name=REGION)

bucket = 'dev-assistant-knowledge'
prefix = 'developer_contribution/'  # per-record chunk folder

def normalize_dev_name(raw_name):
    try:
        res = alias_table.get_item(Key={"PK": f"ALIAS#{raw_name}"})
        return res["Item"].get("TargetName", raw_name)
    except:
        return raw_name
    
def ensure_bucket_exists(s3_client, bucket_name, region='us-east-1'):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' exists.")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"🪣 Created bucket '{bucket_name}'.")

ensure_bucket_exists(s3, bucket, REGION)

# Scan the whole raw_table (you can paginate if it's large)
response = raw_table.scan()
items = response['Items']

print(f"Total records found: {len(items)}")

for i, item in enumerate(items):
    pk = item.get('PK')         # e.g., DEV#Ashwanth R
    sk = item.get('SK')         # e.g., SOURCE#GitHub#abc123
    content = item.get('summary') or item.get('content') or ""
    domains = item.get('domains', [])

    raw_developer_name = pk.replace('DEV#', '').strip()
    developer_name = normalize_dev_name(raw_developer_name)
    source = sk.split('#')[1] if '#' in sk else 'Unknown'
    source_id = sk.replace("SOURCE#", "").replace("#", "_")

    if isinstance(domains, str):
        domains = [domains]

    # Create the full text chunk
    chunk_text = f"""Developer: {developer_name}
    Source: {source}
    Domains: {", ".join(domains)}
    Content:
    {content}
    """

    file_key = f"{prefix}record_{i}_{developer_name.replace(' ', '_')}_{source_id}.txt"

    try:
        s3.head_object(Bucket=bucket, Key=file_key)
        print(f"⚠️ Skipping existing file: {file_key}")
        continue  # Skip this record
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            # Not found → safe to upload
            s3.put_object(Bucket=bucket, Key=file_key, Body=chunk_text)
            print(f"✅ Uploaded new file: {file_key}")
        else:
            raise

    # s3.put_object(
    #     Bucket=bucket,
    #     Key=file_key,
    #     Body=chunk_text
    # )

    # print(f"✅ Uploaded: {file_key}")
