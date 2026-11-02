---
konan_journal: 2
investigation:
  id: 2026-11-02-order-500s-null-price
  trigger: "manual (/konan adapter; complaint fingerprint human-1793630076, startsAt 2026-11-02T14:34:36Z, investigation start 2026-11-02T14:34:48Z, trigger latency 12s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-02T14:34:48Z
  concluded: 2026-11-02T14:42:49Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Orders for product 4 (Mystery Box), whose catalog price is null, raise an unhandled TypeError in create_order (shop.py line 82: product[\"price\"] * order.quantity with a None price) and fail with HTTP 500 on every attempt, while orders for products with non-null prices succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "POST /orders for product 4 (Mystery Box, catalog price null) raises an unhandled TypeError at shop.py line 82 — product[\"price\"] * order.quantity with a None left operand — and returns HTTP 500 deterministically for that input, on every retry; orders for in-stock products with non-null prices succeed with 201."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12]
    evidence_against: []
  - id: H2
    statement: "An internal degradation switch (chaos mode) injects the 500s on POST /orders."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E12, E13, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:20.514Z"
    quote: |-
      {"ts": "2026-11-02T14:34:20.514Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "675853fd1199", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last): … File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:20.527Z"
    quote: |-
      {"ts": "2026-11-02T14:34:20.527Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "675853fd1199", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 13.607, "client": "127.0.0.1:58676"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:21.587Z (paired access line 14:34:21.592Z: POST /orders -> 500, client 127.0.0.1:58678)"
    quote: |-
      {"ts": "2026-11-02T14:34:21.587Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "cfb25cfbbd6c", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last): … File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:24.719Z (paired access line 14:34:24.724Z: POST /orders -> 500, client 127.0.0.1:58680)"
    quote: |-
      {"ts": "2026-11-02T14:34:24.719Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "6acaabbc1c0c", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last): … File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E5
    type: metric
    source: "/metrics @ 2026-11-02T14:34:58Z (probe request_id konan-1793630098-93077)"
    quote: http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E6
    type: metric
    source: "/metrics @ 2026-11-02T14:34:58Z (probe request_id konan-1793630098-93077); the same scrape reports status=\"200\" only for every GET route"
    quote: http_requests_total{method="POST",path="/orders",status="201"} 3
  - id: E7
    type: metric
    source: "/metrics @ 2026-11-02T14:34:58Z (probe request_id konan-1793630098-93077)"
    quote: http_exceptions_total{type="TypeError"} 3
  - id: E8
    type: probe
    source: "GET /products (request_id konan-1793630118-93104)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001534s request_id=konan-1793630118-93104
  - id: E9
    type: probe
    source: "GET /products/4 (request_id konan-1793630242-93167)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:17.402Z (paired access line: POST /orders -> 201)"
    quote: |-
      {"ts": "2026-11-02T14:34:17.402Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "7d3cf4402879", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:18.459Z (paired access line: POST /orders -> 201)"
    quote: |-
      {"ts": "2026-11-02T14:34:18.459Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "fb45b91f654d", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:23.655Z (paired access line: POST /orders -> 201); this success sits between the failures of E3 and E4"
    quote: |-
      {"ts": "2026-11-02T14:34:23.655Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "312cc6c82547", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-02T14:34:58Z (probe request_id konan-1793630098-93077)"
    quote: faultline_chaos_enabled 0
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:34:13.604Z — first line of the only log file (no rotated backups); the file contains no chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events"
    quote: |-
      {"ts": "2026-11-02T14:34:13.604Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
gaps:
  - "POST /orders is outside the GET-only probe allowlist, so the failure was not reproduced by the investigator; determinism rests on three identical logged stacks from user traffic."
  - "Access lines do not record the request body, so no log line names the failing orders' product_id; the product-4 attribution is an inference from the throwing expression (None left operand of product[\"price\"] * order.quantity) plus the catalog's single null-price product. The handler's treatment of unknown product ids was not readable (code is outside the surface), so a lookup that returns a None-price record for an unknown id is a residual, unevidenced alternative."
  - "Triage lenses infra-process and interfaces were not spawned; their domains were excluded from baseline evidence (single startup marker E14, chaos gauge 0 E13, all GET routes 200 E6, no gateway tier in the lab topology per docs/lab.md). This is an accepted blind spot."
  - "The chaos gauge was scraped 34 seconds after the last failure; a toggle-off inside the window is excluded only by the absence of chaos transition events in the log, which assumes faultline logs such transitions."
usage:
  model: claude-fable-5
  tokens: 1741232
  wall_clock_seconds: 481
---

# Orders for the null-priced product 4 fail with 500 — unhandled TypeError in create_order

## Summary

Root cause identified. Product 4 ("Mystery Box") carries `price: null` in the catalog (E8, E9). When a customer orders it, `create_order` (faultline `shop.py` line 82) computes `product["price"] * order.quantity` with a `None` price, raises an unhandled `TypeError`, and the request fails with HTTP 500 (E1–E4). The failure is per-input and deterministic, so retries fail identically — exactly the complaint's shape: the same customers fail on every retry while orders for normally priced products succeed (E10–E12, including a 201 interleaved between two 500s). Impact in the observed window: 3 of 6 order attempts failed (E5, E6), all from non-investigator traffic. Chaos mode is off and no injection events exist in the log (E13, E14). Confidence is high; the one residual gap is that the failing orders' product id is inferred (bodies are not logged), not directly observed.

## Timeline

All times UTC, 2026-11-02.

- 14:34:13.604 — faultline 0.1.0 starts; first line of the only log file; no config/flag/chaos change markers anywhere in the log (E14).
- 14:34:17.402 — order 1, product 1 → 201 (E10).
- 14:34:18.459 — order 2, product 2 → 201 (E11).
- 14:34:20.514 — first unhandled TypeError at shop.py:82 → POST /orders 500 (E1, E2).
- 14:34:21.587 — second identical TypeError → 500 (E3).
- 14:34:23.655 — order 3, product 1 → 201, between the second and third failures (E12).
- 14:34:24.719 — third identical TypeError → 500 (E4).
- 14:34:36 — complaint raised (trigger `startsAt`).
- 14:34:48 — investigation starts (trigger latency 12 s).
- 14:34:58 — baseline: health 200, metrics scrape (E5–E7, E13).
- 14:35:18 — catalog probe: product 4 is the only null-price product (E8).
- 14:37:22 — lens probe GET /products/4 confirms `price: null` (E9).

## Investigation

Complaint object (verbatim, synthesized by the /konan adapter):

```json
{
  "source": "human",
  "fingerprint": "human-1793630076",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine." },
  "startsAt": "2026-11-02T14:34:36Z"
}
```

Investigation start: 2026-11-02T14:34:48Z (trigger latency 12 s). No severity was stated by the reporter, so none was recorded.

- **Baseline** (14:34:48–14:35:18): health ok with uptime 45 s; metrics show POST /orders split 3×201 / 3×500 with `http_exceptions_total{type="TypeError"} 3`, every GET route 200, chaos gauge 0, RSS ~47 MB; the log tail covers the whole single file back to startup and holds three identical TypeError stacks; the catalog probe shows one null-price product.
- **Triage** (one round): one lens spawned, software-defect — the baseline already excluded the other two domains with evidence (infra-process: single startup marker, chaos off, flat resources; interfaces: no gateway tier in the lab, in-app stacks on the 500s, no change markers). The lens returned three findings: the deterministic TypeError at shop.py:82; the data-dependent shape pointing at the null-price product 4 (adding probe E9); and the negative check against injected degradation.
- **Deep-dive**: skipped — the triage evidence was deterministic and complete; per the loop contract such a hypothesis goes straight to the judge.
- **Judge** (adversarial, evidence-only): H1 validated, H2 invalidated. The judge verified every quote against the source log, confirmed the counts (3 × 500 = 3 × TypeError), noted that no write traffic other than the six POSTs exists in the log (so no request could have changed a price between failure and probe), and required two honest reservations, both recorded under Gaps: the product-4 link is inference, and the prediction clause was narrowed to in-stock, non-null-price products.

## Hypotheses

### H1 — null-price product breaks create_order (validated)

Orders for product 4 fail because `create_order` multiplies the product's price by the quantity without a null guard; product 4's price is null. For: the three identical stacks naming the operation and line (E1, E3, E4) with their 500 access lines (E2); the exact count match between exceptions and 500s (E5, E7); the catalog's single null-price product (E8, E9); and successes on the same route, same window, for non-null-price products (E10, E11), including one between two failures (E12) — the outcome follows the input, not the clock. Against: nothing. The TypeError's `'NoneType' * 'int'` form proves the dict lookup succeeded and returned `None` for the left operand — a missing product would fail at subscription, not multiplication.

### H2 — chaos/degradation switch (invalidated)

Injected degradation predicts a probabilistic spread across routes and chaos markers in telemetry. Against: the chaos gauge reads 0 (E13); the full single-process log holds zero chaos or simulation events since startup (E14); the failures concentrate on one route and one exception type with every GET at 200 (E5, E6) and a success interleaved (E12). What would reopen it: a chaos-enabled event or gauge=1 reading timestamped inside 14:34:20–14:34:25. No such evidence exists.

## Safe next steps

Read-only; remediation is out of scope.

- Read `create_order` in faultline `src/faultline/shop.py` around line 82 (in the faultline repo, outside this surface) to confirm the missing null-price guard and how unknown product ids are handled — this closes the one inferential gap.
- Read the catalog seed/data source to learn how product 4 acquired `price: null`.
- Watch `http_exceptions_total{type="TypeError"}` and `http_requests_total{method="POST",path="/orders",status="500"}` for growth — each new failed attempt increments both in lockstep while the defect stands.
- If order traffic volume matters for impact sizing, count only non-`konan-` request ids: all three observed failures are user traffic from one client host on sequential ports, consistent with one or few customers retrying.

## Gaps

1. **No direct reproduction.** The probe allowlist is GET-only; POST /orders cannot be probed. Determinism rests on three identical logged stacks from user traffic — strong, but observed rather than exercised.
2. **Product id of the failing orders is inferred.** Request bodies are not logged. The inference chain — None left operand at the price multiplication, one null-price product in the catalog, no write traffic that could have changed a price — is airtight within the surface, but a product lookup that returns a None-price record for an unknown id would produce the identical stack; the handler code is outside the investigator's surface.
3. **Two triage lenses skipped on baseline evidence.** infra-process and interfaces were excluded by cited baseline facts rather than swept by their lenses; if a second, quieter anomaly hides in those domains, this investigation would not have seen it.
4. **Chaos gauge timing.** The gauge was read 34 s after the last failure. The log shows no chaos transitions at all, which excludes a mid-window toggle only if transitions are always logged (the surface contract lists `chaos_enabled`/`chaos_disabled` among logged events, supporting the assumption).
