---
konan_journal: 1
investigation:
  id: 2026-08-25-shop-down-process-crash
  trigger: "manual (/konan, human profile) — complaint object: source=human, fingerprint=human-1787694117, labels.alertname=human-report, startsAt=2026-08-25T21:41:57Z; investigation start 2026-08-25T21:58:35Z; trigger latency 998 s"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-25T21:58:35Z
  concluded: 2026-08-25T22:36:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline process exited (logged as 'crashing now: exiting with code 1') 0.5 s after a GET /simulate/crash request that did not carry the investigator's konan- stamp, and nothing restarted it, so port 8000 refuses every connection and users get no page at all."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The faultline process exited with code 1 at 21:41:39.437Z, 0.5 s after a non-investigator GET /simulate/crash request (id eb15dc0affb1), and was never restarted; port 8000 therefore refuses every connection, which is why users see no page and no error page."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8, E9, E11]
    evidence_against: []
  - id: H2
    statement: "An unhandled exception in the application's own code crashed the process."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E10]
  - id: H3
    statement: "A dependency failure or a chaos/configuration change makes the service return errors to users."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3, E10]
  - id: H4
    statement: "The process is in a restart loop, crashing and restarting repeatedly."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E9, E11]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1787695115-53053, 2026-08-25T21:58:35Z"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000182s request_id=konan-1787695115-53053
  - id: E2
    type: probe
    source: "scripts/probe.sh /metrics, request_id konan-1787695116-53059"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000189s request_id=konan-1787695116-53059
  - id: E3
    type: probe
    source: "scripts/probe.sh /products, request_id konan-1787695145-53082"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000186s request_id=konan-1787695145-53082
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T21:41:38.936Z"
    quote: |-
      {"ts": "2026-08-25T21:41:38.936Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "eb15dc0affb1", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.509, "client": "127.0.0.1:53099"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T21:41:39.437Z (final line of the file)"
    quote: |-
      {"ts": "2026-08-25T21:41:39.437Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "eb15dc0affb1", "event": "crash", "delay": 0.5}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T21:41:32.875Z"
    quote: |-
      {"ts": "2026-08-25T21:41:32.875Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T21:41:36.865Z (last known-good request)"
    quote: |-
      {"ts": "2026-08-25T21:41:36.865Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "6e40c351bfeb", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.909, "client": "127.0.0.1:53095"}
  - id: E8
    type: log
    source: "wc -l lab/logs/app.log, read 2026-08-25T21:58Z; lab/logs/ holds only app.log, no .1–.3 backups"
    quote: "      14 lab/logs/app.log"
  - id: E9
    type: log
    source: "grep -c '\"event\": \"startup\"' lab/logs/app.log ; grep -c '\"event\": \"crash\"' lab/logs/app.log"
    quote: |-
      1
      1
  - id: E10
    type: log
    source: "lab/logs/app.log, all 14 lines, read 2026-08-25T21:58Z — status distribution and absence checks"
    quote: "status 200 x7, 201 x1; zero lines matching unhandled_exception, exception_type, stack, simulated_exception, chaos_enabled, chaos_disabled, chaos_failure; zero 4xx/5xx statuses"
  - id: E11
    type: log
    source: "ls -la lab/logs, read 2026-08-25T21:58Z (local time Aug 26 00:41 = 21:41Z)"
    quote: "-rw-r--r--@ 1 lyudmylan  staff  3181 Aug 26 00:41 app.log"
gaps:
  - "/metrics is unreachable (E2), so process_uptime_seconds, process_max_rss_bytes, faultline_chaos_enabled and all request counters could not be read; the verdict rests on probes and logs only."
  - "The exit status itself was not observed — E5 records the process's logged intent ('exiting with code 1'); the surface contract exposes no supervisor or process-table view, so 'process not running' is inferred from connection refused (E1–E3) plus log silence (E5, E8, E11)."
  - "stderr is not part of the surface; a traceback written only to stderr would be invisible. lab/server.out mirrors app.log and shows nothing after the crash line, which narrows but does not close this gap."
  - "Whether the app echoes the investigator's konan-* request id into its access lines was not observable in this log (no investigator probe reached a live server); the 'non-investigator' attribution of eb15dc0affb1 rests on the probe.sh stamping contract in docs/lab.md and the absence of the konan- prefix."
  - "Lenses for load-saturation, third-party and data-db do not exist in this repo (only infra-process, software-defect, interfaces); their domains were not swept by a dedicated lens. Connection refused on the service's own port (E1–E3) makes them unlikely for this incident but they were not independently checked."
  - "Trigger latency was 998 s and the judge step needed three attempts (two API failures while the host slept); the wall clock of 2245 s reflects that, not the evidence-gathering time (~1 minute)."
usage:
  model: claude-fable-5
  tokens: 1172049
  wall_clock_seconds: 2245
---

# Shop fully down: faultline process exited after a /simulate/crash request and was never restarted

## Summary

**Verdict: root cause identified (H1, infra-process).** The faultline process stopped at
2026-08-25T21:41:39.437Z. The log shows a `GET /simulate/crash` request (E4) followed 0.5 s
later by a CRITICAL `crash` event, "crashing now: exiting with code 1" (E5). That is the
last line the service ever wrote (E8, E11). No startup marker follows (E9), so nothing
restarted the process. As a result port 8000 refuses every connection: `/health`,
`/metrics` and `/products` all return `HTTP 000` / "Couldn't connect to server" (E1–E3).
This matches the complaint exactly — no page and no error page, because no process is
listening. Impact: 100 % of users, every route, from 21:41:39Z until now (still down at
the last probe). Confidence: high — the evidence is deterministic and the three
alternative hypotheses were killed by direct evidence. The crash request did not carry
the investigator's `konan-` stamp, so this is user-side (or operator-side) traffic, not a
probe artefact.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 21:41:32.875Z | Process starts; `faultline 0.1.0 started` (the only startup marker) | E6, E9 |
| 21:41:33–21:41:36.865Z | Healthy traffic: all routes 200/201, ~1 ms; last known-good `GET /orders -> 200` | E7, E10 |
| 21:41:38.936Z | `GET /simulate/crash -> 200`, request id `eb15dc0affb1`, client 127.0.0.1:53099 | E4 |
| 21:41:39.437Z | CRITICAL `crash`: "crashing now: exiting with code 1" — final log line; file mtime freezes at 21:41 | E5, E8, E11 |
| 21:41:57Z | Human complaint raised (`startsAt`) | complaint block |
| 21:58:35Z | Investigation starts; `/health` refused (`HTTP 000`) | E1 |
| 21:58:36–21:58:45Z | `/metrics` and `/products` refused | E2, E3 |
| 22:36:00Z | Concluded; service still down at last probe | — |

No `chaos_*` or other configuration-change markers exist in the log (E10).

## Investigation

- **Baseline** (21:58:35–21:58:45Z): three probes, all connection refused (E1–E3); log
  tail read in full — 14 lines, one startup, one crash, nothing after (E5, E6, E8, E9);
  `lab/server.out` mirrors the log; no rotated backups.
- **Triage**: three lenses spawned in parallel, blind to each other — infra-process,
  software-defect, interfaces. All three converged: process exit after `/simulate/crash`,
  no restart, no exceptions, no gateway statuses, no chaos markers. Each lens ran one
  extra `/health` (and one `/products`) probe; all refused.
- **Deep-dive**: skipped — the triage evidence was deterministic and complete, so the
  hypotheses went straight to the judge (per the investigate skill).
- **Judge** (adversarial, evidence-only; third attempt after two API failures):
  H1 validated; H2, H3, H4 invalidated. The judge flagged two soft sub-claims in H1
  (exit status not directly observed; konan-id echo not proven) — both recorded under
  Gaps — and one settling check for H4 (log mtime vs. crash time), which E11 satisfies.

## Hypotheses

### H1 — process exited after `/simulate/crash`, never restarted (infra-process) — validated

For: E4 and E5 share request id `eb15dc0affb1`, 0.501 s apart, matching `"delay": 0.5`.
E5 is the final line (E8); the file mtime equals the crash minute (E11); there is exactly
one startup and one crash event (E9), so no restart happened. Every probe 17 minutes
later is refused at the TCP level (E1–E3), which is what a dead listener looks like.
Against: none.

### H2 — unhandled exception in application code (software-defect) — invalidated

Against: zero `unhandled_exception`, `exception_type` or `stack` fields anywhere in the
log (E10); the exit is announced by the `faultline.simulate` logger as a deliberate
`crash` event (E5), not by an exception handler.

### H3 — dependency failure or chaos/config change returning errors (interfaces) — invalidated

Against: users and probes receive no HTTP response at all (E1–E3, `HTTP 000`); a
dependency or chaos failure would answer with a status (5xx). No `chaos_*` markers and
no 4xx/5xx in the log (E10).

### H4 — restart loop (infra-process) — invalidated

Against: one startup marker and one crash event (E9); the log ends at the crash and its
mtime has not moved since 21:41 (E8, E11). A loop would produce fresh startup lines.

## Safe next steps

Read-only suggestions only:

- Check the host's process table / listener list for port 8000 to confirm directly that
  no faultline process exists (outside konan's surface; for the operator).
- Identify the origin of client `127.0.0.1:53099` that issued `GET /simulate/crash` at
  21:41:38.936Z (E4) — the operator surface should not be reachable by end users.
- Review whether a supervisor is expected to restart the service; the log shows none
  acted.
- After any operator restart, re-probe `/health` and `/metrics` and confirm a fresh
  `startup` marker and a reset `process_uptime_seconds`.

## Gaps

- No metrics snapshot exists for the incident (E2 refused), so uptime, RSS and counters
  are unavailable; nothing in the verdict depends on them.
- The exit status is the process's logged intent, not an observed exit code; the surface
  contract has no supervisor or process view.
- stderr is outside the surface; `lab/server.out` (mirroring app.log) shows no extra
  output, which narrows the gap but does not close it.
- Echo of `konan-*` ids in access lines was not observable in this log; attribution of
  `eb15dc0affb1` as non-investigator traffic rests on the stamping contract in
  `docs/lab.md` and the missing prefix.
- No dedicated lenses exist for load-saturation, third-party or data-db; connection
  refused on the service's own port makes them unlikely here, but they were not swept.
- Trigger latency 998 s and two judge-agent API failures inflated the wall clock to
  2245 s; evidence gathering itself took about one minute.
