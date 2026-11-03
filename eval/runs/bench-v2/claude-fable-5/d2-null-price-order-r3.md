---
konan_journal: 2
investigation:
  id: 2026-11-02-order-500s-null-price
  trigger: "manual — /konan adapter, human complaint; alertname human-report, fingerprint human-1793631498, startsAt 2026-11-02T14:58:18Z; investigation start 2026-11-02T14:58:40Z (trigger latency 22s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-02T14:58:40Z
  concluded: 2026-11-02T15:05:26Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's own order-creation code raises an unhandled TypeError when it multiplies a null product price by the ordered quantity; the null-priced catalog record (product 4, \"Mystery Box\") makes the failure deterministic for every order of that product, while orders for priced products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order-creation handler (create_order, shop.py line 82) multiplies product[\"price\"] by the ordered quantity with no guard for a null price; catalog product 4 (\"Mystery Box\", price null, 75 units in stock) deterministically raises an unhandled TypeError, so every POST /orders for that product returns HTTP 500 on first try and on every retry, while orders for priced products return 201."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "An injected degradation switch (chaos mode) inside the target causes the order 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5]
  - id: H3
    statement: "Process instability — crash loop, restarts, or resource exhaustion — causes the order failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E14, E15, E16, E17]
  - id: H4
    statement: "A deploy or configuration change at some time T broke order placement (worked until T, fails after T)."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E11, E14]
latent_findings:
  - statement: "The published API contract does not constrain product price to a number: /openapi.json declares the /products response items as an open object, so a null price does not violate the declared schema — the catalog can legally serve the value that crashes the order path."
    evidence: [E18, E12]
evidence:
  - id: E1
    type: metric
    source: "GET /metrics @ 2026-11-02T14:58:57Z (probe konan-1793631537-93789)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
  - id: E2
    type: metric
    source: "GET /metrics @ 2026-11-02T14:58:57Z (probe konan-1793631537-93789)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E3
    type: metric
    source: "GET /metrics @ 2026-11-02T14:58:57Z (probe konan-1793631537-93789)"
    quote: |-
      http_exceptions_total{type="TypeError"} 3
  - id: E4
    type: metric
    source: "GET /metrics @ 2026-11-02T14:58:57Z (probe konan-1793631537-93789)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:57:59.221Z (stack trimmed to its last frame)"
    quote: |-
      {"ts": "2026-11-02T14:57:59.221Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "a10ad829ba48", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last): … File \"…/faultline/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:58:00.288Z (trimmed; stack identical to E5)"
    quote: |-
      {"ts": "2026-11-02T14:58:00.288Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "d6d64ff1615d", "event": "unhandled_exception", "exception_type": "TypeError", …}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:58:03.421Z (trimmed; stack identical to E5)"
    quote: |-
      {"ts": "2026-11-02T14:58:03.421Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "f9efe87f2166", "event": "unhandled_exception", "exception_type": "TypeError", …}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:57:59.232Z"
    quote: |-
      {"ts": "2026-11-02T14:57:59.232Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "a10ad829ba48", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 12.145, "client": "127.0.0.1:58851"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:57:56.090Z"
    quote: |-
      {"ts": "2026-11-02T14:57:56.090Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "09e004ee249b", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:57:57.156Z"
    quote: |-
      {"ts": "2026-11-02T14:57:57.156Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "98e648d900d8", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:58:02.354Z"
    quote: |-
      {"ts": "2026-11-02T14:58:02.354Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "d51aa2753177", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E12
    type: probe
    source: "GET /products (probe konan-1793631570-93805, HTTP 200 in 0.005157s)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E13
    type: probe
    source: "GET /products/4 (probe konan-1793631692-93895, HTTP 200; run by the interfaces triage lens)"
    quote: |-
      "id":4,"name":"Mystery Box","price":null
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:57:52.227Z (the only startup event in the log; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-02T14:57:52.227Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E15
    type: metric
    source: "GET /metrics @ 2026-11-02T14:58:57Z (probe konan-1793631537-93789)"
    quote: |-
      process_uptime_seconds 65.63447983306833
  - id: E16
    type: probe
    source: "GET /health @ ~2026-11-02T15:01:08Z (probe konan-1793631667-93854, HTTP 200; run by the infra-process triage lens)"
    quote: |-
      {"status":"ok","uptime_seconds":195.5}
  - id: E17
    type: metric
    source: "GET /metrics @ 2026-11-02T14:58:57Z (probe konan-1793631537-93789); the infra-process lens read the same value again at ~15:01:08Z"
    quote: |-
      process_max_rss_bytes 48939008
  - id: E18
    type: probe
    source: "GET /openapi.json (probe konan-1793631693-93900, HTTP 200; run by the interfaces triage lens) — /products response item schema"
    quote: |-
      {"additionalProperties": true, "type": "object"}
gaps:
  - "The failed POST /orders requests' bodies and product ids are not logged (product_id appears only in order_created success events), so the link from the TypeError to product 4 rests on inference: the error proves the ordered product's price was None (E5), and product 4 is the only catalog record with a null price (E12). A captured failing request body would turn this into direct proof."
  - "The catalog was probed at 14:59:30Z (E12), about 90 seconds after the failure window (14:57:59–14:58:03Z); a transient null price on a different product during the window cannot be excluded from this surface."
  - "No reproduction was possible: POST /orders is outside the read-only probe allowlist by design, so confirmation rests on telemetry of user traffic only."
  - "No pre-startup history: the process started at 14:57:52.227Z (E14), no rotated log backups (app.log.1–.3) exist, and the metrics counters begin at startup — whether the null price predates this process start is unobservable."
  - "The chaos gauge was read after the failure window, not during it (E4); the absence of chaos_enabled/chaos_disabled/chaos_failure events anywhere in the log closes this only if toggles always log."
usage:
  model: claude-fable-5
  tokens: 1283988
  wall_clock_seconds: 406
---

# Order placement returns 500 for every attempt on the null-priced product 4 ("Mystery Box")

## Summary

Root cause identified, high confidence. Order creation (`POST /orders`) crashes with an
unhandled `TypeError` at `create_order` (shop.py line 82) when it computes
`product["price"] * order.quantity` for a product whose price is `null` — and the catalog
holds exactly one such product: id 4, "Mystery Box", 75 units in stock (E12, E13). The
failure is deterministic per input: every order for product 4 returns HTTP 500, on the
first try and on every retry, which matches the complaint exactly ("it keeps failing when
they retry"). Orders for priced products succeed throughout the window (E9–E11). In the
observed window, 3 of 6 real order attempts failed (E1, E2) — all of them user traffic,
none investigator probes (E8). Chaos mode is off (E4), the process is stable (E14–E17),
and no change event precedes the failures (E14), so nothing competes with the data-
dependent defect. The 500 counter had not grown between 14:58:03Z and the last check at
~15:01Z, but the defect remains armed for any customer who orders product 4.

## Timeline

- **14:57:52.227Z** — faultline 0.1.0 starts; the only change-shaped marker in the log (E14).
- **14:57:56.090Z / 14:57:57.156Z** — orders 1 and 2 created (products 1 and 2), 201 (E9, E10).
- **14:57:59.221Z** — first unhandled `TypeError` at shop.py:82; the request returns 500 in 12.1 ms (E5, E8).
- **14:58:00.288Z** — second identical failure, one second later — consistent with an immediate retry failing the same way (E6).
- **14:58:02.354Z** — order 3 created (product 1), 201, *between* the failures (E11).
- **14:58:03.421Z** — third identical failure (E7).
- **14:58:18Z** — human complaint raised via support (`startsAt`).
- **14:58:40Z** — investigation starts (trigger latency 22 s).
- **14:58:57Z** — baseline metrics: 3×201 and 3×500 on POST /orders, 3 TypeErrors, chaos gauge 0 (E1–E4, E15).
- **14:59:30Z** — catalog probe finds product 4 "Mystery Box" with `"price":null` (E12).
- **~15:01:08Z** — uptime monotonic (195.5 s), RSS flat, 500 counter unchanged since 14:58:03Z (E16, E17).

## Investigation

- **Baseline** (14:58:40–14:58:58Z): health 200, metrics snapshot, full log window since
  startup. The log tail already carried the three identical TypeError stacks paired 1:1
  with the three 500s; `http_exceptions_total` equals the 500 count exactly (E3 = E2).
- **Triage** — three lenses in parallel, each blind to the others: *software-defect*
  (confirmed the data-dependent crash and the unique null-price product),
  *infra-process* (no anomalies: one startup, monotonic uptime, flat RSS, fast-fail
  500s, no chaos events), *interfaces* (no dependency or gateway shape; found the
  OpenAPI contract gap recorded as a latent finding).
- **Deep-dive** — skipped: H1's triage evidence was already deterministic and complete
  (identical stack on every failure, full accounting of all six order attempts, unique
  null-price record), so it went straight to the judge.
- **Judge** — adversarial, evidence-only: H1 **validated**; H2, H3, H4 **invalidated**.
  The judge flagged the two honest caveats now in Gaps: the product-4 attribution is a
  declared one-step inference, and the catalog probe post-dates the failure window.

## Hypotheses

### H1 — null-price order crash (software-defect) — validated

Every 500 on POST /orders carries the identical unhandled `TypeError` at
`create_order`, shop.py line 82: `product["price"] * order.quantity` with a `NoneType`
left operand (E5–E7), and each error pairs with a 500 access line by request id (E8).
The quantity parsed as `int`, so the request body was well formed; the price was `None`.
The catalog holds exactly one null-price product — id 4, "Mystery Box", in stock (E12,
E13) — and every successful order in the window was for a priced product (E9–E11).
Metrics fully account for all six attempts: 3×201, 3×500, 3 TypeErrors (E1–E3). Nothing
contradicts the hypothesis; the one inferential step (no failed-request product id in
the logs) is declared in Gaps.

### H2 — chaos injection (infra-process) — invalidated

`faultline_chaos_enabled 0` (E4), zero chaos or simulated-exception events anywhere in
the log, and the failures are a real application stack trace (E5), not an injected
status. Caveat recorded in Gaps: the gauge was read after the window.

### H3 — process instability (infra-process) — invalidated

One startup marker in the whole log (E14), uptime arithmetically consistent across
probes (E15, E16), peak RSS flat (E17), and the failed requests completed in 6–12 ms
(E8) — clean fast 500s, not timeouts, stalls, or restarts.

### H4 — change event at time T (infra-process) — invalidated

The only marker is the startup at 14:57:52Z (E14), and a 201 at 14:58:02.355Z sits
between 500s at 14:58:00.294Z and 14:58:03.426Z (E6, E7, E11): there is no T with
"no successes after T". The failures select on input data, not on time.

## Safe next steps

Read-only only; remediation is out of scope for a journal.

- Watch `http_requests_total{method="POST",path="/orders",status="500"}`: each increment
  is another failed customer order attempt while product 4 stays null-priced.
- Re-probe `GET /products/4` to detect when the price changes; the defect disarms the
  moment the price becomes numeric (and would re-arm on any other product whose price
  goes null).
- If any operator-side record exists of how the catalog was seeded or edited, read it to
  date the null price — the lab surface cannot see catalog history.
- Correlate any future `unhandled_exception` TypeError request id against the absence of
  a matching `order_created` event to count affected attempts precisely.

## Gaps

Elaborated from the frontmatter list: the failing requests' product ids are not logged,
so product-4 attribution is a one-step inference from the unique null price (the judge
validated H1 with this caveat declared); the catalog probe post-dates the failure window
by ~90 s, so a transient null price elsewhere is not excluded; POST is outside the
read-only surface, so no controlled reproduction was possible; no telemetry exists from
before the 14:57:52Z startup; and the chaos gauge read post-dates the window, covered
only by the absence of toggle events in the log.
