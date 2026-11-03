---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-down-process-crash
  trigger: "manual (/konan human-report, fingerprint human-1793709199, startsAt 2026-11-03T12:33:19Z; investigation start 2026-11-03T12:33:29Z, trigger latency 10s)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-03T12:33:29Z
  concluded: 2026-11-03T12:37:46Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline server process exited at 2026-11-03T12:33:06.392Z, 0.5 s after a localhost client's GET to the operator endpoint /simulate/crash returned 200; no restart followed, so nothing listens on 127.0.0.1:8000 and every connection attempt is refused — a total outage with no error page."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The server process deliberately exited (self-reported code 1) at 12:33:06.392Z after a request to /simulate/crash, and was not restarted; with no listener on 127.0.0.1:8000, all connections are refused."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "An in-target operational degradation switch is on and injects error statuses or latency, which makes pages fail to load."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7]
  - id: H3
    statement: "A proxy/gateway tier in front of a healthy application fails on its own, so users get no page although the app is up."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E5, E6, E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:32:59.839Z"
    quote: |-
      {"ts": "2026-11-03T12:32:59.839Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:32:59.840Z"
    quote: |-
      {"ts": "2026-11-03T12:32:59.840Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:33:03.824Z"
    quote: |-
      {"ts": "2026-11-03T12:33:03.824Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "9a6945c79cd7", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1.166, "client": "127.0.0.1:50703"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:33:05.891Z"
    quote: |-
      {"ts": "2026-11-03T12:33:05.891Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "b76be610dfbf", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.268, "client": "127.0.0.1:50704"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:33:06.392Z (final line of the log; the whole file is 14 lines, no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-03T12:33:06.392Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "b76be610dfbf", "event": "crash", "delay": 0.5}
  - id: E6
    type: probe
    source: "/health @ request_id konan-1793709220-33631 (2026-11-03T12:33:40Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000213s request_id=konan-1793709220-33631
  - id: E7
    type: probe
    source: "/metrics @ request_id konan-1793709226-33637 (2026-11-03T12:33:46Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000207s request_id=konan-1793709226-33637
  - id: E8
    type: probe
    source: "/health @ request_id konan-1793709463-33728 (2026-11-03T12:37:43Z)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000204s request_id=konan-1793709463-33728
gaps:
  - "Process-table and supervisor state could not be read: ps and scripts/lab.sh status are approval-gated in this non-interactive session. Process death is instead established from the log's final CRITICAL line (E5) plus connection-refused probes (E6-E8)."
  - "Triage lenses (infra-process, interfaces, software-defect) were not spawned: the target accepts no connections and the complete 14-line log corpus was already fully read at baseline, so no additional surface existed for a lens to examine. Their domains were covered by hypotheses H1-H3 and judged adversarially."
  - "The exit code 1 is self-reported by the process's own log line (E5); the observed exit status was not captured — server stdout (lab/server.out) ends at the same line."
  - "'Not restarted' is evidenced up to the last probe at 12:37:43Z (E8); no evidence covers time after that."
  - "Actor attribution for the /simulate/crash request is outside the telemetry surface: E4 shows only a localhost client (127.0.0.1:50704) without an investigator request-id stamp; who operated that client is unknown."
  - "/metrics was unreachable for the whole investigation (E7), so no counter or uptime readings exist for the baseline."
usage:
  model: claude-fable-5
  tokens: 1171353
  wall_clock_seconds: 257
---

# Shop total outage: server process exited after a /simulate/crash call and never came back

## Summary

Root cause identified. The faultline server process exited at 2026-11-03T12:33:06.392Z, half a second after a localhost client called the operator endpoint `GET /simulate/crash` (E4, E5 — same `request_id` b76be610dfbf links the request to the crash event). Nothing restarted it: probes at 12:33:40Z, 12:33:46Z, and 12:37:43Z all fail at the TCP level with "Couldn't connect to server" (E6–E8). With no listener on 127.0.0.1:8000, browsers get no response of any kind — which matches the complaint exactly: "pages do not load at all, not even an error page". Impact is total: 100% of requests fail at connection level from 12:33:06Z onward, still failing at conclusion (12:37:46Z). Confidence is high; the one soft spot is that the exit code (1) is the process's own announcement, not an observed exit status.

## Timeline

- 12:32:59.839Z — process start: "faultline 0.1.0 started" (E1); listener up on 127.0.0.1:8000 (E2).
- 12:33:00Z–12:33:03.824Z — healthy unstamped (end-user-side) traffic, all 200/201; last healthy request `GET /orders -> 200` (E3).
- 12:33:05.891Z — `GET /simulate/crash -> 200` from client 127.0.0.1:50704, request_id b76be610dfbf (E4). Operator-surface change marker.
- 12:33:06.392Z — CRITICAL "crashing now: exiting with code 1", same request_id, delay 0.5 (E5). Final log line; the log is silent after this.
- 12:33:19Z — human complaint raised (`startsAt`).
- 12:33:29Z — investigation start (trigger latency 10 s).
- 12:33:40Z / 12:33:46Z — `/health` and `/metrics` probes: connection refused, HTTP 000 (E6, E7).
- 12:37:43Z — final `/health` probe: still connection refused (E8).
- 12:37:46Z — concluded.

## Investigation

One round sufficed. Baseline probing found the target unreachable at TCP level (E6, E7), and the full log corpus — 14 lines, no rotated backups — fit in one read: a single process lifecycle from startup (E1) to a CRITICAL crash announcement (E5), with nothing after. Because the target accepted no connections and the whole corpus was already read, there was no additional surface for triage lenses to examine; the three lens domains (infra-process, interfaces, software-defect adjacent) were instead covered as explicit hypotheses H1–H3, and the skipped fan-out is recorded in Gaps. The deterministic evidence skipped deep-dive per the loop's skip rule and went straight to an adversarial judge, which saw only the hypothesis list and verbatim quotes. The judge validated H1 and invalidated H2 and H3, flagging four soft spots on H1 (self-reported exit code, restart window, two-probe generalization, actor attribution) — all adopted into Gaps and the root-cause statement, none changing the verdict. A final probe (E8) then extended the "not restarted" window to conclusion time.

## Hypotheses

### H1 — process exited and was not restarted (validated)

The chain is complete and request-id-linked: one process start (E1) with one listener on 127.0.0.1:8000 (E2); a request to `/simulate/crash` (E4); a CRITICAL "crashing now: exiting with code 1" carrying the same request_id b76be610dfbf 0.501 s later (E5), exactly matching the event's `delay: 0.5`; E5 is the final line of the complete corpus; and three probes over four minutes get no TCP connection at all on the app's own port (E6–E8). No listener and no response explains "not even an error page". Judge verdict: validated. The judge's qualifications: the exit code is self-reported (E5); "not restarted" is proven only up to E8; "every connection refused" generalizes from three probes (sound, since no listener exists); the caller of E4 is a localhost client on an operator endpoint — actor attribution stays soft.

### H2 — degradation switch injecting errors/latency (invalidated)

A switch that injects error statuses or latency needs a serving process: it returns HTTP responses, slow or erroneous. The probes got no TCP handshake at all, failing in under a millisecond (E6, E7). The final log event is a process exit, not an injection event, and no switch-enable event exists anywhere in the complete 14-line corpus (E5). Judge verdict: invalidated — incompatible with the observed failure mode, with a directly-evidenced alternative present. What would revive it: a probe that completes a TCP connection during the outage and receives an injected error response, or a log line showing the switch on.

### H3 — gateway tier failing in front of a healthy app (invalidated)

The hypothesis requires a healthy application behind a failing front. Two citations kill the premise: the application's own logger records its own exit (E5), and the probes target the application's own listener address directly — 127.0.0.1:8000, the address E2 names — with no tier in between, and the connection is refused (E6, E7). A gateway fault cannot produce connection refusal on the application's own socket. Judge verdict: invalidated. What would revive it: a direct probe of 127.0.0.1:8000 returning a healthy response concurrent with gateway-tier errors on the user path.

## Safe next steps

Read-only suggestions only:

- Re-probe `/health` periodically; a 200 plus a fresh `startup` event and a `process_uptime_seconds` reset in `/metrics` will mark the recovery time.
- After recovery, read the new log segment from startup onward to confirm a clean start and to catch any repeat call to the operator surface.
- Correlate the 12:33:05.891Z request from client 127.0.0.1:50704 (E4) with operator-side records outside this telemetry surface, to establish who or what called `/simulate/crash`.

## Gaps

- Process-table and supervisor state were out of reach: `ps` and `scripts/lab.sh status` are approval-gated in this non-interactive session. The process-death claim rests on E5 plus E6–E8, which are sufficient but indirect.
- No triage lenses were spawned. The target accepted no connections, `/metrics` was unreachable, and the complete 14-line log corpus was read at baseline — a lens had no surface left to examine. The lens domains were covered as hypotheses H1–H3 and judged adversarially; this is recorded as a deliberate, evidence-based skip, not an oversight.
- The exit code is self-reported (E5); `lab/server.out` ends at the same line, so the observed exit status is uncaptured.
- "Not restarted" holds up to 12:37:43Z (E8) only.
- Actor attribution for the crash-triggering request is outside the surface: only the client socket 127.0.0.1:50704 is known (E4).
- No metrics baseline exists: `/metrics` never answered during the investigation (E7).
