---
konan_journal: 2
investigation:
  id: 2026-11-15-order-500s-null-price
  trigger: |-
    manual — /konan, human profile (docs/triggers.md). Complaint object: {"source":"human","fingerprint":"human-1794748645","labels":{"alertname":"human-report"},"annotations":{"summary":"Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."},"startsAt":"2026-11-15T13:17:25Z"}. Investigation start: 2026-11-15T13:17:37Z (trigger latency 12 s). No severity stated by the reporter.
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-15T13:17:37Z
  concluded: 2026-11-15T13:23:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The order-creation code multiplies the product price by the quantity without handling a null price, so every order for a product whose price is null (product 4 is the only one in the catalog) raises an unhandled TypeError and returns HTTP 500, while orders for priced products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order-creation code (shop.py line 82, create_order) multiplies the product price by the quantity and does not handle a product whose price is null; each order for such a product raises an unhandled TypeError and returns HTTP 500 on every attempt, while orders for products with a numeric price succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E13, E14, E19, E20, E21]
    evidence_against: []
  - id: H2
    statement: "The order failures come from the process or its platform: a restart, a crash, a resource limit, or an internal degradation switch (chaos mode) that injects errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E15, E16]
    evidence_against: [E1, E7, E8, E9, E12, E17]
  - id: H3
    statement: "The root cause is in the data layer: the catalog record of product 4 holds a wrong (corrupt or missing) price value, and that wrong data is what breaks the orders."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E13, E14]
    evidence_against: []
latent_findings:
  - statement: "The product detail endpoint divides the units ordered by the units in stock; for product 3 (units_in_stock 0) it raises an unhandled ZeroDivisionError and returns HTTP 500. Only one investigator probe triggered it; no user request for that path is in the log."
    evidence: [E13, E19, E23, E24]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:14.996Z (stack trimmed to its last frame, cut marked […]; local path prefix redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:17:14.996Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "578e7e82e5d4", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n […] File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:15.004Z"
    quote: |-
      {"ts": "2026-11-15T13:17:15.004Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "578e7e82e5d4", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 8.181, "client": "127.0.0.1:52207"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:16.063Z (stack trimmed to its last frame, cut marked […]; local path prefix redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:17:16.063Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "168ac862a98f", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n […] File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:16.067Z"
    quote: |-
      {"ts": "2026-11-15T13:17:16.067Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "168ac862a98f", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.28, "client": "127.0.0.1:52208"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:19.182Z (stack trimmed to its last frame, cut marked […]; local path prefix redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:17:19.182Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "952888209e14", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n […] File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:19.186Z"
    quote: |-
      {"ts": "2026-11-15T13:17:19.186Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "952888209e14", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.141, "client": "127.0.0.1:52210"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:11.901Z"
    quote: |-
      {"ts": "2026-11-15T13:17:11.901Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "2414b32f30f3", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:12.954Z"
    quote: |-
      {"ts": "2026-11-15T13:17:12.954Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b4d539901b9d", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:18.124Z"
    quote: |-
      {"ts": "2026-11-15T13:17:18.124Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b541fabbc52d", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-15T13:17:41.389Z, request id konan-1794748661-97533 (the complete http_requests_total block of the scrape)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E11
    type: metric
    source: "/metrics @ 2026-11-15T13:17:41.389Z, request id konan-1794748661-97533 (the only http_exceptions_total line)"
    quote: |-
      http_exceptions_total{type="TypeError"} 3
  - id: E12
    type: metric
    source: "/metrics @ 2026-11-15T13:17:41.389Z, request id konan-1794748661-97533"
    quote: |-
      faultline_chaos_enabled 0
  - id: E13
    type: probe
    source: "/products, request id konan-1794748674-97542"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001523s request_id=konan-1794748674-97542
  - id: E14
    type: probe
    source: "/products/4, request id konan-1794748762-97685"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001657s request_id=konan-1794748762-97685
  - id: E15
    type: probe
    source: "/health, request id konan-1794748660-97528"
    quote: |-
      {"status":"ok","uptime_seconds":32.97683495795354}
      -- HTTP 200 in 0.002197s request_id=konan-1794748660-97528
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:17:08.034Z"
    quote: |-
      {"ts": "2026-11-15T13:17:08.034Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E17
    type: metric
    source: "/metrics @ 2026-11-15T13:19:23.788Z, request id konan-1794748763-97700 (lines trimmed to the ones cited)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 135.76720441691577
      process_max_rss_bytes 48168960
  - id: E18
    type: probe
    source: "/products/999, request id konan-1794748763-97695"
    quote: |-
      {"detail":"no such product: 999"}
      -- HTTP 404 in 0.001214s request_id=konan-1794748763-97695
  - id: E19
    type: probe
    source: "/products/1, request id konan-1794748762-97690"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":117,"units_ordered":3,"turnover_score":0.02564102564102564}
      -- HTTP 200 in 0.001303s request_id=konan-1794748762-97690
  - id: E20
    type: probe
    source: "/orders, request id konan-1794748675-97547"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T13:17:11.901+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T13:17:12.954+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T13:17:18.124+00:00"}]
      -- HTTP 200 in 0.001305s request_id=konan-1794748675-97547
  - id: E21
    type: probe
    source: "/openapi.json, request id konan-1794748873-97746 (trimmed to the OrderRequest schema)"
    quote: |-
      "OrderRequest":{"properties":{"product_id":{"type":"integer","title":"Product Id"},"quantity":{"type":"integer","maximum":1000.0,"minimum":1.0,"title":"Quantity"}},"type":"object","required":["product_id","quantity"],"title":"OrderRequest"}
  - id: E22
    type: probe
    source: "/openapi.json, request id konan-1794748873-97746 (trimmed to the 200 response of GET /products/{product_id})"
    quote: |-
      "responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{"type":"object","additionalProperties":true,"title":"Response Get Product Products  Product Id  Get"}}}}
  - id: E23
    type: probe
    source: "/products/3, request id konan-1794748912-97784"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794748912-97784"}
      -- HTTP 500 in 0.006108s request_id=konan-1794748912-97784
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:21:52.771Z (stack trimmed to its last frame, cut marked […]; local path prefix redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:21:52.771Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794748912-97784", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n […] File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
gaps:
  - "The log lines of a failed order (the exception line and the access line) carry no product_id and no request body, and the surface is GET-only, so no probe can show which product the three failed requests named. Product 4 is named by elimination: the stack proves a null price at the multiplication, and the catalog holds exactly one product with a null price."
  - "Whether the null price of product 4 is wrong data or an intended value cannot be read from telemetry: the API schema declares no type for product fields (E22), and the source and the seed data are outside the surface. H3 stays inconclusive."
  - "The telemetry holds no customer identity. It shows three failures from three client ports; it cannot show that they were retries of the same customers, as the complaint says."
  - "The telemetry starts at the process start, 2026-11-15T13:17:08.034Z, with no rotated log backups. Failures before that time, and the reason for that start, are not visible."
  - "The sample is six order requests in eight seconds. No order request arrived after 2026-11-15T13:17:20Z, so the failure was read from the log and the counters, not observed live during the investigation."
  - "Only three lenses exist in this repo (software-defect, infra-process, interfaces). No lens swept load-saturation, third-party, or data-db; the baseline shows millisecond durations and a flat peak RSS, and the lab has no database and no third party."
usage:
  model: claude-fable-5-2
  tokens: 2046578
  wall_clock_seconds: 366
---

# Orders for a product with a null price fail with HTTP 500

## Summary

**Root cause identified (software defect, unhandled exception).** The order-creation
code multiplies the product price by the order quantity (`shop.py` line 82,
`create_order`) and does not handle a null price. The catalog holds one product with
`"price":null` — product 4, "Mystery Box" (E13, E14). Every order for such a product
raises `TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'` and returns
HTTP 500 (E1–E6). The failure is deterministic per input, so a retry fails again, and
orders for priced products succeed in between (E7–E9) — the shape the complaint
describes.

Impact in the observed window: 3 of 6 user order requests failed (E10), between
13:17:14.996Z and 13:17:19.186Z. All other routes returned 200 to users. The process
did not restart, and chaos mode is off (E12, E16, E17).

Confidence: high on the mechanism (the stack shows it directly, three times, and the
judge validated it). The product identity is an inference by elimination, not an
observation: failed requests do not log the product id (see Gaps).

One latent finding rides along: the product detail page of product 3 (zero stock)
returns HTTP 500 with a ZeroDivisionError (E23, E24). Only an investigator probe
triggered it; it is not the reported incident.

## Timeline

All times UTC, 2026-11-15.

- 13:17:08.034 — process start, `faultline 0.1.0 started`; the only startup event in the log (E16).
- 13:17:11.901 — order 1 created, product 1, HTTP 201 (E7).
- 13:17:12.954 — order 2 created, product 2, HTTP 201 (E8).
- 13:17:14.996 — first unhandled TypeError in `create_order`; `POST /orders -> 500` at 13:17:15.004 (E1, E2).
- 13:17:16.063 — second TypeError, same line; `POST /orders -> 500` at 13:17:16.067 (E3, E4).
- 13:17:18.124 — order 3 created, product 1, HTTP 201 — a success between two failures (E9).
- 13:17:19.182 — third TypeError, same line; `POST /orders -> 500` at 13:17:19.186 (E5, E6).
- 13:17:20.244 — last user request in the log (`GET /orders -> 200`).
- 13:17:25 — complaint raised (`startsAt`).
- 13:17:37 — investigation start.
- 13:17:41 — baseline: health 200, uptime 32.98 s; order counters 201 = 3, 500 = 3; TypeError = 3; chaos gauge 0 (E10, E11, E12, E15).
- 13:19:23 — second scrape: order and exception counters unchanged, uptime 135.77 s, continuous (E17).
- 13:21:52.771 — investigator probe of `/products/3` raises ZeroDivisionError, HTTP 500 (E23, E24) — latent finding.

No configuration, deploy, or flag-change marker is in the log. The only lifecycle
marker is the startup at 13:17:08.034Z; two orders succeeded after it and before the
first failure (E7, E8).

## Investigation

**Complaint.** Manual trigger (`/konan`). The complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794748645",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine." },
  "startsAt": "2026-11-15T13:17:25Z"
}
```

Investigation start: 2026-11-15T13:17:37Z. Trigger latency: 12 s. The complaint text is
data; every claim below comes from telemetry.

**Baseline.** `/health` 200 with uptime 32.98 s (E15). `/metrics`: `POST /orders` 201 = 3
and 500 = 3; one exception type, TypeError = 3; chaos gauge 0; durations in single-digit
milliseconds (E10, E11, E12). The log (25 lines at the baseline, no rotated backups)
holds one startup, three `order_created` lines, and three `unhandled_exception` lines,
each followed by `POST /orders -> 500`. Business surface: `/products` 200 with five
products, `/orders` 200 with three orders (E13, E20). The health endpoint is green while
half of the order requests failed — the healthy-monitoring shape.

**Triage (one round, three lenses in parallel, blind to each other).**

- *software-defect*: one code line throws on `POST /orders`; the failure is
  data-dependent; the catalog holds one null price; 5xx confined to one route and one
  exception type.
- *infra-process*: no anomaly — one start, continuous uptime, flat peak RSS, fast
  failures (5.1–8.2 ms), chaos off, no chaos or simulated events in the log.
- *interfaces*: no anomaly in its domain — no change marker, no gateway-shaped status,
  no random rate; `/openapi.json` declares only 201 and 422 for `POST /orders`, so the
  500 is outside the declared contract.

**Deep-dive.** Skipped for H1: the triage evidence was deterministic, and the one open
point (the product id of the failed requests) is out of reach of any read-only probe.
The orchestrator ran four targeted probes for verbatim quotes and for disconfirmation
(`/products/4`, `/products/1`, `/products/999`, a second `/metrics`).

**Judge (fresh agent, evidence only).** H1 validated; H2 invalidated; H3 inconclusive.
The judge set two wording limits on H1, both honored here: the evidence shows three
failures out of three such requests, not that they were retries; and the product
identity is an inference by elimination. Besides the ledger, the judge received two
absence statements that have no verbatim quote: the log holds zero `chaos_enabled`,
`chaos_disabled`, `chaos_failure`, or `simulated_exception` events, and two reads of
product 4, 88 s apart, both return a null price.

**After the judge.** To settle H3, one probe of `/openapi.json`: the product responses
are untyped objects (E22), so the schema does not say whether a null price is legal.
H3 stays inconclusive. One probe of `/products/3` tested a prediction from E13 and E19
(turnover score = units ordered / units in stock, and product 3 has zero stock): HTTP
500, ZeroDivisionError (E23, E24).

**Investigator traffic.** All investigator requests carry the `konan-` prefix. The one
404 on `/products/{product_id}` (E18) and the one 500 on `/products/3` (E23) in the
counters are investigator probes, not user traffic. No user request failed outside
`POST /orders`.

## Hypotheses

### H1 — null price not handled in order creation (software-defect) — validated

The stack names the mechanism directly: at `shop.py` line 82, `product["price"]` was
`None` and the multiplication by an integer quantity raised (E1, E3, E5). Each exception
has a matching `POST /orders -> 500` with the same request id (E2, E4, E6). The counters
agree: three 500s, three TypeErrors, on one route only (E10, E11). The request schema
accepts only an integer `product_id` and an integer `quantity` from 1 to 1000 (E21), so
the integer operand is the quantity and a malformed payload would get a 422, not this
exception. The catalog holds exactly one product with a null price (E13, E14), and that
product has zero completed orders (E14, E20), while product 1 shows three units ordered
(E19). Orders for products 1 and 2 succeeded before and between the failures (E7, E8,
E9). No evidence against was found.

### H2 — process or platform (infra-process) — invalidated

For: the process started 6.96 s before the first failure (E15, E16). Against: two orders
succeeded after the start and before the first failure (E7, E8), and one succeeded
between failures (E9); uptime is continuous over both scrapes and peak RSS grew by
32768 bytes only (E17); the chaos gauge reads 0 in both scrapes (E12, E17); the log
holds no chaos or simulated-exception event; and the exception is a real code-line
error with a stack (E1). A second startup event or a chaos event between 13:17:14 and
13:17:19 would reopen it; the log has none.

### H3 — wrong catalog data (data-db) — inconclusive

The null price exists (E13, E14). Nothing shows that it is an error of the data rather
than an intended value: the two reads agree, the log has no line about catalog loads or
changes, and the API schema declares no type for product fields (E22). The judge's
settle item — the definition of product 4 and the type of the price field in the source
— is outside the surface. Even if the value is wrong, the unhandled exception remains a
defect of the code; H3 can be a contributing cause at most.

## Safe next steps

Read-only only.

- Read `shop.py` line 82 (`create_order`) and the catalog definition of product 4 in the
  target's source, to confirm the missing null handling and to settle whether the null
  price is intended (settles H3).
- Ask support which product the affected customers tried to order; compare with product
  4, "Mystery Box".
- Watch `http_exceptions_total{type="TypeError"}` and
  `http_requests_total{method="POST",path="/orders",status="500"}`; each new order for a
  null-priced product should raise both by one.
- Read `shop.py` line 64 (`get_product`) for the latent division by zero on products
  with zero stock, and check the access log for user requests to `/products/3`.

## Gaps

- **Product id of the failed requests.** The exception line and the access line of a
  failed order carry no product id and no body; the surface is GET-only. Product 4 is
  named by elimination.
- **Wrong data or intended value.** Telemetry cannot say whether the null price is an
  error; the schema is untyped for products and the source is out of bounds. H3 is
  inconclusive.
- **Retries.** No customer identity in telemetry. Three failures came from three client
  ports; that they were retries by the same customers is the complaint's claim, not an
  observation.
- **Before the process start.** Telemetry starts at 13:17:08.034Z with no rotated
  backups. Earlier failures, and the reason for that start, are not visible.
- **Small sample, no live failure.** Six order requests in eight seconds; none after
  13:17:20Z. The failure was read from the log and the counters.
- **Lens coverage.** Three lenses exist and all three ran. No lens swept
  load-saturation, third-party, or data-db; the baseline shows no load signal, and the
  lab has no database and no third party.
