# --- Lambda: chat_handler with RAG via Bedrock Knowledge Base ---
import os
import json
import boto3

# Initialize Bedrock Agent client
bedrock_agent = boto3.client("bedrock-agent-runtime")

def lambda_handler(event, context):
    print(f"Received event: {event}")

    # Extract message
    try:
        if "message" in event:
            user_message = event["message"]
        else:
            user_message = json.loads(event['body'])['message']
    except Exception as e:
        print("Invalid input format", str(e))
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing or invalid 'message' in request."})
        }

    # Call Bedrock RAG
    try:
        response = bedrock_agent.retrieve_and_generate(
            input={"text": user_message},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": os.environ['KNOWLEDGE_BASE_ID'],
                    "modelArn": os.environ['BEDROCK_MODEL_ARN']
                }
            }
        )


        print("RAG raw response:", response)
        answer = response['output']['text']

    except Exception as e:
        print("Bedrock RAG failed:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to query knowledge base."})
        }

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"response": answer})
    }
