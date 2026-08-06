#!/bin/sh
# Eval-side alert emitter — the lab profile's stand-in for a webhook (docs/triggers.md).
# Appends one contract-shaped complaint line to alerts/inbox.jsonl.
# Deliberately eval-side: the detector role is played by the operator/scenario, never
# by the investigator.
#
# Usage: scripts/alert.sh "<summary text>" [alertname] [severity]
set -eu
[ $# -ge 1 ] || { echo "usage: $0 \"<summary>\" [alertname] [severity]" >&2; exit 2; }
dir="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$dir/alerts"
SUMMARY="$1" ALERTNAME="${2:-lab-alert}" SEVERITY="${3:-}" /usr/bin/python3 - >> "$dir/alerts/inbox.jsonl" <<'PY'
import json, os, time
labels = {"alertname": os.environ["ALERTNAME"]}
if os.environ.get("SEVERITY"):
    labels["severity"] = os.environ["SEVERITY"]
print(json.dumps({
    "source": "alert",
    "fingerprint": "lab-%d" % time.time(),
    "labels": labels,
    "annotations": {"summary": os.environ["SUMMARY"]},
    "startsAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}))
PY
echo "alert emitted -> alerts/inbox.jsonl" >&2
