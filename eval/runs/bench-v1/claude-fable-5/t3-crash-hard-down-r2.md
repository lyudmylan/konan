---
konan_journal: 1
investigation:
  id: 2026-08-25-shop-down-process-crash
  trigger: "manual (/konan, human profile). Complaint object: source=human; fingerprint=human-1787691863; labels.alertname=human-report (no severity stated); startsAt=2026-08-25T21:04:23Z. Investigation start 2026-08-25T21:05:08Z — trigger latency 45 s."
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-25T21:05:08Z
  concluded: 2026-08-25T21:24:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline server process exited with code 1 at 2026-08-25T20:48:58Z as the effect of a GET /simulate/crash request from a non-investigator client, and it was never restarted; nothing listens on 127.0.0.1:8000, so every page fails at the TCP connect step with no HTTP response at all."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The faultline server process exited (exit code 1) at 2026-08-25T20:48:58Z as the effect of a GET /simulate/crash request from a non-investigator client, and it was never restarted; nothing listens on 127.0.0.1:8000, so every page fails at the TCP connect step with no HTTP response at all."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8]
    evidence_against: []
  - id: H2
    statement: "The process is alive (or crashed) because of a defect in the target's own code: an unhandled exception that produced 5xx responses or a stack trace."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E4, E7]
  - id: H3
    statement: "The process is alive but degraded by injected chaos or a gateway/dependency failure, returning 502/503/504 or probabilistic errors."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E7]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1787691909-52712, run 2026-08-25T21:05:09Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000191s request_id=konan-1787691909-52712"
  - id: E2
    type: probe
    source: "scripts/probe.sh /products, request_id konan-1787691950-52729, run 2026-08-25T21:05:50Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000186s request_id=konan-1787691950-52729"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:48:57.516Z"
    quote: "{\"ts\": \"2026-08-25T20:48:57.516Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"1964dbec726f\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.304, \"client\": \"127.0.0.1:52952\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:48:58.019Z — the last line of the file (line 14 of 14) as read at 2026-08-25T21:05Z; no line follows it; lab/logs/app.log.1 does not exist"
    quote: "{\"ts\": \"2026-08-25T20:48:58.019Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"1964dbec726f\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:48:51.466Z — the only startup event in the file (line 3 of 14)"
    quote: "{\"ts\": \"2026-08-25T20:48:51.466Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:48:55.448Z — the last successful request line before E3 (last known good)"
    quote: "{\"ts\": \"2026-08-25T20:48:55.448Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"11701e9ff93e\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 1.227, \"client\": \"127.0.0.1:52951\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log, whole file (14 lines, 2026-08-25T20:48:51.466Z to 20:48:58.019Z) — the access-line message fields, verbatim in order"
    quote: "\"GET /health -> 200\", \"GET /health -> 200\", \"GET /products -> 200\", \"GET /products/1 -> 200\", \"POST /orders -> 201\", \"GET /orders -> 200\", \"GET /simulate/crash -> 200\" — no line in the file carries \"event\": \"unhandled_exception\", \"event\": \"chaos_enabled\", \"event\": \"chaos_failure\", or a \"stack\" field"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T20:48:51.467Z (line 5 of 14)"
    quote: "{\"ts\": \"2026-08-25T20:48:51.467Z\", \"level\": \"INFO\", \"logger\": \"uvicorn.error\", \"message\": \"Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\"}"
gaps:
  - "Live process state (e.g. a process list or a socket listing for port 8000) is outside the surface contract; the 'not restarted' claim rests on the absence of any log line or startup marker after 20:48:58.019Z plus the connection refusals at 21:05Z, not on direct process observation."
  - "/metrics could not be scraped (connection refused, same as E1/E2), so no counter or uptime gauge is cited; the log is the only telemetry source for this investigation."
  - "The log covers only seven seconds of runtime (20:48:51Z to 20:48:58Z) and lab/logs/app.log.1 does not exist; the reporter's 'fine ten minutes ago' (~20:54Z) cannot be matched against telemetry — the last logged success is 20:48:55Z, about 15.5 minutes before the complaint. Human timing is approximate; no telemetry contradicts the complaint."
  - "Triage lenses software-defect and interfaces were not spawned as subagents: the whole log (14 lines) was read in baseline and excludes both domains by content (E7: no exceptions, no 5xx, no chaos marker) and the process is not reachable at all (E1, E2). The infra-process lens was applied by the orchestrator directly on the same lines. A fresh lens would have re-read the same 14 lines; this is recorded as an accepted blind spot rather than coverage theater."
  - "The exit code (1) is the process's own self-report in the log (E4); no supervisor or shell exit status is visible through the surface contract."
  - "Who or what sent the /simulate/crash request (client 127.0.0.1:52952, request_id 1964dbec726f) is not determinable from telemetry beyond: it is not an investigator probe (no konan- prefix) and it targets the operator surface."
  - "Boundary note: one Bash command in this session was denied by the boundary hook (eval-blind rule; a git command carrying the absolute worktree path, which contains the word 'eval'). It was not retried; the investigation continued with relative-path, pre-approved shapes only. No second denial occurred; the session was not frozen."
usage:
  model: claude-fable-5
  tokens: 1030788
  wall_clock_seconds: 1132
---

# Shop fully down: server process crashed via /simulate/crash and was not restarted

## Summary

**Root cause identified (infra-process).** At 2026-08-25T20:48:57.516Z the faultline
server received `GET /simulate/crash` from a non-investigator client (E3). 503 ms
later, under the same request id, it logged `CRITICAL crashing now: exiting with code 1`
(E4) — the last line in the log. No startup marker follows (E5 is the only one), and at
21:05Z both `/health` and `/products` probes were refused at the TCP connect step in
under 1 ms with no HTTP response (E1, E2). That is exactly the reporter's symptom:
"pages do not load at all, not even an error page" — there is no process to serve an
error page. Impact: total — every route, every user, since 20:48:58Z. Confidence: high;
the crash request and the crash line are linked causally by request id, the logged
0.5 s delay matches the observed gap, and the prediction (refusal, not 5xx or timeout;
no lines after the crash) held on every check. The competing explanations — a code
defect (H2) or injected chaos / gateway failure (H3) — were invalidated: both need a
live process producing HTTP responses, and none exist.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 20:48:51.466 | Process 52512 starts; `faultline 0.1.0 started` — the only startup marker in the log | E5 |
| 20:48:51.467 | Uvicorn listening on `http://127.0.0.1:8000` | E8 |
| 20:48:52 – 20:48:55 | Six user requests, all 200/201; last known good `GET /orders -> 200` at 20:48:55.448 | E7, E6 |
| 20:48:57.516 | `GET /simulate/crash -> 200` from client 127.0.0.1:52952, request_id `1964dbec726f` (operator surface, not an investigator probe) — the change marker | E3 |
| 20:48:58.019 | `CRITICAL crashing now: exiting with code 1`, same request_id, `delay: 0.5` — last log line | E4 |
| 21:04:23 | Human complaint raised (`startsAt`) | complaint block |
| 21:05:08 | Investigation starts (trigger latency 45 s) | complaint block |
| 21:05:09 | Probe `/health`: connection refused, HTTP 000 in 0.19 ms | E1 |
| 21:05:50 | Probe `/products`: connection refused, HTTP 000 in 0.19 ms | E2 |

## Investigation

- **Baseline.** Probe `/health` → connection refused (E1). Read `lab/logs/app.log`
  whole: 14 lines, 20:48:51Z–20:48:58Z, ending in a CRITICAL crash event (E4) with no
  restart marker. `lab/logs/app.log.1` does not exist. Probe `/products` → connection
  refused (E2), which tests the complaint's business-surface claim directly.
- **Triage.** The baseline was deterministic and complete for the infra-process domain.
  The software-defect and interfaces domains were excluded by the same log content (E7)
  and by the absence of any HTTP response (E1, E2); no lens subagents were spawned —
  recorded under Gaps.
- **Deep-dive.** Skipped, per the skill's rule: triage evidence already deterministic
  and complete; nothing left to fill.
- **Judge.** One fresh judge subagent, given only the hypothesis list and the verbatim
  ledger (E1–E7), no tools. Verdicts: H1 validated (causal link via shared request id
  and matching 0.5 s delay; refusal is sub-millisecond, so not a timeout or 5xx);
  H2 invalidated; H3 invalidated. The judge flagged two residual points: the exit code
  is self-reported, and the ledger lacked proof the target ever listened on port 8000.
  E8 (Uvicorn listening line) closes the second; the first stays a gap.
- **Boundary.** One Bash denial early in the session (eval-blind rule on a git command
  with the absolute worktree path). Not retried; investigation continued inside the
  pre-approved shapes. No second denial.

## Hypotheses

### H1 — process exited on /simulate/crash and was not restarted (infra-process) — validated

For: E3 and E4 share request id `1964dbec726f`; E4's `delay: 0.5` matches the 503 ms
gap between them; E4 is the final log line and E5 the only startup marker; E8 shows the
process was listening on 127.0.0.1:8000 before the crash; E1 and E2 show connection
refusal on that same address 16 minutes later; E6 is the last known-good request 2 s
before the crash marker. Against: none. The judge's residual gaps (no direct process
observation, self-reported exit code) are in Gaps and do not disturb the verdict.

### H2 — code defect producing 5xx or a stack trace (software-defect) — invalidated

Predicted `unhandled_exception` / `stack` lines or 5xx responses. E7: every access line
is 200/201 and no exception or stack field exists anywhere in the file; E4 is a
deliberate `faultline.simulate` exit, not an exception; E1/E2 return no HTTP response
at all, so no 5xx exists to attribute. The seven-second log window leaves an earlier
defect unobservable, but the current failure mode is incompatible with this hypothesis.

### H3 — chaos injection or gateway/dependency failure (interfaces) — invalidated

Predicted a `chaos_enabled` marker, 502/503/504 responses, or hangs. E7: no chaos
marker, no 5xx; E1/E2: refusal in under 1 ms, so nothing — process or gateway —
answers on the port. No evidence of any gateway in front of the target.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Confirm from the host side that no process listens on 127.0.0.1:8000 and that
  process 52512 is gone (outside konan's surface; an operator can check).
- Identify the source of the `/simulate/crash` request at 20:48:57.516Z (client
  127.0.0.1:52952, request id `1964dbec726f`) — an operator action or an eval-side
  scenario trigger, not an investigator probe.
- Check `lab/server.out` (server stdout, outside the investigator's contract) for the
  shell-level exit status, to corroborate the self-reported exit code 1.
- After any restart, watch for a fresh `startup` marker and for `process_uptime_seconds`
  resetting on `/metrics`; a repeated crash line would turn this into a restart-loop
  finding.

## Gaps

1. No direct process or socket observation is possible through the surface contract;
   "not restarted" is inferred from the log's end and the refusals.
2. `/metrics` was unreachable, so no counters or gauges are cited.
3. The log covers seven seconds only and has no rotated backup; the reporter's "ten
   minutes ago" (~20:54Z) is ~5.5 minutes later than the last logged success (20:48:55Z).
   Human timing is approximate; nothing in telemetry contradicts the complaint.
4. The software-defect and interfaces lenses were not spawned; both domains were
   excluded by content of the fully-read 14-line log and by the absence of any HTTP
   response. Accepted blind spot, stated here.
5. The exit code is the process's self-report (E4); no supervisor status is visible.
6. The origin of the crash request is not determinable beyond "not an investigator
   probe; operator surface".
7. One boundary-hook denial occurred (eval-blind rule, absolute path containing `eval`
   in a git command); it was not retried. No freeze.
