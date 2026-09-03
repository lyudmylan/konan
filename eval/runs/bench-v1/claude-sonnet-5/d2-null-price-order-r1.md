---
konan_journal: 1
investigation:
  id: 2026-08-19-orders-500-null-price
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T00:58:32Z
  concluded: 2026-08-19T01:03:22Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders raises an unhandled TypeError and returns 500 whenever the order references a catalog product whose price is null (product_id=4, \"Mystery Box\"), because faultline/src/faultline/shop.py:82 multiplies product[\"price\"] by order.quantity with no null check."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Orders referencing product_id=4 (null price in the catalog) crash create_order with TypeError at shop.py:82, returning 500; every retry of the same order repeats the identical crash, while orders for other (priced) products succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by randomly injected chaos/fault-injection rather than a code defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E7]
  - id: H3
    statement: "The 500s are caused by process instability: a crash/restart loop or resource saturation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10]
  - id: H4
    statement: "The 500s are caused by an upstream/dependency failure, a gateway timeout, or a recent configuration/deploy change."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E5, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T00:58:21.098Z"
    quote: "{\"ts\": \"2026-08-19T00:58:21.098Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"53dfc2310765\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"...File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\n...TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T00:58:21.109Z, 00:58:22.169Z, 00:58:25.294Z"
    quote: "{\"ts\": \"2026-08-19T00:58:21.109Z\", \"message\": \"POST /orders -> 500\", \"request_id\": \"53dfc2310765\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 11.554} — identical shape repeats for request_id 5ab17fce13fb @ 00:58:22.173Z and fcdbd63e58f4 @ 00:58:25.298Z, each immediately preceded by the same unhandled_exception stack as E1"
  - id: E3
    type: probe
    source: "scripts/probe.sh /products, request_id konan-1787101157-35267"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E4
    type: probe
    source: "scripts/probe.sh /products/4, request_id konan-1787101306-35384"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E5
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787101142-35248"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3"
  - id: E6
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787101142-35248"
    quote: "http_exceptions_total{type=\"TypeError\"} 3"
  - id: E7
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787101142-35248"
    quote: "faultline_chaos_enabled 0"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T00:58:17.979Z–00:58:24.233Z"
    quote: "order_created order_id 1 product_id 1 (00:58:17.979Z); order_id 2 product_id 2 (00:58:19.038Z); order_id 3 product_id 1 (00:58:24.232Z) — each immediately followed by \"POST /orders -> 201\" for the same request_id; no order_created line exists for request_ids 53dfc2310765, 5ab17fce13fb, or fcdbd63e58f4"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T00:58:14.064Z"
    quote: "{\"ts\": \"2026-08-19T00:58:14.064Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E10
    type: metric
    source: "ls -la lab/logs/ (single file, no rotated backups) and three scripts/probe.sh /metrics probes at 00:59:02Z, ~01:00Z, 01:01:41Z"
    quote: "lab/logs/ contains only app.log (no .1–.3 backups); process_uptime_seconds read 48.50680887512863, then 207.32111545908265 across the two probes the orchestrator ran directly — monotonically increasing from the single E9 start, no reset"
  - id: E11
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787101301-35377 (final probe before conclusion)"
    quote: "http_exceptions_total{type=\"TypeError\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3 — unchanged from the first /metrics probe, confirming no new order attempts or exceptions occurred during the investigation window"
gaps:
  - "The three failing request bodies are never logged (order_created only fires on success), so request_ids 53dfc2310765, 5ab17fce13fb, and fcdbd63e58f4 are not directly tied to product_id=4 by a logged field — the link is by elimination (product 4 is the only null-priced catalog item, and the only product unaccounted for among the three successful orders in E8). A direct repro (POST /orders for product_id=4) would close this gap but POST is outside the investigator's read-only surface (scripts/probe.sh is GET-only per docs/lab.md)."
  - "Whether product 4's null price is an isolated data-entry error or reflects a wider catalog-ingestion defect (e.g. other products intermittently losing price data) could not be checked — the surface contract exposes no catalog-write history or ingestion logs, only the current snapshot."
  - "The complaint's 'multiple customers' scale could not be independently sized — the visible log window shows only 6 POST /orders total (3 failing, 3 succeeding) from investigation-adjacent traffic; there is no user/session identifier in the log schema to distinguish distinct customers from repeated retries by the same customer."
usage:
  model: claude-sonnet-5
  tokens: 2233504
  wall_clock_seconds: 290
---

# POST /orders 500s: null-priced catalog item crashes order creation

## Summary

**Root cause identified.** Orders for one specific catalog product — id 4, "Mystery
Box" — fail every time with `HTTP 500` because that product's `price` field is `null`
and `faultline/src/faultline/shop.py:82` computes `total_price = round(product["price"]
* order.quantity, 2)` with no null check, raising an unhandled `TypeError`. This is a
deterministic, data-dependent defect (E1–E4): every order for product 4 fails, every
retry of the same order fails identically (matches "keeps failing when they retry"),
while orders for the other four products — all of which have numeric prices — succeed
(matches "other customers' orders are going through fine"). Chaos injection, process
crash/restart, resource saturation, and upstream/dependency/config-change causes were
all checked and ruled out (E5–E11). Confidence is high; the one residual gap (below)
does not change the mechanism, only the exact request-to-product linkage.

## Timeline

- **00:58:14.064Z** (E9) — faultline process starts; the only startup marker in the
  visible log, and `lab/logs/` holds no rotated backups (E10), so no prior crash
  history is hidden.
- **00:58:17.979Z–00:58:24.233Z** (E8) — three orders succeed (product_id 1, 2, 1),
  each returning `201`.
- **00:58:21.098Z, 00:58:22.169Z, 00:58:25.294Z** (E1, E2) — three orders crash with an
  identical `TypeError` at `shop.py:82` and return `500`.
- **~00:59:02Z–01:03:22Z** — investigation window: `/products` (E3) and `/products/4`
  (E4) show product 4's price is `null`; repeated `/metrics` probes (E5–E7, E11) show
  the counts frozen at 3/3 with `faultline_chaos_enabled 0`, and process uptime
  climbing monotonically (E10) — no new order traffic, no new exceptions, no restart.

## Investigation

- **Baseline** (`/health`, `/metrics`, log tail): revealed the anomaly immediately —
  `POST /orders` split 3×`201`/3×`500`, `http_exceptions_total{type="TypeError"}` at 3,
  and a repeated, identical stack trace pinpointing `shop.py:82`.
- **Triage** — three lenses spawned in parallel, each given only the lens file, the
  contract, the complaint, and the baseline summary:
  - *software-defect*: found the null-price/TypeError mechanism directly (E1–E4, E8).
  - *infra-process*: no restart loop, no RSS growth, no latency deterioration, uptime
    consistent with a single process lifetime (E9, E10).
  - *interfaces*: no config/deploy markers, no gateway-shaped statuses, failure pattern
    tied to input not a stable random fraction — ruled out this domain (E5, E9).
- **Deep-dive skipped**: the software-defect lens's evidence was already deterministic
  and complete (exact line, exact null value, exact correlation between successes and
  priced products) — per protocol this goes straight to judge rather than re-proving.
- **Judge**: given only the hypothesis list and verbatim evidence (no lens narrative).
  Validated H1, invalidated H2/H3/H4, and flagged one gap (below) — the failing request
  bodies aren't logged, so the product_id=4 link is by elimination, not a direct quote.

## Hypotheses

### H1 — null-priced product crashes order creation (validated)
`product["price"] * order.quantity` at `shop.py:82` throws `TypeError` when `price` is
`None` (E1). Product 4 is the only catalog item with `price: null` (E3, E4).
`http_requests_total` and `http_exceptions_total` counts match one-to-one: 3 failures,
3 `TypeError`s (E5, E6). The three successful orders logged their `product_id` as 1, 2,
1 — never 4 (E8) — leaving product 4 as the only unaccounted-for input among the
failures. Chaos was off throughout (E7), so this is not injected.

### H2 — random chaos injection (invalidated)
`faultline_chaos_enabled 0` (E7) and an identical, non-varying stack trace on every
occurrence (E1) both argue against randomized fault injection.

### H3 — process crash/restart or resource saturation (invalidated)
Only one startup marker exists, with no rotated logs hiding earlier ones (E9, E10);
uptime increased monotonically across three probes taken minutes apart, never resetting
(E10) — inconsistent with a restart loop or a saturation-driven degradation.

### H4 — upstream/dependency failure, gateway timeout, or config change (invalidated)
The 500s carry full in-process Python tracebacks rooted in the app's own file, not a
502/503/504 gateway shape (E1, E2, E5). The only marker in the log is the startup event
that precedes all traffic in the window — no mid-window config/deploy marker exists
(E9).

## Safe next steps

- Read the faultline product catalog's source of truth (outside this investigation's
  reach) to confirm whether product 4's null price is a one-off data error or a wider
  ingestion gap.
- Watch `http_exceptions_total{type="TypeError"}` and `http_requests_total{...,
  path="/orders",status="500"}` on `/metrics` for further growth — a rising count would
  indicate more customers reaching product 4, not a new defect.
- If support tooling allows it, correlate customer-reported order attempts with the
  specific product they were ordering ("Mystery Box") to confirm the elimination-based
  link in this journal without an investigator-side repro.

## Gaps

- The three failing requests never logged their request bodies (`order_created` only
  fires on success), so `product_id=4` is inferred by elimination — it's the only
  null-priced catalog item and the only product not accounted for among the three
  successful orders — rather than read directly off a failing request. Confirming via a
  live repro was out of reach: `scripts/probe.sh` is GET-only per `docs/lab.md`, and
  `POST /orders` sits outside the investigator's allowlisted, read-only surface.
- Whether the null price on product 4 is an isolated data-entry mistake or a symptom of
  a broader catalog-ingestion defect could not be checked; the surface contract exposes
  only the current catalog snapshot, not write/ingestion history.
- The complaint's "multiple customers" scale could not be sized independently — the log
  schema carries no customer/session identifier, and the visible window shows only 6
  total `POST /orders` calls near the investigation.
