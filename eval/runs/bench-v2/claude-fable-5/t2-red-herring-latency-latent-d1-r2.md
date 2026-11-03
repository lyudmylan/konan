---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-wide-slowness
  trigger: "manual (/konan human profile; fingerprint human-1793705765; startsAt 2026-11-03T11:36:06Z; trigger latency 7 s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once."
  started: 2026-11-03T11:36:13Z
  concluded: 2026-11-03T11:43:38Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operator-surface call turned on faultline's internal chaos switch at 2026-11-03T11:35:44.787Z (failure_rate 0.0, error_status 503, extra_latency_ms 1500); while it stays on, it injects a random delay bounded by 1500 ms into every business route, which users experience as shop-wide slowness."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "faultline's internal chaos switch, enabled through the operator surface at 2026-11-03T11:35:44.787Z with failure_rate 0.0 and extra_latency_ms 1500, injects a random delay bounded by 1500 ms into every business route while /health and /metrics stay fast; the switch is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E16]
    evidence_against: []
  - id: H2
    statement: "The target's own code produces the slowness or the errors (a software defect, deterministic per input)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E15, E12, E13, E3, E5]
  - id: H3
    statement: "Demand exceeds capacity: queues or resource exhaustion degrade the service under load."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E17, E8, E12, E13]
  - id: H4
    statement: "The one-time error page that users report was an error response served by the target inside the observable telemetry window (the armed 503 firing, or an unhandled exception)."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E14, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:38.853Z (first line of the only log file; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-03T11:35:38.853Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:44.787Z"
    quote: |-
      {"ts": "2026-11-03T11:35:44.787Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "c44bdb02210b", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:39.605Z"
    quote: |-
      "message": "GET /products -> 200", "request_id": "502cdaf09dc9", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.247
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:41.725Z"
    quote: |-
      "message": "POST /orders -> 201", "request_id": "c33ca4346026", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.225
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:47.073Z (first request after E2)"
    quote: |-
      "message": "GET /products -> 200", "request_id": "f515e94fa388", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 227.93
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:50.350Z"
    quote: |-
      "message": "GET /products/1 -> 200", "request_id": "303d2ff19f77", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1001.623
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:35:53.878Z"
    quote: |-
      "message": "GET /orders -> 200", "request_id": "71c399a7dabc", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 850.584
  - id: E8
    type: probe
    source: "/health, request_id konan-1793705783-31401 @ 2026-11-03T11:36:23Z"
    quote: |-
      {"status":"ok","uptime_seconds":44.38054775004275}
      -- HTTP 200 in 0.001544s request_id=konan-1793705783-31401
  - id: E9
    type: metric
    source: "/metrics, request_id konan-1793705787-31406 @ 2026-11-03T11:36:27Z"
    quote: |-
      faultline_chaos_enabled 1
  - id: E10
    type: metric
    source: "/metrics, request_id konan-1793705787-31406 @ 2026-11-03T11:36:27Z"
    quote: |-
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
  - id: E11
    type: probe
    source: "/orders, request_id konan-1793705855-31457 @ 2026-11-03T11:37:35Z"
    quote: |-
      -- HTTP 200 in 0.541827s request_id=konan-1793705855-31457
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:38:56.121Z (investigator repeat probe, same path as E13)"
    quote: |-
      "message": "GET /products/1 -> 200", "request_id": "konan-1793705935-31547", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 990.733
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:38:56.358Z (same path as E12, 237 ms later)"
    quote: |-
      "message": "GET /products/1 -> 200", "request_id": "konan-1793705936-31554", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 196.753
  - id: E14
    type: metric
    source: "/metrics, request_id konan-1793706177-31612 @ 2026-11-03T11:42:57Z (counter header with no series beneath it: the exception counter never incremented)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E15
    type: metric
    source: "/metrics, request_id konan-1793706177-31612 @ 2026-11-03T11:42:57Z (every series carries status 200 or 201; 20 requests total)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E16
    type: metric
    source: "/metrics, request_id konan-1793706177-31612 @ 2026-11-03T11:42:57Z"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 439.0270782499574
  - id: E17
    type: metric
    source: "/metrics, request_ids konan-1793705787-31406 @ 11:36:27Z and konan-1793706177-31612 @ 11:42:57Z (identical value at both scrapes; uptime 48.7 s and 439.0 s)"
    quote: |-
      process_max_rss_bytes 48463872
gaps:
  - "The telemetry window opens at process startup 2026-11-03T11:35:38.853Z and no rotated log backups exist; the complaint window ('last few minutes') is wider. An error page shown before startup, served by a component in front of the target, or delivered with a 2xx status is outside the observable surface."
  - "No per-request trace or span exists on the surface, so a slow downstream dependency loaded by other clients is not fully excluded; the 990.733 ms to 196.753 ms recovery on the same path within 237 ms (E12, E13) makes it unlikely."
  - "No client-side capture (screenshot or HAR) of the reported error page was available to tie the sighting to a target response."
usage:
  model: claude-fable-5
  tokens: 1741186
  wall_clock_seconds: 445
---

# Shop-wide slowness: internal chaos switch injects bounded latency

## Summary

**Verdict: root cause identified.** At 2026-11-03T11:35:44.787Z an operator-surface call turned on faultline's internal chaos switch with `failure_rate 0.0`, `error_status 503`, and `extra_latency_ms 1500` (E2, E10). From the first request after that marker, every business route (`/products`, `/products/{id}`, `/orders` GET and POST) slowed from 1–2 ms to 142–1002 ms (E3–E7), while `/health` and `/metrics` stayed below 2 ms (E8) — the classic green-health trap. The switch was still on at 11:42:57Z (E16) and the slowness was still reproducible then (E12). The delay is random and bounded: no observed duration reaches the 1500 ms parameter, and the same path answered in 990.733 ms and then 196.753 ms within 237 ms (E12, E13). With `failure_rate 0.0` the armed 503 fires on nothing; no error response exists anywhere in the telemetry (E14, E15), so the "error page once" part of the complaint is not corroborated inside the observable window (see Gaps). Confidence in the root cause is high: the onset is exact, the mechanism is logged, the gauge confirms the state, and all competing classes are excluded by evidence.

## Timeline

- **11:35:38.853Z** — faultline 0.1.0 starts; the telemetry window opens (E1).
- **11:35:39.605Z–11:35:41.725Z** — business traffic is fast: 1.247 ms and 2.225 ms (E3, E4).
- **11:35:44.787Z** — configuration-change marker: chaos switch enabled, `failure_rate 0.0`, `extra_latency_ms 1500` (E2); one operator POST recorded (E10).
- **11:35:47.073Z–11:35:53.878Z** — unstamped user traffic is slow: 227.93 ms, 1001.623 ms, 850.584 ms (E5, E6, E7).
- **11:36:06Z** — the human complaint is raised (trigger `startsAt`).
- **11:36:13Z** — investigation starts (trigger latency 7 s).
- **11:36:23Z–11:36:27Z** — baseline: `/health` 200 in 1.5 ms (E8); gauge `faultline_chaos_enabled 1` (E9).
- **11:37:35Z** — investigator probe `/orders` 200 in 541.827 ms — impact continues (E11).
- **11:38:56Z** — repeat probes of `/products/1`: 990.733 ms then 196.753 ms — delay is random, bounded, ongoing (E12, E13).
- **11:42:57Z** — final scrape: switch still on at uptime 439 s; zero exceptions; all request counters 200/201 (E14, E15, E16).

## Investigation

**Baseline** (11:36:13Z–11:36:27Z): `/health` green and fast but uptime only 44 s (E8); metrics showed `faultline_chaos_enabled 1` (E9), one POST to the chaos-enable path (E10), and no exception series; the single log file opened at startup with the chaos marker six seconds in (E1, E2). Business-surface probes confirmed live slowness (E11).

**Triage** (three lenses in parallel, each blind): *infra-process* found the active switch, the exact latency onset, and no lifecycle anomaly (one startup, monotonic uptime, flat RSS). *interfaces* found the same change marker, the sharp onset on business routes only, and no contract violations; it flagged that the telemetry window is narrower than the complaint window. *software-defect* found zero exceptions, zero failed requests, and non-deterministic latency on an identical input — actively excluding a code defect. The findings merged into four hypotheses (H1–H4).

**Deep-dive**: skipped — the triage evidence was already deterministic and complete for every hypothesis; the one open point (is the switch still on?) was settled with one fresh metrics scrape (E16).

**Judge** (fresh subagent, evidence-only): H1 validated; H2, H3 invalidated; H4 invalidated as scoped to the observable window. The judge ordered two record corrections, both applied: the H1 mechanism is a *random delay bounded by* 1500 ms (no observed duration reaches the parameter), and the H2 before/after citation must pair the same route (E3 vs E5, both `GET /products`).

## Hypotheses

### H1 — chaos switch injects bounded latency (infra-process) — validated

The marker (E2) sits exactly between fast (E3, E4) and slow (E5, E6, E7) traffic on the same routes. The gauge reads 1 at 11:36:27Z (E9) and still at 11:42:57Z (E16); exactly one operator call enabled it (E10). Health stays sub-2 ms while business routes are slow (E8 vs E11) — consistent with a switch that exempts operational endpoints, and inconsistent with saturation. The repeat probes (E12, E13) prove the delay is ongoing, random, and bounded below 1500 ms. Nothing contradicts the claim.

### H2 — software defect (software-defect) — invalidated

A per-input-deterministic defect cannot answer the same input in 990.733 ms and then 196.753 ms (E12, E13). The exception counter never incremented (E14) and every recorded status is 200 or 201 (E15). The same route was fast before the marker and slow after it with no code-change marker in between (E3 vs E5).

### H3 — load saturation (load-saturation) — invalidated

Twenty requests in ~440 s is near-zero demand, and peak RSS is flat across the window (E15, E17). The process answers `/health` in 1.5 ms while business routes are slow (E8), and a saturated system does not recover by a factor of five within 237 ms (E12, E13).

### H4 — the error page came from the target, in-window (infra-process) — invalidated

With `failure_rate 0.0` the armed 503 fires on nothing (E2). No log line or metric series shows any status at or above 400 (E15), and no exception was ever counted (E14). The log is complete for this process (E1). The sighting therefore did not come from the target inside the observable window; what lies before 11:35:38.853Z, in front of the target, or behind a 2xx status is recorded under Gaps, not claimed.

## Safe next steps

- Ask the operator who issued the chaos-enable call at 11:35:44.787Z (request_id `c44bdb02210b`, client `127.0.0.1:50258`) whether the switch should be on. Turning it off is remediation and stays out of scope here.
- Watch `faultline_chaos_enabled` for the flip to 0, then confirm business-route durations return to the 1–2 ms baseline.
- Request one client-side capture (screenshot plus HAR with its request id) of the reported error page; that single artifact settles whether the sighting predates the window or came from outside the target.

## Gaps

1. **The window is narrower than the complaint.** Telemetry begins at process startup (11:35:38.853Z, E1) and no rotated logs exist. The "error page once" sighting cannot be confirmed or denied for any moment before that, for any component in front of the target, or for an error page delivered with a 2xx status.
2. **No tracing.** The surface has no per-request spans, so a slow downstream dependency loaded by other clients is not mechanically excluded — only made unlikely by the instant recovery between E12 and E13.
3. **No client artifact.** No screenshot or HAR of the error page was available; H4 is judged on server-side evidence alone.
