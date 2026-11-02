---
konan_journal: 2
investigation:
  id: 2026-11-02-orders-500-null-price
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-02T17:53:42Z
  concluded: 2026-11-02T18:07:19Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders raises an unhandled TypeError at shop.py:82 (product[\"price\"] * order.quantity) because product_id=4 ('Mystery Box') is the only catalog entry with a null price; the catalog has no mutating endpoint anywhere in the service, so every order attempt against product 4 fails deterministically on every retry, while orders against the other four products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "POST /orders fails with an unhandled TypeError (500) for any order of product_id=4, because that catalog row has price=null and the order-creation code unconditionally computes product[\"price\"] * order.quantity; all other catalog products have numeric prices and succeed. This matches the complaint exactly: deterministic failure on retry for the affected product, no impact on orders for other products."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:20.984Z / 17:53:20.994Z"
    quote: "{\"level\":\"ERROR\",\"message\":\"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\",\"request_id\":\"c06716e35d7d\",\"event\":\"unhandled_exception\",\"exception_type\":\"TypeError\",\"stack\":\"...File \\\".../faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"} -> next line: {\"message\":\"POST /orders -> 500\",\"request_id\":\"c06716e35d7d\",\"status\":500,\"duration_ms\":10.592}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:22.055Z / 17:53:22.060Z"
    quote: "{\"level\":\"ERROR\",\"message\":\"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\",\"request_id\":\"8e6f42284c43\",\"event\":\"unhandled_exception\",\"exception_type\":\"TypeError\",\"stack\":\"...shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"} -> next line: {\"message\":\"POST /orders -> 500\",\"request_id\":\"8e6f42284c43\",\"status\":500,\"duration_ms\":5.24}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:25.171Z / 17:53:25.175Z"
    quote: "{\"level\":\"ERROR\",\"message\":\"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\",\"request_id\":\"0b4abd2f2268\",\"event\":\"unhandled_exception\",\"exception_type\":\"TypeError\",\"stack\":\"...shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"} -> next line: {\"message\":\"POST /orders -> 500\",\"request_id\":\"0b4abd2f2268\",\"status\":500,\"duration_ms\":4.993}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:17.868Z"
    quote: "{\"message\":\"order created\",\"request_id\":\"7f26781afc3d\",\"event\":\"order_created\",\"order_id\":1,\"product_id\":1,\"quantity\":2,\"total_price\":99.0} -> same ts: {\"message\":\"POST /orders -> 201\",\"request_id\":\"7f26781afc3d\",\"status\":201,\"duration_ms\":1.985}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:18.927Z"
    quote: "{\"message\":\"order created\",\"request_id\":\"5852a1c6c160\",\"event\":\"order_created\",\"order_id\":2,\"product_id\":2,\"quantity\":1,\"total_price\":23.0} -> same ts: {\"message\":\"POST /orders -> 201\",\"request_id\":\"5852a1c6c160\",\"status\":201,\"duration_ms\":1.333}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:24.119Z / 17:53:24.120Z"
    quote: "{\"message\":\"order created\",\"request_id\":\"2989bf9656be\",\"event\":\"order_created\",\"order_id\":3,\"product_id\":1,\"quantity\":1,\"total_price\":49.5} -> next: {\"message\":\"POST /orders -> 201\",\"request_id\":\"2989bf9656be\",\"status\":201,\"duration_ms\":1.514}"
  - id: E7
    type: probe
    source: "GET /products/4, request_id=konan-1793642131-98084"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200"
  - id: E8
    type: probe
    source: "GET /products, request_id=konan-1793642078-98059 (re-confirmed unchanged by two later independent probes, one ~130s and one ~190s afterward)"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}] -- HTTP 200"
  - id: E9
    type: probe
    source: "GET /orders, request_id=konan-1793642131-98078"
    quote: "[{\"id\":1,\"product_id\":1,\"quantity\":2,\"total_price\":99.0,\"created_at\":\"2026-11-02T17:53:17.868+00:00\"},{\"id\":2,\"product_id\":2,\"quantity\":1,\"total_price\":23.0,\"created_at\":\"2026-11-02T17:53:18.927+00:00\"},{\"id\":3,\"product_id\":1,\"quantity\":1,\"total_price\":49.5,\"created_at\":\"2026-11-02T17:53:24.119+00:00\"}] -- HTTP 200"
  - id: E10
    type: metric
    source: "GET /metrics, request_id=konan-1793642064-98049"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3 / http_exceptions_total{type=\"TypeError\"} 3 / faultline_chaos_enabled 0"
  - id: E11
    type: probe
    source: "GET /openapi.json, paths object"
    quote: "\"paths\":{\"/products\":{\"get\":{...}},\"/products/{product_id}\":{\"get\":{...}},\"/orders\":{\"get\":{...},\"post\":{...}},\"/orders/{order_id}\":{\"get\":{...}},\"/simulate/status/{code}\":{\"get\":{...}},\"/simulate/exception\":{\"get\":{...}},\"/simulate/slow\":{\"get\":{...}},\"/simulate/hang\":{\"get\":{...}},\"/simulate/flaky\":{\"get\":{...}},\"/simulate/crash\":{\"get\":{...}},\"/simulate/memory\":{\"get\":{...}},\"/simulate/memory/release\":{\"get\":{...}},\"/simulate/cpu\":{\"get\":{...}},\"/chaos/enable\":{\"post\":{...}},\"/chaos/disable\":{\"post\":{...}},\"/chaos\":{\"get\":{...}},\"/health\":{\"get\":{...}},\"/metrics\":{\"get\":{...}}} -- no POST/PUT/PATCH/DELETE exists for /products or /products/{product_id} anywhere in this object"
  - id: E12
    type: probe
    source: "GET /openapi.json, components.schemas.OrderRequest"
    quote: "\"OrderRequest\":{\"properties\":{\"product_id\":{\"type\":\"integer\",\"title\":\"Product Id\"},\"quantity\":{\"type\":\"integer\",\"maximum\":1000.0,\"minimum\":1.0,\"title\":\"Quantity\"}},\"type\":\"object\",\"required\":[\"product_id\",\"quantity\"],\"title\":\"OrderRequest\"}"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:53:13.976Z (sole startup/lifecycle marker in the full 32-line log file)"
    quote: "{\"ts\":\"2026-11-02T17:53:13.976Z\",\"level\":\"INFO\",\"logger\":\"faultline.app\",\"message\":\"faultline 0.1.0 started\",\"event\":\"startup\",\"version\":\"0.1.0\"}"
gaps:
  - "The three failing requests' access-log lines (E1-E3) carry no product_id field (the contract's `request` event logs method/path/status/duration/client only; the body is never logged, and the order_created line that would carry product_id is only written after the price multiplication succeeds). Attribution to product_id=4 is therefore by closed-set elimination (E7-E9, E11-E12), not a direct per-request field — the strongest link obtainable within the documented surface, confirmed by a second adversarial judge pass, but not a literal quote of 'this request ordered product 4'."
  - "Catalog state before process startup (E13, 2026-11-02T17:53:13.976Z) was not independently observed — only inferred from the absence of any mutating endpoint (E11) and from repeated identical snapshots afterward (E8). Out of reach: no access to seed data or deploy history predates the running process."
  - "product_id=3 ('Unobtainium Ingot', units_in_stock=0 per E8) was never ordered in the observed traffic. Whether an out-of-stock order produces a separate failure mode is untested and outside this complaint's scope — no evidence it is part of the active incident, so it is not reported as a finding."
  - "scripts/lab.sh status/start/stop could not be run directly (not pre-approved for this session); service availability was instead confirmed via GET /health (200, uptime climbing monotonically throughout), which was sufficient for the investigation."
usage:
  model: claude-sonnet-5
  tokens: 4706238
  wall_clock_seconds: 817
---

# Order creation 500s: null-priced catalog item ("Mystery Box", product 4) breaks POST /orders

## Summary

**Root cause identified.** `POST /orders` returns HTTP 500 for every order of product_id=4
("Mystery Box") because that catalog row has `price: null` (E7, E8) while the order-creation
code unconditionally computes `product["price"] * order.quantity` (E1-E3, stack frame at
`shop.py:82`). The catalog has no mutating endpoint anywhere in the service (E11), and the
order request body carries only `product_id`/`quantity` (E12) — so this is not a transient
or environmental failure, it is a deterministic, 100%-reproducible defect for exactly one
product. This explains both halves of the complaint precisely: "it keeps failing when they
retry" (same input, same crash, every time) and "other customers' orders are going through
fine" (any other product's order succeeds — E4-E6, E9). No chaos/degradation switch, process
restart, resource exhaustion, or external dependency was involved (E10, E13). Confidence:
high — validated by two independent adversarial judge passes, the second closing the one
open evidentiary gap (see Hypotheses, Gaps).

## Timeline

- **2026-11-02T17:53:13.976Z** — faultline process starts; the only lifecycle/startup marker
  in the entire log (E13). No restart, crash, or config-change marker appears at any later
  point in the investigation window.
- **2026-11-02T17:53:17.868Z / 17:53:18.927Z** — two orders succeed (product_id 1, product_id
  2) — E4, E5.
- **2026-11-02T17:53:20.984Z** — first `TypeError` / 500 on `POST /orders` — E1.
- **2026-11-02T17:53:22.055Z** — second identical `TypeError` / 500 — E2.
- **2026-11-02T17:53:24.119Z** — a third order succeeds (product_id 1) — E6.
- **2026-11-02T17:53:25.171Z** — third identical `TypeError` / 500 — E3.
- **2026-11-02T17:53:34Z** — complaint `startsAt` (human report filed via `/konan`).
- **2026-11-02T17:53:42Z** — investigation started (trigger latency ≈ 8s).
- **2026-11-02T17:54:21Z onward** — investigator baseline probes begin (`/health`, `/metrics`,
  `/products`, `/orders`, `/products/4`, `/openapi.json`); all `konan-`-prefixed, read-only,
  no new order attempts generated by the investigation itself.
- **2026-11-02T18:07:19Z** — investigation concluded.

## Investigation

1. **Baseline** (`GET /health`, `GET /metrics`, log tail): service up, uptime climbing
   monotonically, but the very first `/metrics` read already showed a 3/3 split between
   `POST /orders` 201s and 500s, all three 500s tagged `exception_type="TypeError"` (E10) —
   the incident signal was present in the baseline itself.
2. **Triage** — all three lenses spawned in parallel, each blind to the others, each given
   only its lens file, the surface contract, the complaint, and the baseline summary:
   - *infra-process*: no anomalies — single startup, monotonic uptime, flat RSS, no
     latency deterioration, chaos toggle off throughout.
   - *interfaces*: no gateway-shaped statuses, no config/chaos markers, confirmed the 3/6
     split tracks a specific input rather than a probabilistic/injected pattern — pointed
     the mechanism toward software-defect territory.
   - *software-defect*: identified the exact mechanism — null-price catalog row, deterministic
     per-input failure, single route, single exception type.
   All three lenses converged with no disconfirming evidence, so the resulting hypothesis
   (H1) had deterministic, complete triage evidence and skipped deep-dive per the loop's
   explicit shortcut for that case.
3. **Judge, round 1**: verdict **inconclusive**. The mechanism (null price → TypeError → 500)
   was accepted as solid, but the judge flagged that the three failing requests' access-log
   lines carry no `product_id` field, so tying those specific failures to product 4 rested
   on elimination, not direct citation — and named two unstated assumptions (catalog stability
   over time; possibility of another code path producing a null price).
4. **Targeted follow-up**: fetched the full `/openapi.json` spec (E11, E12). It shows the
   catalog has no mutating endpoint anywhere (`/products` and `/products/{product_id}` are
   GET-only in the entire route table) and that `OrderRequest` carries only `product_id` and
   `quantity` — no other path can set a product's price. This closes both gaps: the catalog
   cannot have changed since process startup (no code path to write it), and the order path's
   only source of `price` is the catalog lookup keyed by `product_id`.
5. **Judge, round 2**: given E1-E13 together, verdict **validated**. The judge additionally
   noted the exception message itself (`unsupported operand type(s) for *: 'NoneType' and
   'int'`) proves the catalog lookup succeeded and returned a dict with `price: None` — ruling
   out an invalid/nonexistent `product_id`, which would instead raise on subscripting `None`
   itself with a different message.

## Hypotheses

### H1 — validated

`POST /orders` fails with an unhandled `TypeError` (500) for any order of `product_id=4`,
because that catalog row has `price: null` and the order-creation code unconditionally
computes `product["price"] * order.quantity` (E1-E3). All other catalog products carry
numeric prices and their orders succeed (E4-E6, confirmed persisted in E9). The catalog
has no mutating endpoint anywhere in the service (E11) and the order request body carries
no price data of its own (E12), so the null price is a fixed property of the catalog for
the life of the process, not a transient or injected condition (E10, E13 rule out chaos,
restarts, and resource exhaustion as contributing factors).

Evidence for: E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13. Evidence against: none
found.

## Safe next steps

- Keep monitoring `http_exceptions_total{type="TypeError"}` and
  `http_requests_total{method="POST",path="/orders",status="500"}` — a rising count beyond
  the baseline 3 would indicate the same defect continuing to fire, or a second input hitting
  it.
- `GET /products` lets support confirm, for any future complaint, whether the ordered
  product currently has `price: null` before escalating further — a fast, read-only
  discriminator between "this known defect" and a new issue.
- Worth a read-only follow-up check on `product_id=3` ("Unobtainium Ingot",
  `units_in_stock: 0`): no order against it was observed in this window, so whether it has
  its own failure mode is unknown and untested (see Gaps) — not claimed as part of this
  incident.

## Gaps

- The three failing requests' access-log lines (E1-E3) carry no `product_id` field (the
  contract's `request` event logs method/path/status/duration/client only; the body is never
  logged, and the `order_created` line that would carry `product_id` is only written after
  the price multiplication succeeds). Attribution to `product_id=4` is therefore by
  closed-set elimination (E7-E9, E11-E12), not a direct per-request field — the strongest
  link obtainable within the documented surface, confirmed by a second adversarial judge
  pass, but not a literal quote of "this request ordered product 4."
- Catalog state before process startup (E13) was not independently observed — only inferred
  from the absence of any mutating endpoint (E11) and from repeated identical snapshots
  afterward (E8). Out of reach: no access to seed data or deploy history predates the
  running process.
- `product_id=3` ("Unobtainium Ingot", `units_in_stock: 0` per E8) was never ordered in the
  observed traffic. Whether an out-of-stock order produces a separate failure mode is
  untested and outside this complaint's scope — no evidence it is part of the active
  incident, so it is not reported as a finding.
- `scripts/lab.sh status/start/stop` could not be run directly (not pre-approved for this
  session); service availability was instead confirmed via `GET /health` (200, uptime
  climbing monotonically throughout), which was sufficient for the investigation.
