---
konan_journal: 1
investigation:
  id: 2026-08-18-orders-null-price-500
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-18T19:14:54Z
  concluded: 2026-08-18T19:24:07Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders raises an unhandled TypeError (HTTP 500) because shop.py's create_order multiplies product[\"price\"] by quantity without a null check; product_id=4 (\"Mystery Box\") has a null price in the catalog, so every order against that product fails deterministically while orders against other products succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Order creation fails with 500/TypeError specifically when the ordered product has a null price (currently only product_id=4, \"Mystery Box\"); this is a deterministic per-input code defect, not chaos or infrastructure degradation."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by injected chaos or partial gateway/infrastructure degradation (a probabilistic failure hitting some fraction of requests) rather than a per-input code defect."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E11]
evidence:
  - id: E1
    type: probe
    source: "GET /products, request_id konan-1787080562-19816"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:14:41.511Z"
    quote: "{\"level\":\"ERROR\",\"message\":\"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\",\"request_id\":\"c601d3677048\",\"event\":\"unhandled_exception\",\"exception_type\":\"TypeError\"} — stack: File faultline/shop.py, line 82, in create_order: total_price = round(product[\"price\"] * order.quantity, 2) -> TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:14:41.522Z"
    quote: '{"message":"POST /orders -> 500","request_id":"c601d3677048","event":"request","method":"POST","path":"/orders","status":500,"duration_ms":11.531}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:14:42.581Z and 19:14:42.585Z"
    quote: 'unhandled exception (TypeError, identical stack to E2) request_id=55974550734b, followed by {"message":"POST /orders -> 500","request_id":"55974550734b","status":500,"duration_ms":5.524}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:14:45.704Z and 19:14:45.708Z"
    quote: 'unhandled exception (TypeError, identical stack to E2) request_id=331db67f95be, followed by {"message":"POST /orders -> 500","request_id":"331db67f95be","status":500,"duration_ms":4.944}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:14:38.392Z, 19:14:39.449Z, 19:14:44.645Z"
    quote: '{"event":"order_created","request_id":"3737cd99022e","order_id":1,"product_id":1,"quantity":2,"total_price":99.0} / {"event":"order_created","request_id":"8a68bb30fa44","order_id":2,"product_id":2,"quantity":1,"total_price":23.0} / {"event":"order_created","request_id":"0f42262bf517","order_id":3,"product_id":1,"quantity":1,"total_price":49.5}'
  - id: E7
    type: metric
    source: "GET /metrics, current process (uptime ~41s at scrape time)"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 3 / http_requests_total{method="POST",path="/orders",status="500"} 3 / http_exceptions_total{type="TypeError"} 3 / faultline_chaos_enabled 0'
  - id: E8
    type: log
    source: "lab/logs/app.log, current process window 2026-08-18T19:14:34.514Z onward"
    quote: 'Every non-2xx status line in the window is "POST /orders -> 500"; all other routes hit ("GET /health -> 200", "GET /products -> 200", "GET /products/1 -> 200", "GET /orders -> 200") return 200. No 502/503/504 anywhere.'
  - id: E9
    type: probe
    source: "GET /openapi.json, request_id konan-1787080801-20161"
    quote: 'paths include only GET on "/products" and "/products/{product_id}"; no PUT/PATCH/DELETE on either. Only other POST-capable paths are "/chaos/enable" and "/chaos/disable". OrderRequest schema: {"product_id": integer, "quantity": integer} only — price is never client-supplied, always a server-side catalog lookup. No code path exists to mutate product price at runtime.'
  - id: E10
    type: probe
    source: "GET /products, request_id konan-1787080849-20173 (~287s after E1)"
    quote: '[{"id":1,...,"price":49.5,...},{"id":2,...,"price":23.0,...},{"id":3,...,"price":999.0,...},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,...,"price":6.25,...}] — byte-for-byte identical to E1'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:03:52.455Z (earlier, now-dead process)"
    quote: "{\"level\":\"ERROR\",\"message\":\"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\",\"exception_type\":\"TypeError\"} — identical signature recurring in a separate process instance ~70 minutes before the complaint, confirming this is a standing defect, not something newly introduced at the current process's startup"
  - id: E12
    type: log
    source: "lab/logs/app.log, uvicorn lifecycle lines @ 2026-08-18T19:02:58.115Z, 19:03:45.469Z, 19:04:25.251Z"
    quote: '"Started server process [18890]" / "Started server process [19047]" (47.4s later) / "Started server process [19162]" (39.8s later) — three restarts within 90s, vs. a 7-10 minute baseline cadence elsewhere in the session; each cycle shows a clean shutdown/startup, no crash trace'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:14:34.514Z"
    quote: '{"logger":"faultline.app","message":"faultline 0.1.0 started","event":"startup","version":"0.1.0"}'
gaps:
  - "Access logs do not capture POST /orders request bodies, so no single log line names product_id=4 for the three failing request ids (c601d3677048, 55974550734b, 331db67f95be). The attribution to product 4 rests on elimination — it is the only catalog row with a null price (E1, E10), confirmed immutable over the process lifetime because the API exposes no write path for product data (E9) — rather than a direct body capture. The investigator's surface is GET-only (docs/lab.md), so reproducing via POST /orders to close this directly was not possible."
  - "A restart-loop cluster at 19:02:58-19:04:25Z (three restarts within ~90s vs. a 7-10 minute baseline cadence, E12) was flagged by the infra-process lens but not deep-dived: it precedes the current process and the reported failure window by roughly 10 minutes, and its own logs show clean shutdown/startup cycles with no crash trace. Not established as related or unrelated to the current incident within this investigation's budget."
  - "Whether product 4 ('Mystery Box') having a null price is an intentional placeholder (e.g. an unreleased/unpriced product) or a catalog data-entry defect could not be determined from telemetry — that requires product/catalog-ownership context outside the investigator's surface."
usage:
  model: claude-sonnet-5
  tokens: 3943750
  wall_clock_seconds: 553
---

# Orders fail with 500 for one specific product (null price defect)

## Summary

**Root cause identified.** `POST /orders` returns HTTP 500 with an unhandled `TypeError`
whenever the ordered product has a `null` price in the catalog. Today that is exactly one
product: id 4, "Mystery Box" (E1, E10). The order-creation code (`shop.py:82`) computes
`product["price"] * order.quantity` with no null guard; when `price` is `None` the
multiplication raises `TypeError: unsupported operand type(s) for *: 'NoneType' and
'int'` (E2, E4, E5), the request 500s, and no order is created. Orders for every other
product succeed normally (E6) — which matches the complaint exactly: retrying against the
same (Mystery Box) product fails every time because the defect is deterministic per
product, not transient, while other customers ordering other products see no problem.
Chaos mode is off (E7) and no gateway-shaped, config-change, or restart-loop signal
coincides with the failure window (E8, E9, E12) — this is a code/data defect, not
infrastructure or an injected fault. Confidence: high. The one residual gap is that
request bodies aren't logged, so the product-4 attribution for the three specific
observed failures is by elimination (only null-price product, immutable catalog) rather
than a literal body capture — see Gaps.

## Timeline

- **19:02:58Z – 19:04:25Z** — a cluster of three process restarts within ~90s (E12),
  well before the failure window; noted by the infra lens, not established as related.
- **19:14:34.514Z** — current faultline process starts, version 0.1.0 (E13).
- **19:14:38.392Z – 19:14:39.450Z** — two orders succeed: product_id 1, then product_id
  2 (E6).
- **19:14:41.511Z – 19:14:41.522Z** — first failure: `TypeError`, `POST /orders -> 500`,
  request `c601d3677048` (E2, E3).
- **19:14:42.581Z – 19:14:42.585Z** — second failure, identical signature, request
  `55974550734b` (E4).
- **19:14:44.645Z – 19:14:44.646Z** — third order succeeds: product_id 1 again (E6).
- **19:14:45.704Z – 19:14:45.708Z** — third failure, identical signature, request
  `331db67f95be` (E5).
- **19:15:xx – 19:22:xx** — investigator baseline/triage probes: `/products` (E1),
  `/metrics` (E7), `/openapi.json` (E9), repeat `/products` (E10).
- (background) **19:03:52.455Z** — identical `TypeError` signature observed in an
  earlier, separate process instance (E11), showing the defect predates and outlives
  any single process restart — a standing condition, not something newly deployed.

## Investigation

1. **Baseline**: `/health` OK, `process_uptime_seconds` ~41s at first scrape → current
   process is recent; `lab/logs/app.log` retains history across restarts, so log
   entries were filtered to the current process's startup marker (19:14:34.514Z)
   onward. `/metrics` showed 3× `POST /orders` 201, 3× 500, and exactly 3×
   `http_exceptions_total{type="TypeError"}` — the 500s and the TypeErrors are the same
   population.
2. **Triage** — three lenses spawned in parallel, each blind to the others:
   - *software-defect*: identified the exact stack trace (`shop.py:82`,
     `product["price"] * order.quantity`), cross-referenced `/products` and found
     product 4 is the only null-price row, and noted successful orders never reference
     product 4.
   - *infra-process*: found no lifecycle instability in the current process (no
     restarts, no RSS growth, no latency correlation with outcome); separately flagged
     the unrelated restart-loop cluster ~10 minutes earlier.
   - *interfaces*: found no gateway-shaped statuses, no chaos toggle near onset, no
     config/version change at startup — ruled out its entire domain.
   - All three converged on the same explanation and produced one testable hypothesis
     (H1); no lens raised a competing cause, so H2 (chaos/gateway) was formed only to
     be explicitly invalidated rather than left unaddressed, given the complaint's
     surface-level resemblance to a probabilistic/partial-degradation pattern.
3. **Judge round 1**: returned **inconclusive** — the mechanism (null-price × quantity
   TypeError) was accepted, but the attribution of the three specific failing
   request ids to product_id=4 specifically was flagged as inferential, since request
   bodies aren't logged and the catalog probe (E1) was a single, untimestamped
   snapshot that could theoretically have been a coincidence of a mutable catalog.
4. **Targeted follow-up**: pulled `/openapi.json` to check for any product-mutation
   endpoint (found none — E9) and re-probed `/products` ~287s later (E10, identical to
   E1) to demonstrate the null price is not a point-in-time coincidence.
5. **Judge round 2**: returned **validated** — the structural proof (no write path for
   price data exists at all, E9) plus the cross-process recurrence of the identical
   signature (E11) closed the gap; the only remaining item (a literal request-body
   capture) was assessed as adding certainty, not changing the verdict, and is outside
   the investigator's GET-only surface.

## Hypotheses

### H1 — null-price defect in order creation (validated)

`shop.py`'s `create_order` does `product["price"] * order.quantity` with no null check.
Product 4 ("Mystery Box") has `price: null` in the catalog (E1, E10) and the API exposes
no way to mutate that at runtime (E9). Every order against product 4 therefore fails
100% of the time with the identical `TypeError` (E2, E4, E5), while orders against
products with numeric prices succeed (E6). Metrics counts reconcile exactly (E7: 3
success, 3 failure, 3 TypeErrors, chaos off). The same signature recurs across
independent process restarts (E11), consistent with a standing data/code defect rather
than a transient fault.

### H2 — chaos / gateway / partial infrastructure degradation (invalidated)

Considered because "some customers fail, others succeed, retries keep failing" can also
describe a probabilistic partial-degradation pattern. Invalidated: `faultline_chaos_enabled
0` (E7), failures are 100% confined to `POST /orders` with no 502/503/504 anywhere else
(E8), and the identical failure signature recurs unchanged across separate process
restarts (E11) — a chaos/gateway cause would be expected to vary or clear on restart,
not reproduce identically.

## Safe next steps

- Read-only: inspect the catalog source/seed for product id 4 ("Mystery Box") to confirm
  whether `price: null` is intentional (e.g. an unpriced/unreleased item) or a data
  entry gap — this determines whether the fix belongs in `shop.py`'s null handling, the
  catalog data, or both.
- Read-only: if request/response body logging can be added to `POST /orders` (a
  telemetry change, not a target mutation), it would let future investigations confirm
  product-id attribution directly instead of by elimination.
- Read-only: keep an eye on the restart-loop cluster shape (three restarts in ~90s) if
  it recurs — it wasn't contemporaneous with this incident but its cadence was anomalous
  enough to be worth a baseline for comparison next time.

## Gaps

- Access logs do not capture `POST /orders` request bodies, so no single log line names
  `product_id=4` for the three failing request ids (`c601d3677048`, `55974550734b`,
  `331db67f95be`). The attribution rests on elimination — product 4 is the only
  catalog row with a null price (E1, E10), and that price is provably immutable over
  the process lifetime since the API exposes no write path for product data (E9) —
  rather than a direct body capture. The investigator's surface is GET-only
  (`docs/lab.md`), so reproducing via `POST /orders` to close this directly was not
  possible.
- A restart-loop cluster at 19:02:58Z-19:04:25Z (three restarts within ~90s vs. a
  7-10 minute baseline cadence elsewhere in the session, E12) was flagged by the
  infra-process lens but not deep-dived: it precedes the current process and the
  reported failure window by roughly 10 minutes, and its own logs show clean
  shutdown/startup cycles with no crash trace. Not established as related or
  unrelated to the current incident within this investigation's budget.
- Whether product 4 ("Mystery Box") having a null price is an intentional placeholder
  or a catalog data-entry defect could not be determined from telemetry alone — that
  requires product/catalog-ownership context outside the investigator's surface.
