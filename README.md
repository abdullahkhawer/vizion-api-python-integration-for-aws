# Vizion API Integration for AWS

-   Founder: Abdullah Khawer (LinkedIn: https://www.linkedin.com/in/abdullah-khawer/)
-   Version: v1.0

## Introduction

Vizion API Integration in Python using Flask for AWS using AWS Lambda, AWS API Gateway, AWS S3, and Serverless Framework for Deployment.

AWS Lambda function is using Python 3.7 as its runtime environment.

### Any contributions, improvements and suggestions will be highly appreciated.

## Components Used

Following are the components used in this framework:
-   Python script having the main logic developed in Python 3.7.
-   Boto3 for AWS resources access in Python.
-   Flask for API development in Python.
-   Requests for HTTP/HTTPS requests handing to the Vizion API and Slack in Python.
-   Serverless Framework template in YAML for stack deployment.
-   AWS CloudWatch log group for execution logs by AWS Lambda function.
-   AWS Lambda function to execute the main Python script.
-   AWS IAM role used by the Lambda function with least privileges including AWS S3 write permissions on the desired S3 bucket.
-   AWS API Gateway for API building and management.
-   AWS Lambda Invoke Permission for AWS API Gateway.

## List of Environment Variables

- ENVIRONMENT *(Name of Environment e.g., staging)*
- AWS_REGION *(ID of AWS Region e.g., us-east-1)*
- AWS_LAMBDA_IAM_ROLE_ARN *(ARN of AWS Lambda IAM Role e.g., arn:aws:iam::xxxxxxxxxxxx:role/vizion-api-lambda-role)*
- VIZION_API_HOST *(Vizion API Host e.g., https://demo.vizionapi.com)*
- VIZION_API_KEY *(API Key Provided by the Vizion API)*
- VIZION_API_DATA_S3_BUCKET *(Name of AWS S3 Bucket e.g., my-bucket-12345)*
- (Optional) PAPERTRAIL_HOST *(Papertrail Host e.g., xxxx.papertrailapp.com)*
- (Optional) PAPERTRAIL_PORT *(Papertrail Port e.g., 12345)*
- (Optional) SLACK_WEBHOOK_URL *(Slack Webhook URL e.g., https://hooks.slack.com/services/XXXXX/XXXXX/XXXXXXXXXX)*
- (Optional) SLACK_INFO_CHANNEL *(Slack Info Channel Name e.g., #dummy)*
- (Optional) SLACK_ERROR_CHANNEL *(Slack Info Channel Name e.g., #dummy)*

## Local Deployment Instructions

Pre-requisites:
- Python >= v3.0
- Node >= v10.0.0
- AWS CLI with Credentials Configured having Write Permissions.
- Values for the environment variables mentioned above are set.
- AWS IAM Role for AWS Lambda with Lambda Basic Execution Permissions and AWS S3 Write Permissions for the desired S3 Bucket.

Commands:
- `bash deploy.sh`
- `python api.py`

## Serverless Deployment on AWS Instructions

Pre-requisites:
- Python >= v3.0
- Node >= v10.0.0
- AWS CLI with Credentials Configured having Write Permissions.
- Serverless >= v1.79.0
- Values for the environment variables mentioned above are set.
- AWS IAM Role for AWS Lambda with Lambda Basic Execution Permissions and S3 Write Permissions for the desired S3 Bucket.

Commands:
- `bash deploy.sh`
- `sls deploy`

## Integrated Vizion APIs
Below will be the links of the 6 Vizion APIs that are integrated on AWS which can be accessed over the Internet using a tool like Postman without authentication:
- **METHOD: NAME - URL**
- POST: **Add Container Reference** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/add-container-reference
    - Sample Example:
        {
            "container_id": "TLLU5502800",
            "scac": "ONEY",
            "callback_url": "https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/get-reference-updates-via-callback/"
        }
- GET: **Get Reference Info** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/get-reference-info/[UUID]
- GET: **Get Reference Updates** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/get-reference-updates/[UUID]
- POST: **Get Reference Updates via Callback (For Use by Vizion API Only)** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/get-reference-updates-via-callback/
- DELETE: **Unsubscribe From Reference** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/unsubscribe-from-reference/[UUID]
- GET: **List All Active References** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/list-all-active-references
- GET: **List All Available Carriers** - https://[RESOURCE-ID].execute-api.[REGION].amazonaws.com/staging/list-all-available-carriers

*Note: Don't forget to replace [RESOURCE-ID], [REGION], and/or [UUID] in the above URLs.*

### Warning: You will be billed for the AWS resources used if you create a stack for this solution.
