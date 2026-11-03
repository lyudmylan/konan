---
konan_journal: 2
investigation:
  id: 2026-11-03-products-3-500s
  trigger: "manual (/konan human-report; fingerprint human-1793703100; startsAt 2026-11-03T10:51:40Z; trigger latency 12s)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-03T10:51:52Z
  concluded: 2026-11-03T10:59:26Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The target's own code raises an unhandled ZeroDivisionError in get_product (shop.py line 64, turnover_score = units_ordered / product[\"units_in_stock\"]) whenever a product has units_in_stock = 0; product 3 is the only such product, so every GET /products/3 returns HTTP 500 while all other existing product ids return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E6, E7, E8, E10]
    evidence_against: []
  - id: H2
    statement: "An internal degradation switch (chaos mode) or a configuration change injected the reported 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E6, E8]
  - id: H3
    statement: "A process crash or restart this morning produced transient customer-facing errors before the current process started at 10:51:18Z."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E9]
    evidence_against: []
  - id: H4
    statement: "The customer reports from this morning were produced by the H1 defect, i.e. customers requested /products/3 while its units_in_stock was 0."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E5, E6, E7]
    evidence_against: [E4]
latent_findings:
  - statement: "GET /products/{product_id} raises an unhandled ZeroDivisionError (shop.py line 64) for any product with units_in_stock = 0; product 3 (Unobtainium Ingot) has stock 0, so every GET /products/3 returns HTTP 500 deterministically. Within the telemetry window only investigator (konan-*) probes triggered it; no non-investigator request has failed."
    evidence: [E5, E6, E7, E8, E10]
  - statement: "Product 4 (Mystery Box) carries price: null in /products and /products/4; the endpoint returns 200, but a client that expects a numeric price would break."
    evidence: [E7, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:51:18.345Z"
    quote: |-
      {"ts": "2026-11-03T10:51:18.345Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: probe
    source: "/health, request_id konan-1793703129-29736"
    quote: |-
      {"status":"ok","uptime_seconds":51.59849662496708}
      -- HTTP 200 in 0.004409s request_id=konan-1793703129-29736
  - id: E3
    type: metric
    source: "/metrics @ 2026-11-03T10:52:10Z, request_id konan-1793703130-29741"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 1
      faultline_chaos_enabled 0
      process_uptime_seconds 52.28097774996422
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:51:19Z-10:51:24Z (non-investigator request ids)"
    quote: |-
      {"ts": "2026-11-03T10:51:20.175Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "2e0018a78917", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.114, "client": "127.0.0.1:49911"}
      {"ts": "2026-11-03T10:51:21.240Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "f9761fb68003", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.067, "client": "127.0.0.1:49912"}
      {"ts": "2026-11-03T10:51:24.435Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "67fc84ab8d06", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.85, "client": "127.0.0.1:49915"}
  - id: E5
    type: probe
    source: "/products/3, request_id konan-1793703202-29841"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793703202-29841"}
      -- HTTP 500 in 0.0089s
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:53:22.514Z"
    quote: |-
      {"ts": "2026-11-03T10:53:22.514Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793703202-29841", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): [...] File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
      {"ts": "2026-11-03T10:53:22.522Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793703202-29841", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.098, "client": "127.0.0.1:49942"}
  - id: E7
    type: probe
    source: "/products, request_id konan-1793703264-29940"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001423s request_id=konan-1793703264-29940
  - id: E8
    type: metric
    source: "/metrics @ ~2026-11-03T10:54:25Z, request_id konan-1793703265-29945"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
      faultline_chaos_enabled 0
      process_uptime_seconds 186.74196612508968
      process_max_rss_bytes 47955968
  - id: E9
    type: log
    source: "ls -la lab/logs/ @ 2026-11-03T10:52Z"
    quote: |-
      -rw-r--r--@ 1 lyudmylan  staff  3809 Nov  3 12:51 app.log
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:53:32Z-10:53:36Z"
    quote: |-
      {"ts": "2026-11-03T10:53:32.887Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793703212-29895", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.481, "client": "127.0.0.1:49945"}
      {"ts": "2026-11-03T10:53:32.903Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793703212-29898", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.381, "client": "127.0.0.1:49946"}
      {"ts": "2026-11-03T10:53:35.979Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793703215-29911", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.359, "client": "127.0.0.1:49949"}
  - id: E11
    type: probe
    source: "/products/4, request_id konan-1793703215-29914"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200
gaps:
  - "No telemetry exists from before 2026-11-03T10:51:18Z: lab/logs/ holds one fresh app.log and no rotated backups (E9), and all metrics counters start at the 10:51:18Z process start (E1). The complaint window ('this morning') is therefore unobservable; H4 (attribution of the customer reports to the H1 defect) and H3 (an earlier crash or restart) cannot be settled from the surface."
  - "Chaos/configuration state before 10:51:18Z is unknowable from the surface; H2 is invalidated only for the logged period."
  - "Process-supervisor or orchestrator records (restart counts, prior exit codes), proxy/load-balancer/CDN access logs, and the customers' exact error pages, URLs and timestamps are outside the surface contract (docs/lab.md) and were not read."
  - "Non-existent product ids (e.g. /products/999) were not probed; H1's 'all other ids return 200' claim covers only the five catalog products."
usage:
  model: claude-fable-5
  tokens: 1334351
  wall_clock_seconds: 454
---

# Product-page 500s: live zero-stock defect found; morning customer impact unverifiable

## Summary

**Verdict: no active incident is evidenced in the observable telemetry — but a live, deterministic, customer-facing defect was found and rides along as a latent finding.** `GET /products/3` fails on every request with HTTP 500: an unhandled `ZeroDivisionError` at `shop.py` line 64 (`turnover_score = units_ordered / product["units_in_stock"]`), because product 3 (Unobtainium Ingot) is the only product with `units_in_stock: 0` (E5–E8, E10). All four recorded 500s were triggered by investigator probes (`konan-*` request ids); every non-investigator request in the window succeeded (E4). The telemetry window only opens at 10:51:18Z, when the current process started (E1, E9), so the morning errors that Support reported left no record. The H1 defect would produce exactly the reported symptom on exactly the reported surface, and it is the most probable cause of the reports — but that attribution (H4) is inconclusive on the evidence, not established. A responder should treat the defect as urgent regardless of the verdict: any customer who opens product 3's page right now will receive a 500.

## Timeline

- **10:51:18.345Z** — current faultline process starts (E1). No telemetry exists before this moment; the log directory holds a single fresh `app.log` with no rotations (E9).
- **10:51:19–24Z** — non-investigator traffic: `GET /products/1`, `/products/2`, `/products/5`, `GET /products`, `POST /orders`, `GET /orders` — all 200/201 (E4). None touches `/products/3`.
- **10:51:40Z** — complaint raised via `/konan` (startsAt).
- **10:51:52Z** — investigation starts (trigger latency 12 s). Baseline: health 200 (E2), all counters 2xx-only, no exceptions, chaos gauge 0 (E3).
- **10:53:22.514Z** — triage probe `GET /products/3` → HTTP 500, `ZeroDivisionError` at `shop.py:64` (E5, E6).
- **10:53:32–36Z** — reproduced three more times, identical stack each time (E10); `GET /products/4` (null price, stock 75) → 200 (E11).
- **~10:54:25Z** — metrics confirm: `status="500"` = 4 and `http_exceptions_total{type="ZeroDivisionError"}` = 4 on the one route, all investigator-stamped; chaos gauge still 0; uptime monotonic; RSS flat (E8).
- **10:59:26Z** — concluded after judge verdicts.

No configuration, deploy, or chaos-toggle markers appear anywhere in the log.

## Investigation

**Baseline** (10:51:52–10:52:10Z): health ok, all request counters 2xx, no exception series, `faultline_chaos_enabled 0` (E2, E3). Startup marker 34 s before investigation start flagged immediately as process-lifecycle evidence (E1).

**Triage** — all three lenses spawned in parallel (infra-process, interfaces, software-defect), none excludable from the baseline. All three converged: infra-process found no lifecycle/resource/chaos anomaly and reproduced a 500 on `/products/3`; interfaces found no dependency, gateway, or config-change signal and confirmed the failure is input-tied and deterministic; software-defect identified the mechanism (zero-stock division, `shop.py:64`) and the single bad input (product 3, stock 0).

**Deep-dive** — skipped. H1's triage evidence was already deterministic and complete (4/4 reproductions with identical stacks, input isolated, neighbors pass); deep-dives exist to fill evidence gaps, and the remaining gaps (pre-window telemetry) cannot be filled from the surface.

**Judge** (fresh subagent, evidence-only): H1 **validated**; H2 **invalidated** for the logged period (gauge 0 at both samples, no chaos events, a genuine arithmetic stack trace, failures confined to one route); H3 **inconclusive** (a single startup line cannot distinguish first boot from post-crash restart; nothing earlier survives); H4 **inconclusive** (no non-investigator request to `/products/3` exists in telemetry; product 3's stock level this morning is unknown; the customers' exact error page is unknown — title-case "Internal Server Error" also fits a proxy or framework default page).

Budget: one triage round, zero deep-dive agents, one judge — concluded in round 1. `usage.tokens` is null because the harness exposes only a coarse remaining-budget counter for the orchestrator and no totals for the lens and judge subagents.

## Hypotheses

### H1 — zero-stock division defect (software-defect) — validated

Every `GET /products/3` fails with an unhandled `ZeroDivisionError` from `get_product` at `shop.py:64`, which divides `units_ordered` by `units_in_stock` (E6). Product 3 is the only zero-stock product (E7). Four of four probes failed identically (E5, E10); metrics agree exactly — four 500s, four `ZeroDivisionError`, on this route only (E8). Products 1, 2, 4, 5 return 200 (E4, E11), which narrows the trigger to the zero denominator — even product 4's null price passes. Nothing timed out (responses 2–9 ms). The judge found no evidence against.

### H2 — chaos or config change (infra-process) — invalidated

Prediction failed everywhere in the logged period: `faultline_chaos_enabled` 0 at both samples (E3, E8), no `chaos_*` or `simulated_exception` events in the log, and the failures are deterministic on one input with a genuine application stack trace (E6) — the opposite of injected, spread-out errors. The invalidation cannot be extended to before 10:51:18Z (see Gaps).

### H3 — earlier crash or restart (infra-process) — inconclusive

The single startup at 10:51:18Z (E1) and the fresh, rotation-less log file (E9) are consistent with both a routine start and a post-crash replacement; uptime rises monotonically only from the current start (E2). No in-surface evidence can distinguish these. Settling evidence: supervisor/orchestrator records for the morning.

### H4 — the morning reports were the H1 defect (software-defect) — inconclusive

For: the defect produces exactly the reported symptom ("internal server error") on exactly the reported surface (a product page), deterministically (E5, E6, E7). Against: H4's own prediction fails — the telemetry contains zero non-investigator requests to `/products/3`, and every recorded 500 is `konan-*`-stamped (E4); the window opens after the reported period, product 3's stock level this morning is unknown, and the customers' exact error text/URL is unrecorded. The link is a plausible inference, not an evidenced claim. Settling evidence: one edge-log entry or customer-supplied URL+timestamp from the morning.

## Safe next steps

Read-only suggestions; remediation is out of scope.

1. Watch for the first non-investigator request to `/products/3`: its status settles user-facing impact immediately.
2. Obtain this morning's proxy/load-balancer/CDN access logs, or one customer's exact URL, timestamp, and error-page body, from Support. A 500 on `/products/3` with `exception_type: ZeroDivisionError` validates H4; a different path or body invalidates it.
3. Obtain process-supervisor/orchestrator records (restart count, previous exit code or signal) for the morning to settle H3.
4. Check the data-change history for product 3: when did `units_in_stock` become 0?
5. Flag `shop.py:64` (`turnover_score` computation) and product 4's `price: null` to the owning team for review.

## Gaps

- **The complaint window is unobservable.** All telemetry starts at the 10:51:18Z process start: one fresh `app.log`, no rotated backups, counters from zero (E1, E9). Whatever customers hit "this morning" left no record reachable through the surface contract. This single gap is why H3 and H4 are inconclusive and why the verdict is not root-cause-identified despite a validated defect mechanism.
- **Pre-window chaos/config state is unknowable**; H2's invalidation covers only the logged period.
- **Out-of-surface sources were not read**: supervisor/orchestrator records, edge access logs, customer-side error details, `lab/server.out` (listed in the lab doc but not part of the investigator's surface in `docs/lab.md`).
- **Non-existent product ids were not probed**; H1's contrast set is the five catalog products.
