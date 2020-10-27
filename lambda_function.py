import json
from botocore.vendored import requests

def lambda_handler(event, context):
    r = requests.get("https://httpbin.org/get?key=10")
    return {
        'statusCode': 200,
        'key': r.status_code,
        'body': json.dumps(f"There are {len(urls)} found")
}
