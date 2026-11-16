---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-down-process-exit
  trigger: "manual (/konan, human profile); complaint object: source=human, fingerprint=human-1794783112, labels.alertname=human-report, no severity stated, startsAt=2026-11-15T22:51:52Z; investigation start 2026-11-15T22:52:04Z; trigger latency 12 s"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-15T22:52:04Z
  concluded: 2026-11-15T22:55:29Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The target process announced an exit with code 1 at 2026-11-15T22:51:42.867Z, 0.5 s after a request to its crash-simulation path, and no restart followed; no process listens on the port, so every request is refused at connect."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The target process exited with code 1 at 2026-11-15T22:51:42.867Z, 0.5 s after a request to its crash-simulation path, and nothing restarted it; no process listens on the port, so every request is refused at connect."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E4, E5, E6, E7, E8, E9, E10, E12]
    evidence_against: []
  - id: H2
    statement: "The target process is alive but hung: it holds the port and does not serve."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E9, E10]
  - id: H3
    statement: "A defect in the target's own code (an unhandled exception on some input) took the service down."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E3, E11, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:51:36.354Z"
    quote: '{"ts": "2026-11-15T22:51:36.354Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [26432]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:51:36.354Z"
    quote: '{"ts": "2026-11-15T22:51:36.354Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:51:40.305Z"
    quote: '{"ts": "2026-11-15T22:51:40.305Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "650117fa5789", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.858, "client": "127.0.0.1:57193"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:51:42.365Z"
    quote: '{"ts": "2026-11-15T22:51:42.365Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "00fd1d1796c9", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.222, "client": "127.0.0.1:57194"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:51:42.867Z (last line of the file)"
    quote: '{"ts": "2026-11-15T22:51:42.867Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "00fd1d1796c9", "event": "crash", "delay": 0.5}'
  - id: E6
    type: probe
    source: "/health, request_id=konan-1794783131-26525 (2026-11-15T22:52:11Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000189s request_id=konan-1794783131-26525
  - id: E7
    type: probe
    source: "/metrics, request_id=konan-1794783140-26534 (2026-11-15T22:52:20Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000199s request_id=konan-1794783140-26534
  - id: E8
    type: probe
    source: "/products, request_id=konan-1794783141-26539 (2026-11-15T22:52:21Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000190s request_id=konan-1794783141-26539
  - id: E9
    type: probe
    source: "/health, request_id=konan-1794783200-26563 (2026-11-15T22:53:20Z, triage lens)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000176s request_id=konan-1794783200-26563
  - id: E10
    type: probe
    source: "/orders, request_id=konan-1794783235-26578 (2026-11-15T22:53:55Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000228s request_id=konan-1794783235-26578
  - id: E11
    type: log
    source: "lab/logs/app.log, whole file, count of lines with unhandled_exception, taken after E10"
    quote: "0"
  - id: E12
    type: log
    source: "lab/logs/app.log, whole file, count of lines with \"event\": \"startup\" and the line count of the file, taken after E10"
    quote: |-
      1
            14 lab/logs/app.log
  - id: E13
    type: log
    source: "lab/logs/app.log, whole file, count of lines with \"level\": \"ERROR\", taken after the judge"
    quote: "0"
gaps:
  - "Metrics: /metrics refused the connection (E7), so no snapshot exists: no process_uptime_seconds, no process_max_rss_bytes, no faultline_chaos_enabled, no request counters."
  - "The exit itself is not observed: E5 is the process's own announcement. The process table, a listener listing for port 8000, the exit status and lab/server.out are outside the surface contract, so they were not read."
  - "The sender of the crash-simulation request is unknown: the log shows only client 127.0.0.1:57194, and that path is operator surface, outside the probe allowlist."
  - "No telemetry exists before 2026-11-15T22:51:36.354Z: the log starts there and has no rotated backups, so the complaint's 'fine ten minutes ago' could not be checked."
  - "Two triage lenses were not spawned: software-defect and interfaces. The baseline excluded their domains: the whole log is 14 lines, all access lines carry status 200 or 201, no exception, gateway-status, chaos or configuration-change line exists. This is an accepted blind spot."
  - "User impact after the exit is not measurable from telemetry: a refused connection never reaches the process, so the log holds no failed user request. The only observed failures are investigator probes."
  - "The 'no restart' statement holds for the window to 2026-11-15T22:53:55Z (five probes over 104 s) and for the log as read at conclusion."
usage:
  model: claude-fable-5-2
  tokens: 942656
  wall_clock_seconds: 205
---

# Shop down: the target process exited and was not restarted

## Summary

**Verdict: root cause identified — `infra-process` / `process-crashed`.** The target
process (pid 26432) logged a request to its crash-simulation path at 22:51:42.365Z (E4)
and, with the same request id, announced `crashing now: exiting with code 1` at
22:51:42.867Z (E5). That is the last line of the log. No second startup event exists
(E12). Five investigator probes on four paths between 22:52:11Z and 22:53:55Z were
refused at connect in under 1 ms (E6–E10): nothing listens on the port. This matches the
complaint: no page loads, and no error page appears, because no process is there to
answer.

Impact: total. Every request to the target fails at connect from 22:51:42.867Z until
someone starts the process. Confidence: high for the mechanism; the exit itself is
inferred from the process's own announcement plus the refusals, not observed in a
process table (see Gaps).

One part of the complaint has no support in telemetry: "fine ten minutes ago". The log
starts at 22:51:36.354Z, 16 s before the complaint, and the only process instance in it
lived about 6.5 s.

## Timeline

All times UTC, 2026-11-15.

- 22:51:36.354 — server process 26432 starts; `startup` event, version 0.1.0 (E1, E2).
- 22:51:37.101–22:51:40.305 — six requests, all 200 or 201; the last one is
  `GET /orders -> 200` (E3).
- 22:51:42.365 — `GET /simulate/crash -> 200`, request id `00fd1d1796c9`, not an
  investigator request (E4). **Operator-surface marker: the change event.**
- 22:51:42.867 — `crashing now: exiting with code 1`, same request id, `delay: 0.5`;
  last line of the log (E5).
- 22:51:52 — complaint raised.
- 22:52:04 — investigation starts (trigger latency 12 s).
- 22:52:11–22:52:21 — probes on `/health`, `/metrics`, `/products` refused at connect
  (E6, E7, E8).
- 22:53:20 — triage lens probe on `/health` refused (E9).
- 22:53:55 — probe on `/orders` refused (E10); the log still has 14 lines and one
  startup event (E12).

## Investigation

Complaint object, as synthesized by the manual trigger adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794783112",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-15T22:51:52Z"
}
```

Investigation start: 2026-11-15T22:52:04Z. `KONAN_ADAPTER` was unset, so the surface
contract is `docs/lab.md`.

- **Baseline.** `/health`, `/metrics` and `/products` all refused the connection
  (E6–E8). No metrics snapshot was possible. The log has 14 lines; the orchestrator read
  all of them. Normal, as far as the log shows it: one startup, six requests with status
  200 or 201 and durations from 0.858 ms to 12.097 ms.
- **Triage.** One lens: infra-process. It reported the announced exit (E4, E5), the
  refusal with no restart (E9, E12), and the short, healthy life of the only process
  instance (E1, E2). The software-defect and interfaces lenses were not spawned; the
  baseline excluded their domains (see Gaps).
- **Deep-dive.** Skipped. The triage evidence for H1 was deterministic and complete, so
  H1 went straight to the judge. The orchestrator added one more probe (E10) and the log
  counts (E11, E12).
- **Judge.** H1 validated, with two wording limits: E5 is an announcement of the exit,
  not an observation of it, and "no restart" holds only for the probe window and this
  log. H2 invalidated. H3 invalidated, mainly by E4 and E5; the judge called E3 and E11
  weak and asked for proof that no ERROR-level line exists. E13 answers that: zero
  ERROR-level lines.

One triage round, no deep-dive round, one judge.

## Hypotheses

### H1 — the process exited and was not restarted (validated)

E4 and E5 share request id `00fd1d1796c9` and sit 0.502 s apart, against `delay: 0.5`
in E5. E5 is the last line of the file. The log holds one startup event in 14 lines
(E2, E12), so no restart happened. Five probes on four paths were refused at connect in
about 0.2 ms each (E6–E10): a refusal, not a timeout, so no listener holds the port.
No evidence contradicts H1. Class `infra-process`, cause `process-crashed`: the process
exited once and was not restarted.

### H2 — the process is alive but hung (invalidated)

A hung process that holds the port accepts the connection and then stalls; the probe
would time out. E6, E9 and E10 show an immediate refusal instead, and E5 shows the
process announcing its exit.

### H3 — a code defect took the service down (invalidated)

E5 names the mechanism: a deliberate exit from logger `faultline.simulate`, tied by
request id to the crash-simulation request (E4). The process was alive to write that
line. The log holds no `unhandled_exception` line (E11) and no ERROR-level line (E13),
and the last user request before the exit answered 200 (E3).

## Safe next steps

Read-only only.

- Read `lab/server.out` and the process table for pid 26432 to observe the exit and its
  code; list the listeners on port 8000. These are outside the investigator's surface,
  so an operator does this.
- Find who sent the request with id `00fd1d1796c9` from client `127.0.0.1:57194` at
  22:51:42.365Z: check operator or eval-side activity at that time.
- Check whether a supervisor is expected to restart the process, and if so, read its
  log for the reason it did not.
- After the process is back, watch for a new `startup` event in `lab/logs/app.log` and
  read `process_uptime_seconds` from `/metrics` to confirm the restart time.

## Gaps

- **No metrics.** `/metrics` refused the connection (E7). Uptime, memory, the chaos
  gauge and the request counters were out of reach for the whole investigation.
- **The exit is inferred, not observed.** E5 is the process's own announcement. The
  process table, a listener listing, the exit status and `lab/server.out` are outside
  the surface contract.
- **Unknown sender.** The crash-simulation request came from `127.0.0.1:57194`; that
  path is operator surface and the investigator cannot ask about it.
- **No history.** The log starts at 22:51:36.354Z with no rotated backups. The
  complaint's "fine ten minutes ago" could not be checked.
- **Two lenses skipped.** Software-defect and interfaces were excluded by the baseline
  (14 lines read in full; statuses 200 and 201 only; no exception, gateway-status, chaos
  or configuration-change line). This is an accepted blind spot.
- **User impact is not countable.** A refused connection leaves no log line, so the only
  observed failures are the investigator's five probes.
- **"No restart" has a window.** It holds to 22:53:55Z and for the log as read at
  conclusion.
