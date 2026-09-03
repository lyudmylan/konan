---
konan_journal: 1
investigation:
  id: 2026-08-25-shop-down-process-exit
  trigger: "manual — /konan human-report (fingerprint human-1787689712, startsAt 2026-08-25T20:28:32Z, investigation start 2026-08-25T20:28:44Z, trigger latency 12 s)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-25T20:28:44Z
  concluded: 2026-08-25T20:47:34Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline server process [52108] exited with code 1 at 20:28:20.805Z, 0.5 s after serving an operator-surface GET /simulate/crash from unstamped local client 127.0.0.1:52840, and was never restarted, so nothing listens on 127.0.0.1:8000 and every user request is refused at TCP level."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The server process [52108] terminated itself (exit code 1) right after an operator-surface GET /simulate/crash and no process restarted afterwards; the port is closed, so requests are refused before any HTTP response can be produced."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E6, E7, E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "Injected degradation (chaos) or a failing dependency is returning gateway-shaped HTTP errors to users."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E9, E10]
  - id: H3
    statement: "The process is alive but saturated or hung, so user requests time out."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E5, E6, E8, E9]
  - id: H4
    statement: "The process died from an unhandled exception in application code."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E9]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id=konan-1787689736-52244 (2026-08-25 ~20:28:56Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000397s request_id=konan-1787689736-52244
  - id: E2
    type: probe
    source: "/metrics @ request_id=konan-1787689736-52250 (2026-08-25 ~20:28:56Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000191s request_id=konan-1787689736-52250
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:28:14.053Z"
    quote: |-
      {"ts": "2026-08-25T20:28:14.053Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [52108]"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:28:14.053Z"
    quote: |-
      {"ts": "2026-08-25T20:28:14.053Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:28:14.778Z"
    quote: |-
      {"ts": "2026-08-25T20:28:14.778Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "0da475ef0c36", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 19.559, "client": "127.0.0.1:52831"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:28:18.257Z"
    quote: |-
      {"ts": "2026-08-25T20:28:18.257Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "cadb1c738bce", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1.122, "client": "127.0.0.1:52836"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:28:20.304Z"
    quote: |-
      {"ts": "2026-08-25T20:28:20.304Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "aa45f5c20b94", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 0.944, "client": "127.0.0.1:52840"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:28:20.805Z (last line of the file)"
    quote: |-
      {"ts": "2026-08-25T20:28:20.805Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "aa45f5c20b94", "event": "crash", "delay": 0.5}
  - id: E9
    type: log
    source: "lab/logs/app.log whole-file inventory (wc -l, ls lab/logs/) read 2026-08-25T20:44:19Z"
    quote: |-
            14 lab/logs/app.log
  - id: E10
    type: probe
    source: "/health @ request_id=konan-1787690733-52378 (2026-08-25 ~20:45Z, interfaces triage lens)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000187s request_id=konan-1787690733-52378
  - id: E11
    type: probe
    source: "/metrics @ request_id=konan-1787690733-52384 (2026-08-25 ~20:45Z, interfaces triage lens)"
    quote: |-
      -- HTTP 000 in 0.000180s request_id=konan-1787690733-52384
gaps:
  - "No metrics snapshot: /metrics is unreachable (E2, E11), so process_uptime_seconds, process_max_rss_bytes, http_requests_total and faultline_chaos_enabled could not be read; the exit is argued from the log and TCP refusals only."
  - "No process-table observation: the surface contract (docs/lab.md) exposes no ps/lsof view and lab/server.out is outside the investigator's surface, so the exit is evidenced by the process's own last log line (E8) plus persistent connection refusal (E1, E10), not by an observed exit status."
  - "No telemetry before 2026-08-25T20:28:14.053Z: app.log has 14 lines and no rotated backups (E9), so the complaint's 'fine ten minutes ago' and any earlier restarts cannot be checked."
  - "The identity of client 127.0.0.1:52840 that issued GET /simulate/crash (E7) cannot be determined from telemetry; it carries no konan- request id, so it was not the investigator."
  - "Software-defect triage lens deliberately not spawned: the whole 14-line log (E9) contains no unhandled_exception event, no stack, and no 5xx, and the process is not running; covered instead by hypothesis H4 (invalidated by the judge)."
usage:
  model: claude-fable-5
  tokens: 627860
  wall_clock_seconds: 1130
---

# Shop fully down: server process exited after an operator-surface /simulate/crash and was not restarted

## Summary

**Verdict: root cause identified (infra-process).** The faultline server process
`[52108]` served `GET /simulate/crash` at `20:28:20.304Z` from an unstamped local client
and, 0.5 s later, logged `crashing now: exiting with code 1` (E7, E8). That is the last
line in the log; no restart marker follows (E9). Since then nothing listens on
`127.0.0.1:8000`: every probe is refused at TCP level after 0 ms (`HTTP 000`, E1, E2,
E10, E11), which is exactly why users see no page at all — there is no process to send
an error page. Impact: total outage of the business surface (all routes) since
`20:28:20.805Z`, continuous through at least `~20:45Z`. Confidence: high — the
mechanism is deterministic, the log names the exit, and the prediction (port closed,
silent log, no second startup) held on two probe passes 17 minutes apart. The
investigator's own probes never reached the application (no `konan-` id in the log), so
user impact is not investigator-induced.

## Complaint

Complaint object (verbatim, as synthesized by the `/konan` adapter):

```json
{
  "source": "human",
  "fingerprint": "human-1787689712",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-08-25T20:28:32Z"
}
```

Investigation start: `2026-08-25T20:28:44Z` (trigger latency 12 s). No severity was
stated, so none was recorded.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 20:28:14.053Z | Server process `[52108]` starts; `faultline 0.1.0 started` | E3, E4 |
| 20:28:14.778Z – 20:28:18.257Z | Healthy traffic: 6 requests, all 200/201, 1–20 ms | E5, E6 |
| 20:28:20.304Z | `GET /simulate/crash -> 200` from client `127.0.0.1:52840` (change marker; operator surface) | E7 |
| 20:28:20.805Z | CRITICAL `crashing now: exiting with code 1` — last log line ever | E8 |
| 20:28:32Z | Human complaint raised (`startsAt`) | — |
| 20:28:44Z | Investigation starts | — |
| ~20:28:56Z | `/health`, `/metrics` → connection refused, `HTTP 000` | E1, E2 |
| ~20:45Z | `/health`, `/metrics` still refused, `HTTP 000` | E10, E11 |

No `chaos_enabled`/`chaos_disabled`, `unhandled_exception`, or second `startup` line
exists anywhere in the file (E9).

## Investigation

- **Baseline** (20:28:44Z–20:44:19Z): both probes refused (E1, E2); the full log is
  14 lines with no backups (E9) — 5 startup lines (E3, E4 and three more uvicorn lines),
  7 traffic lines (6 requests + one `order_created`) all 200/201, then E7 and E8.
- **Triage** — two lenses in parallel, each blind to the other: *infra-process* and
  *interfaces*. The *software-defect* lens was not spawned (see Gaps). Both lenses
  returned the same three facts: one startup, one operator-triggered exit, zero restarts;
  listener gone (TCP refusal, not HTTP error); metrics surface unavailable. The interfaces
  lens re-probed at ~20:45Z and confirmed the outage is continuous (E10, E11).
- **Deep-dive** — skipped: triage evidence for H1 was deterministic and complete
  (the log names the exit, the prediction was already tested twice).
- **Judge** (fresh subagent, evidence quotes only): H1 validated; H2, H3, H4
  invalidated. The judge noted that no ledger item observes the process table — recorded
  as a gap, it is outside the surface contract — and flagged a line-count mismatch in my
  first inventory summary, which was an arithmetic error in the summary, not a hidden
  line: the complete 14-line file was read verbatim (E9) and is itemized above.

## Hypotheses

### H1 — process exited after /simulate/crash, never restarted (infra-process) — validated

For: E3/E4 place a single startup at 20:28:14Z; E7 shows the operator-surface request and
E8, 0.501 s later, the self-announced exit with code 1 under the same request id; E9 shows
nothing after E8 and no second startup; E1/E2 and E10/E11 show TCP refusal after 0 ms on
two paths, 17 minutes apart, matching the prediction "port closed, silent log".
Against: none.

### H2 — chaos injection or dependency failure (interfaces) — invalidated

A chaos or gateway path must return an HTTP status; all probes are TCP refusals with
`HTTP 000` (E1, E2, E10). The whole file has no `chaos_*` event and only 200/201
statuses (E9).

### H3 — process alive but saturated/hung (load-saturation) — invalidated

A hung process keeps its socket and accepts connections; refusal after 0 ms (E1) is not a
timeout. Durations were 19.6 ms and 1.1 ms with no degradation up to the last request
(E5, E6), and E8 records a deliberate exit, not a stall.

### H4 — unhandled exception in application code (software-defect) — invalidated

E8 is emitted by logger `faultline.simulate`, event `crash`, tied to the E7 request on
`/simulate/crash`: an operator-surface action doing what its name says. No
`unhandled_exception` line or stack exists in the file (E9).

## Safe next steps

Read-only suggestions only:

- Confirm from the host side (outside konan's surface) that no process holds
  `127.0.0.1:8000` and that pid `52108` is gone — this is the one missing direct
  observation the judge named.
- Read `lab/server.out` (operator surface) for the process's stdout at exit.
- Establish who or what at `127.0.0.1:52840` issued `GET /simulate/crash` at
  `20:28:20.304Z`; it is unstamped, so it was not the investigator.
- Check whether a supervisor is expected to restart the service; the log shows none did
  for at least 17 minutes.

## Gaps

- **Metrics**: `/metrics` unreachable (E2, E11); no gauges or counters could be read.
- **Process table**: not in the surface contract; the exit is evidenced by the process's
  own last line and persistent refusal, not by an observed exit status.
- **History before 20:28:14Z**: none exists (E9), so the reporter's "fine ten minutes ago"
  and any prior restarts cannot be checked.
- **Actor behind the crash request**: client `127.0.0.1:52840` is not identifiable from
  telemetry.
- **Software-defect lens** not spawned, on the evidence that the full log holds no
  exception, stack, or 5xx and the process is not running; the domain was still tested
  as H4 and invalidated by the judge.
