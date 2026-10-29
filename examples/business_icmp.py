import json
import time
from urllib.error import HTTPError
from urllib.request import urlopen

url = "https://stealth.net/api/business-platforms"
try:
    response = urlopen(url, timeout=15)
except HTTPError as error:
    if error.code != 503:
        raise
    response = error  # 503 still contains a snapshot.
with response:
    data = json.load(response)
if data.get("schema_version") != 1:
    raise ValueError("Unsupported measurement schema")
if data.get("state") not in {"live", "empty"}:
    raise RuntimeError("Current measurements unavailable")
now = time.time()  # Keep the client clock accurate.
fresh = lambda stamp: type(stamp) in (int, float) and now - 120 <= stamp <= now + 5
if not all(fresh(data.get(key)) for key in ("server_time", "generated_at", "source_snapshot_at")):
    raise RuntimeError("Snapshot is old or client/server clocks differ")
for endpoint in data["endpoints"]:
    status = endpoint["probes"]["icmp"]
    metric = endpoint["metrics"]["icmp"]
    stamps = (metric["recorded_at"], status["success_at"], status["up_at"])
    current = metric["current_ms"] if status["state"] == "up" and all(map(fresh, stamps)) else None
    label = status["label"]
    if status["state"] in {"up", "down"} and not all(map(fresh, stamps[1:])):
        label = "Unconfirmed"
    print(endpoint["instance"], label, current)
# Request each feed at most once per minute. None means unavailable.
