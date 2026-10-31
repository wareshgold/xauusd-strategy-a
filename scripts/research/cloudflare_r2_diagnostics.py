#!/usr/bin/env python3
"""Read-only connectivity and scope diagnostics for Cloudflare R2.

This script never creates buckets, uploads, downloads, deletes, or changes
bucket configuration. It verifies credentials against one configured bucket
and lists at most ten object names under the configured evidence prefix.
"""
from __future__ import annotations

import os
import re
import sys
from typing import Mapping
from urllib.parse import urlparse


DEFAULT_BUCKET = "sp2l-forward-evidence"
DEFAULT_PREFIX = "forward-test/"
REQUIRED_ENV = (
    "CF_R2_ACCOUNT_ID",
    "CF_R2_ACCESS_KEY_ID",
    "CF_R2_SECRET_ACCESS_KEY",
)


def validate_config(env: Mapping[str, str]) -> dict[str, str]:
    missing = [name for name in REQUIRED_ENV if not env.get(name, "").strip()]
    if missing:
        raise ValueError("Missing environment variable(s): " + ", ".join(missing))

    account_id = env["CF_R2_ACCOUNT_ID"].strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{10,64}", account_id):
        raise ValueError("CF_R2_ACCOUNT_ID has an unexpected format")

    bucket = env.get("CF_R2_BUCKET", DEFAULT_BUCKET).strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket):
        raise ValueError("CF_R2_BUCKET is not a valid DNS-style bucket name")

    prefix = env.get("CF_R2_PREFIX", DEFAULT_PREFIX).strip()
    if not prefix or prefix.startswith("/") or ".." in prefix.split("/"):
        raise ValueError("CF_R2_PREFIX must be a non-empty relative object prefix")
    if not prefix.endswith("/"):
        prefix += "/"

    endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Could not construct a valid R2 endpoint")

    return {
        "account_id": account_id,
        "bucket": bucket,
        "prefix": prefix,
        "access_key_id": env["CF_R2_ACCESS_KEY_ID"].strip(),
        "secret_access_key": env["CF_R2_SECRET_ACCESS_KEY"],
        "endpoint": endpoint,
    }


def main() -> int:
    print("SP2L CLOUDFLARE R2 READ-ONLY DIAGNOSTICS")
    print("Actions: authenticate, HEAD one bucket, list up to 10 names under one prefix")
    print("No bucket listing, upload, download, delete, or configuration mutation.")

    try:
        config = validate_config(os.environ)
    except ValueError as exc:
        print(f"CONFIGURATION=FAIL: {exc}")
        return 2

    print(f"BUCKET={config['bucket']}")
    print(f"PREFIX={config['prefix']}")
    print(f"ENDPOINT_HOST={urlparse(config['endpoint']).hostname}")

    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("DEPENDENCY=FAIL: boto3 is not installed")
        print("Install with: python -m pip install boto3")
        return 3

    try:
        client = boto3.client(
            "s3",
            endpoint_url=config["endpoint"],
            aws_access_key_id=config["access_key_id"],
            aws_secret_access_key=config["secret_access_key"],
            region_name="auto",
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

        print("[1/2] Checking bucket access...")
        client.head_bucket(Bucket=config["bucket"])
        print("BUCKET_ACCESS=PASS")

        print("[2/2] Listing names under the evidence prefix...")
        response = client.list_objects_v2(
            Bucket=config["bucket"],
            Prefix=config["prefix"],
            MaxKeys=10,
        )
        contents = response.get("Contents", [])
        print(f"LIST_PREFIX=PASS")
        print(f"OBJECT_COUNT_RETURNED={len(contents)}")
        for item in contents:
            # Names are useful for confirming the intended prefix. No object
            # contents, metadata, credentials, or tokens are printed.
            print(f"OBJECT_KEY={item.get('Key', '')}")
        print("DIAGNOSTIC_RESULT=PASS")
        return 0
    except Exception as exc:  # sanitized: never dump request headers or secrets
        response = getattr(exc, "response", {}) or {}
        error = response.get("Error", {}) if isinstance(response, dict) else {}
        code = error.get("Code", "UNKNOWN") if isinstance(error, dict) else "UNKNOWN"
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode", "UNKNOWN") if isinstance(response, dict) else "UNKNOWN"
        print(f"DIAGNOSTIC_RESULT=FAIL")
        print(f"ERROR_CODE={code}")
        print(f"HTTP_STATUS={status}")
        print("DETAILS=Sensitive exception text suppressed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
