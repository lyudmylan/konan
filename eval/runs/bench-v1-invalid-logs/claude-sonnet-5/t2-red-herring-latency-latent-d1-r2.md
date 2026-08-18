---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-slowness-chaos-latency
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-18T21:08:56Z
  concluded: 2026-08-18T21:16:07Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos latency injection (failure_rate=0.0, extra_latency_ms=1500) was re-armed at 2026-08-18T21:08:38Z, adding hundreds of milliseconds to over a second of per-request latency to real shop traffic (products, orders) while /health and /metrics stayed fast, producing the 'painfully slow' symptom."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos-injected extra latency, re-enabled at 21:08:38Z, is the active cause of the reported shop-wide slowness."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: []
  - id: H2
    statement: "The GET /products/3 ZeroDivisionError (division by zero when a product's stock is 0) is the cause of the reported 'error page once'."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8]
    evidence_against: [E9, E10]
  - id: H3
    statement: "The earlier high-failure-rate chaos episode (failure_rate=0.6, ~20:07-20:22) is the cause of the reported 'error page once'."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E11]
    evidence_against: [E12]
latent_findings:
  - statement: "GET /products/3 throws an unhandled ZeroDivisionError (src/faultline/shop.py:64, units_ordered / product['units_in_stock'] when stock is 0) — a deterministic, 100%-reproducible defect. Every occurrence in the full retained log (9/9) was triggered by investigator-stamped probes; no real user traffic has ever hit it."
    evidence: [E7, E9, E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:08:38.273Z"
    quote: '{"ts": "2026-08-18T21:08:38.273Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "a578bdda60fd", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:08:33.088Z (unstamped request, pre-chaos baseline)"
    quote: '{"ts": "2026-08-18T21:08:33.088Z", "message": "GET /products -> 200", "request_id": "b735af52f548", "status": 200, "duration_ms": 1.96}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:08:47.365Z (unstamped request, post-chaos)"
    quote: '{"ts": "2026-08-18T21:08:47.365Z", "message": "GET /orders -> 200", "request_id": "3f20fff1426d", "status": 200, "duration_ms": 1313.767}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:08:42.308Z (unstamped request, post-chaos)"
    quote: '{"ts": "2026-08-18T21:08:42.308Z", "message": "GET /products/2 -> 200", "request_id": "98caf7de2fc2", "status": 200, "duration_ms": 504.259}'
  - id: E5
    type: metric
    source: "GET /metrics probe @ 2026-08-18T21:09:08Z"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/orders"} 1.3137674171011895 / http_request_duration_seconds_count{method="GET",path="/orders"} 1'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:09:07.881Z (investigator probe, same window as E3/E4)"
    quote: '{"ts": "2026-08-18T21:09:07.881Z", "message": "GET /health -> 200", "request_id": "konan-1787087347-25500", "status": 200, "duration_ms": 0.591}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:12:32.575Z-21:12:32.593Z (live investigator reproduction)"
    quote: '{"ts": "2026-08-18T21:12:32.575Z", "level": "ERROR", "request_id": "konan-1787087551-25827", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"} then {"ts": "2026-08-18T21:12:32.593Z", "message": "GET /products/3 -> 500", "request_id": "konan-1787087551-25827", "status": 500, "duration_ms": 1332.201}'
  - id: E8
    type: metric
    source: "GET /metrics probe @ 2026-08-18T21:12Z (post live reproduction)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1'
  - id: E9
    type: log
    source: "lab/logs/app.log, full-log scan for event=unhandled_exception (9 occurrences, 2026-08-18T20:11:52Z-21:12:32Z)"
    quote: 'all 9 unhandled_exception lines carry a request_id prefixed "konan-"; earliest: {"ts": "2026-08-18T20:11:52.050Z", "message": "GET /products/3 -> 500", "request_id": "konan-1787083912-22619", "status": 500, "duration_ms": 7.675}'
  - id: E10
    type: log
    source: "lab/logs/app.log, full-log scan of unstamped GET /products/{id} traffic"
    quote: 'unstamped (non-"konan-") GET /products/{id} requests across the entire retained log only ever targeted ids 1, 2, and 5 - never 3 - and all returned status 200'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:01.558Z-20:22:05.794Z"
    quote: '{"ts": "2026-08-18T20:22:01.558Z", "event": "chaos_enabled", "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0} then {"ts": "2026-08-18T20:22:05.794Z", "message": "POST /orders -> 503", "request_id": "d40f49113600", "status": 503, "duration_ms": 0.283}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:07.911Z"
    quote: '{"ts": "2026-08-18T20:22:07.911Z", "level": "WARNING", "message": "chaos mode disabled", "request_id": "0d3ed61424da", "event": "chaos_disabled"}'
gaps:
  - "No telemetry (log or metric) anywhere in the retained window explains the complaint's 'seeing an error page once' clause for real users. Both tested candidate causes (H2, H3) were invalidated. Cannot rule out a client-side effect (e.g. a frontend timeout) triggered by the +1500ms latency injection (H1) that never surfaces as a server-side error status - the surface contract gives no visibility into client/browser behavior."
  - "The magnitude of observed post-chaos latencies (E3: 1313.767ms, E4: 504.259ms) does not cleanly match a fixed +1500ms addition over a ~2ms baseline, suggesting extra_latency_ms may be a randomized ceiling rather than a fixed add - the chaos implementation itself is outside the investigator's read-only surface (docs/lab.md excludes /chaos, /simulate/*, and source code), so this could not be confirmed."
  - "Log retention is rotating (app.log plus .1-.3 backups per docs/lab.md); only the currently retained window (back to ~20:07Z) was read. Any earlier activity that has already rotated out was not checked."
usage:
  model: claude-sonnet-5
  tokens: 3899024
  wall_clock_seconds: 431
---

# Shop-wide slowness from re-armed chaos latency injection; reported error page unexplained

## Summary

**Root cause identified.** The shop-wide slowness reported in the complaint is caused by
chaos latency injection (`extra_latency_ms=1500`, `failure_rate=0.0`) that was re-armed
at `2026-08-18T21:08:38Z` — 14 seconds before the complaint's timestamp. Real (non-investigator)
requests to `/products`, `/products/{id}`, `POST /orders`, and `GET /orders` jumped from a
sub-2ms baseline to 400ms-1.3s immediately after, while `/health` and `/metrics` stayed fast
throughout (E1-E6) — the classic healthy-monitoring-while-business-traffic-degrades shape.
Confidence: high; the judge validated H1 without qualification on the causal chain, flagging
only that the exact injected-latency magnitude doesn't cleanly match a fixed +1500ms add
(noted as a gap, not a defect in the finding).

The complaint's second clause — "some also mention seeing an error page once" — could **not**
be explained by any evidence on the observable surface. Two candidate causes were tested and
both invalidated: a genuine, 100%-reproducible `ZeroDivisionError` on `GET /products/3` (H2)
has never been triggered by real traffic, only by investigator probes across the entire
retained log; and an earlier high-failure-rate chaos episode (H3) fully resolved 46+ minutes
before the complaint with no unstamped errors in between. This is recorded as a gap, not
folded into the root cause.

## Timeline

- `20:07:20Z`-`20:22:07Z` — an earlier, higher-severity chaos episode (`failure_rate=0.6`,
  producing real unstamped 503s, E11) runs in three short bursts and is fully disabled by
  `20:22:07.911Z` (E12) — stale by the time of the complaint.
- `20:11Z`-`21:01Z` — investigator probes (this and prior sessions) repeatedly trigger the
  `GET /products/3` `ZeroDivisionError` (E9); no real traffic ever does.
- `21:08:32.336Z` — faultline process restarts cleanly (3rd restart in the retained window).
- `21:08:38.273Z` — chaos re-armed with `failure_rate=0.0, extra_latency_ms=1500` (E1).
- `21:08:40Z`-`21:08:47Z` — real shop traffic slows sharply: E2 (1.96ms) -> E4 (504ms) ->
  E3 (1313.767ms), corroborated independently by `/metrics` (E5); `/health` stays fast (E6).
- `21:08:52Z` — complaint reported ("startsAt").
- `21:12:32Z` — investigator live-reproduces the `/products/3` defect on demand (E7, E8) to
  confirm determinism; still never hit by real traffic.

## Investigation

Baseline: `/health` and `/metrics` probed clean and fast; process uptime showed a recent
restart (~35s old). Triage fanned out across all three available lenses (infra-process,
interfaces, software-defect) in parallel, each blind to the others, given the same baseline.
All three independently converged on the chaos re-arm as the slowness driver and flagged the
`/products/3` defect as investigator-only. No deep-dive round was needed — triage evidence was
already deterministic (log timestamps bracketing the chaos toggle, matching `/metrics` sums,
a full-log grep of every exception and every unstamped request to the affected route) — so
the three hypotheses went straight to the adversarial judge, which validated H1 and
invalidated H2 and H3 on the evidence as cited.

## Hypotheses

### H1 — Chaos latency injection (validated)
Re-armed at `21:08:38Z` immediately before the complaint; real traffic to shop routes went
from ~2ms to 400ms-1.3s (E2-E4), corroborated by `/metrics` (E5), while `/health` stayed fast
(E6) — a per-request injected-latency signature, not host-wide saturation. No evidence
against was found.

### H2 — ZeroDivisionError on /products/3 (invalidated)
Real defect, 100% reproducible (E7, E8), but every one of the 9 occurrences in the full
retained log carries an investigator (`konan-`) request id (E9), and real traffic has never
targeted product id 3 (E10). The cited evidence supports the opposite of the hypothesis: this
bug has not caused any user-visible error. Recorded separately as a latent finding.

### H3 — Stale high-failure-rate chaos episode (invalidated)
Did produce real 503s while active (E11), but was disabled at `20:22:07Z` (E12), 46+ minutes
before the complaint, with no unstamped errors in the gap.

## Safe next steps

- Re-probe `/metrics` (`faultline_chaos_enabled`) periodically to confirm whether/when the
  current chaos episode is disabled and whether shop-route latency returns to baseline.
- If the "error page" report recurs, capture the client-side detail (URL, browser network
  tab / HTTP status) at the time it happens — the server-side surface currently gives no way
  to distinguish a genuine 5xx from a client-side timeout under added latency.
- Continue treating `GET /products/3` as a known, reproducible latent defect for read-only
  monitoring; no remediation action is in scope for this journal.

## Gaps

- No telemetry (log or metric) anywhere in the retained window explains the complaint's
  "seeing an error page once" clause for real users. Both tested candidate causes (H2, H3)
  were invalidated. A client-side effect (e.g. a frontend timeout under the +1500ms
  injection) that never surfaces as a server-side error status cannot be ruled out — the
  surface contract gives no visibility into client/browser behavior.
- The magnitude of observed post-chaos latencies (1313.767ms, 504.259ms) doesn't cleanly
  match a fixed +1500ms addition over a ~2ms baseline, suggesting `extra_latency_ms` may be
  a randomized ceiling rather than a fixed add — the chaos implementation is outside the
  investigator's read-only surface, so this could not be confirmed.
- Log retention is rotating (`app.log` plus `.1`-`.3` backups); only the currently retained
  window (back to ~20:07Z) was read. Earlier activity that has already rotated out was not
  checked.
