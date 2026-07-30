#!/bin/sh
# Eval-side scenario controls for the faultline lab. Deliberately NOT
# pre-approved in .claude/settings.json: triggering failures stays a conscious,
# prompted act. The investigator never runs this — its only tool is
# scripts/probe.sh (see AGENTS.md).
set -eu
BASE="${KONAN_LAB_BASE:-http://127.0.0.1:8000}"
usage="usage: scripts/scenario.sh chaos-on [rate] [status] [latency_ms] | chaos-off | chaos-status | sim <path> | order <product_id> [quantity]"
cmd="${1:?$usage}"
shift || true
case "$cmd" in
  chaos-on)
    rate="${1:-0.3}"; status="${2:-503}"; lat="${3:-0}"
    curl -sS -X POST "$BASE/chaos/enable" -H 'content-type: application/json' \
      -d "{\"failure_rate\": $rate, \"error_status\": $status, \"extra_latency_ms\": $lat}"
    echo ;;
  chaos-off)
    curl -sS -X POST "$BASE/chaos/disable"; echo ;;
  chaos-status)
    curl -sS "$BASE/chaos"; echo ;;
  sim)
    curl -sS --max-time "${KONAN_SIM_TIMEOUT:-15}" "$BASE/simulate/${1:?sim needs a path, e.g. 'status/500' or 'flaky?rate=0.8'}"; echo ;;
  order)
    curl -sS -X POST "$BASE/orders" -H 'content-type: application/json' \
      -d "{\"product_id\": ${1:?order needs a product_id}, \"quantity\": ${2:-1}}"; echo ;;
  *)
    echo "scenario.sh: unknown command '$cmd'" >&2; echo "$usage" >&2; exit 2 ;;
esac
