---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-down-process-crash
  trigger: "manual (/konan human-report, fingerprint human-1793708825, startsAt 2026-11-03T12:27:05Z, trigger latency 12s)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-03T12:27:17Z
  concluded: 2026-11-03T12:31:09Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline server process (PID 33310) exited with code 1 at 12:26:48Z, commanded by an operator-surface request GET /simulate/crash, and was not restarted; nothing listens on 127.0.0.1:8000, so every connection is refused."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The server process exited with code 1 at ~12:26:48.5Z, triggered by the operator-surface request GET /simulate/crash, and was not restarted; no listener remains on 127.0.0.1:8000, so all connections are refused — a total outage from 12:26:48Z onward."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The process is still alive but does not serve requests (hang), which is why pages do not load."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E7, E8]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:26:41.944Z"
    quote: |-
      {"ts": "2026-11-03T12:26:41.944Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [33310]"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:26:45.902Z"
    quote: |-
      {"ts": "2026-11-03T12:26:45.902Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "b6365638d1e8", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.794, "client": "127.0.0.1:50651"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:26:47.962Z"
    quote: |-
      {"ts": "2026-11-03T12:26:47.962Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "2f3ad5e8580f", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 2.41, "client": "127.0.0.1:50652"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:26:48.464Z (final line of the file)"
    quote: |-
      {"ts": "2026-11-03T12:26:48.464Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "2f3ad5e8580f", "event": "crash", "delay": 0.5}
  - id: E5
    type: log
    source: "lab/logs/ directory listing and line count @ ~2026-11-03T12:28Z"
    quote: |-
      -rw-r--r--@ 1 lyudmylan  staff  3180 Nov  3 14:26 app.log
      14 lab/logs/app.log
  - id: E6
    type: probe
    source: "GET /health @ 2026-11-03T12:27:38Z, request_id=konan-1793708858-33387"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000180s request_id=konan-1793708858-33387
  - id: E7
    type: probe
    source: "GET /metrics @ 2026-11-03T12:27:39Z, request_id=konan-1793708859-33392"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000231s request_id=konan-1793708859-33392
  - id: E8
    type: probe
    source: "GET /health @ 2026-11-03T12:31:01Z, request_id=konan-1793709061-33490"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000179s request_id=konan-1793709061-33490
gaps:
  - "No process-table or socket-level view is in the surface contract, so 'exited and not restarted' rests on the log record and the connect-refusal signature, not on a direct process listing."
  - "lab/server.out (server stdout) is outside the investigator surface; the process exit code was not confirmed from stdout."
  - "/metrics was unreachable for the whole investigation (the service is down), so no metrics snapshot exists — uptime and request counters could not be read."
  - "The triage lens fan-out was skipped: the baseline evidence was deterministic (explicit crash log plus refused connections), and with the process down the only remaining telemetry is the static log, which was read in full (14 lines, E5)."
  - "The issuer of GET /simulate/crash is unknown beyond client 127.0.0.1:50652 (E3); the operator surface is outside the investigator's reach."
usage:
  model: claude-fable-5
  tokens: 585606
  wall_clock_seconds: 232
---

# Shop fully down: server process crashed after an operator-surface crash trigger and was not restarted

## Summary

**Root cause identified.** The faultline server process (PID 33310, started 12:26:41.944Z, E1)
exited with code 1 at ~12:26:48.5Z. The exit was commanded: a request `GET /simulate/crash`
(operator/eval surface, E3) produced the CRITICAL log line "crashing now: exiting with code 1"
(E4, same request_id `2f3ad5e8580f`). The process was not restarted — E4 is the last line the
service ever logged (E5) — so nothing listens on 127.0.0.1:8000 and every connection is refused
in under a millisecond (E6, E7, E8). That matches the complaint exactly: pages do not load at
all, and no error page appears, because no HTTP response of any kind is produced. Impact is
total: all endpoints, all users, from 12:26:48Z through at least 12:31:01Z (E8, the last
observation). Confidence is high — the causal chain is a single request_id from trigger to exit,
confirmed by the connect-refusal signature; the adversarial judge validated H1 and invalidated
the alternative.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 12:26:41.944Z | Server process 33310 starts; service comes up | E1 |
| 12:26:42–12:26:45.902Z | Healthy traffic: /health, /products, /products/1, POST /orders (201), GET /orders — all succeed | E2 |
| 12:26:47.962Z | `GET /simulate/crash -> 200` from client 127.0.0.1:50652 — operator-surface crash trigger | E3 |
| 12:26:48.464Z | CRITICAL "crashing now: exiting with code 1" — last log line ever written | E4, E5 |
| 12:27:05Z | Human complaint raised (`startsAt`) | — |
| 12:27:17Z | Investigation starts (trigger latency 12s) | — |
| 12:27:38–39Z | Baseline probes /health and /metrics: connection refused, HTTP 000 | E6, E7 |
| 12:31:01Z | Final probe /health: still refused | E8 |
| 12:31:09Z | Investigation concluded | — |

## Investigation

Trigger: manual `/konan` human report, normalized per `docs/triggers.md`:

```json
{
  "source": "human",
  "fingerprint": "human-1793708825",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-03T12:27:05Z"
}
```

Rounds as they ran:

1. **Baseline** — probes to /health and /metrics both failed at connect time (E6, E7); the log
   tail covered the service's entire 7-second life and ended in an explicit commanded exit
   (E1–E4). The log holds exactly 14 lines and has no rotated backups (E5), so the full history
   was read, not sampled.
2. **Triage** — skipped as fan-out: the baseline already contained deterministic, complete
   evidence for the process-lifecycle cause (an explicit crash event tied by request_id to its
   trigger, plus the no-listener refusal signature), and no other telemetry exists while the
   process is down. Recorded as a deliberate gap.
3. **Deep-dive** — skipped per the skill: a hypothesis whose triage evidence is already
   deterministic and complete goes straight to the judge.
4. **Judge** — a fresh subagent received only the hypotheses and verbatim evidence. Verdicts:
   H1 **validated** ("direct causal tie, not only a correlation in time"; the refusal in under
   1 ms on loopback means no socket is bound), H2 **invalidated** (a hung process keeps its
   listen socket; immediate refusal is the signature of no listener). The judge's caveat — the
   outage beyond 12:27:39Z was then a prediction — was answered with a final probe at 12:31:01Z
   (E8) before concluding.

Note on the complaint's framing ("fine ten minutes ago"): the service only came up at
12:26:41.944Z (E1) and died 7 seconds later. The reporter's timeline is approximate; the
telemetry's is not. Approximate token usage for this run was in the tens of thousands
(~70k orchestrator-side plus ~28k judge); the exact total could not be captured in this
manual session, hence `tokens: null`.

## Hypotheses

### H1 — commanded process exit, not restarted (validated)

The process exited with code 1 at ~12:26:48.5Z, triggered by `GET /simulate/crash`, and was
not restarted; no listener remains on port 8000. For: E3 and E4 share request_id
`2f3ad5e8580f` — the trigger and the exit are one causal chain, not a coincidence in time. E4
is the final line of the only log file (E5); a restart would have written a new startup marker
like E1, and none exists. E6, E7, and E8 show connect-time refusal (HTTP 000 in <1 ms) at
12:27:38Z, 12:27:39Z, and 12:31:01Z — no socket bound, for the whole observed window. Against:
nothing. Judge: validated.

### H2 — process alive but hung (invalidated)

If the process were hung, its listen socket would persist: connections would be accepted into
the backlog or time out, not be refused instantly. E6–E8 show immediate refusal — the
no-listener signature. E4 states an explicit exit and E5 shows all log output stopped at that
line. No evidence supports H2. Judge: invalidated.

## Safe next steps

Read-only; remediation is out of scope.

- Confirm the exit code from `lab/server.out` (operator-side; outside the investigator surface).
- Check the process table for PID 33310 and the listen state of port 8000 (operator-side) to
  close the judge's caveat with a direct observation.
- Identify what issued `GET /simulate/crash` from client 127.0.0.1:50652 (E3) in operator/eval
  records — the trigger came through the operator surface.
- After any operator action, a `/health` probe plus `process_uptime_seconds` and a fresh
  startup marker in the log will show recovery unambiguously.

## Gaps

- **No process/socket view in the contract.** The surface is probes, logs, metrics; "exited and
  not restarted" therefore rests on the log record (E4, E5) and the refusal signature (E6–E8),
  not a process listing. The judge accepted this chain while naming the direct listing as the
  evidence that would overturn it.
- **`lab/server.out` not read.** Server stdout is a lab runtime artifact, not one of the three
  investigator surface items, so the exit code was not confirmed there.
- **No metrics snapshot.** `/metrics` was down with the service for the entire investigation.
- **Lens fan-out skipped.** A deliberate choice, recorded per the skill: the baseline evidence
  was deterministic and complete, and the dead process leaves no live telemetry for other
  lenses to read beyond the 14-line log, which was read in full.
- **The trigger's issuer is unknown.** Only the client address 127.0.0.1:50652 is visible (E3);
  attribution beyond that lives on the operator surface.
