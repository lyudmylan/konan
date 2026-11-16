---
konan_journal: 2
investigation:
  id: 2026-11-15-routine-handover-check
  trigger: "manual — /konan human report; source human; fingerprint human-1794750799; alertname human-report; no severity stated; startsAt 2026-11-15T13:53:19Z; investigation start 2026-11-15T13:53:30Z (trigger latency 11 s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-15T13:53:30Z
  concluded: 2026-11-15T13:56:17Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses: []
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794750815-99253"
    quote: |-
      {"status":"ok","uptime_seconds":29.828037916217}
      -- HTTP 200 in 0.002097s request_id=konan-1794750815-99253
  - id: E2
    type: metric
    source: "/metrics, request_id=konan-1794750815-99258 (baseline)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E3
    type: metric
    source: "/metrics, request_id=konan-1794750815-99258 (baseline)"
    quote: |-
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
  - id: E4
    type: metric
    source: "/metrics, request_id=konan-1794750815-99258 (baseline)"
    quote: |-
      process_uptime_seconds 30.403071916196495
      process_max_rss_bytes 46907392
  - id: E5
    type: metric
    source: "/metrics, request_id=konan-1794750815-99258 (baseline)"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.002653791569173336
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 3
      http_request_duration_seconds_sum{method="POST",path="/orders"} 0.00305795855820179
      http_request_duration_seconds_count{method="POST",path="/orders"} 2
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:53:05.507Z"
    quote: '{"ts": "2026-11-15T13:53:05.507Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:53:06.226Z"
    quote: '{"ts": "2026-11-15T13:53:06.226Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "a4bc6a2a6b19", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 12.343, "client": "127.0.0.1:52555"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:53:11.471Z"
    quote: '{"ts": "2026-11-15T13:53:11.471Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "0825faadb603", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.29, "client": "127.0.0.1:52561"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:53:14.580Z"
    quote: '{"ts": "2026-11-15T13:53:14.580Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "1aac1bd56784", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.783, "client": "127.0.0.1:52563"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:54:17.101Z"
    quote: '{"ts": "2026-11-15T13:54:17.101Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794750857-99335", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.429, "client": "127.0.0.1:52594"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:54:17.687Z"
    quote: '{"ts": "2026-11-15T13:54:17.687Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "konan-1794750857-99345", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.549, "client": "127.0.0.1:52596"}'
  - id: E12
    type: metric
    source: "/metrics, request_id=konan-1794750894-99363 (closing)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E13
    type: metric
    source: "/metrics, request_id=konan-1794750894-99363 (closing)"
    quote: |-
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
  - id: E14
    type: metric
    source: "/metrics, request_id=konan-1794750894-99363 (closing)"
    quote: |-
      process_uptime_seconds 109.04085612483323
      process_max_rss_bytes 46923776
  - id: E15
    type: probe
    source: "/health, request_id=konan-1794750895-99368"
    quote: |-
      {"status":"ok","uptime_seconds":109.56181895779446}
      -- HTTP 200 in 0.001487s request_id=konan-1794750895-99368
  - id: E16
    type: probe
    source: "/products, request_id=konan-1794750901-99387"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001586s request_id=konan-1794750901-99387
gaps:
  - "The observable window is short: the process started at 2026-11-15T13:53:05Z, about 25 s before the investigation, and lab/logs holds app.log only (no rotated backups). Nothing before that start is visible, so an earlier process that died cannot be excluded."
  - "User traffic in the window is 9 requests over about 8 s, the last at 13:53:14.580Z. That is too little to show slow memory growth, latency drift, or a low-rate intermittent failure."
  - "No request in the window touched /products/3 or /products/4, and no order names product 3 or 4. The list shows these two records differ from the exercised ones (units_in_stock 0; price null). Their detail and order paths are unobserved; the investigator did not probe them because no telemetry showed a failure."
  - "POST /orders is outside the investigator's GET-only surface; the order path is known only from two user requests in the log."
  - "No hypothesis was formed, so no deep-dive and no judge ran; the verdict rests on the baseline, three triage lenses, and the closing reading."
usage:
  model: claude-fable-5-2
  tokens: 1157366
  wall_clock_seconds: 167
---

# Routine handover check: no active incident on the shop service

## Summary

**No active incident.** The service is healthy on every surface the lab contract
exposes, at the baseline (13:53:35Z) and at the closing reading (13:54:55Z). Health
answers `ok` in about 2 ms (E1, E15). Every request counter series is 200 or 201, at
both readings (E2, E12). The exception counter has no series and the chaos switch is
off, at both readings (E3, E13). The business surface works, not only health: users
listed products, read product details, and created orders with success (E8, E9), and
investigator probes of `/orders`, `/products`, and `/products/5` returned 200 (E10,
E11, E16). All user counters are unchanged between the two readings; the growth is
investigator probes only (E2, E12).

Confidence: high for "nothing is failing now"; limited for anything that needs a long
window. The process is about 2 minutes old (E6, E14) and saw 9 user requests. Two
product records (ids 3 and 4) carry edge values and saw no traffic (E16) — a coverage
gap, not a finding.

## Timeline

- 13:53:05.507Z — `startup` event, faultline 0.1.0 (E6). The only lifecycle or change
  marker in the log. No chaos, configuration, or deploy marker follows it.
- 13:53:06.226Z — first user request, `GET /health` 200 in 12.343 ms (E7); a one-time
  cold-start duration, later requests take about 1 ms.
- 13:53:11.471Z — `POST /orders` 201 (E8); the second of two successful orders.
- 13:53:14.580Z — last user request in the window, `GET /products/5` 200 (E9).
- 13:53:19Z — complaint raised (`startsAt`).
- 13:53:30Z — investigation start.
- 13:53:35Z — baseline: health ok (E1); 2xx-only counters (E2); no exceptions, chaos
  off (E3); uptime 30.4 s, peak RSS 46907392 (E4).
- 13:54:02Z–13:54:22Z — triage lens probes; all 200 (E10, E11).
- 13:54:54Z — closing reading: 2xx-only counters (E12); no exceptions, chaos off
  (E13); uptime 109.0 s, peak RSS 46923776 (E14); health ok (E15).

## Investigation

Complaint block (the complaint object, verbatim, plus the investigation start):

```json
{
  "source": "human",
  "fingerprint": "human-1794750799",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-15T13:53:19Z"
}
```

Investigation start: 2026-11-15T13:53:30Z. Trigger latency: 11 s.

**Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.

**Baseline.** One `/health` probe (E1), one `/metrics` probe (E2–E5), and the full
`lab/logs/app.log` (18 lines at that time). The log held one startup (E6), then 9 user
access lines from 13:53:06.226Z to 13:53:14.580Z, all 200 or 201 (E7–E9), and two
`order_created` lines. No line above INFO level, no `unhandled_exception`, no chaos
event. Mean durations are about 0.9 ms for product details and 1.5 ms for orders (E5).

**Triage.** The complaint is vague, so all three lenses ran in parallel, each blind to
the others: software-defect, infra-process, interfaces.

- Software-defect: no anomaly. No exception series, no 5xx, no route with mixed
  outcomes. It named the unexercised product ids 3 and 4 as a coverage gap.
- Infra-process: no anomaly. One startup, no uptime reset between readings, peak RSS
  flat, chaos switch off, no slow route.
- Interfaces: no anomaly. No gateway-shaped status, no change marker after startup;
  its probes of `/products`, `/orders`, `/products/5` returned 200 (E10, E11), and the
  `/orders` content agreed with the `order_created` log lines.

**Closing reading.** `/metrics` (E12–E14) and `/health` (E15) about 80 s after the
baseline. User counters are identical to the baseline: `POST /orders` 201 stays 2, and
the growth on the GET routes equals the investigator probes in the log (E2, E12). The
uptime rose from 30.4 s to 109.0 s with no reset (E4, E14). Peak RSS rose 16384 bytes
(E4, E14). A whole-file check of the log (29 lines) found 0 lines above INFO level and
9 access lines without the investigator stamp.

**Deep-dive and judge.** Not run. No lens found an anomaly and the baseline difference
is clean, so no hypothesis exists to test; the loop ends at triage by its own rule.

## Hypotheses

None. No lens reported an anomaly, so no cause statement was formed or tested. The
hypothesis list in the machine core is empty by intent.

## Safe next steps

- Read `/metrics` again after real traffic resumes; compare the request counters and
  `http_exceptions_total` with the closing reading (E12, E13).
- Watch `process_max_rss_bytes` and `process_uptime_seconds` over a longer window
  (E14) to cover memory growth and restarts, which a 2-minute window cannot show.
- When user traffic reaches product ids 3 and 4, read the access lines for those
  requests in `lab/logs/app.log`. A read-only probe of `/products/3` and `/products/4`
  is within the allowlist; such a probe is investigator traffic and a failure it
  triggers would be a latent finding, not user impact.

## Gaps

- **Short window.** The process started at 13:53:05Z (E6) and only `app.log` exists.
  The surface shows nothing before that start; whether this start replaced an earlier
  process that died is unknown.
- **Little traffic.** 9 user requests over about 8 s (E7–E9). Slow memory growth,
  latency drift, and low-rate intermittent failures are out of reach of this sample.
- **Unexercised records.** Product 3 has `units_in_stock` 0 and product 4 has `price`
  null (E16). No user request touched their detail routes or ordered them. The
  investigator did not probe them: no telemetry pointed at a failure, and the loop
  ends at a clean triage.
- **Order path.** `POST /orders` is outside the GET-only probe surface; the evidence
  for it is two user requests (E8, E2).
- **No judge.** With no hypothesis, the adversarial judge had nothing to rule on.
