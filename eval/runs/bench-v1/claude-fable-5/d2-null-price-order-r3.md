---
konan_journal: 1
investigation:
  id: 2026-08-20-order-500s-null-price
  trigger: "manual (/konan adapter; complaint object: source=human, fingerprint=human-1787203072, labels.alertname=human-report, startsAt=2026-08-20T05:17:52Z; investigation start 2026-08-20T05:18:22Z; trigger latency 30s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-20T05:18:22Z
  concluded: 2026-08-20T05:22:51Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Orders for the catalog product with price null (product 4, 'Mystery Box') deterministically crash create_order at shop.py:82, where product[\"price\"] * order.quantity raises an unhandled TypeError, so POST /orders returns HTTP 500 on every attempt for that product while orders for priced products succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Data-dependent software defect: a catalog product carries price=null, and create_order (shop.py:82) multiplies it without a null check, raising TypeError -> 500; retries hit the same data and fail again, orders for priced products succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5]
    evidence_against: []
  - id: H2
    statement: "Injected chaos / fault injection causes the POST /orders 500s."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7]
  - id: H3
    statement: "Infrastructure/process failure (crash loop, restart, resource exhaustion, or latency degradation) causes the order failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E2]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:17:31.916Z"
    quote: "{\"ts\": \"2026-08-20T05:17:31.916Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"41b30877fd88\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"... File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\" — identical stack repeats at 2026-08-20T05:17:32.989Z (request_id 4c72b1f5b8fc) and 2026-08-20T05:17:36.123Z (request_id 9b7cc8464ce1)"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:17:31.927Z"
    quote: "{\"ts\": \"2026-08-20T05:17:31.927Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 500\", \"request_id\": \"41b30877fd88\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 11.923, \"client\": \"127.0.0.1:51963\"} — matching 500 access lines at 2026-08-20T05:17:32.994Z (duration_ms 5.206) and 2026-08-20T05:17:36.127Z (duration_ms 5.469); none carries a konan-* request id (user traffic, not investigator probes)"
  - id: E3
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787203116-78400"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3; http_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3; http_exceptions_total{type=\"TypeError\"} 3"
  - id: E4
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787203204-78443"
    quote: "HTTP 200; body includes {\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75}; products 1, 2, 3, 5 all have numeric prices — product 4 is the only null-price product"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:17:28.788Z"
    quote: "{\"ts\": \"2026-08-20T05:17:28.788Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"c53ef1dcdf2a\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 1, \"quantity\": 2, \"total_price\": 99.0} then \"POST /orders -> 201\"; same shape at 2026-08-20T05:17:29.849Z (product_id 2, total_price 23.0) and 2026-08-20T05:17:35.059Z (product_id 1, total_price 49.5); no order_created line accompanies any of the three 500s"
  - id: E6
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787203116-78400; full lab/logs/app.log (24 lines)"
    quote: "faultline_chaos_enabled 0 — and the complete log contains zero chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:17:24.715Z; /health and /metrics probes"
    quote: "{\"ts\": \"2026-08-20T05:17:24.715Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} — the only startup event; no .1–.3 log backups exist; /health uptime_seconds rose monotonically 64.7 (konan-1787203109-78394) -> 175.81 (konan-1787203220-78468); process_max_rss_bytes 49430528 unchanged between probes ~2 minutes apart"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:17:37.187Z"
    quote: "{\"ts\": \"2026-08-20T05:17:37.187Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"910361dba9af\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 1.12, \"client\": \"127.0.0.1:51968\"}"
gaps:
  - "The failed requests' product_id is not directly observed: failed POST /orders requests log no product_id (the handler dies before order_created), and the investigator surface is GET-only, so a failing POST cannot be replayed. Attribution to product 4 is inference from the TypeError requiring a null price plus product 4 being the only null-price product at probe time (probed after the failures)."
  - "The complaint's 'multiple customers' and 'retry' shape is not confirmable from telemetry: the three 500s carry three distinct request_ids and only loopback client addresses; nothing ties them to distinct customers or retries."
  - "No pre-incident history exists: the process started at 05:17:24Z and the 24-line log is the entire history, so no known-good window is available for comparison."
  - "Products 3 and 5 (numeric prices) were never ordered in the observed traffic, so 'all priced products succeed' is sampled from products 1 and 2 only."
usage:
  model: claude-fable-5
  tokens: 1653953
  wall_clock_seconds: 269
---

# Order placement returns 500 for the null-price product ("Mystery Box")

## Summary

Root cause identified. `POST /orders` fails with HTTP 500 whenever the ordered
product's catalog price is `null`: `create_order` at `faultline/src/faultline/shop.py`
line 82 computes `product["price"] * order.quantity` with no null check, which raises
an unhandled `TypeError` (E1). Exactly one catalog product has a null price — product 4,
"Mystery Box" (E4). The failure is deterministic per input, which is why the affected
customers fail on every retry, and orders for priced products succeed in the same
seconds (E5). Impact in the observed window: 3 of 6 user order attempts failed, and
the metrics account for every failure — 3× 500 = 3× TypeError, no residue (E3).
Confidence is high on the mechanism; the attribution to product 4 specifically is an
inference (see Gaps). Chaos injection is off (E6) and the process is healthy (E7, E8).

## Timeline

- 2026-08-20T05:17:24.715Z — process start, faultline 0.1.0, the only startup marker;
  no chaos or config-change markers appear anywhere in the log (E7, E6).
- 05:17:28.788Z–05:17:29.850Z — two user orders succeed (products 1 and 2) (E5).
- 05:17:31.916Z — first unhandled TypeError at shop.py:82; POST /orders → 500 (E1, E2).
- 05:17:32.989Z — second identical TypeError → 500 (E1, E2).
- 05:17:35.059Z — a user order for product 1 succeeds between the failures (E5).
- 05:17:36.123Z — third identical TypeError → 500 (E1, E2).
- 05:17:37.187Z — GET /orders → 200; the service keeps serving normally (E8).
- 05:17:52Z — complaint raised (startsAt); 05:18:22Z — investigation start (trigger
  latency 30s).
- 05:18:29Z–05:20Z — investigator probes: /health 200, /metrics, /products (E3, E4, E7).

## Investigation

- **Baseline** (05:18:22Z–05:18:36Z): /health 200 with uptime 64.7s, metrics snapshot
  showing POST /orders split 3× 201 / 3× 500 and `http_exceptions_total{type="TypeError"} 3`,
  full 24-line log tail read. The deviation from normal was already visible at baseline.
- **Triage**: all three lenses spawned in parallel (software-defect, interfaces,
  infra-process) — the complaint and baseline could not exclude any domain. The
  software-defect and interfaces lenses independently found the null-price product via
  `GET /products` (E4); the infra-process lens found a stable process and no resource
  or latency anomaly (E7, E8).
- **Deep-dive**: skipped. H1's triage evidence was deterministic and complete (exact
  crash line, exact 3/3/3 counter accounting, catalog probe); H2 and H3 were already
  killed by triage evidence. All three went straight to the judge.
- **Judge** (adversarial, evidence-only): H1 validated; H2 and H3 invalidated. The
  judge flagged the inferential leaps now recorded under Gaps.

## Hypotheses

### H1 — null-price catalog data crashes create_order (validated)

Orders for a product whose catalog `price` is `null` crash at shop.py:82
(`product["price"] * order.quantity`) with `TypeError: unsupported operand type(s)
for *: 'NoneType' and 'int'` (E1). Each TypeError maps one-to-one onto a POST /orders
500 by request_id (E2), and the counters agree exactly: 3 exceptions, 3 five-hundreds,
3 successes (E3). The error is raised on the multiplication, not the subscript — a
product record existed and its price was None, which excludes the missing-product
path. Product 4 is the only null-price product in the catalog (E4). Successes for
priced products interleave with the failures within seconds (E5), which rules out any
global or temporal cause and matches the complaint shape: the same input fails every
retry while other orders pass. No evidence stands against it.

### H2 — chaos injection (invalidated)

The chaos gauge reads 0 and the complete process log — one startup, no backups, so
the log is the whole history — contains zero chaos or simulation events (E6, E7).
The failure signature is ordinary application code failing on real data, not an
injected fault.

### H3 — infrastructure/process failure (invalidated)

One startup marker, monotonically rising uptime, flat peak RSS (E7); the service
answered normally immediately after the last failure (E8); the 500s themselves
completed in 5–12 ms (E2) — the opposite of saturation or latency degradation.

## Safe next steps

Read-only suggestions only; remediation is out of scope for this journal.

- Confirm attribution: inspect any request-body or audit record tying a failed
  request_id (41b30877fd88, 4c72b1f5b8fc, 9b7cc8464ce1) to product_id 4 — the one
  piece of evidence the judge named as settling the residual inference.
- Watch `http_exceptions_total{type="TypeError"}` and
  `http_requests_total{method="POST",path="/orders",status="500"}` — they increment
  with each further user impact.
- Audit the catalog read-only (`GET /products`) for other null or malformed fields
  that could reach the same unguarded arithmetic.

## Gaps

- **Product-4 attribution is inference, not observation.** Failed POSTs log no
  product_id and the investigator surface is GET-only, so no failing request could be
  replayed. The chain is: the TypeError requires `price=None`, and product 4 was the
  only null-price product at probe time — a catalog mutation between failure and probe
  would break the chain.
- **The complaint's customer shape is unverifiable.** Three distinct request_ids from
  loopback addresses; telemetry cannot show "multiple customers" or "retries".
- **No pre-incident baseline.** The process is 3 minutes old and the 24-line log is
  its entire history; the defect condition was present from startup ("born broken").
- **Success sampling is partial.** Only products 1 and 2 were ordered successfully;
  products 3 and 5 were never exercised by user traffic.
