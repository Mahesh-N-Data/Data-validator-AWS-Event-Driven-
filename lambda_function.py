import json
import boto3
import urllib.parse
import os

s3 = boto3.client('s3')
sns = boto3.client('sns')

# --- CONFIGURATION ---
SNS_TOPIC_ARN = 'YOUR_SNS_ARN_HERE'  # <--- PASTE YOUR ARN HERE
# ---------------------

def lambda_handler(event, context):
    # 1. Get the bucket name and file key from the event trigger
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        print(f"File detected: {key} in bucket: {bucket}")
        
        # 2. Read the first line of the file (The Header)
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8-sig')
        lines = content.split('\n')
        header_row = lines[0].strip()
        
        # 3. Validation Logic: Check if header matches expected schema
        # We expect: order_date,product,region,quantity,price
        expected_schema = "order_date,product,region,quantity,price"
        
        if header_row == expected_schema:
            print("Validation Success: Moving to clean_zone")
            
            # Copy to Clean Zone
            new_key = key.replace("landing_zone/", "clean_zone/")
            s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=new_key)
            
            # Delete from Landing Zone
            s3.delete_object(Bucket=bucket, Key=key)
            
        else:
            print(f"Validation Failed. Found header: {header_row}")
            raise Exception("Invalid Schema Mismatch")

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        
        # 4. Failure Handling: Move to Quarantine and Alert
        print("Moving file to quarantine_zone and sending alert...")
        
        # Copy to Quarantine
        bad_key = key.replace("landing_zone/", "quarantine_zone/")
        s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=bad_key)
        
        # Delete from Landing
        s3.delete_object(Bucket=bucket, Key=key)
        
        # Send Email via SNS
        message = f"ALARM: Data Validation Failed!\n\nFile: {key}\nError: {str(e)}\nBucket: {bucket}"
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message, Subject="Data Ingestion Failure")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Process Complete')
    }