---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500
  trigger: "manual — /konan human report; complaint object: source=human, fingerprint=human-1794772456, labels.alertname=human-report (no severity stated), startsAt=2026-11-15T19:54:16Z; investigation start 2026-11-15T19:54:22Z, trigger latency 6 s"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-15T19:54:22Z
  concluded: 2026-11-15T19:59:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product page handler divides by the product's units_in_stock; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500 'internal server error', while every other product page succeeds."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product page handler (get_product) computes turnover_score as units_ordered / units_in_stock; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500; other product ids are not affected."
    incident_class: software-defect
    state: validated
    evidence_for: [E4, E5, E6, E7, E8, E9, E10, E11, E12, E15, E16, E17]
    evidence_against: []
  - id: H2
    statement: "A process event (crash, restart, hang) or an internal degradation switch (chaos mode) produces the 500 responses on product pages."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3, E12, E13, E14]
  - id: H3
    statement: "A failure at a boundary (gateway tier, dependency, partial rollout) fails a fraction of product page requests."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E12, E15]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794772473-22020 (baseline)"
    quote: |-
      {"status":"ok","uptime_seconds":29.53435462526977}
      -- HTTP 200 in 0.007918s request_id=konan-1794772473-22020
  - id: E2
    type: metric
    source: "/metrics scrape, request_id=konan-1794772474-22025 (baseline, before any investigator probe of a product page; process_uptime_seconds 29.897855458315462 in the same scrape)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:54:04.405Z"
    quote: |-
      {"ts": "2026-11-15T19:54:04.405Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:54:06.212Z (user traffic)"
    quote: |-
      {"ts": "2026-11-15T19:54:06.212Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "ce5eb9c24041", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.044, "client": "127.0.0.1:55957"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:54:07.266Z (user traffic)"
    quote: |-
      {"ts": "2026-11-15T19:54:07.266Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "60401c036a84", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.58, "client": "127.0.0.1:55958"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:54:10.415Z (user traffic)"
    quote: |-
      {"ts": "2026-11-15T19:54:10.415Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "d75e6e9c5984", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.561, "client": "127.0.0.1:55961"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:55:25.747Z (stack trimmed to its last frame, marked '...'; the local path prefix of the target's checkout is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T19:55:25.747Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794772525-22093", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:55:25.756Z"
    quote: |-
      {"ts": "2026-11-15T19:55:25.756Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772525-22093", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.512, "client": "127.0.0.1:55989"}
  - id: E9
    type: probe
    source: "/products/3, request_id=konan-1794772532-22127"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794772532-22127"}
      -- HTTP 500 in 0.003165s request_id=konan-1794772532-22127
  - id: E10
    type: probe
    source: "/products/3, request_id=konan-1794772540-22174"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794772540-22174"}
      -- HTTP 500 in 0.003657s request_id=konan-1794772540-22174
  - id: E11
    type: probe
    source: "/products, request_id=konan-1794772575-22199"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001329s request_id=konan-1794772575-22199
  - id: E12
    type: metric
    source: "/metrics scrape, request_id=konan-1794772575-22194 (all series of http_requests_total and http_exceptions_total in the scrape)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 5
      http_requests_total{method="GET",path="/metrics",status="200"} 5
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_requests_total{method="POST",path="/orders",status="201"} 1
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E13
    type: metric
    source: "/metrics scrape, request_id=konan-1794772575-22194"
    quote: "faultline_chaos_enabled 0"
  - id: E14
    type: metric
    source: "/metrics scrape, request_id=konan-1794772575-22194 (101 s after the scrape of E2)"
    quote: "process_uptime_seconds 130.86407600017264"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:55:32.661Z – 19:55:33.487Z (three consecutive request lines; the ERROR line between the second and the third is left out)"
    quote: |-
      {"ts": "2026-11-15T19:55:32.661Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772532-22127", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.419, "client": "127.0.0.1:55995"}
      {"ts": "2026-11-15T19:55:33.098Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794772533-22132", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.457, "client": "127.0.0.1:55996"}
      {"ts": "2026-11-15T19:55:33.487Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772533-22137", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.969, "client": "127.0.0.1:55997"}
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:55:26.260Z"
    quote: |-
      {"ts": "2026-11-15T19:55:26.260Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794772526-22098", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.475, "client": "127.0.0.1:55990"}
  - id: E17
    type: probe
    source: "/products/6, request_id=konan-1794772607-22205"
    quote: |-
      {"detail":"no such product: 6"}
      -- HTTP 404 in 0.001357s request_id=konan-1794772607-22205
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:54:08.312Z (the only order_created line in the log)"
    quote: |-
      {"ts": "2026-11-15T19:54:08.312Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "49e3ee714677", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5}
gaps:
  - "User impact is not shown in telemetry: all four failed requests for /products/3 carry investigator request ids (konan-*); the log holds no user request for /products/3. The link between the defect and the customers' reports rests on the symptom match and on the complaint text."
  - "The period 'this morning' is outside the telemetry: lab/logs/app.log starts at the process start, 2026-11-15T19:54:04.404Z, and no rotated backup file exists. Onset time, earlier restarts, and earlier customer failures could not be checked."
  - "The time when units_in_stock of product 3 became 0 is unknown: no order for product 3 is in the log, and the state before the process start is not observable."
  - "The order paths are not checkable: the surface is GET-only, so the behaviour of POST /orders for product 3 (stock 0) and product 4 (price null) was not tested."
  - "Only the application's own log and metrics are in the surface; a tier in front of the application, if one exists, is not observable."
  - "The journal was checked against the schema and the referential rules by hand; no automated validator ran in this session."
usage:
  model: claude-fable-5-2
  tokens: 1746650
  wall_clock_seconds: 321
---

# Product page of product 3 returns HTTP 500 on every request (division by zero stock)

## Summary

**Verdict: root cause identified — software defect, unhandled exception.** The product
page handler computes `turnover_score` as `units_ordered / units_in_stock` (E7). Product 3
("Unobtainium Ingot") has `units_in_stock` 0 (E11), so every `GET /products/3` raises an
unhandled `ZeroDivisionError` and returns HTTP 500 with the body
`{"error":"internal server error", ...}` (E8, E9, E10). The failure is deterministic per
input: 4 of 4 requests for product 3 failed, and all requests for products 1, 2, 4 and 5
succeeded (E4, E5, E6, E12, E15, E16). The process is healthy, chaos mode is off, and no
other route returns 5xx (E1, E12, E13, E14).

**Impact.** Any customer who opens the page of product 3 gets the error while its stock
is 0. **No customer request for product 3 is in the available telemetry**: all four
recorded failures are investigator probes, and the log starts at 19:54:04Z, 12 seconds
before the complaint. Confidence in the mechanism is high (reproduced, stack trace,
exception counter). Confidence that this is what the customers saw rests on the exact
symptom match with the complaint, not on a recorded customer request.

## Timeline

- 19:54:04.405Z — process start, `faultline 0.1.0 started` (E3). No earlier telemetry
  exists.
- 19:54:06Z–19:54:10Z — user traffic opens the pages of products 1, 2 and 5; all 200
  (E4, E5, E6). One order, for product 1 (E18). No order for product 3.
- 19:54:16Z — the complaint is raised (`startsAt`).
- 19:54:22Z — the investigation starts.
- 19:54:33Z–19:54:34Z — baseline: health 200 (E1); no exception series, 3 product page
  requests, all 200 (E2).
- 19:55:25.747Z — first recorded failure: unhandled `ZeroDivisionError` in `get_product`
  on an investigator probe of `/products/3` (E7, E8).
- 19:55:32Z–19:55:40Z — three more investigator probes of `/products/3`, all 500; a
  request for product 1 between two of them returns 200 (E9, E10, E15).
- 19:56:15Z — metrics: 4 × 500 and 8 × 200 on the product route, 4 `ZeroDivisionError`,
  chaos gauge 0, uptime 130.9 s with no reset (E12, E13, E14).
- No configuration, deploy, flag or chaos marker is in the log.

## Investigation

Complaint object, as synthesized by the manual trigger adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794772456",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?" },
  "startsAt": "2026-11-15T19:54:16Z"
}
```

Investigation start: 2026-11-15T19:54:22Z (trigger latency 6 s).

- **Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.
- **Baseline.** `/health` 200 with uptime 29.5 s (E1); `/metrics` with only 2xx series,
  no exception series, chaos gauge 0 (E2); log of 16 lines with one startup marker (E3)
  and user traffic on products 1, 2 and 5, all 200 (E4–E6). The baseline was clean.
- **Triage.** Three lenses ran in parallel, each blind to the others: software-defect,
  infra-process, interfaces. The software-defect lens found the deterministic failure of
  `/products/3`. The infra-process lens found no anomaly (one startup, steady uptime,
  constant RSS, chaos off). The interfaces lens found no gateway-shaped status, no change
  marker, and no probabilistic failure, and confirmed the same per-input failure.
- **Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete. The
  orchestrator added two probes to bound the spread: `/products/6` → 404 (E17) and
  `/products/abc` → 422.
- **Judge.** A fresh judge saw only the hypotheses and the quoted evidence. H1:
  validated as the cause of the recorded 500 responses. H2: invalidated. H3: invalidated.
  The judge added that user impact is not proven by the records, because all failures on
  record are investigator probes; that limit is in Gaps.
- **Conclusion.** One round. The evidence that would show user impact (a customer
  request for product 3, or records from before 19:54:04Z) is not in the surface, so a
  second round had nothing to gather.

## Hypotheses

### H1 — division by zero stock in the product page handler (validated)

The stack trace ends in `get_product`, at
`"turnover_score": units_ordered / product["units_in_stock"]` (E7), on a request for
`/products/3` (E8). The product list shows `units_in_stock` 0 for product 3 only (E11).
The prediction was: every request for product 3 fails, every other id does not. It held:
4 of 4 requests for product 3 returned 500 with `ZeroDivisionError` (E8, E9, E10, E12,
E15); products 1, 2, 4 and 5 returned 200, from users and from probes (E4, E5, E6, E15,
E16); an unknown id returned 404, not 500 (E17). The exception counter equals the 500
counter, 4 and 4, with one exception type (E12). No evidence contradicts the mechanism.

### H2 — process event or degradation switch (invalidated)

The log holds one startup marker (E3). Uptime rose by 101 s between two scrapes 101 s
apart (E2 source note, E14), and health stayed 200 (E1), so the process did not restart
or hang. The chaos gauge is 0 (E13), and the log holds no chaos event. The 500 responses
are on one route, one input and one exception type (E12), not spread. The state before
19:54:04Z is not observable.

### H3 — boundary or probabilistic failure (invalidated)

No 502, 503 or 504 status exists (E12). The failures are not a fraction: product 3 fails
4 of 4, other inputs fail 0 times (E12, E15). The error body names an exception of the
application's own code (E9, E10).

## Safe next steps

- Search the log store that covers this morning (outside this surface) for user
  requests to `/products/3` and for `ZeroDivisionError`, to confirm the link with the
  customers' reports and to date the onset.
- Ask support which product page the customers opened.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the
  `status="500"` series of `/products/{product_id}` for growth from user traffic.
- Hand the stack trace of E7 (`shop.py`, line 64, `get_product`) to the owner of the
  service.

## Gaps

- **User impact is not shown in telemetry.** All four failed requests for `/products/3`
  are investigator probes. User traffic in the window opened products 1, 2 and 5 only.
  The link to the customers' reports is the symptom match.
- **"This morning" is outside the telemetry.** The log starts at the process start,
  19:54:04.404Z, and no rotated backup exists. Onset, earlier restarts and earlier
  customer failures could not be checked.
- **When the stock of product 3 became 0 is unknown.** The log holds one order, for
  product 1 (E18); the state before the process start is not observable.
- **Order paths were not tested.** The surface is GET-only. `POST /orders` for product 3
  (stock 0) and for product 4 (`price` null, E11) could not be checked.
- **Only the application is observable.** A tier in front of it, if one exists, is not in
  the surface.
- **No automated validation.** The journal was checked by hand against the schema and
  the referential rules (references resolve, root cause points at a validated
  hypothesis, cause id in its class, wall clock = concluded − started).
