---
konan_journal: 1
investigation:
  id: 2026-07-31-intermittent-errors
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: "2026-07-31T12:06:45+03:00"
  concluded: "2026-07-31T20:24:45+03:00"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode — faultline's runtime degradation switch — was enabled at 08:57:59Z through the operator-surface POST /chaos/enable (declared failure_rate 0.4, error_status 503, extra_latency_ms 0) and was never disabled; it injects per-request 503 failures across business endpoints while the health and metrics paths stay exempt, so users see intermittent errors while the health dashboard stays green."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime degradation switch (chaos mode) enabled at 08:57:59Z via the operator-surface POST /chaos/enable injects per-request 503s across business endpoints and remains enabled; all seven user 503s in the burst carry per-failure chaos_failure tags with matching request ids, successes interleave on the same routes because injection is per-request ('fails, then works on retry'), and the exempt health path explains the green dashboard."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E5, E6, E7, E8, E10, E11, E12, E13, E16]
    evidence_against: []
  - id: H2
    statement: "The 503s are produced by a defect in the application's own handler code — an exception or logic error."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E8, E9, E13]
  - id: H3
    statement: "Process instability or resource saturation — restart loop, memory pressure, overload — causes the intermittent 503s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E5, E6, E7, E14, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-07-31T08:57:49.352Z"
    quote: |-
      {"ts": "2026-07-31T08:57:49.352Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-07-31T08:57:59.351Z — the configuration-change marker"
    quote: |-
      {"ts": "2026-07-31T08:57:59.351Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "5d8568dc9bcf", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-07-31T08:57:59.352Z"
    quote: |-
      {"ts": "2026-07-31T08:57:59.352Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "5d8568dc9bcf", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.131, "client": "127.0.0.1:49401"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-07-31T08:57:56.324Z — last user request before the marker"
    quote: |-
      {"ts": "2026-07-31T08:57:56.324Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "99ca658d844a", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.978, "client": "127.0.0.1:49400"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-07-31T09:06:25.233Z — first failure after the marker; all seven user 503s carry a paired chaos_failure line with matching request_id"
    quote: |-
      {"ts": "2026-07-31T09:06:25.233Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e374a54e001d", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-07-31T09:06:25.233Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "e374a54e001d", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.479, "client": "127.0.0.1:49442"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 09:06:26.266Z and 09:06:32.493Z — same route, user traffic, success then failure within 7 seconds"
    quote: |-
      {"ts": "2026-07-31T09:06:26.266Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "65a97e995d7f", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.812, "client": "127.0.0.1:49445"}
      {"ts": "2026-07-31T09:06:32.493Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "bbdd376c5d91", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.264, "client": "127.0.0.1:49452"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 09:06:28.337Z and 09:06:31.458Z — the write path flipping success/failure per request"
    quote: |-
      {"ts": "2026-07-31T09:06:28.337Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "e37ff8851ad4", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.348, "client": "127.0.0.1:49447"}
      {"ts": "2026-07-31T09:06:31.458Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "856da2efd1fe", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.272, "client": "127.0.0.1:49451"}
  - id: E8
    type: metric
    source: "probe /metrics, request_id=konan-1785488890-70524 @ ~2026-07-31T09:08:10Z"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/4",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E9
    type: metric
    source: "probe /metrics, request_ids konan-1785488801-70469 @ 09:06:41Z and konan-1785518324-76120 @ ~17:18:45Z — zero sample lines at both reads; the log likewise has zero unhandled_exception/stack lines"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E10
    type: metric
    source: "probe /metrics, request_id=konan-1785488801-70469 @ 09:06:41Z — also 1 at konan-1785488890-70524 (~09:08:10Z) and konan-1785518324-76120 (~17:18:45Z)"
    quote: |-
      faultline_chaos_enabled 1
  - id: E11
    type: probe
    source: "probe /health, request_id=konan-1785488889-70519 @ ~2026-07-31T09:08:09Z — green while the chaos gauge reads 1"
    quote: |-
      HTTP 200 — {"status":"ok","uptime_seconds":612.469}
  - id: E12
    type: metric
    source: "probe /metrics, request_id=konan-1785488890-70524 — no non-200 /health series exists"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
  - id: E13
    type: probe
    source: "probe /products/1, request_id=konan-1785518330-76130 @ 2026-07-31T17:18:50Z — correlated log line is WARNING event=chaos_failure with the same request id"
    quote: |-
      HTTP 503 — {"error":"service temporarily degraded","request_id":"konan-1785518330-76130"}
  - id: E14
    type: metric
    source: "probes konan-1785488801-70469, konan-1785488881-70506, konan-1785488890-70529 — monotonic, back-computing to the single ~08:57:49Z start"
    quote: |-
      process_uptime_seconds 621.65
  - id: E15
    type: metric
    source: "probes konan-1785488801-70469 @ 09:06:41Z and konan-1785488890-70529 @ ~09:08:10Z — identical at both reads"
    quote: |-
      process_max_rss_bytes 46940160
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-07-31T09:06:34.570Z — the last failure in the burst"
    quote: |-
      {"ts": "2026-07-31T09:06:34.570Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 503", "request_id": "d75150f3910f", "event": "request", "method": "GET", "path": "/products/4", "status": 503, "duration_ms": 0.281, "client": "127.0.0.1:49455"}
gaps:
  - "Actor and intent behind the switch are outside this surface: telemetry names the endpoint (POST /chaos/enable) and a localhost client, not an identity; correlating with change management or shell history is not possible read-only."
  - "The declared failure_rate is 0.4; the observed user-traffic rate in the burst is 7 of 10 — a sample too small to verify the declared rate, and no business traffic ran between the flip (08:57:59Z) and the burst (09:06:25Z), so the flag's effect was unobservable during that gap."
  - "The health/metrics exemption is an empirical, path-scoped inference (health never failed in 4 lifetime requests while a konan probe on a business route was injected); no configuration document of the exemption's scope is visible in telemetry."
  - "wall_clock_seconds includes ~8.2 hours during which the investigating session was suspended between triage dispatch and completion (operator-side stall; the target and its flag state ran on — the gauge still read 1 at 17:18:45Z and the effect reproduced at 17:18:50Z). Active investigation time was ~12 minutes."
  - "User-vs-investigator attribution rests on the request-id convention: all observed traffic originates from 127.0.0.1; unstamped ids are read as end-user or operator per the surface contract."
usage:
  model: claude-fable-5
  tokens: null
  wall_clock_seconds: 29880
---

# Intermittent 503s across the shop — chaos degradation switch enabled and never turned off

## Summary

Root cause identified. faultline's runtime degradation switch — chaos mode — was
enabled at 08:57:59Z via the operator-surface `POST /chaos/enable` with declared
`failure_rate 0.4`, `error_status 503`, no added latency (E2, E3), and was never
disabled (E10: the gauge still reads 1 over eight hours later; E13: the effect still
reproduces). It injects failures **per request** across business endpoints: 7 of 10
user requests in the 09:06:25–35Z burst returned 503, every one tagged with a
matching-request-id `chaos_failure` event (E5), with clean 200/201s interleaved on
the very same routes (E6, E7) — exactly the complaint's "fails, then works on
retry". The health path is exempt (E11, E12), which is why the dashboard stayed
green while users failed — the healthy-monitoring trap, switched on deliberately.
Code defects and process instability were checked and ruled out (H2, H3: zero
exceptions ever, single process, flat memory, sub-millisecond fail-fast errors).

## Timeline

All times UTC, from telemetry.

- **08:57:49.352Z** — process start, faultline 0.1.0 (E1); no telemetry before it.
- **08:57:50–56Z** — healthy user traffic, 200/201s; last known-good at
  08:57:56.324Z (E4).
- **08:57:59.351Z** — **configuration-change marker**: WARNING `chaos_enabled`,
  failure_rate 0.4, error_status 503 (E2), via `POST /chaos/enable` → 200 from a
  localhost client (E3).
- **08:57:59–09:06:25Z** — no business traffic; the flag's effect is unobservable
  in this gap (gap 2).
- **09:06:25.233Z** — first injected failure: `GET /products` → 503, paired
  `chaos_failure` tag (E5).
- **09:06:25–35Z** — the burst: 7 of 10 user requests fail across six routes,
  read and write paths alike, successes interleaved on the same routes (E6, E7,
  E8, E16).
- **09:06:41Z** — investigation baseline: health green, uptime 531.9s, gauge
  `faultline_chaos_enabled 1` (E10).
- **~09:08Z** — lens sweep: 503 spread counters (E8), zero exception series (E9),
  process stable (E14, E15), health 200-only (E11, E12).
- **[~8.2h session suspension — gap 4]**
- **17:18:45–50Z** — flag still enabled (E10); konan probe on `/products/1` draws
  an injected 503 with the degradation envelope (E13) — the incident is still live.

## Investigation

Baseline showed the shape at first glance: 503s scattered across many business
routes with successes on the same routes, an **empty** exception counter — errors
without exceptions — health green, and `faultline_chaos_enabled 1` in the gauge
block. The log tail held the config-change marker nine minutes before the burst.

Triage ran three lenses in parallel, blind to each other. Interfaces assembled the
causal chain: the marker (E2/E3), per-failure `chaos_failure` attribution on all
seven user 503s (E5), same-route success/failure flips on reads and writes (E6,
E7), and the health exemption reconciling the green dashboard (E11, E12).
Software-defect returned a clean domain — zero exceptions ever, no stacks, no
data-dependent shape, spread not concentration — and reproduced one injected 503
read-only, drawing the degradation envelope with no exception fields (E13).
Infra-process returned a clean domain: single startup, monotonic uptime, flat peak
RSS, sub-millisecond fail-fast failures (E1, E14, E15).

Selection: **no deep-dives** — the evidence was deterministic and complete at
triage (the marker, the per-failure tags, and the reproduction close the chain;
what remains unknown — actor, empirical rate — is unfillable through this surface).
All three hypotheses went straight to the judge.

The judge (fresh context, cited evidence only) validated H1 and invalidated H2 and
H3, with refinements adopted here: 0.4 is the *declared* rate, empirically
unverified at this sample size (gap 2); the exemption is a path-scoped empirical
inference — its strongest evidence being that a konan probe was injected on a
business route while health never failed (gap 3); the burst's end bound needed its
own citation (E16, added); and the enable's actor is an endpoint, not an identity
(gap 1). The judge also named the decisive counterfactual — disable the flag,
observe the gauge drop and 503s cease — which is a mutation and therefore an
operator action, not konan's (safe next steps).

Budget: one triage round (3 lenses), zero deep-dives of a permitted three, one
judge — concluded in round 1. Tokens: subagents alone consumed ~138k; the
orchestrator's share is not measurable in an interactive session, so the machine
core records `tokens: null`.

## Hypotheses

### H1 — degradation switch enabled and left on (validated)

Every link independently evidenced: activation marker tied by request id to the
operator-surface POST (E2, E3); all seven user 503s carrying matching-request-id
`chaos_failure` tags (E5, E16) with the per-route counters summing to exactly seven
and 503 the only 5xx anywhere (E8); config-behavior agreement on two axes (status
503 as declared; sub-millisecond failures matching `extra_latency_ms 0`);
per-request injection shown by same-route flips on reads and writes (E6, E7);
persistence across 8+ hours (E10) with a live reproduction (E13); and the health
exemption (E11, E12) — where the strongest scope evidence is the contrast that a
konan probe *was* injected on a business route while health *never* failed:
path-scoped, not client-scoped.

### H2 — application code defect (invalidated)

`http_exceptions_total` has zero samples at reads bracketing the burst and 8.3
hours later, and the log has zero exception or stack lines (E9) — no exception
branch exists. The logic-error branch is excluded by positive attribution: every
503 is explicitly tagged as injected (E5), and the reproduced 503 returns a clean
degradation envelope with no exception fields (E13). Spread across six unrelated
read and write routes (E8) fits an injected shared status, not a handler defect.

### H3 — process instability or saturation (invalidated)

Single startup in a complete single-PID log (E1), uptime monotonic through the
window (E14), peak RSS byte-identical across reads (E15), failures returning in
under a millisecond (E5) — nothing queue-, timeout-, or pressure-shaped — and
clean responses served between failures seconds apart (E6, E7). Injection
attribution (E5) leaves this hypothesis nothing to explain.

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Hand to the operators: disable chaos mode via the operator surface
  (`POST /chaos/disable`) — the judge's decisive counterfactual: expect
  `faultline_chaos_enabled` to drop to 0 and injected 503s to cease. Until then
  the incident is live (E13).
- Trace the change: who called `POST /chaos/enable` at 08:57:59Z (E3) — telemetry
  has the endpoint and a localhost client, not an identity (gap 1); shell history
  or change records are the next surface.
- Dashboard blind spot: health alone cannot see this incident class (E11, E12) —
  put the `faultline_chaos_enabled` gauge and a non-200 business-route rate on the
  dashboard, and alert on `chaos_enabled`/`chaos_failure` WARNING events.

## Gaps

The machine core lists five. In brief: the actor behind the flip is unattributable
read-only (1); the declared 0.4 rate is unverified at 7-of-10 sample size, with an
unobservable gap between flip and first traffic (2); the health/metrics exemption
is empirical path-scoped inference (3); the wall clock includes an ~8.2-hour
session suspension — active investigation was ~12 minutes (4); user attribution
rests on the request-id convention (5).
