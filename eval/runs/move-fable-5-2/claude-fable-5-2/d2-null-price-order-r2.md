---
konan_journal: 2
investigation:
  id: 2026-11-15-order-500s-null-price
  trigger: >-
    manual — /konan human report. Complaint object:
    {"source": "human", "fingerprint": "human-1794749687",
    "labels": {"alertname": "human-report"},
    "annotations": {"summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."},
    "startsAt": "2026-11-15T13:34:47Z"}.
    Investigation start 2026-11-15T13:34:53Z; trigger latency 6 s. No severity stated by the reporter.
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-15T13:34:53Z
  concluded: 2026-11-15T13:39:30Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: >-
    The order-creation code (create_order, shop.py line 82) multiplies the product price by the
    quantity with no handling of a null price; the catalog serves one product with a null price
    (product 4, "Mystery Box"), and each of the three failed POST /orders requests raised an
    unhandled TypeError ('NoneType' * 'int') at that line and returned HTTP 500. The link to
    product 4 is by elimination (the only null price in the catalog), not by a logged product id.
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: >-
      The order-creation code multiplies the product price by the quantity and does not handle a
      null price. Product 4 has a null price, so an order for product 4 raises an unhandled
      TypeError and returns HTTP 500. Orders for products with a numeric price (observed:
      products 1 and 2) succeed.
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16]
    evidence_against: []
  - id: H2
    statement: >-
      An internal degradation switch (chaos mode) of the target injects the 500 responses on
      POST /orders.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E24, E17, E4, E6, E8, E3, E21]
  - id: H3
    statement: >-
      A process crash, a restart, or resource exhaustion causes the 500 responses.
    incident_class: infra-process
    state: invalidated
    evidence_for: [E18]
    evidence_against: [E19, E20, E22, E23, E12, E13, E14, E4, E6, E8]
  - id: H4
    statement: >-
      A failing dependency or a gateway tier fails about half of the order requests,
      independent of the input.
    incident_class: interfaces
    state: invalidated
    evidence_for: [E1, E2]
    evidence_against: [E4, E6, E8, E10, E11, E16, E21]
evidence:
  - id: E1
    type: metric
    source: "/metrics scraped 2026-11-15T13:35:04Z, request id konan-1794749704-98248"
    quote: 'http_requests_total{method="POST",path="/orders",status="500"} 3'
  - id: E2
    type: metric
    source: "/metrics scraped 2026-11-15T13:35:04Z, request id konan-1794749704-98248"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 3'
  - id: E3
    type: metric
    source: "/metrics scraped 2026-11-15T13:35:04Z, request id konan-1794749704-98248"
    quote: 'http_exceptions_total{type="TypeError"} 3'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:36.557Z (framework stack frames trimmed at the mark …; the checkout prefix of the file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:34:36.557Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "a0ebb9a21fa0", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n … File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:36.568Z"
    quote: |-
      {"ts": "2026-11-15T13:34:36.568Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "a0ebb9a21fa0", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.84, "client": "127.0.0.1:52341"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:37.620Z (framework stack frames trimmed at the mark …; the checkout prefix of the file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:34:37.620Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "0491aaa28e47", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n … File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:37.625Z"
    quote: |-
      {"ts": "2026-11-15T13:34:37.625Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "0491aaa28e47", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.436, "client": "127.0.0.1:52342"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:40.735Z (framework stack frames trimmed at the mark …; the checkout prefix of the file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:34:40.735Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "c7668ea5e054", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n … File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:40.739Z"
    quote: |-
      {"ts": "2026-11-15T13:34:40.739Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "c7668ea5e054", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.07, "client": "127.0.0.1:52344"}
  - id: E10
    type: probe
    source: "/products, request id konan-1794749714-98261 (HTTP 200, 2026-11-15T13:35:14Z)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E11
    type: probe
    source: "/products/4, request id konan-1794749807-98386 (2026-11-15T13:36:47Z)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001494s request_id=konan-1794749807-98386
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:33.454Z"
    quote: |-
      {"ts": "2026-11-15T13:34:33.454Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "ee65e8d0707d", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:34.503Z"
    quote: |-
      {"ts": "2026-11-15T13:34:34.503Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "f9f8b010102b", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:39.679Z"
    quote: |-
      {"ts": "2026-11-15T13:34:39.679Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "7121b119d941", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E15
    type: probe
    source: "/orders, request id konan-1794749715-98266 (HTTP 200, 2026-11-15T13:35:15Z)"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T13:34:33.454+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T13:34:34.503+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T13:34:39.679+00:00"}]
  - id: E16
    type: probe
    source: "/products/1, request id konan-1794749808-98391 (2026-11-15T13:36:48Z)"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":117,"units_ordered":3,"turnover_score":0.02564102564102564}
      -- HTTP 200 in 0.001364s request_id=konan-1794749808-98391
  - id: E17
    type: metric
    source: "/metrics scraped 2026-11-15T13:36:48Z, request id konan-1794749808-98396"
    quote: "faultline_chaos_enabled 0"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:29.447Z"
    quote: |-
      {"ts": "2026-11-15T13:34:29.447Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E19
    type: metric
    source: "/metrics scraped 2026-11-15T13:35:04Z, request id konan-1794749704-98248"
    quote: "process_uptime_seconds 34.9178594998084"
  - id: E20
    type: metric
    source: "/metrics scraped 2026-11-15T13:36:48Z, request id konan-1794749808-98396"
    quote: "process_uptime_seconds 139.51924483291805"
  - id: E21
    type: metric
    source: "/metrics scraped 2026-11-15T13:36:48Z, request id konan-1794749808-98396 (the complete http_requests_total series list, and the exception counter)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 2
      http_requests_total{method="GET",path="/orders",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
  - id: E22
    type: probe
    source: "/health, request id konan-1794749704-98243 (2026-11-15T13:35:04Z)"
    quote: |-
      {"status":"ok","uptime_seconds":34.78777949977666}
      -- HTTP 200 in 0.002548s request_id=konan-1794749704-98243
  - id: E23
    type: metric
    source: "/metrics scraped 2026-11-15T13:36:48Z, request id konan-1794749808-98396"
    quote: "process_max_rss_bytes 48988160"
  - id: E24
    type: metric
    source: "/metrics scraped 2026-11-15T13:35:04Z, request id konan-1794749704-98248"
    quote: "faultline_chaos_enabled 0"
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:34:41.793Z (the last request line without the investigator prefix konan-, as of 13:36:48Z)"
    quote: |-
      {"ts": "2026-11-15T13:34:41.793Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "5802e75c8883", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.906, "client": "127.0.0.1:52345"}
gaps:
  - "The three failing requests log no product id, and the investigator surface is GET-only, so the failing POST was not reproduced. The link from the failures to product 4 is by elimination: it is the only product with a null price (E10, E11)."
  - "The origin of the null price is not visible. The log starts at the process startup (13:34:29.447Z, no backup files), and the surface has no telemetry on the catalog source. The evidence cannot tell a wrong catalog record from an intended one that the code does not handle."
  - "The clause 'it keeps failing when they retry' is not verifiable. The three failures have different request ids and client ports, and the telemetry carries no customer identity."
  - "Success is observed for products 1 and 2 only. No user ordered product 3 (stock 0) or product 5 in the window."
  - "The sample is small: 6 user order requests in 7 seconds, and no user traffic after 13:34:41.793Z (E25). The failure rate under real traffic is unknown."
  - "The interfaces lens reported that /openapi.json declares only 201 and 422 for POST /orders; the orchestrator did not capture that response body, so it is not in the evidence ledger."
  - "The token total of the session was not captured. The journal was checked against the schema by hand; no validation script ran."
usage:
  model: claude-fable-5-2
  tokens: 1476759
  wall_clock_seconds: 277
---

# Orders for a product with a null price fail with HTTP 500

## Summary

**Verdict: root cause identified (software defect, unhandled exception).** The
order-creation code computes `product["price"] * order.quantity` at `shop.py` line 82
and does not handle a null price. The catalog serves one product with a null price:
product 4, "Mystery Box" (E10, E11). Each of the three failed `POST /orders` requests
raised the same unhandled `TypeError: unsupported operand type(s) for *: 'NoneType' and
'int'` at that line and returned 500 (E4–E9). The counts close: 3 exceptions (E3) equal
3 responses with status 500 (E1), and the 3 successful orders name products 1 and 2
only (E12–E15).

Impact: 3 of 6 user order requests failed between 13:34:36Z and 13:34:40Z. The failure
follows the input, so a retry of the same order fails again; orders for products with
a numeric price succeed. The condition is still present: product 4 still had a null
price at 13:36:47Z (E11). All other routes return 200 (E21), and `/health` is green
(E22) while the orders fail.

Confidence: high on the mechanism (the stack line is in the log three times). The link
to product 4 is an inference by elimination, because the failing requests log no
product id (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 13:34:29.447 — process startup, the only startup marker in the log (E18). No
  configuration, deploy or flag-change marker exists in the log.
- 13:34:33.454 — order 1 created, product 1 (E12).
- 13:34:34.503 — order 2 created, product 2 (E13).
- 13:34:36.557 — first unhandled TypeError in `create_order`; `POST /orders -> 500`
  at 13:34:36.568 (E4, E5).
- 13:34:37.620 — second TypeError; 500 at 13:34:37.625 (E6, E7).
- 13:34:39.679 — order 3 created, product 1, between the failures (E14).
- 13:34:40.735 — third TypeError; 500 at 13:34:40.739 (E8, E9).
- 13:34:41.793 — last user request in the log (E25).
- 13:34:47 — complaint raised (`startsAt`). 13:34:53 — investigation start.
- 13:35:04 — baseline: health ok (E22); 3 × 201 and 3 × 500 on `POST /orders`
  (E1, E2); 3 TypeErrors (E3); chaos gauge 0 (E24).
- 13:35:14 — `/products` shows product 4 with `"price":null` (E10).
- 13:36:47–13:36:48 — product 4 still null (E11); counters unchanged, one process
  since startup (E20, E21).

## Investigation

**Baseline.** `/health`, `/metrics`, the whole of `lab/logs/app.log` (24 lines at that
time, no backups), `/products`, `/orders`. Normal: all GET routes 200, order requests
of 1 to 2 ms. Abnormal: three 500 responses on `POST /orders`, each with an
`unhandled_exception` line.

**Triage (one round, three lenses in parallel, each blind to the others).**

- Software-defect lens: one TypeError at one code line on all three failures; one
  product with a null price; the failure follows the input.
- Infra-process lens: no anomaly. One startup, uptime monotonic, counters not reset,
  RSS flat, chaos gauge 0, no chaos or simulation event in the log.
- Interfaces lens: no anomaly of its class. No 502/503/504, no change marker, no sharp
  onset. It handed the failure to the software-defect lens.

**Deep-dive.** Skipped: the triage evidence for H1 was already deterministic (the
stack line plus the catalog). The orchestrator ran two confirming probes
(`/products/4`, `/products/1`) and a second metrics scrape.

**Judge (fresh agent, evidence only).** H1 validated, with three clauses narrowed
(retry, "other products", "each order for product 4"); the statements above carry the
narrowed form. H2, H3 and H4 invalidated. The judge named one piece of evidence that
would close the remaining gap: the product id of one failing request. That evidence is
out of reach of the surface (see Gaps).

Budget used: one triage round, no deep-dive agent, one judge round.

## Hypotheses

### H1 — null price not handled in order creation (software-defect) — validated

The exception message, the type, and the last stack frame are identical on the three
failures (E4, E6, E8), and each is followed by the 500 access line with the same
request id (E5, E7, E9). The left operand of the multiplication is `product["price"]`,
and it is `None`. The catalog has exactly one product with a null price, product 4
(E10), stable 93 seconds later (E11). Product 4 shows `units_ordered":0` (E11) while
product 1 shows `units_ordered":3` (E16), which matches the orders that succeeded
(E12–E15). Nothing was found against it. The link to product 4 stays an inference.

### H2 — chaos mode injects the 500s (infra-process) — invalidated

The gauge read 0 at 24 seconds after the last failure (E24) and again later (E17). The
log has no `chaos_enabled`, `chaos_disabled`, `chaos_failure` or `simulated_exception`
line. Every 500 is explained by an exception in the order arithmetic (E4, E6, E8), and
the exception count equals the 500 count (E3, E21). No 500 remains for an injected
fault.

### H3 — crash, restart or resource exhaustion (infra-process) — invalidated

The startup at 13:34:29.447 (E18) came 7 seconds before the first failure, which is
why this was tested. One process served the whole window (E19, E20, E22). Two orders
succeeded after the startup and before the first failure (E12, E13), and one between
failures (E14). RSS is flat near 49 MB (E23). The failures are a TypeError, not a
resource error (E4, E6, E8).

### H4 — dependency or gateway fails half of the requests (interfaces) — invalidated

The 3 of 6 ratio with interleaving (E1, E2) looked like a stable fraction. The
application itself raised each 500 in its own arithmetic (E4, E6, E8). No 502, 503 or
504 exists (E21). The null is stable on product 4 across two reads, and product 1
reads 49.5 twice (E10, E11, E16), so an intermittent wrong answer does not fit.

## Safe next steps

Read-only only.

- Find the product id of the failing requests `a0ebb9a21fa0`, `0491aaa28e47` and
  `c7668ea5e054` in any record outside this surface (client logs, support tickets).
  All three as product 4 closes the last gap.
- Read `create_order` in `shop.py` around line 82 to see how a product without a price
  reaches the multiplication.
- Read the source of the catalog record of product 4 to learn whether the null price
  is intended.
- Watch `http_exceptions_total{type="TypeError"}` and
  `http_requests_total{method="POST",path="/orders",status="500"}`; they move together
  while the condition holds.

## Gaps

- **No product id on the failures.** The `unhandled_exception` and access lines carry
  no product id, and the surface is GET-only. The failing order was not reproduced.
  Product 4 is named by elimination.
- **Origin of the null price.** The log starts at the process startup and has no
  backups. Nothing shows when or why the price became null, or whether it is intended.
- **Retries.** Nothing in the telemetry ties two requests to one customer. The claim
  that a retry fails follows from the mechanism, not from an observation.
- **Other products.** Success is observed for products 1 and 2 only.
- **Small sample.** Six user order requests in 7 seconds; no user traffic after
  13:34:41.793Z.
- **Declared contract.** The interfaces lens saw that `/openapi.json` declares only 201
  and 422 for `POST /orders`. The orchestrator did not capture the body, so the point
  is not in the ledger.
- **Usage and validation.** The token total was not captured. The schema check was
  done by hand.
