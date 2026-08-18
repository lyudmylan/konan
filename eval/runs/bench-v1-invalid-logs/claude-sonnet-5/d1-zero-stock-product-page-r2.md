---
konan_journal: 1
investigation:
  id: 2026-08-18-products-3-500s
  trigger: manual (/konan human report, fingerprint human-1787079357)
  complaint: |-
    Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of.
  started: "2026-08-18T18:55:57Z"
  concluded: "2026-08-18T19:01:20Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/3 raises an unhandled ZeroDivisionError in get_product's turnover_score computation (units_ordered / product[\"units_in_stock\"]) because product 3 (Unobtainium Ingot) is served with units_in_stock 0 — a zero denominator — so every request for that specific product, whether from investigator probes or ordinary traffic, returns HTTP 500, while every other product id succeeds."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/3 fails deterministically with an unhandled ZeroDivisionError raised in get_product at the turnover_score computation (units_ordered / product[\"units_in_stock\"]) because product id 3 (Unobtainium Ingot) is served with units_in_stock 0. Non-investigator requests to /products/3 at 18:55:46-52Z all returned 500 with this exact exception, while sibling product ids (1,2,4,5) returned 200 throughout the same window, and the failure reproduces on demand."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The process is caught in a restart loop and the restarts (or whatever is causing them) are producing the customer-visible 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E5, E6, E10]
  - id: H3
    statement: "An operator chaos/fault-injection toggle is producing the 500 responses on /products/3."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E9]
latent_findings:
  - statement: "Catalog data anomaly: product id 4 (Mystery Box) is served with price:null in the /products payload. HTTP 200 throughout, no failure observed from it on the read surface — a latent oddity, not the incident."
    evidence: [E2]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1787079377-18557 (2026-08-18T18:56:17Z)"
    quote: |-
      {"status":"ok","uptime_seconds":38.4375707921572}
      -- HTTP 200 in 0.002302s request_id=konan-1787079377-18557
  - id: E2
    type: probe
    source: "/products @ request_id konan-1787079411-18601 (2026-08-18T18:56:51Z), full catalog body"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:10.692Z and .703Z — first observed exception in this process lifetime, paired access line, same request_id"
    quote: |-
      {"ts": "2026-08-18T18:48:10.692Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "19b4aea67888", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
        File "/Users/lyudmylan/Projects/faultline/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
      {"ts": "2026-08-18T18:48:10.703Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "19b4aea67888", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.41, "client": "127.0.0.1:49958"}
  - id: E4
    type: metric
    source: "/metrics @ request_id konan-1787079379-18563 (2026-08-18T18:56:19Z)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
      faultline_chaos_enabled 0
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:53:29.573-.622Z and 18:55:41.165-42.221Z — successful requests to the other product ids bracketing the 18:55 failure burst"
    quote: |-
      {"ts": "2026-08-18T18:53:29.573Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1787079209-18367", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.58, "client": "127.0.0.1:50023"}
      {"ts": "2026-08-18T18:53:29.622Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "konan-1787079209-18373", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.449, "client": "127.0.0.1:50024"}
      {"ts": "2026-08-18T18:55:41.165Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "51d47e7d88e8", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.993, "client": "127.0.0.1:50045"}
      {"ts": "2026-08-18T18:55:42.221Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "2a56c1a685ad", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.968, "client": "127.0.0.1:50046"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:55:46.351-52.662Z — four non-investigator requests (unstamped request_ids, i.e. simulated/real end-user traffic, not konan-* probes), all to /products/3, all 500"
    quote: |-
      {"ts": "2026-08-18T18:55:46.351Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "3ff5de81ba85", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.409, "client": "127.0.0.1:50048"}
      {"ts": "2026-08-18T18:55:47.414Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "1a96aaefe3fb", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.994, "client": "127.0.0.1:50049"}
      {"ts": "2026-08-18T18:55:50.536Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "c7ffa73df0eb", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.297, "client": "127.0.0.1:50051"}
      {"ts": "2026-08-18T18:55:52.662Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "d2520894b5b4", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.923, "client": "127.0.0.1:50053"}
  - id: E7
    type: probe
    source: "GET /products/3 @ request_id konan-1787079546-18777 (2026-08-18T18:59:06Z) — investigator reproduction"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787079546-18777"}
      -- HTTP 500 in 0.004596s request_id=konan-1787079546-18777
  - id: E8
    type: probe
    source: "GET /products/1 @ request_id konan-1787079548-18783 (2026-08-18T18:59:08Z) — investigator control probe, confirms the turnover_score formula and that non-zero-stock products succeed"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":118,"units_ordered":2,"turnover_score":0.01694915254237288}
      -- HTTP 200 in 0.001545s request_id=konan-1787079548-18783
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:29:24.068Z and 18:39:38.833Z — the only two chaos-toggle events in the observed window, identical values"
    quote: |-
      {"ts": "2026-08-18T18:29:24.068Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "57ee29738398", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
      {"ts": "2026-08-18T18:39:38.833Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "59b2268e88a7", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E10
    type: log
    source: "lab/logs/app.log — all four startup events in the observed window, no shutdown/exit/crash event precedes any of them anywhere in the log"
    quote: |-
      {"ts": "2026-08-18T18:29:17.911Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
      {"ts": "2026-08-18T18:39:32.880Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
      {"ts": "2026-08-18T18:48:03.701Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
      {"ts": "2026-08-18T18:55:39.341Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
gaps:
  - "The restart loop noted under H2 (E10) has no in-app cause visible on this surface — no shutdown/crash/exit event precedes any of the four startups. What is cycling the process is outside the investigator's read-only surface (no access to a process supervisor or host-level trace). It is excluded as the incident's cause on the strength of what IS visible: /health stayed 200 across every restart (E1), and the failure boundary tracks product id, not proximity to a restart (E5, E6) — but the restart cause itself remains unexplained and worth an operator-side look."
  - "Chaos-toggle history is a snapshot surface: only two chaos_enabled log lines exist in the whole window, both with failure_rate 0.0 and error_status 503 (E9), and no chaos_disabled event appears at all. That is enough to invalidate H3 for this specific defect (wrong status code, wrong rate, timing predates onset by ~19 minutes) but a continuous operator-side toggle audit trail is outside the surface and was not available to double check nothing else was toggled silently."
  - "Traffic origin for the non-investigator failing requests (E6) is outside the surface: they carry only loopback client ports (50048-50053), so 'several customers' is supported only as four-plus distinct unstamped requests over ~6 seconds, consistent with the complaint but not verifiable as distinct individual customers from target-side telemetry alone."
usage:
  model: claude-sonnet-5
  tokens: 3832755
  wall_clock_seconds: 323
---

# human-report: /products/3 errors out for every visitor with a ZeroDivisionError

## Summary

Verdict: **root-cause-identified**. `GET /products/3` deterministically returns HTTP 500
because the product-detail handler computes `turnover_score = units_ordered /
product["units_in_stock"]`, and product 3 ("Unobtainium Ingot") is carried in the
catalog with `units_in_stock: 0` (E2) — a zero denominator that throws an unhandled
`ZeroDivisionError` on every single request for that product (E3, E7), while every
other product id (1, 2, 4, 5) succeeds every time it's requested (E5, E8). Real,
non-investigator traffic hit this same failure repeatedly during the observation window
(E6), matching the complaint exactly: one specific product page is broken, other pages
load fine, and it recurs on every refresh because the defect is deterministic, not
transient. No deploy or config-change marker correlates with onset; the one chaos
toggle found in the logs is configured with `failure_rate: 0.0` and the wrong status
code (503, not 500) and predates the first observed failure by ~19 minutes (E9) — ruled
out. A separate process-restart pattern was also found and ruled out as the cause (see
Gaps) — it does not explain a failure confined to one product id. Confidence: high; the
defect was reproduced live on demand (E7, E8) and confirmed by the source line and
exception type quoted straight from the logs (E3).

## Timeline

- **18:29:17Z – 18:55:39Z** (E10): faultline process starts four times across the
  observed window; no crash/shutdown marker precedes any restart.
- **18:29:24Z, 18:39:38Z** (E9): the only two chaos-toggle events in the window,
  `failure_rate: 0.0`, `error_status: 503` — inert for this defect and long before the
  first observed failure.
- **18:48:10.692Z** (E3): first captured `unhandled_exception` / `ZeroDivisionError` for
  `/products/3` in this process lifetime, immediately followed by the 500 access line.
- **18:53:29Z** (E5): `/products/4` and `/products/5` both succeed (200) in the same
  window.
- **18:55:41-42Z** (E5): `/products/1` and `/products/2` succeed (200) seconds before
  the next failure burst.
- **18:55:46-52Z** (E6): four unstamped (non-investigator) requests to `/products/3`,
  all 500 — the user-facing burst matching the complaint.
- **18:59:06Z / 18:59:08Z** (E7, E8): investigator reproduces the failure on
  `/products/3` and confirms success plus the `turnover_score` formula on `/products/1`.

## Investigation

Baseline: `/health` reported OK (E1); `/metrics` already showed
`http_exceptions_total{type="ZeroDivisionError"} 4` and 4 prior 500s on
`/products/{product_id}` (E4) alongside clean 200s elsewhere — a signal in the baseline
itself, not just the complaint.

Triage ran all three lenses in parallel, each blind to the others, given only the lens
file, `docs/lab.md`, the complaint verbatim, and this baseline summary:

- **software-defect** lens: found the exact throwing line
  (`shop.py:64`, `units_ordered / product["units_in_stock"]`), confirmed the failure is
  isolated to `product_id=3`, and reproduced it live.
- **interfaces** lens: found no gateway-shaped or probabilistic pattern — 100% of
  `/products/3` requests fail, 100% of every other product id succeeds — and explicitly
  ruled out the chaos-toggle marker on rate and status-code grounds.
- **infra-process** lens: found a restart loop (four startups, no crash marker) but no
  latency/saturation signature, and flagged the exception content as outside its domain.

`software-defect`'s evidence was already deterministic and complete (live reproduction,
exact source line, clean data-dependent split), so per the loop's skip rule this
hypothesis went straight to judge rather than a redundant deep-dive round. The
`infra-process` restart-loop finding does not predict a per-product-id failure pattern,
so it was carried to judge as a competing/secondary hypothesis rather than deep-dived
further (the "why" of the restarts is outside the surface — see Gaps).

An adversarial judge, shown only the hypothesis statements and verbatim cited evidence
(no narrative), validated H1 and invalidated H2 and H3, in both cases because the cited
evidence does not predict what the hypothesis requires (H2: failures would need to
track restart proximity, not product id; H3: the toggle's own logged rate and status
code don't match what was observed).

## Hypotheses

### H1 — software defect (validated)

`GET /products/3` computes `turnover_score = units_ordered / product["units_in_stock"]`
against a catalog record with `units_in_stock: 0` (E2), throwing `ZeroDivisionError`
(E3) on every request. The split is clean: every request to id 3 fails, every request
to ids 1/2/4/5 succeeds, in both real traffic (E5, E6) and investigator probes (E7, E8).
No evidence against.

### H2 — restart loop is the cause (invalidated)

The process restarted four times with no visible crash cause (E10), but `/health`
stayed 200 throughout every restart (E1) and the failure boundary is precisely
per-product-id, not correlated with proximity to any restart (E5 shows clean successes
on other ids right before and after the 18:55 failure burst; E6 shows the burst itself
concentrated only on id 3). The judge: a restart-loop cause would be expected to
produce failures spread across endpoints near each restart, which isn't observed.

### H3 — chaos/config toggle (invalidated)

The only chaos-toggle events logged (E9) specify `failure_rate: 0.0` (should inject
nothing) and `error_status: 503` (observed failures are 500s with `ZeroDivisionError`,
not injected 503s), and both events predate the first observed `/products/3` failure by
about 19 minutes. The judge: the cited evidence contradicts rather than supports this
hypothesis on its own terms.

## Safe next steps

- Read `lab/logs/app.log` around any future `/products/{id}` 500 and grep the
  `request_id` to pull the paired `unhandled_exception` line — confirms whether it's the
  same `shop.py:64` signature or a new one.
- Probe `/products` (read-only) periodically to watch for other catalog entries drifting
  to `units_in_stock: 0` — same shape would recur for any such id (product 4's
  `price: null` is a similar catalog-data smell worth the same watch — see latent
  findings).
- If a process-restart cause needs chasing, that's operator/host-level (outside this
  read-only surface) — worth a look but not urgent, since restarts don't correlate with
  the reported symptom.

## Gaps

- The restart loop (E10) has no in-app cause visible here; process-supervisor or
  host-level traces are outside the read-only surface. Excluded as the incident's cause
  by health continuity (E1) and the per-product-id failure boundary (E5, E6), but the
  restart cause itself is unexplained and worth an operator-side look.
- Chaos-toggle history is snapshot-only: two `chaos_enabled` lines (E9), no
  `chaos_disabled` line at all, and no continuous operator-side audit trail was
  available to double check nothing else toggled silently in between.
- Traffic origin for the non-investigator failures (E6) is outside the surface — only
  loopback client ports are visible, so "several customers" is supported as four-plus
  distinct unstamped requests over ~6 seconds, not verified as distinct individuals.
