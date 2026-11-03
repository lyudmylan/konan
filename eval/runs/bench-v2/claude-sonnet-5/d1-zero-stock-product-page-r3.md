---
konan_journal: 2
investigation:
  id: "2026-11-02-products-3-500s"
  trigger: "manual (human report via /konan)"
  complaint: |-
    Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of.
  started: "2026-11-02T17:40:05Z"
  concluded: "2026-11-02T17:49:36Z"
target:
  name: "faultline"
  surface_contract: "docs/lab.md"
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: |-
    The service divides units_ordered by units_in_stock without a zero-guard when computing turnover_score at faultline/src/faultline/shop.py line 64; product 3 (Unobtainium Ingot) has units_in_stock equal to 0, so every GET /products/3 request raises an unhandled ZeroDivisionError and returns HTTP 500.
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: |-
      GET /products/3 returns HTTP 500 on every observed request (6 of 6) because the service divides units_ordered by units_in_stock without a zero-guard at faultline/src/faultline/shop.py line 64, and product 3 (Unobtainium Ingot) has units_in_stock equal to 0; no other product id and no other allow-listed endpoint failed.
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E10]
    evidence_against: []
  - id: H2
    statement: |-
      A process-lifecycle fault (crash-restart loop, resource exhaustion, latency degradation) or an internal chaos/degradation switch is causing the product page failures.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E9]
  - id: H3
    statement: |-
      A boundary or contract fault (gateway failure, malformed payload, schema/contract mismatch, a configuration or deploy change at a boundary) is causing the product page failures.
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E6, E7, E11, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:39:49.745Z, request_id 94d1573586bb"
    quote: |-
      {"ts": "2026-11-02T17:39:49.745Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "94d1573586bb", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): ... File \"faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:39:49.756Z, request_id 94d1573586bb"
    quote: |-
      {"ts": "2026-11-02T17:39:49.756Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "94d1573586bb", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.186}
  - id: E3
    type: log
    source: "lab/logs/app.log — the identical ERROR+500 pattern for GET /products/3 recurs at request_id 5da7c8777723 @17:39:50.812Z/.816Z, eadbfeddcc5c @17:39:53.926Z/.930Z, a12b280992ec @17:39:56.044Z/.048Z, konan-1793641351-97583 @17:42:31.068Z/.077Z, konan-1793641412-97662 @17:43:32.477Z/.481Z — 5 further occurrences beyond E1/E2, every one the same exception_type and the same shop.py:64 traceback frame"
    quote: |-
      {"ts": "2026-11-02T17:39:50.816Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "5da7c8777723", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.641}
  - id: E4
    type: probe
    source: "GET /products, request_id konan-1793641487-97722, 2026-11-02T17:44:47.436Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E5
    type: log
    source: "lab/logs/app.log — the same success pattern recurs for GET /products/2 (request_id b6681f86b956 @17:39:45.633Z; 02c00b3948c8 @17:39:52.872Z), GET /products/4 (konan-1793641368-97611 @17:42:48.682Z), GET /products/5 (konan-1793641368-97614 @17:42:48.697Z) — all HTTP 200"
    quote: |-
      {"ts": "2026-11-02T17:39:44.573Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "fcc53d7e504a", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.013}
  - id: E6
    type: metric
    source: "GET /metrics, request_id konan-1793641482-97717, 2026-11-02T17:44:42.737Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 6
      http_exceptions_total{type="ZeroDivisionError"} 6
  - id: E7
    type: metric
    source: "GET /metrics, two scrapes ~4 minutes apart: request_id konan-1793641261-97547 @2026-11-02T17:41:01.545Z and konan-1793641482-97717 @17:44:42.737Z, both reading 0; zero chaos_enabled/chaos_disabled/chaos_failure events in lab/logs/app.log (43 lines, full file)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E8
    type: log
    source: "lab/logs/app.log, line 3 — the only startup/lifecycle event among all 43 lines of the file; lab/logs/ contains only app.log, no .1-.3 rotation backups"
    quote: |-
      {"ts": "2026-11-02T17:39:42.777Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E9
    type: metric
    source: "GET /metrics, request_id konan-1793641482-97717 @2026-11-02T17:44:42.737Z; compare earlier scrape request_id konan-1793641261-97547 @17:41:01.545Z: process_uptime_seconds 78.78147316607647, process_max_rss_bytes 49397760 — uptime rose ~221s with no reset, RSS identical"
    quote: |-
      process_uptime_seconds 299.98271566606127
      process_max_rss_bytes 49397760
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:39:47.695Z and 17:39:54.988Z, request_ids c5cd421ef862 and 8a5d8ccc090c — both POST /orders succeeded (201)"
    quote: |-
      {"ts": "2026-11-02T17:39:47.695Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "c5cd421ef862", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E11
    type: probe
    source: "GET /products/3 response body, request_id konan-1793641412-97662, 2026-11-02T17:43:32.481Z"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793641412-97662"}
  - id: E12
    type: log
    source: "lab/logs/app.log — every other allow-listed path also returned success throughout the window: GET /health x4 (latest konan-1793641398-97638 @17:43:18.560Z), GET /metrics x3 (latest konan-1793641482-97717 @17:44:42.737Z), GET /openapi.json (konan-1793641413-97667 @17:43:33.394Z), GET /orders/1 (konan-1793641425-97678 @17:43:45.620Z), GET /products x3 (latest konan-1793641487-97722 @17:44:47.436Z)"
    quote: |-
      {"ts": "2026-11-02T17:43:45.605Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1793641425-97675", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.51}
gaps:
  - "process_max_rss_bytes was sampled at only two points ~221 seconds apart (E9), both identical; a continuous memory time series across the full window was not captured, so a slow leak smaller than this sampling resolution is not fully excluded — though the flat reading across repeated failing requests makes one unlikely."
  - "Telemetry only covers the lab process's own lifetime (started 2026-11-02T17:39:42Z, this session's own startup); no log predates it, so whether units_in_stock=0 on product 3 is a long-standing data state or a very recent change could not be dated from the available surface — no config/data-change marker exists in the log either way."
  - "Eval-blind boundary: ground-truth defect recipes and fixtures (eval/, the faultline checkout) were not and could not be consulted; this journal argues from the surface contract (docs/lab.md) only."
usage:
  model: "claude-sonnet-5"
  tokens: 3222963
  wall_clock_seconds: 571
---

# Product page (GET /products/3) returns Internal Server Error on every request — unguarded division by zero stock

## Summary

**Verdict: root-cause-identified.** The product detail endpoint `GET /products/3` fails
with HTTP 500 on every single observed request (6 of 6, 100%). The cause is a code
defect, not infrastructure, chaos, or a boundary problem: `faultline/src/faultline/shop.py`
line 64 computes `turnover_score` by dividing `units_ordered` by `units_in_stock` with no
zero-guard, and product 3 ("Unobtainium Ingot") has `units_in_stock = 0` (E4). Every
request to this one product id raises an unhandled `ZeroDivisionError` (E1, E3) and
returns a generic `{"error":"internal server error", ...}` body (E11). All other
products (1, 2, 4, 5) and every other allow-listed endpoint — `/health`, `/metrics`,
`/openapi.json`, `/products`, `/orders`, `/orders/{id}` — returned success throughout
the observation window (E5, E12), matching the complaint exactly: "a product page"
fails, "other pages load fine." Chaos mode was off the whole time (E7), the process
never restarted and showed no resource/latency degradation (E8, E9), and no boundary or
contract anomaly was found (E4, E6, E11) — ruling out infra-process and interfaces as
the cause. Confidence is high: the failure is deterministic per-input and the stack
trace pinpoints the exact line and the exact data value that triggers it.

## Timeline

- **2026-11-02T17:39:42.777Z** — process startup, version 0.1.0 (E8); the only
  lifecycle event in the whole log — no restart, no crash loop.
- **2026-11-02T17:39:44.573Z – 17:39:45.633Z** — `GET /products/1`, `GET /products/2`
  succeed (E5).
- **2026-11-02T17:39:49.745Z** — first observed `ZeroDivisionError` on `GET /products/3`
  (E1, E2); recurs identically 5 more times through 17:43:32.481Z (E3).
- **Throughout** — `POST /orders` succeeds for products 1 and 2 (E10); chaos stays
  disabled the entire time (E7); uptime climbs monotonically with flat memory, no
  degradation (E9).
- **2026-11-02T17:44:47.436Z** — `GET /products` confirms product 3's
  `units_in_stock: 0`, the mechanical cause of every failure (E4).

No configuration-change, deploy, or chaos-toggle marker appears anywhere in the log —
consistent with the report's "no deploys that we know of."

## Investigation

1. **Baseline**: `GET /health` healthy; `GET /metrics` showed `http_exceptions_total{type="ZeroDivisionError"}`
   already non-zero and `http_requests_total{...path="/products/{product_id}",status="500"}`
   alongside successes on the same path — a data-dependent failure shape, not a global
   outage. `faultline_chaos_enabled 0` ruled out the obvious chaos-injection explanation
   immediately.
2. **Triage (3 lenses, parallel, blind to each other)**:
   - `software-defect` lens: found the `ZeroDivisionError` at `shop.py:64`, confirmed
     `units_in_stock=0` on product 3, confirmed other products succeed.
   - `infra-process` lens: no anomalies — single clean startup, flat RSS, no latency
     degradation, chaos off.
   - `interfaces` lens: no anomalies — failure is 100%-deterministic on one route (not
     gateway-shaped/partial), no config marker, well-formed error envelope, product 3's
     stock is a data value, not a contract break.
3. **Deep-dive skipped**: the software-defect hypothesis's evidence was already
   deterministic and complete (exact line, exact data value, exact reproduction rate),
   per the loop's rule to skip re-proving what triage already nailed down.
4. **Judge** (fresh subagent, evidence-only): validated H1, with two citation-precision
   objections — (a) "every request fails" needed an exact count rather than a partial
   quote, (b) the interfaces exclusion lacked a quoted response body. Both closed
   directly: a full re-read of the log confirmed 6/6 `/products/3` requests were 500
   with zero successes (E3 lists all occurrences), and the actual 500 response body was
   captured and quoted (E11). No new agent round was needed; the gaps were citation
   completeness, not substantive doubt.

## Hypotheses

- **H1 (validated)** — software-defect, unhandled-exception. The division-by-zero at
  `shop.py:64` against product 3's `units_in_stock=0` fully explains the complaint:
  one product page, reproducible on refresh, other pages fine. Evidence for: E1-E6, E10.
  No evidence against.
- **H2 (invalidated)** — infra-process. A process/resource/chaos-switch cause would
  predict a restart marker, memory growth, added latency, or `faultline_chaos_enabled=1`
  at some point. None appeared (E7, E8, E9).
- **H3 (invalidated)** — interfaces. A boundary/contract cause would predict a
  probabilistic or route-wide failure pattern, a malformed response, or a config-change
  marker. The failure is instead 100% deterministic on one input only, the error body is
  well-formed, and no marker exists (E4, E6, E7, E11, E12).

## Safe next steps

- Read-only: watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}` on `/metrics` for
  whether any other product id's stock reaches 0 and starts failing the same way.
- Read-only: if the catalog data source is queryable read-only, check how many other
  product rows currently have `units_in_stock = 0` — that count scopes current
  blast radius without changing anything.
- Out of scope for this journal: adding a zero-guard at `shop.py:64`, or correcting
  product 3's stock value — both are remediation, not investigation.

## Gaps

- Memory (`process_max_rss_bytes`) was sampled only twice, ~221 seconds apart (E9);
  both readings were identical, but a slow leak finer than that sampling interval
  can't be fully ruled out. Low concern given the flat reading across repeated
  failing requests.
- All available telemetry starts at this process's own boot
  (2026-11-02T17:39:42Z); there is no log history before it, so when
  `units_in_stock` on product 3 actually became 0 — moments ago or long-standing —
  cannot be dated from the surface. No config/data-change marker exists either way.
- Ground-truth defect recipes and fixtures (`eval/`, the faultline checkout) were
  out of bounds by the blinding contract and were not consulted; every claim above
  rests on `docs/lab.md`'s surface only.
