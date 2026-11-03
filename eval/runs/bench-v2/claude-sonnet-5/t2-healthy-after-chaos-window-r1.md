---
konan_journal: 2
investigation:
  id: 2026-11-02-handover-chaos-toggle
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-02T21:54:28Z
  concluded: 2026-11-02T22:00:24Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation toggle in faultline was switched on for ~6.3 seconds, injecting 503s on /products and /orders at its configured 0.6 failure rate; it was switched off afterward and the service has run cleanly since."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos/degradation toggle in faultline was switched on for ~6.3 seconds (21:53:38.877Z-21:53:45.215Z) at a configured 0.6 failure rate, injecting 503s on /products and /orders; it was switched off afterward and the service has run cleanly since."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "The 503s were caused by an unhandled exception or code defect in faultline's own request-handling logic."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E4, E10, E11]
  - id: H3
    statement: "The 503s were caused by a gateway, proxy, or upstream-dependency boundary failure rather than an internal switch."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:53:38.877Z"
    quote: "{\"ts\": \"2026-11-02T21:53:38.877Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"4a26f54e15c9\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:53:39.935Z"
    quote: "{\"ts\": \"2026-11-02T21:53:39.935Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"16c349d47f78\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:53:43.109Z"
    quote: "{\"ts\": \"2026-11-02T21:53:43.109Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"e6f3de6fd83d\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:53:44.159Z"
    quote: "{\"ts\": \"2026-11-02T21:53:44.159Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"856fd487f53e\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:53:45.215Z"
    quote: "{\"ts\": \"2026-11-02T21:53:45.215Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"19448b8865c3\", \"event\": \"chaos_disabled\"}"
  - id: E6
    type: metric
    source: "/metrics probe, post-episode (request_id konan-1793656575-7536)"
    quote: "faultline_chaos_enabled 0"
  - id: E7
    type: metric
    source: "/metrics probe, post-episode (request_id konan-1793656575-7536)"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 2 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:54:09.501Z (last line in file)"
    quote: "{\"ts\": \"2026-11-02T21:54:09.501Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/5 -> 200\", \"request_id\": \"6f972353281f\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/5\", \"status\": 200, \"duration_ms\": 0.751, \"client\": \"127.0.0.1:61605\"}"
  - id: E9
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1793656572-7530"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":157.02595541696064} -- HTTP 200 in 0.004529s"
  - id: E10
    type: metric
    source: "/metrics probe, exceptions counter family, post-episode"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E11
    type: probe
    source: "software-defect triage lens probe, GET /products/999"
    quote: "{\"detail\":\"no such product: 999\"} (HTTP 404)"
gaps:
  - "E10 (the exception counter carrying zero samples) proves no exception reached that metric; it cannot by itself rule out a defect path that emits 503 without incrementing it. Source code is outside the investigator's reach, so H2's rejection rests on the app's own chaos_failure event tagging (E2-E4) rather than a source-level proof."
  - "H3 (gateway/boundary failure) was invalidated from E1 (an internal faultline.chaos logger event) and E7 (exact count-match leaving no unexplained 503s), not from an independent gateway/proxy access log — no such log was found or examined. docs/lab.md states the lab has no distributed topology, which was taken on the contract's word rather than independently probed."
  - "Only lab/logs/app.log was available (27-35 lines, single process lifetime since the one startup event at 21:53:35.003Z); no rotated backups (.1-.3) existed yet, so nothing before that startup could be examined."
  - "The chaos episode's configured failure_rate (0.6, from E1) was not independently cross-checked against total in-window request volume; 3 failures across 5 requests on the affected routes is consistent with it but is a small sample."
usage:
  model: claude-sonnet-5
  tokens: 3161057
  wall_clock_seconds: 356
---

# Shop service: brief chaos-toggle blip around handover, already resolved

## Summary

**No active incident right now.** There was a real but brief incident shortly before this
check: an internal chaos/degradation toggle in faultline was switched on for about 6.3
seconds and injected three 503 responses (two on `GET /products`, one on `POST /orders`)
before being switched off again (E1-E5, E7). The service has returned 200/201 on every
request since, and current `/health` and `/metrics` probes show a clean, continuously-running
process with zero unhandled exceptions and flat resource usage (E6, E8-E10). This matches
the handover report exactly: "some noise earlier" that nobody filed, because it was a short
self-resolving blip rather than a sustained failure. Root cause: an internal degradation
switch (infra-process / `degradation-switch`), not a code defect or an external/gateway
fault — both alternatives were tested and invalidated (H2, H3). Confidence: high: three
independent triage lenses converged on the same read of the same evidence, and an adversarial
judge pass validated H1 and invalidated H2/H3 on direct quotes.

## Timeline (UTC)

- `21:53:35.003Z` — faultline process starts (single startup event; no restart since).
- `21:53:38.877Z` — **E1**: chaos toggle enabled, `failure_rate=0.6`, `error_status=503`.
- `21:53:39.935Z` — **E2**: `GET /products` fails 503, tagged `chaos_failure`.
- `21:53:43.109Z` — **E3**: `POST /orders` fails 503, tagged `chaos_failure`.
- `21:53:44.159Z` — **E4**: `GET /products` fails 503, tagged `chaos_failure`.
- `21:53:45.215Z` — **E5**: chaos toggle disabled. Total elapsed: ~6.34s.
- `21:54:05Z`-`21:54:09.501Z` — normal traffic resumes cleanly: `GET /products` 200,
  `GET /products/1` 200, an order created and read back (201/200), `GET /products/5` 200
  (**E8**).
- `21:54:20Z` — human complaint raised ("noise earlier... nobody filed a report").
- `21:54:28Z` — investigation started (8s trigger latency from complaint to start).
- `21:56:xxZ` — fresh `/health` (**E9**) and `/metrics` (**E6**, **E7**, **E10**) probes
  confirm the service has stayed clean since the episode: `faultline_chaos_enabled 0`,
  3 total 503s ever recorded (all inside the window above, none since), zero unhandled
  exceptions.
- `22:00:24Z` — investigation concluded.

## Investigation

1. **Baseline**: read `lab/logs/app.log` and `lab/server.out` in full (both short, single
   process lifetime), then probed `/health` and `/metrics`. This immediately surfaced the
   chaos toggle episode and confirmed current state is clean.
2. **Triage (discipline-parallel, all three lenses)**: spawned infra-process, interfaces,
   and software-defect lenses in parallel, each blind to the others, given only the lens
   file, the surface contract, the complaint verbatim, and the baseline summary. All three
   independently found the same episode and none found an open anomaly in their own domain:
   - infra-process: classified the toggle as its domain's anomaly (internal operational
     switch), already resolved; no restart, no RSS growth, no latency drift.
   - interfaces: found the same episode, correctly deferred classification to infra-process
     per its own lens rule (internal switch, not a boundary/gateway fault), found no other
     gateway-shaped (502/504) anomalies.
   - software-defect: confirmed all three 503s are tagged `chaos_failure`, not
     `unhandled_exception`; zero exceptions ever recorded; live-probed `GET /products/999`
     (**E11**) and got a clean 404, arguing against a crash-prone code path.
3. **Deep-dive: skipped.** Per the skill, a hypothesis whose triage evidence is already
   deterministic and complete goes straight to the judge. The chaos toggle's start/stop
   markers, the exact match between the configured failure count and the metrics counter,
   and three independent lenses finding no competing anomaly left nothing a deep-dive probe
   would add.
4. **Judge** (adversarial, evidence-only, fresh agent, no lens reasoning given): validated
   H1, invalidated H2 and H3, each citing the same evidence ledger. The judge flagged two
   residual gaps (noted in machine core `gaps` and below) that temper confidence slightly
   but do not change any verdict.

## Hypotheses

### H1 — internal chaos/degradation toggle (validated)

Bracketed cleanly by E1 (enable) and E5 (disable), a ~6.34s window. E2-E4 are the three
503s inside that window, each self-tagged `chaos_failure` by the app's own instrumentation.
E7's metric count (2 on `/products`, 1 on `/orders` — 3 total, ever) matches E2-E4 exactly,
with none before or after. E6/E8/E9/E10 show a clean, continuous process since. The judge
validated this, noting multiple independent sources (logs, metrics, probes) triangulate
without contradiction.

### H2 — software defect (invalidated)

E2-E4 are the app's own declaration that these are deliberate chaos injections, not
exceptions; E10 shows zero unhandled exceptions recorded at any point; E11 shows clean
input validation on a probed edge case. The judge noted a residual gap: E10 only proves no
exception *reached* that metric, not that no defect path could emit 503 without touching it
— this can't be closed without reading faultline's source, which is outside the
investigator's surface. The explicit `chaos_failure` tagging is the stronger signal and is
why the verdict stands at invalidated rather than inconclusive.

### H3 — gateway / dependency boundary failure (invalidated)

E1 shows the switch lives inside faultline's own `faultline.chaos` logger, not a proxy or
gateway tier; E7 leaves no unexplained 503 for an external layer to account for. The judge
noted this doesn't positively prove no gateway/proxy exists in the topology — only that the
observed failures are fully explained by the internal switch. `docs/lab.md` independently
states this lab has no distributed topology, which is consistent but was not itself
re-verified by probing.

## Safe next steps

- No remediation needed — the episode is already resolved and was deliberate fault
  injection, not an organic defect.
- If "noise earlier" reports recur without a filed incident, consider whether chaos-toggle
  episodes should emit a visible marker to on-call (read-only observability improvement,
  not a code change to the target) so brief blips are not silently absorbed.
- Future handover checks could grep `lab/logs/app.log` for `chaos_enabled`/`chaos_disabled`
  pairs directly as a fast first pass, since this pair bracketed the entire episode here.

## Gaps

- Could not rule out, at the source-code level, a defect path that returns 503 without
  incrementing `http_exceptions_total`; relied on the app's own `chaos_failure` event
  tagging instead (software-defect domain is read-only/black-box here by design).
- Did not independently confirm the absence of a gateway/proxy tier via its own access
  logs; relied on E1's internal-logger attribution plus the surface contract's own
  statement that this lab has no distributed topology.
- Only the current `lab/logs/app.log` was available (single process lifetime since
  `21:53:35.003Z`); no rotated backups existed, so nothing before that startup could be
  examined.
- The configured `failure_rate=0.6` (E1) was not cross-checked against total in-window
  request volume beyond the 3-failures-of-5-requests sample visible in the log.
