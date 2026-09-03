---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-down-crash
  trigger: manual
  complaint: 'The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago.'
  started: 2026-08-19T03:32:18Z
  concluded: 2026-08-19T03:38:38Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'A GET /simulate/crash request drove the faultline process to log a crash-exit intent and stop listening on port 8000, and nothing restarted it, producing a total, sustained outage.'
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: 'The faultline server stopped responding to requests (connection refused on port 8000) after handling a GET /simulate/crash request; the application logged intent to crash-exit (code 1) 0.502s later via the same request_id, and no further log activity (startup, request, or otherwise) occurred across a 4-minute observation window with three independent /health probes all refused — consistent with the crash killing the listening process and nothing restarting it.'
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:32:07.550Z'
    quote: '{"ts": "2026-08-19T03:32:07.550Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "6e8ce3fc1bb4", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.419, "client": "127.0.0.1:55674"}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:32:08.052Z (last line in file; file is 14 lines total)'
    quote: '{"ts": "2026-08-19T03:32:08.052Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "6e8ce3fc1bb4", "event": "crash", "delay": 0.5}'
  - id: E3
    type: probe
    source: 'scripts/probe.sh /health, request_id konan-1787110351-41960, ~2026-08-19T03:32:31Z'
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000221s request_id=konan-1787110351-41960"
  - id: E4
    type: probe
    source: 'scripts/probe.sh /health, request_id konan-1787110386-41994, ~2026-08-19T03:32:59Z'
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000201s request_id=konan-1787110386-41994"
  - id: E5
    type: log
    source: 'lab/logs/app.log, re-checked 2026-08-19T03:36:13Z (4 minutes after E2)'
    quote: 'file line count unchanged at 14 lines; last line unchanged, still: {"ts": "2026-08-19T03:32:08.052Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "6e8ce3fc1bb4", "event": "crash", "delay": 0.5}'
  - id: E6
    type: probe
    source: 'scripts/probe.sh /health, request_id konan-1787110575-42083, ~2026-08-19T03:36:15Z'
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000183s request_id=konan-1787110575-42083"
gaps:
  - 'Did not fan out the interfaces and software-defect triage lenses. Baseline evidence (E1-E2) already showed a deterministic crash-exit log tied by request_id to the triggering request, and E3/E4 confirmed a TCP-level connection refusal (nothing listening), not an HTTP-level error — a fully dead listener precludes app-level contract or data-dependent explanations, since there is no live process left to exhibit them. Treated as a deliberate scope decision rather than an unexamined blind spot.'
  - 'Could not determine who or what issued the GET /simulate/crash request. /simulate/* is operator/eval surface, outside docs/lab.md''s investigator-visible surface; only its logged effect (E1, E2) is observable, not its origin or intent.'
  - 'Could not formally cite the process-table check (ps -p on the pid recorded in lab/faultline.pid and lab/server.out) as ledger evidence — the process died, corroborating E2, but the schema''s evidence types (log/metric/probe) have no category for process-table observations, so it is corroborating context only, not a citation.'
  - 'The complaint states the shop "was fine ten minutes ago," but the application log history begins at the 2026-08-19T03:32:01.543Z startup marker, only ~7 seconds before the crash-triggering request (E1) and about 17 seconds before this investigation started. No earlier telemetry exists to confirm or reconcile the "ten minutes" framing; the complaint is treated as approximate, untrusted symptom text, not a timestamp.'
  - 'The exact mechanism behind the crash-exit (e.g. os._exit, an uncaught exception propagating out of the ASGI loop, or something else) is not evidenced — E2 only records the application''s own logged intent to exit, not an externally observed process exit status.'
usage:
  model: claude-sonnet-5
  tokens: 2287760
  wall_clock_seconds: 380
---

# Shop-wide outage: faultline process crash-exit after /simulate/crash

## Summary

**Root cause identified.** The faultline service is completely down because the server
process stopped listening on port 8000 after handling a `GET /simulate/crash` request:
the application logged a crash-exit intent (`"crashing now: exiting with code 1"`,
event `crash`) 0.502s after that request completed, tied to it by a shared
`request_id` (E1, E2). Every probe against `/health` since — three of them, spanning a
4-minute window — was refused at the TCP level (`curl: (7) ... Couldn't connect to
server`, E3/E4/E6), and the application log has not grown a single new line in that
same window (E5): no restart, no new startup marker, nothing. This matches the report
exactly — total, sudden unreachability, not even an error page, because nothing is
listening to serve one. Confidence is high: the causal chain is a direct request/crash
correlation by request_id, and the "nothing since" evidence rules out a transient blip
or an in-progress restart.

## Timeline (UTC)

- `2026-08-19T03:32:01.543Z` — faultline process starts (`Uvicorn running on
  http://127.0.0.1:8000`), per `lab/server.out`/`lab/logs/app.log` startup lines.
- `2026-08-19T03:32:02Z`–`03:32:05Z` — normal traffic: `/health`, `/products`,
  `/products/1`, `POST /orders`, `/orders` all return 200/201 with sub-2ms durations.
- `2026-08-19T03:32:07.550Z` (**E1**) — `GET /simulate/crash -> 200`,
  `request_id=6e8ce3fc1bb4`.
- `2026-08-19T03:32:08.052Z` (**E2**) — CRITICAL: `"crashing now: exiting with code
  1"`, same `request_id`, `delay: 0.5`. Last line in `lab/logs/app.log`.
- `2026-08-19T03:32:15Z` — human complaint received (`startsAt`).
- `2026-08-19T03:32:18Z` — investigation started.
- `~2026-08-19T03:32:31Z` (**E3**) — first `/health` probe: connection refused.
- `~2026-08-19T03:32:59Z` (**E4**) — second `/health` probe, ~35s later: connection
  refused again.
- `2026-08-19T03:36:13Z` (**E5**) — log file re-checked: still 14 lines, no growth.
- `~2026-08-19T03:36:15Z` (**E6**) — third `/health` probe, ~4 min after the crash log:
  connection refused again.
- `2026-08-19T03:38:38Z` — investigation concluded.

## Investigation

**Baseline**: attempted `/health` — connection refused immediately (before any other
telemetry was pulled), which itself is the first, strongest signal: the health
endpoint being unreachable at the TCP level (not a 5xx) is the "healthy-monitoring
trap" inverted — there is no green endpoint here at all. Pulled `lab/server.out` and
`lab/logs/app.log` next; both end mid-timeline with a CRITICAL crash log immediately
after a `/simulate/crash` request (E1, E2). Checked `lab/faultline.pid` and the pid
uvicorn logged at startup — none of the recorded pids have a live process (`ps -p`
returns nothing for any of them), corroborating the crash but not formally citable
under the evidence taxonomy (log/metric/probe only).

**Triage**: skipped the discipline-parallel lens fan-out. The baseline evidence was
already deterministic — a crash-exit log line correlated by `request_id` to its
trigger, plus a TCP-level (not HTTP-level) connection refusal confirming nothing is
listening at all. A dead listener gives the `interfaces` and `software-defect` lenses
nothing to query; there is no live process left to exhibit a contract violation or a
data-dependent defect. This is recorded as a deliberate scope decision (see Gaps), not
unexamined coverage.

**Deep-dive**: skipped per protocol — the hypothesis's evidence was already
deterministic and complete from baseline.

**Judge**: two rounds. First round (H1 stated with a specific pid and an asserted OS
exit code) came back **inconclusive** — the judge correctly flagged that the pid and
"exited with code 1" were not actually in the cited evidence (only in uncited `ps`
context), and that a 23-second gap between the crash log and the first probe was
unevidenced. H1 was tightened to claim only what E1-E6 directly show (crash-exit
*intent* logged, not a confirmed OS exit code; no pid asserted; outage scoped to the
observed window) and two additional data points were gathered (E5, E6) to close the
"no restart" gap with a 4-minute observation window instead of a single pair of
probes. Second round: **validated**, with the judge independently re-reading the
source files to check quote fidelity.

## Hypotheses

### H1 — crash-exit after `/simulate/crash`, no restart (validated)

Statement: the server stopped listening after a `GET /simulate/crash` request; the
app logged crash-exit intent 0.502s later via the same request_id; no further log
activity or restart occurred across a 4-minute window with three refused `/health`
probes.

For: E1 (triggering request), E2 (crash-intent log, same request_id), E3/E4/E6 (three
independent connection-refused probes spanning ~4 minutes), E5 (log file unchanged
across that same window — no restart marker appeared).

Against: none found.

The judge noted, and I agree, that the exact kill mechanism (clean `os._exit` vs. an
uncaught exception vs. something else) is not evidenced — only the application's own
logged intent to exit is. The hypothesis is worded to claim exactly that and no more.

## Safe next steps

- Re-probe `/health` periodically (read-only) to detect if/when the service comes back
  without investigator action, and note the recovery timestamp if it does.
- If the lab is meant to auto-restart faultline on crash, check that supervision
  mechanism's own status/logs (outside this investigator's surface) — this journal
  only establishes that no restart occurred within the observed window, not why.
- Correlate `request_id=6e8ce3fc1bb4` against the eval harness / operator-side
  scenario log (outside `docs/lab.md`'s investigator surface) to confirm whether the
  crash was scenario-injected rather than externally triggered.

## Gaps

- Did not fan out the `interfaces` and `software-defect` triage lenses — see
  Investigation above; a TCP-level connection refusal on a dead listener leaves no
  live process for either lens to query, so it was excluded with evidence rather than
  skipped blind.
- Could not determine who or what issued `GET /simulate/crash` — `/simulate/*` is
  operator/eval surface outside the investigator-visible contract; only its logged
  effect is observable.
- The process-table check (dead pids in `lab/faultline.pid`/`server.out`) corroborates
  E2 but has no home in the log/metric/probe evidence taxonomy, so it rides along as
  context, not a citation.
- The complaint's "was fine ten minutes ago" cannot be reconciled against telemetry:
  the application's own log history starts only ~7 seconds before the crash-triggering
  request. Treated as approximate, untrusted symptom text.
- The precise crash mechanism (clean exit vs. exception vs. signal) is not evidenced —
  only the application's logged intent to exit is.
