---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-slowness-chaos-latency
  trigger: "manual (/konan; complaint object: source=human, fingerprint=human-1787175059, labels.alertname=human-report, startsAt=2026-08-19T21:30:59Z; investigation start 2026-08-19T21:31:12Z; trigger latency 13s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-08-19T21:31:12Z"
  concluded: "2026-08-19T21:33:43Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode — faultline's runtime degradation switch — was enabled at 21:30:42.769Z via the operator-surface POST /chaos/enable in latency-only form (extra_latency_ms 1500, failure_rate 0.0) and is still enabled; it adds a variable per-request delay (observed 271–1453 ms) to the business endpoints while /health and /metrics stay at ~1 ms — so every page is slow, nothing errors, and health checks stay green and fast."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A latency-only degradation switch (chaos mode, extra_latency_ms 1500, failure_rate 0.0) enabled at 21:30:42.769Z via POST /chaos/enable adds a variable per-request delay to /products, /products/{id} and /orders while /health and /metrics are unaffected; the same route and input flips from ~1 ms to hundreds of ms across the marker, investigator probes reproduce it, every response stays 200/201, and the switch has not been turned off."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E13]
    evidence_against: []
  - id: H2
    statement: "A defect in the application's own code — slow query, lock, N+1, or exception-retry loop — causes the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E9, E10, E11]
  - id: H3
    statement: "Load or resource exhaustion, or a process lifecycle event (restart, CPU burn, memory pressure, worker starvation), causes the slowness."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E8, E9, E10, E12, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:30:36.795Z — the only startup event in the log"
    quote: |-
      {"ts": "2026-08-19T21:30:36.795Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:30:42.769Z — the configuration-change marker; the only WARNING in the log"
    quote: |-
      {"ts": "2026-08-19T21:30:42.769Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "ae6b6ddb3404", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:30:42.770Z — same request_id as E2: the POST that changed the config"
    quote: |-
      {"ts": "2026-08-19T21:30:42.770Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "ae6b6ddb3404", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.98, "client": "127.0.0.1:65423"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:30:38.626Z — user request before the marker"
    quote: |-
      {"ts": "2026-08-19T21:30:38.626Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "632badfea26d", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.002, "client": "127.0.0.1:65421"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:30:48.913Z — same route and input as E4, after the marker: ~880x slower, still 200"
    quote: |-
      {"ts": "2026-08-19T21:30:48.913Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "040c61c4ba75", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 882.276, "client": "127.0.0.1:65426"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:30:39.698Z — last user request before the marker"
    quote: |-
      {"ts": "2026-08-19T21:30:39.698Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "65ae24bb27a2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.735, "client": "127.0.0.1:65422"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 21:30:45.355Z and 21:30:51.447Z — first user request after the marker, and the slowest; post-marker user durations range 271–1453 ms, all under the declared 1500 ms, none erroring"
    quote: |-
      {"ts": "2026-08-19T21:30:45.355Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "0fd2c5aca0f2", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 512.214, "client": "127.0.0.1:65424"}
      {"ts": "2026-08-19T21:30:51.447Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8a1b64f68ad5", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1453.206, "client": "127.0.0.1:65427"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:31:14.836Z — investigator health probe after the marker, still sub-millisecond"
    quote: |-
      {"ts": "2026-08-19T21:31:14.836Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787175074-71816", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.642, "client": "127.0.0.1:65450"}
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1787175077-71822 @ ~2026-08-19T21:31:17Z — chaos gauge on, no exception series, only 200/201 statuses"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 40.93101125000976
      process_max_rss_bytes 47759360
      # TYPE http_exceptions_total counter
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E10
    type: probe
    source: "probes /health (konan-1787175074-71816), /products (konan-1787175093-71848), /orders (konan-1787175096-71854) @ ~21:31:14–21:31:36Z — investigator traffic reproduces the asymmetry"
    quote: |-
      -- HTTP 200 in 0.002121s request_id=konan-1787175074-71816
      -- HTTP 200 in 0.512960s request_id=konan-1787175093-71848
      -- HTTP 200 in 0.386010s request_id=konan-1787175096-71854
  - id: E11
    type: log
    source: "lab/logs/app.log, full file (22 lines at baseline, no rotated backups) — grep results"
    quote: |-
      no line contains "chaos_disabled", "unhandled_exception", or a "stack" field; every "event": "request" line has "status": 200 or 201
  - id: E12
    type: metric
    source: "probe /metrics @ ~2026-08-19T21:32:14Z (infra lens) and probe /health — uptime monotonic, RSS flat"
    quote: |-
      process_uptime_seconds 97.67331791599281
      process_max_rss_bytes 47841280
      {"status":"ok","uptime_seconds":104.22351862490177}
  - id: E13
    type: metric
    source: "probe /metrics, request_id=konan-1787175219-71929 @ ~2026-08-19T21:33:39Z — final re-read: switch still on, no restart, no exceptions"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 183.00547370803542
      process_max_rss_bytes 47923200
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.017355667194351554
      http_request_duration_seconds_count{method="GET",path="/health"} 4
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 2.282097707968205
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 4
gaps:
  - "Who or what issued POST /chaos/enable (E3, client 127.0.0.1:65423) is outside the investigator's surface; /chaos is operator-only and read-only rules forbid querying its current parameters directly — the gauge (E9, E13) is the only view of its state."
  - "The observation window is one process lifetime of ~3 minutes with low request counts; the 'variable delay' claim rests on 8 user samples plus 3 investigator probes."
  - "The per-request delay mechanism (random vs. fixed) cannot be read from telemetry; the observed 271–1453 ms spread under a 1500 ms declared ceiling is consistent with a randomized delay but not proven."
usage:
  model: claude-fable-5
  tokens: 1820235
  wall_clock_seconds: 151
---

# Shop-wide latency with no errors: chaos mode enabled in latency-only form

## Summary

**Root cause identified.** At 21:30:42.769Z the operator-surface `POST /chaos/enable`
turned on faultline's chaos mode with `extra_latency_ms 1500` and `failure_rate 0.0`
(E2, E3). From that moment every business route — `/products`, `/products/{id}`,
`/orders`, `POST /orders` — takes hundreds of milliseconds to 1.45 s instead of ~1 ms
(E4→E5, E6→E7), while `/health` and `/metrics` stay at ~1 ms (E8, E10). Because the
failure rate is zero, no request errors (E9, E11). The switch is still on at the end of
the investigation (E13). Impact: all user-facing shop traffic since 21:30:42Z is slow;
none of it fails. Confidence: high — the config marker, the before/after step change on
identical routes, the live reproduction by investigator probes, and the gauge all agree,
and the two alternative classes are excluded by the same evidence.

## Timeline

- 21:30:36.795Z — process start, the only startup event (E1).
- 21:30:37–21:30:39Z — user traffic at 1–14 ms, all 200/201 (E4, E6).
- **21:30:42.769Z — `chaos_enabled` WARNING, `extra_latency_ms 1500`, `failure_rate 0.0`, via `POST /chaos/enable` (E2, E3).**
- 21:30:45.355Z — first user request after the marker: `GET /products` 512 ms (E7).
- 21:30:48.913Z — `GET /products/1` 882 ms, same route/input that took 1.0 ms at 21:30:38Z (E4, E5).
- 21:30:51.447Z — `POST /orders` 1453 ms, still 201 (E7).
- 21:30:59Z — complaint received (`startsAt`); 21:31:12Z investigation start.
- 21:31:14–21:31:36Z — investigator probes: `/health` 2 ms, `/products` 513 ms, `/orders` 386 ms (E8, E10).
- 21:33:39Z — final metrics read: `faultline_chaos_enabled 1`, uptime 183 s, no exception series (E13).

## Investigation

- **Baseline**: `/health` 200 in 2 ms; `/metrics` showed `faultline_chaos_enabled 1`,
  no exception series, all statuses 200/201; the 22-line log held the startup event,
  fast pre-marker traffic, the `chaos_enabled` marker, and slow post-marker traffic.
- **Triage** (three lenses in parallel, blind: software-defect, infra-process,
  interfaces): all three located the same marker (E2) as the onset, reported zero
  exceptions/non-2xx, the `/health`-exempt shape, and that the condition is live.
  Infra-process additionally confirmed single startup, monotonic uptime, flat RSS (E12).
- **Deep-dive**: skipped — triage evidence for H1 was deterministic and complete; the
  budget was not needed.
- **Judge** (evidence-only): H1 validated; H2 and H3 invalidated. The judge flagged
  that "remains enabled" rested on one gauge read; a final `/metrics` read (E13) closed
  that gap.

## Hypotheses

### H1 — chaos mode, latency-only — validated
For: the marker and its originating POST (E2, E3); identical route/input fast before
and slow after (E4, E5; E6, E7); `/health` unaffected after the marker (E8, E10);
gauge on and no errors (E9); no disable marker (E11); still on at conclusion (E13).
Against: none.

### H2 — application code defect — invalidated
Against: no exception series and no stack/unhandled_exception lines (E9, E11); the same
input `/products/1` flips from 1 ms to 882 ms across a config marker (E4, E5); all
routes degrade together rather than one route or one input (E10).

### H3 — load/saturation or process lifecycle — invalidated
Against: one startup event and monotonic uptime 40 → 97 → 183 s (E1, E9, E12, E13);
RSS flat at ~47.8 MB (E9, E12, E13); `/health` stays sub-millisecond in the same process
while business routes are slow (E8, E10); a step change at E2, not a ramp.

## Safe next steps

- Confirm with the operator who or what issued `POST /chaos/enable` at 21:30:42.769Z
  from `127.0.0.1:65423` (E3) and whether it was intended.
- Keep watching `faultline_chaos_enabled` and the per-route duration sums; a
  `chaos_disabled` log event would mark the end of impact.
- Note for monitoring: `/health` does not traverse the degraded path, so liveness probes
  cannot see this incident class; a business-route latency probe would.

## Gaps

- The identity and intent behind the `POST /chaos/enable` call are outside the
  read-only surface; `/chaos` itself may not be queried.
- Short window, low sample count: 8 user requests and 3 investigator probes after the
  marker.
- Whether the injected delay is randomized is inferred from the 271–1453 ms spread under
  a 1500 ms ceiling, not read from telemetry.
