---
konan_journal: 2
investigation:
  id: 2026-11-03-occasional-shop-503s
  trigger: 'manual (/konan adapter; fingerprint human-1793710536; complaint startsAt 2026-11-03T12:55:36Z; investigation start 2026-11-03T12:55:45Z; trigger latency 9s)'
  complaint: 'A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?'
  started: 2026-11-03T12:55:45Z
  concluded: 2026-11-03T13:01:13Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'An internal chaos degradation switch, enabled at 2026-11-03T12:55:22.368Z with failure_rate 0.08 and error_status 503, injects per-request probabilistic 503 failures into shop traffic; it was still enabled at conclusion.'
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: 'An internal chaos switch (enabled 12:55:22.368Z, failure_rate 0.08, error_status 503, no added latency) injects probabilistic 503s into user requests; retries succeed because the failure is per-request; the switch remains on, so the error risk continues.'
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E13, E16, E17]
    evidence_against: []
  - id: H2
    statement: 'The target''s own code fails for some inputs (deterministic per-input defect or unhandled exception) and causes the user-visible errors.'
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E6, E7, E9, E10]
  - id: H3
    statement: 'A process crash or restart during the complaint window caused the user-visible errors.'
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E12, E14, E16]
  - id: H4
    statement: 'A dependency, proxy, or gateway tier failed on its own and produced the 503s.'
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E4, E5, E10]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:22.368Z'
    quote: '{"ts": "2026-11-03T12:55:22.368Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "f3f5e790e8d4", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:23.455Z'
    quote: '{"ts": "2026-11-03T12:55:23.455Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "3d8794a742ff", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:23.455Z'
    quote: '{"ts": "2026-11-03T12:55:23.455Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "3d8794a742ff", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.223, "client": "127.0.0.1:50936"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:23.474Z'
    quote: '{"ts": "2026-11-03T12:55:23.474Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "97702bdb1744", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:23.474Z'
    quote: '{"ts": "2026-11-03T12:55:23.474Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "97702bdb1744", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.186, "client": "127.0.0.1:50937"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:23.553Z'
    quote: '{"ts": "2026-11-03T12:55:23.553Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "aa44388133d4", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.45, "client": "127.0.0.1:50942"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:23.568Z'
    quote: '{"ts": "2026-11-03T12:55:23.568Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "62e137697844", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.419, "client": "127.0.0.1:50943"}'
  - id: E8
    type: metric
    source: '/metrics @ 2026-11-03T12:56:05Z (request_id konan-1793710565-34475)'
    quote: 'faultline_chaos_enabled 1'
  - id: E9
    type: metric
    source: '/metrics @ 2026-11-03T12:56:05Z (request_id konan-1793710565-34475)'
    quote: 'http_requests_total{method="GET",path="/products/1",status="503"} 1 | http_requests_total{method="GET",path="/products/2",status="503"} 1 | http_requests_total{method="GET",path="/products/{product_id}",status="200"} 15'
  - id: E10
    type: metric
    source: '/metrics @ 2026-11-03T12:56:05Z (request_id konan-1793710565-34475); the counter has zero series — no samples follow the header'
    quote: '# HELP http_exceptions_total Unhandled exceptions by Python class name. | # TYPE http_exceptions_total counter'
  - id: E11
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:55:17.444Z — the only startup event in the log'
    quote: '{"ts": "2026-11-03T12:55:17.444Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E12
    type: probe
    source: '/health @ 2026-11-03T12:56:04Z (request_id konan-1793710564-34470)'
    quote: '{"status":"ok","uptime_seconds":46.96982095902786} -- HTTP 200 in 0.008340s'
  - id: E13
    type: metric
    source: '/metrics @ 2026-11-03T12:56:05Z (request_id konan-1793710565-34475)'
    quote: 'http_requests_total{method="POST",path="/chaos/enable",status="200"} 1'
  - id: E14
    type: metric
    source: '/metrics @ 2026-11-03T12:56:05Z (request_id konan-1793710565-34475)'
    quote: 'process_uptime_seconds 47.60328166699037'
  - id: E15
    type: metric
    source: '/metrics @ 2026-11-03T12:56:05Z (request_id konan-1793710565-34475)'
    quote: 'http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.0072302480693906546 | http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 15'
  - id: E16
    type: metric
    source: '/metrics @ 2026-11-03T12:57:30Z (infra-process triage lens scrape)'
    quote: 'faultline_chaos_enabled 1 | process_uptime_seconds 132.8'
  - id: E17
    type: metric
    source: '/metrics @ 2026-11-03T13:01:13Z (request_id konan-1793710873-34649)'
    quote: 'faultline_chaos_enabled 1 | process_uptime_seconds 355.83972895890474 | http_requests_total{method="GET",path="/products/1",status="503"} 1 | http_requests_total{method="GET",path="/products/2",status="503"} 1'
gaps:
  - 'No telemetry exists before the startup marker at 2026-11-03T12:55:17.444Z (single log file, no rotated backups). Failures earlier in the reported "last few minutes" window are unobservable.'
  - 'The identity and intent of the operator call that enabled the switch (POST /chaos/enable from 127.0.0.1:50934 at 12:55:22.368Z) are outside the surface contract; only the client address is visible.'
  - 'No non-investigator traffic arrived after 12:55:23.912Z, so continued user impact is inferred from the live gauge (E17), not observed as new 503s.'
usage:
  model: claude-fable-5
  tokens: 1297544
  wall_clock_seconds: 328
---

# Occasional shop 503s: an internal chaos degradation switch is on

## Summary

Root cause identified. The report is not "nothing": an internal chaos degradation
switch was enabled at 12:55:22.368Z with `failure_rate: 0.08` and `error_status: 503`
(E1). While it is on, each request has an ~8% chance of an injected 503. Two user
requests failed (`GET /products/1`, `GET /products/2` — E3, E5), each tagged by the
service itself as a chaos-injected failure with a matching request id (E2, E4).
Immediate retries of the same paths returned 200 (E6, E7), which matches the
"works on retry" symptom. The switch was still on at conclusion (E17), so the
low-rate error risk continues until an operator disables it. Confidence is high:
every 503 in the window pairs one-to-one with a chaos event, and the judge
invalidated all rival hypotheses.

## Timeline

- 12:55:17.444Z — process start, faultline 0.1.0 (E11). Telemetry begins here.
- 12:55:18–12:55:22Z — healthy traffic, all 200/201.
- 12:55:22.368Z — config-change marker: chaos mode enabled, rate 0.08, status 503,
  no added latency (E1); one `POST /chaos/enable -> 200` (E13).
- 12:55:23.455Z — `GET /products/1 -> 503`, chaos-injected, user traffic (E2, E3).
- 12:55:23.474Z — `GET /products/2 -> 503`, chaos-injected, user traffic (E4, E5).
- 12:55:23.553Z / 12:55:23.568Z — same paths return 200 on retry (E6, E7).
- 12:55:36Z — human complaint raised (trigger `startsAt`).
- 12:55:45Z — investigation start (trigger latency 9 s).
- 12:56:04–05Z — baseline: health 200 (E12), chaos gauge 1 (E8), two 503 counters (E9).
- 12:57:30Z — triage re-check: gauge still 1, uptime monotonic (E16).
- 13:01:13Z — final scrape: gauge still 1, no new 503s, no restart (E17). Concluded.

## Investigation

Baseline (12:56:04–05Z): green health endpoint over a live chaos gauge — the
healthy-monitoring trap shape. Three triage lenses ran in parallel, each blind to
the others: software-defect, infra-process, interfaces. All three converged:
no exceptions (E10), clean process lifecycle (E11, E12, E14), no latency or
resource anomaly (E15), and the chaos switch as the single anomaly (E1, E8).
Triage evidence for H1 was deterministic and complete (marker → paired failures →
live gauge), so no deep-dive round was needed; four hypotheses went to the
adversarial judge. The judge validated H1 and invalidated H2–H4, with one caveat:
continued impact was inference, not observation. A final scrape (E17) confirmed
the switch is still on; it stays an inference that future requests will fail,
grounded in the configured rate.

## Hypotheses

### H1 — chaos degradation switch (validated)

The switch went on at 12:55:22.368Z (E1) via the operator endpoint (E13); the
first user 503 followed ~1.1 s later. Both 503s share request ids with
`chaos_failure` events (E2→E3, E4→E5) — a one-to-one pairing with no orphan
errors (E9). The same inputs succeeded ~100 ms later (E6, E7), the signature of a
per-request probabilistic fault. Observed failure fraction ≈ 2/17 product
requests, consistent with rate 0.08 in a small sample. The gauge read 1 at three
scrapes across five minutes (E8, E16, E17). Nothing contradicts it.

### H2 — software defect (invalidated)

No unhandled exceptions exist (E10, zero series). The failing inputs succeed on
retry with no code change (E6, E7) — a deterministic per-input defect cannot do
that. Every failure is labeled chaos-injected (E2, E4), and the 503 count equals
the chaos-failure count (E9): no unexplained remainder for a defect to own.

### H3 — process crash or restart (invalidated)

One startup marker only (E11). Uptime back-computes to the same start time at
12:56:05Z (E14), 12:57:30Z (E16), and 13:01:13Z (E17 — monotonic, no reset), and
health returned 200 (E12). The observed errors were served and logged in-process,
which a crashed process cannot do.

### H4 — dependency, proxy, or gateway failure (invalidated)

The 503s were generated inside the target: the target's own request logger emits
the `chaos_failure` events (E2, E4), durations are sub-millisecond (E3: 0.223 ms,
E5: 0.186 ms — too fast for a failed upstream call), and no exception a failed
dependency call would raise exists (E10).

## Safe next steps

- Ask the operator who enabled the switch (the `POST /chaos/enable` call at
  12:55:22.368Z from 127.0.0.1:50934, E13) whether it is intentional and when it
  will go off. Disabling it is remediation and is out of scope here.
- Watch `faultline_chaos_enabled` for the return to 0, and the per-path 503
  counters in `http_requests_total` for new increments while it stays on.
- If user reports continue after the gauge reads 0, reopen: the pairing check
  (503 access line ↔ `chaos_failure` event per request id) is the discriminator.

## Gaps

- Telemetry starts at 12:55:17.444Z; there are no rotated log backups. If users
  saw errors earlier in their "last few minutes", that part of the window is
  unobservable. It cannot change the verdict for the observed window.
- The operator identity behind the enable call is outside the read-only surface;
  only the client address is visible.
- No real user traffic arrived after 12:55:23.912Z, so "errors continue" rests on
  the live gauge and the configured rate (E17), not on newly observed failures.
