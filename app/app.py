import os
import json
import boto3
from flask import Flask, jsonify, request
from botocore.config import Config

app = Flask(__name__)

# Connect to LocalStack instead of real AWS
LOCALSTACK_URL = os.environ.get("LOCALSTACK_URL", "http://localstack:4566")
boto_config = Config(region_name="us-east-1")


def get_s3():
    return boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=boto_config,
    )


def get_sqs():
    return boto3.client(
        "sqs",
        endpoint_url=LOCALSTACK_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=boto_config,
    )


def get_dynamodb():
    return boto3.resource(
        "dynamodb",
        endpoint_url=LOCALSTACK_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=boto_config,
    )


@app.route("/")
def health():
    return jsonify({"status": "ok", "message": "Flask app is running!"})


@app.route("/s3/upload", methods=["POST"])
def upload_to_s3():
    data = request.json
    s3 = get_s3()
    bucket = os.environ.get("S3_BUCKET", "app-bucket")
    key = data.get("key", "default.json")
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(data))
    return jsonify({"message": f"Uploaded '{key}' to S3 bucket '{bucket}'"})


@app.route("/s3/list", methods=["GET"])
def list_s3():
    s3 = get_s3()
    bucket = os.environ.get("S3_BUCKET", "app-bucket")
    response = s3.list_objects_v2(Bucket=bucket)
    files = [obj["Key"] for obj in response.get("Contents", [])]
    return jsonify({"bucket": bucket, "files": files})


@app.route("/sqs/send", methods=["POST"])
def send_to_sqs():
    data = request.json
    sqs = get_sqs()
    queue_url = os.environ.get("SQS_QUEUE_URL", "http://localstack:4566/000000000000/app-queue")
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(data))
    return jsonify({"message": "Message sent to SQS queue"})


@app.route("/sqs/receive", methods=["GET"])
def receive_from_sqs():
    sqs = get_sqs()
    queue_url = os.environ.get("SQS_QUEUE_URL", "http://localstack:4566/000000000000/app-queue")
    response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=5)
    messages = [m["Body"] for m in response.get("Messages", [])]
    return jsonify({"messages": messages})


@app.route("/dynamodb/put", methods=["POST"])
def put_item():
    data = request.json
    dynamodb = get_dynamodb()
    table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "app-table"))
    table.put_item(Item=data)
    return jsonify({"message": "Item saved to DynamoDB", "item": data})


@app.route("/dynamodb/get/<item_id>", methods=["GET"])
def get_item(item_id):
    dynamodb = get_dynamodb()
    table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "app-table"))
    response = table.get_item(Key={"id": item_id})
    item = response.get("Item", {})
    return jsonify({"item": item})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


@app.route("/health/detailed", methods=["GET"])
def detailed_health():
    checks = {}

    try:
        s3 = get_s3()
        s3.list_buckets()
        checks["s3"] = "ok"
    except Exception as e:
        checks["s3"] = str(e)

    try:
        dynamodb = get_dynamodb()
        list(dynamodb.tables.all())
        checks["dynamodb"] = "ok"
    except Exception as e:
        checks["dynamodb"] = str(e)

    all_ok = all(v == "ok" for v in checks.values())
    return jsonify({
        "status": "healthy" if all_ok else "degraded",
        "services": checks
    }), 200 if all_ok else 503
