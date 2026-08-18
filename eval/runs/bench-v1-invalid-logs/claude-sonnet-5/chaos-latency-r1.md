---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-wide-latency-injection
  trigger: "manual (human via /konan; fingerprint human-1787074153)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-08-18T17:29:20Z
  concluded: 2026-08-18T17:37:15Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos-mode latency injection (extra_latency_ms=1500 used as a cap, failure_rate=0.0) was enabled at 17:28:58.692Z and added randomized delay, bounded at ~1.5s, to business-facing routes (/products, /products/{id}, /orders) while leaving /health and /metrics untouched, producing shop-wide slowness with zero errors."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "A runtime chaos-mode configuration change (chaos_enabled, extra_latency_ms=1500 as a cap, failure_rate=0.0) enabled at 17:28:58.692Z injected randomized/jittered added latency, bounded at 1500ms, into business routes (/products, /products/{id}, /orders), causing shop pages to load slowly with no errors, while /health and /metrics remained fast because they sit outside the affected route set."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E9, E10, E11, E12, E13, E14, E15]
    evidence_against: []
  - id: H2
    statement: "Process restarts around the same time caused the slowdown via resource churn or cold start, rather than the chaos config change."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E2, E6, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:28:58.692Z"
    quote: "{\"ts\": \"2026-08-18T17:28:58.692Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"84696288e9aa\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.0, \"error_status\": 503, \"extra_latency_ms\": 1500}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:28:53.515Z"
    quote: "{\"ts\": \"2026-08-18T17:28:53.515Z\", \"message\": \"GET /products -> 200\", \"request_id\": \"bb6bc8a7527d\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 1.731}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:29:01.514Z"
    quote: "{\"ts\": \"2026-08-18T17:29:01.514Z\", \"message\": \"GET /products -> 200\", \"request_id\": \"2b36f22838a6\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 763.235}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:29:03.879Z"
    quote: "{\"ts\": \"2026-08-18T17:29:03.879Z\", \"message\": \"GET /products/2 -> 200\", \"request_id\": \"ab031391ab12\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 200, \"duration_ms\": 1297.31}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:29:06.667Z"
    quote: "{\"ts\": \"2026-08-18T17:29:06.667Z\", \"message\": \"POST /orders -> 201\", \"request_id\": \"1926d88a0dd4\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 577.332}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:29:39.927Z"
    quote: "{\"ts\": \"2026-08-18T17:29:39.927Z\", \"message\": \"GET /health -> 200\", \"request_id\": \"konan-1787074179-15734\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/health\", \"status\": 200, \"duration_ms\": 0.57}"
  - id: E7
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787074179-15740 @ ~2026-08-18T17:29:39Z"
    quote: "faultline_chaos_enabled 1"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:28:52.752Z"
    quote: "{\"ts\": \"2026-08-18T17:28:52.752Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:29:39.978Z"
    quote: "{\"ts\": \"2026-08-18T17:29:39.978Z\", \"message\": \"GET /metrics -> 200\", \"request_id\": \"konan-1787074179-15740\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/metrics\", \"status\": 200, \"duration_ms\": 0.549}"
  - id: E10
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787074477-15943"
    quote: "-- HTTP 200 in 0.245920s request_id=konan-1787074477-15943"
  - id: E11
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787074478-15949"
    quote: "-- HTTP 200 in 0.498599s request_id=konan-1787074478-15949"
  - id: E12
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787074479-15955"
    quote: "-- HTTP 200 in 0.905592s request_id=konan-1787074479-15955"
  - id: E13
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787074479-15961"
    quote: "-- HTTP 200 in 0.362315s request_id=konan-1787074479-15961"
  - id: E14
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1787074480-15967"
    quote: "-- HTTP 200 in 0.395463s request_id=konan-1787074480-15967"
  - id: E15
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787074485-15975 @ ~2026-08-18T17:34:45Z"
    quote: "faultline_chaos_enabled 1 ; http_request_duration_seconds_sum{method=\"GET\",path=\"/metrics\"} 0.0010817907750606537 / _count 2 ; http_request_duration_seconds_sum{method=\"GET\",path=\"/health\"} 0.014343958115205169 / _count 3"
gaps:
  - "The faultline chaos-injection code path is outside the investigator's read-only surface (docs/lab.md scopes access to probes/logs/metrics only). The exact injection distribution (e.g. uniform 0-1500ms) is inferred from 8 sampled durations (E3, E4, E5, E10-E14), all within 0-1500ms with no clustering near a single fixed value — not confirmed from source."
  - "Who or what triggered POST /chaos/enable at 17:28:58.692Z is unknown — that endpoint is operator/eval surface, not probed by the investigator; only the resulting log line (E1) was observed."
  - "The three server restarts at 17:21:14, 17:28:10, and 17:28:52 UTC were not root-caused beyond their orderly shutdown/startup log lines; whether they originate from the lab harness or elsewhere is outside the investigator's surface. They were tested as H2 and invalidated as the cause of the reported slowness."
usage:
  model: claude-sonnet-5
  tokens: 2810613
  wall_clock_seconds: 475
---

# Shop-wide latency injection via chaos-mode config change

## Summary

**Root cause identified.** At 2026-08-18T17:28:58.692Z, a runtime chaos-mode configuration
change (`chaos_enabled`, `extra_latency_ms=1500` used as a cap, `failure_rate=0.0`) began
injecting randomized added latency — observed range ~246ms to ~1297ms, always below the
1500ms cap — into every business-facing route (`/products`, `/products/{id}`, `/orders`
GET and POST). Zero requests failed; every affected request still returned 200/201. `/health`
and `/metrics` stayed sub-millisecond throughout, because they sit outside the route set the
chaos middleware degrades. This matches the complaint exactly: pages painfully slow, nothing
errors out, health checks green and fast. Confidence is high — three independent triage
lenses converged on the same config-change marker, and a targeted 5-probe latency sample
confirmed the mechanism (jittered, capped delay) rather than a fixed add. A competing
hypothesis (recent process restarts causing the slowdown) was tested and invalidated: the
first business-route request after the last restart was fast, and the slowdown only began
6-9 seconds later, timed to the chaos-enable event, not the restart.

## Timeline (UTC)

- `17:28:52.752Z` — process restart completes cleanly (E8); no crash markers precede it.
- `17:28:53.515Z` — first post-restart `/products` request is fast, 1.731ms (E2).
- `17:28:58.692Z` — **`chaos_enabled` config-change marker**: `failure_rate=0.0`,
  `extra_latency_ms=1500` (E1). This is the onset event.
- `17:29:01.514Z` onward — business routes go slow with no errors: `/products` 763ms (E3),
  `/products/2` 1297ms (E4), `POST /orders` 577ms (E5).
- `17:29:13Z` — human complaint reported (trigger `startsAt`).
- `17:29:20Z` — investigation loop entered (7s trigger latency).
- `17:29:39Z` — `/health` and `/metrics` sampled mid-incident, both sub-millisecond (E6, E9);
  `/metrics` confirms `faultline_chaos_enabled 1` (E7).
- `~17:34:37Z-17:34:40Z` — 5 targeted `/products` probes during the still-active incident:
  246ms, 499ms, 906ms, 362ms, 395ms (E10-E14) — all under the 1500ms cap, no clustering near
  a single value, all 200s.
- `~17:34:45Z` — re-confirmed `faultline_chaos_enabled 1`; `/health`/`/metrics` still
  sub-millisecond after the slow probes (E15).

## Investigation

1. **Baseline**: `/health` (fast, 200), `/metrics` (chaos flag already reading 1), and the
   log tail showed the `chaos_enabled` marker with `extra_latency_ms=1500` directly in the
   recent window — strong initial signal.
2. **Triage — 3 lenses in parallel** (software-defect, infra-process, interfaces), each
   given only the lens file, the surface contract, the complaint, and the baseline:
   - software-defect: no unhandled exceptions, empty `http_exceptions_total`, latency spread
     across unrelated routes rather than concentrated — no code-defect signature.
   - infra-process: health/metrics stayed fast through the slow window (rules out
     whole-process saturation); three restarts found but all clean, and the last one
     completed 6s *before* the latency onset — flagged as a timeline distractor.
   - interfaces: identified the `chaos_enabled` marker directly as a config-change event
     immediately preceding a ~440x latency jump on business routes, with `/health` exempted.
   All three converged without contradiction.
3. Since the triage evidence for the config-change hypothesis was already a directly-quoted
   marker plus tight before/after timing, deep-dive was skipped per protocol and the
   hypothesis list went straight to an adversarial judge.
4. **Judge round 1**: H1 (as first stated, "fixed added latency of 1500ms") ruled
   *inconclusive* — the three cited post-marker durations (577-1297ms) didn't cluster near a
   flat 1500ms add. H2 (restart-caused) ruled *invalidated* on timing grounds.
5. **Targeted follow-up**: 5 additional `/products` probes while chaos was still active
   (E10-E14) showed durations spread across 246-906ms, all under the 1500ms cap — consistent
   with randomized/capped injection, not a fixed delay.
6. **Judge round 2** (fresh judge, revised H1 wording + new probe evidence): H1 *validated*,
   H2 *invalidated* — no contradicting evidence found in either the cited set or the judge's
   own independent log check.

## Hypotheses

### H1 — chaos-mode latency injection (validated)

A `chaos_enabled` config change at 17:28:58.692Z set `extra_latency_ms=1500` as an apparent
cap with `failure_rate=0.0`. Evidence for: the marker itself (E1), the sharp before/after
jump on `/products`, `/products/2`, and `POST /orders` (E2-E5), `/health`/`/metrics` staying
unaffected across the whole window (E6, E7, E9, E15), and 5 follow-up probes (E10-E14)
showing jittered durations under the 1500ms cap with no fixed clustering. No evidence against
was found by either the investigator or the judge's independent log check.

### H2 — process restart / resource churn (invalidated)

Three orderly restarts occurred in the preceding minutes, the last completing at
17:28:52.752Z (E8), close enough in time to look like a candidate cause. Invalidated because
the very first business-route request after that restart (17:28:53.515Z, E2) was fast
(1.731ms) — a cold-start theory predicts the opposite — and the slowdown only began 6-9s
later, timed to the chaos marker (E1), not the restart. `/health`/`/metrics` staying fast
throughout (E6, E9) further argues against a whole-process resource effect.

## Safe next steps

- Continue read-only monitoring of `/metrics` for `faultline_chaos_enabled` to know when the
  condition clears.
- No remediation performed or suggested here — chaos configuration is operator/eval surface,
  outside the investigator's read-only boundary (docs/lab.md).

## Gaps

- The chaos-injection code path is not on the investigator's surface, so the exact latency
  distribution (uniform 0-1500ms vs. some other shape) is inferred from 8 sampled durations,
  not confirmed from source.
- The origin of the `POST /chaos/enable` call at 17:28:58.692Z (who/what triggered it) is
  unknown — that endpoint is operator/eval surface, not probed.
- The three process restarts were tested as a competing hypothesis and invalidated, but their
  own root cause (lab harness activity vs. something else) was not investigated further, since
  it does not bear on the reported symptom.
