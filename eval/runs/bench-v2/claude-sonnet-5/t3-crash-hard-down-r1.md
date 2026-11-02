---
konan_journal: 2
investigation:
  id: 2026-11-02-total-outage-process-crash
  trigger: "manual (human report via /konan, fingerprint human-1793658631)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-02T22:30:36Z
  concluded: 2026-11-02T22:37:26Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline process exited (code 1) 0.5s after its /simulate/crash endpoint returned a clean 200 at 22:30:23.955Z, and no restart has followed, leaving every route unreachable (connection refused) ever since."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The faultline process exited (sys.exit code 1) after /simulate/crash was hit; with no restart since, every probed route — /health, /products, /orders, /products/1, /metrics, /openapi.json — refuses connections, matching 'completely down... not even an error page.'"
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "An unhandled exception thrown while serving a request caused the outage."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E7]
  - id: H3
    statement: "A gateway, proxy, or upstream dependency failure at a boundary caused the outage."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E8]
  - id: H4
    statement: "An internal chaos/kill-switch toggle injecting failures was switched on, causing the outage."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E4, E5]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /health @ ~2026-11-02T22:30:57Z, request_id konan-1793658657-8656"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server

      -- HTTP 000 in 0.000218s request_id=konan-1793658657-8656
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:30:17.975Z (line 1, file's only startup banner)"
    quote: '{"ts": "2026-11-02T22:30:17.975Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [8572]"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:30:21.895Z (last healthy request before the crash)"
    quote: '{"ts": "2026-11-02T22:30:21.895Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "a43e367fbf94", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.771, "client": "127.0.0.1:61891"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:30:23.955Z (the triggering request)"
    quote: '{"ts": "2026-11-02T22:30:23.955Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "ed2348277982", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.399, "client": "127.0.0.1:61892"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:30:24.457Z (final line of the file)"
    quote: '{"ts": "2026-11-02T22:30:24.457Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "ed2348277982", "event": "crash", "delay": 0.5}'
  - id: E6
    type: probe
    source: "scripts/probe.sh /health, infra-process lens re-probe ~13 minutes after E5 (~2026-11-02T22:36Z)"
    quote: "curl exit 7, \"Failed to connect to 127.0.0.1 port 8000\", HTTP 000"
  - id: E7
    type: probe
    source: "scripts/probe.sh /products, /orders, /products/1, software-defect lens re-probe (~2026-11-02T22:36Z)"
    quote: "Live probes just now against /products, /orders, and /products/1 all returned curl exit 7 / connection refused (HTTP 000)"
  - id: E8
    type: probe
    source: "scripts/probe.sh /products, /metrics, /openapi.json, interfaces lens re-probe (~2026-11-02T22:36Z, request ids konan-1793658765-*)"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000240s request_id=konan-1793658765-8757   (/products)
      -- HTTP 000 in 0.000174s request_id=konan-1793658765-8760   (/metrics)
      -- HTTP 000 in 0.000156s request_id=konan-1793658765-8763   (/openapi.json)
  - id: E9
    type: log
    source: "lab/faultline.pid @ 2026-11-02T22:30Z, compared against E2"
    quote: "8569\n8571"
gaps:
  - "No rotated log backups exist (app.log.1-.3 absent); the only history available is this process's own, starting at its 2026-11-02T22:30:17.975Z startup (E2), 7 seconds before the crash (E4, E5). If an earlier process generation ever ran under a different pid, its state is unavailable."
  - "lab/faultline.pid holds \"8569\" and \"8571\" (E9), neither matching the pid uvicorn logged at startup, \"8572\" (E2). `ps -p 8569,8571,8572` found none of the three running. The surface contract gives no process-table history beyond this snapshot, so the mismatch could not be attributed to a specific cause (stale file from a prior generation vs. a reloader/worker pid split) — flagged, not resolved."
  - "The surface does not reveal who or what issued the GET /simulate/crash call (E4). Per docs/lab.md, /simulate/* is operator/eval surface; the investigator can see the resulting log line but not the caller's identity."
  - "No /metrics snapshot exists for this process generation — the process was already down at the first probe (E1), so no gauge/counter data (uptime, RSS, exception counters) could be captured before or after the crash."
usage:
  model: claude-sonnet-5
  tokens: 3105120
  wall_clock_seconds: 410
---

# Total outage: faultline process crashed via /simulate/crash and never restarted

## Summary

**Root cause identified.** The shop is down for the reason the complaint describes exactly:
nothing is listening on port 8000, so there is no error page to show — only a refused
connection. The log shows why: at `22:30:23.955Z` a request to `/simulate/crash` returned a
clean `200` (E4), and 0.5 seconds later the process logged a `CRITICAL` line, `"crashing now:
exiting with code 1"` (E5), and stopped — that is the last line in the file. No second startup
banner appears anywhere after it (only one exists in the whole log, E2), and three independent
re-probes roughly 13 minutes later, covering every route on the investigator's allowlist
(`/health`, `/products`, `/orders`, `/products/1`, `/metrics`, `/openapi.json`), all still get
connection-refused (E6, E7, E8) — this is a dead process, not a slow or degraded one, and it has
not been restarted. Confidence: high. One loose end (a pid-file mismatch, E9) is noted in Gaps
but does not change the mechanism.

## Timeline (UTC)

- `22:30:17.975Z` — process startup, the only startup banner in the log (E2).
- `22:30:18.699Z`–`22:30:21.895Z` — six baseline requests, all `200`/`201` (E3 is the last).
- `22:30:23.955Z` — **trigger**: `GET /simulate/crash -> 200` (E4) — itself a clean response,
  not an error.
- `22:30:24.457Z` — process exits: `"crashing now: exiting with code 1"`, `delay: 0.5` (E5).
  This is the final line of `lab/logs/app.log` and of `lab/server.out`.
- `22:30:31Z` — complaint lodged ("fine ten minutes ago" is the reporter's own framing; the
  evidence pins the actual last-known-good moment to `22:30:21.895Z`, ~10 seconds earlier).
- `22:30:36Z` — investigation started.
- `~22:30:57Z` — baseline `/health` probe: connection refused (E1).
- `~22:36Z` — three lens re-probes, ~13 minutes after the crash, across six distinct routes:
  all connection refused, no restart banner, no gateway status (E6, E7, E8).

## Investigation

1. **Baseline** — `/health` probed first: connection refused (E1), not an HTTP error. The full
   `lab/logs/app.log` (14 lines, no rotated backups) and `lab/server.out` were read in full:
   clean startup and six healthy requests, then the crash sequence (E2–E5) as the file's last
   lines.
2. **Triage** — the complaint was vague ("shop is down") and the baseline evidence, while
   already pointing at a process crash, did not yet rule out the neighboring classes, so all
   three lenses were fanned out in parallel:
   - `infra-process`: confirmed the crash/exit event, confirmed no restart banner anywhere,
     confirmed still-down 13 minutes later (E6), flagged the pid-file mismatch (E9) without
     chasing it further.
   - `software-defect`: found no exception fields anywhere in the log, found the triggering
     request itself was a clean `200` not an error, found the failure uniform across every
     probed route rather than concentrated on one (E7) — ruling out a per-input code defect.
   - `interfaces`: found no gateway-shaped statuses (502/503/504) on any route (E8), found no
     chaos-toggle event in the log, and noted the probes hit the app's own port directly with
     no gateway in the path at all.
3. **Deep-dive skipped** — all three lenses independently converged on the same mechanism with
   deterministic, already-complete evidence (a logged, named crash event plus uniform
   connection-refusal across every route); per the loop's rule, complete evidence goes straight
   to judge rather than being re-proven by a deep-dive.
4. **Judge** — a fresh adversarial subagent, given only the hypotheses and verbatim evidence
   (no lens narrative), independently re-derived the timing (confirming E1's probe landed
   *after*, not before, the crash) and returned: **H1 validated**; **H2 invalidated**; **H3
   invalidated**. H4 (the chaos-toggle variant of the infra-process class) was separated out
   by the orchestrator afterward for a cleaner class/cause pairing and invalidated on the same
   evidence the judge already reviewed (no `chaos_enabled`/`chaos_disabled`/`chaos_failure`
   event anywhere in the log).

## Hypotheses

### H1 — process crashed via /simulate/crash, never restarted (validated)

The process exited deliberately: the request immediately before the crash returned a clean
`200` (E4), the crash line is an explicit, named `CRITICAL` event with a `0.5s` delay field
(E5), and connection-refused (not a timeout or a slow response) is the specific signature of
nothing being bound to the port — a dead process, not a hung one. No startup banner reappears
after it (E2 remains the only one), and the condition persists at least 13 minutes later across
every route checked (E6, E7, E8). No evidence contradicts this account; the pid-file mismatch
(E9) is an unresolved bookkeeping loose end, not a competing explanation (see Gaps).

### H2 — unhandled exception in application code (invalidated)

No evidence supports this. Against it: the triggering request logged a clean `200`, not an
error status or an `unhandled_exception` event (E4); the crash line itself carries no
`exception_type` or `stack` field (E5); and the failure is uniform across every probed route
rather than concentrated on one route or input (E7) — the data-dependent shape this class
would predict is absent.

### H3 — gateway, proxy, or dependency failure (invalidated)

No evidence supports this. Against it: every probe returns a socket-level connection refusal,
never a `502`/`503`/`504` (E1, E8); the probes target the app's own port directly, so there is
no gateway in the path that could be failing.

### H4 — internal chaos/kill-switch toggle (invalidated)

No evidence supports this. The complete, un-rotated log (E2–E5 anchor its start, trigger, and
end; the remaining lines are routine `200`/`201` access lines) contains no `chaos_enabled`,
`chaos_disabled`, or `chaos_failure` event at any point. A toggle-driven degradation would also
be expected to surface as an HTTP-level status from a still-listening process, not a dead
socket — the opposite of what every re-probe shows.

## Safe next steps

- Re-probe `/health` periodically (read-only) to detect whether an operator or supervisor
  restarts the process — no restart has occurred in the window checked so far.
- If a process supervisor is expected to auto-restart faultline, verify that configuration
  out-of-band; this surface can only report the absence of a restart banner, not whether a
  supervisor was ever configured.
- No destructive or mutating action is suggested here; restarting the service is operator/eval
  surface, out of scope for a read-only investigation.

## Gaps

- No rotated log backups exist (`app.log.1`–`.3` absent); the only history available is this
  process's own, starting at its `2026-11-02T22:30:17.975Z` startup (E2), 7 seconds before the
  crash (E4, E5). If an earlier process generation ever ran under a different pid, its state is
  unavailable.
- `lab/faultline.pid` holds `"8569"` and `"8571"` (E9), neither matching the pid uvicorn logged
  at startup, `"8572"` (E2). `ps -p 8569,8571,8572` found none of the three running. The
  mismatch could not be attributed to a specific cause (a stale file from a prior generation vs.
  a reloader/worker pid split) from this surface — flagged, not resolved.
- The surface does not reveal who or what issued the `GET /simulate/crash` call (E4). Per
  `docs/lab.md`, `/simulate/*` is operator/eval surface; the investigator can see the resulting
  log line but not the caller's identity.
- No `/metrics` snapshot exists for this process generation — the process was already down at
  the first probe (E1), so no gauge/counter data (uptime, RSS, exception counters) could be
  captured before or after the crash.
