#!/usr/bin/env python3
"""Display current public AI endpoint observations from Stealth NYC."""
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

URL = "https://stealth.net/api/ai-latency"


def fresh(value, now):
    return type(value) in (int, float) and now - 120 <= value <= now + 5


def summarize(data, now):
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported measurement schema version")
    if not isinstance(data.get("endpoints"), list):
        raise ValueError("Snapshot is missing its endpoints list")
    snapshot_fresh = (data.get("state") in {"live", "empty"}
                      and all(fresh(data.get(key), now) for key in ("generated_at", "server_time")))
    for endpoint in data["endpoints"]:
        output = {"provider": endpoint.get("provider"), "instance": endpoint.get("instance")}
        for protocol in ("icmp", "tcp"):
            probe = endpoint["probes"][protocol]
            state = probe["state"]
            if not snapshot_fresh or not all(fresh(probe.get(key), now) for key in ("success_at", "up_at")):
                state = "unconfirmed"
            output[protocol + "_state"] = state
        latency = endpoint.get("latest_ms")
        output["icmp_latency_ms"] = (latency if output["icmp_state"] == "up"
                                     and not endpoint.get("latest_stale", True)
                                     and fresh(endpoint.get("recorded_at"), now)
                                     and type(latency) in (int, float) else None)
        yield output


def main():
    try:
        response = urlopen(URL, timeout=15)
    except HTTPError as error:
        if error.code != 503:
            raise
        response = error  # A 503 still contains an unavailable snapshot.
    with response:
        status = response.status
        data = json.load(response)
    result = {"source": URL, "http_status": status, "snapshot_state": data.get("state"),
              "generated_at": data.get("generated_at"), "baseline_ms": data.get("baseline_ms"),
              "endpoints": list(summarize(data, time.time()))}
    print(json.dumps(result, indent=2))
    return 0 if status == 200 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        print("Measurement request failed: " + str(exc), file=sys.stderr)
        sys.exit(1)
