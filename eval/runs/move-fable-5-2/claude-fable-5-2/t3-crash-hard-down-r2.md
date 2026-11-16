---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-down-process-exit
  trigger: "manual — /konan human profile (docs/triggers.md); complaint object fingerprint human-1794756408, startsAt 2026-11-15T15:26:48Z; investigation start 2026-11-15T15:26:59Z; trigger latency 11 s"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-15T15:26:59Z
  concluded: 2026-11-15T15:30:03Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The server process announced an exit with code 1 at 2026-11-15T15:26:40.175Z, 0.5 s after it served a non-investigator GET to the operator path /simulate/crash; it was not restarted, so nothing accepts connections on 127.0.0.1:8000 and every request fails at connect."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The target's server process exited with code 1 at 2026-11-15T15:26:40.175Z, 0.5 s after it served a request to the path /simulate/crash; it was not restarted, so nothing listens on 127.0.0.1:8000 and every connection is refused."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "The process is alive but hung — it holds the port and does not serve."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E7, E8, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:26:33.690Z (line 1 of 14; the only startup sequence in the file; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-15T15:26:33.690Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [4929]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:26:37.615Z (line 12 of 14; the last access line before E3)"
    quote: |-
      {"ts": "2026-11-15T15:26:37.615Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "13de6211da50", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.836, "client": "127.0.0.1:53710"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:26:39.673Z (line 13 of 14)"
    quote: |-
      {"ts": "2026-11-15T15:26:39.673Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "e852b412df14", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.386, "client": "127.0.0.1:53711"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:26:40.175Z (line 14 of 14, the last line; the file still ended here at the reads of about 15:27:06Z and 15:28:45Z)"
    quote: |-
      {"ts": "2026-11-15T15:26:40.175Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "e852b412df14", "event": "crash", "delay": 0.5}
  - id: E5
    type: probe
    source: "/health, request id konan-1794756425-5031 (15:27:05Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000177s request_id=konan-1794756425-5031
  - id: E6
    type: probe
    source: "/metrics, request id konan-1794756426-5036 (15:27:06Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000193s request_id=konan-1794756426-5036
  - id: E7
    type: probe
    source: "/products, request id konan-1794756426-5041 (15:27:06Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000190s request_id=konan-1794756426-5041
  - id: E8
    type: probe
    source: "/health, request id konan-1794756498-5078 (15:28:18Z; probe of the infra-process triage lens)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000188s request_id=konan-1794756498-5078
  - id: E9
    type: probe
    source: "/health, request id konan-1794756524-5087 (15:28:44Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000173s request_id=konan-1794756524-5087
gaps:
  - "No metrics could be read: /metrics fails at connect (E6). Uptime, memory footprint, request and exception counters are unknown, so saturation before the exit is not assessable."
  - "The log starts at 2026-11-15T15:26:33.690Z and has no rotated backups. The claim 'fine ten minutes ago' cannot be checked; the visible process lived about 6.5 s."
  - "The sender of the GET /simulate/crash request is not identified. The log shows a loopback client (127.0.0.1:53711) and a request id without the konan- prefix, so it is not an investigator probe; nothing more."
  - "No process listing and no listening-socket listing is in the surface contract. The exit status and the state of PID 4929 were not observed; the conclusion rests on the announced exit (E4) and on connects that fail at once (E5–E9)."
  - "'Not restarted' holds up to the last observation at 15:28:44Z (E9). The 25 s between E4 and E5 have no probe."
  - "User impact after the exit is not visible in telemetry: a process that is down logs nothing. The outage scope rests on the investigator's probes of three paths on IPv4 127.0.0.1:8000."
  - "Triage lens skipped: software-defect. Reason: the 14 log lines hold no unhandled_exception event and no 5xx status; the exit line comes from the logger faultline.simulate (E4). With the process down there is nothing more for that lens to read."
  - "Triage lens skipped: interfaces. Reason: the lab has no boundary component (docs/lab.md, known gaps) and the probes fail at connect on the process's own address (E5–E9); no gateway-shaped status exists in the log."
  - "The event value 'crash' (E4) is not in the event list of docs/lab.md. It is quoted as it appears."
usage:
  model: claude-fable-5-2
  tokens: 859827
  wall_clock_seconds: 184
---

# Shop down: the server process exited after a request to /simulate/crash and was not restarted

## Summary

**Verdict: root cause identified — infra-process, process-crashed.** The server process
[4929] started at 15:26:33.690Z (E1) and served eight requests, all 2xx; the last
ordinary one is `GET /orders -> 200` at 15:26:37.615Z (E2). At 15:26:39.673Z it served
`GET /simulate/crash -> 200` from a loopback client, with a request id that is not an
investigator id (E3). 0.5 s later, under the same request id, it logged
`crashing now: exiting with code 1` (E4). Nothing is logged after that line, and no
second startup sequence exists. Every probe since then fails at connect in about 0.2 ms
on `/health`, `/metrics` and `/products`, from 15:27:05Z to 15:28:44Z (E5–E9).

Impact: total. Nothing accepts connections on 127.0.0.1:8000, which matches the
complaint ("pages do not load at all, not even an error page"). Confidence: high for the
mechanism (the exit marker and the request share one request id, and the `delay` field
matches the 0.502 s between the two lines). Not established: who sent the request, the
observed exit status, and the claim "fine ten minutes ago" — see Gaps.

## Timeline

All times UTC, 2026-11-15.

- 15:26:33.690 — `Started server process [4929]`; the only startup sequence in the log (E1).
- 15:26:34.437–15:26:37.615 — seven requests, all 2xx; the last is `GET /orders -> 200` (E2). Last known-good.
- 15:26:39.673 — `GET /simulate/crash -> 200`, request id `e852b412df14`, client `127.0.0.1:53711` (E3). Operator-surface marker; not an investigator probe.
- 15:26:40.175 — CRITICAL `crashing now: exiting with code 1`, same request id, `"delay": 0.5` (E4). Last log line.
- 15:26:48 — complaint raised (`startsAt` of the complaint object).
- 15:26:59 — investigation start.
- 15:27:05–15:27:06 — `/health`, `/metrics`, `/products` fail at connect (E5, E6, E7). First known-bad.
- 15:28:18 — `/health` fails at connect, triage lens probe (E8).
- 15:28:44 — `/health` fails at connect; the log still ends at E4 (E9, E4).

## Investigation

**Complaint block.** The complaint object, verbatim, as the `/konan` adapter built it:

```json
{
  "source": "human",
  "fingerprint": "human-1794756408",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-15T15:26:48Z"
}
```

Investigation start: 2026-11-15T15:26:59Z. Trigger latency: 11 s. The reporter stated no
severity, so the object carries none.

**Setup.** `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`. Budget:
the default.

**Baseline.** Three probes, one per command: `/health`, `/metrics`, `/products` — all
failed at connect (E5–E7). No metrics snapshot exists. `lab/logs/app.log` holds 14
lines, 15:26:33.690Z to 15:26:40.175Z, with no backups. Boundary note: I also opened
`lab/server.out` once. It is under `lab/` but the surface list of `docs/lab.md` does not
name it; it carried the same lines, and no evidence here is cited from it.

**Triage.** One lens ran: infra-process. It reported three findings — the exit marker
(E4), the trigger request under the same request id (E3), and a process that is down,
not degraded, with no restart (E1, E8). It found no latency anomaly before the exit
(durations 0.836–11.919 ms) and no `chaos_enabled` event. The lenses software-defect
and interfaces were not spawned; the excluding evidence is under Gaps.

**Deep-dive.** Skipped. The triage evidence for H1 was already deterministic and
complete. One more `/health` probe and one more log read confirmed the state at
15:28:44Z (E9).

**Judge.** One fresh judge saw the two hypotheses and the nine quotes only. H1:
validated — every prediction met. H2: invalidated — both predictions fail. The judge
named what the evidence does not carry: E4 is an announcement, not an observed exit
status; "not restarted" holds only up to the last probe; the sender of the request is
unknown. These limits are in Gaps, and the root-cause statement says "announced".

## Hypotheses

### H1 — the process exited after a request to /simulate/crash and was not restarted (validated)

Prediction: an exit marker tied to that request; no later log line and no second
startup; connects that fail at once on every path, and still later. All met. E3 and E4
share request id `e852b412df14`, and the `delay` of 0.5 matches the 0.502 s between
them. E1 is the only startup sequence and E4 is the last line at both reads. E5–E9 fail
at connect in about 0.2 ms on three paths over 99 s. E2 anchors the last known-good
request. No evidence against was found.

### H2 — the process is alive but hung (invalidated)

Prediction: connections are accepted and then time out; no exit marker. Both fail. The
probes fail at connect in about 0.2 ms, not after a timeout (E5–E9), and the log holds
an exit marker (E4). The judge's settling evidence: a listing of listening sockets on
TCP 8000 with the owning process id — outside this surface contract.

## Safe next steps

Read-only only.

- List the listening sockets on TCP 8000 and look for process id 4929 in the process
  list. An empty result closes the last doubt between "exited" and "alive without a
  listener".
- Read the operator-side and eval-side records for a call to `/simulate/crash` at
  15:26:39.673Z from the same machine. The telemetry does not name the sender.
- Read the supervisor or launcher configuration: is an automatic restart expected after
  an exit with code 1? The log shows none in the 2 minutes after the exit.
- Read `scripts/lab.sh status` output for the launcher's own view of the process.
- Look for older logs outside `lab/logs/` that cover the ten minutes before the
  complaint. The visible log covers 6.5 s.

## Gaps

- **No metrics.** `/metrics` fails at connect (E6). No uptime, memory, request or
  exception counters; saturation before the exit is not assessable.
- **Short log history.** The log starts at 15:26:33.690Z with no backups. "Fine ten
  minutes ago" cannot be checked. The visible process lived about 6.5 s, so an earlier
  process instance may have existed; the telemetry does not show one.
- **Unknown sender.** The crash request came from `127.0.0.1:53711` with an unstamped
  request id. It is not an investigator probe. The telemetry says nothing more.
- **No process or socket view.** The surface contract has no process listing. The exit
  status and the state of process 4929 were not observed.
- **"Not restarted" is bounded.** It holds up to 15:28:44Z (E9). The 25 s between E4
  and E5 have no probe.
- **User impact after the exit is inferred.** A process that is down logs nothing. The
  scope rests on investigator probes of three paths on IPv4 127.0.0.1:8000.
- **Two lenses skipped.** Software-defect: no `unhandled_exception` event and no 5xx in
  the 14 lines; the exit line comes from the logger `faultline.simulate` (E4).
  Interfaces: the lab has no boundary component, and the failure is at connect on the
  process's own address (E5–E9).
- **Unlisted event value.** `"event": "crash"` is not in the event list of
  `docs/lab.md`.
