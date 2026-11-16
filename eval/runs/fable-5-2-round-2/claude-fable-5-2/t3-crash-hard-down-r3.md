---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-down-process-exited
  trigger: "manual (/konan, human profile; fingerprint human-1794783408; alertname human-report; no severity stated; startsAt 2026-11-15T22:56:48Z; investigation start 2026-11-15T22:57:04Z; trigger latency 16 s)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-15T22:57:04Z
  concluded: 2026-11-15T23:00:46Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The service process announced its own exit with code 1 at 22:56:39.513Z, 0.5 s after a GET to its operator crash route, and no process started in its place; nothing listens on port 8000, so every request fails at the connection."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The service process exited at 22:56:39.513Z (announced exit code 1), 0.5 s after a request to its operator crash route, and was not restarted; nothing listens on port 8000, so every request on every path is refused at the connection."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The process is alive but hung and does not serve: connections are accepted and then time out."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E3, E9]
  - id: H3
    statement: "A defect in the service's own request-handling code raised an unhandled exception on a user request and killed the process."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E8]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log line 14 (last line of the file) @ 2026-11-15T22:56:39.513Z"
    quote: '{"ts": "2026-11-15T22:56:39.513Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "6b5346564f8f", "event": "crash", "delay": 0.5}'
  - id: E2
    type: log
    source: "lab/logs/app.log line 13 @ 2026-11-15T22:56:39.012Z"
    quote: '{"ts": "2026-11-15T22:56:39.012Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "6b5346564f8f", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.909, "client": "127.0.0.1:57236"}'
  - id: E3
    type: probe
    source: "/health, request id konan-1794783424-26742 (2026-11-15T22:57:04Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000189s request_id=konan-1794783424-26742
  - id: E4
    type: probe
    source: "/metrics, request id konan-1794783431-26755 (2026-11-15T22:57:11Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000197s request_id=konan-1794783431-26755
  - id: E5
    type: probe
    source: "/products, request id konan-1794783440-26760 (2026-11-15T22:57:20Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000197s request_id=konan-1794783440-26760
  - id: E6
    type: log
    source: "lab/logs/app.log line 3 (the only startup event in the file) @ 2026-11-15T22:56:33.037Z"
    quote: '{"ts": "2026-11-15T22:56:33.037Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E7
    type: log
    source: "lab/logs/app.log line 1 (first line of the file) @ 2026-11-15T22:56:33.036Z"
    quote: '{"ts": "2026-11-15T22:56:33.036Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [26651]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}'
  - id: E8
    type: log
    source: "lab/logs/app.log line 12 (last access line before the crash request) @ 2026-11-15T22:56:36.956Z"
    quote: '{"ts": "2026-11-15T22:56:36.956Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "64da08781502", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.524, "client": "127.0.0.1:57235"}'
  - id: E9
    type: probe
    source: "/health, request id konan-1794783485-26800 (2026-11-15T22:58:05Z, triage lens probe)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000201s request_id=konan-1794783485-26800
  - id: E10
    type: probe
    source: "/health, request id konan-1794783577-26829 (2026-11-15T22:59:37Z, confirmation probe after the judge)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000174s request_id=konan-1794783577-26829
gaps:
  - "Metrics could not be read: /metrics refuses the connection (E4), so process_uptime_seconds, process_max_rss_bytes, faultline_chaos_enabled and the request and exception counters are unknown. Every statement about the time before the exit rests on the log alone."
  - "The log starts at 2026-11-15T22:56:33.036Z and has no rotated backups; the logged process lived about 6.5 s. The complaint's 'fine ten minutes ago' can be neither confirmed nor refuted."
  - "The sender of the crash-route request is unknown: client 127.0.0.1:57236, request id 6b5346564f8f without the investigator prefix. The operator surface is out of bounds for the investigator, so intent and origin could not be checked."
  - "The exit status was not observed, only the process's own announcement (E1). A process listing and the process's stderr are outside the surface contract, so the absence of pid 26651 (E7) was not checked directly."
  - "No restart was observed up to 2026-11-15T22:59:37Z (E10); a later restart is outside this investigation's window."
  - "User impact could not be counted: a refused connection leaves no log line, and the counters are unreadable. 'For everyone' is supported by the mechanism (no listener), not by a count of failed user requests."
  - "The software-defect lens was not spawned in triage: the baseline log held no unhandled_exception event, no stack field and no status other than 200 or 201. The defect hypothesis (H3) was still put to the judge."
usage:
  model: claude-fable-5-2
  tokens: 1046407
  wall_clock_seconds: 222
---

# Shop down: the service process exited after a crash-route request and was not restarted

## Summary

**Verdict: root cause identified** (`infra-process` / `process-crashed`). The service
process logged `crashing now: exiting with code 1` at 22:56:39.513Z (E1). The same
request id appears 0.5 s earlier on a GET to the operator route `/simulate/crash` (E2),
and the gap matches the logged `"delay": 0.5`. The log holds one startup event (E6) and
no line after the exit line. Every probe since then, on `/health`, `/metrics` and
`/products`, is refused at the connection in under 1 ms (E3, E4, E5, E9, E10): nothing
listens on port 8000. That matches the complaint exactly: no page loads and no error
page is served, because no process answers.

Impact: total. Every path is unreachable from 22:56:39.513Z to at least 22:59:37Z.
Confidence: high for the mechanism (exit line, linked request, refused connections).
The crash request did not come from the investigator (no `konan-` request id); who sent
it is not known. The complaint's "fine ten minutes ago" is not verifiable: the log
starts 6.5 s before the exit.

## Timeline

All times UTC, 2026-11-15.

- 22:56:33.036 — server process 26651 starts (E7); startup event `faultline 0.1.0 started` at 22:56:33.037 (E6).
- 22:56:33.785 to 22:56:36.956 — seven access lines, all 200 or 201; the last is `GET /orders -> 200` (E8).
- 22:56:39.012 — `GET /simulate/crash -> 200`, request id `6b5346564f8f`, client 127.0.0.1:57236 (E2). This is the change marker.
- 22:56:39.513 — `crashing now: exiting with code 1`, same request id (E1). Last line of the log.
- 22:56:48 — complaint raised (`startsAt`).
- 22:57:04 — investigation starts; `/health` refused (E3).
- 22:57:11, 22:57:20 — `/metrics` and `/products` refused (E4, E5).
- 22:58:05 — `/health` still refused (E9).
- 22:59:37 — `/health` still refused (E10). No startup line after E1.

## Investigation

Complaint object, as synthesized by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794783408",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-15T22:56:48Z"
}
```

Investigation start: 2026-11-15T22:57:04Z (trigger latency 16 s). `KONAN_ADAPTER` was
unset, so the surface contract is `docs/lab.md`.

- **Baseline.** Three probes (`/health`, `/metrics`, `/products`) were refused at the
  connection (E3, E4, E5). No metrics snapshot exists. The complete log is 14 lines:
  one startup, seven successful access lines, the crash-route request, the exit line.
  During baseline the orchestrator also opened `lab/server.out` and `lab/faultline.pid`;
  they are runtime files under `lab/` but not part of the surface list in `docs/lab.md`,
  and nothing is cited from them.
- **Triage.** Two lenses ran in parallel: infra-process and interfaces. Both found the
  exit line, its link to the crash-route request, and the missing restart; both found
  no saturation, latency, gateway status or chaos event. The interfaces lens classed the
  mechanism as `infra-process`. The software-defect lens was not spawned (see Gaps).
- **Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete.
- **Judge.** One fresh judge saw the hypotheses and the verbatim evidence E1 to E9 only.
  Verdicts: H1 validated, H2 invalidated, H3 invalidated. The judge noted that "code 1"
  is the process's announcement and that "no restart" holds only up to the last probe;
  the root-cause statement and the gaps carry both limits. E10 is a confirmation probe
  sent after the judge.

## Hypotheses

### H1 — the process exited and was not restarted (validated)

E1 and E2 share request id `6b5346564f8f`; the 501 ms between them matches the logged
delay. E1 is the last line of the log and E6 is the only startup event. E3, E4, E5, E9
and E10 show an immediate refusal on three paths over 153 s. The prediction (refused
connection on every path, exit line last, no later startup) held on every check.

### H2 — the process is alive but hung (invalidated)

A hung process accepts connections and then times out. The probes were refused at once
(E3, E9), and the log holds an exit line (E1).

### H3 — an unhandled exception in request-handling code killed the process (invalidated)

The log has no `unhandled_exception` event, no stack, and no status other than 200 or
201; the last business request succeeded (E8). The exit line comes from the logger
`faultline.simulate`, tied to the crash-route request that itself returned 200 (E1, E2).
Residual doubt: a process can die without a log line, and the counters are unreadable.

## Safe next steps

Read-only only.

- Check the process list for pid 26651 and read the state of whatever supervises the
  service; confirm that no supervisor is configured to restart it.
- Read the captured stderr of the process for a traceback before the exit.
- Find the sender of request `6b5346564f8f` (client 127.0.0.1:57236) in the records of
  whoever has access to the operator surface.
- Once the owner has the service up again, read `/health`, `/metrics`
  (`process_uptime_seconds` near zero confirms a new process) and one business path.

## Gaps

- **Metrics unreadable.** `/metrics` is refused (E4). Uptime, RSS, the chaos gauge and
  the request and exception counters are unknown; the picture before the exit rests on
  14 log lines.
- **"Fine ten minutes ago" unverified.** The log starts at 22:56:33.036Z with no
  backups. The logged process lived about 6.5 s.
- **Sender of the crash request unknown.** The request carries no investigator prefix.
  The operator surface is out of bounds, so origin and intent were not checked.
- **Exit status not observed.** Only the announcement in E1. A process listing and
  stderr are outside the surface contract.
- **Restart window.** No restart up to 22:59:37Z (E10); nothing is known after that.
- **User impact not counted.** Refused connections leave no log line. "For everyone"
  follows from the mechanism, not from a count.
- **Software-defect lens skipped.** The baseline excluded its signals (no exception
  event, no stack, no non-2xx status). H3 still went to the judge.
