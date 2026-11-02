---
konan_journal: 2
investigation:
  id: 2026-11-02-chaos-toggle-503s
  trigger: "manual (/konan adapter; complaint fingerprint human-1793645042, startsAt 2026-11-02T18:44:02Z, investigation start 2026-11-02T18:44:06Z — trigger latency 4s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: "2026-11-02T18:44:06Z"
  concluded: "2026-11-02T18:52:14Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos switch inside faultline was turned on via POST /chaos/enable at 2026-11-02T18:43:40.912Z (failure_rate 0.4, error_status 503); from that point, requests to the business routes (/products, /products/{id}, /orders) fail with HTTP 503 at a rate matching 0.4, interleaved with successes, while /health and /metrics are not subject to the injected failures — so the health dashboard stays green while users see intermittent errors that clear on retry."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "A degradation switch (chaos mode) was enabled inside the target at 2026-11-02T18:43:40.912Z (failure_rate 0.4, error_status 503, request_id 9a568e03f327); from that moment, business-route requests (/products, /products/{id}, /orders) fail with HTTP 503 at a rate matching the stamped 0.4 (4 of the 10 non-investigator requests after the toggle), interleaved with successes on the same routes, while /health and /metrics stay 200 throughout — explaining both the retry-clears symptom and the green health dashboard."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E10]
    evidence_against: []
  - id: H2
    statement: "The intermittent 503s are a software defect in the target's own code (an unhandled exception, or a deterministic per-input failure) rather than an injected toggle."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E8, E11]
  - id: H3
    statement: "The intermittent 503s stem from resource saturation under load (CPU, memory, or connection exhaustion) rather than an operational toggle."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:43:40.912Z — the toggle event itself"
    quote: |-
      {"ts": "2026-11-02T18:43:40.912Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "9a568e03f327", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:43:40.913Z — same request_id as E1, the access line for the toggle call itself; unstamped (not an investigator probe)"
    quote: |-
      {"ts": "2026-11-02T18:43:40.913Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "9a568e03f327", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.516, "client": "127.0.0.1:60254"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:43:44.029Z — first chaos-injected failure after the toggle, same request_id pairs the warning and the access line"
    quote: |-
      {"ts": "2026-11-02T18:43:44.029Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5df5ac05bf47", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-02T18:43:44.029Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "5df5ac05bf47", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.291, "client": "127.0.0.1:60256"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:43:51.430Z — a different business route hit the same way, confirming the failure is not route-specific"
    quote: |-
      {"ts": "2026-11-02T18:43:51.430Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ad06c075736f", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-02T18:43:51.430Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "ad06c075736f", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.257, "client": "127.0.0.1:60263"}
  - id: E5
    type: metric
    source: "probe /metrics, request_id=konan-1793645480-99978 @ 2026-11-02T18:51:20Z — closing scrape, ~7.5 min after the toggle; chaos still on"
    quote: |-
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 2
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      faultline_chaos_enabled 1
  - id: E6
    type: probe
    source: "probe /health, request_id=konan-1793645088-99772 @ 2026-11-02T18:44:48.853Z — investigator-stamped, after the toggle; every /health and /metrics line in the full log is status 200, none 503"
    quote: |-
      {"status":"ok","uptime_seconds":75.93188529205509}
      -- HTTP 200 in 0.001638s request_id=konan-1793645088-99772
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:43:32.932Z — the only startup event in the process's life; no second one appears before or after the toggle"
    quote: |-
      {"ts": "2026-11-02T18:43:32.932Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E8
    type: probe
    source: "probe /products/1, request_id=konan-1793645319-99926 @ 2026-11-02T18:48:39.900Z (software-defect lens) — the same route that 503'd twice earlier (E3) now succeeds, with chaos still enabled"
    quote: |-
      {"ts": "2026-11-02T18:48:39.900Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1793645319-99926", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.562, "client": "127.0.0.1:60298"}
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1793645093-99777 @ 2026-11-02T18:44:53Z vs. request_id=konan-1793645480-99978 @ 2026-11-02T18:51:20Z — same value ~6.5 minutes apart"
    quote: |-
      process_max_rss_bytes 47038464    # identical on both scrapes
  - id: E10
    type: log
    source: "lab/logs/app.log, the 10 non-investigator (unstamped) requests between 2026-11-02T18:43:42.971Z and 18:43:52.479Z — the entire post-toggle business-traffic window"
    quote: |-
      200 GET /products (18:43:42.971Z) · 503 GET /products/1 (18:43:44.029Z) · 200 GET /products/2 (18:43:45.086Z) ·
      201 POST /orders (18:43:46.143Z) · 200 GET /products (18:43:47.201Z) · 503 GET /products/5 (18:43:48.258Z) ·
      201 POST /orders (18:43:49.315Z) · 503 GET /products/1 (18:43:50.374Z) · 503 GET /orders (18:43:51.430Z) ·
      200 GET /products/4 (18:43:52.479Z)
      — 4 of 10 requests failed (0.4), matching the failure_rate stamped in E1 exactly.
  - id: E11
    type: metric
    source: "probe /metrics, request_id=konan-1793645093-99777 @ 2026-11-02T18:44:53Z and request_id=konan-1793645480-99978 @ 2026-11-02T18:51:20Z — both scrapes"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      (no series under either scrape — zero unhandled exceptions ever recorded)
gaps:
  - "Non-investigator (business) traffic was observed only in an 18.7s window (18:43:33.685Z–18:43:52.479Z, 14 requests); none occurred afterward through conclusion (~7.5 min later). Whether the incident is still generating live user impact at conclusion time rests on the toggle state, not on fresh user traffic: the chaos gauge still reads 1 at the closing scrape (E5), and a later investigator probe of the same route that had failed still returned a healthy 200 (E8), consistent with the stamped 0.4 rate still applying to any new request rather than the toggle having been silently turned back off."
  - "POST /chaos/enable (E1, E2) carries no actor or auth field in the log, so who or what issued that call is not visible from this surface — only that it happened and what parameters it set. Whether it was an intentional operator action, a scheduled drill, or an accident is outside the investigator's reach."
  - "The pre-toggle observation window was short: the process itself started only ~8s before the toggle (E7 at 18:43:32.932Z vs. E1 at 18:43:40.912Z), with 4 requests in between. 'Normal' here is inferred from that small sample, not from an extended steady-state baseline."
  - "/metrics labels successful business-route requests under the route template (e.g. /products/{product_id}) but labels chaos-injected failures under the literal path (e.g. /products/1, /products/5) — a labeling quirk of this build. It means the counters alone cannot cross-tabulate success/failure per literal route; the 4-of-10 empirical rate (E10) was reconstructed by walking the log, not read off one counter pair."
  - "User attribution rests entirely on the request-id convention: investigator probes carry the konan-* prefix, everything else is read as end-user or operator traffic. The surface has no other field distinguishing a real end user from the eval harness's own simulated-traffic generator."
usage:
  model: claude-sonnet-5
  tokens: 5902420
  wall_clock_seconds: 488
---

# Intermittent shop 503s — chaos toggle switched on mid-session

## Summary

Root cause identified. At 2026-11-02T18:43:40.912Z an internal degradation switch
(chaos mode) inside the faultline service was turned on via `POST /chaos/enable`
(E1, E2), stamped with `failure_rate 0.4` and `error_status 503`. From that instant,
requests to business routes — `/products`, `/products/{id}`, `/orders` — fail with
HTTP 503 at a rate matching 0.4 (4 of the 10 non-investigator requests observed after
the toggle, E10), interleaved with successes on the very same routes (E3, E4, E8),
which is exactly the "fails, then works again on retry" shape reported. `/health` and
`/metrics` are not subject to the injected failures — every line for either endpoint
in the whole log is HTTP 200 (E6) — which is exactly why the health dashboard stayed
green while users saw errors: this is the healthy-monitoring-trap shape, confirmed
rather than assumed. No unhandled exception exists anywhere in the process's life
(E11), the process never restarted (one startup marker, E7), and memory is flat
across the window (E9) — ruling out a code defect or resource exhaustion as the
mechanism. Confidence is high: all three independent lenses converged on the same
mechanism, and the judge's one open question (whether the observed failures actually
cluster near the declared 0.4 rate, or that was merely asserted) was closed with an
exact empirical match (E10).

## Timeline

All times UTC, from telemetry.

- **18:43:32.932Z** — process starts, faultline 0.1.0, the only startup event in this
  process's life (E7).
- **18:43:33.657–18:43:39Z** — four clean requests (health, products, products/1,
  an order) — the only pre-toggle sample.
- **18:43:40.912Z** — `POST /chaos/enable` turns chaos on: `failure_rate 0.4`,
  `error_status 503`, `extra_latency_ms 0` (E1, E2). Sharp onset, not gradual.
- **18:43:42.971Z–18:43:52.479Z** — 10 business requests, 4 fail with 503 (products/1
  ×2, products/5, orders), 6 succeed (products ×3, products/2, orders ×2 as POST 201,
  products/4) — 4/10 = 0.4, matching the toggle's own stamp (E3, E4, E10).
- **18:43:52.479Z** — last non-investigator request observed in the window (gap 1).
- **18:44:02Z** — complaint stamped (`startsAt`).
- **18:44:06Z** — investigation start (trigger latency 4s).
- **18:44:48Z–18:51:20Z** — investigator baseline, triage, judge, and confirmation
  probes: `/health` and `/metrics` consistently 200 (E6, E5, E11); RSS unchanged
  (E9); a re-probe of `/products/1` — the earlier-failing route — now succeeds (E8),
  confirming the failure is probabilistic, not sticky to that input.
- **18:52:14Z** — concluded.

## Investigation

Baseline (`/health`, `/metrics`, log tail) already showed `faultline_chaos_enabled 1`
and a handful of 503s on business routes — too specific a signal to treat the
complaint as fully unexplored, so the full discipline-parallel triage sweep still
ran, rather than jumping straight to a conclusion.

Three lenses ran in parallel, blind to each other, each given only its lens file,
the surface contract, the complaint verbatim, and the baseline summary:

- **infra-process** identified the chaos toggle itself as the mechanism (E1, E2),
  confirmed no restart or saturation (E7, and RSS/duration stats), and noted
  `/health`/`/metrics` are exempt from the injected failures.
- **interfaces** independently found the same config-change marker (E1, E2),
  classified the gateway-shaped probabilistic 503s as consistent with the stamped
  rate, and — per its own lens's classification rule — deferred the incident class
  to `infra-process` since the switch is internal, not an external dependency.
- **software-defect** found zero unhandled exceptions or stack traces anywhere
  (E11), confirmed the failures are 1:1 paired with `chaos_failure` log events (no
  503 without one, no `chaos_failure` without a matching 503), and reproduced
  non-determinism by re-probing `/products/1` to a 200 (E8) — ruling out a
  deterministic per-input defect.

All three lenses converged on one hypothesis with no competing explanation, and the
evidence was already deterministic (an explicit toggle log line, paired
failure/access lines, a stable RSS gauge, an empty exception counter) — per the
skill, that skips deep-dive and goes straight to the judge.

The judge validated the core causal claim (toggle → business-route 503s,
health/metrics unaffected, no restart, no exceptions, non-deterministic per input)
but flagged that the cited evidence at that point asserted the 0.4 failure rate from
the toggle's own log line without an independent count of successes and failures
over the same window — correlation of mechanism, not yet a confirmed rate. One more
targeted round closed it: walking the full log for the 10 non-investigator requests
after the toggle gave exactly 4 failures and 6 successes (E10) — an exact match to
the declared 0.4, with real sample size, not a restated assertion.

Budget used: one triage round (3 lenses), zero deep-dives (the evidence was already
deterministic and complete), one judge pass, one confirmation round to close the
judge's gap. Tokens: subagents reported their own token usage; the orchestrator's
share is not measurable in this interactive session, so the machine core records
`tokens: null`.

## Hypotheses

### H1 — degradation switch (chaos toggle) — validated

The toggle event (E1) and its access line (E2) are not mere correlation: the toggle
log line is the fault-injection code announcing itself, and every subsequent 503
(E3, E4) is paired, same request, with a `chaos_failure` warning from that same
code path — a mechanism, not a coincidence. The empirical rate (E10) matches the
declared parameter exactly. `/health` and `/metrics` are untouched throughout (E6),
which is the second half of the explanation the complaint needed: why the dashboard
read green. No evidence against.

### H2 — software defect — invalidated

A code-level defect would show an unhandled exception or a sticky per-input
failure. Neither exists: zero exceptions or stack traces anywhere in the process's
life (E11), every 503 is attributed to the chaos code path rather than an
application error (E3, E4), and the one route that failed twice (`/products/1`)
later succeeded with chaos still on (E8) — the opposite of a deterministic defect
signature.

### H3 — resource saturation — invalidated

Saturation would show growing memory, CPU burn, or slowing responses. RSS is
byte-for-byte identical across scrapes 6.5 minutes apart (E9), the process never
restarted (E7, single startup marker), and every request in the log — including the
503s — completes in under a millisecond. Nothing in the telemetry resembles
saturation.

## Safe next steps

- Watch `faultline_chaos_enabled` and the business-route 503 counters in `/metrics`
  (read-only) to see when the toggle clears; until then, any new business request
  carries roughly a 0.4 chance of a 503 that a retry should clear.
- Since `/health` does not reflect business-route health, treat a green health
  dashboard as insufficient evidence of "all clear" for this class of incident going
  forward — confirm against the business surface (`/products`, `/orders`) too.
- If an operator console or audit log outside this surface exists, check who or what
  issued `POST /chaos/enable` at 18:43:40.912Z (gap 2) to tell an intentional drill
  from an accidental toggle — that lookup is outside the investigator's reach here.

## Gaps

Five, in brief: business traffic was only observed in an 18.7s window and none since
(1), so live user impact at conclusion time is inferred from the toggle's own state,
not fresh user traffic; the actor behind the toggle call is not visible on this
surface (2); the pre-toggle baseline sample was very small, ~8s and 4 requests (3);
`/metrics` labels successes and chaos-injected failures under different path forms
for the same route, so the empirical rate had to be reconstructed from the log
rather than read off one counter (4); and user-vs-investigator attribution rests
entirely on the `konan-*` request-id convention, with no other field to distinguish
a real end user from the eval harness's own traffic generator (5).
