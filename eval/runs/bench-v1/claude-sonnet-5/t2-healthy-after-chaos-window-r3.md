---
konan_journal: 1
investigation:
  id: 2026-08-19-routine-handover-chaos-toggle
  trigger: manual
  complaint: |-
    {"source": "human", "fingerprint": "human-1787104523", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."}, "startsAt": "2026-08-19T01:55:23Z"}
  started: "2026-08-19T01:55:29Z"
  concluded: "2026-08-19T02:00:28Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The 'noise' referenced in the complaint was a chaos-mode toggle (POST /chaos/enable -> POST /chaos/disable) that produced a bounded ~6.35s window of probabilistic 503s (failure_rate 0.6) across /products, /products/2, and POST /orders shortly after process startup; it fully self-resolved and no active incident exists at check time."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
latent_findings: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:42.641Z (line 3)"
    quote: '{"ts": "2026-08-19T01:54:42.641Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:46.529Z (line 10)"
    quote: '{"ts": "2026-08-19T01:54:46.529Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "749dbc732fcc", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:47.589Z (line 13, paired with chaos_failure line, request_id 84053946c212)"
    quote: '{"ts": "2026-08-19T01:54:47.589Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "84053946c212", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.284, "client": "127.0.0.1:54549"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:48.646Z (line 15, request_id c46443a3cb73)"
    quote: '{"ts": "2026-08-19T01:54:48.646Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "c46443a3cb73", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.279, "client": "127.0.0.1:54550"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:50.766Z (line 18, request_id dc1cdf3ddb7d)"
    quote: '{"ts": "2026-08-19T01:54:50.766Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "dc1cdf3ddb7d", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.306, "client": "127.0.0.1:54552"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:51.822Z (line 20, request_id 03cd99e5e8d6)"
    quote: '{"ts": "2026-08-19T01:54:51.822Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "03cd99e5e8d6", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.268, "client": "127.0.0.1:54553"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:54:52.880Z (line 21)"
    quote: '{"ts": "2026-08-19T01:54:52.880Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "8ba95345fc67", "event": "chaos_disabled"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:55:15.055Z-01:55:15.056Z — first order placed after chaos_disabled (E7)"
    quote: '{"ts": "2026-08-19T01:55:15.055Z", "message": "order created", "request_id": "24224b63a069", "event": "order_created", "order_id": 1, "product_id": 2, "quantity": 1, "total_price": 23.0} / {"ts": "2026-08-19T01:55:15.056Z", "message": "POST /orders -> 201", "request_id": "24224b63a069", "status": 201}'
  - id: E9
    type: probe
    source: "GET /health @ request_id konan-1787104555-37847 (2026-08-19T01:55:55Z)"
    quote: |-
      {"status":"ok","uptime_seconds":73.10993183404207}
      -- HTTP 200 in 0.001677s request_id=konan-1787104555-37847
  - id: E10
    type: metric
    source: "GET /metrics @ request_id konan-1787104557-37853 (2026-08-19T01:55:57Z)"
    quote: 'faultline_chaos_enabled 0'
  - id: E11
    type: log
    source: "lab/logs/app.log — full-file grep for '\"status\": 503', 31 lines total in file (spans process startup 01:54:42Z through 01:57:01Z)"
    quote: |-
      $ grep -c '"status": 503' lab/logs/app.log
      4
      (matching line numbers 13, 15, 18, 20 — exactly E3-E6; no 503 appears before chaos_enabled (E2, line 10) or after chaos_disabled (E7, line 21))
  - id: E12
    type: log
    source: "lab/logs/app.log — full-file grep for chaos toggle events"
    quote: |-
      $ grep -c '"event": "chaos_enabled"' lab/logs/app.log
      1
      $ grep -c '"event": "chaos_disabled"' lab/logs/app.log
      1
  - id: E13
    type: log
    source: "lab/logs/app.log — full-file grep for unhandled exceptions"
    quote: |-
      $ grep -c '"event": "unhandled_exception"' lab/logs/app.log
      0
  - id: E14
    type: log
    source: "lab/logs/app.log — full-file grep for process startup markers"
    quote: |-
      $ grep -c '"event": "startup"' lab/logs/app.log
      1
gaps:
  - "The identity of the client that triggered chaos_enabled/chaos_disabled (client 127.0.0.1:54548 / 127.0.0.1:54554, E2/E7) cannot be attributed beyond 'not investigator-stamped' — request logs carry no auth/operator-identity field, so whether this was the eval harness's scenario.sh or another operator cannot be distinguished from telemetry alone."
  - "No rotated log backups exist on disk (lab/logs/ contains only app.log) and the current file's single startup marker (E14) covers the process's full 75+-second lifetime — if the complaint's 'earlier' referred to something before this process started, it left no telemetry and could not be checked."
usage:
  model: claude-sonnet-5
  tokens: 2026426
  wall_clock_seconds: 299
---

# Routine handover check: earlier "noise" traced to a self-resolved chaos toggle, no active incident

## Summary

**Verdict: no active incident.** The service is healthy at check time: `/health` returns
`200 ok`, `/metrics` shows `faultline_chaos_enabled 0` and zero exceptions, and every
request since 01:54:52.880Z has succeeded. The "noise" the complaint referred to is fully
explained and closed: chaos mode was toggled on (`failure_rate=0.6`, `error_status=503`)
at 01:54:46.529Z, produced four 503s spread across `/products`, `/products/2`, and
`POST /orders` over ~6.35 seconds, then was toggled off at 01:54:52.880Z. All traffic
since — including a full order placed and read back — has been clean. A full-file grep
confirms these four 503s are the *only* 503s in the entire log, and the enable/disable
pair occurs exactly once, so nothing outside this bounded window is unaccounted for.
Confidence: high — the mechanism is directly instrumented (explicit `chaos_enabled`/
`chaos_failure`/`chaos_disabled` log events), not inferred.

## Timeline (all 2026-08-19, UTC)

- `01:54:42.641Z` — process startup (E1), single marker in the log — this is the entire
  lifetime available for inspection.
- `01:54:46.529Z` — chaos mode enabled, `failure_rate=0.6`, `error_status=503` (E2).
- `01:54:47.589Z`–`01:54:51.822Z` — four chaos-injected 503s: `GET /products` (E3),
  `GET /products/2` (E4), `POST /orders` (E5), `GET /products` again (E6).
- `01:54:52.880Z` — chaos mode disabled (E7).
- `01:55:12.939Z` onward — traffic resumes clean; an order is placed and confirmed
  (E8), `GET /orders` and further `/products/*` reads all return 200.
- `01:55:55Z`–`01:55:57Z` — investigator baseline probes: `/health` 200 (E9), `/metrics`
  200 showing chaos off (E10).
- `01:55:5x`–`01:57:01Z` — full-file greps (E11–E14) confirm the window is the complete
  and only anomaly in the log.

## Investigation

1. **Baseline** — `/health`, `/metrics`, and the full log tail (only 31 lines exist,
   covering the whole process lifetime) were read. The chaos episode was already visible
   in the baseline log tail.
2. **Triage** — three lenses (infra-process, interfaces, software-defect) ran in
   parallel against the baseline, each blind to the others. All three independently
   converged on the same explanation: a bounded chaos toggle, not a process crash, not a
   code defect, not an ongoing dependency issue. No lens reported a competing hypothesis.
3. **Deep-dive** — skipped. The triage evidence was already deterministic (explicit
   `chaos_enabled`/`chaos_failure`/`chaos_disabled` event markers directly named the
   mechanism), so H1 went straight to judgment rather than a re-proving deep-dive.
4. **Judge** — first pass returned **inconclusive**: the cited evidence was a sample (a
   5-line post-recovery excerpt, four named failures) rather than a proof that *no* 503s
   or toggle events existed outside the cited window. The judge specified the exact
   check that would settle it: a full-file count of every 503 and every chaos toggle
   event.
5. **Round 2** — ran that exact grep against the complete `lab/logs/app.log` (E11–E14):
   exactly 4 total 503s in the file, all four matching the already-cited lines; exactly
   one `chaos_enabled` and one `chaos_disabled`; zero `unhandled_exception` events; one
   `startup` marker. This closes the gap the judge identified — H1 validated.

## Hypotheses

### H1 — chaos-mode toggle, self-resolved (validated)

The complaint's "noise" was chaos mode being switched on then off shortly after process
start, producing four probabilistic 503s across three routes over ~6.35 seconds (E2–E7).
Evidence for: the causal chain is directly instrumented, not inferred — each
`chaos_failure` line pairs 1:1 by `request_id` with a 503 access line (E3–E6), bounded on
both sides by explicit toggle events (E2, E7). The full-file grep (E11) proves these four
are the *only* 503s anywhere in the log — nothing failed before the toggle or after it.
Current state confirms resolution: `faultline_chaos_enabled 0` (E10), a full order
lifecycle succeeding post-recovery (E8), and zero exceptions ever logged (E13). No
evidence against.

The client that triggered the toggle (127.0.0.1:54548/54554) is not investigator-stamped
(investigator probes carry a `konan-` request-id prefix; these do not), so this was not
the investigation's own traffic — consistent with an eval/operator action rather than a
target-side defect.

## Safe next steps

- If chaos-toggle windows like this should generate their own alert (rather than surfacing
  only as word-of-mouth "noise" with no filed report), that is a detector/alerting-coverage
  question for the owning team — read-only telemetry alone can't say why no alert fired.
- Nothing on the target needs remediation: no code defect, no resource exhaustion, no
  ongoing dependency failure was found.

## Gaps

- The identity of whoever/whatever toggled chaos mode cannot be resolved past "not the
  investigator" — request logs carry no operator-identity field.
- No rotated log backups exist; the current log's one startup marker covers the full
  process lifetime, so if "earlier" meant before this process started, that period left
  no telemetry to check.
