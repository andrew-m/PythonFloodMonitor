import json
import os

import boto3

import river_config
import river_data
import render_image


def handler(event, context):
    bucket_name = os.environ["BUCKET_NAME"]
    key_prefix = os.environ.get("KEY_PREFIX", "")
    if key_prefix and not key_prefix.endswith("/"):
        key_prefix = f"{key_prefix}/"

    payload = river_data.build_river_level_document(river_config.STATIONS, threshold=200)

    json_key = f"{key_prefix}walking-skeleton/latest.json"
    png_key = f"{key_prefix}walking-skeleton/latest.png"
    bin_key = f"{key_prefix}walking-skeleton/latest.bin"

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=json_key,
        Body=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        ContentType="application/json",
    )

    png_bytes = render_image.render_latest_png(payload)
    s3.put_object(
        Bucket=bucket_name,
        Key=png_key,
        Body=png_bytes,
        ContentType="image/png",
    )

    bin_bytes = render_image.render_latest_mono_hlsb_black(payload)
    s3.put_object(
        Bucket=bucket_name,
        Key=bin_key,
        Body=bin_bytes,
        ContentType="application/octet-stream",
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "wrote": {
                    "bucket": bucket_name,
                    "json_key": json_key,
                    "png_key": png_key,
                    "bin_key": bin_key,
                },
                **payload,
            }
        ),
    }
