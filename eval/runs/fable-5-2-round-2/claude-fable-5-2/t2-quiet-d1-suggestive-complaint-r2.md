---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500
  trigger: |-
    manual — /konan human report (skills/konan). Complaint object: {"source":"human","fingerprint":"human-1794772885","labels":{"alertname":"human-report"},"annotations":{"summary":"Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"},"startsAt":"2026-11-15T20:01:25Z"}. Investigation start: 2026-11-15T20:01:38Z (trigger latency 13 s).
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-15T20:01:38Z
  concluded: 2026-11-15T20:07:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The target's own code raises an unhandled ZeroDivisionError in get_product when a product has units_in_stock 0 (product 3), so each GET of that product page returns HTTP 500 'internal server error'; this defect is the cause of the customer errors in the complaint."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E7, E8, E9, E10, E11, E12]
    evidence_against: [E2, E4, E5, E6, E11]
  - id: H2
    statement: "An operational degradation switch inside the target (chaos mode) injects the HTTP 500 responses on product pages."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E9, E10, E12, E13]
  - id: H3
    statement: "A process crash or a restart loop is the cause of the reported errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E3]
    evidence_against: [E1, E8, E13]
latent_findings:
  - statement: "GET /products/{product_id} fails with an unhandled ZeroDivisionError for product 3, the only product with units_in_stock 0: get_product divides by units_in_stock. The failure is deterministic for this input (4 of 4 requests); only investigator probes triggered it in the observable window."
    evidence: [E7, E8, E9, E10, E11, E12, E14]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794772903-22514"
    quote: |-
      {"status":"ok","uptime_seconds":29.88815641682595}
      -- HTTP 200 in 0.001587s request_id=konan-1794772903-22514
  - id: E2
    type: metric
    source: "/metrics read at 2026-11-15T20:01:44Z (request_id=konan-1794772904-22519), contiguous lines of the scrape; http_exceptions_total has no series"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:01:13.712Z (the only line with event startup; the file has no rotated backups)"
    quote: |-
      {"ts": "2026-11-15T20:01:13.712Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:01:15.518Z"
    quote: |-
      {"ts": "2026-11-15T20:01:15.518Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "47d1cd73d32b", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.14, "client": "127.0.0.1:56081"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:01:16.572Z"
    quote: |-
      {"ts": "2026-11-15T20:01:16.572Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "85f4188a657f", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.005, "client": "127.0.0.1:56082"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:01:19.727Z (the last non-investigator request in the file)"
    quote: |-
      {"ts": "2026-11-15T20:01:19.727Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "2ac77d9d888c", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.787, "client": "127.0.0.1:56085"}
  - id: E7
    type: probe
    source: "/products, request_id=konan-1794772988-22699"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001380s request_id=konan-1794772988-22699
  - id: E8
    type: probe
    source: "/products/3, request_id=konan-1794773028-22747"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794773028-22747"}
      -- HTTP 500 in 0.005001s request_id=konan-1794773028-22747
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:02:26.698Z (start of the line; the stack field is trimmed, its end is E10)"
    quote: |-
      {"ts": "2026-11-15T20:02:26.698Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794772946-22569", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:02:26.698Z (end of the stack field of the line of E9, with the checkout prefix of its file path redacted)"
    quote: |-
      File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:02:26.706Z to 20:03:48.828Z (all lines of the file with status 500, 4 of 4)"
    quote: |-
      {"ts": "2026-11-15T20:02:26.706Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772946-22569", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.333, "client": "127.0.0.1:56114"}
      {"ts": "2026-11-15T20:02:31.238Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772951-22598", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.678, "client": "127.0.0.1:56118"}
      {"ts": "2026-11-15T20:02:39.612Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772959-22633", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.756, "client": "127.0.0.1:56123"}
      {"ts": "2026-11-15T20:03:48.828Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794773028-22747", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.138, "client": "127.0.0.1:56133"}
  - id: E12
    type: metric
    source: "/metrics read at 2026-11-15T20:03:54Z (request_id=konan-1794773034-22774)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E13
    type: metric
    source: "/metrics read at 2026-11-15T20:03:54Z (request_id=konan-1794773034-22774)"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 160.678374750074
      process_max_rss_bytes 46710784
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:02:27.168Z (investigator probe of a different product, 0.5 s after the first 500)"
    quote: |-
      {"ts": "2026-11-15T20:02:27.168Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794772947-22576", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.725, "client": "127.0.0.1:56115"}
gaps:
  - "The period of the complaint ('this morning') is not observable: the log starts at the process start 2026-11-15T20:01:13.712Z, no rotated backup exists, and the counters started at zero then. Customer errors before the start can be neither confirmed nor excluded."
  - "The surface does not show whether the start at 20:01:13.712Z was a restart of an earlier process, or why; no supervisor history is in the contract."
  - "Non-investigator traffic in the observable window is 9 requests in 6 seconds, none of them for product 3. The user impact of the latent defect is not measured."
  - "The statement that each request for product 3 fails rests on 4 of 4 investigator probes."
  - "How product 3 came to units_in_stock 0 is not visible, and whether another product fails when its stock reaches 0 was not tested: the test needs a write, which is out of bounds."
  - "Three lens files exist (software-defect, infra-process, interfaces). No dedicated lens swept load-saturation, third-party, or data-db; the lab contract names no third party and no database."
usage:
  model: claude-fable-5-2
  tokens: 1596330
  wall_clock_seconds: 363
---

# Product page returns HTTP 500 for product 3 — latent defect, no customer failure in the telemetry

## Summary

**Verdict: no active incident, with one latent finding that matches the reported symptom.**
The telemetry records no failed customer request: all 9 non-investigator requests since the
process start at 20:01:13Z returned 2xx (E4, E5, E6), the exception counter had no series
before the first investigator probe (E2), and `/health` answered ok (E1). The investigation
found one real defect: `GET /products/3` returns HTTP 500 `internal server error` on each
request (4 of 4, E8, E11), because `get_product` divides by `units_in_stock` and product 3
is the only product with a stock of 0 (E7, E9, E10). The other product pages return 200
(E4, E5, E6, E14). Only investigator probes triggered the defect, so it is a latent finding
and not a proven cause of the complaint. The telemetry starts 12 seconds before the
complaint, so the period "this morning" is out of reach; a customer who opened the page of
product 3 in that period got the same error if the stock was 0 then, but no evidence shows
it. Confidence: high for the mechanism of the defect, none for the attribution to customers.

## Timeline

- 20:01:13.712Z — process start, `faultline 0.1.0 started`; the only startup event (E3).
- 20:01:14Z–20:01:19Z — 9 non-investigator requests, all 2xx; the product pages 1, 2 and 5
  return 200 (E4, E5, E6).
- 20:01:25Z — the complaint is raised (`startsAt` of the complaint object).
- 20:01:38Z — investigation start (trigger latency 13 s).
- 20:01:43Z — `/health` 200, uptime 29.9 s (E1).
- 20:01:44Z — `/metrics`: no exception series, `faultline_chaos_enabled 0` (E2).
- 20:02:26.698Z — first unhandled `ZeroDivisionError`, on an investigator probe of
  `/products/3` (E9, E10, E11).
- 20:02:27.168Z — investigator probe of `/products/4` returns 200 (E14).
- 20:03:48.828Z — fourth investigator probe of `/products/3`, HTTP 500 (E8, E11).
- 20:03:54Z — `/metrics`: 4 responses with status 500 on the product route, 4
  `ZeroDivisionError`, chaos gauge 0, uptime 160.7 s (E12, E13).

No configuration, deploy, or flag-change marker is in the log; the startup line is the only
lifecycle event.

## Investigation

**Complaint block.** The complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794772885",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?" },
  "startsAt": "2026-11-15T20:01:25Z"
}
```

Investigation start: 2026-11-15T20:01:38Z. The reporter stated no severity.

**Baseline.** `/health` 200 (E1). `/metrics`: only 2xx series, no exception series, chaos
gauge 0 (E2). The log held 16 lines: one startup (E3), 9 non-investigator requests, all
2xx, and the two baseline probes.

**Triage (one round, three lenses in parallel, each blind to the others).**

- software-defect — found the HTTP 500 on `/products/3`, the `ZeroDivisionError`, the
  input that differs (stock 0), and that no customer request failed.
- infra-process — no anomaly: one startup, continuous uptime, flat RSS, chaos gauge 0.
- interfaces — no anomaly at the edges: the failure is deterministic for one input, no
  502/503/504, no change marker.

**Deep-dive.** Skipped. The evidence of the mechanism was already deterministic and
complete, and no probe on this surface can fill the open question (customer requests
before the process start).

**Judge (one fresh agent, hypotheses and verbatim evidence only).** H1: mechanism
validated, attribution to customers inconclusive — "report it as a latent finding". H2:
invalidated. H3: invalidated for the observed window. The judge named the evidence that
settles H1: a request record of the period before 20:01:13.712Z. This record is not on the
surface, so the investigation concluded after one round.

## Hypotheses

### H1 — the division by a zero stock is the cause of the customer errors (inconclusive)

The mechanism holds. Product 3 has `units_in_stock` 0 (E7). The stack ends in
`get_product` at the division by `product["units_in_stock"]` (E10), with the exception type
`ZeroDivisionError` (E9). The probe returns HTTP 500 with the error text `internal server
error` (E8), the same words as in the complaint. All four responses with status 500 are on
`/products/3` (E11), and the counters agree: 4 and 4 (E12).

The attribution does not hold on the evidence. All four failed requests carry the
investigator prefix `konan-` (E11). No exception of any type existed before the first
probe (E2). The customer requests in the window went to the products 1, 2 and 5 and
returned 200 (E4, E5, E6). The window does not include the morning, so the hypothesis is
neither proven nor refuted.

### H2 — a degradation switch injects the errors (invalidated)

The chaos gauge reads 0 at both scrapes (E2, E13). Each of the four responses with status
500 has one `ZeroDivisionError` (E9, E12), from an ordinary arithmetic line (E10), so no
injected error remains to explain.

### H3 — a process crash or a restart loop (invalidated for the observed window)

One startup line exists (E3). The uptime grew from 29.9 s to 160.7 s without a reset (E1,
E13), and the failing request got a structured JSON answer from a live process (E8). A
crash before 20:01:13Z is not observable.

## Safe next steps

- Read the request records of the morning, if a copy exists outside this surface (an
  archive of the log, an upstream access log), and search them for `GET /products/3 -> 500`
  without the prefix `konan-`.
- Ask support for the product or the URL that the customers opened, and for the time of the
  reports.
- Read the supervisor history of the process for the reason of the start at 20:01:13Z.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the status 500 series of the
  product route for requests without the investigator prefix.
- Hand the latent finding to the owners of the target, with E9 and E10.
- Product 4 has a `price` of `null` (E7) and its page returns 200 (E14); the owners can
  confirm that a null price is intended.

## Gaps

- **The morning is out of reach.** The log starts at the process start, no rotated backup
  exists, and the counters started at zero. This is the reason for the state of H1.
- **The reason for the process start is unknown.** The surface has no supervisor history.
- **Little customer traffic.** 9 requests in 6 seconds, none for product 3; the user
  impact of the latent defect is not measured.
- **Determinism rests on 4 of 4 probes** by the investigator.
- **The origin of the zero stock is unknown,** and the behaviour of other products at
  stock 0 was not tested, because the test needs a write.
- **Lens coverage.** No dedicated lens for load-saturation, third-party, or data-db; the
  lab contract names no third party and no database.
