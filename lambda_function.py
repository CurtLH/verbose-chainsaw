import json
import requests


def lambda_handler(event, context):
    r = requests.get("https://httpbin.org/get?key=10")
    return {
        "statusCode": 200,
        "version": requests.__version__,
        "key": r.status_code,
        "body": json.dumps(r.json()),
    }
