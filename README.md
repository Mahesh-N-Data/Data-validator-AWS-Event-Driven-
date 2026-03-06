# AWS Event-Driven Data Validator

## Project Overview
An automated serverless pipeline that validates incoming data files in real-time. It uses **AWS S3 Event Notifications** to trigger an **AWS Lambda** function, which checks the schema of uploaded CSV files. Valid files are promoted to a "Clean Zone," while invalid files are quarantined, and an alert is sent via **AWS SNS**.

## Architecture
Flow: User Upload -> S3 Landing Zone -> S3 Event Notification -> AWS Lambda -> S3 Clean/Quarantine + SNS Alert

<img width="1536" height="1024" alt="Serverless data pipe" src="https://github.com/user-attachments/assets/c0431d89-773f-4e6b-ae04-41659288efea" />


## Technologies Used
Compute: AWS Lambda (Python 3.9)
Storage: AWS S3 (Simple Storage Service)
Messaging: AWS SNS (Simple Notification Service)
IAM: Security & Permissions Management


## How It Works

### 1. Ingestion Trigger
Users upload raw CSV files to the `landing_zone/` folder in an S3 bucket.
An S3 Event Notification instantly triggers the Lambda function.

### 2. Validation Logic (Python)
The Lambda function reads the file header (without downloading the whole file).
Rule: Checks if the header matches: `order_date,product,region,quantity,price`.
Bug Fix: Implemented `utf-8-sig` decoding to handle BOM characters often found in Windows-generated CSVs.

### 3. Automated Routing
Pass: If the schema is correct, the file is moved to the `clean_zone/` folder for downstream processing.
Fail: If the schema is incorrect, the file is moved to the `quarantine_zone/` folder.

### 4. Alerting
If a file fails validation, the Lambda function publishes a message to an **AWS SNS Topic**, which sends an immediate email notification to the Data Engineering team.


## 📂 Project Structure

├── lambda_function.py   # The core logic for validation and routing
├── data/
│   ├── valid_data.csv   # Sample file that passes validation
│   └── bad_data.csv     # Sample file that triggers the alarm
└── README.md
