import json
import os

import boto3

import river_config
import river_data


def handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    key_prefix = os.environ.get("KEY_PREFIX", "")
    if key_prefix and not key_prefix.endswith("/"):
        key_prefix = f"{key_prefix}/"

    payload = river_data.build_river_level_document(river_config.STATIONS, threshold=200)

    key = f"{key_prefix}walking-skeleton/latest.json"

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
