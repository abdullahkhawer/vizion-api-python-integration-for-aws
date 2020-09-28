import os
import json
import logging
import boto3
import requests
import traceback
from flask import Flask
from flask import request
from logging.handlers import SysLogHandler
from urllib.request import Request, urlopen, URLError, HTTPError

ENVIRONMENT = os.environ['ENVIRONMENT']
VIZION_API_KEY = os.environ['VIZION_API_KEY']
VIZION_API_DATA_S3_BUCKET = os.environ['VIZION_API_DATA_S3_BUCKET']
VIZION_ADD_CONTAINER_REFERENCE_API = os.environ['VIZION_API_HOST'] + "/references"
VIZION_GET_REFERENCE_INFO_API = os.environ['VIZION_API_HOST'] + "/references/%s"
VIZION_GET_REFERENCE_UPDATES_API = os.environ['VIZION_API_HOST'] + "/references/%s/updates"
VIZION_UNSUBSCRIBE_FROM_REFERENCE_API = os.environ['VIZION_API_HOST'] + "/references/%s"
VIZION_LIST_ALL_ACTIVE_REFERENCES_API = os.environ['VIZION_API_HOST'] + "/references?include_metadata=true"
VIZION_LIST_ALL_AVAILABLE_CARRIERS_API = os.environ['VIZION_API_HOST'] + "/carriers"
PAPERTRAIL_HOST = os.environ['PAPERTRAIL_HOST']
PAPERTRAIL_PORT = os.environ['PAPERTRAIL_PORT']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
SLACK_INFO_CHANNEL = os.environ['SLACK_INFO_CHANNEL']
SLACK_ERROR_CHANNEL = os.environ['SLACK_ERROR_CHANNEL']

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if ENVIRONMENT != "DEV" and PAPERTRAIL_HOST != "" and PAPERTRAIL_PORT != "":
    syslog = SysLogHandler(address=(PAPERTRAIL_HOST, int(PAPERTRAIL_PORT)))
    format = '%(asctime)s Environment: ' + ENVIRONMENT + ' - VIZION-API: %(message)s'
    formatter = logging.Formatter(format, datefmt='%b %d %H:%M:%S')
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)

headers = {'X-API-Key': VIZION_API_KEY, 'Content-Type': 'application/json'}

app = Flask(__name__)

def post_message_on_slack(SLACK_CHANNEL, SLACK_MESSAGE='DEFAULT MESSAGE'):
    if SLACK_WEBHOOK_URL != "" and SLACK_CHANNEL != "":
        slack_message = {
            "username": "Serverless Vizion API Notification Bot",
            "channel": SLACK_CHANNEL,
            "text": SLACK_MESSAGE
        }

        req = Request(SLACK_WEBHOOK_URL, data=bytes(json.dumps(slack_message), encoding="utf-8"))

        try:
            response = urlopen(req)
            response.read()
            logger.info("Notified Slack in the '" + slack_message['channel'] + "' channel.")
        except HTTPError as error:
            error = traceback.format_exc()
            error_statement = "ERROR: Failed to Send Notification on Slack - Reason: " + str(error)
            logger.error(error_statement)
        except URLError as error:
            error = traceback.format_exc()
            error_statement = "ERROR: Failed to Send Notification on Slack - Reason: " + str(error)
            logger.error(error_statement)

def add_json_object_on_s3(json_object, data_type, timestamp=""):
    s3_client = boto3.client('s3')

    object_key = "vizion-api-data/" + json_object['carrier_scac'] + "/" + json_object['container_id'] + "/" + data_type + timestamp + ".json"

    return s3_client.put_object(
        Body=str(json.dumps(json_object)),
        Bucket=VIZION_API_DATA_S3_BUCKET,
        Key=object_key
    )

    logger.info("File Uploaded on AWS S3 Successfully.")

@app.route("/")
def main():
    print_statement = "Vizion API Integration is Running."

    logger.info(print_statement)

    return {
        'statusCode': 200,
        'body': print_statement
    }

@app.route("/add-container-reference/", methods=["POST"])
def add_container_reference():
    try:
        response = requests.post(VIZION_ADD_CONTAINER_REFERENCE_API, headers=headers, data=request.data)
        response_status = response.status_code
        response_message = response.text

        if response_message == "":
            response_message = {
                "httpMessage":"Added.",
                "httpStatusCode": response_status
            }
        else:
            response_message = json.loads(response_message)
            add_json_object_on_s3(response_message['reference'], "creation")

        logger.info("Container Reference Added Successfully.")

        return {
            'statusCode': response_status,
            'body': response_message
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Add Container Reference - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

@app.route("/get-reference-info/<string:referenceId>", methods=["GET"])
def get_reference_info(referenceId):
    try:
        response = requests.get(VIZION_GET_REFERENCE_INFO_API % referenceId, headers=headers)
        response_status = response.status_code
        response_message = response.text

        if response_message == "":
            response_message = {
                "httpMessage":"Received.",
                "httpStatusCode": response_status
            }
        else:
            response_message = json.loads(response_message)
            add_json_object_on_s3(response_message, "info")

        logger.info("Container Reference Received Successfully.")

        return {
            'statusCode': response_status,
            'body': response_message
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Get Container Reference Info - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

@app.route("/get-reference-updates/<string:referenceId>", methods=["GET"])
def get_reference_updates(referenceId):
    try:
        response = requests.get(VIZION_GET_REFERENCE_UPDATES_API % referenceId, headers=headers)
        response_status = response.status_code
        response_message = response.text

        if response_message == "":
            response_message = {
                "httpMessage":"Received.",
                "httpStatusCode": response_status
            }
        else:
            response_message = json.loads(response_message)
            for item in response_message:
                add_json_object_on_s3(item['payload'], "updates", "-" + item['updated_at'])

        logger.info("Container Reference Updates Received Successfully.")

        return {
            'statusCode': response_status,
            'body': response_message
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Get Container Reference Updates - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

@app.route("/get-reference-updates-via-callback/", methods=["POST"])
def get_reference_updates_via_callback():
    try:
        response_status = 200
        response_message = json.loads(request.data)
        add_json_object_on_s3(response_message['payload'], "updates-via-callback", "-" + response_message['updated_at'])

        logger.info("Container Reference Updates Received via Callback Successfully.")

        return {
            'statusCode': response_status,
            'body': response_message
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Get Container Reference Updates via Callback - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

@app.route("/unsubscribe-from-reference/<string:referenceId>", methods=["DELETE"])
def unsubscribe_from_reference(referenceId):
    try:
        response = requests.delete(VIZION_UNSUBSCRIBE_FROM_REFERENCE_API % referenceId, headers=headers)
        response_status = response.status_code
        response_message = response.text

        if response_message == "":
            response_message = {
                "httpMessage":"Deleted.",
                "httpStatusCode": response_status
            }
        else:
            response_message = json.loads(response_message)

        logger.info("Container Reference Deleted Successfully.")

        return {
            'statusCode': response_status,
            'body': response_message
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Unsubscribe Container Reference - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

@app.route("/list-all-active-references/", methods=["GET"])
def list_all_active_references():
    try:
        api_url = VIZION_LIST_ALL_ACTIVE_REFERENCES_API
        container_references_list = []
        nextToken = True
        while(nextToken == True):
            response = requests.get(api_url, headers=headers)
            response_status = response.status_code
            response_message = response.text

            if response_message == "":
                response_message = {
                    "httpMessage":"Received.",
                    "httpStatusCode": response_status
                }
            else:
                response_message = json.loads(response_message)
                container_references_list = container_references_list + response_message['data']
                if response_message['metadata']['page'] != response_message['metadata']['page_count']:
                    page_number = int(response_message['metadata']['page']) + 1
                    api_url = VIZION_LIST_ALL_ACTIVE_REFERENCES_API + "&page=" + str(page_number)
                else:
                    nextToken = False

        logger.info("Container References List Received Successfully.")

        return {
            'statusCode': response_status,
            'body': container_references_list
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Get the List of All Container References - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

@app.route("/list-all-available-carriers/", methods=["GET"])
def list_all_available_carriers():
    try:
        response = requests.get(VIZION_LIST_ALL_AVAILABLE_CARRIERS_API, headers=headers)
        response_status = response.status_code
        response_message = response.text

        if response_message == "":
            response_message = {
                "httpMessage":"Received.",
                "httpStatusCode": response_status
            }
        else:
            response_message = json.loads(response_message)

        logger.info("Supported Carriers List Received Successfully.")

        return {
            'statusCode': response_status,
            'body': response_message
        }
    except Exception as exp:
        exp = traceback.format_exc()
        error_statement = "ERROR: Failed to Get the List of All Supported Carriers - Reason: " + str(exp)
        logger.error(error_statement)
        post_message_on_slack(SLACK_ERROR_CHANNEL, ":heavy_exclamation_mark:" + error_statement)

        return {
            'statusCode': 500,
            'body': error_statement
        }

def lambda_handler(event, context):
    return main()

# For local testing
if __name__ == '__main__':
    app.run()
