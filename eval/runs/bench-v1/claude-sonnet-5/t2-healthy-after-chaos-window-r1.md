---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-toggle-products-503
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-19T01:37:42Z
  concluded: 2026-08-19T01:42:59Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A config toggle (POST /chaos/enable, failure_rate=0.6) injected three HTTP 503s on GET /products and GET /products/1 between 01:37:03.866Z and 01:37:08.102Z; it was disabled at 01:37:09.162Z and traffic has been clean since."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "The earlier 'noise' was a chaos-mode fault-injection episode (config/flag toggle), not a software defect or infrastructure failure; it is resolved and there is no active incident."
    incident_class: interfaces
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:36:58.916Z"
    quote: '{"ts": "2026-08-19T01:36:58.916Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: probe
    source: "scripts/probe.sh /health, request_id=konan-1787103480-37112"
    quote: '{"status":"ok","uptime_seconds":61.19830612489022}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:02.808Z"
    quote: '{"ts": "2026-08-19T01:37:02.808Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "bcbe2265ef77", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:03.866Z-01:37:03.867Z"
    quote: |
      {"ts": "2026-08-19T01:37:03.866Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "cd2f15236509", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-08-19T01:37:03.867Z", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "cd2f15236509", "event": "request", "method": "GET", "path": "/products", "status": 503}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:04.925Z"
    quote: '{"ts": "2026-08-19T01:37:04.925Z", "message": "GET /products/2 -> 200", "request_id": "659b41b2de4e", "event": "request", "status": 200}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:05.983Z-01:37:05.984Z"
    quote: |
      {"ts": "2026-08-19T01:37:05.983Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5d39dbd7ab2d", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-08-19T01:37:05.984Z", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "5d39dbd7ab2d", "event": "request", "method": "GET", "path": "/products/1", "status": 503}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:07.045Z"
    quote: '{"ts": "2026-08-19T01:37:07.045Z", "message": "POST /orders -> 201", "request_id": "ff82e65151f3", "event": "request", "status": 201}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:08.102Z"
    quote: |
      {"ts": "2026-08-19T01:37:08.102Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "fe329172ab88", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-08-19T01:37:08.102Z", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "fe329172ab88", "event": "request", "method": "GET", "path": "/products", "status": 503}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:09.162Z"
    quote: '{"ts": "2026-08-19T01:37:09.162Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "f3a0b5864daa", "event": "chaos_disabled"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:29.221Z (first clean line after chaos_disabled; every line through 01:38:02.626Z, end of file at investigation time, is likewise 200/201)"
    quote: '{"ts": "2026-08-19T01:37:29.221Z", "message": "GET /products -> 200", "request_id": "20f0d7228646", "event": "request", "method": "GET", "path": "/products", "status": 200}'
  - id: E11
    type: metric
    source: "scripts/probe.sh /metrics, request_id=konan-1787103482-37118 (baseline)"
    quote: |
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
  - id: E12
    type: metric
    source: "scripts/probe.sh /metrics, request_id=konan-1787103482-37118 (baseline) — full metric block quoted; no counter series follow it, i.e. zero exceptions recorded"
    quote: |
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E13
    type: metric
    source: "scripts/probe.sh /metrics, request_id=konan-1787103482-37118 (baseline)"
    quote: 'faultline_chaos_enabled 0'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:00.747Z"
    quote: '{"ts": "2026-08-19T01:37:00.747Z", "message": "GET /products/1 -> 200", "request_id": "6b4b73880771", "status": 200}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:37:30.279Z"
    quote: '{"ts": "2026-08-19T01:37:30.279Z", "message": "GET /products/1 -> 200", "request_id": "2c652fca0624", "status": 200}'
  - id: E16
    type: probe
    source: "scripts/probe.sh /health, request_id=konan-1787103716-37211 (re-probe at conclusion time)"
    quote: '{"status":"ok","uptime_seconds":297.79532733396627}'
  - id: E17
    type: metric
    source: "scripts/probe.sh /metrics, request_id=konan-1787103718-37217 (re-probe at conclusion time — counters identical to E11/E13, no recurrence)"
    quote: |
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      faultline_chaos_enabled 0
  - id: E18
    type: metric
    source: "scripts/probe.sh /metrics, request_id=konan-1787103482-37118 (baseline)"
    quote: 'process_max_rss_bytes 47267840'
gaps:
  - "No rotated log backups exist and only one startup marker is present, so process history before 2026-08-19T01:36:58Z is unavailable — the lab process is short-lived by design and this is the whole of its life."
  - "process_max_rss_bytes (E18) is a single snapshot, not a trend; with only ~5 minutes of process lifetime observed, sustained memory/CPU growth cannot be ruled out or confirmed either way."
  - "The actor and intent behind the chaos toggle (POST /chaos/enable at 01:37:02.808Z) are outside the investigator's surface by design — /chaos and scripts/scenario.sh are explicitly operator/eval-only per docs/lab.md, so who flipped it and why is unrecoverable from this seat."
usage:
  model: claude-sonnet-5
  tokens: 3487235
  wall_clock_seconds: 317
---

# Brief chaos-mode 503 episode on /products, self-resolved before handover

## Summary

**Root cause identified; no active incident.** The "noise earlier" the handover complaint
refers to was a config toggle, not a defect: `POST /chaos/enable` at 01:37:02.808Z armed
fault injection at `failure_rate=0.6` against random requests, producing three HTTP 503
responses — two on `GET /products`, one on `GET /products/1` — inside a 6-second window
(E3–E9). `POST /chaos/disable` at 01:37:09.162Z turned it back off. Every request since,
including a live re-probe taken at conclusion time (uptime 297.8s, E16/E17), has returned
200/201 with the 503 counters unchanged and `faultline_chaos_enabled` still 0. No unhandled
exceptions were logged or counted at any point (E12). Impact was small and brief: 3 failed
GETs, no failed orders, no user-facing outage ongoing. Confidence is high — the judge
validated this hypothesis against the full evidence set with no invalidating findings.

## Timeline (UTC)

- **01:36:58.916Z** — process start, only startup marker in the log (E1).
- **01:37:02.808Z** — `chaos_enabled`, `failure_rate=0.6`, `error_status=503` (E3) — the
  config-change marker.
- **01:37:03.867Z** — `GET /products` → 503, first failure (E4).
- **01:37:04.925Z** — `GET /products/2` → 200, a success inside the window (E5).
- **01:37:05.984Z** — `GET /products/1` → 503 (E6).
- **01:37:07.045Z** — `POST /orders` → 201, another success inside the window (E7).
- **01:37:08.102Z** — `GET /products` → 503, third and last failure (E8).
- **01:37:09.162Z** — `chaos_disabled` (E9) — window closes, 6.354s after onset.
- **01:37:29.221Z onward** — clean 200/201 traffic resumes and continues through the
  current log tail (E10).
- **01:42:56Z (approx, re-probe)** — live health/metrics check at conclusion: uptime
  297.8s, chaos still off, 503 counters unchanged, no exceptions (E16, E17).

## Investigation

1. **Baseline**: `/health` (E2) and `/metrics` (E11–E13, E18) snapshot, plus a full read
   of `lab/logs/app.log` (the only log file present — no rotation). Baseline already
   showed the complete chaos_enabled → chaos_failure(×3) → chaos_disabled sequence and a
   clean tail after it.
2. **Triage** — three lenses run in parallel (infra-process, interfaces,
   software-defect), each given only the lens file, the surface contract, the verbatim
   complaint, and the baseline summary:
   - *infra-process*: no restart/crash, no resource saturation, no latency
     degradation — one continuous process.
   - *interfaces*: 503s bounded exactly by the chaos_enabled/chaos_disabled markers;
     observed failure rate during the window (3/5 non-toggle requests = 60%) matches the
     configured `failure_rate=0.6`.
   - *software-defect*: no unhandled exceptions, no stack traces, no deterministic
     per-input failure (`/products/1` returned 200 both before and after the window).
   All three converged on the same explanation with no competing hypothesis raised, and
   the evidence was already deterministic — so this hypothesis skipped deep-dive per
   budget rules and went straight to judge.
3. **Judge** — one fresh adversarial-judge subagent, given only H1 and its verbatim
   evidence (no narrative). Verdict: **validated**. The judge checked for and rejected
   the alternatives it was asked to consider (coincidental code defect, restart hiding a
   crash, exceptions not being logged for this class) and confirmed the chaos_* event
   trail as first-party, direct evidence rather than inferred correlation. It flagged two
   minor gaps in how the statistical side-predictions were phrased (see Hypotheses below);
   neither affected the verdict.
4. **Post-judge verification** — re-ran `/health` and `/metrics` live before concluding
   to confirm the "right now" state the complaint asked about (E16, E17): still clean,
   ~5 minutes after the episode, no recurrence.

## Hypotheses

### H1 — chaos-mode config toggle (validated)

The three 503s are fault-injector output, not a code defect or infra failure: each is
immediately preceded by a `chaos_failure` log line sharing its `request_id` (E4, E6, E8),
bracketed by explicit `chaos_enabled` (E3) and `chaos_disabled` (E9) events. The observed
in-window failure rate (3 failures out of the 5 non-toggle requests logged in that
window — E4, E5, E6, E7, E8 are the complete set, confirmed by reading the full log file)
matches the configured `failure_rate=0.6` exactly (E11 vs. E3). `http_exceptions_total`
recorded zero entries throughout (E12), ruling out an unhandled-exception cause. Traffic
resumed clean immediately after disable (E10) and remained clean through a live re-probe
five minutes later (E16, E17).

The judge noted the same-route-and-input 200/503 contrast (E14, E6, E15) spans
before→during→after the window rather than two outcomes strictly inside it — the
window itself has no repeated route. This still functionally rules out a deterministic
per-input defect (the same input is fine on both sides of the failure), it just isn't the
literal "two outcomes inside one window" shape a stricter reading of the prediction would
want. Not disconfirming, just a phrasing gap; noted here rather than left silent.

## Safe next steps

- If this pattern recurs, correlate future `chaos_enabled`/`chaos_disabled` pairs against
  who/what is driving them — that identity is outside this investigator's read-only
  surface (see Gaps) but may be visible from wherever `scripts/scenario.sh` is invoked.
- Watch `process_max_rss_bytes` over a longer live window next time the process runs
  more than a few minutes; the current read is a single snapshot and cannot speak to
  sustained memory behavior.
- No action needed on the /products / /products/1 503s themselves — self-resolved,
  counters static, no exceptions, no repeat in ~5 minutes of subsequent observation.

## Gaps

- No rotated log backups and a single startup marker mean process history before
  2026-08-19T01:36:58Z is unavailable. In this lab the process is short-lived by design,
  so this is understood to be the whole of its observable life, not a truncated window.
- `process_max_rss_bytes` is one snapshot, not a trend; sustained resource growth over a
  longer runtime is neither confirmed nor ruled out.
- Who or what triggered `POST /chaos/enable` is unrecoverable from the investigator's
  surface — `/chaos` and `scripts/scenario.sh` are explicitly operator/eval-only per
  `docs/lab.md`, walled off from read-only investigation by design.
