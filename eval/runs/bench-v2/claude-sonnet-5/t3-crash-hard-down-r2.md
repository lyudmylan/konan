---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-down-process-crash
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-02T22:41:20Z
  concluded: 2026-11-02T22:48:22Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline process crashed (exited with code 1) following a call to /simulate/crash and has not restarted since, leaving the entire service unreachable for all traffic."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The faultline process crashed (exited with code 1) 0.5s after a call to /simulate/crash and has not restarted since; every probe since (health and metrics alike) gets a TCP connection refusal, consistent with total, sustained outage."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: []
  - id: H2
    statement: "An internal degradation switch (chaos/feature toggle) injected the outage while the process stayed alive."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E5]
  - id: H3
    statement: "An unhandled exception in the target's own code crashed request handling."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3]
  - id: H4
    statement: "A boundary/gateway or upstream-dependency failure caused the outage rather than the app process itself."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:41:03.033Z"
    quote: "{\"ts\": \"2026-11-02T22:41:03.033Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"8ad59827ee5e\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 0.828, \"client\": \"127.0.0.1:61958\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:41:05.093Z"
    quote: "{\"ts\": \"2026-11-02T22:41:05.093Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"bbdca88b84ba\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 2.629, \"client\": \"127.0.0.1:61959\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:41:05.596Z (last line in the file)"
    quote: "{\"ts\": \"2026-11-02T22:41:05.596Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"bbdca88b84ba\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E4
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1793659329-9015"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000173s request_id=konan-1793659329-9015"
  - id: E5
    type: probe
    source: "scripts/probe.sh /metrics, request_id konan-1793659433-9055"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000185s request_id=konan-1793659433-9055"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:40:59.111Z (only startup marker in a 14-line file; no .1-.3 rotation backups exist)"
    quote: "{\"ts\": \"2026-11-02T22:40:59.111Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
gaps:
  - "Could not confirm process death at the OS level (e.g. a liveness/process check) — the investigator's surface contract (docs/lab.md) allows only probes and lab/ log reads, not OS-level process inspection. The judge named this as the one thing that would most cleanly settle residual doubt on H2; the log (E3) and the path-agnostic TCP refusals (E4, E5) were taken as sufficient without it."
  - "No distinct gateway/proxy layer's own logs exist to examine for H4; relied on E6 (port 8000 is faultline's own listening port, per its own startup log) and on docs/lab.md's statement that this lab has no distributed topology, rather than an independent gateway log."
  - "Could not determine who or what called /simulate/crash. /simulate/* is operator/eval surface, explicitly outside the investigator's reach by the lab's blinding contract (docs/lab.md), so the trigger's identity and intent could not be checked and were not needed for the mechanism finding."
  - "Only lab/logs/app.log was available (14 lines, single process lifetime since the one startup marker at 22:40:59.111Z, E6); no rotated backups (.1-.3) existed, so nothing before that startup could be examined — including whether the reporter's 'fine ten minutes ago' baseline corresponds to an earlier, unlogged process instance. The complaint's timing is taken as an approximate human estimate, not reconciled against telemetry."
usage:
  model: claude-sonnet-5
  tokens: 3902509
  wall_clock_seconds: 422
---

# Shop service: total outage from a process crash

## Summary

**Root cause identified.** The faultline process crashed and has not restarted: a request
to `/simulate/crash` returned 200 (E2), and 0.5 seconds later the process logged a CRITICAL
line announcing its own exit and then stopped logging entirely — no line follows it in the
file (E3). Every probe since, on two different paths (`/health` and `/metrics`), gets a raw
TCP connection refusal rather than any HTTP status (E4, E5) — exactly the shape of "pages do
not load at all, not even an error page" in the complaint, since nothing is listening on the
port to even render an error page. Three independent triage lenses (infra-process,
interfaces, software-defect) each read the same complete log and converged on this same
event while finding no evidence for a toggle, a code exception, or a boundary/gateway fault
in their own domains. An adversarial judge, given only the hypotheses and verbatim evidence,
validated the crash hypothesis and invalidated the three alternatives. Confidence: high.
Root cause: process crash (`infra-process` / `process-crashed`).

## Timeline (UTC)

- `22:40:59.111Z` — **E6**: faultline process starts (single startup marker; no restart
  since).
- `22:40:59.858Z`-`22:41:03.033Z` — normal traffic: health checks, product browsing, an
  order created and read back, all 200/201 (**E1** is the last of these).
- `22:41:05.093Z` — **E2**: `GET /simulate/crash -> 200`.
- `22:41:05.596Z` — **E3**: CRITICAL `"crashing now: exiting with code 1"`, `delay: 0.5` —
  same request id as E2. Last line in the log; nothing follows.
- `22:41:15Z` — human complaint received (fingerprint `human-1793659275`, `alertname:
  human-report`): "The shop is completely down for everyone... It was fine ten minutes
  ago."
- `22:41:20Z` — investigation started (5s trigger latency from complaint to start).
- `22:42:09Z` — **E4**: `/health` probe, connection refused.
- `22:43:53Z` — **E5**: `/metrics` probe, connection refused.
- `~22:42Z`-`~22:44Z` — the three triage lenses each independently re-probe `/health` and
  get the same connection-refused result, confirming the outage held steady across the
  whole triage round rather than flickering.
- `22:48:22Z` — investigation concluded.

## Investigation

1. **Baseline**: probed `/health` and `/metrics` (both connection-refused), then read
   `lab/logs/app.log` in full (14 lines, single process lifetime, no rotated backups).
   This alone surfaced the crash event and its trigger.
2. **Triage (discipline-parallel, all three lenses)**: spawned infra-process, interfaces,
   and software-defect lenses in parallel, each blind to the others, given only the lens
   file, the surface contract, the complaint verbatim, and the baseline summary.
   - infra-process: independently re-probed `/health` and `/metrics` (both refused),
     confirmed the single startup marker and the terminal crash line, concluded complete
     process death rather than degradation.
   - interfaces: found no gateway-shaped status (502/503/504) anywhere — only TCP refusal
     — and no `chaos_enabled`/`chaos_disabled`/`chaos_failure` markers, ruling out both a
     boundary fault and an internal toggle in its own domain.
   - software-defect: found no `unhandled_exception` event or `exception_type`/`stack`
     field anywhere in the log; confirmed the crash line is a deliberate, named exit
     rather than an exception surfacing from request handling.
3. **Deep-dive: skipped.** The crash log line (E3) ties directly to the preceding request
   (E2) by shared request id with a stated 0.5s delay, and three independent lenses found
   no competing anomaly in their own domains from the same complete log. Per the skill, a
   hypothesis whose triage evidence is already deterministic and complete goes straight to
   the judge.
4. **Judge** (adversarial, evidence-only, fresh agent, no lens reasoning given): validated
   H1, invalidated H2, H3, and H4, each from the same six-item evidence ledger, and named
   one piece of evidence that would most cleanly settle residual doubt (an OS-level process
   check) — out of the investigator's surface contract, noted under Gaps.

## Hypotheses

### H1 — process crash via /simulate/crash, no restart (validated)

E2 and E3 share request id `bbdca88b84ba`: E2 records the call, E3 records the exit 0.5s
later with the delay the exit event itself names. E3 is the last line in the file, which a
truly dead process would produce. E4 and E5 are TCP-level refusals, not HTTP error codes, on
two different paths — refusal at the socket level is path-agnostic evidence that nothing is
listening, generalizing to all traffic rather than one route. E6 is the only startup marker
in the file, with no rotated backups to hide a second one, supporting "has not restarted."
The judge found every clause traceable to a specific, unforced reading of the evidence, with
nothing cited against it.

### H2 — internal degradation switch, process stayed alive (invalidated)

E3 is a CRITICAL log announcing the process's own exit — the opposite of staying alive — and
E4/E5 are connection-refused, not an HTTP status a live process behind a toggle would still
return. The judge named an OS-level liveness check as the one thing that would remove all
residual doubt; that check is outside the investigator's surface (see Gaps).

### H3 — unhandled exception in the target's own code (invalidated)

E3's logger (`faultline.simulate`) and message (`"crashing now: exiting with code 1"`, with
a staged `delay`) read as a deliberate, scripted self-termination, not an exception
surfacing from business logic — which would carry an `exception_type`/`stack` field instead.
E1 shows clean request handling two seconds earlier, and E2 ties the crash to a deliberately
invoked simulation endpoint rather than a normal code path.

### H4 — boundary/gateway or upstream-dependency failure (invalidated)

E4 and E5 are failures to establish a TCP connection to the app's own port, not an
HTTP 502/503/504 a gateway would return while its upstream was unreachable. E6 confirms
port 8000 is faultline's own listening port, not a separate gateway process. The judge
noted this doesn't positively prove no gateway exists anywhere — only that the observed
failure is fully explained at the app's own port, with no gateway/proxy log in evidence
either way.

## Safe next steps

- Re-probe `/health` periodically (read-only) to detect a restart, since nothing in the
  current evidence shows one occurring.
- If the lab is restarted, grep `lab/logs/app.log` going forward for a second `"faultline
  0.1.0 started"` line and diff request volume before/after to confirm clean recovery.
- No remediation performed or suggested here — restarting the process is an operator
  action outside the investigator's read-only surface.

## Gaps

- Could not confirm process death at the OS level (e.g. a liveness/process check) — the
  surface contract allows only probes and `lab/` log reads, not OS-level process
  inspection. The judge named this as the one thing that would most cleanly settle
  residual doubt on H2; the log (E3) and the path-agnostic TCP refusals (E4, E5) were
  taken as sufficient without it.
- No distinct gateway/proxy layer's own logs exist to examine for H4; relied on E6 (port
  8000 is faultline's own listening port) and on `docs/lab.md`'s statement that this lab
  has no distributed topology, rather than an independent gateway log.
- Could not determine who or what called `/simulate/crash`. `/simulate/*` is operator/eval
  surface, explicitly outside the investigator's reach by the lab's blinding contract, so
  the trigger's identity and intent could not be checked and were not needed for the
  mechanism finding.
- Only `lab/logs/app.log` was available (14 lines, single process lifetime since the one
  startup marker at `22:40:59.111Z`, E6); no rotated backups (`.1`-`.3`) existed, so
  nothing before that startup could be examined — including whether the reporter's "fine
  ten minutes ago" baseline corresponds to an earlier, unlogged process instance. The
  complaint's timing is taken as an approximate human estimate, not reconciled against
  telemetry.
