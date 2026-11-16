---
konan_journal: 2
investigation:
  id: 2026-11-15-order-500-null-price
  trigger: "manual: /konan human profile. Complaint object: source=human, fingerprint=human-1794769513, labels.alertname=human-report (no severity stated), startsAt=2026-11-15T19:05:13Z. Investigation start 2026-11-15T19:05:24Z; trigger latency 11 s."
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-15T19:05:24Z
  concluded: 2026-11-15T19:09:59Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The order-creation code raises an unhandled TypeError when the ordered product has a null price (it multiplies a None price by the quantity at shop.py line 82, create_order), so POST /orders answers HTTP 500 for that input while orders for priced products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order-creation code raises an unhandled TypeError when the ordered product has a null price: it multiplies product[\"price\"] (None) by the quantity at shop.py line 82 (create_order), and the request answers HTTP 500. One catalogue product (id 4) has a null price, so an order for it fails, while orders for priced products succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E23, E24]
    evidence_against: []
  - id: H2
    statement: "The root cause is in the data layer: the catalogue record of product 4 is corrupt or incomplete (price missing), and the order code is correct for valid data."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E10, E11]
    evidence_against: [E13]
  - id: H3
    statement: "An operational degradation switch (chaos mode) inside the target injects the 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E17, E20, E24, E1, E3, E5]
  - id: H4
    statement: "Process instability (crash, restart, hang) causes the failed orders."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E18, E19, E21, E22, E23, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:03.032Z (stack trimmed to its last frame; the checkout prefix of its file path is redacted)"
    quote: |-
      {"ts": "2026-11-15T19:05:03.032Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "c13ac4108e87", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:03.038Z"
    quote: |-
      {"ts": "2026-11-15T19:05:03.038Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "c13ac4108e87", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.723, "client": "127.0.0.1:55294"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:04.094Z (stack trimmed to its last frame; the checkout prefix of its file path is redacted)"
    quote: |-
      {"ts": "2026-11-15T19:05:04.094Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "61fcc83e1d60", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:04.098Z"
    quote: |-
      {"ts": "2026-11-15T19:05:04.098Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "61fcc83e1d60", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.24, "client": "127.0.0.1:55296"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:07.220Z (stack trimmed to its last frame; the checkout prefix of its file path is redacted)"
    quote: |-
      {"ts": "2026-11-15T19:05:07.220Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "121b4aad0d63", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:07.225Z"
    quote: |-
      {"ts": "2026-11-15T19:05:07.225Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "121b4aad0d63", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.169, "client": "127.0.0.1:55298"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:04:59.929Z"
    quote: |-
      {"ts": "2026-11-15T19:04:59.929Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "14571ea99b63", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:00.991Z"
    quote: |-
      {"ts": "2026-11-15T19:05:00.991Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "791e0a81af0f", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:05:06.160Z"
    quote: |-
      {"ts": "2026-11-15T19:05:06.160Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "7b7246460f8c", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E10
    type: probe
    source: "GET /products, request_id=konan-1794769629-18742 (2026-11-15T19:07:09Z)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001999s request_id=konan-1794769629-18742
  - id: E11
    type: probe
    source: "GET /products/4, request_id=konan-1794769630-18752 (2026-11-15T19:07:10Z)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001377s request_id=konan-1794769630-18752
  - id: E12
    type: probe
    source: "GET /orders, request_id=konan-1794769630-18747 (2026-11-15T19:07:10Z)"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T19:04:59.929+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T19:05:00.991+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:05:06.160+00:00"}]
      -- HTTP 200 in 0.001362s request_id=konan-1794769630-18747
  - id: E13
    type: probe
    source: "GET /openapi.json, request_id=konan-1794769651-18774 (2026-11-15T19:07:31Z); trimmed to the order request schema and the product response schema"
    quote: |-
      "OrderRequest":{"properties":{"product_id":{"type":"integer","title":"Product Id"},"quantity":{"type":"integer","maximum":1000.0,"minimum":1.0,"title":"Quantity"}},"type":"object","required":["product_id","quantity"],"title":"OrderRequest"}
      "responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{"type":"object","additionalProperties":true,"title":"Response Get Product Products  Product Id  Get"}}}}
  - id: E14
    type: metric
    source: "/metrics scrape, request_id=konan-1794769525-18629 (2026-11-15T19:05:25Z)"
    quote: 'http_requests_total{method="POST",path="/orders",status="500"} 3'
  - id: E15
    type: metric
    source: "/metrics scrape, request_id=konan-1794769525-18629 (2026-11-15T19:05:25Z)"
    quote: 'http_exceptions_total{type="TypeError"} 3'
  - id: E16
    type: metric
    source: "/metrics scrape, request_id=konan-1794769525-18629 (2026-11-15T19:05:25Z)"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 3'
  - id: E17
    type: metric
    source: "/metrics scrape, request_id=konan-1794769525-18629 (2026-11-15T19:05:25Z)"
    quote: 'faultline_chaos_enabled 0'
  - id: E18
    type: metric
    source: "/metrics scrape, request_id=konan-1794769525-18629 (2026-11-15T19:05:25Z)"
    quote: 'process_uptime_seconds 29.705111249815673'
  - id: E19
    type: metric
    source: "/metrics scrape, request_id=konan-1794769634-18765 (2026-11-15T19:07:14Z)"
    quote: 'process_uptime_seconds 138.89353591715917'
  - id: E20
    type: metric
    source: "/metrics scrape, request_id=konan-1794769634-18765 (2026-11-15T19:07:14Z)"
    quote: 'faultline_chaos_enabled 0'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:04:56.058Z"
    quote: |-
      {"ts": "2026-11-15T19:04:56.058Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E22
    type: probe
    source: "GET /health, request_id=konan-1794769525-18624 (2026-11-15T19:05:25Z)"
    quote: |-
      {"status":"ok","uptime_seconds":29.15603999979794}
      -- HTTP 200 in 0.004038s request_id=konan-1794769525-18624
  - id: E23
    type: metric
    source: "/metrics scrape, request_id=konan-1794769634-18765 (2026-11-15T19:07:14Z)"
    quote: 'http_exceptions_total{type="TypeError"} 3'
  - id: E24
    type: metric
    source: "/metrics scrape, request_id=konan-1794769634-18765 (2026-11-15T19:07:14Z); the complete http_requests_total series"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 3
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
gaps:
  - "The failing requests log no product id, and the investigator surface is GET-only, so no order could be placed to reproduce the failure. The link from the three failures to product 4 is an inference: the stack trace proves a None price, and product 4 is the only catalogue record with a null price."
  - "The retry part of the complaint is not observable: no log field identifies a customer or links two requests as a retry. The same exception at the same line three times is consistent with a per-input failure, not proof of retries."
  - "The surface holds no data contract for a product record (the API schema declares it as an untyped object), no record history, and no database. Whether a null price is a valid state or wrong data stays open (H2 inconclusive)."
  - "The log starts at the process start (2026-11-15T19:04:56Z) with no rotated backups. Nothing before this process is visible, and the first failure came 7 seconds after the start, so there is no known-good period and no onset to date. The catalogue was read about 2 minutes after the failures."
  - "The chaos gauge was first sampled 18 seconds after the last failure. For the failure window, H3 rests on the absence of chaos events in the full log and on the code stack trace in each failure."
  - "No user traffic arrived after 2026-11-15T19:05:08Z, so the sample is 6 order requests (3 failed, 3 succeeded)."
  - "Lenses exist for three classes only (software-defect, infra-process, interfaces). No lens ran for load-saturation, third-party, or data-db; the lab has no database and no third-party dependency."
usage:
  model: claude-fable-5-2
  tokens: 1434300
  wall_clock_seconds: 275
---

# Orders fail with HTTP 500 for a product with a null price

## Summary

**Verdict: root cause identified (software defect, unhandled exception).** The
order-creation code multiplies the product's price by the quantity without a check for
a missing price. For a product whose price is null, the multiplication raises a
`TypeError` at `shop.py` line 82 (`create_order`), nothing handles it, and `POST /orders`
answers HTTP 500 (E1–E6). The catalogue holds exactly one such product: id 4, "Mystery
Box", `"price":null` (E10, E11). Orders for priced products succeed on the same route in
the same seconds (E7–E9), which matches "other customers' orders are going through
fine".

Impact in the visible window: 3 of 6 user order requests failed (E14, E16), all with the
same exception at the same line (E15). No other route returned an error (E24). The
process is healthy, did not restart, and chaos mode is off (E17–E22).

Confidence: high for the mechanism (the stack trace is direct evidence). The product id
of the failing requests is inferred, not observed: failed requests log no product id.
The inference is tight: the order request carries no price (E13), so the None price
comes from the catalogue record, and one record only has a null price.

Complaint object, as delivered by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794769513",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine." },
  "startsAt": "2026-11-15T19:05:13Z"
}
```

Investigation start: 2026-11-15T19:05:24Z (trigger latency 11 s).

## Timeline

All times UTC, 2026-11-15.

- 19:04:56.058 — process start, the only startup marker in the log (E21). No
  configuration, deploy, or flag-change marker follows it.
- 19:04:59.929 — order 1 created, product 1 (E7).
- 19:05:00.991 — order 2 created, product 2 (E8).
- 19:05:03.032 — first `TypeError` in `create_order`; `POST /orders -> 500` (E1, E2).
- 19:05:04.094 — second `TypeError`, same line; `POST /orders -> 500` (E3, E4).
- 19:05:06.160 — order 3 created, product 1, between two failures (E9).
- 19:05:07.220 — third `TypeError`, same line; `POST /orders -> 500` (E5, E6).
- 19:05:13 — complaint raised. 19:05:24 — investigation start.
- 19:05:25 — baseline: health ok (E22); 3 orders with 201, 3 with 500, 3 `TypeError`
  (E14–E16); chaos gauge 0 (E17); uptime 29.7 s (E18).
- 19:07:09–19:07:10 — catalogue and order list read: product 4 has a null price and no
  ordered units; the three stored orders are for products 1 and 2 (E10–E12).
- 19:07:14 — second scrape: counters unchanged, no error on another route, chaos gauge
  0, uptime 138.9 s (E19, E20, E23, E24).

## Investigation

- **Baseline.** Health, metrics, and the full log (24 lines at that time). Health was
  green while half of the order requests failed: the known shape of healthy monitoring
  over failing business traffic.
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. Software-defect reported the `TypeError`, the null price of
  product 4, and the single-route spread. Infra-process reported no anomaly: one
  startup, monotonic uptime, flat memory, chaos off. Interfaces reported the null price
  and the 500 that the API schema does not document, and found no change marker.
- **Deep-dive.** Skipped. The triage evidence for H1 was deterministic; the orchestrator
  ran five verification probes (products, product 4, orders, metrics, API schema) to
  quote the evidence first-hand.
- **Judge.** One fresh judge saw the hypotheses and the verbatim ledger only. Verdicts:
  H1 validated, H2 inconclusive, H3 invalidated, H4 invalidated. The judge required the
  removal of the claim that retries fail, because no log field links requests as
  retries; the H1 statement no longer carries it.
- **Budget.** One triage round, no deep-dive round, one judge round.

## Hypotheses

### H1 — unhandled TypeError on a null price (software-defect): validated

All three 500s pair by request id with the same exception at the same line (E1–E6). The
exception counter equals the 500 counter in both scrapes (E14, E15, E23, E24). The order
request has two fields, product id and quantity, and no price (E13), so the None operand
comes from the product record. Product 4 is the only record with a null price, and it
has zero ordered units (E10, E11). All stored orders are for priced products (E7–E9,
E12). Order 3 succeeded between two failures (E9), which fits a per-input fault and not
a time-window fault. Caveat: the product id of the failing requests is inferred.

### H2 — wrong data in the catalogue record (data-db): inconclusive

The null price (E10, E11) is also the trigger of H1, so it does not separate the two.
Nothing shows that null is an invalid state: the API schema declares a product as an
untyped object (E13), and no record history is visible. The judge's settling evidence:
a data contract for the product price that says whether it may be null. Even with wrong
data, the code answers it with an unhandled exception, so H2 could be a contributing
cause at most.

### H3 — chaos switch injects the errors (infra-process): invalidated

The chaos gauge reads 0 in both scrapes (E17, E20). The 500s are on one route only
(E24). Each failure carries a code stack trace (E1, E3, E5). The full log holds no chaos
event. Weak point: the first gauge sample came 18 seconds after the last failure.

### H4 — process instability (infra-process): invalidated

Uptime grew by 109.19 s across the 109 s between the scrapes (E18, E19). The exception
counter held at 3 with no reset (E15, E23). The log holds one startup event (E21), and
health answers ok (E22). The process served order 3 after two failures (E9).

## Safe next steps

Read-only only.

- Read the client-side or gateway-side records of the three failed requests
  (`c13ac4108e87`, `61fcc83e1d60`, `121b4aad0d63`) and confirm the product id.
- Ask support which product the affected customers ordered.
- Read the product data contract: may the price be null? The answer settles H2.
- Read `create_order` around `shop.py` line 82 to confirm that no check precedes the
  multiplication.
- Watch `http_exceptions_total{type="TypeError"}` against
  `http_requests_total{method="POST",path="/orders",status="500"}`; equal growth
  confirms the same failure.

## Gaps

- **Product id of the failures.** Failed requests log no product id, and the surface is
  GET-only. The link to product 4 is an inference from the stack trace and the catalogue.
- **Retries.** No field identifies a customer or links requests. The complaint's "keeps
  failing when they retry" is consistent with the evidence and not observed.
- **Validity of a null price.** No data contract, no record history, no database in the
  surface. H2 stays inconclusive.
- **History.** The log starts at the process start, 7 seconds before the first failure.
  No known-good period and no onset are visible. The catalogue was read about 2 minutes
  after the failures.
- **Chaos gauge timing.** First sampled 18 seconds after the last failure; the failure
  window rests on the log and the stack traces.
- **Sample size.** 6 user order requests; no user traffic after 19:05:08.
- **Lens coverage.** No lens exists for load-saturation, third-party, or data-db. The
  lab has no database and no third-party dependency.
