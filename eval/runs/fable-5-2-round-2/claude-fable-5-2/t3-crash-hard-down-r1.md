---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-down-process-crashed
  trigger: "manual (/konan, human profile); fingerprint human-1794782799; alertname human-report; no severity stated; startsAt 2026-11-15T22:46:39Z; investigation start 2026-11-15T22:46:51Z; trigger latency 12 s"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-15T22:46:51Z
  concluded: 2026-11-15T22:50:32Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The target process announced its exit with code 1 at 22:46:31.193Z, 0.5 s after a request to its internal crash endpoint (request f243cb6cdf08), and nothing restarted it, so no process listens on port 8000 and every connection is refused."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The target process exited at 22:46:31.193Z, 0.5 s after a request to its internal crash endpoint, and was not restarted; no process listens on port 8000, so every request is refused at connect."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E4, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code (an unhandled exception on some input) took the service down."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E11, E12, E13]
  - id: H3
    statement: "A failure at a boundary between the clients and the target (gateway, network path) blocks the requests while the target process is alive."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E7, E9]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794782816-26264 (2026-11-15T22:46:56Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000196s request_id=konan-1794782816-26264
  - id: E2
    type: probe
    source: "/metrics, request id konan-1794782816-26269 (2026-11-15T22:46:56Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000208s request_id=konan-1794782816-26269
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:24.697Z"
    quote: '{"ts": "2026-11-15T22:46:24.697Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [26172]"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:24.698Z"
    quote: '{"ts": "2026-11-15T22:46:24.698Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:28.634Z"
    quote: '{"ts": "2026-11-15T22:46:28.634Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "f3096f9f2c76", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.739, "client": "127.0.0.1:57135"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:30.692Z"
    quote: '{"ts": "2026-11-15T22:46:30.692Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "f243cb6cdf08", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 2.403, "client": "127.0.0.1:57136"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:31.193Z"
    quote: '{"ts": "2026-11-15T22:46:31.193Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "f243cb6cdf08", "event": "crash", "delay": 0.5}'
  - id: E8
    type: probe
    source: "/health, request id konan-1794782888-26329 (2026-11-15T22:48:08Z, re-probe of the infra-process lens)"
    quote: "-- HTTP 000 in 0.000223s request_id=konan-1794782888-26329"
  - id: E9
    type: probe
    source: "/products, request id konan-1794782927-26342 (2026-11-15T22:48:47Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000208s request_id=konan-1794782927-26342
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:24.698Z"
    quote: '{"ts": "2026-11-15T22:46:24.698Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:25.434Z"
    quote: '{"ts": "2026-11-15T22:46:25.434Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "3b6fe73a7261", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 12.382, "client": "127.0.0.1:57130"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:25.461Z"
    quote: '{"ts": "2026-11-15T22:46:25.461Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "b137b692da8a", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.179, "client": "127.0.0.1:57132"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:46:27.579Z"
    quote: '{"ts": "2026-11-15T22:46:27.579Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "5258b83306f2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.953, "client": "127.0.0.1:57134"}'
gaps:
  - "No metrics snapshot: /metrics refused the connection (E2), so process_uptime_seconds, process_max_rss_bytes, http_exceptions_total and faultline_chaos_enabled have no values."
  - "The exit itself is not observed: E7 is the process's own announcement. The process table, the listener list for port 8000, lab/server.out and lab/faultline.pid are outside the surface contract."
  - "No telemetry exists before 2026-11-15T22:46:24.697Z (one log file, no rotated backups), so the claim 'fine ten minutes ago' cannot be checked."
  - "The sender of the crash request is unknown: the log shows only client 127.0.0.1:57136 and a request id without the investigator prefix."
  - "'Not restarted' holds only to 2026-11-15T22:48:48Z, the last check of the log and of the probes."
  - "User impact after the exit is inferred from refused investigator probes on three paths; a dead process logs no user traffic."
usage:
  model: claude-fable-5-2
  tokens: 1167859
  wall_clock_seconds: 221
---

# Shop down: the faultline process exited after a crash request and was not restarted

## Summary

**Verdict: root cause identified** (`infra-process` / `process-crashed`). The target
process started at 22:46:24.697Z (E3, E4), served seven requests with 2xx statuses
(E5, E11, E12, E13), and then received `GET /simulate/crash` at 22:46:30.692Z (E6).
0.5 s later it logged `crashing now: exiting with code 1` under the same request id
(E7). No line follows, and no second startup event exists. Every probe since then is
refused at connect on `127.0.0.1:8000` in about 0.2 ms, on `/health`, `/metrics` and
`/products` (E1, E2, E8, E9), which is the address the process had bound (E10).
Impact: total, every path, since 22:46:31Z; the complaint arrived 8 s later and matches
("not even an error page" is a refused connection). Confidence: high for the mechanism;
the judge validated H1 and invalidated the two alternatives. The crash request was not
investigator traffic (its request id has no `konan-` prefix); who sent it is unknown.

## Timeline

All times UTC, 2026-11-15.

- 22:46:24.697 — server process 26172 starts (E3); `startup` event, version 0.1.0 (E4);
  listener on `http://127.0.0.1:8000` (E10).
- 22:46:25.434 – 22:46:28.634 — normal traffic, all 2xx, durations 0.7–12.4 ms
  (E11, E12, E13, E5). Last known-good request: `GET /orders -> 200` (E5).
- 22:46:30.692 — **change marker**: `GET /simulate/crash -> 200`, request
  `f243cb6cdf08`, client `127.0.0.1:57136` (E6).
- 22:46:31.193 — CRITICAL `crashing now: exiting with code 1`, same request id,
  `delay: 0.5` (E7). Last line of the log.
- 22:46:39 — complaint raised (`startsAt`).
- 22:46:51 — investigation starts (trigger latency 12 s).
- 22:46:56 — first known-bad: `/health` and `/metrics` refused (E1, E2).
- 22:48:08 — `/health` still refused (E8).
- 22:48:47 — `/products` refused (E9); the log still has 14 lines at 22:48:48.

## Investigation

**Complaint object** (manual trigger, `/konan`), verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794782799",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-15T22:46:39Z"
}
```

Investigation start: `2026-11-15T22:46:51Z` (trigger latency 12 s). The reporter stated
no severity. `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`.

**Baseline.** `/health` and `/metrics` both refused the connection (E1, E2); no metrics
snapshot exists. The log `lab/logs/app.log` has 14 lines and no rotated backups; it was
read whole. It ends with the crash line (E7).

**Triage.** Three lenses ran in parallel, each blind to the others: infra-process,
interfaces, software-defect. All three found the same pair of lines (E6, E7) and the
missing restart. The interfaces lens found no gateway-shaped status and no contract
anomaly, and handed the mechanism to infra-process. The software-defect lens found no
exception line, no stack, and no failing route or input. One orchestrator probe of the
business surface followed (`/products`, E9).

**Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete.

**Judge.** One fresh judge saw the hypothesis list and the verbatim evidence only.
Verdicts: H1 validated, H2 invalidated, H3 invalidated. The judge limited the wording of
H1 on three points, all recorded under Gaps: the exit is announced, not observed; "not
restarted" holds to the last check; E8 carries no curl error line. The judge also asked
for a line that ties the log to port 8000; E10 was added for that.

Budget used: one triage round, zero deep-dive agents, one judge round.

## Hypotheses

### H1 — the process exited after a crash request and was not restarted (validated)

`infra-process` / `process-crashed`. E6 and E7 share the request id `f243cb6cdf08`, and
the 0.501 s gap between them equals `delay: 0.5`. E7 is the last line of the log; E4 is
the only startup event. The prediction was: every path is refused at connect, and the
log stays silent. Both hold: E1, E2, E8 and E9 show `HTTP 000` in about 0.2 ms on the
address of E10, and the log did not grow. No evidence against.

The cause id is `process-crashed`, not `degradation-switch`: the endpoint did not inject
errors or latency while on; it ended the process once, and the process stayed down.

### H2 — a defect in the target's own code (invalidated)

`software-defect`. The prediction was an unhandled-exception line, a stack, or a 5xx
status before the outage. The complete log has none: all access lines are 2xx
(E5, E11, E12, E13), the crash request itself returned 200 in 2.4 ms (E6), and the exit
is announced by the target's simulate logger (E7). The judge names what would reverse
this: a traceback or a signal death in the process's stderr or exit record.

### H3 — a boundary failure in front of a live process (invalidated)

`interfaces`. The refusals (E1, E2, E9) give H3 no support of their own, because H1
predicts the same. They count against it: a refusal in 0.2 ms on the loopback address
leaves no gateway or network path to fail, and a live listener would accept. E7 shows
the process announced its exit. The judge notes that log silence alone does not count
against H3; the listener list for port 8000 would settle it finally.

## Safe next steps

Read-only suggestions only.

- Read the process table and the listener list for port 8000 to confirm that pid 26172
  is gone and nothing listens.
- Read `lab/server.out` for the exit record of the process.
- Identify the sender of request `f243cb6cdf08` (client `127.0.0.1:57136`) from the
  operator side; the target's telemetry does not name it.
- Check whether a supervisor is expected to restart the process, and why it did not.
- Find when the service last ran before 22:46:24Z, to test "fine ten minutes ago".

## Gaps

- **No metrics.** `/metrics` was refused (E2). Uptime, memory, the exception counter
  and the chaos gauge have no values, so no counter-reset evidence exists.
- **The exit is announced, not observed.** E7 is the process's own line. The process
  table, the listener list, `lab/server.out` and `lab/faultline.pid` are outside the
  surface contract and were not read.
- **No history before 22:46:24.697Z.** One log file, no rotated backups. The process
  lived about 6.5 s. The claim "fine ten minutes ago" is neither confirmed nor refuted.
- **Unknown sender.** The crash request came from `127.0.0.1:57136` with a request id
  that has no investigator prefix. The telemetry says nothing more about its origin.
- **Restart window.** "Not restarted" is true to 22:48:48Z only.
- **User impact is inferred.** A dead process logs nothing; the impact claim rests on
  refused investigator probes on three paths.
