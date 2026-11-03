---
konan_journal: 2
investigation:
  id: 2026-11-03-chaos-switch-products-503s
  trigger: 'manual (/konan human profile; fingerprint human-1793708181; complaint startsAt 2026-11-03T12:16:21Z; investigation start 2026-11-03T12:16:52Z; trigger latency 31s)'
  complaint: 'Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report.'
  started: 2026-11-03T12:16:52Z
  concluded: 2026-11-03T12:24:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'An operational chaos switch inside faultline, enabled at 2026-11-03T12:15:37.432Z with failure_rate 0.6 and error_status 503, injected the only two 503 responses on GET /products (user-style traffic) until it was disabled at 2026-11-03T12:15:43.776Z; the switch is off now and no impact continues.'
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: 'An internal degradation switch (chaos mode), enabled at 12:15:37.432Z with failure_rate 0.6 and error_status 503, injected the only two 503 responses on GET /products, and was disabled at 12:15:43.776Z.'
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: 'A defect in the shop service''s own code caused the 503 responses on GET /products.'
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E10, E11, E13]
  - id: H3
    statement: 'The degradation switch is still on and the shop service still fails user requests at investigation time (an active incident now).'
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E9, E11, E13, E14, E15]
latent_findings:
  - statement: 'Product 4 (Mystery Box) carries price: null; reads of it return 200, and no order of product 4 appears anywhere in telemetry, so the order path over a null price is unexercised; only an investigator probe observed this.'
    evidence: [E17]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:33.570Z'
    quote: '{"ts": "2026-11-03T12:15:33.570Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:37.432Z'
    quote: '{"ts": "2026-11-03T12:15:37.432Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "fb21e169522f", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:38.493Z'
    quote: '{"ts": "2026-11-03T12:15:38.493Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "40043fe0628e", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:38.493Z'
    quote: '{"ts": "2026-11-03T12:15:38.493Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "40043fe0628e", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.324, "client": "127.0.0.1:50568"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:42.718Z'
    quote: '{"ts": "2026-11-03T12:15:42.718Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "96607429e2e8", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:42.719Z'
    quote: '{"ts": "2026-11-03T12:15:42.719Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "96607429e2e8", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.286, "client": "127.0.0.1:50572"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:15:43.776Z'
    quote: '{"ts": "2026-11-03T12:15:43.776Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "2524d8e205d0", "event": "chaos_disabled"}'
  - id: E8
    type: metric
    source: '/metrics probe, request_id konan-1793708219-33079'
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 2'
  - id: E9
    type: metric
    source: '/metrics probe, request_id konan-1793708219-33079'
    quote: 'faultline_chaos_enabled 0'
  - id: E10
    type: metric
    source: '/metrics probe, request_id konan-1793708219-33079'
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E11
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:16:03.840Z'
    quote: '{"ts": "2026-11-03T12:16:03.840Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "da3676c3011e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.768, "client": "127.0.0.1:50575"}'
  - id: E12
    type: probe
    source: '/health, request_id konan-1793708214-33074'
    quote: |-
      {"status":"ok","uptime_seconds":81.39077162486501}
      -- HTTP 200 in 0.002019s request_id=konan-1793708214-33074
  - id: E13
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:18:56.424Z'
    quote: '{"ts": "2026-11-03T12:18:56.424Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793708336-33149", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.487, "client": "127.0.0.1:50612"}'
  - id: E14
    type: metric
    source: '/metrics probe at conclusion, request_id konan-1793708645-33236'
    quote: 'faultline_chaos_enabled 0'
  - id: E15
    type: metric
    source: '/metrics probe at conclusion, request_id konan-1793708645-33236'
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 2'
  - id: E16
    type: metric
    source: '/metrics probe at conclusion, request_id konan-1793708645-33236'
    quote: 'process_uptime_seconds 511.7113696669694'
  - id: E17
    type: probe
    source: '/products/4, request_id konan-1793708458-33198'
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001982s request_id=konan-1793708458-33198
gaps:
  - 'No telemetry exists before the process start at 2026-11-03T12:15:33.570Z (E1 is the first log line; no rotated backups). If the reported "noise earlier" predates that start, it is out of observable reach. The tie between the complaint and the chaos window rests on the window being the only anomaly in the full observable history, not on a complaint timestamp — the judge marked this clause unprovable from telemetry, so it stays a gap, not a claim.'
  - 'The identity of whoever operated the chaos switch is outside the telemetry surface: the log records only local client addresses (127.0.0.1:50567 enabled it, 127.0.0.1:50573 disabled it).'
  - 'No dedicated lens exists for load-saturation, third-party, or data-db. Saturation signals were checked in passing (durations under 13 ms, stable RSS 46989312, E16 continuous uptime); the lab has no database or third-party dependency per docs/lab.md, so those classes were out of scope by contract, not verified empty.'
usage:
  model: claude-fable-5
  tokens: 1876049
  wall_clock_seconds: 482
---

# Chaos switch injected 503s on GET /products — six-second window, closed

## Summary

Root cause identified, incident over. An operational chaos switch inside faultline was enabled at 12:15:37.432Z with a 60% failure rate and error status 503 (E2), injected exactly two 503 responses on `GET /products` for user-style traffic (E3–E6, count confirmed by E8), and was disabled 6.3 seconds later at 12:15:43.776Z (E7). This is the "noise earlier" from the handover complaint — it is the only anomaly in the entire observable telemetry history. Nothing is wrong with the shop service now: the chaos gauge reads 0 at conclusion (E14), the 503 counter has not moved (E15), the exceptions counter is empty (E10), every request after the disable marker returned 200/201 (E11, E13), and the process has run continuously since start (E16). Impact: two failed user requests out of five user-style requests in the window. Confidence is high — each failed request carries a chaos-injection marker with a matching request id, so attribution is per-request, not by time correlation.

## Timeline

- 12:15:33.570Z — faultline 0.1.0 starts; first line of the observable history (E1).
- 12:15:37.432Z — **flag-change marker**: chaos mode enabled, failure_rate 0.6, error_status 503, extra_latency_ms 0 (E2).
- 12:15:38.493Z — first injected failure: `GET /products -> 503`, request_id 40043fe0628e (E3, E4).
- 12:15:42.718Z — second injected failure: `GET /products -> 503`, request_id 96607429e2e8 (E5, E6).
- 12:15:43.776Z — **flag-change marker**: chaos mode disabled (E7).
- 12:16:03.840Z–12:16:08Z — user-style traffic resumes, all 200/201 (E11).
- 12:16:21Z — complaint raised (`startsAt`); investigation starts 12:16:52Z.
- 12:16:54Z — baseline: `/health` 200, uptime 81.4 s (E12); metrics show 503 count 2, chaos gauge 0 (E8, E9).
- 12:18:56.424Z — investigator probe `GET /products -> 200` (E13).
- 12:24:05Z — conclusion reads: gauge still 0, 503 count still 2, uptime 511.7 s continuous (E14, E15, E16).

## Investigation

Baseline (12:16:52Z–12:17:00Z): `/health` 200 with 81 s uptime (E12), full metrics snapshot (E8–E10), and the complete log — 29 lines at that point, covering the whole process life. The baseline alone exposed the chaos window.

Triage: three lenses ran in parallel, each blind to the others — infra-process, software-defect, interfaces. All three independently attributed the two 503s to the chaos window via the per-request `chaos_failure` markers. The software-defect lens added the product-4 null-price observation (E17). No lens found an active anomaly.

Deep-dive: skipped. The triage evidence for H1 was deterministic and complete (request-id linkage between injection markers and failed requests), so the hypothesis list went straight to the judge.

Judge (adversarial, evidence-only): validated H1's injection mechanism; flagged the clause tying the window to the complaint's "noise" as uncited (moved to Gaps); invalidated H2 and H3; asked for one fresh gauge read at report time to make H3 final. The conclusion metrics read (E14–E16) supplied it.

## Hypotheses

### H1 — internal degradation switch injected the 503s (validated)

The switch-on marker (E2) names the exact mechanism: failure rate 0.6, error status 503. Both 503 responses (E4, E6) carry request ids that also appear on `chaos_failure` injection markers (E3, E5) — attribution at the request level. The metrics counter agrees: exactly two 503s on that route (E8). The switch-off marker (E7) bounds the window. Nothing contradicts it.

### H2 — a code defect caused the 503s (invalidated)

The 503s themselves (E3, E5) show occurrence, not cause. Every 503 in history is chaos-marked; the exceptions counter has no series at all (E10); the same route returned 200 for user traffic twenty seconds later with no code change in between (E11) and for an investigator probe at 12:18:56Z (E13). The failure pattern was probabilistic per request, not deterministic per input.

### H3 — the incident is still active (invalidated)

The disable marker (E7), the gauge at 0 in both the baseline (E9) and conclusion (E14) reads, an unmoved 503 counter (E15), and healthy responses from both user traffic (E11) and investigator probes (E13) refute it. Continuous uptime (E16) rules out a masking restart.

## Safe next steps

- Ask in the operator channel who enabled the chaos switch at 12:15:37Z and whether it was sanctioned — the log shows only local client addresses, not an identity.
- Watch `faultline_chaos_enabled` for a re-enable; a 1 on that gauge is the leading indicator of a repeat.
- Show the product-4 `price: null` record (E17) to the shop data owner; the order path over a null price is unexercised and its behavior is unknown.

## Gaps

1. **Pre-start blindness.** The log begins at 12:15:33.570Z with no rotated backups; telemetry before the process start does not exist. If the reporter's "noise" predates it, this investigation cannot see it. The complaint carries no timestamp, so the tie to the chaos window is by elimination — it is the only anomaly in the observable history — not by matched times. The judge required this to be stated as a gap rather than claimed as evidence.
2. **Operator identity.** Who toggled the switch is outside the surface contract; the log shows only `127.0.0.1` client ports.
3. **Unlensed classes.** load-saturation, third-party, and data-db had no dedicated lens. Saturation signals were checked in passing (sub-13 ms durations, stable RSS, continuous uptime); the lab declares no database and no third-party dependency (docs/lab.md), so those classes are out of scope by contract rather than verified empty.
