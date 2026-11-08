#!/bin/sh
# konan's only hands on a target: read-only GET against the lab base URL.
# The mechanical boundary is: GET only, path allowlist, timeout. /simulate and
# /chaos are excluded on purpose — faultline serves mutating GETs there
# (crash, hang, memory ballast), and chaos state is operator surface.
# The allowlist below IS faultline's surface contract (docs/lab.md); a different
# target replaces this adapter (allowlist + runner + scenario controls), not konan.
set -eu
BASE="${KONAN_LAB_BASE:-http://127.0.0.1:8000}"
raw="${1:?usage: scripts/probe.sh /path[?query]}"
path="${raw%%\?*}"
case "$path" in
  *..*|*%*|*//*)
    echo "probe.sh: refusing path with traversal or encoding tricks: '$path'" >&2
    exit 2 ;;
esac
case "$path" in
  /health|/metrics|/openapi.json|/products|/products/*|/orders|/orders/*) ;;
  *) echo "probe.sh: '$path' is outside the read-only allowlist" >&2; exit 2 ;;
esac
rid="konan-$(date +%s)-$$"
curl -sS --max-time "${KONAN_PROBE_TIMEOUT:-10}" \
  -H "X-Request-ID: $rid" \
  -w "\n-- HTTP %{http_code} in %{time_total}s request_id=$rid\n" \
  "$BASE$raw"
