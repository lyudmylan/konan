---
konan_journal: 1
investigation:
  id: 2026-08-24-product-3-zero-stock-500s
  trigger: "manual — /konan human-report; complaint object: source=human, fingerprint=human-1787591752, labels.alertname=human-report (no severity stated), startsAt=2026-08-24T17:15:52Z; investigation start 2026-08-24T17:16:05Z (trigger latency 13 s)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-24T17:16:05Z
  concluded: 2026-08-24T17:19:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{product_id} computes turnover_score = units_ordered / product[\"units_in_stock\"]; product 3 (Unobtainium Ingot) has units_in_stock 0, so the handler raises ZeroDivisionError and every request for that product page returns HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/{product_id} divides units_ordered by product[\"units_in_stock\"] in get_product (shop.py line 64); product id 3 has units_in_stock 0, so the request raises ZeroDivisionError and returns HTTP 500 deterministically — for every request to /products/3 and for no other product id."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "Injected or probabilistic degradation (chaos mode or a failing dependency) is producing the product-page 500s."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E9, E10]
  - id: H3
    statement: "A process crash/restart or resource saturation caused the customer-facing errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:17:01.284Z"
    quote: |-
      {"ts": "2026-08-24T17:17:01.284Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787591821-28023", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:17:01.292Z"
    quote: |-
      {"ts": "2026-08-24T17:17:01.292Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787591821-28023", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.557, "client": "127.0.0.1:63148"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:17:07.835Z"
    quote: |-
      {"ts": "2026-08-24T17:17:07.835Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787591827-28076", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.491, "client": "127.0.0.1:63155"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:17:13.320Z"
    quote: |-
      {"ts": "2026-08-24T17:17:13.320Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787591833-28122", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.36, "client": "127.0.0.1:63160"}
  - id: E5
    type: probe
    source: "GET /products, request_id konan-1787591897-28170"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001479s request_id=konan-1787591897-28170
  - id: E6
    type: metric
    source: "/metrics via probe request_id konan-1787591898-28176 @ 2026-08-24T17:18:18Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 11
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 3
      http_exceptions_total{type="ZeroDivisionError"} 3
  - id: E7
    type: metric
    source: "/metrics via probe request_id konan-1787591898-28176 @ 2026-08-24T17:18:18Z (same value at baseline scrape konan-1787591771-27965 @ 17:16:11Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:17:01.936Z"
    quote: |-
      {"ts": "2026-08-24T17:17:01.936Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1787591821-28035", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.431, "client": "127.0.0.1:63150"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:15:35.855Z"
    quote: |-
      {"ts": "2026-08-24T17:15:35.855Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E10
    type: metric
    source: "/metrics via probe request_id konan-1787591771-27965 @ 2026-08-24T17:16:11Z and konan-1787591898-28176 @ 2026-08-24T17:18:18Z"
    quote: |-
      process_uptime_seconds 35.26833970914595
      process_uptime_seconds 162.24285808415152
  - id: E11
    type: metric
    source: "/metrics via probe request_id konan-1787591771-27965 @ 2026-08-24T17:16:11Z and konan-1787591898-28176 @ 2026-08-24T17:18:18Z"
    quote: |-
      process_max_rss_bytes 47202304
      process_max_rss_bytes 48316416
  - id: E12
    type: metric
    source: "/metrics via probe request_id konan-1787591898-28176 @ 2026-08-24T17:18:18Z"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.021077247336506844
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 17
  - id: E13
    type: metric
    source: "/metrics via probe request_id konan-1787591771-27965 @ 2026-08-24T17:16:11Z (baseline, before any investigator request to /products/3)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:15:37.692Z (non-investigator traffic; the only unstamped product-page requests in the log are /products/1, /products/2, /products/5, all 200)"
    quote: |-
      {"ts": "2026-08-24T17:15:37.692Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a10ea0dacb11", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.117, "client": "127.0.0.1:63114"}
gaps:
  - "Log retention starts at the startup marker 2026-08-24T17:15:35.855Z (E9) and lab/logs/app.log has no .1–.3 backups; the customer-facing 500s reported for 'this morning' are outside retained telemetry. The retained non-investigator traffic (17:15:36Z–17:15:42Z, E14) never requested /products/3, and no non-investigator 5xx exists (E13). H1 explains what any customer opening product 3 receives; the customers' own occurrences are not in evidence."
  - "Whether the process restarted before 17:15:35Z is unobservable from this surface; a restart in the unretained window is neither shown nor excluded."
  - "lab/server.out was not read: docs/lab.md lists only lab/logs/app.log, probes and /metrics as the investigator's surface."
  - "This journal was not machine-validated against journal.schema.json in-session: the local python check hit a permission prompt and, per the lab boundary, was not retried."
usage:
  model: claude-fable-5
  tokens: 964591
  wall_clock_seconds: 216
---

# Product page 500s: ZeroDivisionError on /products/3 (units_in_stock = 0)

## Summary

**Root cause identified.** `GET /products/{product_id}` computes `turnover_score = units_ordered / product["units_in_stock"]` in `get_product` (`shop.py` line 64). Product 3, "Unobtainium Ingot", is the only catalogue item with `units_in_stock: 0` (E5), so every request for that product page raises `ZeroDivisionError` and returns HTTP 500 with an `internal server error` envelope (E1–E4). The defect is deterministic and data-dependent: 3 of 3 requests to `/products/3` failed; products 1, 2, 4 and 5 returned 200 and unknown ids returned a handled 404 within the same seconds (E6, E8). No other route emits 5xx, chaos mode is off (E7), and the process is alive, stable and fast (E9–E12). Impact: any customer who opens the product page for product 3 gets an Internal Server Error; every other product page works. Confidence is high for the mechanism. One honest caveat: the retained log starts at 17:15:35Z, so the customer occurrences reported for "this morning" are not themselves in evidence (see Gaps) — the finding is the currently active, reproducible cause of exactly the reported symptom.

## Timeline

All times UTC, 2026-08-24.

- **17:15:35.855Z** — `faultline 0.1.0 started`, the only startup marker and the start of retained telemetry (E9). No configuration, flag or chaos change markers appear anywhere in the log (E7).
- **17:15:36Z–17:15:42Z** — non-investigator traffic: `/products/1`, `/products/2`, `/products/5`, orders — all 200/201 (E14); `/products/3` is never requested.
- **17:15:52Z** — complaint raised (`startsAt`); **17:16:05Z** — investigation starts.
- **17:16:11Z** — baseline: no 5xx series, no exception counter, chaos 0, uptime 35 s (E13, E7, E10).
- **17:17:01.284Z** — first investigator probe of `/products/3`: `ZeroDivisionError` in `get_product`, `shop.py` line 64 (E1), access line `GET /products/3 -> 500` (E2). 0.6 s later `/products/4 -> 200` (E8).
- **17:17:07.835Z** and **17:17:13.320Z** — two independent reproductions, identical exception and frame (E3, E4).
- **17:18:18Z** — post-triage metrics: `status="500"` 3, `ZeroDivisionError` 3, `status="200"` 11, `404` 3 on the product route; chaos 0; uptime monotonic, RSS flat (E6, E7, E10, E11, E12).

## Investigation

- **Baseline** (17:16:10–11Z): `/health` 200, `/metrics` clean, log tail all 2xx since startup. Nothing excluded any lens with evidence, because the complaint window precedes retention.
- **Triage** — three lenses in parallel, each blind to the others: software-defect, infra-process, interfaces. Software-defect found the deterministic `/products/3` failure and the distinguishing input (`units_in_stock: 0`), and reproduced it. Interfaces independently reproduced it, found no chaos/config markers and no gateway-shaped or probabilistic failures, and handed the finding to the software-defect domain. Infra-process found a single start, monotonic uptime, flat RSS and sub-2.5 ms latencies.
- **Deep-dive** — skipped: H1's triage evidence was already deterministic and complete (3/3 reproductions with full stack trace, sibling inputs succeed, input correlation from the list endpoint); H2 and H3 already carried direct counter-evidence.
- **Judge** — a fresh judge with the hypothesis list and verbatim evidence only: H1 **validated** (mechanism supported directly by the stack frame, input correlation and 3/3 reproduction; noted the n = 3 sample and the retention caveat as scope, not contradiction); H2 **invalidated** (chaos gauge 0, no chaos events, no 502/503/504, no 2xx/5xx interleave on the same input, no I/O frame in the stack); H3 **invalidated** (one startup marker, uptime 35 → 162 s monotonic, RSS +1.1 MB, no latency degradation; the next request after the exception succeeds).
- Budget used: one triage round, zero deep-dive agents, one judge.

## Hypotheses

### H1 — ZeroDivisionError in get_product for units_in_stock = 0 (software-defect) — validated

E1 names the throwing operation and expression verbatim: `"turnover_score": units_ordered / product["units_in_stock"]` raising `ZeroDivisionError: division by zero` in `get_product`. E5 shows product 3 is the only item with `units_in_stock: 0`. E2, E3, E4 are three separate requests to `/products/3`, all 500, each paired with the identical exception line. E6 shows the exception counter equals the 500 count on the route and that no other path has a 5xx series. E8 shows a sibling id succeeding 0.6 s after a failure. E7 excludes injected failure. Nothing in the ledger contradicts it.

### H2 — injected or dependency degradation (interfaces) — invalidated

Predicted chaos gauge 1 or chaos/simulated events (E7: 0, none), 5xx interleaved with 2xx on the same input (E2–E4: 3/3 fail, E8: siblings succeed), or gateway statuses (E6: only 500). The stack in E1 is a pure in-process arithmetic error with no I/O frame. The judge's single settling item — one `chaos_*`/`simulated_exception` line, or one `/products/3 -> 200` in the window — does not exist.

### H3 — process crash/restart or saturation (infra-process) — invalidated

Predicted repeated startup markers (E9: one), uptime/counter resets (E10: 35 → 162 s, counters only increase), RSS growth (E11: 47.2 → 48.3 MB), or latency degradation (E12: 17 requests in 21 ms). The exception is caught by middleware and the process keeps serving (E8). What would overturn: a second `startup` line or an uptime value lower than the previous scrape.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- Confirm customer impact scope from support data: which product page the affected customers opened (prediction: product 3 / "Unobtainium Ingot"). Any customer report naming a different product would not be explained by H1 and would reopen the investigation.
- If longer log retention or an external log sink exists, count unstamped `GET /products/3 -> 500` lines for the morning window to size the impact.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and `http_requests_total{path="/products/{product_id}",status="500"}`; investigator probes contributed exactly 3 to each (E6, E13) — any increase beyond that is customer traffic.
- Note for the owners: any product whose stock reaches 0 will hit the same path; the list endpoint (E5) is the cheap read-only check for new zero-stock items.
- Observation, not a finding: product 4 returns `"price": null` (E5) with a 200; no error was tied to it in this window.

## Gaps

- **Retention.** Telemetry begins at the startup marker (E9); there are no rotated backups. The "this morning" customer errors are outside what can be observed. Retained non-investigator traffic never touched `/products/3` (E14) and had no 5xx (E13). The verdict rests on a currently active, deterministic defect that produces exactly the reported symptom, not on the customers' own request lines.
- **Pre-retention lifecycle.** A restart before 17:15:35Z cannot be seen or excluded from this surface.
- **`lab/server.out`** not read — outside the surface listed in `docs/lab.md`.
- **Schema validation** of this file was not run in-session (permission prompt on the python check; not retried per the lab boundary).
