---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-handover-chaos-and-products-3
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: "2026-08-18T20:22:40Z"
  concluded: "2026-08-18T20:33:04Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "Chaos mode was deliberately toggled on and off three separate times, each shortly after a process (re)start — process starts at 20:07:17Z, 20:08:19Z, and 20:21:57Z — with chaos episodes at 20:07:20-27Z, 20:08:23-29Z, and 20:22:01-08Z. Each episode injected probabilistic 503s (configured failure_rate 0.6) across /products, /products/2, and POST /orders, evidenced by direct chaos-injected-failure log lines in all three episodes, and self-resolved via a matching chaos_disabled marker before the next restart (or, for the third episode, before the present). No further chaos-related failures have occurred since the last disable marker at 20:22:07.911Z."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 deterministically returns 500 (ZeroDivisionError) because product 3 (Unobtainium Ingot) has units_in_stock 0, dividing by zero when computing turnover_score in shop.py:64. Every recorded request to this path in the retained log (5 occurrences, spanning two process instances) carries an investigator-stamped konan- request id; no non-investigator traffic hit it during this investigation's window."
    evidence: [E14, E15, E16, E17, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:17.072Z"
    quote: "{\"ts\": \"2026-08-18T20:07:17.072Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:20.948Z"
    quote: "{\"ts\": \"2026-08-18T20:07:20.948Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"ddc4edac99ce\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:22.008Z-20:07:22.009Z"
    quote: "{\"message\": \"chaos-injected failure\", \"request_id\": \"33c824dddf8e\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} / {\"message\": \"GET /products -> 503\", \"status\": 503, \"duration_ms\": 0.294}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:27.300Z"
    quote: "{\"ts\": \"2026-08-18T20:07:27.300Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"3aeca5655f5f\", \"event\": \"chaos_disabled\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:19.219Z"
    quote: "{\"ts\": \"2026-08-18T20:08:19.219Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:23.129Z"
    quote: "{\"ts\": \"2026-08-18T20:08:23.129Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"656197e653c3\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:25.247Z, 20:08:27.365Z-366Z, 20:08:28.423Z"
    quote: "chaos-injected failure GET /products/2 -> 503 (req 2d270de331b6) / chaos-injected failure POST /orders -> 503 (req 45b8ee9d5569) / chaos-injected failure GET /products -> 503 (req 1d1cce4cb225)"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:29.480Z"
    quote: "{\"ts\": \"2026-08-18T20:08:29.480Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"c6f66e10e77d\", \"event\": \"chaos_disabled\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:21:57.657Z"
    quote: "{\"ts\": \"2026-08-18T20:21:57.657Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:01.558Z"
    quote: "{\"ts\": \"2026-08-18T20:22:01.558Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"33536b678954\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:02.615Z, 20:22:03.674Z, 20:22:05.793Z"
    quote: "chaos-injected failure GET /products -> 503 (req 6aa97b0a7688) / chaos-injected failure GET /products/2 -> 503 (req 20104f20ce5d) / chaos-injected failure POST /orders -> 503 (req d40f49113600)"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:07.911Z"
    quote: "{\"ts\": \"2026-08-18T20:22:07.911Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"0d3ed61424da\", \"event\": \"chaos_disabled\"}"
  - id: E13
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-08-18T20:26:13Z (request_id konan-1787084773-23301, process_uptime_seconds 255.7 - current process, no restart since E9)"
    quote: "faultline_chaos_enabled 0 / http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1 (counts match episode 3 alone; no new 503s since E12)"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.043Z"
    quote: "{\"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787083912-22619\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n...ZeroDivisionError: division by zero\"}"
  - id: E15
    type: probe
    source: "scripts/probe.sh /products @ 2026-08-18T20:26:13Z (request_id konan-1787084773-23295)"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0}"
  - id: E16
    type: probe
    source: "scripts/probe.sh /products/3 @ 2026-08-18T20:27:00Z"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787084820-23309\"} -- HTTP 500 in 0.005375s"
  - id: E17
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-08-18T20:26:13Z"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 2"
  - id: E18
    type: log
    source: "lab/logs/app.log, full-file grep for path=/products/3"
    quote: "5 matching lines, request_ids konan-1787083912-22619 (20:11:52.050Z), konan-1787083917-22635 (20:11:57.813Z), konan-1787084665-23136 (20:24:25.740Z), konan-1787084691-23226 (20:24:51.884Z), konan-1787084820-23309 (20:27:00.306Z) — every one status 500, every request_id konan-prefixed; no other request_id ever appears on this path"
gaps:
  - "Who or what issued the three POST /chaos/enable calls (operator vs. scheduled scenario harness) is not visible on the investigator's surface — /chaos is operator-only; only its logged effect is observable."
  - "Log rotation retains only the current window (since 2026-08-18T19:52:52Z); any state before that could not be checked."
  - "Whether real (non-investigator) traffic ever hit /products/3 before this retained window is unknown from this log alone."
usage:
  model: claude-sonnet-5
  tokens: 4977979
  wall_clock_seconds: 624
---

# Shop on-call handover check: chaos noise self-resolved, /products/3 still a latent ZeroDivisionError

## Summary

**No active incident.** The "noise earlier" the on-call handover mentioned matches three
short, self-resolving chaos-mode episodes (20:07:20-27Z, 20:08:23-29Z, and 20:22:01-08Z),
each a deliberate `chaos_enabled`/`chaos_disabled` toggle pair injecting probabilistic
503s (configured `failure_rate: 0.6`) across `/products`, `/products/2`, and
`POST /orders`. All three self-resolved via their own disable marker; the service has been
back to a clean chaos-off state since 20:22:07.911Z, confirmed by the current `/metrics`
snapshot showing no 503s since. Confidence: high — every episode has direct evidence of
both the toggle and the injected failures, cross-checked against process-restart markers,
and survived two rounds of adversarial review.

Riding along, not the incident: `GET /products/3` still deterministically 500s
(`ZeroDivisionError`, product 3 has `units_in_stock: 0`). It reproduced on every probe this
session, but the retained log shows no non-investigator traffic ever hit that route — it is
latent, not currently user-facing.

## Timeline

- **20:07:17Z** (E1) — process restart.
- **20:07:20Z-20:07:27Z** (E2, E3, E4) — chaos episode 1: enabled, injected 503 on
  `/products`, disabled.
- **20:08:19Z** (E5) — process restart.
- **20:08:23Z-20:08:29Z** (E6, E7, E8) — chaos episode 2: enabled, injected 503s on
  `/products/2`, `POST /orders`, `/products`, disabled.
- **20:11:52Z, 20:11:57Z** (E14, part of E18) — investigator probes trigger the
  `/products/3` `ZeroDivisionError` in the process instance started at 20:08:19Z.
- **20:21:57Z** (E9) — process restart (current process instance).
- **20:22:01Z-20:22:07Z** (E10, E11, E12) — chaos episode 3: enabled, injected 503s on
  `/products`, `/products/2`, `POST /orders`, disabled. This is the episode nearest the
  handover complaint's "noise earlier."
- **20:22:37Z** — human handover complaint received.
- **20:22:40Z** — investigation started.
- **20:24:25Z, 20:24:51Z, 20:27:00Z** (part of E18, E16) — further investigator probes
  reproduce the `/products/3` `ZeroDivisionError`, confirming it is still live and
  deterministic.
- **20:26:13Z** (E13, E15, E17) — baseline/confirmation snapshot: chaos off, no new
  chaos-related 503s since E12; product 3 confirmed at `units_in_stock: 0`.
- **20:33:04Z** — investigation concluded.

## Investigation

Baseline (health, metrics, log tail) showed a service that was healthy right now but with
visible history of 503s and two `unhandled_exception` lines in the retained log window —
enough ambiguity to warrant a full discipline-parallel triage rather than a health-check
rubber stamp (the healthy-monitoring trap).

Triage fanned out three lenses in parallel:
- **software-defect** found the `/products/3` `ZeroDivisionError`, reproduced it live,
  and confirmed it is data-dependent on `units_in_stock: 0` (product 3 only).
- **interfaces** found three matched chaos-toggle episodes, gateway-shaped and
  probabilistic (rate near the configured 0.6, spread across routes), each
  self-terminating, with no active degradation now.
- **infra-process** found nothing anomalous: restarts are graceful (clean shutdown before
  each), no RSS growth, no latency drift.

Both remaining candidate explanations (chaos toggles for "noise earlier"; the
`/products/3` defect as a possible separate concern) had deterministic, reproducible
triage evidence, so both skipped deep-dive and went straight to the adversarial judge.

**Round 1 judge**: invalidated the first draft of H1, which claimed the three episodes
happened "in this process's lifetime" — its own cited evidence (`process_uptime_seconds`
on the current process) contradicted that, since only the third episode fell inside the
current process's uptime. The judge validated the `/products/3` latent finding as-is.

**Round 2**: re-anchored each chaos episode to the process-restart marker immediately
preceding it (three separate process instances, one episode per instance) and added the
missing direct `chaos_failure` log lines for episodes 1 and 3 (previously only markers
were cited for those two). Re-judged: the chaos-toggle mechanics were validated outright.
The judge flagged one remaining overreach — an early draft claimed "the service is
currently in a clean state," which the same log window contradicts (the `/products/3`
500s recur throughout). The hypothesis statement was narrowed to scope the "clean state"
claim to chaos-related failures only, which the evidence fully supports.

## Hypotheses

### H1 — chaos-toggle noise, self-resolved (validated)

Three deliberate chaos-mode toggles, one shortly after each of three process restarts,
each injecting probabilistic 503s and disabling itself minutes later. Direct
`chaos_failure` log lines exist for all three episodes (E3, E7, E11), not just the
enable/disable markers, and the current `/metrics` snapshot (E13) shows no chaos-related
503 since the last disable. This is the best fit for the complaint's "noise earlier ...
nobody filed a report" — each episode was brief, self-terminating, and left no residue.

### Latent finding — `/products/3` `ZeroDivisionError` (not the incident)

Deterministic, data-dependent 500 on `GET /products/3`: product 3 (`Unobtainium Ingot`)
has `units_in_stock: 0`, and `shop.py:64` divides `units_ordered / product["units_in_stock"]`
when building `turnover_score`. Reproduced on demand throughout this investigation (E16),
with a matching stack trace from earlier in the retained window (E14). Every one of the 5
requests this path has received in the retained log carries an investigator (`konan-`)
request id (E18) — no user traffic has exercised it in this window, so it does not change
the no-active-incident verdict. It is a genuine, standing defect, though: this exact
code path, product, and root cause (`units_in_stock: 0`) previously caused a
user-facing incident, documented outside this investigation's evidence window.

## Safe next steps

- Confirm with the team whether `/products/3`'s zero-stock data and the unhandled
  `ZeroDivisionError` it triggers are already tracked — this defect has fired on every
  probe of that route in this session and has a documented history of user impact when
  real traffic reaches it.
- No action needed on the chaos-toggle episodes — they were self-resolving and have left
  no active effect; if the toggle cadence (three times in under 15 minutes of wall clock,
  spread across restarts) is unexpected for this environment, confirm with whoever
  operates the chaos/scenario controls that it was intentional.
- If restart cadence (6 restarts in ~29 minutes across the full retained log) is
  unexpected for this environment, confirm with the process owner — this investigation
  found no evidence it is harmful (all restarts were graceful), so it is a question of
  intent, not health.

## Gaps

- Who or what issued the three `POST /chaos/enable` calls is not visible on the
  investigator's read-only surface — only the logged effect is observable, not the
  operator/harness identity behind each request.
- Log rotation bounds this investigation to the window since 2026-08-18T19:52:52Z;
  nothing before that could be checked.
- Whether real (non-investigator) traffic has ever hit `/products/3` within this
  retained window is unknown beyond what the log shows — the log shows none, but a gap
  before 19:52:52Z is unverifiable.
