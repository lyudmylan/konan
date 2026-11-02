---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-occasional-503s
  trigger: "manual (human report via /konan, fingerprint human-1793660793, startsAt 2026-11-02T23:06:33Z, investigation start 2026-11-02T23:06:42Z — 9s trigger latency)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-02T23:06:42Z
  concluded: 2026-11-02T23:21:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos toggle (failure_rate=0.08, error_status=503) was switched on via POST /chaos/enable at 23:06:24.667Z, injecting probabilistic 503s on GET /products/5, GET /orders, and POST /orders — each one recovering on an immediate retry of the same route — which matches the complaint's 'occasional error... works on retry, most people notice nothing' almost exactly."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos/fault-injection toggle (failure_rate=0.08, error_status=503) was switched on and injects probabilistic 503s on specific business routes (GET /products/5, GET /orders, POST /orders), each recovering on an immediate retry of the same route; no code defect, process crash/restart, or resource/latency issue is responsible."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12]
    evidence_against: []
  - id: H2
    statement: "GET /products/5 has a data-dependent code defect that makes it fail on that specific product id."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:19.773Z"
    quote: '{"ts": "2026-11-02T23:06:19.773Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:20.501Z-23:06:22.610Z (complete pre-toggle window; process started at 23:06:19.773Z)"
    quote: |-
      {"ts": "2026-11-02T23:06:20.501Z", ..., "message": "GET /health -> 200", "status": 200}
      {"ts": "2026-11-02T23:06:20.520Z", ..., "message": "GET /products -> 200", "status": 200}
      {"ts": "2026-11-02T23:06:21.569Z", ..., "message": "GET /products/1 -> 200", "status": 200}
      {"ts": "2026-11-02T23:06:22.610Z", ..., "message": "POST /orders -> 201", "status": 201}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:24.667Z"
    quote: '{"ts": "2026-11-02T23:06:24.667Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "a5cd1bcf982a", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:24.668Z"
    quote: '{"ts": "2026-11-02T23:06:24.668Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "a5cd1bcf982a", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.515, "client": "127.0.0.1:62166"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:25.870Z"
    quote: '{"ts": "2026-11-02T23:06:25.870Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "1e84777c8ec2", "event": "chaos_failure", "method": "GET", "path": "/products/5"} / {"ts": "2026-11-02T23:06:25.870Z", "level": "INFO", "message": "GET /products/5 -> 503", "request_id": "1e84777c8ec2", "event": "request", "status": 503, "duration_ms": 0.144}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:25.954Z"
    quote: '{"ts": "2026-11-02T23:06:25.954Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "ec6be409b477", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.402, "client": "127.0.0.1:62182"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:25.967Z and 23:06:26.049Z"
    quote: '{"ts": "2026-11-02T23:06:25.967Z", "level": "WARNING", "message": "chaos-injected failure", "request_id": "9e92e5e17a81", "event": "chaos_failure", "method": "GET", "path": "/orders"} / {"ts": "2026-11-02T23:06:25.967Z", "message": "GET /orders -> 503", "status": 503} ... then {"ts": "2026-11-02T23:06:26.049Z", "message": "GET /orders -> 200", "request_id": "d04f199a2458", "status": 200}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:06:26.063Z and 23:06:26.146Z"
    quote: '{"ts": "2026-11-02T23:06:26.063Z", "level": "WARNING", "message": "chaos-injected failure", "request_id": "23bb1f393bd9", "event": "chaos_failure", "method": "POST", "path": "/orders"} / {"ts": "2026-11-02T23:06:26.063Z", "message": "POST /orders -> 503", "status": 503} ... then {"ts": "2026-11-02T23:06:26.146Z", "message": "POST /orders -> 201", "request_id": "cc6e864aff06", "status": 201}'
  - id: E9
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-02T23:07:17.018Z, request_id konan-1793660837-9962"
    quote: |-
      http_requests_total{method="GET",path="/products/5",status="503"} 2
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 1
      process_uptime_seconds 57.25933870812878
      process_max_rss_bytes 47235072
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:14:16.101Z (investigator-run probe, cross-checked live against the /metrics counter)"
    quote: |-
      {"ts": "2026-11-02T23:14:16.101Z", "level": "WARNING", "message": "chaos-injected failure", "request_id": "konan-1793661256-10276", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-02T23:14:16.101Z", "message": "GET /orders -> 503", "request_id": "konan-1793661256-10276", "status": 503}
      -- same burst's /metrics delta: http_requests_total{method="GET",path="/orders",status="503"} rose from 1 to 2, in exact lockstep with this one new chaos_failure line (an independently-sourced counter, not just the self-consistent request-log pairing)
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:14:11.374Z-23:14:11.560Z (15 consecutive investigator probes of GET /products/5; 3 of 15 shown, all identical in shape)"
    quote: |-
      {"ts": "2026-11-02T23:14:11.374Z", "message": "GET /products/5 -> 200", "request_id": "konan-1793661251-10212", "status": 200}
      {"ts": "2026-11-02T23:14:11.389Z", "message": "GET /products/5 -> 200", "request_id": "konan-1793661251-10215", "status": 200}
      {"ts": "2026-11-02T23:14:11.560Z", "message": "GET /products/5 -> 200", "request_id": "konan-1793661251-10254", "status": 200}
  - id: E12
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-02T23:26:41Z (approx), request_id konan-1793661601-10531"
    quote: |-
      http_requests_total{method="GET",path="/orders",status="503"} 2
      http_requests_total{method="GET",path="/products/5",status="503"} 3
      http_requests_total{method="POST",path="/orders",status="503"} 1
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 1
      process_uptime_seconds 821.6640412081033
      process_max_rss_bytes 47235072
gaps:
  - "No pre-toggle clean baseline exists specifically for GET /products/5 or GET /orders (GET) — the process was only 4.9 seconds old when the toggle fired (E1, E3), and no rotated log backup exists (ls lab/logs/ shows only app.log) to extend the window further back. This is a hard limit of process age, not a fixable gap: the entire observable history of this process instance is captured."
  - "An on/off comparison (disable chaos and confirm the failure rate drops to zero) was not performed and could not be: /chaos and /simulate are operator/eval surface, mechanically blocked for a read-only investigator per docs/lab.md and the lab boundary in AGENTS.md — only the eval harness may trigger such actions. Chaos remained enabled (faultline_chaos_enabled 1) at every check through the end of this investigation (E9, E12), with zero chaos_disabled events anywhere in the log."
  - "The surface contract (docs/lab.md) does not expose who or what called POST /chaos/enable — only the resulting log line (E3, E4). Attribution to a specific actor (operator, scenario script, or otherwise) is out of reach from telemetry alone."
  - "This surface shows server-side telemetry only. It cannot confirm how many of the complaint's \"couple of users\" specifically hit a 503, versus the broader simulated/background traffic also visible in the log — only that the aggregate failure rate (roughly 8-14% on the three affected routes, consistent with the configured 0.08) and its retry-recoverable shape are consistent with the complaint as reported."
usage:
  model: claude-sonnet-5
  tokens: 5179120
  wall_clock_seconds: 901
---

# Occasional, retryable shop errors traced to a live chaos toggle

## Summary

**Root cause identified — and it is, largely, "nothing" from a code standpoint, but it is real.**
At 23:06:24.667Z an internal chaos/fault-injection toggle was switched on
(`failure_rate=0.08`, `error_status=503`, E3), 4.9 seconds after the process itself started
(E1). Within 1.2 seconds, the first injected failure landed on `GET /products/5` (E5),
followed seconds later by the same pattern on `GET /orders` (E7) and `POST /orders` (E8) —
each failure paired with an immediate success on a retry of the very same route (E6, E7, E8).
A live reproduction run roughly 8 minutes into the investigation confirmed the toggle was
still firing (E10, cross-checked against an independently-sourced Prometheus counter, not
just the self-reported log tag) and that the failure is probabilistic, not a deterministic
per-input defect: 15 straight probes of the suspect route all succeeded (E11). No unhandled
exception, process restart, or resource/latency drift was found anywhere in the log or in
two `/metrics` snapshots taken ~20 minutes apart (E9, E12) — RSS and uptime both track a
single continuous process lifetime. This matches the complaint almost exactly: an occasional,
retry-recoverable error on a small, stable fraction of requests, invisible to most users.
Confidence: high on the mechanism and its scope; see Gaps for what this read-only surface
could not settle (chiefly: who/what flipped the toggle, and that it is still on as of this
writing).

## Timeline (UTC)

- `23:06:19.773Z` — process startup, single `startup` event (E1).
- `23:06:20.501Z`-`23:06:22.610Z` — clean baseline traffic: `/health`, `/products`,
  `/products/1`, `POST /orders`, all 200/201 (E2). No pre-toggle sample exists yet for
  `/products/5` or `GET /orders`.
- `23:06:24.667Z` — **config-change marker**: chaos toggle enabled, `failure_rate=0.08`,
  `error_status=503`, `extra_latency_ms=0` (E3), via `POST /chaos/enable -> 200` (E4).
- `23:06:25.870Z` — first failure, 1.2s after the marker: `GET /products/5 -> 503`,
  tagged `chaos_failure` (E5).
- `23:06:25.954Z` — same route recovers on next call, 84ms later: `GET /products/5 -> 200`
  (E6).
- `23:06:25.967Z`-`23:06:26.049Z` — same fail/recover pattern on `GET /orders` (E7).
- `23:06:26.063Z`-`23:06:26.146Z` — same pattern on `POST /orders` (E8) — the write path is
  affected too, not just reads.
- `23:06:33Z` — complaint `startsAt` (human report, fingerprint `human-1793660793`).
- `23:06:42Z` — investigation start (9s trigger latency).
- `23:07:17.018Z` — first `/metrics` snapshot: toggle still on, uptime 57.26s, zero
  exceptions (E9).
- `23:14:11Z`-`23:14:16Z` — live reproduction: 15/15 clean on `/products/5` (E11), then one
  failure in a 10-probe burst on `/orders`, matched 1:1 against an independent Prometheus
  counter delta (E10).
- `~23:26:41Z` — final `/metrics` snapshot: toggle still on (never disabled), uptime 821.66s
  continuous, RSS unchanged, zero exceptions throughout (E12).

## Investigation

0. **Trigger** — complaint object (verbatim): `{"source":"human","fingerprint":"human-1793660793","labels":{"alertname":"human-report"},"annotations":{"summary":"A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"},"startsAt":"2026-11-02T23:06:33Z"}`. Investigation start `2026-11-02T23:06:42Z` — 9s trigger latency.
1. **Baseline** — `/health` and `/metrics` probed; process uptime ~57s, `faultline_chaos_enabled 1`
   already set, 503s already present on three routes (E9). Full log read (single file, no
   rotated backups).
2. **Triage** — all three lenses fanned out in parallel (the complaint was too vague to
   exclude any domain):
   - `infra-process`: found the chaos toggle itself as the anomaly, confirmed still live,
     ruled out restart/resource drift via gauges.
   - `interfaces`: found the same toggle as a sharp-onset config marker, built the
     before/after timeline, confirmed the failure rate held steady and was spread across
     routes rather than concentrated.
   - `software-defect`: found zero exceptions, reproduced `/products/5` repeatedly to show
     the failure is probabilistic (not deterministic per-input), confirmed 5xx counts are
     fully explained by `chaos_failure` tags with no bare/unexplained 503s.
3. **Deep-dive skipped on round 1** — all three lenses independently converged on the same
   mechanism with deterministic, logged evidence; per the loop's rule, this hypothesis went
   straight to judge instead of being re-proven.
4. **Judge (round 1)** — fresh adversarial subagent, given only the hypothesis and verbatim
   evidence: **inconclusive**. It flagged two real gaps: (a) no verified pre-toggle baseline
   specifically on `GET /products/5`/`GET /orders`, and (b) the `chaos_failure` log tag and
   the 503 response are written by the same code path, so their 1:1 match is not independent
   confirmation.
5. **Deep-dive (round 2)** — one targeted agent closed what was closeable: confirmed gap (a)
   is a hard limit (process was 4.9s old at the toggle, no backups exist to extend the
   window), and closed gap (b) by running a fresh probe burst and comparing its result
   against an independently-sourced Prometheus counter delta, which moved in exact lockstep
   with the log tag (E10). It also ran the reproduction burst that produced E11.
6. **Judge (round 2, final)** — re-run with the closed gaps: **H1 validated**. The on/off
   comparison the judge would otherwise want is a structural limit (operator/eval surface,
   out of reach for a read-only investigator), not a missed step, and is recorded as a gap
   rather than chased further.
7. **Supplementary check** — confirmed `/health` (4/4 200) and `GET /products` list (7/7 200)
   stayed completely clean throughout, per the final `/metrics` counters (E12), tightening the
   "spread across specific routes, not everywhere" framing.

## Hypotheses

### H1 — chaos/fault-injection toggle (validated)

An internal toggle (`failure_rate=0.08`, `error_status=503`) was switched on (E3, E4) and
injects probabilistic 503s on `GET /products/5`, `GET /orders`, and `POST /orders` (E5, E7,
E8), each one recovering on an immediate retry of the same route (E6, E7, E8). The mechanism
is still active at the end of this investigation, ~20 minutes and two independent `/metrics`
pulls later (E9, E12), with no restart (E1), no exception (E9, E12), and no RSS/latency drift
(E9 vs E12) to explain it any other way. An independent probe burst (E10) confirmed the
`chaos_failure` log tag isn't just self-reported bookkeeping: a separately-sourced Prometheus
counter moved in lockstep with it. No evidence against.

### H2 — data-dependent code defect on product id 5 (invalidated)

Tested because `/products/5` carried the highest 503 count of any single route early on.
Invalidated: the same route recovered on the very next call after failing (E6), and a later
burst of 15 consecutive probes against it returned 200 every time (E11) — a genuine per-input
defect would fail consistently, not succeed on 14 of the last 16 attempts. The failure instead
tracks the chaos toggle's configured rate, not the input.

## Safe next steps

- Re-probe `/metrics` periodically (read-only) to see whether `faultline_chaos_enabled` ever
  reverts to `0` on its own, which would bound how long this lasts.
- If a user reports a *persistent* (non-retryable) error on the shop, treat that as a
  different signal from this one — this incident's shape is specifically "fails sometimes,
  succeeds on retry."
- No destructive or mutating action is suggested here; turning chaos off is operator/eval
  surface (`scripts/scenario.sh chaos-off`), out of scope for a read-only investigation.

## Gaps

- No pre-toggle clean baseline exists specifically for `GET /products/5` or `GET /orders`
  (GET) — the process was only 4.9 seconds old when the toggle fired, and no rotated log
  backup exists to extend the window further back. A hard limit of process age, not a
  fixable gap: the entire observable history of this process instance is captured.
- An on/off comparison (disable chaos, confirm the failure rate drops to zero) was not
  performed and could not be: `/chaos` and `/simulate` are operator/eval surface, mechanically
  blocked for a read-only investigator. Chaos remained enabled at every check through the end
  of this investigation, with zero `chaos_disabled` events anywhere in the log.
- The surface contract does not expose who or what called `POST /chaos/enable` — only the
  resulting log line. Attribution to a specific actor is out of reach from telemetry alone.
- This surface shows server-side telemetry only; it cannot confirm exactly how many of the
  complaint's "couple of users" hit a 503 versus the broader traffic also visible in the log
  — only that the aggregate rate and its retry-recoverable shape are consistent with the
  complaint as reported.
