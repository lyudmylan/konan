---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-503-chaos-switch
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: "2026-08-18T17:13:11Z"
  concluded: "2026-08-18T17:18:10Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode — faultline's runtime fault-injection switch — was enabled via the operator-surface POST /chaos/enable (declared failure_rate 0.4, error_status 503) roughly 8 seconds before the first user-visible 503, and stayed enabled; it injects per-request 503s across business endpoints while the health path stays exempt, producing intermittent failures against a green dashboard."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime fault-injection switch (chaos mode) was enabled shortly before the complaint and injects per-request 503s across business routes at a configured rate; the health endpoint is exempt from the injected state, so the dashboard reads green while users fail."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7]
    evidence_against: []
  - id: H2
    statement: "The 503s are produced by a defect in the target's own code — an unhandled exception or a deterministic per-input logic error."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E7, E9]
  - id: H3
    statement: "Process instability or resource saturation — a restart, memory pressure, or overload — causes the intermittent failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E8]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:12:45.723Z — the only startup marker in the visible log"
    quote: |-
      {"ts": "2026-08-18T17:12:45.723Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:12:53.911Z — the configuration-change marker"
    quote: |-
      {"ts": "2026-08-18T17:12:53.911Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "e4e3fb173f4e", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
      {"ts": "2026-08-18T17:12:53.912Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "e4e3fb173f4e", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.211, "client": "127.0.0.1:65470"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:12:59.166Z — a business request succeeding after the marker"
    quote: |-
      {"ts": "2026-08-18T17:12:59.166Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "9b8ef82f8dbc", "event": "order_created", "order_id": 2, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-08-18T17:12:59.167Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "9b8ef82f8dbc", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.326, "client": "127.0.0.1:65475"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:13:02.356Z — same route as E3, ~3s later, tagged chaos_failure"
    quote: |-
      {"ts": "2026-08-18T17:13:02.356Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "88ce8327e11b", "event": "chaos_failure", "method": "POST", "path": "/orders"}
      {"ts": "2026-08-18T17:13:02.356Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "88ce8327e11b", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.31, "client": "127.0.0.1:65479"}
  - id: E5
    type: metric
    source: "probe /metrics, request_id=konan-1787073226-14801 @ 2026-08-18T17:13:46Z"
    quote: |-
      faultline_chaos_enabled 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E6
    type: probe
    source: "probe /health, request_id=konan-1787073222-14795 @ 2026-08-18T17:13:42Z — green while E5's chaos gauge reads 1 four seconds later"
    quote: |-
      HTTP 200 — {"status":"ok","uptime_seconds":56.3863339999225}
  - id: E7
    type: probe
    source: "reproduction probes on identical input GET /products/9999, request_ids konan-1787073321-14928 @ 2026-08-18T17:15:21Z and konan-1787073325-14934 @ 2026-08-18T17:15:25Z — same input, different outcome on immediate retry"
    quote: |-
      HTTP 503 — {"error":"service temporarily degraded","request_id":"konan-1787073321-14928"}
      HTTP 404 — {"detail":"no such product: 9999","request_id":"konan-1787073325-14934"}
  - id: E8
    type: metric
    source: "probes ~2026-08-18T17:13:46Z, ~17:14:55Z, and ~17:15:00Z — uptime monotonic, RSS flat across the window"
    quote: |-
      process_uptime_seconds 129.167 (then 135.017 shortly after)
      process_max_rss_bytes 47579136 (identical at both reads)
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1787073226-14801 @ 2026-08-18T17:13:46Z — no data row under the counter, i.e. zero exceptions of any type recorded; full lab/logs/app.log scan likewise has zero unhandled_exception/simulated_exception lines"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
gaps:
  - "Actor and intent behind the switch are outside this surface: telemetry names the endpoint (POST /chaos/enable) and a localhost client, not an identity — correlating with change management or shell history is not possible read-only."
  - "The declared failure_rate is 0.4; only two chaos-tagged failures were directly cited (E4, E7) against roughly a dozen post-onset successes in the visible window — too small a sample to verify the declared rate empirically, per the judge's review."
  - "Ground-truth scenario recipes and the defect catalog are deliberately outside investigator reach per the lab boundary (eval/, the faultline checkout) — this conclusion is argued from telemetry alone and was not cross-checked against ground truth."
  - "No rotated log backups (.1-.3) existed at conclusion (process uptime under 6 minutes throughout), so there is no pre-startup history to check; moot since only one process instance ran across the investigation."
usage:
  model: claude-sonnet-5
  tokens: 3094328
  wall_clock_seconds: 299
---

# Intermittent shop 503s — chaos fault-injection switch enabled minutes before the complaint

## Summary

Root cause identified. faultline's runtime fault-injection switch ("chaos mode")
was enabled at 17:12:53.911Z via the operator-surface `POST /chaos/enable`, declared
`failure_rate 0.4`, `error_status 503` (E2) — about 8 seconds before the first
user-visible 503 and roughly 17 seconds before the complaint's own `startsAt`. It
injects failures **per request** on business routes: the same `POST /orders` route
returned 201 at 17:12:59.166Z and 503 at 17:13:02.356Z, three seconds apart (E3, E4)
— exactly the complaint's "fails, then works on retry" shape. A read-only
reproduction on an identical input (`GET /products/9999`) flipped from 503 to 404 on
immediate retry (E7), confirming per-request randomness rather than a sticky code
defect. `/health` stayed green throughout (E6) even while `/metrics` showed
`faultline_chaos_enabled 1` (E5) — the health endpoint's contract doesn't surface
the flag, explaining the "dashboard is green" detail directly. Code defects and
process instability were checked and ruled out (H2, H3: zero exceptions anywhere,
a single continuous process, flat memory, monotonic uptime).

## Timeline

All times UTC, from telemetry.

- **17:12:45.723Z** — process start, faultline 0.1.0 (E1); no telemetry before it,
  and no further startup markers appear anywhere in the investigation.
- **17:12:46–17:12:53Z** — healthy traffic, 200/201s only.
- **17:12:53.911Z** — **configuration-change marker**: WARNING `chaos_enabled`,
  `failure_rate 0.4`, `error_status 503`, via `POST /chaos/enable` → 200 (E2).
- **17:12:59.166Z** — `POST /orders` succeeds (order_id=2, 201) — the switch does
  not fail every request (E3).
- **17:13:02.356Z** — same route, `POST /orders` fails with a paired
  `chaos_failure` tag (E4) — three seconds after the last success on that route.
- **17:13:11Z** — complaint `startsAt`; users are already seeing this pattern.
- **17:13:42–17:13:46Z** — investigation baseline: `/health` green (E6),
  `/metrics` shows `faultline_chaos_enabled 1` and the 201/503 split on
  `POST /orders` (E5), zero rows under `http_exceptions_total` (E9).
- **~17:14:55–17:15:00Z** — infra-process check: uptime monotonic, RSS flat (E8).
- **17:15:21Z / 17:15:25Z** — reproduction on `GET /products/9999`: 503, then 404
  on immediate retry — same input, different outcome (E7).

## Investigation

Baseline (a `/health` probe and a `/metrics` snapshot) already carried the shape of
the answer: `faultline_chaos_enabled 1` next to a green `/health`, and a log tail
showing a `chaos_enabled` WARNING with an explicit `failure_rate`/`error_status`
eight seconds before the first 503. That is the healthy-monitoring trap the skill
warns about — a green health check while a business path fails.

Triage ran three lenses in parallel, blind to each other, each given only the lens
file, the surface contract, the complaint, and this baseline. Interfaces assembled
the causal chain end to end: the config marker, the same-route success-then-failure
pair, and the health/metrics contract gap. Software-defect returned a clean
domain — zero exception log lines or counters — and, per its own method, reproduced
one request read-only to test determinism: the same input drew a 503 and then a 404
on immediate retry, ruling out a sticky per-input defect. Infra-process returned a
clean domain too: one startup marker, monotonic uptime, flat peak RSS, no
degradation trend in latency.

Selection: no deep-dive round was needed. The marker, the paired success/failure on
the same route, and the reproduction already closed the causal chain at triage —
what remained unresolved (actor identity, the empirical failure rate at this sample
size) is not fillable through more probing of this surface. All three hypotheses
(the chaos switch, a code defect, and process instability) went straight to a fresh
adversarial judge with only the cited evidence, no narrative.

The judge validated H1 and invalidated H2/H3, naming the causal-mechanism citation
(E2, self-reported by the target's own chaos logger) as strong log evidence, the
same-route mixed outcomes (E3/E4) and the retry-flip (E7) as directly supporting
"fails, then works on retry," and the health/metrics gap (E5/E6) as a clean
explanation for the green dashboard. It flagged one soft spot, carried into gaps:
the declared 0.4 rate is asserted, not verified against a full tally of the
post-onset window.

Budget: one triage round (3 lenses), zero of three permitted deep-dives, one judge
— concluded in round 1.

## Hypotheses

### H1 — chaos fault-injection switch enabled shortly before the complaint (validated)

The self-reported config-change marker (E2) precedes the first user-visible failure
by seconds; the same route alternates success and failure post-onset (E3, E4),
matching per-request probabilistic injection rather than a persistent defect; a
same-input reproduction flips outcome on retry (E7); and the health/metrics split
(E5, E6) explains why the dashboard read green. No evidence against.

### H2 — a code defect in the target's own handlers (invalidated)

Zero unhandled-exception log lines or counter entries anywhere in the investigation
(E9); the 503 in E4 carries a `chaos_failure` tag with no exception type or stack,
unlike a real handler exception; and the reproduction in E7 shows the *same* input
producing *different* outcomes on immediate retry, which a deterministic per-input
defect would not do.

### H3 — process instability or resource saturation (invalidated)

Exactly one startup marker across the whole investigation, no restart or crash
events (E1); process uptime read monotonically and peak RSS stayed identical across
probes taken roughly a minute apart (E8) — no saturation or restart-loop signature.

## Safe next steps

- Re-probe `/metrics` periodically (read-only) to watch `faultline_chaos_enabled`
  and the `POST /orders` status split — confirm whether the switch is disabled and,
  if so, when 503s stop.
- If dashboard coverage is meant to catch this class of incident, that is a
  monitoring-contract gap worth flagging to whoever owns the health dashboard: it
  does not currently surface `faultline_chaos_enabled`.
- Widening the sample (more read-only `/metrics` reads over time) would let a
  future investigation verify the declared 0.4 failure rate empirically rather than
  from two data points.
- Any actual toggle-off, restart, or config change is a mutation and out of scope
  for a read-only investigation — that is an operator action, not this journal's.

## Gaps

- Actor and intent behind the switch are outside this surface: telemetry names the
  endpoint (`POST /chaos/enable`) and a localhost client, not an identity —
  correlating with change management or shell history is not possible read-only.
- The declared `failure_rate` is 0.4; only two chaos-tagged failures were directly
  cited (E4, E7) against roughly a dozen post-onset successes in the visible
  window — too small a sample to verify the declared rate empirically, per the
  judge's review.
- Ground-truth scenario recipes and the defect catalog are deliberately outside
  investigator reach per the lab boundary (`eval/`, the faultline checkout) — this
  conclusion is argued from telemetry alone and was not cross-checked against
  ground truth.
- No rotated log backups (`.1`-`.3`) existed at conclusion (process uptime under 6
  minutes throughout), so there is no pre-startup history to check; moot since only
  one process instance ran across the investigation.
