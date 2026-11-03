---
konan_journal: 2
investigation:
  id: 2026-11-02-handover-chaos-recheck
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-02T22:03:52Z
  concluded: 2026-11-02T22:11:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation toggle in faultline was switched on for ~6.33 seconds, injecting 503s on GET /products, GET /products/1, GET /products/2, and POST /orders at its configured 0.6 failure rate; it was switched off afterward and the service has run cleanly since, with no active incident at the time of this handover check."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos/degradation toggle in faultline was switched on for ~6.33 seconds (22:03:07.725Z-22:03:14.056Z) at a configured 0.6 failure rate, injecting 503s on GET /products (x2), GET /products/1, GET /products/2, and POST /orders; it was switched off afterward and the service has run cleanly since."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "The 503s were produced by an unhandled exception or a code defect in faultline's own request-handling logic, not by a deliberate internal toggle."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E4, E5, E6, E14]
  - id: H3
    statement: "The 503s (or an associated slowdown) were caused by a process crash/restart loop or resource saturation rather than a deliberate chaos toggle."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E11, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:07.725Z"
    quote: "{\"ts\": \"2026-11-02T22:03:07.725Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"e4ec0eec719d\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:08.779Z"
    quote: "{\"ts\": \"2026-11-02T22:03:08.779Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"cef8dc53340d\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:09.834Z"
    quote: "{\"ts\": \"2026-11-02T22:03:09.834Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"f1685a47c802\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/2\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:10.889Z"
    quote: "{\"ts\": \"2026-11-02T22:03:10.889Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"801a7c84b8db\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:11.944Z"
    quote: "{\"ts\": \"2026-11-02T22:03:11.944Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"0de97744658f\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:12.999Z"
    quote: "{\"ts\": \"2026-11-02T22:03:12.999Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"b7b9b2e7c570\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:14.056Z"
    quote: "{\"ts\": \"2026-11-02T22:03:14.056Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"0cfab466f3fe\", \"event\": \"chaos_disabled\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:34.115Z"
    quote: "{\"ts\": \"2026-11-02T22:03:34.115Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"7006d1c524a8\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 0.717, \"client\": \"127.0.0.1:61675\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:36.231Z"
    quote: "{\"ts\": \"2026-11-02T22:03:36.231Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"40512b78b0ad\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.697, \"client\": \"127.0.0.1:61677\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:03:03.855Z (only startup event in the file)"
    quote: "{\"ts\": \"2026-11-02T22:03:03.855Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E11
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1793657064-7838"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":80.21025654184632} -- HTTP 200 in 0.002269s"
  - id: E12
    type: metric
    source: "/metrics probe, request_id konan-1793657068-7843"
    quote: "faultline_chaos_enabled 0"
  - id: E13
    type: metric
    source: "/metrics probe, request_id konan-1793657068-7843"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
  - id: E14
    type: metric
    source: "/metrics probe, exceptions counter family, request_id konan-1793657068-7843"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E15
    type: metric
    source: "/metrics probe, request_id konan-1793657068-7843"
    quote: "process_max_rss_bytes 46710784"
  - id: E16
    type: metric
    source: "/metrics probe, request_id konan-1793657068-7843"
    quote: "http_request_duration_seconds_sum{method=\"GET\",path=\"/products\"} 0.002339542144909501\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products\"} 4"
gaps:
  - "Cannot rule out, at source-code level, a defect path that returns 503 without incrementing http_exceptions_total; relied on faultline's own chaos_failure event tagging (E2-E6) instead, since source code is outside the investigator's read-only surface."
  - "Did not independently verify the absence of a gateway/proxy tier via its own access logs; relied on E1's internal faultline.chaos logger attribution and docs/lab.md's own statement that this lab has no distributed topology."
  - "Only the current lab/logs/app.log was available (31 lines, single process lifetime since the 22:03:03.855Z startup, E10); no rotated backups (.1-.3) existed yet, so nothing before that startup could be examined."
  - "The configured failure_rate=0.6 (E1) was not independently cross-checked against total in-window request volume beyond the 5-failures sample visible in the log; the true realized rate during the window is not separately verified."
usage:
  model: claude-sonnet-5
  tokens: 2585819
  wall_clock_seconds: 471
---

# Shop service: chaos-toggle blip around handover, already resolved

## Summary

**No active incident right now.** A real but brief incident happened shortly before this
check: an internal chaos/degradation toggle in faultline was switched on for about 6.33
seconds and injected five 503 responses (two on `GET /products`, one each on
`GET /products/1`, `GET /products/2`, and `POST /orders`) before being switched off again
(E1-E7). The service returned clean 200/201s on every request afterward, including a full
order-creation round trip (E8, E9), and the current `/health` and `/metrics` probes show a
continuously-running process (single startup event, no restart — E10, E11) with zero
unhandled exceptions and unremarkable resource/latency figures (E12-E16). This matches the
handover report exactly: "some noise earlier" that nobody filed, because it was a short,
self-resolving blip rather than a sustained failure. Root cause: an internal degradation
switch (`infra-process` / `degradation-switch`), not a code defect or a saturation/restart
problem — both alternatives were tested and invalidated (H2, H3). Confidence: high — three
independent triage lenses converged on the same read of the same evidence, and an
adversarial judge pass validated H1 and invalidated H2/H3 on direct quotes, with only minor
caveats that don't change any verdict.

## Timeline (UTC)

- `22:03:03.855Z` — **E10**: faultline process starts; the only startup event in the log —
  no restart since.
- `22:03:04.583Z`-`22:03:05.665Z` — clean 200s before the episode (`/health`, `/products`,
  `/products/1`).
- `22:03:07.725Z` — **E1**: chaos toggle enabled, `failure_rate=0.6`, `error_status=503`.
- `22:03:08.779Z`-`22:03:12.999Z` — **E2-E6**: five `chaos_failure`-tagged 503s across
  `GET /products` (x2), `GET /products/1`, `GET /products/2`, `POST /orders`.
- `22:03:14.056Z` — **E7**: chaos toggle disabled. Elapsed since E1: ~6.33s.
- `22:03:34.115Z`-`22:03:38.343Z` — normal traffic resumes cleanly: `GET /products` 200
  (**E8**), `GET /products/1` 200, an order created and read back 201/200 (**E9**),
  `GET /products/5` 200.
- `22:03:47Z` — human complaint raised: "Routine on-call handover check: anything wrong
  with the shop service right now? There was some noise earlier but nobody filed a
  report."
- `22:03:52Z` — investigation started (5s trigger latency from complaint to start).
- `22:04:24Z`-`22:04:28Z` — investigator's baseline probes: `/health` (**E11**) and
  `/metrics` (**E12**-**E16**) confirm the service has stayed clean since the episode:
  `faultline_chaos_enabled 0`, exactly 5 total 503s ever recorded (all inside the window
  above, none since), zero unhandled exceptions, flat RSS, sub-10ms latency sums.
- `22:11:43Z` — investigation concluded.

## Investigation

1. **Baseline**: read `lab/logs/app.log` in full (31 lines, single process lifetime), then
   probed `/health` and `/metrics`. This immediately surfaced the chaos-toggle episode and
   confirmed current state is clean.
2. **Triage (discipline-parallel, all three lenses)**: spawned infra-process, interfaces,
   and software-defect lenses in parallel, each blind to the others, given only the lens
   file, the surface contract, the complaint verbatim, and the baseline summary. All three
   independently found the same episode and none found an open anomaly in their own domain:
   - infra-process: classified the toggle as its own domain's anomaly (an internal
     operational switch), already resolved; no restart, no RSS growth, no latency drift,
     confirmed via its own repeat probes (uptime climbing monotonically, RSS unchanged).
   - interfaces: found the same episode, correctly deferred classification to infra-process
     per its own lens rule (an internal switch, not a boundary/gateway fault), found no
     other gateway-shaped (502/504) anomalies or config/flag markers besides the toggle
     itself.
   - software-defect: confirmed all five 503s are tagged `chaos_failure`, not
     `unhandled_exception`; zero exceptions or `simulated_exception` events ever recorded;
     noted the failures spread across four different route/method pairs rather than one
     input repeatedly failing, which argues against a data-dependent code defect.
3. **Deep-dive: skipped.** Per the skill, a hypothesis whose triage evidence is already
   deterministic and complete goes straight to the judge. The chaos toggle's start/stop
   markers, the exact match between the chaos-tagged failure count and the metrics
   counters, and three independent lenses finding no competing anomaly left nothing a
   deep-dive probe would add.
4. **Judge** (adversarial, evidence-only, fresh agent, no lens reasoning given): validated
   H1, invalidated H2 and H3, each against the same evidence ledger. The judge flagged
   minor caveats (noted below and in `gaps`) that temper confidence slightly but do not
   change any verdict.

## Hypotheses

### H1 — internal chaos/degradation toggle (validated)

Bracketed cleanly by E1 (enable) and E7 (disable), a ~6.33s window. E2-E6 are the five 503s
inside that window, each self-tagged `chaos_failure` by the app's own instrumentation.
E13's metric counts (2 on `/products`, 1 each on `/products/1`, `/products/2`, and
`/orders` — 5 total, ever) match E2-E6 exactly, with none before or after. E8-E9 and
E11-E16 show a clean, continuous process since. The judge validated this, noting that logs,
metrics, and probes triangulate without contradiction, and that the exact request-ID
pairing between each `chaos_failure` line and its matching 503 access line is direct
attribution, not inference.

### H2 — software defect (invalidated)

E2-E6 are the app's own declaration that these are deliberate chaos injections, not
exceptions; E14 shows zero unhandled exceptions recorded at any point. The judge noted a
residual gap: E14 only proves no exception *reached* that metric, not that no defect path
could emit 503 without touching it — this can't be closed without reading faultline's
source, which is outside the investigator's surface (recorded in `gaps`). The judge also
noted that the four-different-routes observation alone is weak evidence against a shared-
dependency defect, but combined with the explicit `chaos_failure` tagging (which already
names the cause of each failure at the moment it happened), the disconfirmation stands.

### H3 — crash/restart loop or resource saturation (invalidated)

E10 (the single `startup` event in the whole log) and E11 (current `/health` probe, healthy)
argue against a restart; repeat probes by the infra-process lens showed uptime increasing
monotonically with no reset. E15 (flat RSS) and E16 (sub-10ms latency sums, consistent
request counts including the 503s) argue against saturation — the failing requests
themselves were near-instant, not slow or queued, which is the opposite of a saturation
signature. The judge validated this invalidation, flagging only an unverified assumption
(whether the duration histogram includes failed requests) that, if wrong, would weaken but
not reverse the saturation argument; the restart-loop argument stands independently of that
assumption.

## Safe next steps

- No remediation needed — the episode is already resolved and was deliberate fault
  injection, not an organic defect.
- If "noise earlier" reports keep recurring without a filed incident, consider whether
  chaos-toggle episodes should emit a visible marker to on-call (a read-only observability
  improvement, not a change to the target) so brief blips are not silently absorbed.
- Future handover checks could grep `lab/logs/app.log` for `chaos_enabled`/`chaos_disabled`
  pairs directly as a fast first pass, since this pair bracketed the entire episode here.

## Gaps

- Could not rule out, at the source-code level, a defect path that returns 503 without
  incrementing `http_exceptions_total`; relied on the app's own `chaos_failure` event
  tagging instead (software-defect domain is read-only/black-box here by design).
- Did not independently confirm the absence of a gateway/proxy tier via its own access
  logs; relied on E1's internal-logger attribution plus the surface contract's own
  statement that this lab has no distributed topology.
- Only the current `lab/logs/app.log` was available (31 lines, single process lifetime
  since the `22:03:03.855Z` startup, E10); no rotated backups (`.1`-`.3`) existed yet, so
  nothing before that startup could be examined.
- The configured `failure_rate=0.6` (E1) was not independently cross-checked against total
  in-window request volume beyond the 5-failures sample visible in the log; the true
  realized rate during the window is not separately verified.
