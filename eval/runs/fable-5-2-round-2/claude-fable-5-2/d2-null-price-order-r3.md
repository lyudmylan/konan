---
konan_journal: 2
investigation:
  id: 2026-11-15-order-null-price-typeerror
  trigger: "manual: /konan human report; fingerprint human-1794769901; startsAt 2026-11-15T19:11:41Z; investigation start 2026-11-15T19:11:54Z; trigger latency 13 s"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-15T19:11:54Z
  concluded: 2026-11-15T19:15:59Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The order-creation code (create_order, shop.py line 82) multiplies the product price by the quantity without handling a null price, so every order for a product with a null price (product 4, Mystery Box) raises an unhandled TypeError and returns HTTP 500, while orders for priced products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order-creation code (create_order, shop.py line 82) multiplies the product price by the quantity and does not handle a product whose price is null; every order for product 4 (Mystery Box, price null) raises an unhandled TypeError and returns 500, and orders for priced products succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E13, E14, E15, E17, E22, E23]
    evidence_against: []
  - id: H2
    statement: "The 500s come from the process or its platform: an injected degradation switch (chaos), or a crash or restart of the process."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E16]
    evidence_against: [E1, E7, E11, E12, E18, E21]
  - id: H3
    statement: "The root cause is in the data layer: the catalog record of product 4 is wrong (its price is missing), and the code is correct for valid data."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E13, E14]
    evidence_against: [E1, E20]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:31.085Z; stack trimmed to its final frame, with the checkout prefix of its file path redacted as <checkout>"
    quote: |-
      {"ts": "2026-11-15T19:11:31.085Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "6ad8def6f471", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "[...] File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:31.095Z"
    quote: |-
      {"ts": "2026-11-15T19:11:31.095Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "6ad8def6f471", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.341, "client": "127.0.0.1:55394"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:32.150Z; stack trimmed to its final frame, with the checkout prefix of its file path redacted as <checkout>"
    quote: |-
      {"ts": "2026-11-15T19:11:32.150Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "cb80a73ddd7f", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "[...] File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:35.263Z; stack trimmed to its final frame, with the checkout prefix of its file path redacted as <checkout>"
    quote: |-
      {"ts": "2026-11-15T19:11:35.263Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "b983fd851a86", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "[...] File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:27.973Z"
    quote: |-
      {"ts": "2026-11-15T19:11:27.973Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b1577b0b2054", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:29.027Z"
    quote: |-
      {"ts": "2026-11-15T19:11:29.027Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "eb96bdf97c62", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:34.208Z"
    quote: |-
      {"ts": "2026-11-15T19:11:34.208Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "091f08315e3d", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E8
    type: metric
    source: "/metrics scrape, request_id=konan-1794769918-19045 (2026-11-15T19:11:58Z)"
    quote: 'http_requests_total{method="POST",path="/orders",status="500"} 3'
  - id: E9
    type: metric
    source: "/metrics scrape, request_id=konan-1794769918-19045 (2026-11-15T19:11:58Z)"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 3'
  - id: E10
    type: metric
    source: "/metrics scrape, request_id=konan-1794769918-19045 (2026-11-15T19:11:58Z)"
    quote: 'http_exceptions_total{type="TypeError"} 3'
  - id: E11
    type: metric
    source: "/metrics scrape, request_id=konan-1794769918-19045 (2026-11-15T19:11:58Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E12
    type: metric
    source: "/metrics scrape, request_id=konan-1794769918-19045 (2026-11-15T19:11:58Z)"
    quote: "process_uptime_seconds 34.48629037523642"
  - id: E13
    type: probe
    source: "/products, request_id=konan-1794769928-19084"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001503s request_id=konan-1794769928-19084
  - id: E14
    type: probe
    source: "/products/4, request_id=konan-1794770015-19192"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001540s request_id=konan-1794770015-19192
  - id: E15
    type: probe
    source: "/orders, request_id=konan-1794769928-19089"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T19:11:27.973+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T19:11:29.027+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:11:34.208+00:00"}]
      -- HTTP 200 in 0.001530s request_id=konan-1794769928-19089
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:24.125Z (the only startup event in the file; the file holds no chaos_enabled, chaos_disabled, chaos_failure, or simulated_exception event)"
    quote: |-
      {"ts": "2026-11-15T19:11:24.125Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E17
    type: probe
    source: "/openapi.json, request_id=konan-1794770016-19197 (body trimmed to the OrderRequest schema)"
    quote: |-
      "OrderRequest":{"properties":{"product_id":{"type":"integer","title":"Product Id"},"quantity":{"type":"integer","maximum":1000.0,"minimum":1.0,"title":"Quantity"}},"type":"object","required":["product_id","quantity"],"title":"OrderRequest"}
  - id: E18
    type: metric
    source: "/metrics scrape, request_id=konan-1794770017-19202 (2026-11-15T19:13:37Z; lines trimmed to four series)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 132.93426345894113
  - id: E19
    type: probe
    source: "/health, request_id=konan-1794769918-19040"
    quote: |-
      {"status":"ok","uptime_seconds":34.132085791788995}
      -- HTTP 200 in 0.001709s request_id=konan-1794769918-19040
  - id: E20
    type: probe
    source: "/openapi.json, request_id=konan-1794770016-19197 (body trimmed to the 200 response schema of GET /products/{product_id})"
    quote: |-
      "schema":{"type":"object","additionalProperties":true,"title":"Response Get Product Products  Product Id  Get"}
  - id: E21
    type: metric
    source: "/metrics scrape, request_id=konan-1794770017-19202 (2026-11-15T19:13:37Z; the complete http_requests_total series list)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 2
      http_requests_total{method="GET",path="/orders",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 2
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:32.155Z"
    quote: |-
      {"ts": "2026-11-15T19:11:32.155Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "cb80a73ddd7f", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.475, "client": "127.0.0.1:55395"}
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:11:35.267Z"
    quote: |-
      {"ts": "2026-11-15T19:11:35.267Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "b983fd851a86", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.06, "client": "127.0.0.1:55397"}
gaps:
  - "The failing access lines carry no product_id and request bodies are not logged: the link from the three failures to product 4 is inferred from the stack (price is None) plus the catalog (product 4 is the only product with a null price), not observed."
  - "The surface is GET-only: the failure was not reproduced by the investigator."
  - "The claim that every order for a null-price product fails rests on three failures; no order was observed for products 3 and 5."
  - "Whether a null price is an invalid state of the catalog record cannot be decided: the published API schema declares no product type (E20), and the data store is not on the surface. H3 stays inconclusive."
  - "The log starts at the process start of 2026-11-15T19:11:24.125Z with no rotated backups: there is no history before this start, so the age of the defect and the count of affected customers before it are unknown."
  - "No order traffic arrived after 2026-11-15T19:11:35.267Z, so the retry behaviour that the complaint describes was observed on three requests only; the telemetry carries no customer identity."
  - "Lenses spawned: software-defect, infra-process, interfaces. The skill ships no lens for load-saturation, third-party, or data-db; those domains were covered only by the baseline (latency 1-11 ms, no 502/503/504, stable peak RSS)."
  - "The machine core was checked against the schema by hand; no interpreter was available for an automated check."
usage:
  model: claude-fable-5-2
  tokens: 1429439
  wall_clock_seconds: 245
---

# Orders for a product with a null price fail with HTTP 500 (unhandled TypeError)

## Summary

**Verdict: root cause identified — software defect, unhandled exception.** The
order-creation code (`create_order`, `shop.py` line 82) computes
`product["price"] * order.quantity` and does not handle a null price. Product 4
("Mystery Box") is the only catalog product with `price: null` (E13, E14). Every
`POST /orders` that reached line 82 with that price raised
`TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'` and returned 500
(E1–E4, E22, E23). Orders for priced products succeeded before, between, and after the
failures (E5–E7), which matches the complaint: the same customers fail on each retry,
other customers succeed.

Impact in the observed window: 3 of 6 `POST /orders` requests failed (E8, E9), all from
non-investigator clients; the exception counter equals the 500 counter (E10). The
failure is deterministic per input, not time-based and not injected: the chaos gauge is
0 (E11, E18), the process did not restart (E12, E16, E18), and no other route returned
a 5xx (E21). The defect is still present: product 4 still has a null price (E14).

Confidence: high on the mechanism (three identical stacks at one line). The link to
product 4 is an inference: the failing requests do not log their product id, and the
surface is GET-only, so the failure was not reproduced (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 19:11:24.125 — process start, `faultline 0.1.0 started` (E16). The only startup
  marker; no configuration, deploy, flag, or chaos marker exists in the log.
- 19:11:27.973 — order 1 created, product 1 (E5).
- 19:11:29.027 — order 2 created, product 2 (E6).
- 19:11:31.085 — first unhandled TypeError at `shop.py` line 82; `POST /orders -> 500`
  at 19:11:31.095 (E1, E2).
- 19:11:32.150 — second identical TypeError; 500 at 19:11:32.155 (E3, E22).
- 19:11:34.208 — order 3 created, product 1, between two failures (E7).
- 19:11:35.263 — third identical TypeError; 500 at 19:11:35.267 (E4, E23).
- 19:11:41 — complaint raised (`startsAt`); 19:11:54 — investigation start.
- 19:11:58 — baseline: health ok (E19); 3 × 201, 3 × 500, 3 × TypeError, chaos 0,
  uptime 34.5 s (E8–E12).
- 19:13:37 — second scrape: counters unchanged, chaos 0, uptime 132.9 s, no 5xx on
  any other route (E18, E21). No order traffic arrived after 19:11:35.267.

## Investigation

Complaint object, verbatim, as built by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794769901",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine." },
  "startsAt": "2026-11-15T19:11:41Z"
}
```

Investigation start: 2026-11-15T19:11:54Z (trigger latency 13 s). The reporter stated
no severity. Surface contract: `docs/lab.md` (`KONAN_ADAPTER` unset).

- **Baseline.** `/health` 200 (E19); `/metrics` (E8–E12); the full log (24 lines, one
  startup, no rotated backups); `/products` (E13) and `/orders` (E15). The health
  endpoint was green while half of the order requests failed.
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. Software-defect: one exception type at one code line, one
  route, a null-price product in the catalog. Infra-process: no anomaly (one startup,
  uptime in step with wall time, chaos 0, stable peak RSS, latency 1–11 ms).
  Interfaces: no gateway-shaped status and no change marker; the null-price record and
  the absence of a product schema in the published API.
- **Deep-dive.** Skipped. The triage evidence for H1 was deterministic; the
  orchestrator added three targeted probes: `/products/4` (E14), `/openapi.json`
  (E17, E20), and a second `/metrics` scrape (E18, E21).
- **Judge.** One fresh judge saw the hypothesis list and the verbatim evidence E1–E18
  only. Verdicts: H1 validated, H2 invalidated, H3 inconclusive. For H2 the judge
  asked for the complete 5xx series list: E21 supplies it (the only 5xx series is
  `POST /orders`). For H3 the judge asked for the product schema: E20 shows the API
  declares none, so H3 stays inconclusive.
- **Budget.** One triage round, no deep-dive agent, one judge round.

## Hypotheses

### H1 — null price is not handled in order creation (software-defect) — validated

All three 500s carry the same exception, at the same line, with the same operand
types (E1, E3, E4), and each pairs with its 500 access line by request id (E2, E22,
E23). The left operand of the multiplication is `product["price"]` and it is `None`;
the right operand is the quantity, which the request schema forces to an integer
(E17). The catalog holds exactly one product with a null price, product 4 (E13, E14).
The three successful orders used products 1 and 2 (E5–E7), and no order for product 4
exists (E15; `units_ordered` 0 in E14). The counts agree: 3 × 500, 3 × 201, 3 ×
TypeError (E8–E10). A success sits between two failures (E7), so the failure depends
on the input, not on the time. The judge's limits: the product id of a failing request
is inferred, and "every" rests on three failures.

### H2 — injected degradation or process lifecycle (infra-process) — invalidated

For: a process start 7 s before the first failure (E16). Against: the chaos gauge is 0
in both scrapes (E11, E18) and the log holds no chaos or simulated-exception event
(E16); the uptime matches the single startup and grows in step with wall time (E12,
E18); the exception comes from the order code, not from an injection point (E1); an
order succeeded between two failures after the same startup (E7); and no route other
than `POST /orders` has a 5xx series (E21).

### H3 — wrong catalog data is the root cause (data-db) — inconclusive

For: the record of product 4 has a null price (E13, E14). Against: the service's own
code raises an unhandled exception instead of a handled error (E1), and nothing on the
surface declares a null price invalid — the read route serves the record with 200
(E14) and the published schema has no product type (E20). H1 and H3 are not exclusive:
the code defect is proven; a data defect in addition to it cannot be decided from this
surface.

## Safe next steps

Read-only only.

- Ask support which product the affected customers ordered; a match with product 4
  ("Mystery Box") closes the inference gap.
- Read `create_order` in `shop.py` around line 82 in the service's source and confirm
  that no null-price guard exists.
- Ask the catalog owner whether a null price for product 4 is intended (settles H3).
- Watch `http_exceptions_total{type="TypeError"}` and
  `http_requests_total{method="POST",path="/orders",status="500"}`; growth together
  means more affected orders.
- Check the catalog (`/products`) for further records with a null price as it changes.

## Gaps

- **Product id of the failures is inferred.** Failing access lines carry no
  `product_id`, and request bodies are not logged. The chain is: the stack shows a
  `None` price; product 4 is the only product with a null price.
- **No reproduction.** The surface is GET-only; an order cannot be placed by the
  investigator.
- **Small sample.** Three failures and three successes; no order was observed for
  products 3 and 5.
- **Validity of the null price.** The API schema declares no product type (E20) and
  the data store is not on the surface, so H3 cannot be settled.
- **No history before 19:11:24.125Z.** One log file, no backups, one process start;
  the age of the defect and earlier customer impact are unknown.
- **Retry behaviour.** No order traffic after 19:11:35.267Z; the telemetry carries no
  customer identity, so "the same customer retried" is not observable.
- **Lenses.** Software-defect, infra-process, and interfaces ran. Load-saturation,
  third-party, and data-db have no lens file; the baseline covered them only in part.
- **Schema check by hand.** No interpreter was available; the machine core was checked
  against `journal.schema.json` manually (references, root cause, cause class, wall
  clock, field names, body sections).
