import json
import os
from datetime import datetime, timezone

import boto3


def handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    key_prefix = os.environ.get("KEY_PREFIX", "")
    if key_prefix and not key_prefix.endswith("/"):
        key_prefix = f"{key_prefix}/"

    now = datetime.now(timezone.utc)
    payload = {
        "message": "hello world",
        "utc_time": now.isoformat(),
    }

    key = f"{key_prefix}walking-skeleton/{now.strftime('%Y%m%dT%H%M%SZ')}.json"

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        ContentType="application/json",
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "wrote": {
                    "bucket": bucket_name,
                    "key": key,
                },
                **payload,
            }
        ),
    }
