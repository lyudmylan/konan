---
konan_journal: 1
investigation:
  id: 2026-08-25-shop-wide-latency-chaos-flag
  trigger: "manual (/konan, human profile; fingerprint human-1787633652; startsAt 2026-08-25T04:54:12Z; investigation start 2026-08-25T04:55:14Z; trigger latency 62s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-25T04:55:14Z
  concluded: 2026-08-25T04:59:58Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change at 04:53:52.776Z enabled chaos mode with extra_latency_ms 1500 (failure_rate 0.0), which injects up to ~1.5 s of latency into every shop request (products, orders) while /health and /metrics stay fast, so the shop is slow and the health checks stay green."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode enabled at 04:53:52.776Z (extra_latency_ms 1500, failure_rate 0.0) injects variable latency up to ~1.5 s into every shop route; /health and /metrics are exempt, which explains green and fast health checks during a slow shop."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E23, E2, E3, E4, E5, E6, E7, E8, E29, E9, E27, E10, E25, E11, E12, E26, E30]
    evidence_against: []
  - id: H2
    statement: "The 'error page once' was a user request to /products/3 hitting the ZeroDivisionError in get_product (units_in_stock 0) during the incident window."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E18, E19, E20, E21, E24]
    evidence_against: [E13, E14, E22, E28]
  - id: H3
    statement: "The 'error page once' was a chaos-injected 503 (error_status 503) fired probabilistically by the same chaos configuration."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13, E28]
  - id: H4
    statement: "The slowness and the error page come from a process crash/restart or resource saturation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E15, E16, E17, E10, E25]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 deterministically (2/2) with ZeroDivisionError in get_product: turnover_score divides units_ordered by units_in_stock, and product 3 is the only product with units_in_stock 0. Only investigator probes (konan-*) ever triggered it; no user request reached /products/3."
    evidence: [E18, E19, E20, E21, E24, E22]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:52.776Z"
    quote: '{"ts": "2026-08-25T04:53:52.776Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "4bf1019c7371", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:47.572Z"
    quote: '{"ts": "2026-08-25T04:53:47.572Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "78f3921d7d54", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.199, "client": "127.0.0.1:65432"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:48.639Z"
    quote: '{"ts": "2026-08-25T04:53:48.639Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "f8077792207a", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.025, "client": "127.0.0.1:65433"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:49.707Z"
    quote: '{"ts": "2026-08-25T04:53:49.707Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "08f3c9ea76c7", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.009, "client": "127.0.0.1:65434"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:55.827Z"
    quote: '{"ts": "2026-08-25T04:53:55.827Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "57008d2bcab7", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 981.308, "client": "127.0.0.1:65436"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:57.959Z"
    quote: '{"ts": "2026-08-25T04:53:57.959Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "1818b4470634", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1050.332, "client": "127.0.0.1:65437"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:59.514Z"
    quote: '{"ts": "2026-08-25T04:53:59.514Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "f11f3ecc4b86", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 469.825, "client": "127.0.0.1:65439"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:54:02.944Z"
    quote: '{"ts": "2026-08-25T04:54:02.944Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "2da4ed6ea931", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1181.286, "client": "127.0.0.1:65441"}'
  - id: E9
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633715-37432 @ 2026-08-25T04:55:15Z"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: probe
    source: "/health, request_id=konan-1787633715-37426 @ 2026-08-25T04:55:15Z"
    quote: '{"status":"ok","uptime_seconds":88.55281587480567} -- HTTP 200 in 0.001539s request_id=konan-1787633715-37426'
  - id: E11
    type: probe
    source: "/products, request_id=konan-1787633743-37444 @ 2026-08-25T04:55:43Z"
    quote: "-- HTTP 200 in 0.477738s request_id=konan-1787633743-37444"
  - id: E12
    type: probe
    source: "/orders, request_id=konan-1787633744-37450 @ 2026-08-25T04:55:44Z"
    quote: "-- HTTP 200 in 0.565053s request_id=konan-1787633744-37450"
  - id: E13
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633715-37432 @ 2026-08-25T04:55:15Z (complete http_requests_total and http_exceptions_total sections, before any investigator probe of a shop route)"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 3 / http_requests_total{method="GET",path="/orders",status="200"} 1 / http_requests_total{method="GET",path="/products",status="200"} 2 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 2 / # HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter / # HELP faultline_chaos_enabled Whether chaos mode is active.'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:46.816Z (line 3 of 37; the only startup event; lab/logs/ holds app.log only, no rotated backups)"
    quote: '{"ts": "2026-08-25T04:53:46.816Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633715-37432 @ 2026-08-25T04:55:15Z"
    quote: "process_uptime_seconds 88.60077912500128"
  - id: E16
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633972-37609 @ 2026-08-25T04:59:32Z"
    quote: "process_uptime_seconds 346.1762794579845"
  - id: E17
    type: metric
    source: "/metrics via scripts/probe.sh @ 2026-08-25T04:55:15Z (konan-1787633715-37432) and @ 2026-08-25T04:59:32Z (konan-1787633972-37609)"
    quote: "process_max_rss_bytes 47529984 / process_max_rss_bytes 48840704"
  - id: E18
    type: probe
    source: "/products/3, request_id=konan-1787633808-37549 @ 2026-08-25T04:56:49Z (software-defect lens)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787633808-37549"} -- HTTP 500 in 0.581000s request_id=konan-1787633808-37549'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:56:49.051Z (stack trimmed to its last frame)"
    quote: '{"ts": "2026-08-25T04:56:49.051Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787633808-37549", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n ... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:56:49.075Z"
    quote: '{"ts": "2026-08-25T04:56:49.075Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787633808-37549", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 579.555, "client": "127.0.0.1:65480"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:56:58.572Z"
    quote: '{"ts": "2026-08-25T04:56:58.572Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787633817-37578", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 756.763, "client": "127.0.0.1:65485"}'
  - id: E22
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633972-37609 @ 2026-08-25T04:59:32Z"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2'
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:53:52.777Z"
    quote: '{"ts": "2026-08-25T04:53:52.777Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "4bf1019c7371", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.72, "client": "127.0.0.1:65435"}'
  - id: E24
    type: probe
    source: "/products, request_id=konan-1787633743-37444 @ 2026-08-25T04:55:43Z (response body)"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:55:15.356Z"
    quote: '{"ts": "2026-08-25T04:55:15.356Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787633715-37426", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.489, "client": "127.0.0.1:65463"}'
  - id: E26
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:56:44.705Z"
    quote: '{"ts": "2026-08-25T04:56:44.705Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1787633803-37521", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1347.882, "client": "127.0.0.1:65477"}'
  - id: E27
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633972-37609 @ 2026-08-25T04:59:32Z"
    quote: "faultline_chaos_enabled 1"
  - id: E28
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787633972-37609 @ 2026-08-25T04:59:32Z (complete http_requests_total section at conclusion)"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 5 / http_requests_total{method="GET",path="/metrics",status="200"} 5 / http_requests_total{method="GET",path="/orders",status="200"} 3 / http_requests_total{method="GET",path="/orders/{order_id}",status="200"} 1 / http_requests_total{method="GET",path="/products",status="200"} 4 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 2'
  - id: E29
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:54:00.685Z"
    quote: '{"ts": "2026-08-25T04:54:00.685Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "cb90d44b5570", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 88.809, "client": "127.0.0.1:65440"}'
  - id: E30
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:56:50.890Z"
    quote: '{"ts": "2026-08-25T04:56:50.890Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders/2 -> 200", "request_id": "konan-1787633809-37565", "event": "request", "method": "GET", "path": "/orders/2", "status": 200, "duration_ms": 1025.512, "client": "127.0.0.1:65482"}'
gaps:
  - "The reported 'error page once' has no server-side trace: every unstamped (user) request line in the whole log has status 200 or 201, and the log covers the process from its start at 04:53:46.816Z (E14, E13, E28). An error seen before that instant, on another service, or on the client side is outside this surface."
  - "No user traffic exists after 04:54:02.944Z (E8); persistence of the slowness after that time is shown by investigator probes only (E11, E12, E26, E30)."
  - "The exemption of /health and /metrics from the injected latency is inferred from behavior (E10, E25 vs E5-E8), not read from configuration; the operator surface that holds chaos configuration is outside the read-only contract."
  - "The decisive counterfactual (disable chaos and observe ~1 ms shop latency again) is a mutation and outside the read-only boundary."
  - "No CPU or thread/worker gauges exist on /metrics; saturation is excluded only by flat RSS (E17), monotonic uptime (E15, E16) and fast /health (E10, E25)."
  - "POST /orders for product 3 (units_in_stock 0) or product 4 (price null, E24) cannot be exercised read-only; whether those inputs fail on the order path is unverified."
usage:
  model: claude-fable-5
  tokens: 1277966
  wall_clock_seconds: 284
---

# Shop-wide latency after chaos mode was enabled with 1.5 s extra latency; health exempt

## Summary

**Verdict: root cause identified (H1, incident class: interfaces — runtime configuration change).** At 04:53:52.776Z a `chaos_enabled` marker was logged with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E1, E23). Every user shop request before that instant completed in 1–2 ms (E2, E3, E4); every user shop request after it took 470–1181 ms (E5–E8), and a POST /orders took 89 ms instead of 2 ms (E29). The gauge `faultline_chaos_enabled` read 1 at 04:55:15Z and still at 04:59:32Z (E9, E27), and investigator probes of /products and /orders still took 0.48–1.35 s at conclusion (E11, E12, E26, E30). Meanwhile /health answered in 0.5–1.5 ms throughout (E10, E25) — the healthy-monitoring trap: the injected latency does not touch /health or /metrics, so "health checks are green and fast" is expected and is not evidence against the incident. Impact: all shop routes (products, product detail, orders) for all users since 04:53:52.776Z; no errors were produced by this cause. Confidence: high — a single logged change marker sits 3 s before a 500× latency step on every business route, with no competing lifecycle or resource signal (E14–E17), and the judge validated H1 with no evidence against it.

The "error page once" is **not explained** by telemetry: there is no non-2xx response for any user request in the whole log (E13, E28). The only 5xx observed was triggered by investigator probes: GET /products/3 returns 500 (ZeroDivisionError, deterministic 2/2) because product 3 has `units_in_stock: 0` (E18–E22, E24). That is recorded as a **latent finding**, not the active incident.

## Timeline

- 04:53:46.816Z — process start, `faultline 0.1.0 started`; the only startup event (E14).
- 04:53:47.572Z–04:53:49.707Z — user traffic normal: /products 1.2 ms, /products/1 1.0 ms, POST /orders 2.0 ms (E2, E3, E4). Last known-good: 04:53:49.707Z.
- **04:53:52.776Z — change marker: `chaos mode enabled`, `extra_latency_ms: 1500`, `failure_rate: 0.0`, `error_status: 503` (E1); `POST /chaos/enable -> 200` from an unstamped client (E23).**
- 04:53:55.827Z — first known-bad: /products 981 ms (E5); then /products/2 1050 ms (E6), /products/1 470 ms (E7), POST /orders 89 ms (E29), /orders 1181 ms (E8, 04:54:02.944Z, last user request in the log).
- 04:54:12Z — complaint raised (`startsAt`); 04:55:14Z — investigation start (trigger latency 62 s).
- 04:55:15Z — baseline: /health 200 in 1.5 ms (E10, E25), `faultline_chaos_enabled 1` (E9), uptime 88.6 s (E15), only 2xx series and no exception series (E13).
- 04:55:43Z–04:56:50Z — probes confirm the condition persists: /products 0.48 s and 1.35 s, /orders 0.57 s, /orders/2 1.03 s (E11, E12, E26, E30).
- 04:56:49Z, 04:56:58Z — investigator probes of /products/3 → 500 ZeroDivisionError, twice (E18–E21); latent, konan-* ids only.
- 04:59:32Z — conclusion snapshot: `faultline_chaos_enabled 1`, uptime 346 s (monotonic), RSS 48.8 MB, the only 500 series is the two investigator probes (E27, E16, E17, E22, E28).

## Investigation

- **Baseline** (orchestrator): /health, /metrics, full log tail (19 lines at the time), /products, /orders. The log already showed the chaos marker and a latency step; health fast; no exceptions.
- **Triage** — three lenses in parallel, blind to each other: infra-process, interfaces, software-defect. Each triage prompt carried the four prescribed items plus a short block of mechanical boundary rules (one probe per command, relative paths, no git, no operator-surface strings) — added because the session's boundary tripwire is session-wide and one denial had already been recorded (see below). Findings converged: a single change marker at 04:53:52.776Z with a sharp latency onset on all shop routes and /health exempt (interfaces, infra-process); alive-but-degraded, no restart or saturation (infra-process); no user-visible error anywhere and a latent, deterministic /products/3 500 triggered only by probes (software-defect).
- **Deep-dive**: none spawned. H1's triage evidence was deterministic and complete (marker + before/after on every route + gauge + persistence), so it went straight to the judge; H2–H4 were already contradicted by complete log and metrics scans.
- **Judge** (fresh agent, evidence-only, no tools): H1 validated; H2, H3, H4 invalidated. The judge's one residual gap for H1 — no gauge reading quoted after 04:55:15Z while symptoms were shown at 04:56:43Z — is closed by the 04:59:32Z scrape (E27) taken in the same window as the last slow probes.
- **Boundary note**: one boundary denial occurred early — the orchestrator's first listing command combined `git` with an absolute worktree path, which the eval-blind rule rejects. No target-touching or mutating command was attempted; all later commands used the pre-approved shapes. Recorded here per the contract's "record the wall" rule.

## Hypotheses

### H1 — injected latency from the chaos configuration change (validated)

Statement: chaos mode enabled at 04:53:52.776Z with `extra_latency_ms 1500` adds variable latency (observed 89–1348 ms) to every shop request; /health and /metrics are exempt. For: the marker itself (E1, E23); user traffic 1–2 ms before (E2–E4) and 470–1181 ms after (E5–E8, E29); gauge 1 at baseline and at conclusion (E9, E27); probes 0.48–1.35 s on shop routes (E11, E12, E26, E30) while /health stayed 0.5–1.5 ms (E10, E25). Against: none. The prediction — every non-health request after the marker slower by 0–1.5 s with no errors, health unaffected, gauge stays 1 while symptoms persist — held on every observation.

### H2 — the error page was a user hitting the /products/3 ZeroDivisionError (invalidated)

The defect is real and deterministic (E18–E21), and product 3 is the only zero-stock product (E24). But before any investigator probe the metrics had no exception series and only 2xx status series (E13); the log covers the whole process life with one startup (E14); at conclusion the only 500 series counts exactly 2, matching the two konan-* probes (E22, E28). No user request to /products/3 exists. Kept as a latent finding.

### H3 — the error page was a chaos-injected 503 (invalidated)

The same marker sets `failure_rate: 0.0` (E1), no 503 series exists (E13, E28), and the log has no `chaos_failure` event. The configuration cannot fire a 503 by its own terms.

### H4 — crash/restart or resource saturation (invalidated)

One startup event (E14); uptime monotonic 88.6 s → 346.2 s (E15, E16); RSS flat at ~47.5–48.8 MB (E17); /health fast and stable (E10, E25). Alive and degraded, not restarted or starved.

## Safe next steps

- Read-only: check who or what issued `POST /chaos/enable` at 04:53:52.777Z from `127.0.0.1:65435` (E23) — an operator action, a stale scenario, or an unintended trigger; the answer settles whether the change was intended.
- Read-only: keep watching `faultline_chaos_enabled` and the `http_request_duration_seconds_sum/_count` ratio on `/products` and `/orders`; a return to ~1 ms coinciding with a `chaos_disabled` event would confirm the mechanism end to end.
- Read-only: ask the reporters for the time and URL of the "error page"; if it was `/products/3`, the latent finding becomes the answer; if it predates 04:53:46.816Z, it belongs to an earlier process whose log is not on this surface.
- Do not alert on `/health` alone for this service: it is exempt from the injected latency (E10, E25 vs E5–E8).
- Latent: `/products/3` (zero stock) 500s deterministically on the `turnover_score` division (E19); product 4 has `price: null` (E24) and is an untested input for the order path.

## Gaps

- **Error page unexplained.** Every user request line in the log is 200/201 (E13, E28) and the log spans the process's entire life (E14). The report cannot be confirmed or refuted from this surface; it could be an earlier process, another service, or client-side.
- **No user traffic after 04:54:02.944Z (E8).** Persistence of the condition is shown by konan-* probes only.
- **Health/metrics exemption is behavioral inference.** The chaos configuration lives on the operator surface, outside the read-only contract.
- **No counterfactual.** Disabling chaos is a mutation and outside the boundary.
- **No CPU/thread gauges.** Saturation is excluded by RSS, uptime and health only.
- **Order-path inputs untested.** POST is not probeable read-only; product 3 (stock 0) and product 4 (price null) on `/orders` remain unverified.
