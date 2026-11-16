---
konan_journal: 2
investigation:
  id: 2026-11-15-order-null-price-typeerror
  trigger: |-
    manual — the /konan human profile (docs/triggers.md). Complaint object as synthesized by the adapter:
    {"source": "human", "fingerprint": "human-1794769136", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."}, "startsAt": "2026-11-15T18:58:56Z"}
    Investigation start: 2026-11-15T18:59:08Z (trigger latency 12 s). The reporter stated no severity.
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-15T18:59:08Z
  concluded: 2026-11-15T19:03:19Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The order-creation code (create_order, shop.py line 82) multiplies the product's price by the quantity without handling a null price, so every order for the one catalog product with a null price (product 4, 'Mystery Box') raises an unhandled TypeError and returns HTTP 500, while orders for priced products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order-creation code multiplies the product's price by the quantity and does not handle a product whose price is null; an order for such a product (the catalog holds one: product 4) raises an unhandled TypeError and returns HTTP 500 on every attempt, while orders for priced products succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E17]
    evidence_against: []
  - id: H2
    statement: "An internal degradation switch (chaos mode) in the target injects errors into about half of the POST /orders requests."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E13]
    evidence_against: [E1, E2, E4, E6, E15, E16]
  - id: H3
    statement: "The fault is in the data layer: the record of product 4 is corrupt or inconsistent (its price is missing), and this bad record, not the code, is the root cause."
    incident_class: data-db
    state: invalidated
    evidence_for: [E10, E11]
    evidence_against: [E2, E14, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:45.384Z (the stack field is omitted from the quote; its final frame is E2)"
    quote: |-
      {"ts": "2026-11-15T18:58:45.384Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "eec3e3066bbd", "event": "unhandled_exception", "exception_type": "TypeError"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:45.384Z, request_id eec3e3066bbd — the final frame of the stack field, with the checkout prefix of its file path redacted as <checkout>; the same final frame closes the stacks of the lines of E4 and E6"
    quote: |-
      File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:45.394Z"
    quote: |-
      {"ts": "2026-11-15T18:58:45.394Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "eec3e3066bbd", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.534, "client": "127.0.0.1:55231"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:46.453Z (the stack field is omitted from the quote)"
    quote: |-
      {"ts": "2026-11-15T18:58:46.453Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "247d707447cc", "event": "unhandled_exception", "exception_type": "TypeError"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:46.457Z"
    quote: |-
      {"ts": "2026-11-15T18:58:46.457Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "247d707447cc", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.094, "client": "127.0.0.1:55232"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:49.575Z (the stack field is omitted from the quote)"
    quote: |-
      {"ts": "2026-11-15T18:58:49.575Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "4268a2cdd952", "event": "unhandled_exception", "exception_type": "TypeError"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:49.580Z"
    quote: |-
      {"ts": "2026-11-15T18:58:49.580Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "4268a2cdd952", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.183, "client": "127.0.0.1:55234"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:48.517Z (a success between the second and the third failure)"
    quote: |-
      {"ts": "2026-11-15T18:58:48.517Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "dd60365c94fe", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:48.517Z"
    quote: |-
      {"ts": "2026-11-15T18:58:48.517Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "dd60365c94fe", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.194, "client": "127.0.0.1:55233"}
  - id: E10
    type: probe
    source: "/products, request_id konan-1794769250-18363, HTTP 200"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E11
    type: probe
    source: "/products/4, request_id konan-1794769251-18368, HTTP 200"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E12
    type: probe
    source: "/orders, request_id konan-1794769252-18373, HTTP 200 (the complete list of stored orders)"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T18:58:42.265+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T18:58:43.323+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T18:58:48.517+00:00"}]
  - id: E13
    type: metric
    source: "/metrics, request_id konan-1794769153-18258 (baseline scrape, 2026-11-15T18:59:13Z)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E14
    type: metric
    source: "/metrics, request_id konan-1794769153-18258 (the only series of this counter)"
    quote: |-
      http_exceptions_total{type="TypeError"} 3
  - id: E15
    type: metric
    source: "/metrics, request_id konan-1794769153-18258; the same value in the later scrape konan-1794769274-18395"
    quote: |-
      faultline_chaos_enabled 0
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:58:38.409Z — the only startup event; the whole file was read (24 lines at the baseline, no rotated backup files) and holds no line with event chaos_enabled, chaos_disabled, chaos_failure or simulated_exception"
    quote: |-
      {"ts": "2026-11-15T18:58:38.409Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E17
    type: metric
    source: "/metrics, request_id konan-1794769274-18395 (later scrape, 2026-11-15T19:01:14Z)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      process_uptime_seconds 156.50613237498328
  - id: E18
    type: probe
    source: "/health, request_id konan-1794769152-18253, HTTP 200"
    quote: |-
      {"status":"ok","uptime_seconds":34.26928329188377}
  - id: E19
    type: probe
    source: "/openapi.json, request_id konan-1794769252-18378, HTTP 200 — the response schema of GET /products/{product_id}; the document declares no schema for a product and no type for its price"
    quote: |-
      "schema":{"type":"object","additionalProperties":true,"title":"Response Get Product Products  Product Id  Get"}
gaps:
  - "The failing access lines and exception lines carry no product_id. The link from the three failed orders to product 4 is a deduction (E2: the price operand is None; E10: product 4 is the only product with a null price), not an observation."
  - "The probe surface is GET-only, so no failing order was reproduced. 'Fails on every attempt' rests on three failures out of three and on the deterministic shape of the code line in E2."
  - "The catalog was read about two minutes after the failures (E10, E11). The null price at the time of the failures rests on E2 alone."
  - "The triage ran the software-defect lens only. The baseline excluded the infra-process and interfaces domains with evidence (E15, E16, no 502/503/504 series, each 500 paired with an in-process stack trace), so those two lenses were not spawned; this is an accepted blind spot."
  - "The chaos gauge was not sampled during the failure window (18:58:45Z to 18:58:50Z); its exclusion for that window rests on the absence of chaos events in the complete log (E16)."
  - "No telemetry shows whether the null price of product 4 is intended or an unintended data fault: the surface exposes no data-layer schema and no write history. The weaker form of H3 (a data fault alongside the code defect) stays untested."
  - "The number and identity of affected customers are not visible: access lines carry only a local client address and port."
  - "No deep-dive round ran: the triage evidence was deterministic, so the hypothesis list went straight to the judge."
  - "Token totals were not captured in this session; journal validation was a manual checklist, no automated schema check ran."
usage:
  model: claude-fable-5-2
  tokens: 1093107
  wall_clock_seconds: 251
---

# Orders for the product with a null price fail with HTTP 500 (unhandled TypeError in order creation)

## Summary

**Verdict: root cause identified — software defect, unhandled exception.** The
order-creation code computes `product["price"] * order.quantity` (`shop.py` line 82,
E2) with no handling of a null price. The catalog holds one product with a null price:
product 4, "Mystery Box", 75 units in stock (E10, E11). An order for it raises an
unhandled `TypeError` and the customer gets HTTP 500 (E1–E7). The failure depends on
the input, not on the request, so a retry of the same order fails again; orders for
priced products succeed in the same process, also between the failures (E8, E9, E12).
That matches the complaint: some customers fail on each retry, other customers are
fine.

Impact so far: 3 of 6 `POST /orders` requests failed (E13), all three with the same
exception (E14); every other route answered 200 and `/health` is green (E18) — the
health endpoint does not see this failure. No investigator probe caused a failure; all
three failures are user traffic. Confidence is high on the mechanism (the judge
validated H1). The link to product 4 is a deduction, because the failing log lines
carry no product id (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 18:58:38.409 — process start, `faultline 0.1.0 started` (E16). The only lifecycle
  marker in the log. No configuration, deploy, flag or chaos marker exists.
- 18:58:42.265, 18:58:43.323 — two orders succeed, products 1 and 2 (E12).
- 18:58:45.384 — first unhandled `TypeError` in `create_order`; `POST /orders -> 500`
  at 18:58:45.394 (E1, E2, E3).
- 18:58:46.453 — second `TypeError`; 500 at 18:58:46.457 (E4, E5).
- 18:58:48.517 — an order for product 1 succeeds, 201 (E8, E9).
- 18:58:49.575 — third `TypeError`; 500 at 18:58:49.580 (E6, E7).
- 18:58:56 — complaint raised (`startsAt`).
- 18:59:08 — investigation start.
- 18:59:12–18:59:13 — baseline: `/health` 200 (E18); `POST /orders` 201 = 3, 500 = 3
  (E13); `TypeError` = 3 (E14); chaos gauge 0 (E15).
- 19:00:50–19:00:52 — catalog and order probes: product 4 has a null price, no stored
  order names product 4 (E10, E11, E12); the API document declares no product schema
  (E19).
- 19:01:14 — later scrape: 500 count and `TypeError` count still 3, uptime 156.5 s,
  no restart (E17).
- 19:03:19 — conclusion.

## Investigation

- **Setup.** `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`.
  Budget: one triage round, at most 3 deep-dives per round, at most 2 rounds.
- **Baseline.** `/health`, `/metrics` and the complete log (24 lines, no backups).
  Normal: every GET route 200, orders for products 1 and 2 return 201 in about 1 ms.
  Deviation: three `POST /orders` 500s, each paired by request id with an unhandled
  `TypeError`; one startup, chaos gauge 0, no gateway-shaped status.
- **Triage.** One lens, software-defect. The baseline excluded the infra-process and
  interfaces domains with evidence (E15, E16, no 502/503/504 series, an in-process
  stack on every 500), so those lenses were not spawned (recorded under Gaps). The
  lens returned three findings: one exception at one code line for all 500s; a
  data-dependent shape with one null-price product in the catalog; failures confined
  to one route with no injected fault. The orchestrator repeated the probes to quote
  the evidence first-hand.
- **Deep-dive.** Skipped. The triage evidence was deterministic, and the one open
  item (the product id of the failed orders) cannot be closed on a GET-only surface.
- **Judge.** One fresh judge saw only the hypothesis list and the verbatim evidence.
  Verdicts: H1 validated, H2 invalidated, H3 invalidated as stated. The judge named
  the limits now listed under Gaps.

## Hypotheses

### H1 — unhandled TypeError on a null price in order creation (software-defect) — validated

Each of the three 500s shares a request id with one `TypeError` (E1/E3, E4/E5,
E6/E7), and every stack ends at `shop.py` line 82 on `product["price"] *
order.quantity` with a `NoneType` left operand (E2). The counts match with no
remainder: three 500s, three `TypeError`s, no other exception series (E13, E14, E17).
The catalog holds exactly one product with a null price, product 4 (E10, E11). The
three stored orders are for the priced products 1 and 2 (E12), and product 4 shows
`units_ordered` 0 (E11). A success sits between the second and the third failure in
the same process (E8, E9). No evidence against.

### H2 — an internal degradation switch injects the errors (infra-process) — invalidated

Its only support is the 3-to-3 ratio on the route (E13), which six requests cannot
tell apart from the request mix. All three predictions fail: the chaos gauge reads 0
in both scrapes (E15); the complete log holds no chaos or simulated-exception event
(E16); every failing request carries an application stack trace from the target's
own code (E1, E2, E4, E6).

### H3 — a corrupt product record in the data layer is the root cause (data-db) — invalidated

E10 and E11 show that the price of product 4 is null; they do not show corruption or
inconsistency — the list read and the detail read agree. No data-layer error exists:
the only exception type is the `TypeError` raised in application code (E14, E2), and
the target's own code raising an unhandled error on this input is the software-defect
definition whatever the origin of the record. The API document is silent on the type
of a price (E19), so it neither allows nor forbids null. The weaker claim — the null
price is also an unintended data fault — is untested (see Gaps).

## Safe next steps

Read-only suggestions only.

- Read `create_order` around `shop.py` line 82 and the product lookup before it, to
  confirm that no guard exists for a null price.
- Read the source of the catalog record of product 4, to learn whether the null price
  is intended (a product without a price yet) or a data fault.
- Ask support which product the failed orders named, to turn the deduction about
  product 4 into an observation.
- Watch `http_exceptions_total{type="TypeError"}` and
  `http_requests_total{method="POST",path="/orders",status="500"}`; growth means more
  customers hit the same input.
- Review other code paths that read a product's price (for example the
  `turnover_score` of the product detail) for the same assumption.

## Gaps

- **No product id on the failing lines.** The link from the three failed orders to
  product 4 is a deduction from E2 and E10.
- **No reproduction.** The surface is GET-only; "fails on every attempt" rests on
  three failures out of three and the deterministic code line.
- **Catalog read after the fact.** The probes ran about two minutes after the
  failures; the null price at failure time rests on E2.
- **Two lenses not spawned.** infra-process and interfaces were excluded by baseline
  evidence, not by their own sweep.
- **Chaos gauge not sampled in the failure window.** The exclusion for that window
  rests on the absence of chaos events in the complete log.
- **Intended or faulty data.** No telemetry shows whether a null price is a legal
  state of a product.
- **Affected customers.** Access lines carry a local address and port only; the
  number of distinct customers is not visible.
- **No deep-dive round.** The hypothesis list went from triage to the judge.
- **Usage and validation.** Token totals were not captured; the journal was checked
  by hand against the schema, no automated check ran.
