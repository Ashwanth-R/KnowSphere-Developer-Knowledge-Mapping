import os
import json
import boto3
from collections import defaultdict

# Initialize DynamoDB clients
ddb = boto3.resource("dynamodb")
source_table = ddb.Table(os.environ['RAW_TABLE'])
map_table = ddb.Table(os.environ['DEV_DOMAIN_TABLE'])
alias_table = ddb.Table(os.environ['DEV_IDENTITY_TABLE'])

def normalize_dev_name(raw_name):
    try:
        res = alias_table.get_item(Key={"PK": f"ALIAS#{raw_name}"})
        return res["Item"].get("TargetName", raw_name)
    except:
        return raw_name

def lambda_handler(event, context):
    try:
        # Step 1: Scan source table
        response = source_table.scan()
        items = response.get('Items', [])

        # Step 2: Aggregate by developer
        dev_map = {}

        for item in items:
            pk = item["PK"]
            raw_dev = pk.split("#")[1]
            dev = normalize_dev_name(raw_dev)

            if dev not in dev_map:
                dev_map[dev] = {
                    "domains": defaultdict(int),
                    "summaries": defaultdict(list)
                }

            sk = item["SK"]
            summary = item.get("summary", "") if "GitHub" in sk else item.get("content", "")

            for domain in item.get("domains", []):
                dev_map[dev]["domains"][domain] += 1
                dev_map[dev]["summaries"][domain].append(summary)

        # Step 3: Store in summary table
        for dev, data in dev_map.items():
            total_score = sum(data["domains"].values())

            map_table.put_item(Item={
                "PK": f"DEV#{dev}",
                "domains": dict(data["domains"]),
                "summary": dict(data["summaries"]),
                "total_score": total_score
            })

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Developer domain summary updated successfully."})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
