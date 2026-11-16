---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-wide-latency
  trigger: "manual (/konan adapter; complaint object: source human, fingerprint human-1794747146, labels.alertname human-report, no severity stated, startsAt 2026-11-15T12:52:26Z; investigation start 2026-11-15T12:52:44Z — trigger latency 18s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-11-15T12:52:44Z"
  concluded: "2026-11-15T12:58:00Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The service's internal chaos switch was turned on at 12:52:09.653Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on, every observed shop request (/products, /products/{id}, /orders) takes between 120 ms and about 1.4 s instead of about 1 ms, with no error statuses, and /health stays fast; the switch was still on at 12:54:21Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the service (chaos mode) was turned on at 12:52:09.653Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on, it adds a delay of up to about 1500 ms to the shop routes (/products, /products/{id}, /orders) and returns no errors."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E18, E19, E20, E24]
    evidence_against: []
  - id: H2
    statement: "A defect in the service's own code makes requests slow for specific inputs or on a specific route."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E7, E9, E10, E11, E12, E16, E17]
  - id: H3
    statement: "Demand exceeds the capacity of the service, and requests queue."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14, E18, E20, E23]
  - id: H4
    statement: "The process start at 12:52:03.750Z (a cold start) is the cause of the slowness."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E21, E22]
    evidence_against: [E4, E5, E6, E15, E16, E17, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:09.653Z"
    quote: '{"ts": "2026-11-15T12:52:09.653Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "df3abc1811bc", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: metric
    source: "/metrics @ request_id=konan-1794747165-96179 (2026-11-15T12:52:45Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: metric
    source: "/metrics @ request_id=konan-1794747261-96271 (2026-11-15T12:54:21Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:04.494Z"
    quote: '{"ts": "2026-11-15T12:52:04.494Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "3c7530c956a3", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.122, "client": "127.0.0.1:51912"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:05.544Z"
    quote: '{"ts": "2026-11-15T12:52:05.544Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "936d92f8e357", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.009, "client": "127.0.0.1:51913"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:06.598Z"
    quote: '{"ts": "2026-11-15T12:52:06.598Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "c7a69fc0c303", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.938, "client": "127.0.0.1:51914"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:12.689Z"
    quote: '{"ts": "2026-11-15T12:52:12.689Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d42fd5a83014", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 979.86, "client": "127.0.0.1:51916"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:14.701Z"
    quote: '{"ts": "2026-11-15T12:52:14.701Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "9551a8d71e7b", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 949.13, "client": "127.0.0.1:51917"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:17.102Z"
    quote: '{"ts": "2026-11-15T12:52:17.102Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a97863098c3c", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1336.361, "client": "127.0.0.1:51918"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:18.822Z"
    quote: '{"ts": "2026-11-15T12:52:18.822Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1b02349a0f10", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 659.76, "client": "127.0.0.1:51920"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:20.034Z"
    quote: '{"ts": "2026-11-15T12:52:20.034Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "759c6d64aedc", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 147.026, "client": "127.0.0.1:51921"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:21.205Z"
    quote: '{"ts": "2026-11-15T12:52:21.205Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "35005e215ebd", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 120.316, "client": "127.0.0.1:51922"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:44.689Z"
    quote: '{"ts": "2026-11-15T12:52:44.689Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794747164-96174", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.492, "client": "127.0.0.1:51941"}'
  - id: E14
    type: probe
    source: "/health @ request_id=konan-1794747164-96174"
    quote: |-
      {"status":"ok","uptime_seconds":40.950168542098254}
      -- HTTP 200 in 0.001542s request_id=konan-1794747164-96174
  - id: E15
    type: probe
    source: "/products @ request_id=konan-1794747178-96192"
    quote: "-- HTTP 200 in 0.921632s request_id=konan-1794747178-96192"
  - id: E16
    type: probe
    source: "/orders @ request_id=konan-1794747179-96197"
    quote: "-- HTTP 200 in 1.381101s request_id=konan-1794747179-96197"
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:53:41.554Z"
    quote: '{"ts": "2026-11-15T12:53:41.554Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794747220-96246", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 983.896, "client": "127.0.0.1:51952"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:53:41.628Z"
    quote: '{"ts": "2026-11-15T12:53:41.628Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794747221-96257", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.53, "client": "127.0.0.1:51954"}'
  - id: E19
    type: metric
    source: "/metrics @ request_id=konan-1794747261-96271 (2026-11-15T12:54:21Z); the complete http_exceptions_total section, which has no series"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E20
    type: metric
    source: "/metrics @ request_id=konan-1794747261-96271 (2026-11-15T12:54:21Z); the complete http_requests_total section"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:52:03.750Z"
    quote: '{"ts": "2026-11-15T12:52:03.750Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E22
    type: metric
    source: "/metrics @ request_id=konan-1794747165-96179 (2026-11-15T12:52:45Z)"
    quote: |-
      process_uptime_seconds 41.49086112482473
      process_max_rss_bytes 48054272
  - id: E23
    type: metric
    source: "/metrics @ request_id=konan-1794747261-96271 (2026-11-15T12:54:21Z)"
    quote: |-
      process_uptime_seconds 137.30995933292434
      process_max_rss_bytes 48054272
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:53:00.430Z"
    quote: '{"ts": "2026-11-15T12:53:00.430Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794747179-96197", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1379.074, "client": "127.0.0.1:51946"}'
gaps:
  - "The visible history starts at the process start, 2026-11-15T12:52:03.749Z; the log has no backup files. The complaint says 'the last few minutes', and nothing before that start is on the surface."
  - "The known-good window is 3 shop requests in about 2 seconds (E4, E5, E6). GET /orders has no reading before the switch."
  - "The mechanism rests on timing and on the parameter extra_latency_ms; no log line ties the delay of a single request to the switch. The decisive test (a shop request with the gauge at 0) needs a change of the switch, which is outside the read-only surface."
  - "The first order write (12:52:06.598Z) also lies between the last fast and the first slow shop request. Timing alone does not separate it from the switch; the wide spread on one route (E7, E11) and the fast order write itself (E6) make it unlikely."
  - "The surface does not show who sent POST /chaos/enable (request id df3abc1811bc, client 127.0.0.1:51915), or why."
  - "Only product ids 1 and 2 were observed slow; the other ids were not probed."
  - "The switch state is proven up to 2026-11-15T12:54:21Z (E3) only."
  - "The lab has no measure of requests in flight or of processor use; the rejection of load saturation rests on the request count and on the fast /health."
usage:
  model: claude-fable-5-2
  tokens: 1324906
  wall_clock_seconds: 316
---

# Shop-wide latency from the chaos switch, with no errors

## Summary

**Root cause identified: an internal degradation switch (`infra-process`, `degradation-switch`).**
The service's chaos mode was turned on at 12:52:09.653Z with `extra_latency_ms` 1500
and `failure_rate` 0.0 (E1). From that moment every observed shop request
(`/products`, `/products/{id}`, `GET /orders`, `POST /orders`) took between 120 ms
and about 1.4 s (E7–E12, E15–E17, E24); before it, the same routes took 1.0 to 1.9 ms
(E4, E5, E6). No request failed: all statuses are 200 or 201 (E20) and there are no
exceptions (E19). `/health` is not affected and stays at about 0.5 ms (E13, E14, E18),
which is why the health checks are green. The switch was still on at 12:54:21Z (E3).

Impact on users: 6 of 6 non-investigator shop requests after the switch were slow
(E7–E12). Confidence: high for the correlation and the match of the switch parameters
with the symptom (latency, no errors, health exempt); the mechanism is inferred from
timing and parameters, not from a per-request marker (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 12:52:03.750 — the process starts (`startup` event, E21). It is the only start in the log.
- 12:52:04.494 to 12:52:06.598 — three shop requests take 1.0 to 1.9 ms (E4, E5, E6).
- **12:52:09.653 — `chaos_enabled`: `failure_rate` 0.0, `extra_latency_ms` 1500 (E1).** A switch-change marker.
- 12:52:12.689 — the first slow shop request: `GET /products`, 979.86 ms (E7).
- 12:52:14.701 to 12:52:21.205 — five more slow shop requests, 120 to 1336 ms, on all four shop routes (E8–E12).
- 12:52:26 — the complaint arrives.
- 12:52:44 — the investigation starts; `/health` answers in 0.5 ms (E13, E14); the gauge `faultline_chaos_enabled` reads 1 (E2).
- 12:52:58 to 12:53:00 — investigator probes: `/products` 0.92 s, `/orders` 1.38 s (E15, E16, E24).
- 12:53:41 — `/products/1` still takes 983.896 ms; `/health` takes 0.53 ms (E17, E18).
- 12:54:21 — the gauge still reads 1; the uptime is 137 s with no reset; no error series (E3, E19, E20, E23).

## Investigation

- **Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.
- **Baseline.** `/health` green and fast (E14). `/metrics`: all 2xx, no exceptions, the
  chaos gauge at 1 (E2), uptime 41 s (E22). Log: one startup, fast requests, a
  `chaos_enabled` warning, then slow requests. Business surface probed: `/products`
  and `/orders` slow (E15, E16).
- **Triage.** Three lenses in parallel: infra-process, interfaces, software-defect.
  All three pointed at the same marker (E1) and the same step in durations. The
  interfaces lens found no boundary component and classed the mechanism as
  `infra-process`. The software-defect lens found no anomaly in its domain.
- **Deep-dive.** Skipped: the triage evidence for H1 was already complete, and the
  one remaining test (a request with the switch off) is outside the read-only surface.
- **Judge.** One fresh judge, evidence only. H1 validated with limits on the wording
  (a delay of up to about 1500 ms, not 1500 ms; inputs observed, not every input;
  the switch state has a time limit). H2, H3, H4 invalidated. The limits are in the
  hypothesis statements and in Gaps.

## Hypotheses

### H1 — the chaos switch adds latency (validated)

The marker E1 states the switch and its parameters. The 3 shop requests before it took
1.0 to 1.9 ms (E4, E5, E6); the 9 after it took 120 ms to 1.38 s (E7–E12, E15–E17,
E24), with no exception to the pattern. The same input `/products/1` is on both sides:
1.009 ms (E5), then 1336.361 ms (E9) and 983.896 ms (E17). `failure_rate` 0.0 matches
the absence of error statuses (E20) and of exceptions (E19). `/health` stays fast
(E13, E14, E18). The gauge reads 1 at two readings (E2, E3). The delays vary widely and
all are below 1500 ms; that fits a random delay of up to the configured value.

### H2 — a code defect tied to an input or a route (invalidated)

A defect of this shape repeats for the same input and does not depend on time. Here
the same input was fast, then slow (E5 against E9 and E17), and the same route took
1.122 ms, 979.86 ms and 147.026 ms (E4, E7, E11). The slowness is on all four shop
routes (E10, E12, E16), not on one.

### H3 — load saturation (invalidated)

The service handled 21 requests in about 137 s (E20, E23), and the slow requests did
not overlap. `/health` took about 0.5 ms during the slow period (E13, E14, E18), so
nothing queued in front of the handlers.

### H4 — a cold start (invalidated)

The process was about 22 s old at the complaint (E21, E22). But the first shop requests, 0.7
to 2.8 s after the start, were fast (E4, E5, E6), and there is no trend toward faster:
requests at 55 to 98 s of uptime still took 0.9 to 1.4 s (E15, E16, E17). The uptime
rises without a reset (E23).

## Safe next steps

Read-only only:

- Read `faultline_chaos_enabled` again; a value of 0 followed by shop requests near
  1 ms settles the mechanism without further tests.
- Ask the operators who sent `POST /chaos/enable` at 12:52:09 (request id
  `df3abc1811bc`) and whether it was planned.
- Watch `http_request_duration_seconds_sum` / `_count` per shop route to see the
  average delay per request over time.
- Note for monitoring: `/health` is exempt from the delay, so a health check does not
  see this incident shape; a check on a shop route does.

## Gaps

- **History.** The log starts at the process start (12:52:03.749Z) and has no backups.
  The complaint says "the last few minutes"; the surface shows less than one minute
  before the complaint. An earlier process, if any, is not visible.
- **Thin known-good window.** Three shop requests in about 2 seconds; `GET /orders`
  has no reading before the switch.
- **Mechanism inferred.** No log line ties one request's delay to the switch. The
  decisive test needs the switch off, which is not a read-only action.
- **First order write.** It lies in the same gap as the switch. The spread on one
  route (E7, E11) and the fast write itself (E6) make it unlikely, not excluded.
- **Who and why.** The surface does not show the sender of `POST /chaos/enable`.
- **Inputs.** Only product ids 1 and 2 were observed slow.
- **Switch state.** Proven up to 12:54:21Z only.
- **Load.** No measure of requests in flight or of processor use exists on this surface.
