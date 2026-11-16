---
konan_journal: 2
investigation:
  id: 2026-11-15-order-500s-null-price
  trigger: >-
    manual (/konan, human profile). Complaint object:
    {"source": "human", "fingerprint": "human-1794750076",
    "labels": {"alertname": "human-report"},
    "annotations": {"summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."},
    "startsAt": "2026-11-15T13:41:16Z"}.
    Investigation start 2026-11-15T13:41:28Z; trigger latency 12 s.
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-15T13:41:28Z
  concluded: 2026-11-15T13:45:33Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: >-
    The order-creation code (create_order, shop.py line 82) multiplies the price of the
    ordered product by the quantity without handling a null price; an order for a product
    whose price is null raises an unhandled TypeError and returns HTTP 500 on every
    attempt, while orders for priced products succeed. The catalog holds one product with
    a null price, id 4 "Mystery Box"; that it is the product of the failing orders is
    inferred, because the failing log lines record no product id.
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: >-
      The order-creation code raises an unhandled TypeError when it multiplies the price
      of the ordered product by the quantity and the price is null; the request fails
      with HTTP 500 for every order of a product with a null price (the catalog holds one
      such product, id 4), and orders of priced products succeed.
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E15, E17]
    evidence_against: []
  - id: H2
    statement: >-
      A process lifecycle event (crash, restart, hang), a resource saturation, or an
      internal degradation switch causes the 500s on order placement.
    incident_class: infra-process
    state: invalidated
    evidence_for: [E2]
    evidence_against: [E10, E11, E12, E13, E14, E15, E16]
  - id: H3
    statement: >-
      A probabilistic per-request failure at a boundary (a gateway tier, a dependency, or
      a configuration/deploy change) causes the 500s on order placement.
    incident_class: interfaces
    state: invalidated
    evidence_for: [E10]
    evidence_against: [E1, E3, E4, E5, E6, E9, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:41:05.718Z (stack trimmed to its last frame; the checkout prefix of its file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:41:05.718Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "c5e3834c347d", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:41:05.729Z"
    quote: |-
      {"ts": "2026-11-15T13:41:05.729Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "c5e3834c347d", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.878, "client": "127.0.0.1:52418"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:41:06.784Z and its access line @ 13:41:06.789Z (stack trimmed to its last frame; the checkout prefix of its file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:41:06.784Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "b5907ea67574", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
      {"ts": "2026-11-15T13:41:06.789Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "b5907ea67574", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.431, "client": "127.0.0.1:52419"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:41:09.897Z and its access line @ 13:41:09.901Z (stack trimmed to its last frame; the checkout prefix of its file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T13:41:09.897Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "7cd621a8b282", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
      {"ts": "2026-11-15T13:41:09.901Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "7cd621a8b282", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.021, "client": "127.0.0.1:52422"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:41:08.842Z and its access line @ 13:41:08.843Z (between the failures of E3 and E4)"
    quote: |-
      {"ts": "2026-11-15T13:41:08.842Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "336061d10df8", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-11-15T13:41:08.843Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "336061d10df8", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.27, "client": "127.0.0.1:52421"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:41:02.634Z and @ 13:41:03.667Z"
    quote: |-
      {"ts": "2026-11-15T13:41:02.634Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "2a0cb1f7e3fb", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-15T13:41:03.667Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "3d11923d3781", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E7
    type: probe
    source: "/products, request_id=konan-1794750174-98735"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001506s request_id=konan-1794750174-98735
  - id: E8
    type: probe
    source: "/products/4, request_id=konan-1794750175-98740"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001383s request_id=konan-1794750175-98740
  - id: E9
    type: probe
    source: "/orders, request_id=konan-1794750175-98745"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T13:41:02.634+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T13:41:03.667+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T13:41:08.842+00:00"}]
      -- HTTP 200 in 0.001316s request_id=konan-1794750175-98745
  - id: E10
    type: metric
    source: "/metrics, request_id=konan-1794750176-98750, scraped about 2026-11-15T13:42:56Z (the complete http_requests_total family and the complete http_exceptions_total family)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 2
      http_requests_total{method="GET",path="/orders",status="200"} 4
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
  - id: E11
    type: metric
    source: "/metrics, request_id=konan-1794750176-98750, scraped about 2026-11-15T13:42:56Z"
    quote: "faultline_chaos_enabled 0"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:40:58.793Z (the only line with event startup in the file; the file has no backup files)"
    quote: |-
      {"ts": "2026-11-15T13:40:58.793Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E13
    type: probe
    source: "/health, request_id=konan-1794750091-98615 (logged @ 2026-11-15T13:41:31.338Z)"
    quote: |-
      {"status":"ok","uptime_seconds":32.556585874874145}
      -- HTTP 200 in 0.002038s request_id=konan-1794750091-98615
  - id: E14
    type: metric
    source: "/metrics, request_id=konan-1794750176-98750, scraped about 85 s after E13"
    quote: |-
      process_uptime_seconds 117.46156274992973
      process_max_rss_bytes 48119808
  - id: E15
    type: log
    source: "lab/logs/app.log, count of lines by event value over the whole file, read about 2026-11-15T13:43Z (command output)"
    quote: |2-
         3 "event": "order_created"
        28 "event": "request"
         1 "event": "startup"
         3 "event": "unhandled_exception"
  - id: E16
    type: log
    source: "lab/logs/app.log, count of access lines by route and status over the whole file, investigator probes included, read about 2026-11-15T13:43Z (command output)"
    quote: |2-
         4 "message": "GET /health -> 200"
         5 "message": "GET /metrics -> 200"
         2 "message": "GET /openapi.json -> 200"
         4 "message": "GET /orders -> 200"
         4 "message": "GET /products -> 200"
         1 "message": "GET /products/1 -> 200"
         2 "message": "GET /products/4 -> 200"
         3 "message": "POST /orders -> 201"
         3 "message": "POST /orders -> 500"
  - id: E17
    type: metric
    source: "/metrics, request_id=konan-1794750091-98620, the baseline scrape (logged @ 2026-11-15T13:41:31.926Z)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 33.14411154203117
      process_max_rss_bytes 48103424
gaps:
  - "The failing log lines record no product id, and the surface is GET-only, so the failure could not be reproduced: that product 4 is the product of the failing orders is an inference from the traceback (a null price was read) and the catalog (one null price)."
  - "The product lookup above shop.py line 82 is not visible in telemetry; a route by which a priced product yields a null price is not excluded."
  - "Telemetry cannot tell whether the null price of product 4 is intended catalog data or a wrong record; the class software-defect follows the contract's definition (the code raises on some input), and the data-layer reading (data-db, data-inconsistency) was not tested as a hypothesis of its own."
  - "No telemetry exists before the process start at 13:40:58.793Z (no backup log files): what changed at that start, in the code or in the catalog, is unknown."
  - "The degradation gauge was read after the failures (13:41:31Z and 13:42:56Z), not during them; for the failure window only the absence of degradation events in the log speaks."
  - "The window is short: about two minutes of uptime and six order requests, all in 8 s. Orders of products 3 and 5 were not observed."
usage:
  model: claude-fable-5-2
  tokens: 1577057
  wall_clock_seconds: 245
---

# Orders fail with HTTP 500 on an unhandled TypeError: a null product price in the order total

## Summary

Root cause identified, class software-defect, cause unhandled-exception. The
order-creation code computes the total as price times quantity (`shop.py` line 82, in
`create_order`) and does not handle a null price: the multiplication raises
`TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'`, nothing catches it,
and the request returns HTTP 500 (E1–E4). The failure depends on the input and not on
chance, so a retry of the same order fails again, which matches the complaint. The
catalog holds exactly one product with a null price, id 4 "Mystery Box" (E7, E8), and no
order exists for it (E8, E9).

Impact: 3 of 6 user order requests failed between 13:41:05Z and 13:41:09Z; the 3 others,
for products 1 and 2, succeeded, one of them between two failures (E5, E6, E10). All six
are user traffic: the investigator's probes are GET-only and carry `konan-` request ids.
No order request arrived after 13:41:09.9Z (E10 equals E17), but the condition is still
in place: product 4 still has a null price (E7, E8).

Confidence: high for the mechanism (three of three failures share one exception and one
code line; the judge validated H1). Medium for the product: the failing log lines record
no product id, so "product 4" is inferred, not observed. The health endpoint stayed green
through the incident (E13) — the business surface failed while health passed.

## Timeline

- 13:40:58.793Z — process start, the only startup marker in the log (E12). No
  configuration, deploy or degradation marker follows it (E15).
- 13:41:02.634Z, 13:41:03.667Z — orders 1 and 2 created for products 1 and 2, HTTP 201 (E6).
- 13:41:05.718Z — first unhandled TypeError at `shop.py` line 82; `POST /orders -> 500`
  at 13:41:05.729Z, request id `c5e3834c347d` (E1, E2).
- 13:41:06.784Z — second TypeError, same line; 500, request id `b5907ea67574` (E3).
- 13:41:08.842Z — order 3 created for product 1, HTTP 201 (E5).
- 13:41:09.897Z — third TypeError, same line; 500, request id `7cd621a8b282` (E4).
- 13:41:16Z — complaint raised (`startsAt`). 13:41:28Z — investigation start.
- 13:41:31Z — baseline: health 200 with uptime 32.56 s (E13); counters at 3 × 201,
  3 × 500, 3 × TypeError; degradation gauge 0 (E17).
- about 13:42:56Z — second scrape: order counters unchanged (E10), degradation gauge 0
  (E11), uptime 117.46 s, continuous with E13 (E14); catalog and order list read
  (E7, E8, E9).

## Investigation

Complaint object, as synthesized by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794750076",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine." },
  "startsAt": "2026-11-15T13:41:16Z"
}
```

Investigation start: 2026-11-15T13:41:28Z (trigger latency 12 s). No severity was stated.
Surface contract: `docs/lab.md` (`KONAN_ADAPTER` unset).

- **Baseline.** `/health` 200 (E13); `/metrics` showed 3 × 500 on `POST /orders` and
  `http_exceptions_total{type="TypeError"} 3` against 3 × 201 (E17); the log (24 lines,
  one process lifetime) showed three unhandled exceptions, each followed by a 500.
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. Software-defect found the TypeError and the null price of
  product 4. Infra-process found no anomaly in its domain: one startup, continuous
  uptime, flat memory, fast failures (5–12 ms), no degradation switch. Interfaces found
  no change marker, no gateway status, and a failure pattern that is not probabilistic.
- **Deep-dive.** Skipped. The H1 evidence from triage was deterministic, and the one open
  item (the product id of the failing orders) is out of reach of a GET-only surface. The
  orchestrator re-read the catalog, the order list and the metrics for verbatim quotes
  (E7–E11, E14) and counted the log by event and by route (E15, E16).
- **Judge.** One fresh agent, evidence only. H1 validated; H2 and H3 invalidated. The
  judge asked for three corrections, all applied here: the product id is worded as an
  inference; E11 is a point reading after the failures and does not cover the failure
  window (E15 does); E12 is neutral for H3 and was removed from its counter-evidence. It
  also found that the first caption of E16 was wrong (probes are included in the counts);
  the caption is corrected.
- One round; no second round was needed.

## Hypotheses

### H1 — unhandled TypeError on a null product price (software-defect) — validated

Every 500 on `POST /orders` is tied by request id to the same exception at the same line:
`total_price = round(product["price"] * order.quantity, 2)` with `'NoneType' and 'int'`
(E1 with E2, E3, E4). The counts close: three 500s, three TypeErrors, three
`unhandled_exception` lines, no other exception type (E10, E15, E17). Successes
interleave with failures in one process lifetime — order 3 at 13:41:08 sits between the
failures at 13:41:06 and 13:41:09 (E5) — and all successes are for products 1 and 2
(E6, E9). The catalog has one null price, product 4 (E7), and product 4 has
`units_ordered: 0` and no entry in the order list (E8, E9): no order for it has ever
succeeded. Nothing found speaks against H1. Two limits, from the judge: the product id
of the failing orders is inferred, and "orders of priced products succeed" is observed
for products 1 and 2 only.

### H2 — process lifecycle, saturation, or degradation switch (infra-process) — invalidated

The 500s exist (E2), but every prediction of H2 fails. One startup marker and no other
(E12, E15); uptime is continuous — 32.56 s at 13:41:31Z and 117.46 s about 85 s later
(E13, E14); peak memory is flat at about 48 MB (E14, E17); failures sit on one route
only, every GET is 200 (E10, E16); the log holds no degradation event (E15) and the
gauge reads 0 at both scrapes (E11, E17). The gauge readings are after the failure
window, so E15 carries the point for the window itself.

### H3 — probabilistic boundary failure or change event (interfaces) — invalidated

A 3-of-6 failure rate (E10) looks like chance only by count. The three failures share
one code line and one null operand in the target's own arithmetic (E1, E3, E4), and the
three successes are all for priced products (E5, E6, E9): the split is by input, not by
request. The only failing status is 500 — no 502, 503 or 504 (E16) — and the log holds
no change marker after the start (E15). The start itself, 7 s before the first failure,
is neutral: no earlier telemetry exists to compare with (see Gaps).

## Safe next steps

- Read `create_order` in the faultline source, from the product lookup to line 82, to
  confirm that no path handles a null price.
- Ask support which product the failing customers ordered, and compare with product 4.
- Read the history of the catalog entry of product 4 and of `shop.py` line 82: is the
  null price intended, and did either change before the 13:40:58Z start.
- Watch `http_requests_total{method="POST",path="/orders",status="500"}` and
  `http_exceptions_total{type="TypeError"}`: growth in step with each other means the
  same failure continues.

## Gaps

- **Product of the failing orders.** The `unhandled_exception` and access lines of a
  failed order carry no product id, and the surface is GET-only, so the failure was not
  reproduced. Product 4 is an inference: the traceback proves a null price was read, and
  the catalog shows one null price.
- **Lookup above line 82.** Telemetry shows the throwing line only. A path by which a
  priced product yields a null price is not excluded.
- **Code defect or wrong record.** Telemetry cannot tell whether the null price is
  intended catalog data. The journal classes the root cause as software-defect by the
  contract's definition (the target's code raises on some input). The data-layer reading
  (data-db, data-inconsistency) was not tested as its own hypothesis.
- **Before the start.** The log begins at 13:40:58.792Z and has no backups. What changed
  at that start is unknown.
- **Degradation gauge timing.** Read at 13:41:31Z and 13:42:56Z, not during
  13:41:05–13:41:09Z; only the absence of degradation events in the log covers the window.
- **Short window.** About two minutes of uptime, six order requests in 8 s; orders of
  products 3 and 5 were not observed.
