---
konan_journal: 2
investigation:
  id: 2026-11-03-chaos-window-503s
  trigger: "manual (/konan, human profile)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: "2026-11-03T11:57:29Z"
  concluded: "2026-11-03T12:03:48Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's internal chaos switch, enabled at 2026-11-03T11:56:32Z with failure_rate 0.6 and error_status 503, injected 503 failures into end-user traffic (GET /products, POST /orders) until it was disabled at 11:56:38Z; the impact ended with the disable."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "The service's internal chaos switch was enabled at 11:56:32.404Z with failure_rate 0.6 and error_status 503, injected 503 failures into end-user traffic (GET /products at 11:56:33Z, POST /orders at 11:56:36Z), and the impact ended when the switch was disabled at 11:56:38.728Z."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E18, E19]
    evidence_against: []
  - id: H2
    statement: "A defect in the service's own code — an unhandled exception or a data-dependent failure — caused the 503 responses."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E11, E17, E13]
  - id: H3
    statement: "A process crash or restart caused the reported noise."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E15, E16, E20]
  - id: H4
    statement: "The degradation is still active now."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E12, E13, E14, E18, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:28.548Z"
    quote: >-
      {"ts": "2026-11-03T11:56:28.548Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:32.404Z"
    quote: >-
      {"ts": "2026-11-03T11:56:32.404Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "e72948f6382c", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:33.459Z"
    quote: >-
      {"ts": "2026-11-03T11:56:33.459Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "f0b9bb64776d", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:33.460Z"
    quote: >-
      {"ts": "2026-11-03T11:56:33.460Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "f0b9bb64776d", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.295, "client": "127.0.0.1:50426"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:36.620Z"
    quote: >-
      {"ts": "2026-11-03T11:56:36.620Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "efd9877071a2", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:36.620Z"
    quote: >-
      {"ts": "2026-11-03T11:56:36.620Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "efd9877071a2", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.295, "client": "127.0.0.1:50429"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:38.728Z"
    quote: >-
      {"ts": "2026-11-03T11:56:38.728Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "b344a69b960e", "event": "chaos_disabled"}
  - id: E8
    type: metric
    source: "/metrics @ 2026-11-03T11:57:42Z, probe konan-1793707062-32285"
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 1'
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-03T11:57:42Z, probe konan-1793707062-32285"
    quote: 'http_requests_total{method="POST",path="/orders",status="503"} 1'
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-03T11:57:42Z, probe konan-1793707062-32285"
    quote: "faultline_chaos_enabled 0"
  - id: E11
    type: metric
    source: "/metrics @ 2026-11-03T11:57:42Z, probe konan-1793707062-32285 — no series lines follow this header"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E12
    type: probe
    source: "/health @ 2026-11-03T11:57:41Z, request_id konan-1793707061-32280"
    quote: >-
      {"status":"ok","uptime_seconds":73.08284720801748} -- HTTP 200 in 0.002874s
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:57:00.888Z"
    quote: >-
      {"ts": "2026-11-03T11:57:00.888Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "736f2547b89b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.824, "client": "127.0.0.1:50435"}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:58.784Z"
    quote: >-
      {"ts": "2026-11-03T11:56:58.784Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "144d88d6c8be", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.257, "client": "127.0.0.1:50433"}
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-03T11:57:42Z, probe konan-1793707062-32285"
    quote: "process_uptime_seconds 73.71475316700526"
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-03T11:59:37Z, probe konan-1793707177-32422 (triage lens)"
    quote: "process_uptime_seconds 189.0"
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:56:37.675Z"
    quote: >-
      {"ts": "2026-11-03T11:56:37.675Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "724f86933dd7", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.751, "client": "127.0.0.1:50430"}
  - id: E18
    type: metric
    source: "/metrics @ 2026-11-03T12:03:05Z, probe konan-1793707385-32557"
    quote: "faultline_chaos_enabled 0"
  - id: E19
    type: metric
    source: "/metrics @ 2026-11-03T12:03:05Z, probe konan-1793707385-32557 — the only non-2xx series in the full http_requests_total set"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
  - id: E20
    type: metric
    source: "/metrics @ 2026-11-03T12:03:05Z, probe konan-1793707385-32557"
    quote: "process_uptime_seconds 397.4362046669703"
gaps:
  - "Telemetry history starts at the process startup 2026-11-03T11:56:28.548Z (E1); lab/logs/app.log has no rotated backups. If the reported 'noise earlier' happened before that time, it is outside the observable surface."
  - "The chaos enable and disable requests carry non-investigator request ids (e72948f6382c, b344a69b960e) and the surface shows the toggle actions, not the actor. Who or what operated the switch cannot be determined from the investigator's surface; the operator surface is outside the contract."
  - "The emptiness of http_exceptions_total (E11) assumes the counter increments on real unhandled exceptions; the read-only boundary forbids exercising that path to verify it."
  - "Current-state conclusions are point-in-time as of 12:03:05Z; the switch can be re-enabled at any moment through the same unstamped surface."
usage:
  model: claude-fable-5
  tokens: 1470732
  wall_clock_seconds: 379
---

# Chaos-switch window injects 503s into shop traffic, resolved before the handover check

## Summary

Root cause identified; the incident is over and the service is healthy now. faultline's
internal chaos switch was enabled at 11:56:32Z with a 60% failure rate and error status
503 (E2) and disabled six seconds later at 11:56:38Z (E7). Inside that window, 2 of the
5 end-user requests failed with chaos-injected 503s: one GET /products (E3, E4) and one
POST /orders (E5, E6). That is the full user impact — the 12:03:05Z scrape shows those
two counters unchanged at 1 and no other non-2xx series (E19). Since the disable, all
end-user traffic has succeeded, including an order creation (E13, E14), the chaos gauge
reads 0 (E18), health is 200 (E12), and the process never restarted (E1, E20).
Confidence is high: the failure lines carry explicit chaos_failure markers tied to the
failing requests by request id, and the window is bracketed by enable/disable markers.

## Timeline

- 11:56:28.548Z — process start, faultline 0.1.0 (E1).
- 11:56:32.404Z — configuration-change marker: chaos switch enabled, failure_rate 0.6,
  error_status 503, extra_latency_ms 0 (E2).
- 11:56:33.459Z — end-user GET /products fails 503, chaos-injected (E3, E4).
- 11:56:36.620Z — end-user POST /orders fails 503, chaos-injected (E5, E6).
- 11:56:37.675Z — end-user GET /products succeeds inside the window — injection is
  probabilistic, not route- or input-bound (E17).
- 11:56:38.728Z — configuration-change marker: chaos switch disabled; end of impact (E7).
- 11:56:58–11:57:02Z — end-user traffic all 200/201, order created (E14, E13).
- 11:57:14Z — human complaint raised (startsAt).
- 11:57:29Z — investigation start; trigger latency 15 s.
- 11:57:41–42Z — baseline: health 200 (E12), chaos gauge 0 (E10), the two 503 counters
  at 1 (E8, E9), no exception series (E11).
- 12:03:05Z — settling scrape: gauge still 0 (E18), 503 counters unchanged and the only
  non-2xx series (E19), uptime 397 s with no reset (E20).

## Investigation

Complaint object, verbatim, as synthesized by the /konan adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1793707033",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-11-03T11:57:14Z"
}
```

Investigation start 2026-11-03T11:57:29Z (trigger latency 15 s). Baseline captured at
11:57:41–42Z: health, full metrics scrape, complete log read (the file holds the whole
process history; no rotated backups). Triage fanned out three lenses in parallel —
infra-process, interfaces, software-defect — each with the lens file, the surface
contract, the complaint verbatim, and the baseline summary. All three converged on the
chaos window and found nothing else; the interfaces lens corrected the baseline's
impact count (the in-window traffic is unstamped end-user traffic, so impact is 2 of 5
user requests, 40%, consistent with rate 0.6). Triage evidence was deterministic and
complete, so no deep-dive round ran; four hypotheses went straight to the adversarial
judge. The judge validated H1's cause, invalidated H2–H4, and named two settling items
— the complete counter-series list and a fresh chaos-gauge reading — both delivered by
one further scrape at 12:03:05Z (E18–E20). One process note: a triage lens reported
that one of its log-filter commands included an operator-endpoint path, which the
session rules forbid; the command was not denied and was not repeated.

## Hypotheses

### H1 — chaos switch injected the failures (infra-process) — validated

The enable marker (E2) precedes the first failure by one second; both 503s carry a
chaos_failure line sharing the request id of the failing request (E3→E4, E5→E6); the
disable marker (E7) ends the window, after which the 503 counters never move (E8, E9,
E19). A success on the same route inside the window (E17) matches probabilistic
injection at rate 0.6. The judge validated the cause and asked for scope confirmation;
E19 delivered it: no other non-2xx series exists over the whole process life.

### H2 — a software defect caused the 503s (software-defect) — invalidated

Both 503s are explicitly chaos-injected (E3, E5). http_exceptions_total has no series
over the whole process life (E11), and the same routes succeed inside and after the
window with no input-bound pattern (E17, E13).

### H3 — a crash or restart caused the noise (infra-process) — invalidated

One startup marker exists (E1) and uptime climbs monotonically across three readings
spanning the investigation: 73.7 s (E15), 189.0 s (E16), 397.4 s (E20). No reset, no
second startup line.

### H4 — the degradation is still active (infra-process) — invalidated

The chaos gauge reads 0 at baseline (E10) and at the settling scrape (E18), the 503
counters are unchanged (E19), health is 200 (E12), and post-window end-user traffic
succeeds (E13, E14).

## Safe next steps

- Watch `faultline_chaos_enabled` and the two 503 counter series; any rise means a new
  window has opened.
- Re-scrape /metrics at the actual handover moment to confirm the gauge is still 0 —
  the switch sits on an unstamped surface and can be re-enabled at any time.
- If ownership of the toggle matters, consult operator-side records outside this
  surface; the telemetry shows the action, not the actor.

## Gaps

- Observability begins at process startup 11:56:28.548Z; no earlier history exists on
  the surface (no rotated logs). "Noise earlier" than that time is unverifiable here.
- The actor behind the chaos enable/disable is invisible to the investigator's surface:
  the toggle requests are unstamped by design and the operator surface is out of
  contract.
- The no-exceptions claim rests on the counter being wired correctly; exercising an
  exception path to prove it would violate the read-only boundary.
- All current-state claims are as of 12:03:05Z, point-in-time.
