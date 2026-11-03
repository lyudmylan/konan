---
konan_journal: 2
investigation:
  id: 2026-11-03-handover-chaos-window
  trigger: "manual (/konan human profile; fingerprint human-1793707637; startsAt 2026-11-03T12:07:17Z)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: "2026-11-03T12:07:59Z"
  concluded: "2026-11-03T12:13:11Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's internal chaos degradation switch, enabled at 2026-11-03T12:06:28Z with failure_rate 0.6 and error_status 503, injected 503 responses into live shop traffic until it was disabled at 12:06:34Z; it is off now and traffic recovered immediately."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "The chaos degradation switch, enabled at 12:06:28.004Z by POST /chaos/enable (request 5b3e79b107b1, failure_rate 0.6, error_status 503) and disabled at 12:06:34.356Z by request 24aeec203cec, injected every 503 in the process's lifetime: all four 503s fall inside that window and each carries a chaos_failure log marker with a matching request_id."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E15, E17]
    evidence_against: []
  - id: H2
    statement: "A defect in faultline's own code (an unhandled exception, or a data-dependent failure on specific inputs) caused the 503 responses."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E6, E8, E12, E13, E16, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:24.128Z"
    quote: |-
      {"ts": "2026-11-03T12:06:24.128Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:28.004Z"
    quote: |-
      {"ts": "2026-11-03T12:06:28.004Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "5b3e79b107b1", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:29.066Z"
    quote: |-
      {"ts": "2026-11-03T12:06:29.066Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5f3585098621", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:29.066Z"
    quote: |-
      {"ts": "2026-11-03T12:06:29.066Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "5f3585098621", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.281, "client": "127.0.0.1:50499"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:30.125Z"
    quote: |-
      {"ts": "2026-11-03T12:06:30.125Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "71b1d4e79d47", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:32.241Z"
    quote: |-
      {"ts": "2026-11-03T12:06:32.241Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "b29480646db6", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:32.241Z"
    quote: |-
      {"ts": "2026-11-03T12:06:32.241Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "b29480646db6", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.314, "client": "127.0.0.1:50502"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:33.299Z"
    quote: |-
      {"ts": "2026-11-03T12:06:33.299Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "54242d21b1b1", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:31.180Z"
    quote: |-
      {"ts": "2026-11-03T12:06:31.180Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a312f3df4eb1", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.749, "client": "127.0.0.1:50501"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:34.356Z"
    quote: |-
      {"ts": "2026-11-03T12:06:34.356Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "24aeec203cec", "event": "chaos_disabled"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:54.418Z"
    quote: |-
      {"ts": "2026-11-03T12:06:54.418Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "80421f170e8f", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.723, "client": "127.0.0.1:50505"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:56.536Z"
    quote: |-
      {"ts": "2026-11-03T12:06:56.536Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b007037b4691", "event": "order_created", "order_id": 1, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:06:56.537Z"
    quote: |-
      {"ts": "2026-11-03T12:06:56.537Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b007037b4691", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.701, "client": "127.0.0.1:50507"}
  - id: E14
    type: probe
    source: "scripts/probe.sh /health @ 2026-11-03T12:08:00Z, request_id=konan-1793707680-32772"
    quote: |-
      {"status":"ok","uptime_seconds":96.12727308296598}
      -- HTTP 200 in 0.002256s request_id=konan-1793707680-32772
  - id: E15
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-03T12:13:02Z, request_id=konan-1793707982-32889"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E16
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-03T12:13:02Z, request_id=konan-1793707982-32889"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E17
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-03T12:13:02Z, request_id=konan-1793707982-32889"
    quote: |-
      faultline_chaos_enabled 0
  - id: E18
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-03T12:13:02Z, request_id=konan-1793707982-32889"
    quote: |-
      process_uptime_seconds 398.88040345790796
  - id: E19
    type: probe
    source: "scripts/probe.sh /products @ 2026-11-03T12:10:21Z, request_id=konan-1793707821-32853"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001370s request_id=konan-1793707821-32853
gaps:
  - "The actor behind the chaos enable and disable requests (request_ids 5b3e79b107b1 and 24aeec203cec, client 127.0.0.1) cannot be established from the allowed telemetry surface; the log carries no identity fields and the operator endpoints are outside the probe allowlist."
  - "No telemetry exists before process start at 2026-11-03T12:06:24Z (single log file, no rotated backups, counters start at startup); noise earlier than that moment is out of this surface's reach."
usage:
  model: claude-fable-5
  tokens: 1205295
  wall_clock_seconds: 312
---

# Handover check: the earlier 503 noise was a chaos degradation-switch window, off since 12:06:34Z

## Summary

Root cause identified; nothing is wrong with the shop service right now. The "noise earlier" was a 6.4-second window, 2026-11-03T12:06:28.004Z to 12:06:34.356Z, in which faultline's internal chaos degradation switch was on (failure_rate 0.6, error_status 503) and injected 503 responses into live traffic (E2, E10). Four user requests failed — two `GET /products`, one `GET /products/2`, one `POST /orders`, so one real order attempt was lost in that window (E7) — and each failure carries an explicit `chaos_failure` log marker with the same request_id (E3, E5, E6, E8). The switch has stayed off (E17), all user traffic after the window succeeded, including an order for the same product that had failed (E12, E13), and no unhandled exception was recorded at any point (E16). Confidence is high: the log covers the whole process lifetime and every 5xx in it is inside the window and chaos-tagged.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 12:06:24.128Z | faultline 0.1.0 starts; log and counters begin here | E1 |
| 12:06:28.004Z | Config-change marker: chaos mode enabled (failure_rate 0.6, error_status 503, request 5b3e79b107b1) | E2 |
| 12:06:29.066Z | `GET /products` → 503, chaos-tagged | E3, E4 |
| 12:06:30.125Z | `GET /products/2` → 503, chaos-tagged | E5 |
| 12:06:31.180Z | `GET /products/1` → 200 (one request passes inside the window, as a 0.6 rate predicts) | E9 |
| 12:06:32.241Z | `POST /orders` → 503, chaos-tagged — a lost order attempt | E6, E7 |
| 12:06:33.299Z | `GET /products` → 503, chaos-tagged | E8 |
| 12:06:34.356Z | Config-change marker: chaos mode disabled (request 24aeec203cec) | E10 |
| 12:06:54–12:06:58Z | Five user requests, all succeed; order_id 1 created for product 2 | E11, E12, E13 |
| 12:08:00Z | Investigation baseline: health ok, uptime 96 s | E14 |
| 12:13:02Z | Final check: chaos gauge 0, no new 5xx counters, uptime 399 s (no restart) | E15, E17, E18 |

## Investigation

Trigger — the complaint object, verbatim, from the `/konan` manual adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1793707637",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-11-03T12:07:17Z"
}
```

Investigation start 2026-11-03T12:07:59Z; trigger latency 42 s. The reporter stated no severity, so none was recorded.

- **Baseline** (12:08:00Z): `/health` 200 with uptime 96 s (E14); `/metrics` showed `faultline_chaos_enabled 0`, no `http_exceptions_total` series, and four historical 503 counters; the full log `lab/logs/app.log` (30 lines, no rotated backups) spans the whole process lifetime from the startup marker (E1).
- **Triage**: the complaint is vague, so all three lenses ran in parallel — software-defect, infra-process, interfaces. All three converged on the same chaos window and found no other anomaly: no restart, flat memory, sub-11 ms latencies, no exception events, and full recovery after 12:06:34Z.
- **Deep-dive**: skipped. The triage evidence was deterministic and complete — every 503 is chaos-tagged by request_id in a log that covers the entire process lifetime — so the hypotheses went straight to the judge.
- **Judge**: validated H1 and invalidated H2, with three narrowing demands: (1) produce `chaos_failure` lines for the two 503s not yet cited — produced, E5 and E8, so all four 503s are chaos-tagged; (2) do not claim "an operator" enabled the switch, only the request that did — the hypothesis statement names request 5b3e79b107b1 and the actor is recorded as a gap; (3) re-read the switch state before concluding — re-read at 12:13:02Z, still 0, no new 5xx (E15, E17).

## Hypotheses

### H1 — chaos degradation switch (infra-process) — validated

The switch was enabled at 12:06:28.004Z with failure_rate 0.6 and error_status 503 (E2) and disabled at 12:06:34.356Z (E10). All four 503s of the process's lifetime fall inside that window, and each carries a `chaos_failure` marker with the same request_id as its access line (E3+E4, E5, E6+E7, E8). One request inside the window passed (E9), which fits a 0.6 failure rate and does not fit a hard outage. The metric counters match the log exactly (E15). After the disable marker, every request succeeded (E11, E12, E13) and the gauge reads 0 at conclusion time (E17). Nothing cited weighs against it.

### H2 — defect in the target's own code (software-defect) — invalidated

No unhandled exception was ever counted (E16), and the full log holds no `unhandled_exception` event and no stack trace. The failures hit three different routes at random rather than one route on specific inputs (E3, E5, E6, E8). The same inputs that failed succeeded once the switch was off: an order for product 2 was created (E12, E13) and the product listing answers 200 now (E19). A data-dependent code defect predicts repeatable per-input failures; the telemetry shows the opposite.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Ask the team who or what sent `POST /chaos/enable` at 12:06:28Z (request 5b3e79b107b1, client 127.0.0.1) and whether that chaos exercise was announced. This is an audit question; the telemetry surface cannot answer it.
- Watch `faultline_chaos_enabled` at the next handover; a flip back to 1 reproduces the same user impact immediately.
- Note for the catalog owners, unrelated to this incident: product 4 ("Mystery Box") lists `price: null` and product 3 has zero stock (E19). Verify this catalog data is intended; no request involving these products failed in this window.

## Gaps

- **Actor attribution.** The chaos enable and disable requests carry request_ids 5b3e79b107b1 and 24aeec203cec from client 127.0.0.1, with no identity fields in the log. The operator endpoints are outside the investigator's probe allowlist, so who flipped the switch cannot be established from this surface.
- **History before 12:06:24Z.** The process started at 12:06:24.128Z (E1); the single log file begins there, there are no rotated backups, and the metric counters reset at startup. If the reporter's "noise earlier" refers to anything before that moment, no telemetry of it exists on this surface.
