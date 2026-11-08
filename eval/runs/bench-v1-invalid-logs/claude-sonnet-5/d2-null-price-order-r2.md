---
konan_journal: 1
investigation:
  id: 2026-08-18-order-500-null-price
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-18T19:04:43Z
  concluded: 2026-08-18T19:12:01Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "POST /orders returns 500 (unhandled TypeError at shop.py:82, multiplying a None price by the order quantity) whenever the order references a product whose catalog price is null. 'Mystery Box' (product_id 4) is the only catalog product with a null price, so orders referencing it fail deterministically on every attempt while orders for other products succeed — matching 'keeps failing when they retry' and 'other customers' orders are going through fine.'"
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E1, E2, E3, E4, E5, E6, E7]
    evidence_against: []
  - id: H2
    statement: "GET /products/3 (the one catalog product with units_in_stock=0) deterministically returns 500 via a separate ZeroDivisionError in a turnover_score calculation at shop.py:64. Different route, different exception class, different code path from H1 — a distinct defect, not the reported order-placement incident, and confirmed to affect real (non-investigator) traffic."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E8, E9, E10]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 unhandled ZeroDivisionError (units_in_stock=0 turnover_score division) is a live, real-traffic-affecting defect, independent of the order-placement complaint under investigation."
    evidence: [E1, E8, E9, E10]
evidence:
  - id: E1
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787079933-19302, 2026-08-18T19:05:33Z"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:04:32.270Z, request_id f392cc6f89b8"
    quote: |-
      {"level": "ERROR", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "f392cc6f89b8", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n...TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:04:32.279Z, request_id f392cc6f89b8"
    quote: '{"event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 9.797, "request_id": "f392cc6f89b8"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:04:33.335Z, request_id 436fe352f15b"
    quote: |-
      {"event": "unhandled_exception", "exception_type": "TypeError", "message": "unsupported operand type(s) for *: 'NoneType' and 'int'", "stack": "...shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)..."} followed by {"event": "request", "method": "POST", "path": "/orders", "status": 500, "request_id": "436fe352f15b"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:04:36.454Z, request_id 0c8a5ca0aefc"
    quote: |-
      {"event": "unhandled_exception", "exception_type": "TypeError", "message": "unsupported operand type(s) for *: 'NoneType' and 'int'", "stack": "...shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)..."} followed by {"event": "request", "method": "POST", "path": "/orders", "status": 500, "request_id": "0c8a5ca0aefc"}
  - id: E6
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id konan-1787079915-19271, 2026-08-18T19:05:15Z"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
  - id: E7
    type: log
    source: "lab/logs/app.log, order_created events, 2026-08-18T19:04:29Z-19:04:35Z"
    quote: |-
      {"event": "order_created", "request_id": "dc4ff7ab3348", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"event": "order_created", "request_id": "c8937c1c8f2d", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"event": "order_created", "request_id": "5c4591d4bb6a", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E8
    type: log
    source: "lab/logs/app.log, all process lifetimes, grep for '\"status\": 500' access lines"
    quote: |-
      "path": "/products/3", "status": 500   (15 occurrences)
      "path": "/orders", "status": 500       (6 occurrences)
      -- no other path value appears with status 500 anywhere in the file
  - id: E9
    type: probe
    source: "GET /products/3 via scripts/probe.sh, request_id konan-1787080115-19505"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787080115-19505"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:10.692Z, request_id 19b4aea67888 (non-investigator traffic, predates this investigation)"
    quote: |-
      {"event": "unhandled_exception", "exception_type": "ZeroDivisionError", "message": "division by zero", "stack": "...shop.py\", line 64...turnover_score = units_ordered / product[\"units_in_stock\"]...ZeroDivisionError: division by zero"}
gaps:
  - "POST /orders request bodies are not logged, and a failed order is never persisted (no order_id assigned), so no telemetry directly names product_id on the three failing request_ids (E2, E4, E5). The link to product 4's null price (E1) is a closed deduction — product 4 is the only catalog entry with a null price, and the exact TypeError ('NoneType' * 'int' at shop.py:82) can only arise from a None left operand in that multiplication — not a directly cited fact. Re-checked directly: grepping each of the three failing request_ids in the full log returns exactly two lines each (the unhandled_exception and the access line); no third line carries a product_id or request body for any of them. This is why the judge scored H1 inconclusive and why a further deep-dive round was not spawned — the missing evidence does not exist in this telemetry surface, so re-querying it would not produce a different result."
  - "Whether 'keeps failing when they retry' reflects one customer repeating the same product several times, or several different customers each ordering product 4 once, cannot be determined — request_ids are per-request only; no customer or session identifier appears anywhere in the logs."
  - "Only the three lens files present in this repo (software-defect, interfaces, infra-process) were run. Nothing they returned suggested a load-saturation, third-party, or data-db class cause, but no dedicated lens exists here for those classes, so that exclusion rests on absence of anomalies in the lenses run, not on a lens built to look for them specifically."
usage:
  model: claude-sonnet-5
  tokens: 3078503
  wall_clock_seconds: 438
---

# POST /orders 500s for a null-price catalog product ("Mystery Box")

## Summary

**Verdict: inconclusive** (one hypothesis — H1 — explains the complaint and is
well-evidenced but not fully closed; one unrelated real defect — H2 — was found and
validated along the way).

The order-placement complaint is best explained by H1: `POST /orders` throws an
unhandled `TypeError` at `shop.py:82` (`product["price"] * order.quantity`) whenever the
order references a catalog product whose `price` is `null`. The catalog has exactly one
such product — id 4, "Mystery Box" (E1) — so any order for it fails on every attempt
(matches "keeps failing when they retry"), while orders for the other four products
succeed in the same window (E7; matches "other customers' orders are going through
fine"). Three such failures were observed in the current process alone (E2-E5), all on
non-investigator request ids, with chaos mode off (E6) — this is a deterministic,
data-dependent code defect, not transient degradation. The one gap: no telemetry
directly names `product_id=4` on the three failing requests themselves (POST bodies
aren't logged, and failed orders are never persisted), so the judge scored this
inconclusive rather than validated. That gap is structural — it was checked and
confirmed unclosable with the available surface (see Gaps), not merely unexamined.

Along the way, triage surfaced a second, unrelated, already-validated defect (H2): `GET
/products/3` throws an unhandled `ZeroDivisionError` (division by `units_in_stock`,
which is 0 for that product) on every request — a different route, different exception
class, real traffic affected, but not what was reported.

## Timeline

- **19:04:25Z** — current faultline process starts (startup marker).
- **19:04:29Z / 19:04:30Z** — two orders created successfully, products 1 and 2 (E7).
- **19:04:32.270Z** — `TypeError`, request `f392cc6f89b8`; **19:04:32.279Z** — same
  request returns `POST /orders -> 500` (E2, E3).
- **19:04:33.335Z** — second identical `TypeError`/500, request `436fe352f15b` (E4).
- **19:04:35.397Z** — a third order created successfully, product 1 (E7).
- **19:04:36.454Z** — third identical `TypeError`/500, request `0c8a5ca0aefc` (E5).
- **19:05:15Z** — `/metrics` snapshot: 3× `POST /orders` 201, 3× 500, 3×
  `TypeError`, chaos disabled (E6).
- **19:05:33Z** — `/products` probe shows product 4 ("Mystery Box") with `price: null`,
  the only null-price entry in the catalog (E1).
- **18:48:10.692Z** (earlier process, pre-dating this investigation) — non-investigator
  request `19b4aea67888` hits the separate `ZeroDivisionError` on `GET /products/3`
  (E10) — evidence H2 is a pre-existing, real-traffic defect, not new.
- **~19:08:35Z** — investigator reproduces the same `/products/3` 500 live (E9).

## Investigation

1. **Baseline** — `/health`, `/metrics`, `/products`, and the log tail from the current
   process's startup marker. This alone already showed a 50% failure rate on `POST
   /orders` (3/6) with `TypeError` as the only exception type, and one catalog product
   with a null price.
2. **Triage** — three lenses run in parallel, each blind to the others, given only the
   lens file, `docs/lab.md`, the complaint verbatim, and the baseline summary:
   `software-defect`, `interfaces`, `infra-process`.
   - `software-defect` and `interfaces` independently converged on the null-price →
     `TypeError` mechanism (H1); `interfaces` additionally found the unrelated
     `/products/3` `ZeroDivisionError` (H2) and live-reproduced it.
   - `infra-process` found a restart-loop pattern in the minutes before the current
     process started, but all transitions were graceful (clean shutdown/startup pairs,
     no crash markers), and the current process itself showed no latency drift, no RSS
     growth, and no `/health` flaps — nothing in that domain correlates with the order
     failures.
3. **Judge** — H1's mechanism (E1-E7) was evidenced strongly enough that a further
   deep-dive fan-out would only re-query already-exhausted log data, so one adversarial
   judge pass ran directly instead. The judge validated H2 outright and scored H1
   inconclusive, naming the missing citation: a log line tying `product_id=4` to one of
   the three failing request ids.
4. Re-checked that gap directly: grepped each of the three failing request ids
   (`f392cc6f89b8`, `436fe352f15b`, `0c8a5ca0aefc`) against the full log. Each has
   exactly two lines (the exception and the access line) — no request body, no
   product_id, anywhere. The gap is structural, not a missed query, so the
   investigation concludes here rather than spending the remaining budget re-asking the
   same source for data it does not carry.

## Hypotheses

### H1 — null-price product breaks order creation (inconclusive)

`product["price"] * order.quantity` at `shop.py:82` throws `TypeError` when `price` is
`None`. Product 4 ("Mystery Box") is the only catalog entry with `price: null` (E1). All
three observed `POST /orders` failures in the current process show the identical
exception type, message, and throw site (E2, E4, E5), each immediately followed by a
500 on the same request id; in the same window, three other orders for products with
numeric prices succeeded (E7); `/metrics` confirms chaos was off and the failure count
matches the exception count exactly (E6). Against: none directly — the only weakness is
that no evidence entry names `product_id=4` on the three failing requests themselves;
that link is inferred from E1 being the sole null-price product, not cited from a log
line naming it. The judge held this back from `validated`.

### H2 — out-of-stock product breaks turnover calculation (validated, latent to this complaint)

`units_ordered / product["units_in_stock"]` at `shop.py:64` throws `ZeroDivisionError`
when stock is 0. Product 3 ("Unobtainium Ingot") is the only catalog entry with
`units_in_stock: 0` (E1). Across the entire log (all process lifetimes), the only two
distinct paths ever returning 500 are `/products/3` and `/orders` (E8) — confirming this
is concentrated and route-specific, not a route-wide fault. A non-investigator request
(`19b4aea67888`, predating this investigation) already hit it (E10), and the
investigator reproduced it live just now (E9). This is a real defect but a different
route, different exception, and not what the complaint reported — carried as a latent
finding, not the incident.

## Safe next steps

- Read-only data check: confirm in the catalog/config source why product 4
  ("Mystery Box") has `price: null` while every sibling product has a numeric price —
  this is a data-entry/seed gap, not visible from HTTP telemetry alone.
- If a future investigation needs to close H1's remaining gap without inference, that
  requires a logging change (e.g. an order-attempt audit line before the price
  calculation, or request-body capture on `POST /orders`) — out of scope for this
  read-only investigation to make, but worth flagging to whoever owns the logging
  config.
- `GET /products/{id}` for any product with `units_in_stock: 0` (currently only id 3)
  reliably 500s — worth its own read-only investigation/ticket; it is independent of
  the order-placement complaint and was not deep-dived beyond confirming its shape here.

## Gaps

- POST /orders request bodies are not logged, and a failed order is never persisted, so
  no evidence entry names product_id on the three failing requests. The product-4
  attribution is a closed deduction (E1 is the only null-price product; the exact
  exception can only arise from a None left operand in that multiplication), not a
  direct citation. Re-checked and confirmed unclosable with this telemetry surface — see
  Investigation step 4.
- No customer/session identifier appears in the logs, so whether "keeps failing when
  they retry" is one customer retrying or several customers each ordering product 4
  once cannot be distinguished.
- Only the three lens files present in this repo were run (software-defect, interfaces,
  infra-process); no dedicated load-saturation, third-party, or data-db lens exists here
  to rule those classes out affirmatively — their absence from the three lenses' findings
  is the only evidence against them.
