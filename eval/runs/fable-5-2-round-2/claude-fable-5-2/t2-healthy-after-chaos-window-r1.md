---
konan_journal: 2
investigation:
  id: 2026-11-15-handover-check-shop
  trigger: |-
    manual — /konan human adapter. Complaint object: {"source":"human","fingerprint":"human-1794771255","labels":{"alertname":"human-report"},"annotations":{"summary":"Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."},"startsAt":"2026-11-15T19:34:15Z"}. Investigation start: 2026-11-15T19:34:27Z (trigger latency 12 s).
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-15T19:34:27Z
  concluded: 2026-11-15T19:38:09Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode) was on from 2026-11-15T19:33:38.768Z to 19:33:45.062Z and injected the 503 responses in that window; the switch is off now and it causes no failures now."
    incident_class: infra-process
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E16, E17]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code fails requests of users (non-investigator traffic) now."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E21, E22, E23, E24]
    evidence_against: [E4, E6, E8, E11, E12, E13, E15, E25, E26]
  - id: H3
    statement: "The process crashed or restarted in a loop, and that produced the earlier noise."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E2, E18, E19, E20, E27]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 with an unhandled ZeroDivisionError on every call: the product detail divides by units_in_stock, and product 3 has units_in_stock 0. Only investigator probes triggered it in the visible telemetry; no user request met it."
    evidence: [E21, E22, E23, E24, E25]
evidence:
  - id: E1
    type: probe
    source: "/health request_id=konan-1794771270-20705"
    quote: |-
      {"status":"ok","uptime_seconds":56.099823374766856}
      -- HTTP 200 in 0.002221s request_id=konan-1794771270-20705
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:34.912Z (the only startup event in the file)"
    quote: |-
      {"ts": "2026-11-15T19:33:34.912Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:38.768Z"
    quote: |-
      {"ts": "2026-11-15T19:33:38.768Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "662d775e61d6", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:41.912Z"
    quote: |-
      {"ts": "2026-11-15T19:33:41.912Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "aefba6f1ecc5", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:41.913Z"
    quote: |-
      {"ts": "2026-11-15T19:33:41.913Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "aefba6f1ecc5", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 1.063, "client": "127.0.0.1:55698"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:42.959Z"
    quote: |-
      {"ts": "2026-11-15T19:33:42.959Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "aafd1566c9ae", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:42.959Z"
    quote: |-
      {"ts": "2026-11-15T19:33:42.959Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "aafd1566c9ae", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.171, "client": "127.0.0.1:55699"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:44.010Z"
    quote: |-
      {"ts": "2026-11-15T19:33:44.010Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e2b915c1bbac", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:44.010Z"
    quote: |-
      {"ts": "2026-11-15T19:33:44.010Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "e2b915c1bbac", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.342, "client": "127.0.0.1:55700"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:45.062Z"
    quote: |-
      {"ts": "2026-11-15T19:33:45.062Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "90ca41db7e44", "event": "chaos_disabled"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:34:05.115Z"
    quote: |-
      {"ts": "2026-11-15T19:34:05.115Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "383cf7bf90a3", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.315, "client": "127.0.0.1:55704"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:34:07.217Z"
    quote: |-
      {"ts": "2026-11-15T19:34:07.217Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "2f1b0ea9667a", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.295, "client": "127.0.0.1:55706"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:34:06.153Z"
    quote: |-
      {"ts": "2026-11-15T19:34:06.153Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c204da23ea8a", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.645, "client": "127.0.0.1:55705"}
  - id: E14
    type: metric
    source: "/metrics request_id=konan-1794771271-20710 (scrape at 2026-11-15T19:34:31.504Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E15
    type: metric
    source: "/metrics request_id=konan-1794771271-20710 (same scrape; the exceptions counter has no series, before any probe of /products/3)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E16
    type: metric
    source: "/metrics request_id=konan-1794771366-20834 (scrape at 2026-11-15T19:36:06.151Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E17
    type: metric
    source: "/metrics request_id=konan-1794771366-20834 (the 503 counters; equal to their values in the scrape konan-1794771271-20710)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E18
    type: metric
    source: "/metrics request_id=konan-1794771271-20710"
    quote: "process_uptime_seconds 56.6045042918995"
  - id: E19
    type: metric
    source: "/metrics request_id=konan-1794771366-20834"
    quote: "process_uptime_seconds 151.25420741690323"
  - id: E20
    type: metric
    source: "/metrics, both scrapes (konan-1794771271-20710 and konan-1794771366-20834)"
    quote: "process_max_rss_bytes 47202304"
  - id: E21
    type: probe
    source: "/products/3 request_id=konan-1794771357-20819"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794771357-20819"}
      -- HTTP 500 in 0.009484s request_id=konan-1794771357-20819
  - id: E22
    type: probe
    source: "/products/3 request_id=konan-1794771362-20829"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794771362-20829"}
      -- HTTP 500 in 0.003999s request_id=konan-1794771362-20829
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:35:57.725Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T19:35:57.725Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794771357-20819", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E24
    type: probe
    source: "/products request_id=konan-1794771291-20728 (the entry of product 3 in the response body)"
    quote: |-
      {"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}
  - id: E25
    type: metric
    source: "/metrics request_id=konan-1794771366-20834 (after the two investigator probes of /products/3)"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E26
    type: probe
    source: "/products/4 request_id=konan-1794771358-20824"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001468s request_id=konan-1794771358-20824
  - id: E27
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:33:34.912Z (first line of the file; the color_message field is trimmed; the file has no rotated backups)"
    quote: |-
      {"ts": "2026-11-15T19:33:34.912Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [20580]"}
gaps:
  - "Telemetry starts at the process start, 2026-11-15T19:33:34.912Z, and the log has no rotated backups. Noise before that time is not visible, and the surface contract gives no launcher or supervisor record that shows an earlier process."
  - "Who turned the chaos switch on and off, and why, is not visible. The log shows only a local client address; the operator surface is outside the investigator's contract."
  - "The write path POST /orders cannot be probed (probes are GET-only). Its health after the window rests on one non-investigator request that returned 201."
  - "The order request that failed at 19:33:42.959Z (request aafd1566c9ae) created no order. The telemetry cannot show whether that user retried, so one lost order is possible."
  - "Three lenses ran (infra-process, interfaces, software-defect). The repo has no lens for load-saturation, third-party, or data-db, and the lab has no database and no third-party dependency."
  - "Token usage was not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1435386
  wall_clock_seconds: 222
---

# Handover check of the shop service: no active incident; a closed 6-second error-injection window explains the earlier noise

## Summary

**No active incident.** The service is healthy now: the health probe answers 200 (E1),
the business routes answer 200 and 201 for user traffic (E11, E12, E13), and the
error-injection switch reads 0 in two scrapes 95 seconds apart (E14, E16).

The earlier noise has a complete explanation in the telemetry. An operational switch
inside the target (chaos mode) was on for 6.3 seconds, from 19:33:38.768Z (E3) to
19:33:45.062Z (E10), with a failure rate of 0.6 and status 503. Three user requests
failed with 503 in that window, each paired with a `chaos_failure` log line of the same
request id (E4–E9). The 503 counters have not moved since (E17). Impact: three failed
user requests, one of them an order request (E7). Confidence is high for the visible
window; telemetry before the process start at 19:33:34.912Z does not exist (Gaps).

One latent finding rides along: `GET /products/3` fails with an unhandled
`ZeroDivisionError` on every call (E21–E25). Only investigator probes triggered it.

## Timeline

- 19:33:34.912Z — the process starts; one startup event, one server process (E2, E27).
- 19:33:38.768Z — chaos mode enabled: `failure_rate` 0.6, `error_status` 503 (E3). This
  is the change marker.
- 19:33:41.913Z — first failure after the marker: `GET /products/1` → 503 (E4, E5).
- 19:33:42.959Z — `POST /orders` → 503 (E6, E7).
- 19:33:44.010Z — `GET /products` → 503 (E8, E9).
- 19:33:45.062Z — chaos mode disabled (E10).
- 19:34:05.115Z to 19:34:07.217Z — user traffic succeeds again on the same routes
  (E11, E12, E13).
- 19:34:15Z — complaint raised; 19:34:27Z — investigation starts.
- 19:34:31Z — baseline: health 200 (E1), switch 0 (E14), no exception series (E15).
- 19:35:57.725Z and 19:36:02.884Z — investigator probes of `/products/3` return 500
  (E21, E22, E23).
- 19:36:06.151Z — final scrape: switch 0 (E16), 503 counters unchanged (E17), exception
  count 2, equal to the two investigator probes (E25).

## Investigation

- **Baseline.** Probes of `/health`, `/metrics`, `/products`, `/orders`, and a full read
  of `lab/logs/app.log`. Normal after the window: 200 and 201 only, durations below
  3 ms, no exception series.
- **Triage.** Three lenses ran in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the same closed chaos window and no
  active anomaly. The software-defect lens also noted that the injected 503 on the
  product route is counted under the raw path `/products/1`, not under the route
  template (E17); this is an observation, not a conclusion.
- **Follow-up probes.** Products 3 and 4 had no user traffic and unusual catalog values
  (stock 0, price null). `/products/4` answered 200 (E26). `/products/3` answered 500,
  twice (E21, E22).
- **Deep-dive.** Skipped: the evidence for H1 was deterministic and complete after
  triage.
- **Judge.** One fresh judge saw the hypotheses and the verbatim evidence only. Verdicts:
  H1 validated, H2 invalidated as worded, H3 invalidated.

## Hypotheses

### H1 — the chaos switch injected the 503 responses and is off now: validated

The enable marker (E3) and the disable marker (E10) bound the window. Each of the three
503 access lines (E5, E7, E9) shares its request id with a `chaos_failure` line (E4, E6,
E8). The 503 counters hold exactly three and did not move between the two scrapes (E17),
so no 503 lacks a chaos cause. The switch reads 0 in both scrapes (E14, E16), and the
same three routes succeed for users after the disable marker (E11, E12, E13). The class
is `infra-process`: the mechanism is an internal operational switch.

### H2 — a code defect fails user requests now: invalidated

A defect exists (E21–E24), but it does not touch users. The exception counter had no
series before the investigator probed `/products/3` (E15), and its later value of 2
equals the two investigator probes (E25). The three earlier failures carry chaos markers,
not exceptions (E4, E6, E8), and the same inputs succeed outside the window (E11, E12,
E13). `/products/4` is a passing control (E26). The defect is recorded as a latent
finding. One `unhandled_exception` log line with a request id that does not start with
`konan-` would reverse this verdict.

### H3 — a crash or a restart loop produced the noise: invalidated

The process is young (E1), which is the only support. The log holds one startup event
and one server process (E2, E27). Uptime rose from 56.6 s to 151.3 s between the two
scrapes with no reset (E18, E19), and peak memory is flat (E20). The process served and
logged each of the three 503 responses itself. The limit is the time before
19:33:34.912Z, which the telemetry does not cover (Gaps).

## Safe next steps

- Ask the operators who turned chaos mode on at 19:33:38Z and whether it was planned.
- Read `/metrics` again at the next handover: `faultline_chaos_enabled` must stay 0 and
  the 503 counters must stay at 1 each.
- Watch `http_exceptions_total{type="ZeroDivisionError"}`: growth with request ids that
  do not start with `konan-` means users reach the `/products/3` defect.
- Check with the order owner whether the failed order request `aafd1566c9ae` was
  retried.

## Gaps

- **Before the process start.** The log begins at 19:33:34.912Z and has no rotated
  backups. If the noise began earlier, this investigation did not see it. A launcher or
  supervisor record for process 20580 would settle whether an earlier process existed.
- **The operator of the switch.** The log shows the enable and disable requests from a
  local client only. The operator surface is outside the investigator's contract.
- **The write path.** Probes are GET-only, so `POST /orders` was not exercised. One user
  order succeeded after the window (E12).
- **The failed order.** Request `aafd1566c9ae` created no order. A retry by the same
  user cannot be identified in the telemetry.
- **Lens coverage.** Only the three lenses in the repo ran. The lab has no database and
  no third-party dependency, so those classes had no surface to examine.
- **Usage.** Token totals were not captured.
