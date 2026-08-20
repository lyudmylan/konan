---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-latency-injection
  trigger: "manual — /konan human profile; complaint object source=human, fingerprint=human-1787119075, labels.alertname=human-report, no severity stated, startsAt=2026-08-19T05:57:55Z; investigation entered 2026-08-19T05:58:04Z (trigger latency 9s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-08-19T05:58:04Z
  concluded: 2026-08-19T06:03:31Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change enabled chaos mode with latency injection (extra_latency_ms 1500, failure_rate 0.0) at 05:57:36.936Z, adding a per-request variable delay to the shop request paths while leaving /health and /metrics unaffected."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime configuration change enabled chaos mode with latency injection (extra_latency_ms 1500, failure_rate 0.0); the injected delay is the cause of the reported slowness, and the zero failure rate is why nothing errors out."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E14, E15, E16]
    evidence_against: []
  - id: H2
    statement: "A software defect in the shop request handlers is causing the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E4, E7, E8, E15]
  - id: H3
    statement: "Load saturation or resource exhaustion (memory pressure, restart loop, traffic surge) is causing the slowness."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E13, E14, E15]
  - id: H4
    statement: "The service is healthy and there is no active incident — the green, fast health check reflects true system state."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E6, E7, E9, E14]
latent_findings:
  - statement: "The /health and /metrics endpoints do not traverse the degraded path, so liveness monitoring stays green and fast through a full user-facing latency incident — any alerting gated on /health alone is blind to this failure shape."
    evidence: [E10, E11, E17, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:36.936Z"
    quote: '{"ts": "2026-08-19T05:57:36.936Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "2e5b44e545e3", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:31.794Z"
    quote: '{"ts": "2026-08-19T05:57:31.794Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "85f5dfd69dcd", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.327, "client": "127.0.0.1:56915"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:39.392Z"
    quote: '{"ts": "2026-08-19T05:57:39.392Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "748b9cb43895", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 403.197, "client": "127.0.0.1:56919"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:32.832Z"
    quote: '{"ts": "2026-08-19T05:57:32.832Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "80e552102e00", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.651, "client": "127.0.0.1:56916"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:43.022Z"
    quote: '{"ts": "2026-08-19T05:57:43.022Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "045369292b58", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 706.453, "client": "127.0.0.1:56922"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:45.420Z"
    quote: '{"ts": "2026-08-19T05:57:45.420Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "6fef98ba7e31", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1337.379, "client": "127.0.0.1:56923"}'
  - id: E7
    type: metric
    source: "/metrics @ 2026-08-19T06:03:22Z (probe konan-1787119402-46285)"
    quote: "faultline_chaos_enabled 1"
  - id: E8
    type: metric
    source: "/metrics @ 2026-08-19T06:03:22Z (probe konan-1787119402-46285)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      (no series follow the TYPE line; every http_requests_total series carries status="200" or status="201")
  - id: E9
    type: probe
    source: "/products/1 (request id konan-1787119122-45950)"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 1.323453s request_id=konan-1787119122-45950
  - id: E10
    type: probe
    source: "/health (request id konan-1787119093-45917)"
    quote: |-
      {"status":"ok","uptime_seconds":43.0389382080175}
      -- HTTP 200 in 0.002591s request_id=konan-1787119093-45917
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:58:13.848Z"
    quote: '{"ts": "2026-08-19T05:58:13.848Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787119093-45917", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.801, "client": "127.0.0.1:56947"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-19T05:57:30.821Z"
    quote: '{"ts": "2026-08-19T05:57:30.821Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E13
    type: metric
    source: "/metrics @ 05:58:14Z and @ 06:03:22Z (probes konan-1787119094-45923, konan-1787119402-46285)"
    quote: "process_uptime_seconds 43.33971137506887 -> process_uptime_seconds 351.9764865830075; process_max_rss_bytes 47808512 -> process_max_rss_bytes 47808512"
  - id: E14
    type: metric
    source: "/metrics @ 2026-08-19T06:03:22Z (probe konan-1787119402-46285)"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.015325624262914062
      http_request_duration_seconds_count{method="GET",path="/health"} 7
      http_request_duration_seconds_sum{method="GET",path="/metrics"} 0.0021137080620974302
      http_request_duration_seconds_count{method="GET",path="/metrics"} 4
      http_request_duration_seconds_sum{method="GET",path="/orders"} 1.5518337080720812
      http_request_duration_seconds_count{method="GET",path="/orders"} 3
      http_request_duration_seconds_sum{method="GET",path="/products"} 3.858768875710666
      http_request_duration_seconds_count{method="GET",path="/products"} 7
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 6.56808066717349
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 10
  - id: E15
    type: probe
    source: "/products/1 repeated, identical path (request ids konan-1787119122-45950, konan-1787119398-46263, konan-1787119402-46279)"
    quote: |-
      -- HTTP 200 in 1.323453s request_id=konan-1787119122-45950
      -- HTTP 200 in 0.835602s request_id=konan-1787119398-46263
      -- HTTP 200 in 0.335871s request_id=konan-1787119402-46279
  - id: E16
    type: metric
    source: "/metrics @ 2026-08-19T06:03:22Z (probe konan-1787119402-46285)"
    quote: 'http_requests_total{method="POST",path="/chaos/enable",status="200"} 1'
  - id: E17
    type: probe
    source: "/metrics and /health (request ids konan-1787119402-46285, konan-1787119399-46269)"
    quote: |-
      -- HTTP 200 in 0.001434s request_id=konan-1787119402-46285
      -- HTTP 200 in 0.001451s request_id=konan-1787119399-46269
gaps:
  - "No telemetry exists before 2026-08-19T05:57:30.821Z: the log holds exactly one startup marker (E12) and no rotated backups were present. The log window opens ~25s before the complaint was raised, so a slowdown that began earlier than the current process cannot be excluded from this evidence — only the degradation from 05:57:36.936Z onward is attributed."
  - "No actor attribution for the configuration change. The POST /chaos/enable line carries only client 127.0.0.1:56918; the surface contract exposes no audit identity, so telemetry cannot say whether the change was a deliberate drill or unintended."
  - "The injection's distribution is not established. Observed added delay ranges 0.34s-1.32s on one identical path (E15), consistent with a uniform 0-1500ms draw and equally consistent with probabilistic all-or-nothing injection; no per-request injection field is exposed."
  - "A smaller pre-existing latency regression would be masked by the injection. Only two pre-injection samples exist on the affected paths (E2, E4), too few to bound a residual defect."
  - "Host-level signals (CPU, load average, co-tenant contention) and any downstream dependency timings are outside the surface contract in docs/lab.md and were not checked."
  - "Only three triage lenses exist in this repo (infra-process, software-defect, interfaces). The load-saturation, third-party, and data-db domains were covered only by the orchestrator reading process and traffic metrics, not by a dedicated lens."
  - "User impact was assessed from the 6 non-investigator requests recorded after the marker (request ids 748b9cb43895, 7768ae904f2d, 045369292b58, 6fef98ba7e31, 9e1e26a873a4, 3f2597ae9353); no independent user-traffic source exists to size the true blast radius."
  - "One Bash command was denied by the boundary hook during this investigation: a log-counting pipeline whose grep pattern contained a /chaos/... path string, which the hook matches on content. Per the lab boundary a denial is a stop signal, so no reworded variant was attempted; the same count was obtained through the contract-sanctioned path (reading lab/logs/app.log directly)."
usage:
  model: claude-opus-5
  tokens: 2017503
  wall_clock_seconds: 327
---

# Shop-wide latency from a chaos-mode latency injection

## Summary

**Root cause identified.** At 05:57:36.936Z a runtime configuration change enabled
faultline's chaos mode with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E1). The
injection adds a per-request variable delay to the shop request paths, and the zero
failure rate means no request is ever failed — which is exactly why the reported symptom
is "painfully slow" with "nothing errors out". `/health` and `/metrics` do not traverse
the injected path and stayed at sub-5ms throughout (E10, E11, E17), so the green health
check is a false negative rather than a contradiction to explain.

The condition was still active at conclusion: `faultline_chaos_enabled 1` (E7), and a
first-party probe of `/products/1` took 0.335871s against a pre-injection baseline of
0.651ms on the same path (E4, E15). Impact is latency-only across every shop route —
mean 551ms for `/products`, 657ms for `/products/{product_id}`, 517ms for `/orders`
(E14) — against 2.2ms mean for `/health`. Confidence is high: the mechanism is declared
by the target itself, the trigger is counted (E16), the state is still set (E7), and the
`failure_rate: 0.0` parameter makes an independent prediction (zero errors) that the
telemetry confirms (E8).

Read this as an incident whose *cause* is settled but whose *legitimacy* is not: telemetry
records the config change without an actor, so whether this was a deliberate drill is
outside what the evidence can say.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 05:57:30.821 | faultline 0.1.0 starts — the only startup marker in the log; no telemetry exists before this point | E12 |
| 05:57:31.794 | `GET /products` -> 200 in **1.327ms** — healthy baseline | E2 |
| 05:57:32.832 | `GET /products/1` -> 200 in **0.651ms** — healthy baseline | E4 |
| **05:57:36.936** | **Configuration change marker: chaos mode enabled, `failure_rate: 0.0`, `extra_latency_ms: 1500`** | E1, E16 |
| 05:57:39.392 | `GET /products` -> 200 in **403.197ms** — first known-bad, 2.5s after the marker | E3 |
| 05:57:43.022 | `GET /products/1` -> 200 in **706.453ms** — same path as E4, ~1085x slower | E5 |
| 05:57:45.420 | `POST /orders` -> **201** in **1337.379ms** — checkout succeeds, slowly | E6 |
| 05:57:55 | Complaint raised by a human reporter | — |
| 05:58:04 | Investigation starts | — |
| 05:58:13.848 | `GET /health` -> 200 in **0.801ms** deep inside the slow window | E11 |
| 06:03:22 | Chaos still enabled; shop paths still slow, `/metrics` still 1.4ms | E7, E15, E17 |

## Investigation

**Baseline** — `/health` 200 in 2.6ms, a `/metrics` scrape, and the 22-line log tail. The
baseline itself carried two signals: `faultline_chaos_enabled 1` and a `POST /chaos/enable`
counter, alongside zero exception series and zero non-2xx statuses.

**Triage** — three lenses in parallel, each blind to the others: infra-process,
software-defect, interfaces. All three independently landed on the same 05:57:36.936Z
marker, and all three independently flagged the `/health` exemption as a monitoring blind
spot rather than a second fault. Software-defect returned an explicit "no defect signature
in my domain": no exception classes, no stack traces, and slowness independent of input
(`/products/2` degraded equally with `/products/1`).

**Deep-dive: skipped by design.** The triage evidence was already deterministic — the
target declares the mechanism and its parameter in its own log — so per the loop's rule,
deep-dives exist to fill evidence gaps, not to re-prove a settled one. Budget went to the
judge instead.

**Judge** — validated H1 and invalidated H2/H3/H4, with three corrections that changed the
write-up: it refused the `/metrics` exemption claim as uncited, refused "every request is
delayed" (a 2.8ms response existed on the injected path), and flagged that a lens had
mis-transcribed a probe duration. It also noted that pure temporal correlation would not
carry H1 on its own — two pre-change samples cannot establish a step change — and that the
claim rests instead on the declared mechanism, the counted trigger, the persistent state,
and the confirmed zero-error prediction.

**Post-judge gathering** — I re-established the disputed points with my own probes rather
than lens-reported figures: `/products/1` repeated three times (E15) and `/metrics`
timing (E17). Both corrections now stand on first-party quotes. The mis-transcribed value
was dropped from the ledger.

## Hypotheses

### H1 — chaos-mode latency injection (**validated**)

The target announces the cause in its own log: `event: chaos_enabled` with the injected
parameter and its size (E1). Four independent legs carry it beyond correlation — the
declared mechanism (E1); a counted trigger of exactly 1, matching one state transition
(E16); state still set at conclusion (E7); and a *collateral prediction* — `failure_rate:
0.0` predicts zero injected errors, and E8 confirms no exception series and only 200/201
statuses. Every observed slow response sits under the configured 1500ms ceiling (E5, E6,
E15).

The strongest discriminator against rival explanations is E11: `/health` served in 0.801ms
*inside* the slow window. A host-level stall or event-loop block would have slowed
`/health` too. It did not.

Two things the evidence does **not** support, and which are deliberately not claimed: that
every request is delayed (E15 shows 0.335871s on the same path where another took
1.323453s — the delay is per-request variable, not universal), and any specific
distribution for the draw.

### H2 — software defect in the shop handlers (**invalidated**)

No exception signature anywhere on the surface (E8), and the slowness is a time boundary
rather than an input shape: `/products/1` is 0.651ms before the marker and 706.453ms after
with identical input (E4, E5). A sufficient alternative mechanism is declared and confirmed
active (E1, E7). Note the honest limit, which the judge pressed and I accept: this
invalidates a defect as *the cause of the observed slowness*, not the existence of any
defect — hundreds of ms of injected delay would mask a smaller regression, and n=2 pre-injection
samples cannot exclude one. That limit is recorded under Gaps.

### H3 — load saturation / resource exhaustion (**invalidated**)

Exactly one startup marker in the whole log (E12); uptime climbs monotonically 43.3 -> 352.0
with no reset and peak RSS byte-identical across scrapes (E13); total traffic is 34 requests
across all paths (E14) — no surge. A 0.335871s response on the injected path (E15) is by
itself hard to reconcile with saturation. One precision the judge added: `process_max_rss_bytes`
is a high-water gauge, so identical values prove the peak did not rise, not that current
memory is flat. The verdict rests on the other legs.

### H4 — no active incident (**invalidated**)

Worth stating explicitly because it is the complaint's own framing turned into a hypothesis,
and because "no incident" is a legitimate verdict in this loop. It fails here. The absence of
errors has **no** discriminating power: `failure_rate: 0.0` predicts zero errors *while the
fault is active*, so E8 is equally consistent with a fault and with health. What settles it is
two first-party probes seconds apart against the same process: `/health` 200 in 0.002591s (E10)
versus `/products/1` 200 in 1.323453s (E9) — a ~500x gap on the same healthy service. The health
check measures the exempt path and nothing else.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal and for konan.

1. **Establish who made the change.** `POST /chaos/enable` is recorded once (E16) with only a
   localhost client. Confirm with whoever operates the target whether a drill or test was running
   at 05:57:36Z — this decides whether the incident is expected, and telemetry cannot answer it.
2. **Confirm recovery from the business surface, not the health check.** After the flag is
   cleared, verify `faultline_chaos_enabled 0` *and* re-measure `/products/{id}` latency against
   the pre-injection baseline of 0.651ms (E4). Green `/health` will not show recovery any more
   than it showed the fault.
3. **Close the monitoring blind spot** (latent finding). Alerting keyed on `/health` alone stays
   green through a total user-facing latency incident. A user-path SLO alert off
   `http_request_duration_seconds_sum`/`_count` per route would have caught this within seconds
   of 05:57:39.392Z (E3).
4. **Re-baseline after recovery.** Only two pre-injection samples exist (E2, E4). A clean
   latency baseline on the shop routes would let a future investigation detect a masked
   regression instead of recording it as a gap.

## Gaps

- **No telemetry before 05:57:30.821Z.** One startup marker (E12), no rotated backups. The log
  window opens ~25s before the complaint, so an earlier onset cannot be excluded — the complaint
  said "the last few minutes", and only the degradation from 05:57:36.936Z is attributed.
- **No actor attribution** for the config change beyond client 127.0.0.1:56918; the surface has
  no audit identity, so drill-versus-accident is unanswerable from telemetry.
- **Injection distribution unestablished** — E15's spread fits uniform 0–1500ms and
  all-or-nothing injection equally.
- **A masked residual regression cannot be excluded** — n=2 pre-injection samples.
- **Host-level and downstream signals** (CPU, load, co-tenant contention, dependency timings) are
  outside `docs/lab.md` and were not checked.
- **Three lenses exist, not six.** load-saturation, third-party, and data-db had no dedicated
  lens; those domains were covered only by the orchestrator reading process and traffic metrics.
  An accepted blind spot, recorded rather than papered over.
- **Blast radius is a floor, not a measure** — 6 non-investigator requests after the marker
  (748b9cb43895, 7768ae904f2d, 045369292b58, 6fef98ba7e31, 9e1e26a873a4, 3f2597ae9353) is all the
  user traffic this surface records. Every one of them was slow; none of them failed.
- **One boundary denial, not worked around.** A log-counting Bash pipeline was denied because its
  grep pattern contained a `/chaos/…` path string — the hook reads command text whole. Per the lab
  boundary a denial is a signal to stop, never a puzzle to solve, so no reworded variant was tried;
  the count was obtained by reading `lab/logs/app.log` directly, which is item 2 of the
  investigator surface.
