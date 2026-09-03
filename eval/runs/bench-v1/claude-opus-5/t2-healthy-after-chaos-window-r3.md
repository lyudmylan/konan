---
konan_journal: 1
investigation:
  id: 2026-08-19-handover-check
  trigger: "manual — /konan human profile; complaint object: source=human, fingerprint=human-1787140566, labels.alertname=human-report (no severity stated by reporter), startsAt=2026-08-19T11:56:06Z; investigation started 2026-08-19T11:56:31Z (trigger latency 25s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-19T11:56:31Z
  concluded: 2026-08-19T11:58:22Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The earlier noise was an operator-enabled chaos-injection window (failure_rate 0.6, error_status 503) that ran 11:55:28.770Z–11:55:35.143Z and was switched off; it is closed, not ongoing."
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E5, E9]
    evidence_against: []
  - id: H2
    statement: "Users are currently being served 500s by a data-dependent defect on GET /products/{id} for zero-stock products."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8]
    evidence_against: [E9, E10, E11]
  - id: H3
    statement: "The 503 on GET /products/2 was a per-input code defect on that product, so product 2 is still broken."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E3]
    evidence_against: [E4, E6, E12]
  - id: H4
    statement: "The service is unstable at the process level — crash/restart loop or resource saturation behind the noise."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13, E14]
latent_findings:
  - statement: "GET /products/{id} raises an unhandled ZeroDivisionError (HTTP 500) when the product has units_in_stock = 0 — the detail route computes turnover_score = units_ordered / units_in_stock without guarding the zero divisor. Product 3 (Unobtainium Ingot, units_in_stock 0) is currently in that state. Only this investigation's probe has ever triggered it in the running process; no user request has hit it."
    evidence: [E7, E8, E10, E11]
  - statement: "Product 4 (Mystery Box) is served with price = null on both the list and the detail route. The read surface tolerates it (HTTP 200), but any price arithmetic on it — e.g. order total_price — is a plausible failure that this read-only investigation could not test."
    evidence: [E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:55:24.883Z"
    quote: '{"ts": "2026-08-19T11:55:24.883Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:55:28.770Z"
    quote: '{"ts": "2026-08-19T11:55:28.770Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "f72bc3b34c6d", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:55:30.889Z"
    quote: '{"ts": "2026-08-19T11:55:30.889Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "3569e52e6d7c", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:55:30.889Z"
    quote: '{"ts": "2026-08-19T11:55:30.889Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "3569e52e6d7c", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.217, "client": "127.0.0.1:60073"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:55:35.143Z"
    quote: '{"ts": "2026-08-19T11:55:35.143Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "d5208954f622", "event": "chaos_disabled"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:55:55.205Z – 11:55:59.457Z (post-chaos user traffic, five consecutive lines)"
    quote: '"GET /products -> 200" (d4abf9a250be); "GET /products/1 -> 200" (ed18bdcb6fb9); {"event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0} then "POST /orders -> 201" (544fdac19898); "GET /orders -> 200" (da2f30e068f3); "GET /products/5 -> 200" (fa830e6938a9)'
  - id: E7
    type: probe
    source: "GET /products (request_id konan-1787140643-56857)"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E8
    type: probe
    source: "GET /products/3 (request_id konan-1787140651-56869)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787140651-56869"} -- HTTP 500 in 0.009063s'
  - id: E9
    type: metric
    source: "GET /metrics (request_id konan-1787140597-56834, first scrape — before this investigation probed any product detail route)"
    quote: 'faultline_chaos_enabled 0 ; http_requests_total{method="GET",path="/products/2",status="503"} 1 ; http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4 ; "# HELP http_exceptions_total Unhandled exceptions by Python class name." followed by no counter lines'
  - id: E10
    type: metric
    source: "GET /metrics (request_id konan-1787140664-56888, second scrape — after this investigation probed /products/3)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 1 ; http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:57:31.765Z"
    quote: '{"ts": "2026-08-19T11:57:31.765Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787140651-56869", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  File \"/Users/lyudmylan/Projects/faultline/src/faultline/middleware.py\", line 72, in _handle\n    return await call_next(request)"'
  - id: E12
    type: probe
    source: "GET /products/2 (request_id konan-1787140646-56863)"
    quote: '{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39,"units_ordered":1,"turnover_score":0.02564102564102564} -- HTTP 200 in 0.001495s'
  - id: E13
    type: probe
    source: "GET /health (request_id konan-1787140595-56828)"
    quote: '{"status":"ok","uptime_seconds":70.5924619580619} -- HTTP 200 in 0.001650s'
  - id: E14
    type: metric
    source: "GET /metrics (request_ids konan-1787140597-56834 then konan-1787140664-56888)"
    quote: 'process_uptime_seconds 72.94283658312634 then process_uptime_seconds 139.52689341711812 ; process_max_rss_bytes 47169536 unchanged across both scrapes'
  - id: E15
    type: probe
    source: "GET /products/4 (request_id konan-1787140657-56875)"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0} -- HTTP 200 in 0.001560s'
  - id: E16
    type: probe
    source: "GET /orders (request_id konan-1787140662-56882)"
    quote: '[{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-08-19T11:55:33.014+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-08-19T11:55:57.335+00:00"}] -- HTTP 200 in 0.001597s'
gaps:
  - "Telemetry does not reach back before 2026-08-19T11:55:24.883Z (E1). The process started then and lab/logs/ holds only app.log — no .1–.3 rotated backups exist. If the reporter's \"noise earlier\" predates that startup, nothing in the allowed surface can see it; the chaos window at 11:55:28–11:55:35 is the only noise this process recorded."
  - "The order-creation path could not be exercised. POST is outside the read-only probe allowlist, so the null price on product 4 (E15) stays an untested failure mode — the two existing orders (E16) both used priced products."
  - "The latent zero-stock 500 was found by probing /products/3 directly. Whether real users reach that route is unknown beyond this process's lifetime; per-route history before 11:55:24 is unavailable."
  - "Triage lenses (software-defect, interfaces, infra-process) and the adversarial judge were applied in-session by the orchestrator rather than as blind parallel subagents — this session was constrained from spawning subagents. The cross-checks were performed and are cited, but the narrative firewall the loop normally provides was not in place, so confirmation bias is less well controlled than in a standard run."
  - "Chaos was enabled and disabled by the operator surface (E2, E5), which is outside the investigator's reach. Who triggered it, and why, cannot be established from telemetry."
usage:
  model: claude-opus-5
  tokens: 1067914
  wall_clock_seconds: 111
---

# Handover check: no active incident; a closed chaos window explains the noise, plus a latent zero-stock 500

## Summary

**No active incident.** The shop service is healthy right now: `/health` returns
`status: ok` (E13), chaos injection is off (`faultline_chaos_enabled 0`, E9), and every
user request after 11:55:35Z succeeded — product listing, product detail, order
creation, order listing (E6). The "noise earlier" is fully explained: an operator
enabled chaos mode at 11:55:28.770Z with `failure_rate: 0.6, error_status: 503` (E2)
and disabled it 6.4 seconds later at 11:55:35.143Z (E5). Inside that window exactly one
user request failed — `GET /products/2 -> 503`, explicitly tagged `chaos_failure` (E3,
E4). That is the whole of the user-visible impact, and it ended when chaos was switched
off. Confidence: high — the log covers the process's entire lifetime and the failure
carries an injection marker rather than an exception.

Two things worth handing over anyway. First, a **latent defect**: `GET /products/{id}`
crashes with an unhandled `ZeroDivisionError` when the product has `units_in_stock = 0`
(E8, E11) — the detail route divides `units_ordered` by `units_in_stock` to compute
`turnover_score` (visible in the healthy response shape, E12). Product 3 is currently at
zero stock (E7). This is **not** the incident: the exception counter was empty before
this investigation probed (E9) and reads exactly `1` after (E10), and that one is this
investigation's own probe. No user has hit it in this process's lifetime. Second,
product 4 is served with `price: null` (E15); the read surface tolerates it, but order
arithmetic on it is untested and read-only probing cannot test it.

## Timeline

- **11:55:24.883Z** — process starts, `event: startup`, faultline 0.1.0 (E1). This is
  the earliest observable moment; no telemetry exists before it.
- **11:55:25 – 11:55:26** — normal traffic: `/health` ×2, `/products`, `/products/1`,
  all 200.
- **11:55:28.770Z** — **configuration change marker**: chaos mode enabled,
  `failure_rate: 0.6`, `error_status: 503`, `extra_latency_ms: 0` (E2).
- **11:55:30.889Z** — `GET /products/2 -> 503`, preceded on the same request id by
  `chaos-injected failure` (E3, E4). The only user-facing failure of the day.
- **11:55:29 – 11:55:34** — the rest of the window survives the dice: `/products` 200,
  `/products/1` 200, `POST /orders` 201, `/products` 200. One failure in five requests
  against a nominal 0.6 rate — a small sample, not a contradiction.
- **11:55:35.143Z** — **configuration change marker**: chaos mode disabled (E5).
- **11:55:55 – 11:55:59** — post-chaos user traffic, all green: `/products` 200,
  `/products/1` 200, order 2 created (`total_price` 23.0) → 201, `/orders` 200,
  `/products/5` 200 (E6).
- **11:56:35Z onward** — this investigation's probes only (`konan-*` request ids).
- **11:57:31.765Z** — `ZeroDivisionError` on `GET /products/3`, triggered by probe
  `konan-1787140651-56869` (E8, E11). Investigator-caused, recorded for honesty.

## Investigation

Baseline first: `/health` showed `uptime_seconds` ≈ 70 (E13) — a young process, so the
log was likely to cover its whole life, and it does (28 lines at first read). The first
`/metrics` scrape (E9) was taken before any product-detail probing, which is what makes
the exception-counter argument possible later: it showed `http_exceptions_total` with a
HELP line and no counters at all, i.e. zero unhandled exceptions in the process to that
point, and `faultline_chaos_enabled 0`.

The three triage lenses were applied against that baseline:

- **interfaces** — found the timeline gold immediately: two chaos config markers
  bracketing the only 5xx (E2, E5), and the 503 carrying an injection tag rather than an
  exception (E3). Probabilistic, injected, bounded, closed.
- **software-defect** — the first metrics scrape excluded any code-level exception during
  user traffic (E9). The `/products` payload (E7) then surfaced two data-shape oddities
  worth testing on their own merits: `units_in_stock: 0` on product 3 against a detail
  route that reports a `turnover_score` ratio (E12), and `price: null` on product 4.
- **infra-process** — one startup marker, no restarts, uptime advancing monotonically,
  RSS flat at 47169536 across both scrapes, every duration under 2 ms (E1, E13, E14).
  Nothing to pursue.

Deep-dive was targeted rather than broad: re-probe `/products/2` to kill or confirm a
per-input defect (killed — 200, E12); probe `/products/3` to test the zero-divisor
prediction (confirmed — 500 `ZeroDivisionError`, E8); probe `/products/4` to test whether
the null price breaks the read path (it does not — 200, E15); probe `/orders` to check
the business surface end to end (E16). A second `/metrics` scrape (E10) then settled the
latent-vs-active question by attribution: exception count moved 0 → 1, and that 1 is the
investigator's own request id.

The adversarial pass asked of each surviving claim: does the cited evidence actually
support it? The one that needed care is H1 — 1 failure in 5 requests under a declared 0.6
failure rate is weak on its own. It holds because the claim does not rest on the rate: it
rests on the explicit `chaos_enabled` / `chaos_failure` / `chaos_disabled` markers and on
the current gauge reading 0. Per the loop's own standard this pass is weaker than usual —
see Gaps.

## Hypotheses

### H1 — operator chaos window (validated)

The noise was injected degradation, deliberately switched on and off. Evidence for: the
enable marker with its parameters (E2), the injection-tagged failure inside the window
(E3, E4), the disable marker (E5), the current gauge at 0 (E9). Nothing argues against
it. The window is closed; the user impact is one 503 on one request.

### H2 — users are being served zero-stock 500s (invalidated)

The defect is real (E7, E8) but the incident claim is not. The pre-probe metrics scrape
showed no exception counters at all (E9), the post-probe scrape shows exactly one (E10),
and the corresponding log line carries request id `konan-1787140651-56869` — this
investigation's own probe (E11). No user request triggered it. It rides as a latent
finding, not as the verdict.

### H3 — /products/2 is broken per-input (invalidated)

Re-probing returned a complete, healthy body (E12), the failure was tagged
`chaos_failure` rather than an exception (E4), and a user order for product 2 succeeded
at 11:55:57 during the same process (E6). Deterministic per-input failure is the
software-defect signature; this failed exactly once, under injection, and never again.

### H4 — process-level instability (invalidated)

One startup marker in the whole log (E1), `uptime_seconds` advancing 70 → 73 → 140 with
no reset (E13, E14), `process_max_rss_bytes` identical across scrapes (E14), all request
durations sub-2 ms. No restart loop, no saturation, no flap.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. Ask the operator who enabled chaos at 11:55:28.770Z (E2) whether it was a planned
   exercise. If it was, the handover has no open item from the noise; if not, that is a
   process question, not a service question.
2. Track the zero-stock 500 as a defect against faultline with E7/E8/E11 attached. The
   observable trigger is any product reaching `units_in_stock: 0` — product 3 is in that
   state now, so the next user who opens its detail page gets a 500.
3. Watch `http_exceptions_total{type="ZeroDivisionError"}` against non-`konan-*` request
   ids. Any increment there converts the latent finding into an active incident.
4. Confirm on the faultline side whether `POST /orders` guards a null `price` before
   product 4 is orderable (E15). This investigation could not test it read-only.
5. Note that this process is minutes old and logs do not rotate back yet — if the
   reporter believes the noise predates 11:55:24Z, the answer is not in the current
   telemetry and the question should go to whoever restarted the service.

## Gaps

- **No telemetry before 11:55:24.883Z.** The process started then, and `lab/logs/`
  contains only `app.log` with no `.1`–`.3` backups. The reporter's "earlier" is assumed
  to mean the chaos window; if they mean something before the restart, this
  investigation cannot see it.
- **The write path is untestable.** `POST` is outside the read-only probe allowlist, so
  the null-price product (E15) could only be checked on read routes. Both existing
  orders used priced products (E16).
- **Latent-defect exposure is unquantified.** `/products/3` was reached by probing it
  directly; how often real users open a zero-stock product detail page is not visible in
  this process's short history.
- **Lenses and judge ran in-session.** This session was constrained from spawning
  subagents, so the three lens sweeps and the adversarial pass were performed by the
  orchestrator rather than by blind parallel agents and a firewalled judge. Every
  cross-check is cited, but the structural protection against narrative capture was
  absent — treat the confidence here as one investigator's, not a panel's.
- **The chaos trigger's origin is unknowable from telemetry.** `/chaos` is operator
  surface, outside the investigator's contract; the logs record that it was enabled and
  disabled (E2, E5), never by whom or why.
