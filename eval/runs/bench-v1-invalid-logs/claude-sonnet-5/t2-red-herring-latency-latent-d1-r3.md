---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-slow-chaos-latency
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-18T21:18:33Z
  concluded: 2026-08-18T21:25:55Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was re-enabled at 21:18:11.528Z with extra_latency_ms=1500 (failure_rate=0.0), injecting ~1.4s of added latency into every business route while /health bypasses the chaos middleware entirely."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode re-enabled at 21:18:11.528Z (extra_latency_ms=1500, failure_rate=0.0) is injecting ~1.4s latency into /products, /products/{id}, /orders and POST /orders for real traffic, while /health stays sub-millisecond throughout — the mechanism behind 'painfully slow' shop with 'health checks green and fast'."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The reported 'error page seen once' is caused by real user traffic hitting the GET /products/3 ZeroDivisionError bug."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11]
  - id: H3
    statement: "The reported 'error page seen once' refers to the earlier chaos episode (20:07:20Z-20:22:07Z) that injected real HTTP 503s via a failure_rate=0.6 config."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E12, E13, E14]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 throws a deterministic ZeroDivisionError (units_ordered / units_in_stock, with units_in_stock=0 for product 3) — a real, reproducible code defect — but every one of the 9 occurrences in the log carries an investigator-stamped request id; no real user request has hit it yet."
    evidence: [E9, E10, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:18:11.528Z"
    quote: '{"ts": "2026-08-18T21:18:11.528Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "9791633c30c5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:18:08.464Z"
    quote: '{"ts": "2026-08-18T21:18:08.464Z", "message": "POST /orders -> 201", "request_id": "811bb304f34d", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.966}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:18:15.002Z"
    quote: '{"ts": "2026-08-18T21:18:15.002Z", "message": "GET /products -> 200", "request_id": "810110244b11", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1414.619}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:18:18.754Z-21:18:23.180Z"
    quote: '{"path": "/products/1", "status": 200, "duration_ms": 1475.496, "request_id": "12df8103ab91"}; {"path": "/orders", "status": 201, "duration_ms": 1435.496, "request_id": "a556bd3d028b"}; {"path": "/orders", "status": 200, "duration_ms": 863.476, "request_id": "dac331ef9385"} — none carry the investigator konan- prefix'
  - id: E5
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-08-18T21:19:15Z"
    quote: "faultline_chaos_enabled 1"
  - id: E6
    type: probe
    source: "scripts/probe.sh /health @ 2026-08-18T21:19:15Z, and lab/logs/app.log @ 2026-08-18T21:18:04.206Z"
    quote: 'pre-chaos: {"path": "/health", "status": 200, "duration_ms": 0.756}; during-chaos investigator probe trailer: "-- HTTP 200 in 0.002398s request_id=konan-1787087955-26201"'
  - id: E7
    type: log
    source: "lab/logs/app.log full-file grep for event=chaos_disabled"
    quote: 'last chaos_disabled event in the file: {"ts": "2026-08-18T20:22:07.911Z", "message": "chaos mode disabled", "request_id": "0d3ed61424da", "event": "chaos_disabled"} — none after this timestamp'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:18:04.220Z-21:18:05.579Z"
    quote: '{"ts": "2026-08-18T21:18:04.220Z", "message": "Shutting down"} ... {"ts": "2026-08-18T21:18:05.579Z", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:12:32.575Z"
    quote: '{"ts": "2026-08-18T21:12:32.575Z", "level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1787087551-25827", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n...ZeroDivisionError: division by zero"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:12:32.593Z"
    quote: '{"ts": "2026-08-18T21:12:32.593Z", "message": "GET /products/3 -> 500", "request_id": "konan-1787087551-25827", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1332.201}'
  - id: E11
    type: log
    source: "lab/logs/app.log full-file grep for path=/products/3 status=500"
    quote: "all 9 occurrences of GET /products/3 -> 500 in the file carry a konan- prefixed request_id; zero carry an unstamped (real-user) request_id"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:20.948Z"
    quote: '{"ts": "2026-08-18T20:07:20.948Z", "message": "chaos mode enabled", "request_id": "ddc4edac99ce", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:22.009Z"
    quote: '{"ts": "2026-08-18T20:07:22.009Z", "message": "GET /products -> 503", "request_id": "33c824dddf8e", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.294}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:07.911Z"
    quote: '{"ts": "2026-08-18T20:22:07.911Z", "message": "chaos mode disabled", "request_id": "0d3ed61424da", "event": "chaos_disabled"}'
gaps:
  - "The complaint's 'seeing an error page once' has no corroborating evidence in the current window: no real-user (unstamped) request in the log around 21:18:33Z returned any non-2xx status. The nearest real user-facing errors (E12-E14) are ~56 minutes stale and used a different chaos config (error injection, not latency), so they were ruled out as the source (H3 invalidated). The surface contract has no client-side or browser telemetry, so a client-perceived timeout/error during the ~1.4s latency spikes (E3, E4) cannot be confirmed or ruled out from server-side logs alone."
  - "No load-saturation-specific lens exists in this repo's lens set (infra-process, interfaces, software-defect only); infra-process coverage substituted for it and found no resource-saturation evidence (RSS, uptime nominal), but a dedicated load lens was not run."
usage:
  model: claude-sonnet-5
  tokens: 2710850
  wall_clock_seconds: 442
---

# Shop-wide slowness from re-armed chaos latency injection

## Summary

**Root cause identified.** The shop-wide slowness reported by users is caused by chaos
mode being re-enabled at `21:18:11.528Z` with `extra_latency_ms=1500` and
`failure_rate=0.0` (E1) — a pure latency injection, no forced error statuses. Real user
requests (unstamped request ids) to `/products`, `/products/{id}`, `/orders`, and
`POST /orders` jumped from ~1-2ms to 863-1475ms within seconds of the marker (E2-E4),
while `/health` stayed sub-millisecond both before and during the episode (E6) — matching
the complaint's "painfully slow" plus "health checks are green and fast" precisely.
Chaos was still active at the end of this investigation (E5, E7). The "error page seen
once" part of the complaint does **not** have corroborating evidence in this window:
real traffic during the slow episode returned only 200/201 (E3, E4); a genuinely
error-injecting chaos episode did occur earlier (E12-E13) but ended 56 minutes before
this investigation started and used an unrelated config (H3, invalidated); and a real
ZeroDivisionError bug on `GET /products/3` exists (E9-E11) but has only ever been
triggered by investigator probes, never real traffic (H2, invalidated) — it rides along
as a latent finding. Confidence in the latency root cause is high (deterministic
timestamp correlation, config read directly from the log, real-traffic before/after
comparison); confidence in what specifically produced the "error page" report is low —
it is an open gap.

## Timeline (UTC)

- `21:18:04.220Z` — process shutdown begins (E8)
- `21:18:05.579Z` — process restarts, faultline 0.1.0 started (E8)
- `21:18:08.464Z` — last known-good: POST /orders in 1.966ms (E2)
- `21:18:11.528Z` — **chaos mode enabled**: extra_latency_ms=1500, failure_rate=0.0 (E1)
- `21:18:15.002Z` — first known-bad: GET /products in 1414.619ms, still 200 (E3)
- `21:18:18.754Z`-`21:18:23.180Z` — sustained slow real-user traffic, 863-1475ms, all 200/201 (E4)
- `21:18:33Z` — investigation started (complaint received, trigger latency ~3s from report)
- `21:19:15Z` — baseline probes: `/health` fast (0.0024s) (E6), `/metrics` shows `faultline_chaos_enabled 1` (E5)
- `21:25:55Z` — investigation concluded

Earlier, unrelated episode for context (not part of this incident, see H3):
- `20:07:20.948Z` — chaos enabled with failure_rate=0.6, extra_latency_ms=0 (E12)
- `20:07:22.009Z` — real user gets 503 on GET /products (E13)
- `20:22:07.911Z` — chaos disabled (E14)

## Investigation

1. **Baseline**: `/health` and `/metrics` probed first. `/metrics` immediately surfaced
   `faultline_chaos_enabled 1` and a recent process restart (~70s uptime) — the
   healthy-monitoring trap was checked explicitly: health is green, but chaos is active.
2. **Triage** (parallel, blind to each other): infra-process, interfaces, and
   software-defect lenses each read `lab/logs/app.log` and confirmed the same restart →
   chaos-enable → latency-spike pattern independently, plus flagged the `/products/3`
   ZeroDivisionError as a separate, deterministic, investigator-only defect.
3. Evidence from triage was already deterministic and complete (exact timestamp
   correlation, config parameters read verbatim from logs, clean before/after
   comparison) — no deep-dive round was needed; the hypothesis set went straight to
   judgment.
4. **Judge** (adversarial, evidence-only): validated H1, invalidated H2 and H3 — see
   Hypotheses below.

## Hypotheses

### H1 — Chaos latency injection (validated)
Chaos was re-armed at `21:18:11.528Z` with `extra_latency_ms=1500`, `failure_rate=0.0`
(E1). The judge confirmed the causal chain: pre-chaos baseline was sub-2ms (E2),
post-chaos real traffic jumped to 863-1475ms (E3, E4), no `chaos_disabled` event
appears anywhere after `20:22:07.911Z` so the injection was still active through the
observed slow requests and at investigation end (E7, E5). `/health` is unaffected
throughout (E6), explaining the complaint's "green and fast" health checks alongside
"painfully slow" everything else.

### H2 — Real users hit the /products/3 bug (invalidated)
No evidence supports real-user impact. Every one of the 9 `ZeroDivisionError`
occurrences on `GET /products/3` in the full log — including the most recent at
`21:12:32Z` (E9, E10) — carries an investigator-stamped `konan-` request id; a full-file
grep found zero unstamped occurrences (E11). This is a real, reproducible defect
(`units_ordered / units_in_stock` with stock 0 for product 3) but not the source of the
current complaint.

### H3 — "Error page" is the earlier 503 episode (invalidated)
An earlier chaos episode did inject real 503s against real traffic (E12, E13), but it
ended at `20:22:07.911Z` (E14) — 56 minutes before this investigation started and using
an entirely different config (error injection, not latency) than the one active now.
Too stale to match the complaint's "last few minutes" framing.

## Safe next steps

- Re-read `/metrics` and `lab/logs/app.log` periodically to confirm whether the
  `extra_latency_ms=1500` chaos episode is eventually disabled (no `chaos_disabled`
  event was observed through investigation end).
- If a responder wants to explain the "error page" report, correlate it against
  client-side/browser telemetry or a support ticket timestamp, if such a source exists
  outside this lab's surface — it cannot be resolved from `lab/logs/app.log` alone.
- Keep an eye on `GET /products/3` — the ZeroDivisionError is real and will surface a
  500 to the first real shopper who requests that product page, even though it hasn't
  yet.

## Gaps

- The "error page seen once" claim has no corroborating server-side evidence in the
  current incident window — no real-user request near `21:18:33Z` returned non-2xx.
  Whether it was a client-perceived timeout during the ~1.4s latency spikes, a stale
  memory of the earlier 503 episode, or something outside this lab's telemetry surface
  could not be determined from the available logs/metrics alone.
- This repo's lens set has no dedicated load-saturation lens; infra-process coverage was
  used as a substitute and found no resource-saturation signal (RSS and uptime both
  nominal), but a dedicated load-focused pass was not run.
