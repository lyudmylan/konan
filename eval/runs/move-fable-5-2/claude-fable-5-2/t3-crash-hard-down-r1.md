---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-down-process-exit
  trigger: 'manual — /konan, human profile. Complaint object: {"source": "human", "fingerprint": "human-1794756119", "labels": {"alertname": "human-report"}, "annotations": {"summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."}, "startsAt": "2026-11-15T15:21:59Z"}. Investigation start 2026-11-15T15:22:06Z; trigger latency 7 s.'
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-15T15:22:06Z
  concluded: 2026-11-15T15:25:24Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The target process announced an exit with code 1 at 2026-11-15T15:21:51.537Z, 0.5 s after a non-investigator request to its crash operator endpoint (GET /simulate/crash), and nothing restarted it by 15:23:52Z; with no listener on 127.0.0.1:8000, every request is refused at connect."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The target process exited (announced exit code 1) at 2026-11-15T15:21:51.537Z after a request to the target's crash operator endpoint, and nothing restarted it; no listener exists on the port, so every request is refused."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The process is alive but hung: it holds the port and does not serve."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3, E8, E9, E10]
  - id: H3
    statement: "The process is alive and serves, but the network path between clients and the process is broken (wrong address or port, a blocked path)."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E1, E2, E3]
    evidence_against: [E5, E8, E10]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794756141-4799 (about 2026-11-15T15:22:21Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000176s request_id=konan-1794756141-4799
  - id: E2
    type: probe
    source: "/metrics, request id konan-1794756141-4804 (about 2026-11-15T15:22:21Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000182s request_id=konan-1794756141-4804
  - id: E3
    type: probe
    source: "/products, request id konan-1794756142-4809 (about 2026-11-15T15:22:22Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000192s request_id=konan-1794756142-4809
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:21:45.046Z"
    quote: '{"ts": "2026-11-15T15:21:45.046Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:21:45.046Z"
    quote: '"ts": "2026-11-15T15:21:45.046Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:21:48.977Z"
    quote: '{"ts": "2026-11-15T15:21:48.977Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "4d851881b04d", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.841, "client": "127.0.0.1:53665"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:21:51.035Z"
    quote: '{"ts": "2026-11-15T15:21:51.035Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "7e50e2432e20", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.505, "client": "127.0.0.1:53666"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:21:51.537Z"
    quote: '{"ts": "2026-11-15T15:21:51.537Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "7e50e2432e20", "event": "crash", "delay": 0.5}'
  - id: E9
    type: probe
    source: "/health, request id konan-1794756193-4839 (about 2026-11-15T15:23:13Z, triage lens probe)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000196s request_id=konan-1794756193-4839
  - id: E10
    type: probe
    source: "/health, request id konan-1794756231-4870 (about 2026-11-15T15:23:51Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000191s request_id=konan-1794756231-4870
gaps:
  - "No metrics snapshot: /metrics refused the connection (E2), so process_uptime_seconds, process_max_rss_bytes, and the request and exception counters were never read; a resource problem before the exit is not excluded by a gauge."
  - "The absence of the process is inferred, not observed: a process listing and a supervisor record are outside the surface contract. The exit code is the process's own announcement (E8), not an observed exit status."
  - "The sender of the crash request is not on the surface: the log shows only client 127.0.0.1:53666 and an unstamped request id (E7)."
  - "Why nothing restarted the process is not visible; no supervisor appears on the surface. 'Not restarted' holds only up to 2026-11-15T15:23:52Z."
  - "The complaint's 'fine ten minutes ago' cannot be confirmed or denied: the log starts at 2026-11-15T15:21:45.045Z and no backup files exist."
  - "The software-defect lens was not spawned: the baseline excluded its domain (the whole 14-line log has no unhandled_exception event and no 5xx access line). This is an accepted blind spot."
  - "The log event value 'crash' (E8) is not in the event list of docs/lab.md; the reading of that line rests on its message text."
usage:
  model: claude-fable-5-2
  tokens: 939791
  wall_clock_seconds: 198
---

# Shop down: the faultline process exited and was not restarted

## Summary

**Root cause identified (infra-process, `process-crashed`).** The target process
announced "crashing now: exiting with code 1" at 2026-11-15T15:21:51.537Z (E8). The
announcement carries the request id of a `GET /simulate/crash` request that arrived
0.5 s before it (E7); that request id has no `konan-` stamp, so it is not investigator
traffic. No startup line follows the exit line, and the exit line was still the last
line of the log at 15:23:52Z. Five probes on three paths between 15:22:21Z and
15:23:51Z failed at connect in about 0.2 ms each (E1, E2, E3, E9, E10): no listener
exists on 127.0.0.1:8000, the address the process had announced (E5).

Impact: total. Every request is refused before HTTP, which matches the complaint's
"not even an error page". Before the exit the service was healthy: all 7 access lines
of the log carry status 200 or 201 (last business request: E6).

Confidence: high for the mechanism (exit, no restart, connection refused). Two limits
remain: the exit code is announced by the process and not observed from outside, and
"not restarted" is known only up to 15:23:52Z.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 15:21:45.046 | Startup marker, the only one in the log; listener announced on 127.0.0.1:8000 | E4, E5 |
| 15:21:45.772 – 15:21:48.977 | 6 business and health requests, all 200 or 201 | E6 |
| 15:21:51.035 | `GET /simulate/crash -> 200`, request id `7e50e2432e20`, not investigator traffic | E7 |
| 15:21:51.537 | CRITICAL "crashing now: exiting with code 1", same request id; last line of the log | E8 |
| 15:21:59 | Complaint raised (`startsAt`) | — |
| 15:22:06 | Investigation start | — |
| 15:22:21 – 15:22:22 | `/health`, `/metrics`, `/products`: connection refused | E1, E2, E3 |
| 15:23:13 | `/health`: connection refused (triage lens) | E9 |
| 15:23:51 | `/health`: connection refused; log unchanged at 15:23:52 | E10 |

## Investigation

**Complaint block.** Complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794756119",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-15T15:21:59Z"
}
```

Investigation start: 2026-11-15T15:22:06Z. Trigger latency: 7 s. The reporter stated no
severity, so the object carries none.

**Setup.** `KONAN_ADAPTER` was unset; the surface contract is `docs/lab.md`.

**Baseline.** Three probes (`/health`, `/metrics`, `/products`) all failed with
connection refused (E1–E3). No metrics snapshot could be taken. `lab/logs/app.log` held
14 lines from 15:21:45.045Z to 15:21:51.537Z, with no backup files. `lab/server.out`
held the same 14 lines. A "normal" reference exists only inside those 6.5 s: 7 access
lines, all 200 or 201, durations 0.8 ms to 12.5 ms.

**Triage.** Two lenses ran in parallel, each blind to the other: infra-process and
interfaces. The software-defect lens was not spawned (see Gaps). Both lenses
independently found the same exit line (E8) and its trigger request (E7), a sharp and
total onset, and no restart. The interfaces lens classed the mechanism as
`infra-process`, not its own domain. The infra-process lens added one later probe (E9).

**Deep-dive.** Skipped. The triage evidence for H1 was deterministic and complete, so
H1 went straight to the judge with one confirming probe (E10) and a second read of the
log.

**Judge.** One fresh judge saw only the hypothesis list and the verbatim evidence.
Verdicts: H1 validated, H2 invalidated, H3 invalidated. The judge set two wording
limits on H1, both adopted here: the exit code is announced, not observed; "not
restarted" holds only to 15:23:52Z. The judge also noted that E1–E3 do not
discriminate between H1 and H3, and that H3 falls on E5, E8, and the immediate failure
mode.

**Budget.** One triage round, zero deep-dive agents, one judge round.

## Hypotheses

### H1 — process exited and was not restarted (validated)

E7 and E8 share request id `7e50e2432e20`; the 502 ms between them matches
`"delay": 0.5` in E8. E4 is the only startup line and precedes the exit. E8 is the last
line of the log. All five probes fail at connect in about 0.2 ms (E1, E2, E3, E9, E10),
which is the signature of a port with no listener. E6 shows the service answered
normally 2.6 s before the exit, so the onset is sharp. No evidence against was found.

Cause id: `process-crashed` — the process exited once and was not restarted. The exit
was requested through an operator endpoint of the target; that is the instance, and the
mechanism of the outage is the exit without restart.

### H2 — process alive but hung (invalidated)

A hung process that holds the port accepts the connection or lets it time out. Every
probe was refused immediately (E1, E2, E3, E9, E10). The hypothesis also predicts no
exit line; E8 is one.

### H3 — network path broken, process alive (invalidated)

The probes target 127.0.0.1:8000, the same address the process announced (E5), and the
failure is an immediate refusal, not a timeout (E10). E8 contradicts "alive and
serves". E1–E3 are listed for H3 only because a refused connection is what the
hypothesis must explain; they fit H1 equally.

## Safe next steps

Read-only suggestions only.

- Read the process listing or the supervisor record on the host for the server process
  `[4708]` named in the first log line, to observe the exit status directly.
- Find the sender of the request `7e50e2432e20` in operator-side records; the target's
  log shows only a loopback client.
- After the operator brings the service back, verify with `scripts/probe.sh /health`,
  a new `startup` line in `lab/logs/app.log`, and a low `process_uptime_seconds` on
  `/metrics`.
- Then read `/metrics` once for a counter baseline; none exists from this
  investigation.

## Gaps

- **No metrics.** `/metrics` was refused (E2). Uptime, memory, request, and exception
  counters were never read. The clean latencies and statuses before the exit argue
  against a resource problem, but no gauge excludes it.
- **Process absence is inferred.** A process listing and a supervisor record are
  outside the surface contract. The exit code comes from the process's own log line.
- **Sender of the crash request unknown.** The surface shows client `127.0.0.1:53666`
  and an unstamped request id only.
- **No restart explanation.** No supervisor is visible. "Not restarted" is known up to
  15:23:52Z.
- **"Fine ten minutes ago" unverified.** The log covers 6.5 s and has no backups. The
  complaint was raised 8 s after the exit line.
- **Software-defect lens not spawned.** The whole log was 14 lines and held no
  `unhandled_exception` event and no 5xx access line, so the baseline excluded that
  domain. A defect that leaves no trace in those lines stays unseen.
- **Contract drift.** The event value `crash` is absent from the event list of
  `docs/lab.md`.
- **Token total not captured.** The session could not read its own total; the three
  subagents reported 99,762 tokens together.
