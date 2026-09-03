---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-wide-latency
  trigger: "manual (human profile; complaint fingerprint human-1787159755, startsAt 2026-08-19T17:15:55Z, investigation start 2026-08-19T17:16:08Z, trigger latency 13s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-08-19T17:16:08Z"
  concluded: "2026-08-19T17:18:31Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode — faultline's runtime degradation switch — was enabled at 17:15:39.365Z via the operator-surface POST /chaos/enable in latency-only form (extra_latency_ms 1500, failure_rate 0.0) and is still enabled; it adds a variable per-request delay to the business endpoints (observed 84–1347 ms server-side, every sample under the declared 1500 ms ceiling) while /health and /metrics stay sub-millisecond — so every shop page is slow, nothing errors, and health checks stay green and fast."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A latency-only runtime degradation switch (chaos mode, extra_latency_ms 1500, failure_rate 0.0) enabled at 17:15:39.365Z via POST /chaos/enable adds a variable per-request delay to /products, /products/{id} and /orders while /health and /metrics are unaffected; the same route and input flips from ~1 ms to ~1300 ms across the marker, investigator probes reproduce the delay, and every response stays 200/201."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E17]
    evidence_against: []
  - id: H2
    statement: "A defect in the application's own code — a slow query, lock contention, N+1 pattern, or exception/retry loop — causes the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E8, E9, E11, E12]
  - id: H3
    statement: "Traffic load or resource exhaustion — CPU starvation, memory pressure, connection saturation — causes the slowness."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E13, E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:39.365Z"
    quote: '{"ts": "2026-08-19T17:15:39.365Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "72c302c02401", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:39.366Z"
    quote: '{"ts": "2026-08-19T17:15:39.366Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "72c302c02401", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 3.285, "client": "127.0.0.1:63462"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:34.160Z"
    quote: '{"ts": "2026-08-19T17:15:34.160Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e526a87f1072", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.09, "client": "127.0.0.1:63459"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:35.228Z"
    quote: '{"ts": "2026-08-19T17:15:35.228Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "3e4c7d0ea071", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.994, "client": "127.0.0.1:63460"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:45.493Z"
    quote: '{"ts": "2026-08-19T17:15:45.493Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "57830834fb2f", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1347.504, "client": "127.0.0.1:63465"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:41.516Z"
    quote: '{"ts": "2026-08-19T17:15:41.516Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "0cfeab2ff1a8", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 83.603, "client": "127.0.0.1:63463"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:48.268Z"
    quote: '{"ts": "2026-08-19T17:15:48.268Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "7a40b99ef579", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 522.968, "client": "127.0.0.1:63467"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:49.663Z"
    quote: '{"ts": "2026-08-19T17:15:49.663Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "3a6825efce39", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 311.419, "client": "127.0.0.1:63468"}'
  - id: E9
    type: probe
    source: "/products request_id=konan-1787159768-67434"
    quote: "-- HTTP 200 in 1.238943s request_id=konan-1787159768-67434"
  - id: E10
    type: probe
    source: "/health request_id=konan-1787159779-67451"
    quote: '{"status":"ok","uptime_seconds":46.62445825012401} -- HTTP 200 in 0.001290s request_id=konan-1787159779-67451'
  - id: E11
    type: probe
    source: "/products/1 request_id=konan-1787159780-67459"
    quote: "-- HTTP 200 in 0.533927s request_id=konan-1787159780-67459"
  - id: E12
    type: metric
    source: "/metrics request_id=konan-1787159768-67428 @ 2026-08-19T17:16:08Z"
    quote: 'http_exceptions_total: no series (HELP/TYPE only); http_requests_total{method="GET",path="/health",status="200"} 2; http_requests_total{method="GET",path="/orders",status="200"} 1; http_requests_total{method="GET",path="/products",status="200"} 3; http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3; http_requests_total{method="POST",path="/chaos/enable",status="200"} 1; http_requests_total{method="POST",path="/orders",status="201"} 2'
  - id: E13
    type: metric
    source: "/metrics request_id=konan-1787159768-67428 @ 2026-08-19T17:16:08Z"
    quote: "faultline_chaos_enabled 1; process_uptime_seconds 35.207628125092015; process_max_rss_bytes 48054272"
  - id: E14
    type: metric
    source: "/metrics request_id=konan-1787159819-67487 @ 2026-08-19T17:16:59Z"
    quote: "process_uptime_seconds 85.71089458302595; process_max_rss_bytes 48087040"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:15:33.364Z"
    quote: '{"ts": "2026-08-19T17:15:33.364Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E16
    type: metric
    source: "/metrics request_id=konan-1787159819-67487 @ 2026-08-19T17:16:59Z"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/health"} 0.01789637515321374 (count 3); http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 2.341524416115135 (count 4); http_request_duration_seconds_sum{method="GET",path="/products"} 1.8444016678258777 (count 4); http_request_duration_seconds_sum{method="GET",path="/orders"} 1.305822166847065 (count 2)'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:16:19.978Z"
    quote: '{"ts": "2026-08-19T17:16:19.978Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787159779-67451", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.439, "client": "127.0.0.1:63496"}'
gaps:
  - "Who or what issued POST /chaos/enable (client 127.0.0.1:63462) is outside the investigator's surface; the operator surface is not probeable."
  - "No CPU or event-loop metric exists on the surface; saturation is excluded from request counts, flat RSS, continuous uptime and fast /health, not from a CPU sample."
  - "The path-scoping of the injected delay (health/metrics exempt) is inferred from observed latencies, not from documented behaviour."
  - "No chaos_disabled marker was observed; the switch was still on at last observation (17:17:10Z), so the end of impact is unknown."
usage:
  model: claude-fable-5
  tokens: 1195824
  wall_clock_seconds: 143
---

# Shop-wide latency from a latency-only chaos switch enabled at 17:15:39Z

## Summary

**Root cause identified.** At 2026-08-19T17:15:39.365Z faultline's runtime degradation switch ("chaos mode") was enabled through the operator surface (`POST /chaos/enable`) with `extra_latency_ms 1500` and `failure_rate 0.0` (E1, E2). From that second on, every business endpoint (`/products`, `/products/{id}`, `/orders`) answers with a variable added delay — 84–1347 ms observed, never above the 1500 ms ceiling (E5–E9, E11, E16) — while every response stays 200/201 and no exception is recorded (E12). `/health` and `/metrics` are not delayed (E10, E17), so health checks stay green and fast. User traffic was affected (non-investigator request ids in E5–E8); the investigator's own probes reproduce it (E9, E11). The switch was still enabled at last observation (E13). Confidence: high — the change marker, the before/after flip on the same route and input, and the absence of errors all match; the judge found no contradicting evidence.

## Timeline

- 17:15:33.364Z — process start, single startup marker (E15).
- 17:15:34–36Z — business requests at ~1 ms: `/products` 1.09 ms (E3), `/products/1` 0.994 ms (E4).
- **17:15:39.365Z — config-change marker: `chaos_enabled`, `failure_rate 0.0`, `extra_latency_ms 1500` (E1), via `POST /chaos/enable -> 200` (E2).**
- 17:15:41–49Z — user traffic slows: `/products` 83.6 ms (E6), `/products/1` 1347.5 ms (E5), `/products` 523 ms (E7), `/orders` 311 ms (E8). All 200/201.
- 17:16:08Z — investigation start; `/metrics`: `faultline_chaos_enabled 1`, no exceptions (E12, E13).
- 17:16:09–21Z — investigator probes reproduce: `/products` 1.24 s (E9), `/products/1` 0.53 s (E11); `/health` 1.3 ms (E10, E17).
- 17:16:59Z — uptime continuous, RSS flat (E14); flag still on.

## Investigation

- **Baseline**: `/health`, `/metrics`, `/products`, `/orders`, `/products/1` probes and the full 23-line log (no rotated backups). Found the change marker and the latency step.
- **Triage**: three lenses in parallel (software-defect, infra-process, interfaces). All three independently flagged the `chaos_enabled` marker as the onset; software-defect found no exception/non-2xx signature; infra-process found no restart or resource drift; interfaces noted the delay spares `/health` and `/metrics`.
- **Deep-dive**: skipped — H1's triage evidence was deterministic and complete (change marker + same-route before/after + probe reproduction).
- **Judge**: H1 validated; H2 and H3 invalidated. Judge noted that path-scoping of the delay is inferred from observation, not documentation (recorded under Gaps).

## Hypotheses

### H1 — latency-only chaos switch (infra-process) — validated
For: E1/E2 (marker and its request), E3/E4 vs E5/E6/E7/E8 (same routes ~1 ms before, 84–1347 ms after), E9/E11 (probes reproduce), E12 (all 2xx, no exceptions, matching `failure_rate 0.0`), E13 (flag still on), E10/E17 (health unaffected), E16 (per-path duration sums). Against: none.

### H2 — application code defect (software-defect) — invalidated
The same route and input ran at ~1 ms before the marker (E4) and 1347 ms after (E5); no exceptions or non-2xx (E12); latency is bounded and variable across all shop routes (E6, E8, E9, E11), not a fixed slow path. No evidence for.

### H3 — load or saturation (load-saturation) — invalidated
Single-digit request counts per path (E12, E16); RSS flat 48.05→48.09 MB (E13, E14); continuous uptime from one startup (E15, E13, E14); `/health` on the same process answers in <1 ms (E10). A saturated process would not spare `/health`.

## Safe next steps

- Read `/metrics` periodically and watch `faultline_chaos_enabled`; a return to `0` (and a `chaos_disabled` log marker) marks the end of impact.
- Grep `lab/logs/app.log` for `event": "chaos_` to find any later change markers.
- Correlate `client` port `127.0.0.1:63462` of E2 with operator/eval activity outside this surface to identify the actor.

## Gaps

- The actor behind `POST /chaos/enable` is not observable from the investigator's surface.
- No CPU/event-loop metric; saturation is excluded indirectly.
- Health/metrics exemption from the delay is an observation over a small sample (3 `/health` requests), not documented behaviour.
- End of impact unknown: no `chaos_disabled` seen by 17:17:10Z.
