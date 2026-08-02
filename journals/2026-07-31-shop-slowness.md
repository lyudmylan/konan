---
konan_journal: 1
investigation:
  id: 2026-07-31-shop-slowness
  trigger: manual
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-07-31T20:29:20+03:00"
  concluded: "2026-07-31T20:44:20+03:00"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode — faultline's runtime degradation switch — was enabled at 17:28:56Z via the operator-surface POST /chaos/enable in latency-only form (declared extra_latency_ms 1500, failure_rate 0.0) and was still enabled at last observation; it adds a variable per-request delay to business endpoints (observed 88–1301 ms server-side, every sample under the declared ceiling) while health and metrics stay unaffected — so every page is slow, nothing errors, and health checks stay green and fast."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A latency-only degradation switch (chaos mode, declared extra_latency_ms 1500 with failure_rate 0.0) enabled at 17:28:56Z via the operator-surface POST /chaos/enable adds a variable per-request delay to business endpoints while health and metrics stay unaffected; the same route and input flips from ~1 ms to ~1300 ms across the marker, investigator probes reproduce the delay, and every response stays 200/201."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "A defect in the application's own code — a slow query, lock contention, N+1 pattern, or exception-retry loop — causes the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E8, E9, E10]
  - id: H3
    statement: "Traffic load or resource exhaustion — CPU starvation, memory pressure, connection-pool saturation — causes the slowness."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E7, E9, E13, E14, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-07-31T17:28:48.138Z"
    quote: |-
      {"ts": "2026-07-31T17:28:48.138Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-07-31T17:28:56.064Z — the configuration-change marker; the only WARNING in the log"
    quote: |-
      {"ts": "2026-07-31T17:28:56.064Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "7afd9f11ec4e", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-07-31T17:28:56.064Z — same request_id as E2: this POST changed the config"
    quote: |-
      {"ts": "2026-07-31T17:28:56.064Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "7afd9f11ec4e", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.5, "client": "127.0.0.1:52140"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-07-31T17:28:53.026Z — last user request before the marker; all pre-marker user durations are 1.1–1.8 ms"
    quote: |-
      {"ts": "2026-07-31T17:28:53.026Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "0d922da1fce5", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.761, "client": "127.0.0.1:52139"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-07-31T17:28:59.361Z — first user request after the marker: ~700x slower, still 200"
    quote: |-
      {"ts": "2026-07-31T17:28:59.361Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "8b4716af3398", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1260.553, "client": "127.0.0.1:52141"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 17:28:51.991Z and 17:29:02.827Z — the same route and input, fast before the marker, slow after; both user traffic, both 200"
    quote: |-
      {"ts": "2026-07-31T17:28:51.991Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "e367fee263ee", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.167, "client": "127.0.0.1:52138"}
      {"ts": "2026-07-31T17:29:02.827Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c3c6e2734d7c", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1301.059, "client": "127.0.0.1:52145"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 17:29:00.489Z and 17:29:08.104Z — post-marker user durations vary 88–1301 ms (also 713.477 ms on POST /orders, 518.607 ms on GET /products), every one under the declared 1500 ms, none erroring"
    quote: |-
      {"ts": "2026-07-31T17:29:00.489Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "571329d307ad", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 88.099, "client": "127.0.0.1:52144"}
      {"ts": "2026-07-31T17:29:08.104Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "0ceef0ba1c68", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 920.787, "client": "127.0.0.1:52154"}
  - id: E8
    type: metric
    source: "probe /metrics, request_id=konan-1785519051-76430 @ ~2026-07-31T17:31:30Z — shop routes hundreds of ms mean while health/metrics stay milliseconds; means blend pre-marker fast samples, so per-request magnitudes live in E5–E7"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products"} 2.856
      http_request_duration_seconds_count{method="GET",path="/products"} 4
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 2.851
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 4
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.0110
      http_request_duration_seconds_count{method="GET",path="/health"} 3
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1785519051-76430 — no 4xx and no 5xx series exist anywhere; the declared error_status 503 never fired, matching failure_rate 0.0"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E10
    type: metric
    source: "probe /metrics, request_ids konan-1785518954-76367 @ 17:29:14Z and konan-1785519015-76397 @ ~17:30:15Z — zero sample lines at both reads; the log has zero exception/stack/ERROR lines"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E11
    type: metric
    source: "probe /metrics, request_id=konan-1785518954-76367 @ 17:29:14Z — still 1 at konan-1785519051-76430 (~17:31:30Z)"
    quote: |-
      faultline_chaos_enabled 1
  - id: E12
    type: probe
    source: "probe /products, request_id=konan-1785519018-76409 @ ~17:30:19Z — client-side trailer; the server-side log line for it reads duration_ms 1075.556"
    quote: |-
      HTTP 200 in 1.077380s (trailer) — the investigator's own probe drew ~1.1 s on a shop route with a clean, complete JSON body
  - id: E13
    type: probe
    source: "probe /health, request_id=konan-1785519008-76389 @ ~17:30:08Z — sub-3ms in the same window as E12's ~1.1 s shop probe; its uptime back-computes to E1's start, proving the same process serves both"
    quote: |-
      HTTP 200 in 0.002652s — {"status":"ok","uptime_seconds":79.99756262509618}
  - id: E14
    type: metric
    source: "probes konan-1785518954-76367 → konan-1785519017-76404 — monotonic, back-computing to the single ~17:28:48Z start; no reset"
    quote: |-
      process_uptime_seconds 89.66
  - id: E15
    type: metric
    source: "probes konan-1785518954-76367 → konan-1785519017-76404 — peak RSS flat (~47.7 MB, +144 KiB)"
    quote: |-
      process_max_rss_bytes 47661056
gaps:
  - "Actor and intent behind the switch are outside this surface: telemetry names the endpoint (POST /chaos/enable) and a localhost client, not an identity."
  - "The delay mechanism is characterized from ~9 post-marker samples: variance and the 1500 ms bound are observed; that it is a per-request random draw is inference. Likewise 'remains enabled' holds through the last observation (~17:31:30Z), not indefinitely."
  - "Health/metrics being unaffected is a behavioral observation; whether the mechanism deliberately exempts those paths is design intent not visible in telemetry."
  - "The decisive intervention — disable the switch and watch the same route return to ~1–2 ms — is a mutation and therefore outside konan's read-only boundary; until an operator runs it, the causal case is abductive (three independent fingerprints), not interventional."
  - "User-vs-investigator attribution rests on the request-id convention: all observed traffic originates from 127.0.0.1; unstamped ids are read as end-user or operator per the surface contract."
usage:
  model: claude-fable-5
  tokens: null
  wall_clock_seconds: 900
---

# Shop-wide slowness with zero errors — latency-only chaos mode left enabled

## Summary

Root cause identified. faultline's degradation switch was enabled at 17:28:56Z via
the operator-surface `POST /chaos/enable` in **latency-only** form — declared
`extra_latency_ms 1500`, `failure_rate 0.0` (E2, E3) — and was still on at last
observation (E11). Every business request after the marker succeeds but slowly:
the same route and input flips from 1.167 ms to 1301 ms across the marker (E6),
post-marker user durations vary 88–1301 ms server-side with every sample under the
declared ceiling (E5, E7), and konan's own probe drew ~1.1 s on a shop route while
health answered in under 3 ms in the same window (E12, E13). No errors exist
anywhere — no 4xx/5xx series, zero exceptions (E9, E10) — matching the declared
zero failure rate; health and metrics are unaffected, which is why dashboards
stayed green and fast. Code defects and load/saturation were checked and ruled out
(H2, H3). The causal case rests on three independent fingerprints: the
request-id-tied config marker, delays respecting the config-declared ceiling with
config-matching zero errors, and held-constant controls (same route, same input,
same process) — abductive but closed; the interventional proof (disable and watch
it recover) is an operator action (gap 4).

## Timeline

All times UTC, from telemetry.

- **17:28:48.138Z** — process start, faultline 0.1.0 (E1); no telemetry before it.
- **17:28:50–53Z** — healthy user traffic: all 200/201, durations 1.1–1.8 ms; last
  known-good at 17:28:53.026Z (E4).
- **17:28:56.064Z** — **configuration-change marker**: WARNING `chaos_enabled`,
  failure_rate 0.0, extra_latency_ms 1500 (E2), request-id-tied to
  `POST /chaos/enable` → 200 from a localhost client (E3).
- **17:28:59.361Z** — first post-marker user request: `GET /products` → 200 in
  1260.553 ms, ~700x the pre-marker norm (E5).
- **17:28:59–17:29:08Z** — every user request slow-but-successful, 88–1301 ms,
  reads and writes alike (E6, E7); zero errors.
- **17:29:14Z** — investigation baseline: gauge `faultline_chaos_enabled 1` (E11),
  duration summaries already skewed (E8), health fast.
- **17:30:08–25Z** — reproduction: konan's shop-route probes draw ~1.1 s and
  1.46 s (client-side; server-side 1075.556 ms — E12) while `/health` answers in
  2.7 ms (E13); process stable throughout (E14, E15).

## Investigation

Baseline showed a shape with no errors to chase: request counters 200/201-only,
empty exception counter, but duration summaries for shop routes hundreds of times
their pre-marker values — and the chaos gauge at 1 with the enable marker sitting
in the log tail three seconds before the first slow request.

Triage ran three lenses in parallel, blind to each other. Software-defect returned
a clean domain: no exceptions, no error envelopes, not input-correlated — the same
input fast then slow across a config marker while the code did not change (E6) —
and its own reproduce-probe drew a slow-but-complete response. Infra-process found
the latency step anchored to the marker and the health/shop contrast, with the
process itself stable (single start, flat RSS). Interfaces assembled the config
chain: marker tied by request id to the operator POST, latency-only semantics
(declared 503 never fired — E9 doubles as corroboration), scope covering business
routes for users and investigator alike while health/metrics stay fast.

Selection: **no deep-dives** — the marker, the ceiling-respecting delays, the
same-input flip, and the live reproduction close the chain; what remains unknown
(actor, the draw mechanism) is unfillable through this surface. All three
hypotheses went straight to the judge.

The judge (fresh context, cited evidence only) validated H1 and invalidated H2 and
H3, with refinements adopted here: "exempt" is a behavioral observation, not
cited design intent (gap 3); "jittered" is inference from ~9 samples (gap 2); the
1461 ms figure is a client-side trailer — server-side max is 1301 ms (E12 source
note); and the health-is-in-process link is provable from the ledger itself (E13's
uptime back-computes to E1's start), which is what makes the health-vs-shop
contrast refute CPU starvation. The judge named the decisive counterfactual —
disable and re-probe — an operator action (safe next steps).

Budget: one triage round (3 lenses), zero deep-dives of a permitted three, one
judge — concluded in round 1. Tokens: subagents alone consumed ~133k; the
orchestrator's share is not measurable in an interactive session, so the machine
core records `tokens: null`.

## Hypotheses

### H1 — latency-only degradation switch enabled (validated)

Temporal correlation upgraded to causation by three independent fingerprints:
**attribution** — the config event and the POST share a request id (E2, E3);
**parameter match** — every post-marker delay sits under the declared 1500 ms
ceiling (E5, E6, E7, E12) and zero errors appeared anywhere (E9), matching the
declared failure_rate 0.0 — generic slowness has no reason to respect a
config-declared ceiling or to be perfectly error-free; **controls** — same route
and input across the marker (E6), reproduction on investigator probes (E12), and
contemporaneous selectivity (shop ~1 s while health sub-3 ms from the same
process — E8, E13) with the enabled state persisting across the window (E11).

### H2 — application code defect (invalidated)

The same route and input went from 1.167 ms to 1301 ms across a config marker with
no deploy — behavior changed while code and input did not (E6). Degradation is
uniform across shop routes rather than concentrated where a bad query would live
(E8), nothing ever failed or retried (E9, E10), and request counts of 3–4 per
route leave nothing to contend over.

### H3 — load or resource saturation (invalidated)

Peak RSS flat at ~47.7 MB (E15), single stable process (E1, E14), delays jittered
and bounded by a declared ceiling rather than monotonically growing as queues
would (E7), trivial request counts with no shed-load signature (E9) — and the
same process answers `/health` in under 3 ms while shop routes run ~1 s in the
same window (E13), which no starvation mechanism can produce.

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Hand to the operators: disable chaos mode (`POST /chaos/disable`) and re-probe
  the E6 route — recovery to ~1–2 ms converts the causal case from abductive to
  interventionally proven (gap 4). Until then the degradation is live.
- Trace the change: who called `POST /chaos/enable` at 17:28:56Z (E3) — telemetry
  has the endpoint and a localhost client, not an identity (gap 1).
- Dashboard blind spot: neither health status nor error rate can see this incident
  class — it is latency-only and health-exempt. Put the `faultline_chaos_enabled`
  gauge and a shop-route duration percentile on the dashboard, and alert on
  `chaos_enabled` WARNING events.

## Gaps

The machine core lists five. In brief: the actor is unattributable read-only (1);
the jitter mechanism and "still enabled" are bounded inferences (2); exemption is
behavior, not documented intent (3); the interventional proof is a mutation and
therefore an operator action, not konan's (4); user attribution rests on the
request-id convention (5).
