---
konan_journal: 2
investigation:
  id: 2026-11-02-chaos-latency-slowdown
  trigger: manual
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-02T19:10:04Z
  concluded: 2026-11-02T19:19:16Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation switch in faultline was enabled (failure_rate=0.0, extra_latency_ms=1500) at 19:09:42.635Z, injecting elevated latency onto the business routes /products, /products/{id}, and /orders while /health and /metrics stayed unaffected."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "The target's internal chaos/degradation switch was enabled (failure_rate=0.0, extra_latency_ms=1500) at 19:09:42.635Z, injecting elevated latency on the business routes /products, /products/{id}, and /orders, while /health and /metrics remained unaffected — producing the shop-wide slowdown the complaint describes, with no errors."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E18, E19, E20, E21, E22, E23, E24, E25]
    evidence_against: []
  - id: H2
    statement: "faultline's own code throws an unhandled exception or fails deterministically on specific inputs, producing the slowdown."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E26, E12]
  - id: H3
    statement: "An upstream/downstream dependency or gateway tier is failing or degrading intermittently (gateway-shaped 5xx, probabilistic failure), producing the slowdown."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E3, E8, E14]
  - id: H4
    statement: "Demand-driven resource exhaustion (CPU, memory, connections, or worker threads) degraded the service uniformly, producing the slowdown."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E27, E28, E29, E21, E22, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:42.635Z"
    quote: '{"ts": "2026-11-02T19:09:42.635Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "23bf5365a86d", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:37.484Z"
    quote: '{"ts": "2026-11-02T19:09:37.484Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "3b27f71b80ba", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.878, "client": "127.0.0.1:60408"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:46.092Z"
    quote: '{"ts": "2026-11-02T19:09:46.092Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "407414609c5d", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1398.778, "client": "127.0.0.1:60412"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:54.478Z"
    quote: '{"ts": "2026-11-02T19:09:54.478Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "c15716e6527a", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1249.721, "client": "127.0.0.1:60416"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:12:33.919Z"
    quote: '{"ts": "2026-11-02T19:12:33.919Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793646752-1102", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1170.518, "client": "127.0.0.1:60452"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:19.766Z"
    quote: '{"ts": "2026-11-02T19:15:19.766Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793646919-1225", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 278.781, "client": "127.0.0.1:60461"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:38.532Z"
    quote: '{"ts": "2026-11-02T19:09:38.532Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "d5523f0387c7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.99, "client": "127.0.0.1:60409"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:48.614Z"
    quote: '{"ts": "2026-11-02T19:09:48.614Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "97704a87a509", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1456.437, "client": "127.0.0.1:60413"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:50.837Z"
    quote: '{"ts": "2026-11-02T19:09:50.837Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "16aab0356109", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1159.544, "client": "127.0.0.1:60414"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:20.601Z"
    quote: '{"ts": "2026-11-02T19:15:20.601Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1793646919-1232", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 801.472, "client": "127.0.0.1:60462"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:22.964Z"
    quote: '{"ts": "2026-11-02T19:15:22.964Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1793646921-1241", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1198.928, "client": "127.0.0.1:60465"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:12:48.400Z"
    quote: '{"ts": "2026-11-02T19:12:48.400Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/99999 -> 404", "request_id": "konan-1793646767-1134", "event": "request", "method": "GET", "path": "/products/99999", "status": 404, "duration_ms": 838.169, "client": "127.0.0.1:60454"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:39.590Z"
    quote: '{"ts": "2026-11-02T19:09:39.590Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "c95649640910", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.729, "client": "127.0.0.1:60410"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:52.165Z"
    quote: '{"ts": "2026-11-02T19:09:52.165Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "fd3aeb7cf906", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 267.182, "client": "127.0.0.1:60415"}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:56.596Z"
    quote: '{"ts": "2026-11-02T19:09:56.596Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "34b52f4858d1", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1046.599, "client": "127.0.0.1:60417"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:21.732Z"
    quote: '{"ts": "2026-11-02T19:15:21.732Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1793646920-1238", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1075.122, "client": "127.0.0.1:60464"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:37.456Z"
    quote: '{"ts": "2026-11-02T19:09:37.456Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "2edd9dfe45ee", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 11.782, "client": "127.0.0.1:60406"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:37.483Z"
    quote: '{"ts": "2026-11-02T19:09:37.483Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "baef024b0efa", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 1.799, "client": "127.0.0.1:60407"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:10:43.240Z"
    quote: '{"ts": "2026-11-02T19:10:43.240Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793646643-1000", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 1.469, "client": "127.0.0.1:60436"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:12:32.734Z"
    quote: '{"ts": "2026-11-02T19:12:32.734Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793646752-1099", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.477, "client": "127.0.0.1:60451"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:19.474Z"
    quote: '{"ts": "2026-11-02T19:15:19.474Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793646919-1222", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.481, "client": "127.0.0.1:60460"}'
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:20.634Z"
    quote: '{"ts": "2026-11-02T19:15:20.634Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793646920-1235", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.782, "client": "127.0.0.1:60463"}'
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:15:22.997Z"
    quote: '{"ts": "2026-11-02T19:15:22.997Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793646922-1244", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.766, "client": "127.0.0.1:60466"}'
  - id: E24
    type: metric
    source: "/metrics @ 2026-11-02T19:10:45Z"
    quote: "faultline_chaos_enabled 1"
  - id: E25
    type: metric
    source: "/metrics @ 2026-11-02T19:18:58.656Z"
    quote: "faultline_chaos_enabled 1"
  - id: E26
    type: metric
    source: "/metrics @ 2026-11-02T19:10:45Z"
    quote: |
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E27
    type: metric
    source: "/metrics @ 2026-11-02T19:10:45Z"
    quote: "process_max_rss_bytes 47398912"
  - id: E28
    type: metric
    source: "/metrics @ 2026-11-02T19:18:58.656Z"
    quote: "process_max_rss_bytes 47398912"
  - id: E29
    type: metric
    source: "/metrics @ 2026-11-02T19:18:58.656Z"
    quote: "process_uptime_seconds 561.9552268341649"
  - id: E30
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:09:36.731Z"
    quote: '{"ts": "2026-11-02T19:09:36.731Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
gaps:
  - "The exact injection mechanism is not confirmed: post-chaos durations ranged 267ms–1456ms rather than a flat 1500ms, and no log field binds an applied delay value to a specific request id. Whether the mechanism is a fixed add, a capped random draw, or something else lives in faultline's own implementation (its SPEC/repo), which docs/lab.md deliberately keeps out of the investigator's reach."
  - "No CPU-utilization metric is exposed on this surface (only process_max_rss_bytes and process_uptime_seconds), so CPU-based load-saturation could not be measured directly. It was ruled out instead by indirect evidence: health probes taken tens of milliseconds from slow business-route probes (E21-E23) stayed sub-1ms, which a host-wide/process-wide saturation would not permit."
  - "The source of the POST /chaos/enable call that flipped the switch (request_id 23bf5365a86d) could not be attributed beyond its local client address (127.0.0.1) — the access log carries no auth/identity field, and /chaos itself is outside the investigator's probe allowlist (docs/lab.md), so who or what triggered it is unknown."
  - "Did not observe the switch being turned back off (no chaos_disabled marker appeared in the investigated window), so reversion behavior and the cutover's exact end time are unconfirmed."
usage:
  model: claude-sonnet-5
  tokens: 5501939
  wall_clock_seconds: 552
---

# Shop-wide latency spike traced to an internal chaos/degradation switch

## Summary

**Root cause identified.** An internal chaos/degradation switch inside faultline was
enabled at 19:09:42.635Z with `failure_rate=0.0` and `extra_latency_ms=1500` (E1),
injecting elevated latency — observed in the 267ms–1456ms range, two to three orders of
magnitude above the sub-2ms baseline — onto the business routes `/products`,
`/products/{id}`, and `/orders`, while `/health` and `/metrics` stayed at sub-2ms
throughout (E17-E25). This matches the complaint precisely: every shop page slow,
nothing erroring out, health checks green and fast. Confidence is high: the mechanism
is named directly in the trigger log line, the before/after contrast holds across more
than a dozen samples spanning roughly six minutes on all three affected routes, health
samples taken within tens of milliseconds of slow business-route samples rule out a
host-wide slowdown, and three alternative explanations (software defect, dependency/
gateway failure, resource exhaustion) were actively tested and invalidated (H2-H4). The
one open question is the exact injection mechanism behind the magnitude variance,
which sits outside this investigation's blinded surface (see Gaps).

## Timeline

- **19:09:36.731Z** — process startup, the only startup marker in the window; no
  restarts follow (E30).
- **19:09:37.456Z–19:09:39.590Z** — pre-chaos baseline: `/health` (E17, E18),
  `/products` (E2), `/products/1` (E7), and `POST /orders` (E13) all complete in under
  12ms.
- **19:09:42.635Z** — `chaos_enabled`: `enabled=true, failure_rate=0.0,
  error_status=503, extra_latency_ms=1500` (E1).
- **19:09:46.092Z onward** — business routes jump into the hundreds-to-~1.5s range:
  `/products` (E3, E4, E5, E6), `/products/{id}` (E8, E9, E10, E11), `/orders` (E14, E15,
  E16) — including a 404 on a nonexistent product id, itself delayed the same way
  (E12).
- **Throughout the same ~6-minute window** — `/health` (E19, E20, E21, E22, E23) and
  `/metrics` stay sub-2ms; `faultline_chaos_enabled` reads 1 at both the start and end of
  the window (E24, E25); no exception is ever logged (E26); `process_max_rss_bytes` is
  flat (E27, E28) and `process_uptime_seconds` climbs monotonically with no reset (E29).

## Investigation

0. **Complaint received** — manual trigger (`/konan`), complaint object:
   `source: human`, `fingerprint: human-1793646601`, `labels.alertname: human-report`,
   `annotations.summary`: "Users say every page in the shop got painfully slow in the
   last few minutes — nothing errors out, it just takes forever. Health checks are
   green and fast.", `startsAt: 2026-11-02T19:10:01Z`. Investigation loop entered at
   `2026-11-02T19:10:04Z` — trigger latency 3s.
1. **Baseline** — probed `/health` and `/metrics`, and read the log tail. The
   `chaos_enabled` marker (E1) and the `faultline_chaos_enabled=1` gauge were visible
   immediately.
2. **Triage** — fanned out three lenses (infra-process, interfaces, software-defect) in
   parallel against that same baseline, each blind to the others. All three
   independently converged on the chaos toggle; two ran their own confirming re-probes;
   neither alternative lens found an anomaly proper to its own domain.
3. **Deep-dive** — skipped: the triage evidence already named a deterministic
   mechanism, so the hypothesis went straight to the judge.
4. **Judge, round 1** — verdict **inconclusive**. It correctly flagged that the first
   evidence set was one before/after pair on a single route (`/products`), with only
   one `/health` sample taken a full minute after the switch flipped, and no coverage
   of `/products/{id}` or `/orders`.
5. **Targeted round-2 gathering** — ran interleaved probes across `/products`,
   `/products/{id}`, `/orders`, `/health`, and `/metrics` spanning roughly six minutes,
   including `/health` samples taken tens of milliseconds from slow business-route
   samples, and pulled the corresponding log lines (E2-E29).
6. **Judge, round 2** — verdict **validated**, with one noted soft spot: the magnitude
   variance (267ms-1456ms, never exactly 1500ms) is unexplained by any per-request
   instrumentation. Carried forward as a gap rather than left unstated.

## Hypotheses

### H1 — internal degradation switch (validated)

The chaos marker (E1) sits at the exact onset of the slowdown: every business-route
sample before it is sub-12ms (E2, E7, E13, E17, E18); every sample after it on
`/products`, `/products/{id}`, and `/orders` is elevated into the hundreds-to-~1.5s
range (E3-E6, E8-E12, E14-E16), sustained across a six-minute window and still present
at the end of the investigation (E25). `/health` and `/metrics` never deviate from
sub-2ms at any point in that same window (E17-E23), including samples taken seconds
away from slow business-route samples (E21-E23) — ruling out a shared, host-wide
slowdown in favor of a switch that selectively targets business routes.

### H2 — software defect (invalidated)

No exception type is ever incremented in `http_exceptions_total` (E26), and a
deliberately malformed request (`/products/99999`, a nonexistent id) returns a clean
`404` error envelope rather than a stack trace — and is delayed by the same mechanism
as valid requests (E12). That is the opposite of a data-dependent code defect, where
specific inputs would fail while others succeed; here, every input on an affected route
is slow and every input still succeeds.

### H3 — dependency/gateway failure (invalidated)

The chaos marker itself reports `failure_rate=0.0` (E1) — no probabilistic failure is
configured. Every sampled request after the marker returns `200` or `201` (E3, E8, E14,
and others); no `502`/`503`/`504` or other gateway-shaped status appears anywhere in the
window. There is no external party or boundary component in play — the toggle is
internal to the target.

### H4 — resource exhaustion / load-saturation (invalidated)

`process_max_rss_bytes` is identical (47398912) at the start and end of the investigated
window (E27, E28), and `process_uptime_seconds` increases monotonically with no reset
(E29) — no leak, no crash, no restart. Most directly: `/health` probes taken tens of
milliseconds away from slow business-route probes (E21-E23) stay sub-1ms, which a
genuinely saturated process (CPU, event loop, worker pool) would not permit, since it
would slow every request type indiscriminately.

## Safe next steps

- Keep sampling `/products`, `/products/{id}`, `/orders`, `/health`, and `/metrics` at a
  steady interval via `scripts/probe.sh` to track whether and when the switch is turned
  off and latency reverts to baseline.
- Watch `faultline_chaos_enabled` and `http_exceptions_total` on `/metrics` as the
  read-only signal for whether the degradation is still active.
- If authorized, correlate the `POST /chaos/enable` request (`request_id
  23bf5365a86d`) against any separate change-management or on-call record to determine
  who or what enabled it, and whether it was an intentional drill or accidental.

## Gaps

- The exact injection mechanism is not confirmed: post-chaos durations ranged
  267ms-1456ms rather than a flat 1500ms, and no log field binds an applied delay value
  to a specific request id. Whether the mechanism is a fixed add, a capped random draw,
  or something else lives in faultline's own implementation, which `docs/lab.md`
  deliberately keeps out of the investigator's reach.
- No CPU-utilization metric is exposed on this surface (only `process_max_rss_bytes` and
  `process_uptime_seconds`), so CPU-based load-saturation could not be measured
  directly; it was ruled out instead by the health-probe interleaving evidence
  (E21-E23).
- The source of the `POST /chaos/enable` call could not be attributed beyond its local
  client address (127.0.0.1); the access log carries no auth/identity field, and
  `/chaos` itself is outside the investigator's probe allowlist.
- The switch was never observed turning back off (no `chaos_disabled` marker in the
  investigated window), so reversion behavior and the exact end time of the incident
  are unconfirmed.
