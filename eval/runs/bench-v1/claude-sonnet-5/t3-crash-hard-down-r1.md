---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-total-outage-crash
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-19T03:16:31Z
  concluded: 2026-08-19T03:21:24Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A GET request to the operator-surface route /simulate/crash triggered a deliberate process exit (code 1) in the faultline server at 03:16:18.783Z, taking down the only listener on port 8000 with no auto-restart, so every subsequent request — health, business, and metrics alike — fails at the TCP connect stage, matching the reported total outage with no error page."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The faultline process crashed (deliberate process exit with code 1, triggered by a GET /simulate/crash request) at 2026-08-19T03:16:18.783Z and did not restart; every subsequent request fails at the TCP connect stage because nothing listens on port 8000."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "A gateway/config/deploy change or probabilistic dependency degradation (interfaces domain) caused the outage."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E7, E8]
  - id: H3
    statement: "An unhandled application exception or data-dependent code defect (software-defect domain) crashed the process."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:16:12.302Z"
    quote: '{"ts": "2026-08-19T03:16:12.302Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:16:13.028Z"
    quote: '{"ts": "2026-08-19T03:16:13.028Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "be1b745b987a", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 12.715}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:16:16.222Z"
    quote: '{"ts": "2026-08-19T03:16:16.222Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "d82199625136", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.793}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:16:18.281Z"
    quote: '{"ts": "2026-08-19T03:16:18.281Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "24624a1dad8a", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.441}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:16:18.783Z (last line in file)"
    quote: '{"ts": "2026-08-19T03:16:18.783Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "24624a1dad8a", "event": "crash", "delay": 0.5}'
  - id: E6
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1787109418-41423"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000206s request_id=konan-1787109418-41423"
  - id: E7
    type: probe
    source: "scripts/probe.sh /metrics, request_id konan-1787109441-41434"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000194s request_id=konan-1787109441-41434"
  - id: E8
    type: probe
    source: "scripts/probe.sh /products, request_id konan-1787109442-41440"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000207s request_id=konan-1787109442-41440"
  - id: E9
    type: probe
    source: "scripts/probe.sh /health, independent triage-lens agent, request_id konan-1787109551-41507"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000176s request_id=konan-1787109551-41507"
gaps:
  - "OS-level process state (ps/pgrep output, supervisor or container logs) was not available on the investigator's read-only surface (docs/lab.md grants only scripts/probe.sh and lab/ log reads); process death is inferred from the app's own crash log line (E5) plus repeated TCP-level connection refusals (E6-E9), not observed directly at the OS level. The adversarial judge assessed this gap as not verdict-changing: sub-millisecond connect failures already rule out an alive-but-slow process."
  - "scripts/lab.sh status sits outside the pre-approved probe/log surface and requires an interactive permission prompt; that prompt was not resolved during this investigation, so process-manager status was not used as evidence, per the read-only lab boundary."
  - "No rotated log backups (app.log.1-.3) exist — the current process's entire lifetime was roughly 6.5 seconds (startup to crash), so no earlier history could be checked for a prior pattern of crashes or restarts."
usage:
  model: claude-sonnet-5
  tokens: 2140394
  wall_clock_seconds: 293
---

# Shop total outage: /simulate/crash triggered an unrecovered process exit

## Summary

**Root cause identified.** The complaint ("shop completely down for everyone, not even
an error page") matches a full process crash, not an application error. At
2026-08-19T03:16:18.281Z a `GET /simulate/crash` request was served 200 (E4); 0.502s
later — matching its own logged `delay: 0.5` — the process logged a CRITICAL
self-terminate line and exited with code 1 (E5), the last line ever written to
`lab/logs/app.log`. No restart followed. Investigator probes to `/health`, `/metrics`,
and `/products` all fail at the TCP connect stage (`curl: (7) ... Couldn't connect to
server`, HTTP 000 — E6, E7, E8), reproduced independently by a second agent (E9). This
is why users see no error page at all: nothing is listening on port 8000 to render one.
Three independent triage lenses (infra-process, interfaces, software-defect) converged
on the same read and an adversarial judge validated the hypothesis, with one accepted
residual gap (no OS-level process confirmation was reachable on this read-only surface).

## Timeline

- `03:16:12.302Z` — process startup (E1).
- `03:16:13.028Z`–`03:16:16.222Z` — six healthy requests, all 200/201, sub-13ms
  durations; last known-good is `GET /orders -> 200` at `03:16:16.222Z` (E2, E3).
- `03:16:18.281Z` — `GET /simulate/crash -> 200`, request_id `24624a1dad8a` (E4).
- `03:16:18.783Z` — CRITICAL `crashing now: exiting with code 1`, same request_id,
  `delay: 0.5` (E5). Last line in the log; no subsequent startup marker.
- `~03:17:00Z` onward — every investigator probe against `/health`, `/metrics`,
  `/products` returns TCP connection-refused, not an HTTP status (E6, E7, E8, E9).

## Investigation

**Baseline:** read `lab/logs/app.log` in full (15 lines) and probed `/health`,
`/metrics`, `/products` — all three connection-refused. The log tail already showed a
single, complete, self-consistent story (startup → healthy traffic → crash-trigger
request → CRITICAL exit), so the baseline itself was near-decisive.

**Triage (parallel, all three lenses — complaint was vague and impact severe, so no
domain was excluded going in):**
- *infra-process*: confirmed a clean, unrecovered process death (no restart-loop
  signature), confirmed TCP-level refusal (not degradation), confirmed the crash
  request/exit pair is tightly causal (0.502s gap matches the logged 0.5s delay).
- *interfaces*: found no gateway-shaped statuses, no config/flag/deploy markers, and
  an instantaneous TCP-level cutover — ruled out its own domain, pointed at
  infra-process.
- *software-defect*: found zero exceptions, zero 5xx, and identified the crash as a
  deliberate self-terminate call (not a thrown exception or data-dependent failure) —
  ruled out its own domain, pointed at infra-process.

All three lenses converged; evidence was already deterministic and complete, so
per-protocol the deep-dive round was skipped and the hypothesis list went straight to
judgment.

**Judge:** validated H1 against the verbatim evidence above, invalidating the
alternative interfaces- and software-defect-domain explanations. It flagged one gap
(no direct OS-level process confirmation) and assessed it as not verdict-changing,
given the sub-millisecond TCP refusals already rule out a merely slow/alive process.

## Hypotheses

### H1 — process crash via /simulate/crash (validated)

The crash-trigger request and the CRITICAL exit line share `request_id`
`24624a1dad8a` and are 0.502s apart, matching the logged `delay: 0.5` exactly (E4, E5).
No second startup marker follows it, and three independent probes across two agents
all fail at the TCP connect stage rather than returning any HTTP status (E6-E9) — the
signature of nothing listening on the port, not of an overloaded or degraded server.

### H2 — gateway/config/interfaces cause (invalidated)

No config, flag, or deploy marker appears anywhere in the log, and the failure mode is
TCP refusal, not a gateway-shaped 502/503/504 or a probabilistic partial-failure rate —
evidence against a gateway or configuration-drift explanation (E4, E5, E6, E7, E8).

### H3 — software defect / unhandled exception (invalidated)

The crash line is a deliberate CRITICAL log message from `faultline.simulate` naming
its own exit code, not an unhandled exception — no `exception_type` or `stack` field
appears anywhere in the log, and the trigger affected every subsequent request
uniformly rather than a specific input (E5).

## Safe next steps

- Re-probe `/health` periodically (read-only) to detect if/when the process comes back
  without investigator intervention — this investigation performs no restarts.
- If process-manager or supervisor logs become reachable through a future surface-contract
  update, capture them to close the OS-level confirmation gap noted above.
- Once the process is back, compare a fresh `/metrics` `process_uptime_seconds` reading
  against this incident's timestamps to confirm no earlier, unlogged restarts occurred.

## Gaps

- OS-level process state (`ps`/`pgrep`, supervisor/container logs) was not reachable on
  the investigator's surface (`docs/lab.md`); the process-death conclusion rests on the
  app's own crash log line plus repeated TCP-level connection refusals, judged
  sufficient but not a direct OS-level observation.
- `scripts/lab.sh status` falls outside the pre-approved probe/log surface and needs an
  interactive permission prompt; it was not resolved during this investigation and so
  was not used as evidence.
- No rotated log backups exist for this process instance (its whole life was ~6.5
  seconds), so no earlier crash/restart history could be checked.
