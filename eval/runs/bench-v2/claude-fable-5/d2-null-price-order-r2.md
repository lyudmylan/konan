---
konan_journal: 2
investigation:
  id: 2026-11-02-orders-500-null-price
  trigger: "manual (/konan adapter; fingerprint human-1793630764; complaint startsAt 2026-11-02T14:46:04Z, investigation started 25 s later — trigger latency 25 s)"
  complaint: |-
    {"source": "human", "fingerprint": "human-1793630764", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."}, "startsAt": "2026-11-02T14:46:04Z"}
  started: "2026-11-02T14:46:29Z"
  concluded: "2026-11-02T14:53:32Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders for product 4 (Mystery Box), the catalog's only item served with price:null, deterministically raises an unhandled TypeError in create_order at shop.py line 82 (round(product[\"price\"] * order.quantity, 2) — NoneType * int), so every order attempt for that product, including retries, returns HTTP 500 while orders for non-null-price products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "Order placement fails deterministically for exactly one input: product 4 (Mystery Box) is served with price:null, and create_order multiplies that price by the quantity unguarded (shop.py line 82), raising an unhandled TypeError (NoneType * int) that returns HTTP 500 on every attempt — three unstamped user requests, 3/3 failures with the identical stack, two of them 1.07 s apart (retry-shaped) — while orders for products with non-null prices succeed in the same window, including one between the failures."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E4, E5, E6, E7, E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "The 500s on POST /orders are operator-injected degradation (chaos mode) or another internal switch, not a per-input code defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E7]
  - id: H3
    statement: "The root mechanism is corrupt catalog data — product 4's price is wrongly null in the data layer — and the 500s are a downstream symptom of that bad record."
    incident_class: data-db
    state: invalidated
    evidence_for: [E8, E9]
    evidence_against: [E11, E9, E4]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1793630790-93484 (2026-11-02T14:46:30Z) — 48.85 s back-computes to process start 2026-11-02T14:45:41Z; the process lifetime spans every failure with no restart"
    quote: |-
      {"status":"ok","uptime_seconds":48.85096958302893}
      -- HTTP 200 in 0.001930s request_id=konan-1793630790-93484
  - id: E2
    type: metric
    source: "/metrics @ request_id konan-1793630790-93489 (2026-11-02T14:46:30Z)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 49.5493188330438
      process_max_rss_bytes 48726016
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:45:41.180Z — the only startup event in the file; whole-file event census (grep): 1 startup, 16 request, 3 order_created, 3 unhandled_exception, 3 ERROR-level lines, zero chaos_enabled/chaos_disabled/chaos_failure/simulated_exception events; no rotated backups exist"
    quote: |-
      {"ts": "2026-11-02T14:45:41.180Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:45:48.147Z and .158Z — first failing order: exception line (stack trimmed to final frames) plus its access line, same request_id"
    quote: |-
      {"ts": "2026-11-02T14:45:48.147Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "ec3f0f89f915", "event": "unhandled_exception", "exception_type": "TypeError"}
        File "<checkout>/src/faultline/shop.py", line 82, in create_order
          total_price = round(product["price"] * order.quantity, 2)
                              ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~
      TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
      {"ts": "2026-11-02T14:45:48.158Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "ec3f0f89f915", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.455, "client": "127.0.0.1:58770"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:45:49.213Z and .217Z — second failing order, 1.07 s after E4; its stack is byte-identical to E4's (trimmed here), same throw site shop.py line 82"
    quote: |-
      {"ts": "2026-11-02T14:45:49.213Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "03219a5afbc7", "event": "unhandled_exception", "exception_type": "TypeError"}
      {"ts": "2026-11-02T14:45:49.217Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "03219a5afbc7", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.831, "client": "127.0.0.1:58771"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:45:52.326Z and .331Z — third failing order; stack again identical to E4's (trimmed here)"
    quote: |-
      {"ts": "2026-11-02T14:45:52.326Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "3a6daa988560", "event": "unhandled_exception", "exception_type": "TypeError"}
      {"ts": "2026-11-02T14:45:52.331Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "3a6daa988560", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.244, "client": "127.0.0.1:58773"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:45:45.037Z-14:45:51.273Z — the three successful orders (order_created plus access line each); the third succeeds between the second and third failures"
    quote: |-
      {"ts": "2026-11-02T14:45:45.037Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "c71b74461a3b", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-02T14:45:45.038Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "c71b74461a3b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.987, "client": "127.0.0.1:58768"}
      {"ts": "2026-11-02T14:45:46.092Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b8ad965a372f", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"ts": "2026-11-02T14:45:46.093Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b8ad965a372f", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.385, "client": "127.0.0.1:58769"}
      {"ts": "2026-11-02T14:45:51.272Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "00bd4004c34f", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-11-02T14:45:51.273Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "00bd4004c34f", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.267, "client": "127.0.0.1:58772"}
  - id: E8
    type: probe
    source: "GET /products @ request_id konan-1793630853-93504 (2026-11-02T14:47:33Z), full body — product 4 is the catalog's only null-price item"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001675s request_id=konan-1793630853-93504
  - id: E9
    type: probe
    source: "GET /products/4 @ request_id konan-1793630912-93545 (2026-11-02T14:48:32Z) — the read path serves the null price as a well-formed 200"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.002217s request_id=konan-1793630912-93545
  - id: E10
    type: probe
    source: "GET /orders @ request_id konan-1793630854-93509 (2026-11-02T14:47:34Z) — every stored order references a non-null-price product and its total equals price x quantity"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-02T14:45:45.037+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-02T14:45:46.092+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-02T14:45:51.272+00:00"}]
      -- HTTP 200 in 0.001362s request_id=konan-1793630854-93509
  - id: E11
    type: probe
    source: "GET /openapi.json @ request_id konan-1793631129-93593 (2026-11-02T14:52:09Z) — excerpts: every product-bearing response schema is an open object; components.schemas holds only ChaosSettings, HTTPValidationError, OrderRequest, ValidationError — no Product model, no price property, no nullability constraint anywhere"
    quote: |-
      "/products" GET 200 schema: {"items":{"additionalProperties":true,"type":"object"},"type":"array","title":"Response List Products Products Get"}
      "/products/{product_id}" GET 200 schema: {"type":"object","additionalProperties":true,"title":"Response Get Product Products  Product Id  Get"}
      "OrderRequest": {"properties":{"product_id":{"type":"integer","title":"Product Id"},"quantity":{"type":"integer","maximum":1000.0,"minimum":1.0,"title":"Quantity"}},"type":"object","required":["product_id","quantity"],"title":"OrderRequest"}
      -- HTTP 200 in 0.012948s request_id=konan-1793631129-93593
gaps:
  - "Failing POST bodies are not logged, so no log line names the product_id of a failing order; the attribution to product 4 is by elimination — the stack requires a None price at shop.py line 82 (E4) and the catalog serves exactly one null-price product (E8). The judge's airtight-closure item — a failing request body naming product_id 4 — is outside the surface: request bodies are never logged and the probe surface is GET-only."
  - "Log history begins at process start 2026-11-02T14:45:41Z (E3; no rotated backups), so whether this defect produced user-facing 500s in earlier process lifetimes is not checkable from the current surface. Past journals (2026-08-05, 2026-08-06) record the price:null as a latent catalog anomaly with no order-surface impact observed then."
  - "An internal data-layer constraint that forbids a null price — the judge's only resurrect condition for H3 — is not visible through the surface; the published OpenAPI contract declares no constraint on price (E11), and this lab has no separate database to inspect (docs/lab.md)."
  - "Traffic origin is outside the surface: the three failing requests carry only loopback client ports 58770/58771/58773 (E4, E5, E6). 'Multiple customers' is supported only as three distinct unstamped requests — whether they are several customers or one client retrying (E4->E5 is 1.07 s apart, retry-shaped) cannot be determined from target-side telemetry."
usage:
  model: claude-fable-5
  tokens: 1387191
  wall_clock_seconds: 423
---

# Order placement 500s: Mystery Box's null price trips an unhandled TypeError in create_order

## Summary

Verdict: **root-cause-identified**. Placing an order for product 4 (Mystery Box) —
the catalog's only item served with `price: null` (E8) — deterministically raises an
unhandled `TypeError` in `create_order` at `shop.py` line 82, where the handler
computes `round(product["price"] * order.quantity, 2)` with a `None` price (E4). The
request returns HTTP 500 every time, so retries fail every time, which matches the
complaint exactly: three unstamped user requests failed 3/3 with the identical stack
(E4, E5, E6), two of them 1.07 s apart (retry-shaped), while three orders for
non-null-price products succeeded in the same 8-second window — one of them *between*
the failures (E7). Chaos is off and the process ran continuously (E2, E1, E3).
Confidence: high — the counters reconcile with the log with zero residue: 3 POST 500s
= 3 TypeErrors = 3 ERROR lines, and the whole-file census leaves no unexplained
failure (E2, E3). `OrderRequest` validates only `product_id` and `quantity` (E11), so
a Mystery Box order passes input validation and always reaches the unguarded
multiplication.

## Timeline

- 2026-08-05/06 — `price: null` on product 4 first recorded as a latent catalog
  anomaly, no order-surface impact observed
  (journals/2026-08-06-products-3-user-500s.md, latent finding; context, not
  evidence for this incident).
- 2026-11-02T14:45:41.180Z — current process starts (E3); E1's uptime back-computes
  to the same instant.
- 14:45:45.037-46.093Z — two user orders succeed: product 1 x2 (total 99.0),
  product 2 x1 (total 23.0) (E7).
- **14:45:48.147/.158Z — first failing order: unhandled TypeError at shop.py line 82,
  HTTP 500, request_id ec3f0f89f915 (E4).**
- **14:45:49.213/.217Z — second failure, 1.07 s later, identical stack — the
  complaint's "keeps failing when they retry" shape (E5).**
- 14:45:51.272/.273Z — a third order succeeds (product 1) between the failures (E7).
- **14:45:52.326/.331Z — third failure, identical stack (E6).**
- 14:46:04Z — complaint raised via /konan (startsAt).
- 14:46:29Z — investigation starts (trigger latency 25 s).
- 14:46:30Z — baseline: health 200 (E1); scrape shows POST /orders 201=3 / 500=3,
  TypeError=3, chaos 0 (E2).
- 14:47:33-34Z — catalog and orders probes: product 4 is the only null-price item;
  every stored order references a non-null-price product (E8, E10).
- 14:48:32Z — /products/4: the read path serves the null price as a well-formed 200
  (E9).
- 14:52:09Z — OpenAPI probe settles the judge's H3 item: no price constraint is
  declared anywhere in the published contract (E11).
- 14:53:32Z — concluded.

## Investigation

**Baseline** (14:46:30Z): health 200 with uptime spanning every failure (E1); metrics
scrape (E2); the log read end to end — the file covers the entire process lifetime
(single startup event, no rotated backups), and a whole-file census accounts for
every line: 1 startup, 16 requests, 3 order_created, 3 unhandled_exception, 3
ERROR-level lines, zero chaos or simulated-exception events (E3). The baseline alone
contained the full failure mechanism: three identical TypeError stacks naming
shop.py line 82 and the exact operands (NoneType * int), paired 1:1 with the three
POST /orders 500s, all unstamped user traffic.

**Triage**: no lens agents were spawned — each lens domain was either excluded by
baseline evidence or already answered deterministically by it. *software-defect*: the
stack trace names the throw site and operands; the one open datum (which input
carries a None price) took two orchestrator probes (E8, E9). *infra-process*:
excluded — single clean startup, uptime continuity across the window, flat RSS,
chaos gauge 0, and zero switch/config events in a log that covers the whole process
lifetime (E1, E2, E3). *interfaces*: excluded — the failure is an in-process
application stack, and this lab's surface has no gateway, proxy, or third-party
boundary (docs/lab.md). Per the skill, the software-defect evidence was deterministic
and complete, so it went straight to the judge.

**Deep-dive round 1**: none — no evidence gap remained that a deep-dive agent could
fill from the surface.

**Judge round 1** (fresh subagent, claims plus verbatim evidence only): H1
**validated** — "the mechanism is direct, not correlational: the stack shows the
exact operands at the exact line; None * int fails on every execution, so the
determinism claim follows from the mechanism itself." H2 **invalidated** — chaos
gauge 0, zero switch events over the full process lifetime, and all three 500s
accounted for by a real code-path TypeError, leaving nothing for a switch to explain.
H3 **inconclusive** — the settling evidence named: the declared nullability contract
for `price`.

**Round 2**: the judge's settling item was reachable read-only — one probe of
/openapi.json (E11, on the probe allowlist). The published contract declares no
Product model and no `price` property; every product-bearing response schema is an
open object. Handed back to the same judge: H3 **invalidated** — "a value can only be
wrongly null against a contract term that forbids null; no such term exists," and
combined with E9 (the read path serves the null as a well-formed 200) a null price is
a contract-conformant catalog state the order code fails to handle. H1 unchanged and
strengthened: OrderRequest validates only product_id and quantity, so a product-4
order passes validation and reaches the unguarded multiplication.

**Probe accounting**: investigator traffic this session — one each of /health,
/metrics, /products, /orders, /products/4, /openapi.json, all konan-stamped GETs.
None touched the POST /orders counters; all three 500s are unstamped user traffic
(E4, E5, E6 vs E2).

**Audit note**: after all verdicts were final, the orchestrator read
journals/2026-08-06-products-3-user-500s.md from git history (past journals are the
blinding contract's stated exception) for report format; it documents product 4's
null price as a previously recorded latent anomaly. No cited claim in this journal
derives from it.

## Hypotheses

### H1 — validated (root cause): unguarded null price in create_order

The stack names the operation, line, and operand types (E4); `None * int` fails on
every execution, so determinism is mechanical, not statistical. All three failures
carry the identical signature under three distinct unstamped request ids (E4, E5,
E6); the counters reconcile exactly (E2); the catalog serves exactly one null-price
product (E8, E9); every successful order references a non-null-price product with a
total equal to price x quantity (E7, E10); and successes interleave with failures on
the same endpoint within seconds (E7 vs E5/E6), which rules out any whole-endpoint
failure mode. The contract probe (E11) closes the loop: input validation checks only
product_id and quantity, so the poisoned input always reaches line 82. The one
residual inference — no log line names product_id 4 on a failing request — is
recorded under Gaps; the judge held that it does not break the verdict because the
stack requires a None price and only one product has one.

### H2 — invalidated: injected or switch-driven degradation

The chaos gauge reads 0 (E2), the log holds zero chaos/simulated-exception events
across the entire process lifetime (E3 — and the lifetime covers the failure window,
so no earlier toggle can hide), and every 500 is explained by a real application
stack (E4, E5, E6), leaving no failure for a switch to account for. The judge's
resurrect condition — a chaos-enabled signal timestamped inside 14:45:48-52Z — has
no supporting telemetry.

### H3 — invalidated: corrupt catalog data as the root mechanism

E8/E9 prove the price *is* null, not that it is *wrongly* null. The published
contract declares no constraint on price — no Product model, no price property, only
open objects (E11) — so there is no contract term for the data to violate; and the
read path serves the null as a well-formed 200 (E9), making it a representable
catalog state. The raise happens in the service's own order-path code (E4). The
judge's only resurrect condition — an internal data-layer NOT-NULL rule invisible to
the surface — is recorded under Gaps.

## Safe next steps

- Watch `http_requests_total{method="POST",path="/orders",status="500"}` and
  `http_exceptions_total{type="TypeError"}` beyond 3 (E2 is the reference point) —
  any growth is continued user impact; unstamped request ids in the paired log lines
  distinguish customers from konan probes.
- Whether Mystery Box legitimately has no price is a question for the catalog's
  owners: the published contract permits it (E11) and the read surface serves it
  (E9), so the intended data contract — not the telemetry — decides whether the data
  or only the order code needs attention. Remediation is out of scope for this
  journal, and the lab's defects are its contract (AGENTS.md).
- If "multiple customers" needs firming beyond three distinct unstamped requests, the
  traffic source's own logs (outside this surface) would settle customers-vs-retries.
- Product 3 (Unobtainium Ingot) is still served with units_in_stock 0 (E8) — the
  input behind the already-journaled /products/3 ZeroDivisionError
  (journals/2026-08-06-products-3-user-500s.md); nothing triggered it in this
  window, but it remains live catalog state worth tracking.

## Gaps

Elaborated in the frontmatter list: the failing requests' bodies are unlogged, so
product-4 attribution rests on elimination (the judge accepted this as validated with
the closure item named); log history starts at this process's birth, so earlier
lifetimes are unobservable; an internal data-layer constraint that would resurrect H3
is outside the surface, and the published contract declares none; and the identity
behind the three failing requests (several customers vs one retrying client) is
unknowable from target-side telemetry.
