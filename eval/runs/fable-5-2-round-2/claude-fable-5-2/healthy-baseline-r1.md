---
konan_journal: 2
investigation:
  id: 2026-11-15-handover-check
  trigger: >-
    manual — /konan human report. Complaint object:
    {"source": "human", "fingerprint": "human-1794770261",
    "labels": {"alertname": "human-report"},
    "annotations": {"summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."},
    "startsAt": "2026-11-15T19:17:41Z"}.
    Investigation start 2026-11-15T19:17:56Z; trigger latency 15 s. No severity stated by the reporter.
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-15T19:17:56Z
  concluded: 2026-11-15T19:22:28Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: >-
      There is an active incident with user impact now: the product-detail read
      GET /products/{id} raises an unhandled ZeroDivisionError for a product with zero
      units in stock, and end users are failing on it.
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8, E9, E10]
    evidence_against: [E2, E5, E6]
  - id: H2
    statement: >-
      The service process crashed or was restarted abnormally shortly before the check
      (a process-lifecycle incident): it was 30 seconds old at the first probe.
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E4]
    evidence_against: [E3, E11, E12]
latent_findings:
  - statement: >-
      GET /products/3 returns HTTP 500 with an unhandled ZeroDivisionError: the
      product-detail handler divides by units_in_stock, and product 3 has
      units_in_stock 0. Deterministic for that input by the stack; triggered only by
      the investigator's probe konan-1794770364-19645, never by end-user traffic in
      the observed window.
    evidence: [E7, E8, E9, E10]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794770277-19480, 2026-11-15T19:17:57Z"
    quote: |-
      {"status":"ok","uptime_seconds":30.51940208300948}
      -- HTTP 200 in 0.001657s request_id=konan-1794770277-19480
  - id: E2
    type: metric
    source: "/metrics, request id konan-1794770277-19485, 2026-11-15T19:17:57Z (baseline scrape, before any investigator probe of a business path)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E3
    type: metric
    source: "/metrics, request id konan-1794770277-19485, 2026-11-15T19:17:57Z (baseline scrape)"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 30.998817957937717
      process_max_rss_bytes 47382528
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:17:26.641Z (first lines of the file; no backup log files exist)"
    quote: |-
      {"ts": "2026-11-15T19:17:26.641Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [19377]"}
      {"ts": "2026-11-15T19:17:26.641Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:17:28.445Z, 19:17:29.499Z, 19:17:35.697Z (every product-detail access line with an end-user request id in the file)"
    quote: |-
      {"ts": "2026-11-15T19:17:28.445Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "f82a32f554db", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.028}
      {"ts": "2026-11-15T19:17:29.499Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "a784d7834ba0", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.983}
      {"ts": "2026-11-15T19:17:35.697Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "1df4a30a8914", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.49}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:17:31.554Z, 19:17:32.606Z, 19:17:34.659Z (end-user order traffic)"
    quote: |-
      {"ts": "2026-11-15T19:17:31.554Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "2ae008acc9d9", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.914}
      {"ts": "2026-11-15T19:17:32.606Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b58c66c006c6", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.299}
      {"ts": "2026-11-15T19:17:34.659Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "b6044a2323b9", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.855}
  - id: E7
    type: probe
    source: "/products, request id konan-1794770362-19630, 2026-11-15T19:19:22Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001387s request_id=konan-1794770362-19630
  - id: E8
    type: probe
    source: "/products/3, request id konan-1794770364-19645, 2026-11-15T19:19:24Z"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794770364-19645"}
      -- HTTP 500 in 0.009877s request_id=konan-1794770364-19645
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:19:24.289Z (stack trimmed to its last frame; the local path prefix of the target's checkout is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T19:19:24.289Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794770364-19645", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "[...] File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E10
    type: metric
    source: "/metrics, request id konan-1794770370-19657, 2026-11-15T19:19:30Z (final scrape)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
      http_exceptions_total{type="ZeroDivisionError"} 1
  - id: E11
    type: metric
    source: "/metrics, request id konan-1794770370-19657, 2026-11-15T19:19:30Z (final scrape)"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 124.1604064158164
      process_max_rss_bytes 47382528
  - id: E12
    type: probe
    source: "/health, request id konan-1794770371-19662, 2026-11-15T19:19:31Z"
    quote: |-
      {"status":"ok","uptime_seconds":124.62402070779353}
      -- HTTP 200 in 0.001380s request_id=konan-1794770371-19662
  - id: E13
    type: probe
    source: "/products/4, request id konan-1794770363-19640, 2026-11-15T19:19:23Z"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001366s request_id=konan-1794770363-19640
  - id: E14
    type: probe
    source: "/orders, request id konan-1794770363-19635, 2026-11-15T19:19:23Z"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:17:31.553+00:00"},{"id":2,"product_id":2,"quantity":2,"total_price":46.0,"created_at":"2026-11-15T19:17:32.605+00:00"}]
      -- HTTP 200 in 0.001289s request_id=konan-1794770363-19635
  - id: E15
    type: probe
    source: "/orders/1, request id konan-1794770364-19650, 2026-11-15T19:19:24Z"
    quote: |-
      {"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:17:31.553+00:00"}
      -- HTTP 200 in 0.001685s request_id=konan-1794770364-19650
gaps:
  - "No telemetry exists before 2026-11-15T19:17:26.641Z: the log file starts at the startup line and has no backup files, so a first start cannot be told from a restart after a crash (H2 stays inconclusive). The record that would settle it, a supervisor or host record for a predecessor process, is outside the surface contract."
  - "The observation window is short: about 2 minutes of process life and 9 end-user requests, the last at 19:17:35.697Z. A slow memory leak, a gradual latency rise, or a low-rate intermittent failure would not show yet."
  - "Write paths could not be exercised: the probe is GET-only. In particular, an order for product 4 (price null in the catalog) or for product 3 (zero stock) is untested; only the two end-user orders for products 1 and 2 were observed."
  - "No load, third-party, or database lens exists in this skill, and the lab has no real database or external dependency; those classes were checked only as far as the three available lenses and the metrics reach."
usage:
  model: claude-fable-5-2
  tokens: 1348793
  wall_clock_seconds: 272
---

# Handover check of the shop service: no active incident, one latent defect on a product read

## Summary

**No active incident.** At the handover check the service was healthy on every surface an
end user had touched: all 9 end-user requests since process start returned 200 or 201
(E2, E5, E6), the exception counter had no series (E2), the degradation switch was off
(E3, E11), health was green and the business reads answered correctly (E1, E12, E14,
E15). Confidence in "no user impact in the observed window" is high; the window itself
is short (see Gaps).

One **latent defect** rides along: `GET /products/3` fails with HTTP 500 and an unhandled
`ZeroDivisionError`, because the product-detail handler divides by `units_in_stock` and
product 3 has zero stock (E7, E8, E9). Only the investigator's own probe triggered it
(E10 shows exactly one 500, which that probe accounts for); no end user requested that
product (E5). It will fail for any user who opens that product.

One open question: the process was only 30 seconds old at the first probe (E1, E4).
Nothing shows an abnormal start, and nothing can rule out a restart, because no telemetry
exists before the startup line.

## Timeline

- 19:17:26.641Z — server process 19377 starts; startup event "faultline 0.1.0 started" (E4). The log file begins here.
- 19:17:27–19:17:35Z — 9 end-user requests, all 200 or 201: health, product list, product details 1, 2 and 5, two orders, order list (E5, E6, E2).
- 19:17:41Z — the complaint is raised (`startsAt`).
- 19:17:56Z — the investigation starts (trigger latency 15 s).
- 19:17:57Z — baseline: health 200 with uptime 30.5 s (E1); counters show only 200 and 201, no exception series, degradation switch 0, peak RSS 47382528 bytes (E2, E3).
- 19:18:29–19:18:47Z — three triage lenses take their own samples; no anomaly.
- 19:19:22–19:19:24Z — business reads by the investigator: product list 200 (E7), order list 200 (E14), product 4 200 (E13), order 1 200 (E15).
- 19:19:24.289Z — investigator probe of `/products/3` raises `ZeroDivisionError`, HTTP 500 (E8, E9).
- 19:19:30Z — final scrape: one 500 and one `ZeroDivisionError`, both from that probe; uptime 124.2 s, peak RSS unchanged, degradation switch 0 (E10, E11); health 200 (E12).

No configuration, deploy, or flag-change marker appears in the log; the only lifecycle
marker is the single startup line (E4).

## Investigation

- **Baseline.** Health, metrics, and the full log (one file, no backups) were read
  before anything else (E1–E6). Clean: no error status, no exception, no WARNING or
  ERROR line.
- **Triage.** The complaint is vague, so all three lenses ran in parallel and blind to
  each other: infra-process, interfaces, software-defect. Each reported no anomaly in
  its domain. Two lenses noted catalog entries that no request had touched: product 3
  with zero stock and product 4 with a null price.
- **Business surface check.** The orchestrator probed the untouched read paths
  (`/products/3`, `/products/4`, `/orders/1`). `/products/3` failed (E8); the others
  answered 200 (E13, E15). The evidence for the failure was deterministic and complete,
  so no deep-dive agent ran.
- **Judge.** One fresh judge received H1 and H2 with the quoted evidence only. Verdicts:
  H1 invalidated (the defect is real, the user-impact claim fails), H2 inconclusive
  (settling evidence: a supervisor or host record for a predecessor of process 19377).
  The judge also caught a count error in the working notes: 9 end-user requests, not 10;
  this journal carries the corrected count. In the judge's packet E6 was a description of
  the end-user access lines; in this ledger E6 quotes the order lines themselves.
- **Conclusion.** The settling evidence for H2 is outside the surface contract, so the
  investigation ended after one round with the honest state.

## Hypotheses

### H1 — active incident: users fail on the product-detail read (software-defect) — invalidated

The defect half holds: product 3 has `units_in_stock` 0 (E7), the read of `/products/3`
returns 500 with `ZeroDivisionError` (E8), and the stack ends at the division by
`units_in_stock` in the product-detail handler (E9). The incident half does not: the
only failing request carries the investigator's request id (E8, E9); before that probe
the counters held only 200 and 201 and no exception series (E2); the three end-user
product-detail requests went to products 1, 2 and 5 and all succeeded (E5); end-user
orders succeeded (E6). The final counters show exactly one 500 and one exception (E10),
which the probe accounts for. The defect is recorded as a latent finding.

### H2 — abnormal crash or restart shortly before the check (infra-process) — inconclusive

For: the process was 30.5 s old at the first probe (E1), and the log starts with the
startup line at 19:17:26.641Z (E4). Against: uptime rises in step with the clock from
30.5 s to 124.6 s with one startup event, so there was no restart inside the window
(E3, E11, E12); peak memory is flat and the degradation switch is off (E3, E11). None
of the evidence against reaches before 19:17:26Z, and a first start fits the evidence
for equally well. What would settle it: a supervisor or host record that shows whether
a predecessor process existed and how it exited.

## Safe next steps

- Read the supervisor or host record for the start at 19:17:26Z to learn whether it was
  a planned start or a restart (settles H2).
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the 500 series of
  `/products/{product_id}`: a count above 1, or an `unhandled_exception` log line with a
  request id that does not start with `konan-`, means end users now hit the latent defect.
- Report the latent defect to the owners of the service with E7–E9.
- Repeat the health, metrics and log read later in the shift; the first two minutes of a
  process cannot show slow trends.

## Gaps

- **Nothing before the start.** The log begins at 19:17:26.641Z and has no backup files.
  A first start and a restart after a crash look the same from here; H2 stays
  inconclusive.
- **A short window.** About two minutes of process life and 9 end-user requests. A slow
  leak, a gradual latency rise, or a rare intermittent failure would not show yet.
- **Write paths.** The probe is GET-only. An order for product 4 (null price) or product
  3 (zero stock) is untested; the null price is an observation in the catalog (E7, E13),
  not a demonstrated failure.
- **Classes without a lens.** Load, third-party and database causes have no lens in this
  skill, and the lab has no real database or external dependency.
