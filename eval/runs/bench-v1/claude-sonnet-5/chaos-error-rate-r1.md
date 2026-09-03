---
konan_journal: 1
investigation:
  id: 2026-08-18-chaos-mode-enabled
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-18T22:18:49Z
  concluded: 2026-08-18T22:23:19Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime config flip (POST /chaos/enable at 22:18:25.506Z) turned on a 40% injected-503 failure mode on business routes; /health is unaffected by it, so the dashboard stays green while orders and product lookups intermittently fail."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "An operator/runtime action enabled chaos mode (POST /chaos/enable) at 22:18:25.506Z, configuring a 40% injected 503 failure rate on business routes (/orders, /products/{id}); this explains the sudden intermittent order/page-load failures while /health remains unaffected and green."
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E13]
    evidence_against: []
  - id: H2
    statement: "Process lifecycle instability (restart/crash) or resource saturation (memory/CPU) caused the intermittent failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E14, E15]
  - id: H3
    statement: "An unhandled exception or data-dependent code defect in a specific route/input caused the intermittent failures."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E6, E7, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:17.312Z"
    quote: "{\"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:22.442Z"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 200, \"duration_ms\": 0.817}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:25.506Z"
    quote: "{\"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:25.507Z (request_id a977ef10ccf1, same request as E3)"
    quote: "{\"event\": \"request\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 1.823}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:30.738Z-.739Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"} / {\"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.396}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:28.624Z"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.811}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:34.980Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} / {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.275}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:36.039Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/orders\"} / {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.277}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:37.100Z"
    quote: "{\"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/4\"} / {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/4\", \"status\": 503, \"duration_ms\": 0.293}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:18:33.921Z"
    quote: "{\"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.337}"
  - id: E11
    type: metric
    source: "GET /metrics probe @ 2026-08-18T22:19:22.445Z, request_id konan-1787091562-30193"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: metric
    source: "GET /metrics probe @ 2026-08-18T22:19:22.445Z, request_id konan-1787091562-30193"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no data lines — zero recorded series)"
  - id: E13
    type: probe
    source: "GET /health probe @ 2026-08-18T22:19:22.376Z, request_id konan-1787091562-30187"
    quote: "HTTP 200 in 0.002618s request_id=konan-1787091562-30187; body {\"status\":\"ok\",\"uptime_seconds\":65.07570695807226}"
  - id: E14
    type: metric
    source: "two /metrics scrapes ~67s apart spanning the chaos window (orchestrator @22:19:22Z, infra-process lens re-probe later)"
    quote: "process_max_rss_bytes 47300608 (identical on both scrapes)"
  - id: E15
    type: log
    source: "lab/logs/app.log, duration_ms fields on the four chaos_failure-tagged requests (E5, E7, E8, E9)"
    quote: "duration_ms: 0.396, 0.275, 0.277, 0.293 — all sub-millisecond, consistent with extra_latency_ms: 0 in E3"
  - id: E16
    type: probe
    source: "GET /products/1 re-probe during investigation, request_id konan-1787091653-30293"
    quote: "HTTP 200 — same route/id as the 503 recorded at E7, now succeeding"
gaps:
  - "CPU utilization / load-average is not part of this service's exposed telemetry (docs/lab.md's metric list has no CPU gauge) — H2's resource-saturation arm was invalidated on memory (E14) and response-latency (E15) evidence only; a CPU metric was not available to check further."
  - "The actor or origin of the POST /chaos/enable call at 22:18:25.506Z could not be identified beyond `client: 127.0.0.1:52367` — no auth/identity field is logged, and /chaos is outside the investigator's read surface per docs/lab.md, so who or what flipped the flag stays unknown from telemetry."
  - "third-party and data-db incident classes were not investigated as separate lenses: docs/lab.md states this lab service has no real database and no third-party dependency, so these classes are excluded by the surface contract itself, not by omission."
usage:
  model: claude-sonnet-5
  tokens: 2218205
  wall_clock_seconds: 270
---

# Shop intermittent 503s traced to chaos mode being enabled at 22:18:25Z

## Summary

**Root cause identified.** At 2026-08-18T22:18:25.506Z, chaos mode was switched on
(`POST /chaos/enable`, `failure_rate: 0.4`, `error_status: 503`, `extra_latency_ms: 0`) —
E3. From that instant, business routes (`/orders`, `/products/{id}`) began failing
roughly 40% of the time with instant 503s, interleaved with successes on the very same
routes (E5–E10), which matches the complaint's "error out, then work again on retry"
shape exactly. `/health` returned 200 throughout, including 54 seconds into the chaos
window (E13) — chaos mode does not touch the health route, so the dashboard reads green
while real user traffic on other routes degrades. Two alternative explanations —
process/resource instability (H2) and a software defect (H3) — were tested and both
invalidated by direct evidence: no restarts, flat memory, near-zero failure latency
(E1, E14, E15), zero unhandled exceptions, and the exact same route/input flipping
between success and failure across attempts (E12, E6, E7, E16). Confidence: high — the
declared `failure_rate: 0.4` in the enable event matches the observed ~40% failure rate
in the traffic sample, and every failure line is self-labeled `chaos_failure` by the
application.

## Timeline (UTC, 2026-08-18)

- `22:18:17.312Z` — process startup (E1); one clean startup, no restarts since.
- `22:18:17Z`–`22:18:22.442Z` — clean traffic: health, products, an order created, all
  2xx (E2 is the last clean request in this window).
- `22:18:25.506Z` — **chaos mode enabled** (E3), immediately reflected in
  `POST /chaos/enable -> 200` (E4). This is the onset marker.
- `22:18:28.624Z` — `GET /products/1` succeeds (E6) — chaos does not fail every request.
- `22:18:30.738Z` — first injected failure: `POST /orders -> 503` (E5).
- `22:18:33.921Z` — `POST /orders -> 201` succeeds (E10) — same route recovers on a
  later attempt, matching "work again on retry."
- `22:18:34.980Z` — `GET /products/1 -> 503` (E7) — same route/id as the 22:18:28
  success (E6), now failing.
- `22:18:36.039Z` — `GET /orders -> 503` (E8).
- `22:18:37.100Z` — `GET /products/4 -> 503` (E9).
- `22:19:22.376Z` — investigator's own `GET /health` probe returns 200 (E13), ~54s
  after chaos was enabled and still active (E11 shows `faultline_chaos_enabled 1` at
  the same scrape) — confirms health stays green independent of chaos state.

## Investigation

- **Baseline** (step 1): the target process was only ~65s old at first contact, so the
  full `lab/logs/app.log` (31→33 lines) was effectively the complete history. It showed
  a clean startup, clean traffic, then the `chaos_enabled` marker followed by
  interleaved 200s and chaos-tagged 503s. `/metrics` corroborated: `faultline_chaos_enabled 1`,
  no exception series, flat RSS.
- **Triage** (step 2): three lenses spawned in parallel, blind to each other —
  infra-process, interfaces, software-defect (the only classes this lab's surface can
  exercise per `docs/lab.md`'s known-gaps note; third-party and data-db are structurally
  excluded, recorded under Gaps).
  - infra-process: no lifecycle, saturation, or latency anomaly — ruled out its own domain.
  - interfaces: found the config-flip marker (E3/E4), the matching ~40% probabilistic
    rate, and the health-blind-spot shape — this became H1.
  - software-defect: zero exceptions, failures spread across three unrelated routes,
    same input flipping between success/failure — ruled out its own domain.
- **Deep-dive** (step 3): skipped. Triage evidence for all three hypotheses was already
  deterministic and complete (an explicit config-change event with declared parameters
  that exactly match observed behavior, plus clean negative evidence for the
  alternatives) — no additional targeted probing could add information the logs and
  metrics didn't already settle.
- **Judge** (step 4): a fresh adversarial judge, given only the hypothesis list and
  verbatim evidence (no narrative), validated H1 and invalidated H2 and H3, each with
  cited reasoning tied to specific evidence ids. No iteration was needed — verdicts were
  decisive on the first pass.

## Hypotheses

### H1 — chaos mode enabled (validated)

The `chaos_enabled` event (E3) declares `failure_rate: 0.4`, `error_status: 503`,
`extra_latency_ms: 0` at 22:18:25.506Z. Every subsequent 503 in the log is preceded by
a `chaos_failure` warning naming the same method/path (E5, E7, E8, E9), and the same
routes also succeed nearby (E2, E6, E10) — a probabilistic, not deterministic, failure
mode. `/health` stayed green throughout (E13) even though chaos remained enabled at the
same moment (E11) — explaining the complaint's "health dashboard is green" alongside
real, intermittent business-route failures. The judge found no evidence against this
chain.

### H2 — process instability / resource saturation (invalidated)

Only one startup event exists in the whole log, with no restarts (E1). `process_max_rss_bytes`
was identical across two scrapes spanning the chaos window (E14) — no memory growth.
Chaos-tagged failures returned in under half a millisecond (E15), which is the opposite
of how saturation-driven failures behave (queueing, slow responses). The judge noted
CPU utilization isn't exposed by this service (see Gaps) but found the cited evidence
sufficient to invalidate on memory and latency alone.

### H3 — software defect (invalidated)

`http_exceptions_total` had zero recorded series (E12) — no unhandled exception was
counted anywhere. The same route and same product id (`/products/1`) returned 200 at
22:18:28.624Z (E6), 503 at 22:18:34.980Z (E7), and 200 again on a later re-probe (E16) —
inconsistent with a deterministic, data-tied defect. Failures also spread across three
unrelated routes (`/orders`, `/products/1`, `/products/4`) rather than concentrating on
one, which the software-defect lens's own method flags as evidence against a
single-route code bug.

## Safe next steps

- Re-scrape `/metrics` periodically (read-only) to watch `faultline_chaos_enabled` and
  confirm when/if it returns to `0`, and to watch whether the observed failure rate
  keeps tracking the declared `0.4`.
- Keep sampling `/orders` and `/products/{id}` read-only to track the interleaved
  success/failure pattern over time — a change in the ratio would be a signal the
  configuration changed again.
- Continue reading `lab/logs/app.log` for a future `chaos_disabled` marker or any new
  `chaos_enabled` marker with different parameters, both of which would need a fresh
  investigation entry, not an assumption that this one still applies.

## Gaps

- CPU utilization / load-average is not part of this service's exposed telemetry
  (`docs/lab.md`'s metric list has no CPU gauge) — H2's resource-saturation arm was
  invalidated on memory (E14) and response-latency (E15) evidence only; a CPU metric
  was not available to check further.
- The actor or origin of the `POST /chaos/enable` call at 22:18:25.506Z could not be
  identified beyond `client: 127.0.0.1:52367` — no auth/identity field is logged, and
  `/chaos` is outside the investigator's read surface per `docs/lab.md`, so who or what
  flipped the flag stays unknown from telemetry.
- `third-party` and `data-db` incident classes were not investigated as separate
  lenses: `docs/lab.md` states this lab service has no real database and no
  third-party dependency, so these classes are excluded by the surface contract
  itself, not by omission.
