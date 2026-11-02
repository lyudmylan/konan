---
konan_journal: 2
investigation:
  id: 2026-11-02-product-3-zero-stock-500s
  trigger: manual
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T12:17:03Z
  concluded: 2026-11-02T12:23:58Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'GET /products/3 fails because product 3 ("Unobtainium Ingot") has units_in_stock = 0; get_product''s turnover_score calculation divides units_ordered by units_in_stock with no zero guard, raising an unhandled ZeroDivisionError on every request to that one product''s page.'
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: 'GET /products/3 raises an unhandled ZeroDivisionError in get_product''s turnover_score calculation (units_ordered / units_in_stock) because product 3''s units_in_stock is 0, failing every request to that product''s page with HTTP 500 while every other product page succeeds.'
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8, E9, E10, E11]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T12:16:43.353Z, request_id 94cad6b0eb60"
    quote: '"message": "unhandled exception: division by zero", "exception_type": "ZeroDivisionError", "stack": "...File \".../faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n...\nZeroDivisionError: division by zero"'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T12:16:43.362Z, request_id 94cad6b0eb60"
    quote: '"message": "GET /products/3 -> 500", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.724'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T12:16:38.204Z, request_id 7424e0042796"
    quote: '"message": "GET /products/1 -> 200", "path": "/products/1", "status": 200, "duration_ms": 0.897'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T12:16:39.250Z, request_id c12d3bbecfbc"
    quote: '"message": "GET /products/2 -> 200", "path": "/products/2", "status": 200, "duration_ms": 0.779'
  - id: E5
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1793621864-88568"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4 / http_exceptions_total{type="ZeroDivisionError"} 4'
  - id: E6
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1793621864-88568"
    quote: 'faultline_chaos_enabled 0'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T12:16:36.328Z (only startup/restart line in the file)"
    quote: '"message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"'
  - id: E8
    type: probe
    source: "scripts/probe.sh /products/3, request_id konan-1793621983-88759, 2026-11-02T12:19:43Z"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793621983-88759"}'
  - id: E9
    type: probe
    source: "scripts/probe.sh /products, request_id konan-1793622140-88903, 2026-11-02T12:22:20Z"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E10
    type: probe
    source: "scripts/probe.sh /products/4, request_id konan-1793622146-88911, 2026-11-02T12:22:26Z"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0} -- HTTP 200'
  - id: E11
    type: probe
    source: "scripts/probe.sh /products/5, request_id konan-1793622149-88916, 2026-11-02T12:22:29Z"
    quote: '{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0} -- HTTP 200'
gaps:
  - "lab/logs/app.log carries no rotation backups (.1-.3), so process lifecycle history before the 2026-11-02T12:16:36.328Z startup line is unavailable — this investigation cannot independently confirm whether an earlier restart or deploy predates the visible window, only that none occurs within it (E7) and that no config-change or deployment-error markers appear anywhere in the available log."
  - "The surface contract exposes no inventory/database layer directly, only the app's own JSON responses — why product 3's units_in_stock is 0 (seed data, a draining order, a sync fault) could not be determined from telemetry and is reported as unknown."
  - "The surface has no per-customer identifiers, so 'several customers' from the complaint is corroborated only at the HTTP level — every request to the route fails the same way regardless of client (E1, E2, E8) — not per individual reporter."
usage:
  model: claude-sonnet-5
  tokens: 3025278
  wall_clock_seconds: 415
---

# Product 3 page returns 500: unhandled ZeroDivisionError from zero stock

## Summary

**Root cause identified.** The product page for product 3 ("Unobtainium Ingot") fails
on every request with HTTP 500 because `get_product`'s turnover-score calculation
divides `units_ordered` by `units_in_stock` with no guard against zero, and product
3's `units_in_stock` is 0 (E9). This is a pre-existing code defect
(`software-defect` / `unhandled-exception`), not an infrastructure problem or an
injected fault: chaos mode is off (E6), the process shows a single clean startup with
no restart loop (E7), and every other product in the catalog (ids 1, 2, 4, 5 — all with
non-zero stock) returns 200 (E3, E4, E10, E11). The failure is deterministic and
input-specific: it reproduced on every probe to `/products/3` across the investigation
(E1, E2, E8), matching the complaint exactly — one page errors out, refreshing does not
help, other pages load fine. No deploy or config-change marker appears anywhere in the
available log, consistent with "no deploys that we know of." Confidence is high: the
mechanism is pinned to one source line, corroborated by repeated reproduction and a
full-catalog sweep that isolates the defect to the one zero-stock SKU.

## Timeline

- `2026-11-02T12:16:36.328Z` — process startup, the only lifecycle event in the log
  (E7); no restart or crash occurs afterward.
- `2026-11-02T12:16:38.204Z` / `12:16:39.250Z` — `GET /products/1` and `/products/2`
  succeed (E3, E4), establishing the baseline that most product pages work.
- `2026-11-02T12:16:43.353Z` — first observed `unhandled_exception`
  (`ZeroDivisionError`) at `shop.py:64`, immediately followed by `GET /products/3 ->
  500` (E1, E2) — the first captured failure, inside the complaint's "started within
  the last hour" window.
- Three more identical `ZeroDivisionError` failures on `/products/3` follow in the same
  log window, each paired 1:1 with a 500 access line, matching the aggregate counters
  (E5: 4 exceptions, 4 failing requests, 3 successful product-detail requests).
- `2026-11-02T12:19:43Z` — investigator reproduction probe to `/products/3` returns
  the same `ZeroDivisionError` (E8), confirming the defect is still live and
  deterministic, not a transient blip.
- `2026-11-02T12:22:20Z`–`12:22:29Z` — full-catalog sweep: `/products` lists all five
  SKUs, product 3 is the only one with `units_in_stock: 0` (E9); `/products/4` and
  `/products/5` both return 200 (E10, E11), closing out the alternative that other
  product pages might also be failing.

## Investigation

**Baseline** (`/health`, `/metrics`, `lab/logs/app.log` tail): revealed the anomaly
immediately — `http_exceptions_total{type="ZeroDivisionError"} 4` against 4 failing and
3 succeeding `/products/{id}` requests, `faultline_chaos_enabled 0`, and a full stack
trace in the log pointing at one source line.

**Triage** (discipline-parallel, two lenses — `interfaces` was excluded: the lab's
surface contract documents no distributed topology, gateway, or third-party dependency
for that lens to examine):
- `software-defect` lens: independently reproduced the failure on `/products/3`,
  confirmed the exception/500 counters move in lockstep, confirmed products 1 and 2
  consistently return 200 — concluded a data-dependent, single-input code defect.
- `infra-process` lens: found no restart loop, no active chaos switch, no RSS growth or
  latency creep — concluded this domain is clean. It flagged the proximity of the
  single startup event to the first failure as worth weighing against the complaint's
  "within the last hour" framing; resolved in Gaps below (no log rotation history to
  check further back).

Because triage evidence was already deterministic and complete (exact source line,
repeated reproduction, clean counter lockstep, no competing anomaly from either lens),
the deep-dive round was skipped and the hypothesis went straight to the judge.

**Judge**: validated H1's core mechanism from the cited evidence alone, flagging one
residual gap — the claim that "other pages succeed" was only shown for products 1 and
2, not the full catalog. That gap was closed immediately after with a cheap, decisive
check: the full `/products` listing plus probes to the two untested ids (E9, E10, E11),
confirming product 3 is the only zero-stock SKU and the only one that fails.

## Hypotheses

### H1 — validated

GET /products/3 raises an unhandled `ZeroDivisionError` in `get_product`'s
turnover-score calculation because product 3's `units_in_stock` is 0, failing every
request to that product's page while every other product page succeeds.

Evidence for: the stack trace pinpoints the exact line and exception type (E1);
it's tied to a `/products/3 -> 500` access line by matching request id (E2);
products 1, 2, 4, and 5 — all non-zero stock — return 200 every time, including on a
full-catalog sweep (E3, E4, E10, E11); the catalog listing shows product 3 as the only
SKU with `units_in_stock: 0` (E9); exception and 500 counters move together and stay
isolated to this one route/input (E5); chaos is off, ruling out injected fault
(E6); the process shows one clean lifecycle with no restart loop (E7); the failure
reproduced on-demand again after the initial observation (E8). No evidence against was
found.

## Safe next steps

- Read-only: watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}` for continued
  growth, to confirm the defect stays isolated to product 3.
- Read-only: if inventory data is reachable through a non-production read path,
  check whether any other SKU's `units_in_stock` has reached or is trending toward
  zero, since the same code path would fail for any of them.
- Out of scope for this journal: any code change to guard the division, or any change
  to product 3's stock value — remediation is not decided here.

## Gaps

- No log rotation backups exist for `lab/logs/app.log`, so process history before the
  one visible startup line (E7) is unavailable. The investigation can state that no
  restart or config/deploy marker occurs within the observed window, but cannot see
  further back than that window.
- The investigator's surface contract (`docs/lab.md`) exposes no database or inventory
  layer directly — only the app's own JSON responses — so why product 3 ended up at
  zero stock (seed data, a draining order, a sync fault) is unknown and out of reach
  from this surface.
- No per-customer identifiers are visible on this surface, so the complaint's "several
  customers" is corroborated only at the HTTP level (every request to the route fails
  the same way, regardless of client), not per-reporter.
