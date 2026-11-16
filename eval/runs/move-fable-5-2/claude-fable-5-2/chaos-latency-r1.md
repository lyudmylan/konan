---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-wide-slowness
  trigger: 'manual — /konan adapter (human profile). Complaint object: {"source": "human", "fingerprint": "human-1794746384", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."}, "startsAt": "2026-11-15T12:39:44Z"}. Investigation start: 2026-11-15T12:39:55Z (trigger latency 11 s).'
  complaint: 'Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast.'
  started: 2026-11-15T12:39:55Z
  concluded: 2026-11-15T12:44:48Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'The chaos switch inside the target was turned on at 12:39:26.668Z with failure_rate 0.0 and extra_latency_ms 1500; while it is on, every business route answers 2xx with an added delay of up to about 1.25 s observed, and /health stays under 1 ms.'
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: 'An operational switch inside the target (chaos mode) was turned on at 12:39:26.668Z with failure_rate 0.0 and extra_latency_ms 1500; while on, it adds a per-request delay to the business routes, injects no errors, and does not delay /health.'
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E18]
    evidence_against: []
  - id: H2
    statement: 'A crash, a restart loop, or a hang of the process causes the slowness.'
    incident_class: infra-process
    state: invalidated
    evidence_for: [E14]
    evidence_against: [E3, E4, E12, E15, E16]
  - id: H3
    statement: 'Demand exceeds the capacity of the process (CPU, memory, or workers), so requests queue.'
    incident_class: load-saturation
    state: invalidated
    evidence_for: [E5]
    evidence_against: [E10, E12, E13, E15, E16, E17]
  - id: H4
    statement: 'A defect in the code of the target makes the business routes slow for some input.'
    incident_class: software-defect
    state: invalidated
    evidence_for: [E5]
    evidence_against: [E3, E5, E8, E10, E13]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:26.668Z'
    quote: '{"ts": "2026-11-15T12:39:26.668Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "14d8d99694a0", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: metric
    source: '/metrics, request_id konan-1794746483-95556 (12:41:23Z); the same value in the scrape konan-1794746400-95485 (12:40:00Z)'
    quote: 'faultline_chaos_enabled 1'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:21.495Z'
    quote: '{"ts": "2026-11-15T12:39:21.495Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d26301b82905", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.235, "client": "127.0.0.1:51776"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:23.609Z'
    quote: '{"ts": "2026-11-15T12:39:23.609Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "c7743ceeb4dc", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.903, "client": "127.0.0.1:51779"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:29.312Z'
    quote: '{"ts": "2026-11-15T12:39:29.312Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "c5a41b6eedd6", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 586.459, "client": "127.0.0.1:51781"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:31.489Z'
    quote: '{"ts": "2026-11-15T12:39:31.489Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "a19e3c9cd2bd", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1114.394, "client": "127.0.0.1:51782"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:35.493Z'
    quote: '{"ts": "2026-11-15T12:39:35.493Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "05d0164c263c", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1173.228, "client": "127.0.0.1:51784"}'
  - id: E8
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:37.389Z'
    quote: '{"ts": "2026-11-15T12:39:37.389Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d63e1a0be691", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 832.038, "client": "127.0.0.1:51785"}'
  - id: E9
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:38.690Z'
    quote: '{"ts": "2026-11-15T12:39:38.690Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "c8370aaa0822", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 237.563, "client": "127.0.0.1:51787"}'
  - id: E10
    type: probe
    source: '/products, request_id konan-1794746414-95502'
    quote: '-- HTTP 200 in 1.256895s request_id=konan-1794746414-95502'
  - id: E11
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:41:02.761Z'
    quote: '{"ts": "2026-11-15T12:41:02.761Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794746462-95541", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 172.635, "client": "127.0.0.1:51813"}'
  - id: E12
    type: probe
    source: '/health, request_id konan-1794746399-95480'
    quote: |-
      {"status":"ok","uptime_seconds":39.24397470895201}
      -- HTTP 200 in 0.001712s request_id=konan-1794746399-95480
  - id: E13
    type: metric
    source: '/metrics, request_id konan-1794746483-95556 (12:41:23Z): the complete families http_requests_total and http_exceptions_total'
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/metrics",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E14
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:20.758Z'
    quote: '{"ts": "2026-11-15T12:39:20.758Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: metric
    source: '/metrics, request_id konan-1794746400-95485 (12:40:00Z)'
    quote: |-
      process_uptime_seconds 39.610848541837186
      process_max_rss_bytes 47923200
  - id: E16
    type: metric
    source: '/metrics, request_id konan-1794746483-95556 (12:41:23Z)'
    quote: |-
      process_uptime_seconds 123.15335779218003
      process_max_rss_bytes 47923200
  - id: E17
    type: metric
    source: '/metrics, request_id konan-1794746483-95556 (12:41:23Z)'
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.012810667045414448
      http_request_duration_seconds_count{method="GET",path="/health"} 3
      http_request_duration_seconds_sum{method="GET",path="/metrics"} 0.001893125008791685
      http_request_duration_seconds_count{method="GET",path="/metrics"} 3
      http_request_duration_seconds_sum{method="GET",path="/products"} 2.6744665829464793
      http_request_duration_seconds_count{method="GET",path="/products"} 4
  - id: E18
    type: log
    source: 'lab/logs/app.log @ 2026-11-15T12:39:33.257Z'
    quote: '{"ts": "2026-11-15T12:39:33.257Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "2371236457df", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 698.351, "client": "127.0.0.1:51783"}'
gaps:
  - 'The software-defect lens did not run in triage. The baseline excluded its domain with evidence (E13: no exception series, every status 2xx; E3, E5, E8, E10: the same route and input varies from 1.2 ms to 1255 ms). A defect that began in the same 5.7 s window as the switch is not excluded, only unnecessary.'
  - 'Who turned the switch on, and why, is not in the telemetry: the log shows only request 14d8d99694a0 from a local client. The operator surface of the switch is outside the surface contract.'
  - 'How the switch applies the delay is not verified: the source of the target is out of bounds. The eight observed delays are 172 to 1255 ms, all below the configured 1500 ms; a random delay up to the setting fits, a fixed delay does not.'
  - 'The healthy sample before the switch is short: the process started 6 s before it, with three business requests. The log has no rotated backups, so no earlier history exists; the complaint says "the last few minutes", the telemetry shows about 18 s between the switch and the complaint.'
  - 'The metrics surface has no CPU series, so the judge''s check for load (CPU seconds between two scrapes) was out of reach.'
  - 'Token usage was not captured in this interactive session.'
usage:
  model: claude-fable-5-2
  tokens: 1046257
  wall_clock_seconds: 293
---

# Shop-wide slowness without errors: the chaos switch adds latency

## Summary

**Root cause identified** (class `infra-process`, cause `degradation-switch`). The chaos
switch inside the target was turned on at 12:39:26.668Z with `failure_rate` 0.0 and
`extra_latency_ms` 1500 (E1), and it is still on (E2). Since then every business route
(`/products`, `/products/{id}`, `GET /orders`, `POST /orders`) answers 2xx in 172 to
1255 ms (E5–E11, E18); before the switch the same routes answered in 1 to 2 ms (E3, E4). The
switch injects no errors (E13) and does not delay `/health` (E12, E17), which is why the
health checks are green and fast while users wait. User impact is real: six of the slow
requests are not investigator traffic (E5–E9, E18). Confidence is high: the change marker,
the gauge, the onset 2.6 s after the marker, and the investigator's own probes all agree,
and the judge validated H1 and invalidated the three alternatives.

## Timeline

All times UTC, 2026-11-15.

- 12:39:20.758 — the process starts; the only `startup` event in the log (E14).
- 12:39:21.495 – 12:39:23.609 — business requests answer in 0.985 to 1.903 ms (E3, E4).
- **12:39:26.668 — change marker: `chaos mode enabled`, `failure_rate` 0.0,
  `extra_latency_ms` 1500 (E1).**
- 12:39:29.312 — first slow request: `GET /products` 586.459 ms, status 200 (E5).
- 12:39:31.489 – 12:39:38.690 — five more slow user requests, 237 to 1173 ms, all 2xx
  (E6–E9, E18).
- 12:39:44 — the complaint is raised; 12:39:55 — the investigation starts.
- 12:39:59.989 — `/health` probe: 200 in 1.7 ms (E12).
- 12:40:15.777 — `/products` probe: 200 in 1.257 s (E10).
- 12:41:02.761 — `GET /orders` probe: 200 in 172.635 ms (E11).
- 12:41:23 — the gauge `faultline_chaos_enabled` still reads 1; uptime 123 s, no reset
  (E2, E16).

## Investigation

- **Setup.** `KONAN_ADAPTER` unset, so the surface contract is `docs/lab.md`. Budget: the
  default.
- **Baseline.** `/health` green and fast (E12); a `/products` probe took 1.257 s (E10);
  the metrics snapshot showed the chaos gauge at 1, no exception series, every status
  2xx (E2, E13, E15); the log showed one startup, one WARNING line (E1), and a step in
  `duration_ms` right after it.
- **Triage.** Two lenses ran in parallel, blind to each other: infra-process and
  interfaces. Both found the same chain independently: the marker (E1), the gauge (E2),
  the sharp onset on business routes only (E4 → E5), no failures (E13). The interfaces
  lens classified the mechanism as an internal switch, so `infra-process`. The
  infra-process lens also ruled out a restart, memory growth, and worker starvation
  (E12, E15, E16). The software-defect lens was not spawned; see Gaps.
- **Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete, and
  the prediction was already confirmed by probing (E10, E11, E12).
- **Judge.** One fresh judge saw the four hypotheses and the verbatim evidence only.
  Verdicts: H1 validated; H2, H3, H4 invalidated. One round; concluded.

## Hypotheses

### H1 — the chaos switch adds latency (validated)

The marker names the mechanism and its settings (E1); the gauge shows the switch on at
two scrapes that bracket the slow probes (E2). The last fast business request ended 3.1 s
before the marker (E4); every business request after it is slow and 2xx, on all four
business routes (E5–E11, E18). `failure_rate` 0.0 matches the absence of errors (E13).
`/health` stays under 1 ms after the marker (E12, E17). The judge's weak point: "below
1500 ms" is read from the same data; the eight delays fit a random delay up to the
setting, not a fixed one.

### H2 — crash, restart loop, or hang (invalidated)

The process did start 6 s before the onset (E14), but a start is not a crash: it is the
only startup event, the uptime grows by 83.54 s across scrapes 83.5 s apart with no reset
(E15, E16), and the same process served three fast business requests first (E3, E4), so
a cold start does not explain the step. A hang is excluded by `/health` at 1.7 ms during
the slow period (E12).

### H3 — load saturation (invalidated)

Slow responses without errors (E5) fit every hypothesis, so they carry no weight here.
The process handled 18 requests in about 123 s (E13), the peak memory is flat (E15, E16),
a lone investigator probe was still slow (E10), and `/health` and `/metrics` stayed under
1 ms on average (E12, E17). No queue could form.

### H4 — software defect (invalidated)

No exception series and no non-2xx status exist (E13). The delay is not deterministic per
input: `GET /products` took 1.235 ms before the marker and 586, 832, and 1255 ms after it
(E3, E5, E8, E10). The delay is not limited to one route. The judge's limit: a
state-dependent defect that began in the same 5.7 s window is not excluded, only
unnecessary.

## Safe next steps

Read-only only.

- Ask the operator of the lab who sent request `14d8d99694a0` at 12:39:26.668Z, and
  whether the switch is on by intent (E1).
- Watch the gauge `faultline_chaos_enabled` on `/metrics`, and the log for a
  `chaos_disabled` event.
- When the gauge reads 0, probe `/products` again and compare with the 1 to 2 ms of
  E3 and E4.
- Read the health check as a liveness signal only: it does not cover business latency
  (E12 against E10).

## Gaps

- **The software-defect lens did not run.** The baseline excluded its domain with
  evidence (E13; the same-input variance of E3, E5, E8, E10). The blind spot is accepted
  and recorded.
- **Who and why.** The telemetry shows that the switch was turned on, not by whom. The
  operator surface of the switch is outside the surface contract.
- **The delay mechanism.** The source of the target is out of bounds; the shape of the
  delay (random, up to the setting) is read from eight samples.
- **A short healthy sample.** The process started 6 s before the switch; three business
  requests form the "before". No rotated log backups exist. The complaint's "last few
  minutes" is about 18 s in the telemetry.
- **No CPU series** on the metrics surface.
- **Token usage** was not captured.
