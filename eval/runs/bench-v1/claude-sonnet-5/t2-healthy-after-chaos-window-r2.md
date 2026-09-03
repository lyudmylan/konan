---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-toggle-503s
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-19T01:46:23Z
  concluded: 2026-08-19T01:52:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was enabled (failure_rate=0.6, error_status=503) at 01:45:44.208Z, producing a probabilistic burst of 503s across /products, /products/1, /products/2 and POST /orders through 01:45:48.439Z, then disabled at 01:45:50.545Z; the earlier noise was this bounded, self-resolved fault-injection window."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled (failure_rate=0.6, error_status=503) at 01:45:44.208Z, producing a probabilistic burst of 503s across /products, /products/1, /products/2 and POST /orders through 01:45:48.439Z, then disabled at 01:45:50.545Z; this fully explains the 'noise earlier' and had already resolved before this handover check began."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
latent_findings:
  - statement: "Product id=4 ('Mystery Box') is served with price: null, the only product in the catalog with a null price. This is an unconfirmed data anomaly, not an observed failure: no order for product_id=4 appears anywhere in the available log, and testing whether placing one would crash an order-total computation requires a mutating POST /orders call, outside the investigator's read-only, GET-only probe surface."
    evidence: [E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:42.150Z"
    quote: "{\"ts\": \"2026-08-19T01:45:42.150Z\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.994}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:44.208Z"
    quote: "{\"ts\": \"2026-08-19T01:45:44.208Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:45.265Z-01:45:45.266Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} then {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.28}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:46.323Z-01:45:46.324Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/2\"} then {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 503, \"duration_ms\": 0.296}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:47.382Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} then {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.263}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:48.439Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"} then {\"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.299}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:49.486Z"
    quote: "{\"ts\": \"2026-08-19T01:45:49.486Z\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 0.758}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:50.545Z"
    quote: "{\"ts\": \"2026-08-19T01:45:50.545Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"event\": \"chaos_disabled\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:46:12.725Z"
    quote: "{\"ts\": \"2026-08-19T01:46:12.725Z\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 2, \"quantity\": 1, \"total_price\": 23.0} then \"POST /orders -> 201\""
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:45:40.339Z"
    quote: "{\"ts\": \"2026-08-19T01:45:40.339Z\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E11
    type: probe
    source: "GET /health, request_id konan-1787104007-37442, 2026-08-19T01:46:47Z"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":66.76876562507823} -- HTTP 200 in 0.001481s"
  - id: E12
    type: metric
    source: "GET /metrics, request_id konan-1787104011-37451, 2026-08-19T01:46:51Z"
    quote: "faultline_chaos_enabled 0; http_exceptions_total has no data rows (zero unhandled exceptions recorded)"
  - id: E13
    type: probe
    source: "GET /health, request_id konan-1787104304-37639, 2026-08-19T01:51:44Z (approx, uptime-derived)"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":364.516436957987} -- HTTP 200 in 0.001678s"
  - id: E14
    type: metric
    source: "GET /metrics, request_id konan-1787104309-37646, 2026-08-19T01:51:49Z (approx, uptime-derived)"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1; http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1; http_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1; http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1 (all unchanged since baseline — no new failures); faultline_chaos_enabled 0; process_uptime_seconds 368.944918083027 (monotonic, no restart)"
  - id: E15
    type: probe
    source: "GET /products, request_id konan-1787104170-37611, 2026-08-19T01:49:30Z (approx)"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0}"
  - id: E16
    type: log
    source: "grep -n '\"product_id\": 4' lab/logs/app.log (full file)"
    quote: "(no matches — product_id 4 never appears in any order_created or request line in the log)"
gaps:
  - "Could not determine who or what triggered POST /chaos/enable and POST /chaos/disable — the request log only carries client IP (127.0.0.1 for all traffic in this lab) and no auth/user-agent field, so actor attribution is inferred from the lab boundary (only eval-side scripts/scenario.sh can reach /chaos), not directly evidenced in the citations above."
  - "Could not test whether ordering product_id=4 ('Mystery Box', price=null) triggers a defect — POST /orders is a mutating call outside the investigator's read-only, GET-only probe surface (scripts/probe.sh). This remains an open, untested data anomaly (see latent_findings)."
  - "Log history covers only the current process's uptime (~369s at conclusion, single startup marker, no .1-.3 rotation backups present) — nothing before the 01:45:40.339Z startup is observable."
usage:
  model: claude-sonnet-5
  tokens: 3263802
  wall_clock_seconds: 391
---

# Shop service: transient chaos-toggle 503 burst, self-resolved before handover

## Summary

**Verdict: root-cause-identified.** The "noise earlier" referenced in the handover
complaint was a real, bounded incident: chaos mode was enabled at 01:45:44.208Z with a
60% injected-failure rate, producing four 503 responses across `/products`,
`/products/1`, `/products/2`, and `POST /orders` between 01:45:45.265Z and
01:45:48.439Z (E2-E6). It was disabled at 01:45:50.545Z (E8), and every request since —
through the most recent probe at process-uptime 368.9s — has returned 200/201 with zero
unhandled exceptions (E9, E11-E14). **Nothing is wrong with the shop service right now.**
A secondary, unrelated data anomaly was noticed in passing and is carried as a latent
finding, not part of this incident: product id=4 ("Mystery Box") is served with
`price: null` (E15), untested and never ordered (E16).

## Timeline (UTC, 2026-08-19)

- `01:45:40.339Z` — process start, single startup marker in the log (E10).
- `01:45:41Z-01:45:42Z` — clean baseline traffic (E1).
- `01:45:44.208Z` — **config-change marker**: chaos mode enabled, failure_rate=0.6,
  error_status=503 (E2).
- `01:45:45.265Z-01:45:48.439Z` — four chaos-injected 503s spread across four different
  routes, interleaved with one clean 200 (E3-E7) — consistent with a probabilistic
  toggle, not a hard outage or a single-route code defect.
- `01:45:50.545Z` — **config-change marker**: chaos mode disabled (E8).
- `01:46:10Z-01:46:14Z` — clean traffic resumes immediately and gaplessly, including a
  successful order (E9).
- `01:46:23Z` — this investigation begins (konan handover check).
- `01:46:47Z-01:46:51Z` — baseline probes: healthy, chaos off, zero exceptions (E11, E12).
- `01:51:44Z-01:51:49Z` — confirmation probes near conclusion: still healthy, 503
  counters unchanged since the original window (no new failures), chaos still off,
  process uptime climbing monotonically with no restart (E13, E14).

## Investigation

1. **Baseline**: `/health` and `/metrics` probed, plus the full `app.log` (30 lines at
   the time — the entire log, no rotation) read directly. The chaos-toggle episode and
   its clean resolution were both visible in this single read.
2. **Triage** (three lenses, parallel, each blind to the others): infra-process found no
   restart/memory/latency anomalies; interfaces independently reconstructed the same
   chaos-toggle timeline and confirmed current 404/200 contract behavior is well-formed;
   software-defect confirmed zero unhandled exceptions and flagged the `price: null`
   data point on product 4 as an unconfirmed, untriggered anomaly.
3. **Deep-dive**: skipped — both hypotheses (H1 and the latent finding) already had
   deterministic, complete evidence from triage; no gap needed filling by a targeted
   probe round.
4. **Judge** (adversarial, evidence-only): validated H1, noting two soft spots — actor
   attribution for the chaos toggle isn't itself evidenced (now recorded as a gap), and
   the "remains resolved" claim needed a probe closer to the present. Validated the
   latent finding's narrow, hedged claim (the data anomaly exists and is untested; the
   crash mechanism is speculative and out of scope for a read-only probe).
5. **Closing the judge's gap**: took one more `/health` + `/metrics` probe at
   process-uptime ~369s (E13, E14) — 503 counters unchanged, chaos still off — before
   concluding.

## Hypotheses

### H1 — Chaos-toggle 503 burst, self-resolved (validated)

Config-change markers bracket the failure window exactly: `chaos_enabled` (E2)
immediately precedes the first 503 (E3), `chaos_disabled` (E8) immediately precedes the
return to clean traffic (E9). The failure spread across four unrelated routes rather
than concentrating on one input or endpoint, and one request inside the window
succeeded (E7) — both signatures of a probabilistic, injected fault rather than a code
defect or a hard dependency outage. Confirmed still resolved at conclusion (E13, E14).

## Safe next steps

- If the operator identity behind the `/chaos/enable`/`disable` calls matters for the
  handover record, check whatever system issued them (eval harness run logs, CI job,
  etc.) — outside this investigation's read-only surface.
- Consider a source read (not a live test) of the order-total computation path to see
  how it handles a `null` price, given product 4 carries one — read-only code review,
  no order needs to be placed.
- No remediation needed for the chaos-toggle episode itself — it already self-resolved
  and traffic has been clean for the duration of this check.

## Gaps

- Actor attribution for the chaos toggle is inferred from the lab boundary, not
  evidenced directly — the request log has no auth/user-agent field.
- The `price: null` product-4 anomaly could not be tested (would require a mutating
  `POST /orders`, outside the read-only probe surface).
- Log visibility is bounded by the current process's uptime; nothing before
  `01:45:40.339Z` is observable.
