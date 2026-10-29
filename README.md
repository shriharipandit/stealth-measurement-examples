# Stealth public measurement examples

Read the public network observations behind Stealth's [Super Intelligence](https://stealth.net/super-intelligence) and [Business Platforms](https://stealth.net/business-platforms) pages. These examples fetch existing snapshots; they do not trigger measurements or choose targets.

- [Developer guide and interpretation](https://stealth.net/developers/measurements)
- [OpenAPI reference](https://stealth.net/api/measurements/openapi.json)
- [AI measurements schema](https://stealth.net/api/measurements/schemas/ai-latency.json)
- [Business platforms schema](https://stealth.net/api/measurements/schemas/business-platforms.json)

The feeds are public and require no API key. This repository contains client examples and documentation; it does not contain the private monitoring system or website implementation.

## Quick start

Python 3.9 or later is required; no extra packages are needed.

```sh
python3 examples/snapshot.py ai
python3 examples/snapshot.py business
python3 examples/business_icmp.py
python3 examples/super_intelligence.py
```

The first two commands each fetch a single snapshot and report its state, timestamps and number of configured endpoints. The count is not a count of healthy services. HTTP 503 can carry an unavailable snapshot, which is reported with a nonzero exit status.

The third command shows each business platform's ICMP label and latency only when sufficient fresh evidence exists. It checks timestamps against the client clock; keep that clock accurate. `None` means unavailable, not zero. This follows the [published guide](https://stealth.net/developers/measurements).

The fourth command reports Super Intelligence ICMP and TCP states and current ICMP latency when fresh. Latencies are already baseline-adjusted; negative and zero values are valid. It does not report a TCP duration. Stale or insufficient evidence is labeled unconfirmed.

Retrieve the snapshots directly with `curl` if preferred:

```sh
curl --fail --max-time 15 https://stealth.net/api/ai-latency
curl --fail --max-time 15 https://stealth.net/api/business-platforms
```

## Interpret the results

- Poll **each feed no more than once per minute**; after a failure wait at least a minute and back off. Do not attach query parameters.
- Check `schema_version`, snapshot state, individual probe states and timestamps. HTTP 200 can contain stale or empty data and does not prove current reachability.
- Preserve `null` as unknown or unavailable. A numeric zero is a real measurement, not a substitute for missing data.
- AI latency values are already adjusted by the returned baseline; do not subtract it again. Business latency values are raw milliseconds. Stale history is handled differently in each feed.
- ICMP, TCP and TLS are separate network observations. ICMP failure alone does not establish an outage; TCP or TLS reachability does not verify application functionality.
- Read fields by name and allow additional fields. Do not assume a fixed endpoint list, order or count. Keep source and observation timestamps when displaying results.

See the [developer guide](https://stealth.net/developers/measurements) for timestamp meanings, collection windows, protocol states and schema details. Measurements are observations from Stealth NYC, not service-level commitments.

## License

Example code and documentation are available under the [MIT License](LICENSE).
