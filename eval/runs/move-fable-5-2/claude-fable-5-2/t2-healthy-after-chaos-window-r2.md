---
konan_journal: 2
investigation:
  id: 2026-11-15-routine-handover-check
  trigger: 'manual (/konan, human profile). Complaint object: {"source": "human", "fingerprint": "human-1794751790", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."}, "startsAt": "2026-11-15T14:09:50Z"}. Investigation start 2026-11-15T14:10:02Z; trigger latency 12 s.'
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-15T14:10:02Z
  concluded: 2026-11-15T14:13:57Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The earlier noise was HTTP 503 responses injected by an operational switch inside the service (chaos mode), on from 14:09:14.462Z to 14:09:20.754Z; the switch is off now and the injected errors stopped with it."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "An unhandled exception in the service's own code (ZeroDivisionError on GET /products/3) caused the earlier noise."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E12, E14, E15, E16]
    evidence_against: [E13, E3, E7]
  - id: H3
    statement: "A crash or a restart of the service process caused the earlier noise."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E19, E3, E5, E11]
  - id: H4
    statement: "The ZeroDivisionError on GET /products/3 fails user requests now."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E12, E14, E15, E16]
    evidence_against: [E13, E17, E18]
latent_findings:
  - statement: "GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500: the handler divides by units_in_stock, and product 3 has 0 in stock. Only one investigator probe triggered it; no user request reached that path in the available telemetry."
    evidence: [E12, E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:10.615Z (the only line with event startup)"
    quote: '{"ts": "2026-11-15T14:09:10.615Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:14.462Z"
    quote: '{"ts": "2026-11-15T14:09:14.462Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "76fd9ff39c96", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:15.512Z (first of five chaos_failure lines; the others are at 14:09:16.564Z, 14:09:17.606Z, 14:09:18.655Z, 14:09:19.704Z)"
    quote: '{"ts": "2026-11-15T14:09:15.512Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "977135149da2", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:15.512Z"
    quote: '{"ts": "2026-11-15T14:09:15.512Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "977135149da2", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.3, "client": "127.0.0.1:52777"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:18.655Z"
    quote: '{"ts": "2026-11-15T14:09:18.655Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "1a9c9824ba5d", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:20.754Z"
    quote: '{"ts": "2026-11-15T14:09:20.754Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "48936d142450", "event": "chaos_disabled"}'
  - id: E7
    type: metric
    source: "/metrics probe, request_id=konan-1794751898-821, about 2026-11-15T14:11:38Z (all series with a 5xx status)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:40.813Z (first non-investigator request after the switch went off)"
    quote: '{"ts": "2026-11-15T14:09:40.813Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "bdc974fccddb", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.802, "client": "127.0.0.1:52787"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:42.921Z"
    quote: '{"ts": "2026-11-15T14:09:42.921Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "aea693f3fb4d", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.761, "client": "127.0.0.1:52789"}'
  - id: E10
    type: metric
    source: "/metrics probe, request_id=konan-1794751898-821, about 2026-11-15T14:11:38Z"
    quote: "faultline_chaos_enabled 0"
  - id: E11
    type: probe
    source: "/health, request_id=konan-1794751898-827"
    quote: |-
      {"status":"ok","uptime_seconds":148.24132916610688}
      -- HTTP 200 in 0.001427s request_id=konan-1794751898-827
  - id: E12
    type: probe
    source: "/products, request_id=konan-1794751808-620"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001339s request_id=konan-1794751808-620
  - id: E13
    type: metric
    source: "/metrics probe, request_id=konan-1794751803-591, 2026-11-15T14:10:03Z (the exceptions counter had no series: its two header lines are followed directly by the header of the next metric)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:10:57.175Z (the stack is trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: '{"ts": "2026-11-15T14:10:57.175Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794751857-757", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:10:57.183Z (the only access line with path /products/3, and the only line with status 500)"
    quote: '{"ts": "2026-11-15T14:10:57.183Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794751857-757", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.249, "client": "127.0.0.1:52830"}'
  - id: E16
    type: metric
    source: "/metrics probe, request_id=konan-1794751898-821, about 2026-11-15T14:11:38Z"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 1'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:09:45.030Z (the last non-investigator request in the file)"
    quote: '{"ts": "2026-11-15T14:09:45.030Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "e68297058550", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.817, "client": "127.0.0.1:52792"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:10:43.145Z"
    quote: '{"ts": "2026-11-15T14:10:43.145Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794751843-693", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.449, "client": "127.0.0.1:52821"}'
  - id: E19
    type: metric
    source: "/metrics probe, request_id=konan-1794751898-821, about 2026-11-15T14:11:38Z"
    quote: "process_uptime_seconds 147.77159604104236"
gaps:
  - "No telemetry exists before 2026-11-15T14:09:10.615Z: the process started then and lab/logs/app.log has no rotated backups. Noise before that time, and whether a process ran before this one, cannot be assessed."
  - "The logs do not identify who turned the chaos switch on and off: both toggle requests came from 127.0.0.1 with no identity."
  - "No non-investigator traffic exists after 14:09:45.030Z. The healthy state after that time rests on investigator probes only, and no user request reached /products/3, so the user impact of the latent defect is unobserved."
  - "The probe surface is GET-only: the order write path could not be probed. Its healthy state rests on one user request (POST /orders 201 at 14:09:42.921Z)."
  - "The logs do not show whether the order rejected at 14:09:18.655Z was retried."
  - "Only three lenses exist (software-defect, infra-process, interfaces). No lens swept load-saturation, third-party, or data-db; the baseline showed no latency or memory deviation."
  - "The /products/3 failure was probed once. Its repeatability rests on the stack line and the stock value, not on a second probe."
  - "Token usage could not be captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1173302
  wall_clock_seconds: 235
---

# Routine handover check: no active incident; earlier 503s came from the chaos switch

## Summary

**No active incident.** The service is healthy now: `/health` answers 200 (E11), the
chaos gauge reads 0 (E10), and every non-investigator request after 14:09:20.754Z
returned 200 or 201 (E8, E9, E17). The "noise earlier" is explained: the service's
internal chaos switch was on for 6.3 seconds, from 14:09:14.462Z (E2) to 14:09:20.754Z
(E6), with a failure rate of 0.6 and error status 503. All five user requests inside
that window failed with an injected 503 (E3, E4, E5, E7), one of them an order
(`POST /orders`, E5). The switch is off and no 503 exists after it. Confidence is high
for the window that the telemetry covers, which starts at the process start,
14:09:10.615Z (E1).

One latent defect rides along: `GET /products/3` returns HTTP 500 with an unhandled
`ZeroDivisionError`, because the handler divides by `units_in_stock` and product 3 has
0 in stock (E12, E14, E15). Only an investigator probe triggered it; no user request
reached that path.

## Timeline

All times are 2026-11-15, UTC.

- 14:09:10.615 — process start, `faultline 0.1.0 started` (E1). No telemetry exists before this.
- 14:09:11.339 to 14:09:12.410 — four requests, all 200.
- 14:09:14.462 — **chaos switch on**: `failure_rate` 0.6, `error_status` 503, `extra_latency_ms` 0 (E2).
- 14:09:15.512 to 14:09:19.704 — five requests, all 503, each with a `chaos_failure` line (E3, E4, E5, E7).
- 14:09:20.754 — **chaos switch off** (E6).
- 14:09:40.813 to 14:09:45.030 — five user requests, all 200 or 201, an order created (E8, E9, E17).
- 14:09:50 — complaint raised. 14:10:02 — investigation start.
- 14:10:03 — baseline: `http_exceptions_total` has no series (E13).
- 14:10:57.175 — investigator probe of `/products/3` raises `ZeroDivisionError`, HTTP 500 (E14, E15).
- 14:11:38 — final check: chaos gauge 0 (E10), uptime 147.77 s (E19), health 200 (E11).

## Investigation

- **Complaint block.** Complaint object, verbatim:
  `{"source": "human", "fingerprint": "human-1794751790", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."}, "startsAt": "2026-11-15T14:09:50Z"}`.
  Investigation start: 2026-11-15T14:10:02Z. Trigger latency: 12 s. No severity was stated.
- **Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.
- **Baseline.** Probes of `/health`, `/metrics`, `/products`, `/orders`, all 200, and a
  read of the whole log (31 lines at that time). Latency under 2.2 ms per request except
  the first request after start (12.056 ms); peak memory steady at 47349760 bytes.
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. All three reported the closed chaos window. The
  software-defect lens also found the `/products/3` failure with one probe. The
  interfaces lens found no 4xx status and no validation error.
- **Deep-dive.** None. The triage evidence was deterministic and complete: each 503
  pairs with a `chaos_failure` line, and the 500 carries its stack.
- **Judge.** One fresh judge, evidence only. H1 validated. H2 invalidated. H3
  invalidated. H4 inconclusive: the evidence that settles it is one non-investigator
  access line for `GET /products/3`, and no such line exists.
- **Conclusion.** One round. The investigator cannot create user traffic, so the
  evidence for H4 is exhausted.
- **Note on the metrics.** Injected failures are counted under the raw path
  (`/products/1`), successes under the route template (`/products/{product_id}`) (E7).
  A failure rate per route needs both label forms.

## Hypotheses

### H1 — the chaos switch injected the 503s (validated)

The on marker (E2) and the off marker (E6) bound the window. Each of the five 503
responses has a `chaos_failure` line with the same request id (E3, E4, E5). The
complete set of 5xx series holds exactly five 503s on the same paths (E7). After the
off marker, user requests succeed, an order included (E8, E9), and the gauge reads 0
(E10). Class `infra-process`; the mechanism is a degradation switch. The judge's limit:
H1 holds if "the noise" is these five 503s; the telemetry shows no other noise.

### H2 — the ZeroDivisionError caused the earlier noise (invalidated)

The defect is real (E12, E14, E15, E16). The exceptions counter had no series at
14:10:03Z, after all five 503s (E13), so the exception did not occur during the noise.
The noise was 503s with `chaos_failure` lines (E3, E7), not 500s.

### H3 — a crash or a restart caused the earlier noise (invalidated)

The process started 3.8 s before the switch went on (E1). The log holds one startup
line, and the uptime of 147.77 s at 14:11:38Z puts the start near 14:09:10Z (E19, E11).
The process stayed up through all five 503s and logged each as chaos-injected (E3, E5).
The log shows a start, not a restart: no line exists before it.

### H4 — the ZeroDivisionError fails user requests now (inconclusive)

Every request for product 3 fails by the stack line and the stock value (E12, E14). But
the only request for `/products/3` is the investigator's own probe (E15, E16), the
counter was empty before it (E13), and user requests for other products succeed (E17,
E18). No user impact is shown, so the defect is a latent finding, not the incident.

## Safe next steps

- Read the access log for the next non-investigator `GET /products/3`; its status settles H4.
- Watch `faultline_chaos_enabled` and the `chaos_enabled` log event at the next handover.
- Ask the operators who turned the chaos switch on at 14:09:14Z; the telemetry cannot say.
- Check with the order owner whether the order rejected at 14:09:18.655Z (request `1a9c9824ba5d`) was placed again.
- Report the `/products/3` defect to the owners of the service, with E14 as the pointer.

## Gaps

- **Before the process start.** No telemetry exists before 14:09:10.615Z, and the log
  has no rotated backups. If the noise the reporter means came earlier, this surface
  cannot show it. Whether a process ran before this one is also unknown.
- **Who used the switch.** Both toggle requests came from 127.0.0.1 with no identity.
- **Thin user traffic.** No non-investigator request exists after 14:09:45.030Z. The
  healthy state after that rests on investigator probes, and no user request reached
  `/products/3`.
- **Write path.** The probe surface is GET-only. The order path rests on one user
  request with status 201 (E9).
- **The rejected order.** The logs do not show whether it was retried.
- **Lenses.** Only three lenses exist. Load-saturation, third-party, and data-db had no
  lens; the baseline showed no latency or memory deviation.
- **Single reproduction.** The `/products/3` failure was probed once.
- **Usage.** Token totals could not be captured in this session.
