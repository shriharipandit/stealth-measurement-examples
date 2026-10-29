#!/usr/bin/env python3
"""Fetch and summarize one public measurement snapshot."""
import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

FEEDS = {"ai": "https://stealth.net/api/ai-latency",
         "business": "https://stealth.net/api/business-platforms"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feed", choices=FEEDS)
    args = parser.parse_args()
    try:
        response = urlopen(FEEDS[args.feed], timeout=15)
    except HTTPError as error:
        if error.code != 503:
            raise
        response = error
    with response:
        status = response.status
        data = json.load(response)
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported measurement schema version")
    if not isinstance(data.get("endpoints"), list):
        raise ValueError("Snapshot is missing the endpoints list")
    print(json.dumps({"source": FEEDS[args.feed], "http_status": status,
                      "schema_version": data["schema_version"], "state": data.get("state"),
                      "generated_at": data.get("generated_at"), "server_time": data.get("server_time"),
                      "source_snapshot_at": data.get("source_snapshot_at"),
                      "endpoint_count": len(data["endpoints"])}, indent=2))
    return 0 if status == 200 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (URLError, TimeoutError, ValueError) as exc:
        print("Snapshot request failed: " + str(exc), file=sys.stderr)
        sys.exit(1)
