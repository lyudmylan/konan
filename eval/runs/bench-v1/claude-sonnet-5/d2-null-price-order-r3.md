---
konan_journal: 1
investigation:
  id: 2026-08-19-order-500s
  trigger: "manual (/konan adapter; complaint fingerprint human-1787102042, startsAt 2026-08-19T01:14:02Z, investigation start 2026-08-19T01:14:05Z — trigger latency 3s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: "2026-08-19T01:14:05Z"
  concluded: "2026-08-19T01:22:44Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "create_order (faultline shop.py:82) computes total_price as product['price'] * order.quantity with no null-price guard; the catalog's only price=null row is product 4 ('Mystery Box'), so every order for it while its price is null raises an unhandled TypeError (NoneType * int) and returns 500, while orders for priced products succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "POST /orders fails with an unhandled TypeError at shop.py:82 in create_order — total_price multiplies product['price'] by order.quantity, and the exception message's operand order ('NoneType' and 'int') proves the price operand was None, not the quantity. Three requests in the window hit this identical raise site and 500'd, interleaved with three successful orders (products 1 and 2) on the same route."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The product catalog served by this process currently contains exactly one product with a null price: id 4, 'Mystery Box', in stock — the only catalog row capable of supplying the None operand H1's mechanism requires."
    incident_class: data-db
    state: validated
    evidence_for: [E11, E12]
    evidence_against: []
  - id: H3
    statement: "The 500s stem from process instability — crash/restart loop or resource saturation — rather than application code."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13, E14, E15]
  - id: H4
    statement: "The 500s come from injected degradation (chaos mode), a failing dependency, or a gateway/proxy failure rather than the application's own handler code."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E6, E13, E14]
evidence:
  - id: E1
    type: probe
    source: "probe /health, request_id=konan-1787102078-35919 @ 2026-08-19T01:14:38.905Z"
    quote: |-
      {"status":"ok","uptime_seconds":53.880876917159185}
      -- HTTP 200 in 0.001430s request_id=konan-1787102078-35919
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:52.057Z (stack trimmed to the raise site)"
    quote: |-
      {"ts": "2026-08-19T01:13:52.057Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "9cd1b5118c1e", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n...TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:52.068Z"
    quote: |-
      {"ts": "2026-08-19T01:13:52.068Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "9cd1b5118c1e", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.782, "client": "127.0.0.1:54038"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:53.125Z (stack trimmed to the raise site, identical to E2)"
    quote: |-
      {"ts": "2026-08-19T01:13:53.125Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "1d9d6b2d86d2", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n...TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:53.130Z"
    quote: |-
      {"ts": "2026-08-19T01:13:53.130Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "1d9d6b2d86d2", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.478, "client": "127.0.0.1:54039"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:56.248Z (stack trimmed to the raise site, identical to E2)"
    quote: |-
      {"ts": "2026-08-19T01:13:56.248Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "a556bafc78c4", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "...shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n...TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:56.253Z"
    quote: |-
      {"ts": "2026-08-19T01:13:56.253Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "a556bafc78c4", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.303, "client": "127.0.0.1:54041"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:48.935Z-936Z"
    quote: |-
      {"ts": "2026-08-19T01:13:48.935Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "99332c3f24e0", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-08-19T01:13:48.936Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "99332c3f24e0", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.956, "client": "127.0.0.1:54036"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:49.997Z"
    quote: |-
      {"ts": "2026-08-19T01:13:49.997Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "46e373505f12", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"ts": "2026-08-19T01:13:49.997Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "46e373505f12", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.37, "client": "127.0.0.1:54037"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:55.188Z"
    quote: |-
      {"ts": "2026-08-19T01:13:55.188Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "8d4dffa232d3", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-08-19T01:13:55.188Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8d4dffa232d3", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.237, "client": "127.0.0.1:54040"}
  - id: E11
    type: probe
    source: "probe /products, request_id=konan-1787102195-36059"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E12
    type: probe
    source: "probe /products/4, request_id=konan-1787102196-36065"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E13
    type: metric
    source: "probe /metrics, request_id=konan-1787102081-35925 @ 2026-08-19T01:14:41.113Z (baseline, t0)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 56.088367542019114
      process_max_rss_bytes 47972352
  - id: E14
    type: metric
    source: "probe /metrics, request_id=konan-1787102196-36071 @ ~2026-08-19T01:16:36Z (re-probe, t1, ~2 min after t0)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 171.8128212080337
      process_max_rss_bytes 48398336
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:13:45.037Z — the only startup event in the entire log"
    quote: |-
      {"ts": "2026-08-19T01:13:45.037Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
gaps:
  - "No telemetry exists before process start at 01:13:45.037Z (E15); the true onset is unverifiable before boot — within the observable window the defect is present from the first order burst, ~4s after startup."
  - "The product-4 attribution is a closed inference, not a direct observation: POST bodies are not logged and failed orders emit no order_created event, so no log line names the failing product_id for request_ids 9cd1b5118c1e / 1d9d6b2d86d2 / a556bafc78c4. A first adversarial-judge pass on this exact compound claim (mechanism + specific-request attribution bundled into one hypothesis) returned 'inconclusive' for that reason. Splitting the claim into H1 (mechanism, directly cited from three identical stack traces) and H2 (catalog fact, directly cited from two probes) let each be validated on direct citation; a second judge round validated both and called product 4 a 'plausible, not proven' trigger for the three specific failures given it is the sole null-price row in a fully-enumerated 5-item catalog."
  - "The catalog snapshot (E11, E12) was captured ~2.5 minutes after the three failures; nothing in the surface directly confirms product 4's price was already null at 01:13:52-56Z rather than changing in between, though no config/deploy/chaos marker appears anywhere in the log (E15 is the only startup event; chaos stayed 0 across both metric scrapes, E13/E14)."
  - "No read-only reproduction is possible: POST /orders is outside the probe allowlist by design; determinism rests on three byte-identical stack traces (E2, E4, E6), not a controlled repro."
  - "'Other customers' orders going through fine' is directly confirmed only for products 1 and 2 (E8-E10); products 3 (out of stock) and 5 were never observed in any order attempt in this window."
  - "Whether product 4's null price is bad data or intentionally unpriced-by-design ('Mystery Box') is outside this read-only surface."
usage:
  model: claude-sonnet-5
  tokens: 3269227
  wall_clock_seconds: 519
---

# Order-creation 500s — unguarded null price in create_order (product 4)

## Summary

Root cause identified. `create_order` (faultline `shop.py:82`) computes
`total_price = round(product["price"] * order.quantity, 2)` with no null-price
guard; the catalog's only `price: null` row is product 4, "Mystery Box" (E11, E12).
Three requests in the incident window hit this exact raise site and returned 500
(E2-E7), interleaved with three successful orders for other products on the same
route (E8-E10) — the write path is alive, this is data-dependent, not global.
The exception message's operand order (`'NoneType' and 'int'`) is load-bearing: it
proves the *price* operand was `None`, not the quantity (E2, E4, E6). Process
health, chaos state, and dependency shapes were checked and ruled out (H3, H4
invalidated). The link from these three specific failures to product 4 specifically
is a tight elimination argument (sole null-price row in a fully enumerated 5-item
catalog), not a directly logged fact — recorded honestly as a gap rather than
folded into an overclaimed hypothesis. Impact matches the complaint exactly:
customers ordering product 4 get a deterministic 500 on every retry; customers
ordering anything else succeed.

## Timeline

All times UTC, from telemetry.

- **01:13:45.037Z** — process start, faultline 0.1.0 (E15); no telemetry exists
  before it.
- **01:13:48.935Z, 01:13:49.997Z** — two successful orders, products 1 and 2 (E8, E9).
- **01:13:52.057Z** — first failure: `TypeError` at `shop.py:82` in `create_order` →
  `POST /orders` 500, request `9cd1b5118c1e` (E2, E3).
- **01:13:53.125Z** — second identical failure, request `1d9d6b2d86d2` (E4, E5).
- **01:13:55.188Z** — success *between* failures: order 3, product 1 (E10) — the
  write path is not down, only the null-price input fails.
- **01:13:56.248Z** — third identical failure, request `a556bafc78c4` (E6, E7); last
  failure in the window.
- **01:14:41Z** — investigation baseline: counters 3×201 / 3×500, `TypeError`=3,
  chaos 0 (E13).
- **~01:16:36Z** — catalog probe: product 4 is the sole null-price row (E11, E12);
  re-scraped metrics unchanged from baseline — no new failures accrued during the
  investigation itself (E14).

## Investigation

Baseline showed the incident shape immediately: the only 5xx series in the counter
block was `POST /orders` 500=3 against 201=3 on the same route, with
`http_exceptions_total{type="TypeError"}` exactly matching (E13) — a data-dependent
write-path split on a green health endpoint (E1).

Triage ran three lenses in parallel, blind to each other, against this baseline.
Software-defect pulled the stack (raise site `shop.py:82`, `create_order`) and
flagged the null-price catalog condition as the mechanism. Infra-process returned a
clean domain: single startup, monotonic uptime, flat RSS, no restarts, no
degradation. Interfaces ruled out injection and intermediaries: chaos gauge 0, no
gateway-shaped statuses, stack terminating in local application arithmetic — and
independently confirmed via `GET /products` that product 4 carries `price: null`.

I sent a first hypothesis to the adversarial judge that bundled the mechanism with a
specific claim — that the three observed failing requests were themselves orders for
product 4. The judge returned **inconclusive**: the mechanism was well evidenced, but
no log line records a request body or `product_id`, so that specific attribution was
inference by elimination, not citation. Rather than force the compound claim, I split
it into two narrower hypotheses — H1 (the code mechanism, supported directly by three
identical stack traces) and H2 (the catalog fact that product 4 is the sole
null-price row, supported directly by two probes) — and reran a fresh judge. Both
validated on direct citation; the judge separately assessed the combined
elimination argument as "plausible, not proven" for naming product 4 as the trigger
of these three specific failures, given it is the only catalog row capable of
producing the observed exception. That nuance is recorded as a gap, not glossed
over. H3 (infra-process) and H4 (interfaces/injected degradation) were invalidated
by the same triage evidence.

Budget: one triage round (3 lenses), zero deep-dives, two judge rounds (the second
refining the first's finding rather than re-litigating it) — concluded within the
2-round budget.

Note for context, not evidence: this appears to be a recurring condition — a prior
investigation (2026-07-31) reached the same root cause against the same code line
and the same product, and the null price on product 4 had already been flagged as a
latent, not-yet-user-facing finding in investigations as early as 2026-08-05/08-06.
Those are prior journal artifacts, not part of this target's live telemetry surface,
so they inform framing only — every claim above is argued from this session's own
evidence (E1-E15).

## Hypotheses

### H1 — data-dependent code defect at shop.py:82 (validated)

`POST /orders` fails with an unhandled `TypeError` when `product["price"]` is
`None`. Three failures share the identical raise site and exception (E2, E4, E6),
each paired with its 500 access line (E3, E5, E7); three successes on the same
route with non-null prices show the line normally succeeds (E8-E10). The operand
order in the exception message excludes "null quantity" as an alternative reading.

### H2 — product 4 is the catalog's sole null-price row (validated)

A full 5-item catalog enumeration shows exactly one `price: null` row: id 4,
"Mystery Box", in stock (E11), confirmed by direct probe (E12). No other cited
evidence shows a second null-price product.

### H3 — process instability (invalidated)

Single startup event for the whole log (E15); uptime and RSS move monotonically
between baseline and re-probe with no reset (E13, E14); a clean 201 landed between
two 500s (E10) — instability does not selectively fail one input while serving
others correctly seconds apart.

### H4 — injected degradation / dependency / gateway (invalidated)

`faultline_chaos_enabled` is 0 at both scrapes (E13, E14); the stack terminates in
local application arithmetic, not a dependency or transport frame (E2, E4, E6); no
502/503/504 exists anywhere in the observed traffic to attribute to an
intermediary.

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- If the incident recurs, capture the customer's product selection from support
  intake alongside the timestamp, and cross-reference against a fresh
  `GET /products/{id}` taken as close to the failure as possible — the cheapest way
  to close the specific-attribution gap without any change to the target.
- Watch `http_requests_total{method="POST",path="/orders",status="500"}` and
  `http_exceptions_total{type="TypeError"}` on `/metrics`; continued growth while
  `GET /products/4` still reports `price: null` would further corroborate this
  hypothesis.
- This looks like a recurring, not one-off, condition (see Investigation) — worth
  surfacing to the service/data owner as such rather than as an isolated incident.

## Gaps

The machine core lists six. In brief: telemetry starts at boot, so onset before
that is unverifiable (1); the product-4 attribution to these three specific
requests is a closed inference, not a direct observation, and was explicitly
tested and separated from the validated mechanism/catalog claims after a first
judge round flagged the conflation (2); the catalog snapshot postdates the
failures by ~2.5 minutes (3); no read-only reproduction of a POST is possible (4);
"other customers succeed" is confirmed only for products 1 and 2, not the full
catalog (5); whether the null price is bad data or by-design is outside this
surface (6).
