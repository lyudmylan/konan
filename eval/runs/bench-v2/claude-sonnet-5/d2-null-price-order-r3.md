---
konan_journal: 2
investigation:
  id: 2026-11-02-orders-product-4-500s
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-02T18:23:59Z
  concluded: 2026-11-02T18:30:29Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "create_order (faultline/src/faultline/shop.py:82) multiplies product[\"price\"] by the order quantity without a null check; product id 4 (\"Mystery Box\") has price=null, so every order for that product raises an unhandled TypeError and returns HTTP 500, while orders for any other (non-null-price) product succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "create_order (shop.py:82) multiplies product[\"price\"] by order.quantity without guarding against a null price; product id 4 (\"Mystery Box\", price=null) fails every order attempt with an unhandled TypeError/500, while all other products (non-null price) succeed — a deterministic, retry-proof, per-product defect."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E5, E6, E7, E8, E9]
    evidence_against: []
evidence:
  - id: E1
    type: metric
    source: "/metrics probe, request_id konan-1793643896-99065"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3"
  - id: E2
    type: metric
    source: "/metrics probe, request_id konan-1793643896-99065"
    quote: "http_exceptions_total{type=\"TypeError\"} 3"
  - id: E3
    type: metric
    source: "/metrics probe, request_id konan-1793643896-99065"
    quote: "faultline_chaos_enabled 0"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:23:38.083Z"
    quote: "{\"event\": \"startup\", \"message\": \"faultline 0.1.0 started\", \"version\": \"0.1.0\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:23:45.073Z (also 18:23:46.141Z, 18:23:49.258Z)"
    quote: "\"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"exception_type\": \"TypeError\" ... File \"shop.py\", line 82, in create_order\\n    total_price = round(product[\"price\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:23:41.956Z, 18:23:43.015Z, 18:23:48.201Z"
    quote: "\"event\": \"order_created\", \"order_id\": 1, \"product_id\": 1 / \"event\": \"order_created\", \"order_id\": 2, \"product_id\": 2 / \"event\": \"order_created\", \"order_id\": 3, \"product_id\": 1"
  - id: E7
    type: probe
    source: "/products, request_id konan-1793643909-99076"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,...},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,...},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,...},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,...}]"
  - id: E8
    type: probe
    source: "/products/4, request_id konan-1793643918-99081"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E9
    type: probe
    source: "/orders, request_id konan-1793643918-99084"
    quote: "[{\"id\":1,\"product_id\":1,...},{\"id\":2,\"product_id\":2,...},{\"id\":3,\"product_id\":1,...}]"
gaps:
  - "The failing product_id was not read directly off a log line (the unhandled-exception event does not carry the request body/product_id). It is established by closed-world elimination: 6 total POST /orders attempts (E1), 3 of which are fully accounted for as successes against product_id 1, 2, 1 (E6, E9), leaving the 3 TypeError failures (E5) to the remaining attempts; the catalog (E7) has exactly one null-price product (id 4), and the operand-type error names \"price\" (the left operand of the multiply) as the None value. No competing explanation is left open by the evidence, but this is inference, not direct observation."
  - "No live reproduction of POST /orders with product_id=4 was attempted: the surface contract (docs/lab.md) restricts the investigator to GET-only probes; POST is outside the allowlist. Determinism rests on three independent, time-separated identical traces (E5), not a fresh repro."
  - "Latency/resource-saturation checks (infra-process lens) had only a single-point RSS snapshot (no prior baseline to diff against); ruled out as unlikely given the exception is a clean application-level TypeError, not resource exhaustion, but not exhaustively excluded."
usage:
  model: claude-sonnet-5
  tokens: 2544903
  wall_clock_seconds: 390
---

# POST /orders 500s on "Mystery Box" (product id 4) — null price crashes create_order

## Summary

**Root cause identified.** Every order for product id 4 ("Mystery Box") fails with HTTP 500
and will keep failing on retry: `create_order` (`faultline/src/faultline/shop.py:82`)
computes `total_price = round(product["price"] * order.quantity, 2)` with no guard against
a null price, and product 4's `price` field is `null` (E7, E8). The multiply raises an
unhandled `TypeError`, logged identically three separate times (E5), each immediately
followed by `POST /orders -> 500`. Orders for every other product (non-null price) succeed
normally (E6, E9) — matching the complaint exactly: some customers' orders go through fine
while others always fail, and retrying does not help because the defect is deterministic
per product, not transient. Chaos injection is off (E3) and the process shows a single
clean lifecycle with no restart (E4), ruling out infra/chaos causes. Confidence: high for
the mechanism (direct stack-trace evidence); the specific attribution to product id 4 rests
on closed-world elimination rather than a log line naming the product directly (see Gaps).

## Timeline

- **18:23:38.083Z** — process startup, single clean lifecycle (E4).
- **18:23:41.956Z** — order_created, product_id 1 → `POST /orders -> 201` (E6, E9 order id 1).
- **18:23:43.015Z** — order_created, product_id 2 → `POST /orders -> 201` (E6, E9 order id 2).
- **18:23:45.073Z** — unhandled TypeError, `shop.py:82`, → `POST /orders -> 500` (E5).
- **18:23:46.141Z** — identical unhandled TypeError → `POST /orders -> 500` (E5).
- **18:23:48.201Z** — order_created, product_id 1 → `POST /orders -> 201` (E6, E9 order id 3).
- **18:23:49.258Z** — identical unhandled TypeError → `POST /orders -> 500` (E5).
- **Investigation probes** (18:24:53Z–18:25:18Z): `/health`, `/metrics` (E1–E3), `/products`
  (E7) and `/products/4` (E8) confirm product 4 is the only null-priced catalog entry and
  has never had a successful order (`units_ordered: 0`); `/orders` (E9) confirms the 3
  persisted orders are fully accounted for by products 1 and 2.

## Investigation

- **Baseline**: `/health`, `/metrics`, and the `lab/logs/app.log` tail were captured first
  (E1–E6). The metrics snapshot already showed the full shape of the incident: POST
  /orders split exactly 3×201 / 3×500, with `http_exceptions_total{type="TypeError"}=3`
  and chaos disabled.
- **Triage** (3 lenses, parallel, blind to each other, given only the lens file, the
  surface contract, the verbatim complaint, and this baseline):
  - *infra-process*: no anomalies — single clean startup, uptime climbing monotonically,
    chaos toggle off, no restart/saturation signal.
  - *interfaces*: no anomalies — no gateway-shaped statuses, no probabilistic failure
    pattern, no config/chaos change marker in the log, no contract violation (the
    `OrderRequest` schema doesn't declare price nullability, so this isn't a schema
    breach visible at the interface).
  - *software-defect*: found the TypeError stack trace pinpointing `shop.py:82`, the
    null-priced product 4, and the route/exception-type confinement (no other errors,
    no other exception types).
- **Deep-dive**: skipped — the triage evidence was already deterministic and complete
  (stack trace naming the exact line and operand, a closed catalog with exactly one
  null-price product, and counts that fully reconcile), so the hypothesis went straight
  to judgment rather than re-proving itself.
- **Judge** (adversarial, evidence-only, blind to the narrative above): verdict
  **validated**. The judge confirmed the operand-type error names `price` (not quantity)
  as the `None` operand, confirmed the success/failure counts fully reconcile with no
  slack, and confirmed no alternative cause is left open by the evidence. It flagged one
  soft point — product-id attribution for the failures is elimination, not a direct log
  field — which is carried into Gaps below rather than treated as grounds for
  "inconclusive," since no competing account of the three failures exists in the evidence.

## Hypotheses

### H1 — null-price multiply in `create_order` (validated)

**Statement**: `create_order` (`shop.py:82`) multiplies `product["price"] * order.quantity`
without checking for null; product id 4 ("Mystery Box") has `price: null`, so every order
for it raises an unhandled TypeError and 500s, while all other products succeed.

**For**: The stack trace (E5) names the exact file, line, and operation, and the
operand-type error's first-named type is the left operand (`product["price"]`), pinning
the null to the price field. The catalog (E7, E8) shows product 4 is the only null-priced
entry and has zero successful orders ever. The success side (E6, E9) fully accounts for
all 3 successful orders against products 1 and 2, leaving the 3 failures with no other
candidate product. Chaos is off (E3) and the process lifecycle is clean (E4), excluding
infra/chaos alternatives.

**Against**: none found. The one open point — no log line directly tags the failing
requests with `product_id: 4` — is a gap in observability, not evidence against the
hypothesis (see Gaps).

## Safe next steps

- Keep watching `http_exceptions_total{type="TypeError"}` and the POST /orders 500 count
  on `/metrics` — if it climbs beyond multiples of attempts against product 4, that would
  indicate either new customers hitting the same product or (if so) a second null-price
  product, both discoverable read-only via `/products`.
- If support can supply the product customers were ordering when they hit the error, cross-
  check it against `/products` for a null (or otherwise malformed) price — read-only
  confirmation without needing a code change.
- Consider asking whoever owns `faultline` to add request-scoped product/quantity fields
  to the `unhandled_exception` log event, which would close the attribution gap below for
  future incidents (observation suggestion only — no code change made or recommended here).

## Gaps

- Product-id attribution for the three failing requests is inferred by closed-world
  elimination (E1, E6, E7, E9), not read directly from a log field — the
  `unhandled_exception` event does not carry the request body. No competing explanation is
  left open by the evidence, but this is inference, not direct observation.
- No live reproduction of `POST /orders` against product id 4 was attempted: the surface
  contract (`docs/lab.md`) allows the investigator GET-only probes against an allowlist
  that excludes POST, so a fresh repro was out of reach by design. Determinism rests on
  three independent, time-separated, identical in-log traces instead.
- Resource-saturation checks (RSS, CPU) had only one point-in-time snapshot with no prior
  baseline to diff against; saturation is considered unlikely (the failure is a clean,
  named application exception, not a timeout or resource error) but was not exhaustively
  excluded by trend data.
