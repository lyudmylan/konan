---
konan_journal: 1
investigation:
  id: 2026-08-25-shop-slowness-chaos-latency
  trigger: 'manual (/konan, human profile; complaint object: source=human, fingerprint=human-1787632757, labels.alertname=human-report, startsAt=2026-08-25T04:39:17Z; investigation started 2026-08-25T04:39:42Z, trigger latency 25 s)'
  complaint: 'Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast.'
  started: 2026-08-25T04:39:42Z
  concluded: 2026-08-25T04:44:17Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'A runtime configuration change at 2026-08-25T04:38:58.330Z enabled chaos mode with extra_latency_ms 1500 (failure_rate 0.0), which injects a variable 0–1500 ms delay on every shop route (/products, /products/{id}, /orders) while /health and /metrics stay sub-millisecond — the shop is slow and the health check cannot see it.'
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: 'Chaos mode enabled at 04:38:58.330Z with extra_latency_ms 1500 injects variable extra latency (0–1500 ms) on shop routes but not on /health or /metrics; this is the cause of the reported shop-wide slowness while health checks stay green and fast.'
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E15, E19, E20, E21, E22, E23, E24]
    evidence_against: []
  - id: H2
    statement: 'The "error page once" was caused by a process crash or restart (connection refused / error during restart).'
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E15, E16, E17, E18, E24]
  - id: H3
    statement: 'The "error page once" was an unhandled exception or 5xx from application code on a shop route.'
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14, E24]
  - id: H4
    statement: 'The "error page once" was a chaos-injected 503 (the configured error_status).'
    incident_class: interfaces
    state: invalidated
    evidence_for: [E5]
    evidence_against: [E5, E14, E24]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:38:52.115Z (the only startup event in the file)'
    quote: '{"ts": "2026-08-25T04:38:52.115Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:38:53.117Z'
    quote: '{"ts": "2026-08-25T04:38:53.117Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "09b87518a63d", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.279, "client": "127.0.0.1:65298"}'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:38:54.189Z'
    quote: '{"ts": "2026-08-25T04:38:54.189Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "0dfd78fd3f73", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.145, "client": "127.0.0.1:65299"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:38:55.262Z'
    quote: '{"ts": "2026-08-25T04:38:55.262Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "6c49fc5d9202", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.794, "client": "127.0.0.1:65300"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:38:58.330Z (configuration-change marker; the only chaos_enabled event in the file)'
    quote: '{"ts": "2026-08-25T04:38:58.330Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "0790a9183bc7", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:38:58.331Z'
    quote: '{"ts": "2026-08-25T04:38:58.331Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "0790a9183bc7", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.777, "client": "127.0.0.1:65301"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:39:00.902Z (first request after the marker)'
    quote: '{"ts": "2026-08-25T04:39:00.902Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "6b10a84b310f", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 501.076, "client": "127.0.0.1:65302"}'
  - id: E8
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:39:02.307Z'
    quote: '{"ts": "2026-08-25T04:39:02.307Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "bf0ef188c26d", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 323.222, "client": "127.0.0.1:65303"}'
  - id: E9
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:39:04.540Z'
    quote: '{"ts": "2026-08-25T04:39:04.540Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "b2d15ab69e66", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1150.011, "client": "127.0.0.1:65304"}'
  - id: E10
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:39:06.303Z'
    quote: '{"ts": "2026-08-25T04:39:06.303Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "0428cb6e96d6", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 683.44, "client": "127.0.0.1:65305"}'
  - id: E11
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:39:08.868Z'
    quote: '{"ts": "2026-08-25T04:39:08.868Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "b96ec1d1ca56", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1482.545, "client": "127.0.0.1:65306"}'
  - id: E12
    type: metric
    source: '/metrics @ 2026-08-25T04:39:43Z, request_id konan-1787632783-36745'
    quote: 'faultline_chaos_enabled 1'
  - id: E13
    type: metric
    source: '/metrics @ 2026-08-25T04:39:43Z, request_id konan-1787632783-36745 (no series follow the TYPE line)'
    quote: '# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter'
  - id: E14
    type: metric
    source: '/metrics @ 2026-08-25T04:39:43Z, request_id konan-1787632783-36745 (complete http_requests_total set)'
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 3 / http_requests_total{method="GET",path="/orders",status="200"} 1 / http_requests_total{method="GET",path="/products",status="200"} 2 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 2'
  - id: E15
    type: probe
    source: '/health @ 2026-08-25T04:39:43Z, request_id konan-1787632783-36739'
    quote: '{"status":"ok","uptime_seconds":51.48989133303985} -- HTTP 200 in 0.003075s request_id=konan-1787632783-36739'
  - id: E16
    type: metric
    source: '/metrics @ 2026-08-25T04:39:43Z, request_id konan-1787632783-36745'
    quote: 'process_uptime_seconds 51.78029554197565'
  - id: E17
    type: metric
    source: '/metrics @ 2026-08-25T04:40:54Z, request_id konan-1787632854-36823 (infra-process lens)'
    quote: 'process_uptime_seconds 122.01166775007732'
  - id: E18
    type: metric
    source: '/metrics @ 2026-08-25T04:39:43Z (konan-1787632783-36745) and again @ 04:43:48Z (konan-1787633028-36911), same value'
    quote: 'process_max_rss_bytes 48185344'
  - id: E19
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:40:45.327Z (investigator probe, interfaces lens)'
    quote: '{"ts": "2026-08-25T04:40:45.327Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1787632843-36778", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1483.199, "client": "127.0.0.1:65331"}'
  - id: E20
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:40:48.102Z (investigator probe, interfaces lens)'
    quote: '{"ts": "2026-08-25T04:40:48.102Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1787632848-36788", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 10.436, "client": "127.0.0.1:65333"}'
  - id: E21
    type: probe
    source: '/products @ 2026-08-25T04:41:30Z, request_id konan-1787632889-36848'
    quote: '-- HTTP 200 in 0.575372s request_id=konan-1787632889-36848'
  - id: E22
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:39:43.593Z (investigator probe, during chaos)'
    quote: '{"ts": "2026-08-25T04:39:43.593Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787632783-36739", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.935, "client": "127.0.0.1:65325"}'
  - id: E23
    type: log
    source: 'lab/logs/app.log @ 2026-08-25T04:40:48.880Z (investigator probe, during chaos)'
    quote: '{"ts": "2026-08-25T04:40:48.880Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787632848-36801", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.482, "client": "127.0.0.1:65335"}'
  - id: E24
    type: metric
    source: '/metrics @ 2026-08-25T04:43:48Z, request_id konan-1787633028-36911 (complete http_requests_total set at conclusion, plus gauges)'
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 5 / http_requests_total{method="GET",path="/metrics",status="200"} 3 / http_requests_total{method="GET",path="/orders",status="200"} 2 / http_requests_total{method="GET",path="/products",status="200"} 4 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 2 / faultline_chaos_enabled 1 / process_uptime_seconds 296.13009454193525'
gaps:
  - 'The "error page once" is not explained: within the observed window (process start 04:38:52.115Z to conclusion) telemetry shows no non-2xx response, no exception, no restart. The surface holds no data from before 04:38:52.115Z (no rotated log backups exist), so an error page seen before that time — e.g. during a restart that produced the single startup marker E1 — cannot be confirmed or refuted from this surface. The settling evidence is the time and content of the error page the user saw.'
  - 'Causation for H1 is argued from onset timing, the 1500 ms ceiling matching extra_latency_ms, and the health/shop split; a post-disable sample (shop latency returning to ~1 ms after chaos is turned off) would strengthen it but requires an operator action outside the read-only investigator surface.'
  - 'Who or what issued POST /chaos/enable (request_id 0790a9183bc7, client 127.0.0.1:65301) is not observable on this surface.'
  - 'Two boundary-hook denials during the run (one in the software-defect lens subagent, one in the orchestrator for a shell-loop grep over lab/logs); neither was retried. Neither affected the conclusion: the counts they sought are covered by E24 (only 2xx series over the process lifetime) and by the full log read.'
usage:
  model: claude-fable-5
  tokens: 928247
  wall_clock_seconds: 275
---

# Shop-wide slowness from chaos-mode latency injection; health checks unaffected

## Summary

**Verdict: root cause identified.** At 2026-08-25T04:38:58.330Z a runtime configuration change enabled chaos mode with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E5, E6). From the very next request (E7) every shop route — `GET /products`, `GET /products/{id}`, `GET /orders`, `POST /orders` — went from ~1–2 ms to a variable 10–1483 ms per request (E7–E11, E19–E21), while `/health` and `/metrics` stayed sub-millisecond (E22, E23) and the chaos gauge still reads `1` at conclusion (E24). This matches the complaint exactly: the whole shop is slow, and health checks are green and fast because the injected delay does not apply to them. Impact: all user-facing shop traffic since 04:38:58Z, no failed requests — every response is still 200/201. Confidence: high for the slowness. The "error page once" part of the complaint is **not** explained — no non-2xx, exception, or restart exists in the observed window, and nothing before process start (04:38:52Z) is observable (see Gaps).

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 04:38:52.115Z | faultline 0.1.0 process starts (only startup marker in the log) | E1 |
| 04:38:53–04:38:55Z | Shop routes healthy: 1.279 ms, 1.145 ms, 1.794 ms | E2, E3, E4 |
| **04:38:58.330Z** | **Config change: chaos mode enabled, extra_latency_ms 1500, failure_rate 0.0, error_status 503** | E5, E6 |
| 04:39:00.902Z | First request after marker: `GET /products` 501 ms | E7 |
| 04:39:02–04:39:08Z | 323 ms, 1150 ms, 683 ms, 1482 ms on shop routes, all 2xx | E8–E11 |
| 04:39:17Z | Complaint raised (startsAt) | trigger |
| 04:39:42Z | Investigation start; `/health` 3 ms, chaos gauge 1, uptime 51.8 s | E15, E12, E16 |
| 04:40:45–04:40:48Z | Investigator probes: `/products` 1483 ms, `/orders` 10 ms, `/health` 0.48 ms — same-route variance, health exempt | E19, E20, E23 |
| 04:41:30Z | `/products` 575 ms | E21 |
| 04:43:48Z | Conclusion snapshot: only 2xx series, chaos gauge still 1, uptime 296 s, RSS unchanged | E24, E18 |

## Investigation

- **Baseline (04:39:42–04:39:44Z):** `/health` 200 in 3 ms; `/metrics` with only 2xx series, no exception series, `faultline_chaos_enabled 1`, uptime 51.8 s; `lab/logs/app.log` 21 lines, single startup, one `chaos_enabled` WARNING, request durations 1–18 ms before it and 323–1482 ms after it.
- **Triage (one round, three lenses in parallel, each blind):** interfaces, infra-process, software-defect. All three converged on the 04:38:58.330Z marker as the onset anchor. Interfaces: config-change marker + sharp step + probabilistic per-request latency. Infra-process: no restart, no counter/uptime reset, RSS flat, process alive-but-degraded; health/metrics exempt from the slowdown. Software-defect: zero exceptions, zero non-2xx, no per-input pattern (same input `/products/1` at 1.1 ms, 1150 ms, 263 ms). The software-defect lens had one probe call denied by the boundary hook and reported from the log alone.
- **Deep-dive:** skipped. H1's triage evidence was deterministic and complete; H2–H4 were already tested against the full log and the complete counter set, so no evidence gap remained for a deep-dive to fill.
- **Judge (evidence-only, adversarial):** H1 validated; H2, H3, H4 invalidated within the observed window. The judge named the single settling item for H2–H4 — the time and content of the user's error page — and noted that the surface contains nothing from before 04:38:52.115Z. Its residual on H4 (a possible second `chaos_enabled` after the baseline scrape) is closed by E24 (`/chaos/enable` count still 1, no non-2xx series) and by the full log read (one `chaos_enabled` line in 30).

## Hypotheses

### H1 — chaos-mode latency injection (interfaces) — **validated**

Before the marker, shop routes answered in 1.1–1.8 ms (E2–E4). The marker (E5) sets `extra_latency_ms: 1500`; the very next request is 501 ms (E7), then 323, 1150, 683, 1482 ms (E8–E11). Same route, different latency per request — `/orders` 1482 ms then 10 ms (E11, E20); `/products` 501 → 1483 → 575 ms (E7, E19, E21) — a probabilistic, per-request delay whose observed ceiling (1483 ms) matches the configured 1500 ms. All responses remain 2xx (E14, E24), consistent with `failure_rate: 0.0`. `/health` stays at 0.5–0.9 ms during chaos (E22, E23), and the gauge reads `1` at both baseline and conclusion (E12, E24). No evidence against.

### H2 — process crash/restart caused the error page (infra-process) — **invalidated** (in window)

One startup marker only (E1); uptime monotonic 51.5 → 51.8 → 122.0 → 296.1 s (E15, E16, E17, E24); counters monotonic (E14 → E24); RSS flat (E18). Nothing before 04:38:52.115Z is observable, so a restart that *produced* E1 is not excluded — recorded as a gap.

### H3 — application exception / 5xx caused the error page (software-defect) — **invalidated** (in window)

`http_exceptions_total` has no series (E13); `http_requests_total` carries only 200/201 series over the process lifetime (E14, E24); the full log has no `unhandled_exception`, `stack`, or non-2xx request line.

### H4 — chaos-injected 503 caused the error page (interfaces) — **invalidated**

`error_status: 503` is configured (E5) but `failure_rate: 0.0` in the same line; no 503 series ever appears (E14, E24); `/chaos/enable` was called exactly once.

## Safe next steps

Read-only suggestions only:

- Ask the reporting users for the time and what the error page showed (HTTP status, "connection refused", browser timeout) — this single fact settles H2–H4.
- Check the operator's own record of who issued `POST /chaos/enable` at 04:38:58.330Z (request_id `0790a9183bc7`, client `127.0.0.1:65301`) and whether it was intended.
- Keep watching `faultline_chaos_enabled` and shop-route `http_request_duration_seconds_sum/_count`; a return to ~1 ms after the gauge drops to 0 would close the causation gap.
- Note for monitoring: `/health` is exempt from the injected delay, so this incident shape is invisible to the health check — a latency probe on a business route would have caught it.

## Gaps

1. **The error page is unexplained.** Every request in the window is 2xx and no exception or restart exists; the surface has no data before 04:38:52.115Z (no rotated backups), so an error seen before then cannot be tested. Settling evidence: the user's error-page timestamp and content.
2. **No post-disable sample for H1.** Turning chaos off is an operator action outside the read-only surface; causation rests on onset timing, the 1500 ms ceiling, and the health/shop split.
3. **Actor of the config change** is not on the surface.
4. **Two boundary-hook denials** (one in a lens subagent, one orchestrator grep loop over `lab/logs/`), neither retried; the facts they sought are covered by E24 and the full log read.
