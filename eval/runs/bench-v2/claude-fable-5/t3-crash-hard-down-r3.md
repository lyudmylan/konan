---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-down-process-crash
  trigger: 'manual (/konan human-report, fingerprint human-1793709582, startsAt 2026-11-03T12:39:42Z; investigation start 2026-11-03T12:40:06Z, trigger latency 24s)'
  complaint: 'The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago.'
  started: 2026-11-03T12:40:06Z
  concluded: 2026-11-03T12:44:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'A GET /simulate/crash request at 12:39:27Z made the faultline process exit with code 1 at 12:39:28Z; no restart followed in the observed window, so nothing listens on 127.0.0.1:8000 and every connection is refused before any page or error page can be served.'
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: 'The service process deliberately exited with code 1 at 12:39:28Z, half a second after a GET /simulate/crash request, and was not restarted; with no listener on 127.0.0.1:8000, every connection is refused, so pages do not load and no error page appears.'
    incident_class: infra-process
    state: validated
    evidence_for: [E3, E4, E5, E1, E2, E8]
    evidence_against: []
  - id: H2
    statement: 'The network path between users and the shop broke (DNS, routing, firewall) while the process stayed up and serving.'
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E1, E8]
  - id: H3
    statement: 'The service''s own request-handling code raised an unhandled exception on some input and the process died from it.'
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E3, E9]
evidence:
  - id: E1
    type: probe
    source: '/health, request_id=konan-1793709626-33879, 2026-11-03T12:40:26Z'
    quote: 'curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn''t connect to server / -- HTTP 000 in 0.000165s request_id=konan-1793709626-33879'
  - id: E2
    type: probe
    source: '/metrics, request_id=konan-1793709627-33884, 2026-11-03T12:40:27Z'
    quote: 'curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn''t connect to server / -- HTTP 000 in 0.000186s request_id=konan-1793709627-33884'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:39:27.558Z'
    quote: '{"ts": "2026-11-03T12:39:27.558Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "4c8e89779cfc", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 2.104, "client": "127.0.0.1:50750"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:39:28.059Z (final line of the file; unchanged at re-check 12:42:20Z)'
    quote: '{"ts": "2026-11-03T12:39:28.059Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "4c8e89779cfc", "event": "crash", "delay": 0.5}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:39:21.547Z (first line of the file; no rotated backups exist)'
    quote: '{"ts": "2026-11-03T12:39:21.547Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [33803]"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:39:22.313Z'
    quote: '{"ts": "2026-11-03T12:39:22.313Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "75d02c76350e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.251, "client": "127.0.0.1:50746"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T12:39:24.429Z'
    quote: '{"ts": "2026-11-03T12:39:24.429Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "7632b89e460e", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.927, "client": "127.0.0.1:50748"}'
  - id: E8
    type: probe
    source: '/health, request_id=konan-1793709740-33946, 2026-11-03T12:42:20Z'
    quote: 'curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn''t connect to server / -- HTTP 000 in 0.000186s request_id=konan-1793709740-33946'
  - id: E9
    type: log
    source: 'lab/server.out, final line (no traceback or further output follows)'
    quote: '{"ts": "2026-11-03T12:39:28.059Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "4c8e89779cfc", "event": "crash", "delay": 0.5}'
gaps:
  - 'No telemetry exists from before 2026-11-03T12:39:21.547Z: E5 is the first line of app.log and no rotated backups exist. The claim "fine ten minutes ago" and any earlier instability cannot be checked from the surface.'
  - '/metrics was unreachable for the whole investigation (E2), so no counter, uptime, or chaos-flag snapshot exists.'
  - 'The identity of the caller of GET /simulate/crash (client 127.0.0.1:50750, request id not konan-stamped) is outside the investigator surface; /simulate is operator surface.'
  - 'The triage lens fan-out was collapsed into the baseline: the full log (14 lines) was read verbatim and the service accepted no connections. The software-defect and interfaces lenses were not spawned as agents; their domains were tested only as hypotheses H3 and H2. This is an accepted blind spot.'
  - '"Not restarted" is proven only inside the observed window, up to 12:42:20Z (E8).'
usage:
  model: claude-fable-5
  tokens: 812607
  wall_clock_seconds: 288
---

# Shop fully down: faultline process exited after a /simulate/crash request and was not restarted

## Summary

Verdict: root cause identified. The faultline process exited on purpose with code 1 at
12:39:28Z (E4), half a second after an operator-surface request `GET /simulate/crash`
(E3). Nothing restarted it: the log is frozen at the crash line (E4) and probes at
12:40:26Z and 12:42:20Z get an immediate TCP "connection refused" on 127.0.0.1:8000
(E1, E8). With no listener, a browser cannot receive even an error page — this matches
the complaint exactly. Impact: total unavailability of all endpoints from 12:39:28Z,
still in force at the conclusion of this investigation. Confidence: high; the judge
validated H1 and killed both alternatives on the cited evidence.

## Timeline

- 12:39:21.547Z — process 33803 starts; clean startup (E5).
- 12:39:22Z–12:39:25Z — healthy traffic: `/products` 200 (E6), `POST /orders` 201 (E7).
- 12:39:27.558Z — `GET /simulate/crash -> 200` from client 127.0.0.1:50750, request id
  not konan-stamped, so not investigator traffic (E3).
- 12:39:28.059Z — CRITICAL "crashing now: exiting with code 1", event `crash`; the log
  ends here (E4; same final line in server stdout, E9).
- 12:39:42Z — human complaint raised (trigger `startsAt`).
- 12:40:06Z — investigation start (trigger latency 24 s).
- 12:40:26Z / 12:40:27Z — probes to `/health` and `/metrics`: HTTP 000, "Couldn't
  connect to server" (E1, E2).
- 12:42:20Z — re-probe `/health`: still refused; log unchanged (E8).

## Investigation

Complaint object, verbatim, as synthesized by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1793709582",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago." },
  "startsAt": "2026-11-03T12:39:42Z"
}
```

Investigation start: 2026-11-03T12:40:06Z (trigger latency 24 s). No severity was
stated, so none was recorded.

Rounds as they ran:

1. **Baseline** — probes to `/health` and `/metrics` both failed at TCP connect (E1,
   E2). The full log was read: 14 lines, from startup at 12:39:21Z (E5) to the crash
   at 12:39:28Z (E4). Server stdout mirrors it (E9).
2. **Triage** — collapsed into the baseline: the entire telemetry surface was already
   in evidence and the target accepted no connections, so no lens agents were spawned
   (recorded as a gap). Three hypotheses were formed: H1 process down after the
   simulated crash, H2 network path failure, H3 unhandled exception in the target's
   own code.
3. **Deep-dive** — skipped per the loop contract: the triage evidence was
   deterministic and complete (the process logged its own exit; the port refuses
   connections). One persistence re-probe was taken at 12:42:20Z (E8).
4. **Judge** — a fresh judge agent saw only the hypotheses and the verbatim evidence:
   H1 validated, H2 invalidated, H3 invalidated. The judge's one open item for H3 (a
   stderr capture with no traceback) is satisfied by E9.

## Hypotheses

### H1 — process exited after /simulate/crash, not restarted (validated)

The chain has no gap: startup (E5), healthy service (E6, E7), the crash-trigger
request (E3), the self-announced exit 0.501 s later, matching its `delay: 0.5` field
(E4), then an empty log and immediate connection refusal on loopback at 12:40:26Z and
12:42:20Z (E1, E2, E8). A restart would write a new "Started server process" line
(the shape E5 shows); none exists. Both predictions held.

### H2 — network path failure (invalidated)

Requires the process up and serving. E4 shows the process announced its own exit, and
no request line follows it. The probes fail on 127.0.0.1 — the loopback address — in
under 1 ms with "connection refused" (E1, E8): a missing listener, not a path fault.
DNS, routing, or firewall failures cannot explain a refused connect on loopback.

### H3 — unhandled exception in the target's own code (invalidated)

The target emits `unhandled_exception` events with a `stack` field for its own
errors; none appears in the log. The exit is logged by `faultline.simulate` as a
deliberate act with event `crash` (E4), the trigger request was the operator surface
`/simulate/crash` and returned 200 (E3), and server stdout ends with the same crash
line and no traceback (E9).

## Safe next steps

Read-only suggestions; remediation is the operator's call:

- Ask the operator who or what issued `GET /simulate/crash` at 12:39:27Z from
  127.0.0.1:50750 (E3) — the request id is not konan-stamped, so it was not this
  investigation.
- Check eval-side (operator surface) whether a scenario or chaos state is active
  before any restart decision.
- Note for the operator: the lab has no supervisor that restarts the process; the
  outage persists until a manual start.
- After any restart, confirm `process_uptime_seconds` resets on `/metrics` and that a
  fresh startup marker appears in the log.

## Gaps

- **No pre-incident telemetry.** The log begins at the 12:39:21Z startup (E5) with no
  rotated backups, so the reported "fine ten minutes ago" cannot be verified, and
  earlier crashes or restarts are invisible to the surface.
- **No metrics snapshot.** `/metrics` never answered (E2), so uptime, request
  counters, and the chaos flag could not be read.
- **Caller identity.** Who called `/simulate/crash` is outside the investigator
  surface; only client address and an unstamped request id are visible (E3).
- **Lenses not spawned.** The triage fan-out was collapsed because the whole log was
  already in evidence and the target accepted no connections; the software-defect and
  interfaces domains were covered as hypotheses (H3, H2) rather than lens agents.
- **Restart window.** "Not restarted" holds for the observed window only, through
  12:42:20Z (E8).
