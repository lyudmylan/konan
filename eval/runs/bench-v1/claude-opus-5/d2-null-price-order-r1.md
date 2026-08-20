---
konan_journal: 1
investigation:
  id: 2026-08-19-order-500s-null-price
  trigger: "manual (/konan human profile) — complaint object: source=human, fingerprint=human-1787122308, labels.alertname=human-report (no severity stated by the reporter), startsAt=2026-08-19T06:51:48Z; investigation start 2026-08-19T06:51:48Z (adapter stamped both in one call, so trigger latency is under one second)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T06:51:48Z
  concluded: 2026-08-19T07:01:32Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "create_order multiplies the catalog price by the requested quantity without guarding a null price, so an order for a product whose price is null raises an unhandled TypeError at src/faultline/shop.py:82 and the request returns 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "POST /orders fails for a data-dependent input class: when the ordered product's catalog price is null, create_order evaluates product['price'] * order.quantity — None times an int — and raises an unhandled TypeError at src/faultline/shop.py:82, returning 500. Row id 4 ('Mystery Box') is the only null-price row visible on the catalog surface, which indicates but does not directly log it as the failing input."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "The order failures are injected or probabilistic degradation (chaos mode or a random fault injector) rather than a per-input defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E4, E6, E9, E11]
  - id: H3
    statement: "The order failures come from a process-lifecycle or resource-saturation problem — crash/restart, memory exhaustion, thread starvation, or timeouts."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11, E12]
  - id: H4
    statement: "The order failures come from a failing upstream/third-party dependency, or from interface contract drift between the catalog and the order path."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E14]
    evidence_against: [E1, E2, E5, E6]
latent_findings:
  - statement: "GET /products/{id} raises an unhandled ZeroDivisionError while computing turnover_score for product 3, whose units_in_stock is 0. Only investigator-stamped (konan-) traffic reached that path in the observed window, so this is latent, not the reported incident. The divisor is not visible on the telemetry surface, so 'any zero-stock product' is an untested generalisation from a single case."
    evidence: [E13, E5, E11]
  - statement: "The published contract does not describe the failure surface: /openapi.json documents only 201 and 422 for POST /orders (no 500), and types the /products body as free-form objects with no price field or nullability. A request the documented contract fully permits therefore produces an undocumented 500."
    evidence: [E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:51:34.689Z"
    quote: '{"ts": "2026-08-19T06:51:34.689Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: ''NoneType'' and ''int''", "request_id": "41724da84ff7", "event": "unhandled_exception", "exception_type": "TypeError"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:51:34.689Z — final stack frames of E1, identical in all three exception lines"
    quote: |-
      File "/Users/lyudmylan/Projects/faultline/src/faultline/shop.py", line 82, in create_order
          total_price = round(product["price"] * order.quantity, 2)
                              ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~
      TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:51:34.700Z"
    quote: '{"ts": "2026-08-19T06:51:34.700Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "41724da84ff7", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.784, "client": "127.0.0.1:57617"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:51:35.760Z and 2026-08-19T06:51:38.877Z — the other two exception lines, with their access lines at 06:51:35.764Z and 06:51:38.882Z"
    quote: '{"ts": "2026-08-19T06:51:35.760Z", "message": "unhandled exception: unsupported operand type(s) for *: ''NoneType'' and ''int''", "request_id": "250b297f979d", "event": "unhandled_exception", "exception_type": "TypeError"} / {"ts": "2026-08-19T06:51:38.877Z", "message": "unhandled exception: unsupported operand type(s) for *: ''NoneType'' and ''int''", "request_id": "09e22ffe1146", "event": "unhandled_exception", "exception_type": "TypeError"} / {"ts": "2026-08-19T06:51:35.764Z", "message": "POST /orders -> 500", "request_id": "250b297f979d", "status": 500} / {"ts": "2026-08-19T06:51:38.882Z", "message": "POST /orders -> 500", "request_id": "09e22ffe1146", "status": 500}'
  - id: E5
    type: probe
    source: "/products (request_id konan-1787122342-48793) — HTTP 200"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:51:31.570Z, 06:51:32.629Z, 06:51:37.818Z — the three order_created events, access lines 201 at 06:51:31.571Z, 06:51:32.630Z, 06:51:37.819Z"
    quote: '{"ts": "2026-08-19T06:51:31.570Z", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0} / {"ts": "2026-08-19T06:51:32.629Z", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0} / {"ts": "2026-08-19T06:51:37.818Z", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}'
  - id: E7
    type: probe
    source: "/products/4 — HTTP 200, compared with /products/1 and /products/2"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0} — /products/1 reports units_ordered 3, /products/2 reports units_ordered 1'
  - id: E8
    type: probe
    source: "/products/0 and /products/6 — HTTP 404"
    quote: '{"detail":"no such product: 0"} / {"detail":"no such product: 6"}'
  - id: E9
    type: metric
    source: "/metrics (request_id konan-1787122324-48778), scraped 2026-08-19T06:52:04Z"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 36.346992291975766
      process_max_rss_bytes 48201728
  - id: E10
    type: metric
    source: "/metrics, re-scraped roughly 189 seconds after E9"
    quote: |-
      process_uptime_seconds 224.97617308306508
      process_max_rss_bytes 48234496
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:51:27.687Z — the only startup marker in the file; the file carries no chaos_enabled, chaos_disabled, chaos_failure or simulated_exception event, and lab/logs/ holds no rotated .1-.3 backups"
    quote: '{"ts": "2026-08-19T06:51:27.687Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E12
    type: log
    source: "lab/logs/app.log — duration_ms of the six POST /orders requests, and the slowest request on any path in the file"
    quote: 'POST /orders 500s: duration_ms 11.784, 5.475, 5.113. POST /orders 201s: duration_ms 2.593, 1.313, 1.265. Slowest request on any path: duration_ms 12.137 (first GET /health).'
  - id: E13
    type: probe
    source: "/products/3 (request_id konan-1787122650-49096) — HTTP 500; logged in lab/logs/app.log @ 2026-08-19T06:57:30.860Z"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787122650-49096"} — log line: "message": "unhandled exception: division by zero", "exception_type": "ZeroDivisionError", final frame "line 64, in get_product"'
  - id: E14
    type: probe
    source: "/openapi.json — HTTP 200"
    quote: 'POST /orders documents responses 201 and 422 only, with no 500; the /products 200 body is typed as {"items":{"additionalProperties":true,"type":"object"},"type":"array"} — no price field and no nullability.'
gaps:
  - "The failing requests' inputs are not on the telemetry surface. No log line records product_id or quantity for a failed POST /orders — order_created fires only on success — so the link from the three 500s to catalog row 4 is a deduction (row 4 is the only null-price row on the surface, and its units_ordered is 0), not a logged fact. One 'order requested' line before the price math would close this permanently."
  - "Determinism on retry could not be observed. The three 500s carry distinct request_ids, which is what independent attempts and retries look like alike; nothing in the telemetry marks a retry. 'Fails on every attempt' follows from the code path in the stack trace, not from an observed repeat."
  - "No reproduction was possible: confirming the input class would need a POST /orders for product 4, which is outside the read-only boundary (eval-harness surface only)."
  - "Successful orders are observed for products 1 and 2 only. Products 3 and 5 were never ordered in the window, so 'orders for priced products succeed' is unverified for them."
  - "No history before 2026-08-19T06:51:27.687Z. lab/logs/ holds only app.log with no rotated backups, so the record covers one process lifetime. Whether product 4 ever had a price, and when the null appeared, is unknowable from this surface — 'Mystery Box has no price by design' and 'a feed dropped the price' both fit the evidence, and they imply different fixes."
  - "Blast radius is unquantified. 3 of 6 order attempts failed in this window, but the surface does not show how much real user traffic targets product 4."
  - "Investigator artefact: the konan probe at E13 wrote a 500 and a ZeroDivisionError into the target's own telemetry at 06:57:30.860Z. E9 and E10 were both scraped before that, so the counters quoted here are clean — but any later scrape of http_exceptions_total will include a ZeroDivisionError that no user caused."
usage:
  model: claude-opus-5
  tokens: 2150278
  wall_clock_seconds: 584
---

# Orders fail with 500 for a catalog row that has no price

## Summary

**Root cause identified.** `create_order` computes `total_price = round(product["price"] * order.quantity, 2)` with no guard for a null price (E2). When the ordered product's catalog price is `null`, the multiplication is `None * int`, which raises an unhandled `TypeError`, and the request returns 500 (E1, E3). This is a data-dependent software defect: the route is not broken, one input class is. That matches the complaint exactly — the customers who fail keep failing, because the catalog row does not change between their attempts, while everyone ordering a priced product is unaffected.

The catalog holds exactly one null-price row: id 4, "Mystery Box" (E5). It is the only visible input that can make `product["price"]` a `NoneType`, and it has never been ordered successfully (`units_ordered: 0`, E7). **Read this attribution as strongly indicated, not as observed:** no log line records the product_id of a failed order, so the link from the three 500s to row 4 is deduction from the catalog, not a logged fact.

Impact in the observed window: 3 of 6 order attempts failed (E9). The defect fails closed — no order row exists for any 500, and product 4's stock is undecremented (E7), so there is no partial or corrupt order state. Confidence in the mechanism is high; confidence in the specific row is high but inferential.

Health stayed green throughout (`/health` 200, uptime unbroken), which is the healthy-monitoring trap in its usual form: the business surface was failing while the health surface said ok.

## Timeline

- **06:51:27.687Z** — Process starts, `faultline 0.1.0 started`; the only startup marker in the record, and the only lifecycle event of any kind (E11). No configuration, deploy, or flag-change marker appears anywhere in the window.
- **06:51:31.571Z / 06:51:32.630Z** — Two orders succeed, `POST /orders -> 201`, products 1 and 2 (E6).
- **06:51:34.689Z** — First `TypeError` at `shop.py:82` (E1); request 500s at **06:51:34.700Z** (E3).
- **06:51:35.760Z** — Second identical `TypeError`; 500 at 06:51:35.764Z (E4).
- **06:51:37.818Z** — An order **succeeds** between the failures — product 1, `order_id 3` (E6). This is the timeline's key shape: success interleaves with failure, so the selector is the input, not the clock.
- **06:51:38.877Z** — Third identical `TypeError`; 500 at 06:51:38.882Z (E4).
- **06:52:04Z** — Investigation baseline scraped: 3× 201, 3× 500, `http_exceptions_total{type="TypeError"} 3`, `faultline_chaos_enabled 0` (E9).
- **06:55:13Z** — Re-scrape ~189s later: counters unchanged, uptime advanced by the elapsed time, RSS flat at +32 KB (E10). No further user failures; no restart.
- **06:57:30.860Z** — *Investigator-caused:* a konan probe of `/products/3` returns 500 with `ZeroDivisionError` (E13). Latent finding, not user impact.

## Investigation

**Baseline** — `/health` 200 with 36s uptime, `/metrics`, and the 24-line log tail. The metrics snapshot already split the picture: `POST /orders` carried both 201×3 and 500×3, with `http_exceptions_total{type="TypeError"} 3` matching the 500 count exactly and `faultline_chaos_enabled 0`. Following the healthy-monitoring rule, the business surface was probed too — `/products` returned the null-price row.

**Triage (one round, three lenses, parallel, each blind to the others)** — all three domain lenses were spawned; none could be excluded by the baseline, since the complaint named only a symptom.

- *software-defect* — found the `TypeError` at `shop.py:82`, the null-price row as the only possible `NoneType` source, and that the defect fails closed (no order row, no stock decrement).
- *infra-process* — no anomaly, and three clean rule-outs: one startup marker with unbroken uptime (no restart), RSS flat (+0.07% over 189s), and every request under 12.137 ms (no timeout or starvation). A 5–12 ms failure is a synchronous throw.
- *interfaces* — no dependency evidence exists on the surface at all; no gateway-shaped status anywhere. It found the contract gap (E14) and explicitly handed the failure back as per-input, not probabilistic.

**Deep-dive (one hypothesis, one agent)** — H1 only; H2–H4 already had deterministic disconfirming evidence from triage and went straight to the judge. The agent was tasked to break H1: look for a 500 with a different exception or frame, an `order_created` naming product 4, a second null-price row, list-vs-detail disagreement, or unlisted catalog rows. All disconfirmation attempts failed — but it surfaced a second, unrelated defect on `GET /products/{id}` (E13) and confirmed the successes' `total_price` values reconcile with the catalog's current prices, so the catalog did not change mid-window.

**Judge** — validated H1 on mechanism and killed H2, H3, H4. It rejected two sentences of the draft as deduction stated as observation: the product-4 attribution and "fails on every retry". Both have been rewritten and moved into Gaps. It also downgraded L1's generalisation ("any zero-stock product") to n=1, and flagged that the investigator's own probe wrote an exception into the target's telemetry. Those corrections are carried above.

## Hypotheses

### H1 — null catalog price raises an unhandled TypeError in create_order — **validated**

**For:** Three 500s, three identical `TypeError`s, one identical final frame at `shop.py:82` (E1, E2, E4), each tied to its `POST /orders -> 500` access line by request_id (E3, E4). The counters close with no remainder: 3× 500, 3× TypeError, no other exception type and no non-200 on any other user path (E9). The subscript `product["price"]` itself succeeded, so `product` is a real catalog row and the row's price is `None` — not a missing-id lookup returning `None`. The catalog holds exactly one null-price row (E5), confirmed at the detail route (E7) and bounded either side by 404s (E8). Success interleaves with failure in the same four seconds (E6), which is the signature of an input class rather than a time window.

**Against:** Nothing contradicted it. The weakness is not contrary evidence but a missing link — see Gaps: the failing requests' `product_id` is simply not logged.

### H2 — injected or probabilistic degradation — **invalidated**

`faultline_chaos_enabled 0` alone would be weak, being point-in-time. E11 closes that escape: one startup marker, no rotated backups, and no `chaos_*` or `simulated_exception` event, so the file covers the whole process life. The decisive evidence is E1/E2/E4 — a genuine `NoneType * int` at a real application line. A fault injector does not produce a real type error at a real multiplication. The 3-of-6 split is not a rate; it aligns with an input class, and a success sits between two failures (E6).

### H3 — process lifecycle or resource saturation — **invalidated for the window**

Uptime ran 36.3s → 225.0s across a ~189s gap, matching elapsed time, so one process stayed alive; RSS moved 32 KB, which is flat (E9, E10). One startup marker, no rotated logs, no restart (E11). Every request completed under 12.137 ms (E12), which excludes timeouts and thread starvation — the failures returned in 5–12 ms with a type error, not a hang. E12 also refutes any slowness reading of the complaint. Scope honestly stated: the log begins at the 06:51:27 startup, so this rules out a restart *during the failures*, not ever.

### H4 — upstream dependency or interface contract drift — **invalidated as a cause**

E14 shows a documentation gap, not a drift: a contract silent about `price` cannot drift against it, and an undocumented 500 is a symptom of the defect, not its origin. No upstream evidence exists anywhere on the surface — no client frames, no dependency error, no failed outbound call, no gateway-shaped status. The catalog answers 200 with intact data (E5) while orders fail (E1, E2, E6): the null value arrived successfully, and the defect is the unguarded multiplication. E14 is re-filed as a latent contract finding rather than a cause. One part stays genuinely open — the telemetry never dates the null price, so "no price by design" and "a feed dropped it" both fit (see Gaps).

## Safe next steps

Read-only suggestions; remediation is out of scope.

1. **Close the attribution gap in telemetry** — the single highest-value observation change is logging the requested `product_id` and `quantity` on order entry, before the price math. Today a failed order records no input at all, which is why the strongest claim in this journal is a deduction.
2. **Check the catalog source for row 4** — inspect the seed, fixture, or feed that sets `Mystery Box` to `price: null`, to establish whether the null is by design or arrived from a data change. This decides whether the correct fix is a code guard, a data correction, or both.
3. **Quantify exposure** — read how much real traffic targets product 4 to size the impact beyond the 3-of-6 seen here.
4. **Treat the latent `/products/{id}` defect as a separate item** — confirm the divisor at `get_product` line 64 to establish whether every zero-stock product is affected, or only row 3. It has not reached users on this record, but a zero-stock product is a normal catalog state.
5. **Re-file the contract gap (E14)** — POST /orders declares no 500, and `/products` does not type `price` or its nullability.
6. **Note the investigator artefact** when reading later metrics: `http_exceptions_total` now includes one `ZeroDivisionError` that konan's own probe caused at 06:57:30.860Z.

## Gaps

The frontmatter list, in short: the failing requests' inputs are not logged, so the product-4 link is deduction; retry determinism was never observed, only inferred from the code path in the stack trace; no reproduction was possible under the read-only boundary; success is confirmed for products 1 and 2 only, not 3 or 5; there is no history before 06:51:27.687Z, so the null price cannot be dated; blast radius is unquantified; and one exception in the target's telemetry was caused by this investigation's own probe, not by a user.

An empty gap list would have been a claim that nothing was out of reach. This one is not empty — the decisive evidence, the failed orders' input, is on the other side of a logging gap, and the confirming test, placing an order for product 4, is on the other side of the read-only boundary.
