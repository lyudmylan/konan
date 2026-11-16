---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-down-process-exit
  trigger: |-
    manual — /konan human report. Complaint object, verbatim:
    {"source": "human", "fingerprint": "human-1794756676", "labels": {"alertname": "human-report"}, "annotations": {"summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."}, "startsAt": "2026-11-15T15:31:16Z"}
    Investigation start: 2026-11-15T15:31:22Z (trigger latency 6 s). The reporter stated no severity.
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-15T15:31:22Z
  concluded: 2026-11-15T15:34:51Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The server process exited with code 1 at 2026-11-15T15:31:08.065Z, 0.5 s after it served a GET request on the operator path /simulate/crash, and nothing restarted it, so nothing listens on port 8000 and every connection is refused."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The server process exited with code 1 at 2026-11-15T15:31:08.065Z, 0.5 s after it served a GET request on the path /simulate/crash; nothing restarted it, so nothing listens on port 8000 and every connection is refused."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E10]
    evidence_against: []
  - id: H2
    statement: "The process is alive but hung: it holds the port and does not answer."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E6, E7]
  - id: H3
    statement: "An unhandled exception in the target's own code, on some user input, took the process down."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E8, E9]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794756692-5268 (2026-11-15T15:31:32Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000210s request_id=konan-1794756692-5268
  - id: E2
    type: probe
    source: "/metrics, request id konan-1794756693-5273 (2026-11-15T15:31:33Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000195s request_id=konan-1794756693-5273
  - id: E3
    type: probe
    source: "/products, request id konan-1794756693-5278 (2026-11-15T15:31:33Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000190s request_id=konan-1794756693-5278
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:31:01.590Z (line 3 of 14; the only startup line; no backup files)"
    quote: |-
      {"ts": "2026-11-15T15:31:01.590Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:31:07.563Z (line 13 of 14)"
    quote: |-
      {"ts": "2026-11-15T15:31:07.563Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "d5ad37a6e7c6", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.837, "client": "127.0.0.1:53757"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:31:08.065Z (line 14 of 14, the last line; still the last line on a second read at 2026-11-15T15:32:46Z)"
    quote: |-
      {"ts": "2026-11-15T15:31:08.065Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "d5ad37a6e7c6", "event": "crash", "delay": 0.5}
  - id: E7
    type: probe
    source: "/health, request id konan-1794756783-5330 (2026-11-15T15:33:03Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000178s request_id=konan-1794756783-5330
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:31:05.504Z (line 12 of 14; the last access line before E5; all 7 access lines have status 200 or 201)"
    quote: |-
      {"ts": "2026-11-15T15:31:05.504Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "7b11df292b64", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.839, "client": "127.0.0.1:53756"}
  - id: E9
    type: log
    source: "lab/logs/app.log, whole file (14 lines): count of lines that match unhandled_exception, \"level\": \"ERROR\", or \"stack\" (grep -c, 2026-11-15T15:34:47Z)"
    quote: "0"
  - id: E10
    type: probe
    source: "/products, request id konan-1794756887-5367 (2026-11-15T15:34:47Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000169s request_id=konan-1794756887-5367
gaps:
  - "No metrics: /metrics refuses the connection (E2), so process_uptime_seconds, process_max_rss_bytes, faultline_chaos_enabled and the request counters could not be read."
  - "The complaint's 'fine ten minutes ago' could not be checked: the log starts at 2026-11-15T15:31:01.590Z (E4) and has no backup files, so the telemetry holds 6.5 s of process life and nothing older."
  - "The sender of the /simulate/crash request is unknown: the log shows only client 127.0.0.1:53757 and a request id without the investigator prefix (E5); the operator surface is outside the contract."
  - "The exit code and the missing listener are inferred from the log message (E6) and the refused connections (E1, E2, E3, E7, E10); the process table, lab/faultline.pid and lab/server.out are outside the surface contract and were not read."
  - "Why nothing restarted the process could not be checked: no supervisor telemetry exists on the surface."
  - "User impact after the exit is not measured: a refused connection leaves no log line, so 'for everyone' rests on refused investigator probes on three paths, not on user traffic."
  - "Lenses not spawned: software-defect and interfaces. The baseline excluded their domains (E8, E9: no exception line, no 5xx, no gateway-shaped status; the probes reach the process directly), and the service gave no further surface to sweep. The blind spot is accepted."
usage:
  model: claude-fable-5-2
  tokens: 902997
  wall_clock_seconds: 209
---

# Shop down: the server process exited and was not restarted

## Summary

**Root cause identified (infra-process, process-crashed).** The faultline server process
exited with code 1 at 2026-11-15T15:31:08.065Z (E6). The exit followed, by the logged
delay of 0.5 s and under the same request id `d5ad37a6e7c6`, a GET request on the
operator path `/simulate/crash` that returned 200 (E5). Nothing restarted the process:
the log has one startup line (E4) and no line after the exit line (E6), and five probes
on three paths between 15:31:32Z and 15:34:47Z were refused at connect (E1, E2, E3, E7,
E10). This matches the reported symptom — no page and no error page, because no process
answers. Before the exit the service was healthy: all 7 access lines have status 200 or
201 (E8) and the log holds no exception or error line (E9). Confidence is high for the
mechanism. Two details are inferred, not observed: the exit code (from the log message)
and the missing listener (from the refused connections). The complaint's "ten minutes
ago" is not supported by the telemetry, which starts 15 s before the complaint.

## Timeline

- 2026-11-15T15:31:01.590Z — startup marker, `faultline 0.1.0 started` (E4).
- 2026-11-15T15:31:05.504Z — last ordinary request, `GET /orders -> 200` (E8).
- 2026-11-15T15:31:07.563Z — `GET /simulate/crash -> 200`, client `127.0.0.1:53757`,
  request id `d5ad37a6e7c6`, not investigator traffic (E5).
- 2026-11-15T15:31:08.065Z — `crashing now: exiting with code 1`, same request id,
  `"delay": 0.5` (E6). Last line of the log.
- 2026-11-15T15:31:16Z — complaint raised (`startsAt`).
- 2026-11-15T15:31:22Z — investigation start.
- 2026-11-15T15:31:32Z to 15:31:33Z — probes of `/health`, `/metrics`, `/products`
  refused at connect (E1, E2, E3).
- 2026-11-15T15:33:03Z — `/health` still refused (E7).
- 2026-11-15T15:34:47Z — `/products` still refused (E10); no exception or error line
  in the whole log (E9).

## Investigation

- **Setup.** `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`. Budget:
  the default.
- **Baseline.** Three probes (`/health`, `/metrics`, `/products`) were refused at
  connect in about 0.2 ms each (E1, E2, E3). No metrics snapshot exists. The log
  `lab/logs/app.log` has 14 lines and no backups; it was read whole. It shows a healthy
  6.5 s of service (E4, E8) that ends in an exit line (E5, E6).
- **Triage.** One lens ran, infra-process, blind. It returned three findings: the exit
  line (E6), the link to the `/simulate/crash` request by request id and delay (E5), and
  the continued refusal with one startup line only (E4, plus its own refused probe,
  request id `konan-1794756766-5322`). The software-defect and interfaces lenses were not
  spawned; the baseline excluded their domains (see Gaps).
- **Deep-dive.** Skipped. The triage evidence for H1 was deterministic and complete, and
  the baseline already tested H2 and H3.
- **Judge.** One fresh judge, evidence only. H1 validated; H2 invalidated; H3
  invalidated. The judge named one missing item for H3, a count of exception and error
  lines; that count is 0 (E9). A last probe confirmed no restart (E10).

## Hypotheses

### H1 — the process exited and was not restarted (validated)

E5 and E6 carry the same request id, and the 0.502 s between them equals the logged
`"delay": 0.5`, so the exit is tied to the `/simulate/crash` request. The prediction
held on both sides: every probe failed at connect on every path (E1, E2, E3, E7, E10),
and the log has one startup line (E4) and nothing after the exit line (E6). No evidence
against. The refused probes alone would not separate H1 from another cause of a missing
listener; E5 and E6 do.

### H2 — the process is alive but hung (invalidated)

A hung process that holds the port accepts the connection and then times out. The
probes were refused at connect in about 0.2 ms, 91 s apart (E1, E7), and the log holds
an exit line (E6), which this hypothesis says must not exist.

### H3 — an unhandled exception in the target's code took the process down (invalidated)

The exit line comes from the logger `faultline.simulate` with event `crash`, tied to a
request that returned 200 (E5, E6), not from an exception. Every access line before it
has status 200 or 201 (E8), and the whole log holds no `unhandled_exception` line, no
ERROR line and no stack (E9).

## Safe next steps

- Read the process table and `lab/server.out` for process 5186 to confirm the exit and
  its code (outside the investigator's surface; an operator can do it).
- Identify the sender of the request with id `d5ad37a6e7c6` from client
  `127.0.0.1:53757` at 15:31:07.563Z, on the operator side.
- After an operator restores the service, read `process_uptime_seconds` on `/metrics`
  and the new startup line to anchor the end of the outage.
- Check whether a supervisor is expected to restart the process, and read its record
  for 15:31:08Z.

## Gaps

- **No metrics.** `/metrics` refuses the connection (E2). Uptime, memory, the chaos
  gauge and the request counters could not be read.
- **"Fine ten minutes ago."** The log starts at 15:31:01.590Z (E4) with no backups. The
  telemetry shows 6.5 s of process life and an outage that began 8 s before the
  complaint. Nothing older is visible, so the statement is neither confirmed nor denied.
- **Sender of the crash request.** Only the client address and an unstamped request id
  are visible (E5). The operator surface is outside the contract.
- **Exit code and listener.** Both are inferred (E6; E1, E2, E3, E7, E10). The process
  table, `lab/faultline.pid` and `lab/server.out` are outside the surface contract.
- **No restart.** No supervisor telemetry exists on the surface, so the reason is
  unknown.
- **User impact.** A refused connection leaves no log line. "For everyone" rests on
  refused investigator probes on three paths.
- **Lenses not spawned.** Software-defect and interfaces. The baseline excluded their
  domains (E8, E9), and the service gave no further surface to sweep. The blind spot is
  accepted.
