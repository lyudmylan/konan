---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-intermittent-503s
  trigger: "manual (/konan, profile human). Complaint object: {source: human, fingerprint: human-1787159011, labels: {alertname: human-report}, annotations.summary: verbatim below, startsAt: 2026-08-19T17:03:31Z}. Investigation start 2026-08-19T17:03:50Z; trigger latency 19s."
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-19T17:03:50Z
  concluded: 2026-08-19T17:05:40Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "At 2026-08-19T17:03:10Z a runtime configuration change enabled chaos mode (failure_rate 0.4, error_status 503), which injects 503 'service temporarily degraded' responses on a random ~40% of business requests (products, orders) while leaving /health untouched."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled at 17:03:10Z with failure_rate 0.4 / error_status 503 and injects probabilistic 503s on business routes; /health is exempt, so the health dashboard stays green."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E16]
    evidence_against: []
  - id: H2
    statement: "A per-input software defect makes specific product or order inputs fail deterministically."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11, E12, E13, E15]
  - id: H3
    statement: "Process crashes/restarts or resource saturation cause the intermittent errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:10.244Z"
    quote: "{\"ts\": \"2026-08-19T17:03:10.244Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"54cd0d427da2\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:10.245Z"
    quote: "{\"ts\": \"2026-08-19T17:03:10.245Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /chaos/enable -> 200\", \"request_id\": \"54cd0d427da2\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 1.981, \"client\": \"127.0.0.1:63231\"}"
  - id: E3
    type: metric
    source: "/metrics request_id=konan-1787159038-66620"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:12.313Z"
    quote: "{\"ts\": \"2026-08-19T17:03:12.313Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"09208e99cd5f\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:15.523Z"
    quote: "{\"ts\": \"2026-08-19T17:03:15.523Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"04c3d039fc26\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:15.524Z"
    quote: "{\"ts\": \"2026-08-19T17:03:15.524Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 503\", \"request_id\": \"04c3d039fc26\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.507, \"client\": \"127.0.0.1:63236\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:05.102Z (before the chaos marker)"
    quote: "{\"ts\": \"2026-08-19T17:03:05.102Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"f5b07ec27b39\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.776, \"client\": \"127.0.0.1:63228\"}"
  - id: E8
    type: metric
    source: "/metrics request_id=konan-1787159038-66620 (user traffic only; no konan-* probes had hit these paths yet)"
    quote: "http_requests_total{method=\"GET\",path=\"/orders\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/5\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 5\nhttp_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 2"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:13.381Z and 2026-08-19T17:03:19.801Z (same path, different outcome)"
    quote: "{\"ts\": \"2026-08-19T17:03:13.381Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"c9b1eded3fc3\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.908, \"client\": \"127.0.0.1:63234\"}\n{\"ts\": \"2026-08-19T17:03:19.801Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 503\", \"request_id\": \"713154ae3a9d\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.279, \"client\": \"127.0.0.1:63241\"}"
  - id: E10
    type: probe
    source: "/products/5 request_id=konan-1787159073-66668"
    quote: "{\"error\":\"service temporarily degraded\",\"request_id\":\"konan-1787159073-66668\"}\n-- HTTP 503 in 0.000948s request_id=konan-1787159073-66668"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:04:36.539Z (my retry probe konan-1787159076-66674, also 503)"
    quote: "{\"ts\": \"2026-08-19T17:04:36.539Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"konan-1787159076-66674\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/5\"}"
  - id: E12
    type: probe
    source: "/products/5 request_id=konan-1787159078-66681 (second retry of the same input)"
    quote: "{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500,\"units_ordered\":0,\"turnover_score\":0.0}\n-- HTTP 200 in 0.001490s request_id=konan-1787159078-66681"
  - id: E13
    type: metric
    source: "/metrics request_id=konan-1787159038-66620"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n# HELP faultline_chaos_enabled Whether chaos mode is active.\nhttp_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3"
  - id: E14
    type: metric
    source: "/metrics request_id=konan-1787159038-66620"
    quote: "process_uptime_seconds 56.51633466593921\nprocess_max_rss_bytes 47792128\nhttp_request_duration_seconds_sum{method=\"POST\",path=\"/orders\"} 0.002580665983259678\nhttp_request_duration_seconds_count{method=\"POST\",path=\"/orders\"} 3"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:03:01.995Z (the only startup marker in the 32-line log; no unhandled_exception or stack lines anywhere)"
    quote: "{\"ts\": \"2026-08-19T17:03:01.995Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E16
    type: probe
    source: "/health request_id=konan-1787159033-66612 and request_id=konan-1787159081-66687"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":51.383722708094865}\n-- HTTP 200 in 0.003046s request_id=konan-1787159033-66612\n{\"status\":\"ok\",\"uptime_seconds\":100.02768229111098}\n-- HTTP 200 in 0.001348s request_id=konan-1787159081-66687"
gaps:
  - "Triage lenses were not spawned as subagents: the full log (32 lines) and full metrics were read directly in the baseline, and the chaos_enabled marker plus chaos_failure-tagged 503s made the evidence deterministic; the three lens domains were instead covered as H1/H2/H3 and judged. A lens-parallel sweep could still have surfaced a secondary finding I did not look for."
  - "Who or what issued POST /chaos/enable (client 127.0.0.1:63231) is outside the investigator's surface; the change-actor is unknown."
  - "Observed user-traffic failure fraction (6 of 10 requests after the marker) is a small sample; the ~40% rate is taken from the configured failure_rate in E1, not measured independently."
usage:
  model: claude-fable-5
  tokens: 1515260
  wall_clock_seconds: 110
---

# Shop intermittent 503s — chaos mode enabled at 17:03:10Z

## Summary

**Verdict: root cause identified.** At `2026-08-19T17:03:10.244Z` a runtime configuration
change enabled faultline's chaos mode with `failure_rate 0.4, error_status 503` (E1, E2;
gauge `faultline_chaos_enabled 1`, E3). Since then a random ~40% of business requests —
`GET /products`, `GET /products/{id}`, `GET /orders`, `POST /orders` — are answered
`503 {"error":"service temporarily degraded"}` and each is tagged with a `chaos_failure`
log line (E4–E6, E8, E10, E11). The same input fails and then succeeds on retry (E9,
E10→E12), which is exactly the "works again on retry" the users describe. `/health` is
exempt from the injection and always returns 200 (E13, E16), which is why the health
dashboard is green. Impact: all user traffic before the marker was 200/201 (E7); after it,
6 of 10 user requests got 503. No exceptions, no restarts, no latency change (E13–E15).
Confidence: high — every prediction of H1 was confirmed by probing; H2 and H3 were
refuted. Class: `interfaces` (runtime configuration change).

## Timeline

- `17:03:01.995Z` — process start, the only startup marker (E15).
- `17:03:02Z–17:03:07Z` — user traffic all 200/201, including `POST /orders -> 201` (E7).
- `17:03:10.244Z` — **config change marker**: `chaos mode enabled`, `failure_rate 0.4`,
  `error_status 503` via `POST /chaos/enable` from `127.0.0.1:63231` (E1, E2).
- `17:03:12Z–17:03:21Z` — 6 of 10 user requests return 503, each with a `chaos_failure`
  line; `/products/1` is 200 at 17:03:13 and 503 at 17:03:19 (E4–E6, E8, E9).
- `17:03:31Z` — complaint raised (`startsAt`); `17:03:50Z` — investigation start.
- `17:03:53Z–17:03:58Z` — baseline: `/health` 200, `faultline_chaos_enabled 1` (E3, E16).
- `17:04:33Z–17:04:38Z` — my probes to `/products/5`: 503, 503, then 200 (E10–E12).
- `17:04:41Z` — `/health` still 200, uptime 100s, no reset (E16).

## Investigation

Baseline: `/health` 200 (E16), `/metrics` snapshot (E3, E8, E13, E14), full `app.log`
(32 lines, E1–E9, E15). The baseline already contained the config-change marker and the
tagged failures, so no lens subagents were spawned (recorded under Gaps); the three lens
domains became H1 (interfaces), H2 (software-defect), H3 (infra-process). Deep-dive was
done inline with targeted probes: `/products/1`, `/products/2`, `/products`, `/orders`
(all 200), `/products/5` ×3 (503, 503, 200 — E10–E12), `/health` (200, E16). One fresh
judge subagent saw only the hypotheses and verbatim evidence: H1 validated, H2
invalidated, H3 invalidated; no inconclusive verdicts, so one round sufficed.

## Hypotheses

### H1 — chaos mode enabled (interfaces) — validated
For: E1/E2 the marker and its access line; E3 the gauge; E4–E6 `chaos_failure`-tagged
503s on `/products` and `/orders`; E7 vs E8 the before/after split; E9, E10–E12 same
input fails then succeeds; E13/E16 `/health` untouched and no exceptions. Against: none.
Judge caveat: the observed 6/10 fraction is a small sample; the 40% figure comes from E1.

### H2 — per-input software defect — invalidated
Against: E9 and E10–E12 show identical inputs returning 503 then 200; E13/E15 show no
exception counters, no `unhandled_exception` or `stack` lines. A deterministic per-input
defect would not behave this way.

### H3 — process restart or saturation — invalidated
Against: E15 one startup marker only; E14/E16 monotonic uptime 51s→56s→100s, RSS ~47 MB,
sub-2 ms durations; the 503s carry an explicit `chaos_failure` tag.

## Safe next steps

- Confirm with the operator who/what issued `POST /chaos/enable` at 17:03:10Z from
  `127.0.0.1:63231` (E2) — the change-actor is outside the investigator's surface.
- Watch `faultline_chaos_enabled` and the `http_requests_total{status="503"}` series;
  a `chaos_disabled` log event is the signal that the condition has cleared.
- Count only non-`konan-*` request ids when quantifying user impact; my three
  `/products/5` probes added two 503s to the counters (E10, E11).

## Gaps

- No lens subagents were spawned; all three domains were covered as judged hypotheses
  against the complete telemetry, but a lens sweep might have flagged a secondary issue.
- The identity of the change-actor behind `POST /chaos/enable` is not observable here.
- The ~40% failure fraction is the configured rate (E1), not an independent measurement;
  the user-traffic sample after the marker is only 10 requests.
