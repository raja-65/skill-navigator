import json
import os
import uuid
import datetime
import urllib.request
import urllib.error
import boto3
from botocore.exceptions import ClientError

# --- Configuration & Environment Variables ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_ID = "llama3-8b-8192"

# AWS Resource Names (Set these in Lambda Environment Variables)
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "SkillNavigatorUsers")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "skill-navigator-roadmaps")

# Initialize AWS Clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
table = dynamodb.Table(DYNAMODB_TABLE)

# --- Database & Storage Logic ---

def check_credits(user_id):
    """
    Checks if the user has at least 1 credit in DynamoDB.
    """
    try:
        response = table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        
        if not item:
            # User doesn't exist, create with default free credits (e.g., 0 or 1 for trial)
            # For this logic, we assume they need to buy or have been initialized elsewhere.
            # Let's initialize with 0 if not found to be safe.
            table.put_item(Item={'user_id': user_id, 'credits': 0})
            return False
            
        credits = int(item.get('credits', 0))
        return credits >= 1
        
    except ClientError as e:
        print(f"DynamoDB Error: {e.response['Error']['Message']}")
        return False

def decrement_credits(user_id):
    """
    Deducts 1 credit from the user's balance using an atomic update.
    """
    try:
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="set credits = credits - :val",
            ConditionExpression="credits >= :val",
            ExpressionAttributeValues={':val': 1},
            ReturnValues="UPDATED_NEW"
        )
        return int(response['Attributes']['credits'])
    except ClientError as e:
        print(f"DynamoDB Error (Decrement): {e.response['Error']['Message']}")
        raise e

def generate_and_upload_document(roadmap_json):
    """
    Converts roadmap JSON to HTML, uploads to S3, and generates a pre-signed URL.
    """
    skill = roadmap_json.get("skill_name", "Skill")
    file_name = f"roadmaps/{uuid.uuid4()}.html"
    
    # HTML Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Roadmap: {skill}</title>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2563eb; }}
            .step {{ margin-bottom: 20px; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }}
            .step-title {{ font-weight: bold; font-size: 1.2em; }}
            .resources {{ margin-top: 10px; }}
            .resource-link {{ color: #059669; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>Learning Roadmap: {skill}</h1>
        <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
        <hr>
    """
    
    for step in roadmap_json.get("roadmap_steps", []):
        resources_html = ""
        for res in step.get("resources", []):
            resources_html += f'<li><a href="{res["url"]}" class="resource-link" target="_blank">{res["name"]}</a> ({res["type"]})</li>'
            
        html_content += f"""
        <div class="step">
            <div class="step-title">Step {step.get('step_number')}: {step.get('title')}</div>
            <p>{step.get('description')}</p>
            <p><strong>Estimated Time:</strong> {step.get('estimated_time')}</p>
            <div class="resources">
                <strong>Resources:</strong>
                <ul>{resources_html}</ul>
            </div>
        </div>
        """
        
    html_content += "</body></html>"
    
    # Upload to S3
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=html_content,
            ContentType='text/html'
        )
        
        # Generate Pre-signed URL (valid for 1 hour)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': file_name},
            ExpiresIn=3600
        )
        return url
    except ClientError as e:
        print(f"S3 Error: {e}")
        raise e

# --- Groq Inference Logic ---

def call_groq_api(skill_name, current_level):
    """
    Calls Groq API to generate the roadmap.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")

    system_prompt = (
        "You are an expert career counselor and resource curator. "
        "Your goal is to create a hyper-curated, actionable learning roadmap for a specific skill. "
        "You must provide specific, high-quality resources (real links if known, or realistic placeholders). "
        "You must strictly follow the JSON schema provided."
    )
    
    user_prompt = (
        f"Create a learning roadmap for '{skill_name}' starting at a '{current_level}' level. "
        "Include 3-5 distinct steps. For each step, provide a title, description, estimated time, and 2-3 specific resources."
    )
    
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    try:
        req = urllib.request.Request(GROQ_API_URL, data=json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            data = json.loads(response_body)
            content = data['choices'][0]['message']['content']
            return json.loads(content)
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        raise e

# --- Main Lambda Handler ---

def lambda_handler(event, context):
    """
    AWS Lambda Entry Point.
    """
    print("Received event:", json.dumps(event))
    
    try:
        # Handle CORS preflight (if not handled by API Gateway)
        if event.get('httpMethod') == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": ""
            }

        # Parse body
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event

        user_id = body.get('user_id')
        skill_name = body.get('skill_name')
        current_level = body.get('current_level')

        if not all([user_id, skill_name, current_level]):
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"status": "error", "message": "Missing required fields."})
            }

        # 1. Check Credits
        if not check_credits(user_id):
            return {
                "statusCode": 402, # Payment Required
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"status": "error", "message": "Insufficient credits."})
            }

        # 2. Generate Roadmap (Groq)
        roadmap_json = call_groq_api(skill_name, current_level)

        # 3. Generate Document (S3)
        download_url = generate_and_upload_document(roadmap_json)

        # 4. Deduct Credit
        new_balance = decrement_credits(user_id)

        # 5. Return Success
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "status": "success",
                "message": "Roadmap generated and credit deducted.",
                "download_url": download_url,
                "new_credit_balance": new_balance
            })
        }

    except Exception as e:
        print(f"Internal Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"status": "error", "message": str(e)})
        }

