---
konan_journal: 1
investigation:
  id: 2026-08-19-order-500-null-price
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T01:05:47Z
  concluded: 2026-08-19T01:10:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "create_order (faultline/src/faultline/shop.py:82) computes total_price = round(product[\"price\"] * order.quantity, 2) with no null-guard. Product id=4 (\"Mystery Box\") has price=null in the catalog, so any order against product_id=4 deterministically raises an unhandled TypeError, returned to the client as HTTP 500 — matching the complaint's 'fails, keeps failing on retry, others go through fine.'"
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:27.411Z"
    quote: '{"ts": "2026-08-19T01:05:27.411Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:31.308Z"
    quote: '{"ts": "2026-08-19T01:05:31.308Z", "event": "order_created", "request_id": "46db541938da", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:32.369Z"
    quote: '{"ts": "2026-08-19T01:05:32.369Z", "event": "order_created", "request_id": "a3af9299e615", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:34.431Z"
    quote: '{"ts": "2026-08-19T01:05:34.431Z", "level": "ERROR", "message": "unhandled exception: unsupported operand type(s) for *: ''NoneType'' and ''int''", "request_id": "d7606e411b99", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...File "faultline/src/faultline/shop.py", line 82, in create_order\n    total_price = round(product["price"] * order.quantity, 2)\nTypeError: unsupported operand type(s) for *: ''NoneType'' and ''int''"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:34.441Z"
    quote: '{"ts": "2026-08-19T01:05:34.441Z", "message": "POST /orders -> 500", "request_id": "d7606e411b99", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 10.687}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:35.496Z"
    quote: '{"ts": "2026-08-19T01:05:35.496Z", "level": "ERROR", "message": "unhandled exception: unsupported operand type(s) for *: ''NoneType'' and ''int''", "request_id": "9b368f52005f", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...File "faultline/src/faultline/shop.py", line 82, in create_order\n    total_price = round(product["price"] * order.quantity, 2)\nTypeError: unsupported operand type(s) for *: ''NoneType'' and ''int''"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:35.500Z"
    quote: '{"ts": "2026-08-19T01:05:35.500Z", "message": "POST /orders -> 500", "request_id": "9b368f52005f", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.696}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:37.558Z"
    quote: '{"ts": "2026-08-19T01:05:37.558Z", "event": "order_created", "request_id": "992117c470fa", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:38.616Z"
    quote: '{"ts": "2026-08-19T01:05:38.616Z", "level": "ERROR", "message": "unhandled exception: unsupported operand type(s) for *: ''NoneType'' and ''int''", "request_id": "7230665d6126", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...File "faultline/src/faultline/shop.py", line 82, in create_order\n    total_price = round(product["price"] * order.quantity, 2)\nTypeError: unsupported operand type(s) for *: ''NoneType'' and ''int''"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:05:38.621Z"
    quote: '{"ts": "2026-08-19T01:05:38.621Z", "message": "POST /orders -> 500", "request_id": "7230665d6126", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.194}'
  - id: E11
    type: probe
    source: "GET /products via scripts/probe.sh, request_id=konan-1787101567-35583"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E12
    type: probe
    source: "GET /products/4 via scripts/probe.sh, request_id=konan-1787101642-35659"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75}'
  - id: E13
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id=konan-1787101566-35577"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 3 / http_requests_total{method="POST",path="/orders",status="500"} 3 / http_exceptions_total{type="TypeError"} 3'
  - id: E14
    type: metric
    source: "GET /health and GET /metrics via scripts/probe.sh (infra-process triage lens)"
    quote: 'uptime_seconds 93.32 (health) / process_uptime_seconds 96.04 (metrics, monotonically increasing from ~39.6 at baseline) / faultline_chaos_enabled 0'
  - id: E15
    type: probe
    source: "GET /openapi.json via scripts/probe.sh (interfaces triage lens)"
    quote: 'OrderRequest requires product_id (integer) and quantity (integer, 1-1000) only; no non-null constraint declared on product price; no 502/503/504 observed on any route'
  - id: E16
    type: log
    source: "lab/logs/app.log (full file, 31 lines, scanned for every occurrence of product_id and every distinct event type)"
    quote: '"product_id" occurs exactly 3 times in the full file, all 3 inside order_created lines (E2, E3, E8); event-type counts: order_created=3, request=20, startup=1, unhandled_exception=3 — no event type besides order_created carries a product_id field'
gaps:
  - "The three failing request_ids (d7606e411b99, 9b368f52005f, 7230665d6126) cannot be tied directly to product_id=4: the 'request' access-log event (E5, E7, E10) does not capture the POST body, and create_order raises before the order_created line (which does carry product_id) is ever logged. E16 confirms this is a genuine schema gap, not a search that was skipped — product_id appears in the full log exactly 3 times, all inside the 3 successful order_created lines."
  - "The judge named the single piece of evidence that would settle H1: the request payload for the three failing requests, or a reproduction request against product_id=4 yielding the byte-identical failure. Both are unavailable to a read-only investigator: probe.sh is GET-only against the allowlist, POST /orders is not probeable, and issuing mutating traffic is reserved for the eval harness's scenario surface, not konan (docs/lab.md, AGENTS.md lab boundary)."
  - "No rotated log backups (app.log.1-3) exist for this process lifetime, so there was no earlier telemetry to cross-check beyond the single 31-line app.log already reviewed in full."
usage:
  model: claude-sonnet-5
  tokens: 3330594
  wall_clock_seconds: 294
---

# Order creation 500s: null `price` on catalog product, unconfirmed which orders hit it

## Summary

**Inconclusive.** The evidence points strongly, by elimination, to a software defect:
`create_order` (faultline `shop.py:82`) multiplies `product["price"] * order.quantity`
with no null-guard, and product id=4 ("Mystery Box") is the only catalog item with
`price: null` (E11, E12). All three `POST /orders` failures in the log share the
identical exception, line, and message (E4, E6, E9), match the 500 count exactly against
`http_exceptions_total{type="TypeError"}` (E13), and no infra, chaos, or interface
anomaly was found to compete as an alternative explanation (E14, E15). This mechanism
fully explains the complaint: failures are deterministic (retrying the same product
always 500s) while other customers, ordering other products, succeed (E2, E3, E8).

The adversarial judge rated hypothesis H1 **inconclusive**, not validated: no log line
captures the request body for the three failing requests, so the link from "these three
500s" to "product_id=4 specifically" is an elimination argument, not a direct
observation. A second round confirmed this gap cannot be closed on the read-only surface
(E16) — the access log schema doesn't carry POST bodies, and reproducing the request is
outside konan's read-only boundary. The investigation concludes honestly inconclusive
rather than overstating confidence the evidence doesn't quite reach.

## Timeline

- `2026-08-19T01:05:27.411Z` — faultline process starts, single continuous run (E1).
- `01:05:31.308Z` / `01:05:32.369Z` — two orders succeed, product_id 1 and 2, both
  non-null priced (E2, E3).
- `01:05:34.431Z`→`.441Z` — first `POST /orders` 500: unhandled `TypeError` at
  `shop.py:82`, immediately returned as 500 (E4, E5).
- `01:05:35.496Z`→`.500Z` — second, identical failure (E6, E7).
- `01:05:37.558Z` — a third order succeeds, product_id 1 again, non-null priced (E8).
- `01:05:38.616Z`→`.621Z` — third, identical failure (E9, E10).
- `01:06:07Z` onward — investigator baseline probes: `/products` shows product id=4 with
  `price: null` (E11); `/metrics` shows the 201/500/TypeError counts (E13).
- No config, deploy, flag-change, restart, or chaos-toggle marker appears anywhere in the
  process's log lifetime (E1, E14).

## Investigation

1. **Baseline** — `/health`, `/metrics`, `/products`, and the full `app.log` (31 lines,
   one process lifetime) were read. The baseline itself already contained the complete
   incident: 3× `POST /orders` 500 interleaved with 3× 201, all three 500s sharing one
   `TypeError` stack trace, and a catalog product with `price: null`.
2. **Triage** — three lenses spawned in parallel (infra-process, interfaces,
   software-defect), each given only the lens file, the surface contract, the complaint,
   and the baseline summary.
   - infra-process: no anomaly — uptime monotonic, no restart/chaos events, latency flat.
   - interfaces: no anomaly — no gateway-shaped (502/503/504) errors, no documented
     contract violated; failure pattern flagged as data/logic-shaped, not interface-shaped.
   - software-defect: identified the exact mechanism (null price × quantity at
     `shop.py:82`) and confirmed via a fresh `GET /products/4` probe that the null price
     persists (E12).
3. **Deep-dive** — skipped: triage evidence was already deterministic (same code line,
   same exception type, count-for-count match against `POST /orders` 500s) per the
   protocol's rule that complete, deterministic triage evidence goes straight to judge.
4. **Judge** — given only H1's cause statement, prediction, and cited evidence (E1-E15,
   no narrative). Verdict: **inconclusive** — the request-to-product_id linkage is
   inferred by elimination, not observed; named the settling evidence as either the
   failing requests' payloads or a reproduction against product_id=4.
5. **Round 2** — checked for rotated log backups (none exist) and grepped the full log
   for every `product_id` occurrence (E16: exactly 3, all inside the successful
   `order_created` lines). Confirmed the gap is a genuine surface limitation, not an
   unexplored corner — and that closing it would require either request-body logging
   this service doesn't have, or a mutating reproduction request outside konan's
   read-only boundary. Concluded with the honest state rather than spending remaining
   budget on lenses that had already reported no anomaly.

## Hypotheses

### H1 — null `price` on product_id=4 causes deterministic `POST /orders` 500s

**Statement:** `create_order` computes `total_price = round(product["price"] * order.quantity, 2)`
without checking for `None`. Product id=4 ("Mystery Box") has `price: null`; ordering it
always raises `TypeError`, surfaced to the client as an Internal Server Error, on every
attempt including retries. Other products all have numeric prices, so their orders
succeed — matching "other customers' orders are going through fine."

**State:** inconclusive (judge verdict).

**For:** the three 500s are byte-identical in exception type, message, and source line
(E4, E6, E9); the 500 count matches the `TypeError` exception count exactly, with no
other exception type present (E13); product id=4 is the only catalog item with a null
price, both at initial baseline and on recheck (E11, E12); no infra, process-lifecycle,
chaos, or interface-contract anomaly competes as an alternative cause (E1, E14, E15);
the two products that did succeed in the same window (ids 1 and 2) both have numeric
prices and their logged `total_price` values arithmetically match those prices (E2, E3,
E8).

**Against:** none — no evidence contradicts H1. The judge's concern is an evidentiary
gap (unobserved linkage), not a competing explanation.

**What would close it:** the request body (specifically `product_id`) for request_ids
`d7606e411b99`, `9b368f52005f`, `7230665d6126`, or a reproduction request against
product_id=4 yielding the identical stack trace. Neither is obtainable through the
investigator's read-only surface (E16; docs/lab.md probe allowlist is GET-only, and
mutating traffic is reserved for the eval harness).

## Safe next steps

- Ask engineering to add `product_id` (or the full request body) to the
  `unhandled_exception` and/or `request` log events for `POST /orders`, so a future
  investigation can cite the failing request's payload directly instead of inferring it.
- If request-level tracing/APM exists outside this lab's surface, check it for the same
  three request_ids to confirm product_id=4 directly — read-only, no scenario trigger
  needed.
- Treat any catalog product with a `null` price as a standing latent risk for this same
  `TypeError` shape; a read-only census of `/products` for other null-valued required
  fields (only price was checked here) could catch the same defect class before it's
  reported again.

## Gaps

- The three failing request_ids cannot be tied directly to product_id=4 — the access log
  doesn't capture POST bodies, and the exception fires before the order_created line
  (which does carry product_id) would be logged. Confirmed via full-log grep (E16), not
  left unchecked.
- The judge's named settling evidence (failing requests' payloads, or a reproduction
  against product_id=4) is unavailable within konan's read-only boundary — probe.sh is
  GET-only, and POST /orders reproduction is reserved for the eval harness's scenario
  surface.
- No rotated log backups exist for this process lifetime; the full available log history
  (31 lines) was already reviewed in the baseline and round 2.
