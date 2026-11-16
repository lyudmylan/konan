---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-intermittent-503
  trigger: 'manual (/konan, human profile). Complaint object: {"source": "human", "fingerprint": "human-1794782436", "labels": {"alertname": "human-report"}, "annotations": {"summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"}, "startsAt": "2026-11-15T22:40:36Z"}. Investigation start 2026-11-15T22:40:50Z; trigger latency 14 s. No severity stated by the reporter.'
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-15T22:40:50Z
  concluded: 2026-11-15T22:44:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational error-injection switch inside the target (chaos mode, failure_rate 0.08, error_status 503) was turned on at 2026-11-15T22:40:29.184Z and was still on at the last reading; it fails a random fraction of requests with HTTP 503 while other requests on the same route succeed."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational error-injection switch inside the target (chaos mode, failure_rate 0.08, error_status 503) was turned on at 2026-11-15T22:40:29.184Z and is on at every later reading; it makes a random fraction of user requests fail with HTTP 503 while other requests on the same route succeed."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E10, E11]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception on some order inputs, and those user requests fail."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E4, E7]
    evidence_against: [E3, E8, E10, E11]
  - id: H3
    statement: "The process crashed or restarted, and users hit errors around the restart."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E12, E13]
latent_findings:
  - statement: "GET /products/3 fails every time with HTTP 500, ZeroDivisionError: the product-detail code divides by units_in_stock, and product 3 has units_in_stock 0. Only investigator probes triggered it; the exception counter had no series before those probes, and no user request in the telemetry window asked for product 3. It is not the reported incident."
    evidence: [E8, E14, E15, E16, E17, E18, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:29.184Z"
    quote: '{"ts": "2026-11-15T22:40:29.184Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "572e8c6c5eb8", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:29.184Z"
    quote: '{"ts": "2026-11-15T22:40:29.184Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "572e8c6c5eb8", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.754, "client": "127.0.0.1:57048"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:30.505Z"
    quote: '{"ts": "2026-11-15T22:40:30.505Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "d8a26d7e9c1c", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:30.505Z"
    quote: '{"ts": "2026-11-15T22:40:30.505Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "d8a26d7e9c1c", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.158, "client": "127.0.0.1:57066"}'
  - id: E5
    type: metric
    source: "/metrics probe request_id=konan-1794782451-25997, read at 2026-11-15T22:40:51.362Z"
    quote: "faultline_chaos_enabled 1"
  - id: E6
    type: metric
    source: "/metrics probe request_id=konan-1794782543-26078, read at 2026-11-15T22:42:23.173Z"
    quote: "faultline_chaos_enabled 1"
  - id: E7
    type: metric
    source: "/metrics probe request_id=konan-1794782543-26078, read at 2026-11-15T22:42:23.173Z"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 5
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E8
    type: metric
    source: "/metrics probe request_id=konan-1794782543-26078, read at 2026-11-15T22:42:23.173Z; the exception counter family has no sample line, the next family follows directly"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:24.237Z; the only startup event in the file, no rotated backups exist"
    quote: '{"ts": "2026-11-15T22:40:24.237Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:30.418Z"
    quote: '{"ts": "2026-11-15T22:40:30.418Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1fe5a7687622", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.675, "client": "127.0.0.1:57060"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:40:30.591Z"
    quote: '{"ts": "2026-11-15T22:40:30.591Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "4b8214e4d850", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.673, "client": "127.0.0.1:57072"}'
  - id: E12
    type: metric
    source: "/metrics probes request_id=konan-1794782451-25997 (read at 2026-11-15T22:40:51.362Z) and request_id=konan-1794782543-26078 (read at 2026-11-15T22:42:23.173Z), in that order"
    quote: |-
      process_uptime_seconds 27.136080791708082
      process_uptime_seconds 118.94818941690028
  - id: E13
    type: probe
    source: "/health request_id=konan-1794782450-25992"
    quote: |-
      {"status":"ok","uptime_seconds":26.64731412474066}
      -- HTTP 200 in 0.002150s request_id=konan-1794782450-25992
  - id: E14
    type: probe
    source: "/products/3 request_id=konan-1794782652-26102"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794782652-26102"}
      -- HTTP 500 in 0.009033s request_id=konan-1794782652-26102
  - id: E15
    type: probe
    source: "/products/3 request_id=konan-1794782656-26112 (the repeat)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794782656-26112"}
      -- HTTP 500 in 0.003447s request_id=konan-1794782656-26112
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:44:12.205Z; the stack field is trimmed here and quoted in E17"
    quote: '{"ts": "2026-11-15T22:44:12.205Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794782652-26102", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:44:12.205Z, the last frame of the stack field; the local path prefix of the target checkout is redacted as <checkout>"
    quote: |-
      File "<checkout>/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
      ZeroDivisionError: division by zero
  - id: E18
    type: probe
    source: "/products request_id=konan-1794782470-26014 (HTTP 200); the element of product 3, the other elements trimmed"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E19
    type: metric
    source: "/metrics probe request_id=konan-1794782660-26118, the final reading, at process_uptime_seconds 236.68048066692427"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
      faultline_chaos_enabled 1
gaps:
  - "No telemetry exists from before 2026-11-15T22:40:24.236Z: the process started then and the log has no rotated backups. The complaint says 'the last few minutes'; errors before that start could not be checked."
  - "Who turned the switch on, and why, is not visible on this surface: the call came from 127.0.0.1:57048 with an unstamped request id, and the operator surface is out of bounds for the investigator."
  - "'Works on retry' is not verified: the access log carries no request body and no user identity, so no later request could be matched to the failed one. The evidence shows only that other requests on the same route succeed."
  - "The failure rate is the configured value (0.08), not a measured one: one failure in 32 user requests after the switch-on, and user traffic stopped at 2026-11-15T22:40:30.706Z."
  - "The scope of the switch across routes is not established: the one injected failure hit POST /orders, and every GET after the switch-on returned 200 except the two investigator probes of the latent finding."
  - "POST /orders could not be probed (the surface is GET-only), so the injected failure was observed in the log, not reproduced."
  - "Triage ran the three lenses this repo has (infra-process, interfaces, software-defect). No dedicated lens covered load-saturation, third-party, or data-db; the infra-process lens read latency and memory and found them steady."
  - "Token totals were not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1575176
  wall_clock_seconds: 244
---

# Shop: intermittent 503 from an error-injection switch that is on

## Summary

**Root cause identified — it is not nothing.** An operational error-injection switch
inside the target ("chaos mode") was turned on at 22:40:29.184Z with a failure rate of
0.08 and an error status of 503 (E1, E2). 1.3 seconds later one user `POST /orders`
failed with 503, and the target itself labelled that failure as injected (E3, E4). The
switch was still on at every reading, the last one at about 22:44:20Z (E5, E6, E19). The
shape matches the complaint: failures are random and rare, and other requests on the
same route succeed right before and after (E10, E11).

Impact in the telemetry window: one failed order request out of 32 user requests after
the switch-on (one of five `POST /orders`); the failed request created no order. While
the switch stays on, about 8% of requests are configured to fail. Class
`infra-process`, cause `degradation-switch`. Confidence is high for the mechanism: the
evidence is the target's own markers, not a correlation. Confidence is low for the
period before 22:40:24Z, which no telemetry covers.

One latent defect rides along: `GET /products/3` fails every time with a
`ZeroDivisionError` (E14–E18). Only the investigator's probes triggered it; it is not
the reported incident.

## Timeline

All times UTC, 2026-11-15.

- 22:40:24.237 — the process starts; the only startup marker (E9). No telemetry before it.
- 22:40:24.972 – 22:40:27.123 — five user requests, all successful, including one order.
- 22:40:29.184 — **switch-on marker**: `chaos mode enabled`, failure_rate 0.08,
  error_status 503, extra_latency_ms 0, through `POST /chaos/enable -> 200` (E1, E2).
- 22:40:30.418 — `POST /orders -> 201` (E10).
- 22:40:30.505 — **first and only user failure**: `chaos-injected failure`, then
  `POST /orders -> 503` in 0.158 ms, same request id (E3, E4).
- 22:40:30.591 — `POST /orders -> 201` (E11).
- 22:40:30.706 — last user request in the log.
- 22:40:36 — complaint raised (`startsAt`). 22:40:50 — investigation starts.
- 22:40:50 – 22:40:51 — baseline: health 200 (E13); switch gauge at 1 (E5); uptime 27 s (E12).
- 22:42:23 — second reading: switch gauge at 1 (E6), uptime 119 s, no reset (E12), the
  exception counter has no series (E8), one 503 in total (E7).
- 22:44:12 and 22:44:16 — investigator probes of `/products/3` return 500,
  `ZeroDivisionError` (E14, E15, E16, E17) — the latent finding.
- 22:44:20 — final reading: switch gauge at 1; exception counter at 2, both from the
  investigator's probes (E19).

## Investigation

- **Trigger.** Manual, `/konan`. Complaint object as recorded in the machine core
  (`investigation.trigger`); `startsAt` 22:40:36Z, start 22:40:50Z, trigger latency 14 s.
- **Baseline.** Probes of `/health`, `/metrics`, `/products`, `/orders`, and the full
  log (52 lines at capture). Health green, latency sub-millisecond to low-millisecond,
  memory steady, uptime 27 s, one 503 on `POST /orders`, the switch gauge at 1.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the same anomaly on their own: the
  switch-on marker and the injected 503. The software-defect lens found no exception and
  no data-dependent pattern. The infra-process lens found one startup only, no uptime
  reset, and noted that the process is younger than the complaint window.
- **Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete (the
  target's own markers plus the gauge).
- **Judge.** One fresh judge on the evidence ledger only. H1 validated, H2 invalidated,
  H3 invalidated for the observed window. The judge corrected the wording of H1: the
  evidence supports "other requests on the same route succeed", not "a retry succeeds";
  "still on" holds only to the last reading; the rate is configured, not measured. The
  journal uses the corrected wording. The judge moved E9 from support of H3 to evidence
  against it.
- **After the judge.** Two disconfirming probes of product pages that no user request
  had touched: `/products/4` returned 200; `/products/3` returned 500 twice. The full
  log (63 lines at the end) holds no `unhandled_exception` event before these probes.

## Hypotheses

### H1 — error-injection switch is on (validated)

The switch-on marker (E1) and its access line (E2) share one request id. The only user
failure follows it by 1.3 s, carries the configured status 503, and is labelled
`chaos_failure` by the target under the same request id as its access line (E3, E4). Its
duration of 0.158 ms against about 0.67 ms for successful orders fits a rejection before
the order code ran. Successes on the same route sit 87 ms before and 86 ms after the
failure (E10, E11), so the switch fails a fraction of requests, not all. The gauge reads
1 at both judged readings (E5, E6), the only failing status is 503 (E7), and no
exception was counted (E8). Nothing cited speaks against it.

### H2 — code defect on some order inputs (invalidated)

E4 and E7 show only that a failure exists; they fit H1 equally. Against: the failure is
labelled as injected (E3), the exception counter had no series at 22:42:23Z (E8), and
the same route succeeded around the failure (E10, E11 — weak, since a per-input defect
allows other inputs to succeed). The log holds no `unhandled_exception` event from user
traffic. A code defect does exist on another route (the latent finding), but no user
request triggered it in the window.

### H3 — process crash or restart (invalidated for the observed window)

One startup marker only (E9). Uptime rose by 91.8 s across 91.8 s of clock time between
two readings (E12), so no reset. Health is green (E13). The 503 was served and logged by
a live process six seconds after startup. A restart before 22:40:24.236Z cannot be
tested, and it would not explain the injected failure.

### Latent finding — `/products/3` fails with a division by zero

Deterministic: two probes, two HTTP 500 responses with `ZeroDivisionError` (E14, E15).
The stack names the operation: `units_ordered / product["units_in_stock"]` in
`get_product` (E16, E17), and product 3 has `units_in_stock` 0 (E18). The exception
counter went from no series (E8) to 2 (E19), both increments from the investigator's
request ids. User requests in the window asked for products 1, 2 and 5 only.

## Safe next steps

Read-only only.

- Ask the owner of the error-injection switch whether it is on by intent, and read the
  operator-side record of the `POST /chaos/enable` call at 22:40:29.184Z.
- Keep reading `faultline_chaos_enabled` and
  `http_requests_total{path="/orders",status="503"}` to see whether the switch stays on
  and how the failure count grows with real traffic.
- Read the `chaos_failure` log events as they arrive to learn which routes the switch
  affects.
- Look for telemetry from before 22:40:24Z (a process supervisor, an earlier log) to
  cover the "last few minutes" of the complaint.
- Hand the `/products/3` finding to the owners of the target's code, with E14–E18.

## Gaps

- **Before the process start.** Nothing on the surface predates 22:40:24.236Z. The
  complaint speaks of minutes; the evidence covers the 12 seconds before it and the four
  minutes after.
- **Who and why.** The switch-on call is visible; its caller and intent are not.
- **Retry.** No request could be tied to the failed one, so "works on retry" stays the
  reporter's words. The evidence shows that other requests on the route succeed.
- **Rate.** 0.08 is the configured rate. The sample is one failure in 32 requests, and
  user traffic stopped at 22:40:30.706Z.
- **Scope.** Whether the switch also fails GET routes is not established.
- **No reproduction.** `POST /orders` is outside the GET-only probe surface.
- **Lens coverage.** Three lenses exist and ran. Load, third-party, and data-layer
  causes had no dedicated lens; latency and memory were read and were steady, and the
  lab contract lists no third-party dependency and no real database.
- **Tokens.** Not captured in this session.
