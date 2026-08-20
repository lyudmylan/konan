---
konan_journal: 1
investigation:
  id: 2026-08-19-orders-null-price-500s
  trigger: "manual (/konan human profile; complaint object: source=human, fingerprint=human-1787176516, labels.alertname=human-report, startsAt=2026-08-19T21:55:16Z; investigation start 2026-08-19T21:55:24Z; trigger latency 8s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T21:55:24Z
  concluded: 2026-08-19T21:59:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders for catalog product 4 (\"Mystery Box\", price null) deterministically raises an unhandled TypeError in create_order at shop.py:82 (round(product[\"price\"] * order.quantity, 2)), returning 500 on every attempt; orders for priced products succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Orders for product 4, whose catalog price is null, fail with an unhandled TypeError at shop.py:82 in create_order; the failure is per-input deterministic, so retries fail while orders for priced products return 201."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5]
    evidence_against: []
  - id: H2
    statement: "The 500s come from injected degradation, a failing dependency, or a runtime configuration change (probabilistic per-request failure)."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E5, E6, E7]
  - id: H3
    statement: "The 500s come from process lifecycle problems (crash/restart loop), resource saturation, or latency degradation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E7, E8]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:55:04.776Z"
    quote: "{\"ts\": \"2026-08-19T21:55:04.776Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"0bb350ca8452\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"... File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"} — identical stacks for request_id 2885fe17000e @21:55:05.855Z and request_id c99e17763820 @21:55:09.000Z"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:55:04.787Z"
    quote: "{\"ts\": \"2026-08-19T21:55:04.787Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 500\", \"request_id\": \"0bb350ca8452\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 12.09, \"client\": \"127.0.0.1:49371\"} — matching 500 lines @21:55:05.860Z (2885fe17000e) and @21:55:09.004Z (c99e17763820); all three clients unstamped (non-investigator traffic)"
  - id: E3
    type: probe
    source: "/products request_id=konan-1787176656-73129"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}] -- HTTP 200"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:55:01.635Z"
    quote: "{\"ts\": \"2026-08-19T21:55:01.635Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"1d69dabd4ddb\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 1, \"quantity\": 2, \"total_price\": 99.0} — plus order_id 2 (product_id 2, total_price 23.0) @21:55:02.704Z and order_id 3 (product_id 1, total_price 49.5) @21:55:07.928Z, each followed by \"POST /orders -> 201\""
  - id: E5
    type: metric
    source: "/metrics request_id=konan-1787176540-73033 @ 2026-08-19T21:55:40Z"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3 ; http_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3 ; http_exceptions_total{type=\"TypeError\"} 3"
  - id: E6
    type: metric
    source: "/metrics request_id=konan-1787176540-73033 @ 2026-08-19T21:55:40Z"
    quote: "faultline_chaos_enabled 0"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:54:57.731Z"
    quote: "{\"ts\": \"2026-08-19T21:54:57.731Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} — the only startup event across all log files; no chaos_enabled/chaos_disabled/config/deploy markers; no 502/503/504 statuses anywhere"
  - id: E8
    type: metric
    source: "/metrics @ ~2026-08-19T21:57Z (infra-process lens scrape)"
    quote: "process_uptime_seconds 126.20096120797098 (baseline 42.905338749988005, monotonic) ; process_max_rss_bytes 48283648 (baseline 48267264) ; http_request_duration_seconds_sum{method=\"POST\",path=\"/orders\"} 0.028475457103922963 / http_request_duration_seconds_count{method=\"POST\",path=\"/orders\"} 6"
gaps:
  - "Access logs do not record the request payload, so the product_id of the three failing POSTs is inferred from the mechanism (product 4 is the only null-price product and None * int raises exactly this TypeError), not observed directly on the failing request lines."
  - "The 'keeps failing when they retry' sub-claim is consistent with three identical unstamped failures in 5 seconds but is not provable from telemetry: client identity is not logged beyond ephemeral ports."
  - "Determinism was not re-confirmed by reproduction: the investigator's probe surface is GET-only (docs/lab.md allowlist), so no POST /orders reproduction was possible; the three user-traffic failures with byte-identical stacks stand in for it."
usage:
  model: claude-fable-5
  tokens: 1422212
  wall_clock_seconds: 216
---

# Order placement returns 500 for the null-price product ("Mystery Box")

## Summary

Verdict: root cause identified. Customers who order catalog product 4 ("Mystery Box")
always get an "Internal Server Error". The catalog serves this product with
`"price": null` (E3), and `create_order` at `shop.py:82` computes
`round(product["price"] * order.quantity, 2)` without a null check, so Python raises
`TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'` (E1) and the
request ends in a 500 (E2). The failure is deterministic per input: a retry with the
same product fails again, while orders for priced products return 201 in the same
window (E4). Impact in the window observed: 3 of 6 order attempts failed (E5), all
from real user traffic, none from investigator probes. Confidence is high — the stack
trace names the exact throwing operation, the catalog shows exactly one null-price
product, and the failure/success split follows that product exactly.

## Timeline

All times UTC, 2026-08-19.

- 21:54:57.731 — service start, "faultline 0.1.0 started"; the only startup marker,
  and no config/chaos/deploy markers at any point (E7).
- 21:55:01.635 – 21:55:02.705 — two orders succeed: product 1 (order 1) and product 2
  (order 2) (E4).
- 21:55:04.776 — first failure: unhandled TypeError in `create_order` at
  `shop.py:82`, request 0bb350ca8452, POST /orders -> 500 (E1, E2).
- 21:55:05.855 — second failure, identical stack, request 2885fe17000e (E1, E2).
- 21:55:07.928 — an order for product 1 succeeds between the failures (order 3),
  which shows the route itself works (E4).
- 21:55:09.000 — third failure, identical stack, request c99e17763820 (E1, E2).
- 21:55:16 — support raises the complaint (`startsAt` of the complaint object).
- 21:55:24 — investigation starts (trigger latency 8 s).
- 21:55:38 — baseline capture: /health 200, chaos off (E6), POST /orders split
  3x201 / 3x500 (E5).

## Investigation

- **Baseline**: /health 200 with uptime consistent with the 21:54:57 startup; metrics
  showed the 3/3 split on POST /orders, `http_exceptions_total{type="TypeError"} 3`,
  chaos gauge 0; the log tail already contained the three stack traces.
- **Triage** — three lenses in parallel, each blind: software-defect, interfaces,
  infra-process. Software-defect found the throwing operation and the null-price
  product. Interfaces found the same null-price contract violation, confirmed no
  change markers and no gateway-shaped statuses, and classified the failure shape as
  deterministic per-input, not probabilistic. Infra-process reported a clean process:
  single startup, monotonic uptime, flat RSS, ~4.7 ms mean route latency.
- **Deep-dive** — skipped: the triage evidence for H1 was already deterministic and
  complete (stack trace naming the operation, catalog state, per-input split), and
  H2/H3 had direct counter-evidence.
- **Judge** — a fresh adversarial judge saw only the hypotheses and the verbatim
  evidence ledger: H1 validated; H2 and H3 invalidated. The judge flagged one
  sub-claim as inference (see Gaps): the "retries" wording is consistent with the
  telemetry but not provable from it.

## Hypotheses

### H1 — null-price product breaks create_order (validated)

Orders for product 4 fail because its catalog price is null and `create_order`
multiplies it: `round(product["price"] * order.quantity, 2)` at `shop.py:82` raises
`TypeError` (E1), which the middleware surfaces as a 500 (E2). The catalog probe (E3)
shows product 4 is the only null-price item, so every occurrence of this exact
TypeError must come from it. Successes for products 1 and 2 in the same seconds (E4)
and the exact 3x500 = 3xTypeError count match (E5) close the chain. No evidence
against was found.

### H2 — injected degradation / dependency / config change (invalidated)

The chaos gauge reads 0 (E6), the logs contain no chaos, config, flag, or deploy
markers after the single startup (E7), no 502/503/504 appears anywhere (E7), and the
failures are byte-identical application stack traces (E1) split deterministically by
input (E5) — the opposite of a probabilistic per-request fault.

### H3 — process lifecycle / saturation / latency (invalidated)

One startup event only, uptime monotonic across the incident window, RSS flat at
~48 MB, and a ~4.7 ms mean duration on the failing route (E7, E8). The 500s complete
in ~12 ms (E2) — fast application errors served by a healthy process, not timeouts or
a crash.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- Watch `http_exceptions_total{type="TypeError"}` against
  `http_requests_total{method="POST",path="/orders",status="500"}`: while they grow in
  lockstep, the incident shape is unchanged.
- Periodically probe `/products` and check for null `price` fields; the incident ends
  when product 4 carries a price or leaves the catalog, and any new null-price product
  will reproduce the same failure.
- Grep new `unhandled_exception` log lines for `shop.py`, line 82 to see whether the
  same operation keeps throwing.

## Gaps

- The failing request payloads are not logged, so "the three 500s were orders for
  product 4" is a mechanism-level inference: product 4 is the only null-price product
  (E3) and the stack shows the null multiply (E1). A payload log line with
  `product_id` on a failing request would make it direct observation.
- "It keeps failing when they retry" cannot be tied to specific customers: clients
  are logged only as ephemeral ports. The deterministic mechanism implies retries
  fail; the telemetry cannot show that the three failures were retries by the same
  customer.
- No reproduction was performed: the investigator surface is GET-only per
  `docs/lab.md`, so POST /orders cannot be probed. The three identical user-traffic
  stacks serve as the determinism evidence instead.
