---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-total-outage
  trigger: "manual (/konan, human report; fingerprint human-1793697802, alertname human-report, no severity stated; startsAt 2026-11-03T09:23:22Z, investigation start 2026-11-03T09:23:31Z, trigger latency 9s)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-03T09:23:31Z
  concluded: 2026-11-03T09:28:04Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The service process terminated itself during a GET to the operator endpoint /simulate/crash and nothing restarted it, so no socket is bound to port 8000 and every later connection is refused at the TCP layer — which is why callers see no page at all rather than an error page."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The process exited as the direct result of a GET to the operator endpoint /simulate/crash; with no listener bound, every subsequent connection is refused before HTTP, producing a total outage with no error page."
    incident_class: infra-process
    state: validated
    evidence_for: [E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "The process is still running but became unreachable at the network layer (rebind, bind failure, firewall or listener change), so requests never arrive."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E10, E11]
    evidence_against: [E9]
  - id: H3
    statement: "A live process is failing at the application level (dependency loss, exception storm, resource exhaustion), and users are seeing failed responses."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E5, E6, E7, E10, E11]
  - id: H4
    statement: "The reported symptom is unrelated to the recorded exit, because the reporter places normal service ten minutes earlier while this process instance existed for only 6.5 seconds."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:04.074Z"
    quote: '{"ts": "2026-11-03T09:23:04.074Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [26377]"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:04.075Z"
    quote: '{"ts": "2026-11-03T09:23:04.075Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:04.814Z"
    quote: '{"ts": "2026-11-03T09:23:04.814Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "d8f03157c8d9", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 11.99, "client": "127.0.0.1:65523"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:04.841Z"
    quote: '{"ts": "2026-11-03T09:23:04.841Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "8551db63225b", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.144, "client": "127.0.0.1:65525"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:05.897Z"
    quote: '{"ts": "2026-11-03T09:23:05.897Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "46c267d39b21", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.026, "client": "127.0.0.1:65526"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:06.949Z"
    quote: '{"ts": "2026-11-03T09:23:06.949Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "ef5291746ee4", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.787, "client": "127.0.0.1:65527"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:08.008Z"
    quote: '{"ts": "2026-11-03T09:23:08.008Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "64a80cf02db3", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1.021, "client": "127.0.0.1:65528"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:10.069Z"
    quote: '{"ts": "2026-11-03T09:23:10.069Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "bdf12f3c5533", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.25, "client": "127.0.0.1:65529"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:23:10.571Z — final line of the file"
    quote: '{"ts": "2026-11-03T09:23:10.571Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "bdf12f3c5533", "event": "crash", "delay": 0.5}'
  - id: E10
    type: probe
    source: "/health, request_id konan-1793697816-26458"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000184s request_id=konan-1793697816-26458"
  - id: E11
    type: probe
    source: "/products, request_id konan-1793697823-26471"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000183s request_id=konan-1793697823-26471"
gaps:
  - "\"Process is dead\" is not fully separated from \"process is alive with no listening socket\" by evidence inside the surface contract. E10/E11 refuse in 0.0002s, which proves there is no listening socket or an active reject rule; E9 is the process announcing its own exit before it happens, not a record that the exit completed. The decisive checks — a pid liveness check on the pid in lab/faultline.pid and a listener check on port 8000 — are host inspection, outside the telemetry surface of docs/lab.md, so they were not run."
  - "Everything before 2026-11-03T09:23:04.074Z is unobserved. app.log begins at that startup line (E1) and no rotated backups (.1-.3) exist, so the reporter's \"fine ten minutes ago\" cannot be checked against telemetry, and it is not known whether E1 is a first start or a restart. The absence of earlier lines is an instrumentation gap, not evidence of quiet."
  - "No end-user traffic appears anywhere in the observed window. The only non-investigator requests are the contiguous local sequence E3-E8. The outage is total as a service state, but the count of failed real user requests observable in telemetry is zero — \"down for everyone\" is not corroborated by user-traffic evidence."
  - "The caller of the operator endpoint (E8) is identified only negatively: request id bdf12f3c5533 carries no konan- prefix, so it was not an investigator probe. The access line records client 127.0.0.1 and no user agent, headers or forwarded-for, and a local proxy tier would also present as 127.0.0.1, so caller identity beyond \"not the investigator\" is not established."
  - "/metrics could not be scraped because nothing is listening, so this instance has no counter, uptime or RSS snapshot. The metric lens is a blind spot for the whole investigation."
  - "Triage lenses were not fanned out. The baseline itself produced a request-id-linked exit marker that explains the exact reported symptom, so the hypothesis went to the judge directly per the skill's deterministic-evidence rule. Lenses not consulted, and therefore accepted blind spots: load-saturation, data-db, interfaces, third-party."
usage:
  model: claude-opus-5
  tokens: 735403
  wall_clock_seconds: 273
---

# Shop total outage — the service process exited and nothing restarted it

## Summary

**Root cause identified.** The service is not failing requests; it is absent. At
2026-11-03T09:23:10.069Z a GET arrived on the operator endpoint `/simulate/crash`
(E8), and 502 ms later the same request id wrote a CRITICAL line announcing its own
exit (E9). That line is the last line in the log. Read-only probes 26 and 33 seconds
later are refused at the TCP layer in under 0.0002 s with no HTTP status at all
(E10, E11), and neither probe left a log line. That is exactly the shape of the
reported symptom: no process is bound to the port, so there is nothing left to
serve an error page. The outage is total rather than partial, and the mechanism is
process death, not an application fault — class `infra-process`, cause
`process-crashed`.

Confidence is high on the mechanism and on the fact that nothing is serving. One
link is weaker than it looks and is recorded as a gap: E9 is the process speaking
about its own future, written before the exit, so within the declared telemetry
surface "exited" is self-reported. The checks that would close it — a pid liveness
check and a listener check — are host inspection rather than target telemetry, so
they were deliberately not run.

Two cautions for whoever acts on this. First, the request that killed the process
came in on the operator surface, which `docs/lab.md` places outside the
investigator's probe allowlist; a shopper browsing the site has no route to it, so
the call was deliberate. It was not investigator traffic — the crash request id
carries no `konan-` prefix, unlike E10 and E11 — but nothing in telemetry
identifies who did make it. Second, no real user traffic appears anywhere in the
observed window, so "down for everyone" is confirmed as service state and
uncorroborated as user impact.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 09:23:04.074 | Process 26377 starts; this is the first line of the log — nothing before it is observable | E1 |
| 09:23:04.075 | Listening on `http://127.0.0.1:8000` | E2 |
| 09:23:04.814 | First request, `GET /health` 200, 11.99 ms — a cold first call, the rest run near 1 ms | E3 |
| 09:23:04.841 – 09:23:08.008 | Business surface healthy end to end: `/products` 200, `/products/1` 200, `POST /orders` 201, `GET /orders` 200. No 5xx, no exception events, anywhere in the file | E4, E5, E6, E7 |
| 09:23:10.069 | `GET /simulate/crash -> 200`, request id `bdf12f3c5533`, client `127.0.0.1:65529` — the operator surface, reached by a deliberate call | E8 |
| 09:23:10.571 | CRITICAL `"crashing now: exiting with code 1"`, same request id, `delay: 0.5` matching the 502 ms gap. **Log ends here** | E9 |
| 09:23:22 | Human reports the shop down — 11.4 s after the exit marker | complaint `startsAt` |
| 09:23:31 | Investigation starts (trigger latency 9 s) | — |
| 09:23:36 | Probe `/health`: connection refused, HTTP 000 in 0.000184 s, no log line written | E10 |
| 09:23:43 | Probe `/products`: connection refused, HTTP 000 in 0.000183 s, no log line written | E11 |

No configuration-change, deploy or flag-change marker appears in the window. The
only state-changing event in the log is the operator call at 09:23:10.069.

## Investigation

**Baseline (step 1)** was itself decisive, which shaped everything after it. The
first probe of `/health` could not establish a baseline at all — it was refused
before HTTP (E10) — so the baseline came from the log tail instead, which turned
out to contain a healthy run, an operator call, an explicit exit marker, and then
nothing.

**Triage (step 2) was deliberately not fanned out.** The skill's rule is that a
hypothesis whose evidence is already deterministic and complete skips ahead rather
than being re-proved, and the exit marker is tied to the killing request by shared
request id (E8, E9) and explains the precise reported symptom, including the
absence of an error page. Spawning six lenses against a dead port would have been
coverage theater: with nothing listening, no lens can gather anything. The lenses
not consulted are recorded as accepted blind spots under Gaps rather than silently
dropped.

**Deep-dive (step 3)** was skipped for the same reason, and the budget went instead
to the adversarial judge.

**Judge (step 4)** received the four hypotheses and the verbatim ledger with no
narrative, and did real work rather than blessing the obvious. It upheld H1's
mechanism while splitting off the "exit code 1" clause as self-reported, since E9
is written before the exit and no supervisor record or exit status is in the
ledger. It flagged that the still-present pid file proves nothing — a pid file
survives an abrupt exit — so that item was dropped from the support for H1 rather
than counted. It narrowed the force of the refused connections: an instant refusal
excludes a silent drop but not a reject rule, so H2 is invalidated on the exit
marker and the missing bind error, not on the refusals alone. It also caught a
miscount in the ledger as first drafted (six access lines described as five),
corrected here. H3 it invalidated on genuinely discriminating grounds: the probes
fail at connect, so no HTTP layer was reached, and a live application failing
inside itself would complete the handshake and return a 5xx.

**Conclusion (step 5).** Every residual question the judge named is answerable only
with host inspection outside the surface contract, so a second round would have
bought nothing. One round, one judge, concluded.

## Hypotheses

### H1 — process exited on the operator call → **validated**

The causal tie is the shared request id `bdf12f3c5533` across E8 and E9: these are
not two events that happen to sit near each other in time, they are one request.
The `delay: 0.5` field in E9 agrees with the 502 ms wall gap between the two lines.
Downstream, E10 and E11 refuse at connect with no HTTP status and leave no log
line, and E9 is the file's final line. The reported symptom — "not even an error
page" — matches a refused connection and does not match a served 5xx.

Against: nothing observed. The honest weakness is not counter-evidence but a
missing confirmation: E9 announces the exit rather than recording it, so within the
declared surface the completion of the exit is inferred from the refusals, and the
refusals are also consistent with a reject rule in front of a live process. Held as
a gap, not as an invalidation.

### H2 — alive but unreachable at the network layer → **invalidated**

Its first prediction fails outright: an exit marker exists (E9). Its second fails
too: no new log lines appeared for either probe request id. No bind error or
listener-change line appears before the file ends. Note the limit of this kill, per
the judge: the absence of probe log lines does not discriminate between H1 and a
firewall reject, because in both cases the application never sees the request. The
refusals (E10, E11) are listed as evidence *for* H2 for exactly that reason — they
are consistent with it — and H2 falls on E9 instead.

### H3 — application-level failure in a live process → **invalidated**

Here the evidence discriminates cleanly. E10 and E11 fail at the connect step, so
no HTTP layer was reached at all; a live process failing internally completes the
TCP handshake and then returns an error or hangs. And no 5xx and no
`unhandled_exception` event appears anywhere in the file: E3 through E7 are all
2xx, and even E8 is a 200. The window is only 6.5 s, which is thin, but the
TCP-level refusal carries this verdict without needing more.

### H4 — symptom unrelated to the exit → **invalidated as stated**

The inference does not hold. The 6.5 s bounds *one process instance* (pid 26377),
while the complaint is about the service. The present state the reporter describes
matches E10 and E11 exactly, and that match holds whatever came before. The
reporter's "ten minutes ago" is an uncalibrated human estimate made 11.4 s after
the exit marker; it cannot be reconciled with this instance's lifetime, and it
cannot be checked at all, because no telemetry exists before E1. Treating the
mismatch as a reason to dismiss the connection would be reading an instrumentation
gap as a finding.

## Safe next steps

Read-only, in the order that resolves the most uncertainty per step.

1. Close the one soft link in the chain with two host-level read-only checks, which
   sit outside the investigator's surface and so belong to an operator: a liveness
   check on the pid in `lab/faultline.pid`, and a listener check on port 8000. A
   dead pid with no listener closes H1 completely; a live pid with no listener
   reopens H2. Distinguish a reaped pid from a zombie, since a zombie also refuses
   connections.
2. Establish whether the process is expected to be restarted by anything. Nothing
   restarted it in the 33 s between the exit marker and the last probe, and a
   single request taking the whole service down with no recovery is the operationally
   significant property here, independent of what triggered it.
3. Retrieve the full request record for `bdf12f3c5533` from whatever audit surface
   exists outside the app log — user agent, headers, true remote address — to settle
   who called the operator endpoint. The access line alone cannot.
4. Check whether `app.log` is truncated at each start, which decides whether earlier
   instances existed and their history was discarded. That single fact determines
   whether the reporter's "ten minutes ago" is checkable even in principle, and it
   is the cheapest fix to the largest blind spot in this investigation.
5. Note for the monitoring surface rather than for this incident: `/health` returned
   200 eleven times faster than the steady-state calls on its first invocation (E3),
   a cold-start signature. It is not evidence of a fault and is listed only so a
   later reader does not mistake it for one.

## Gaps

The six entries in the machine core, in short: the exit is self-reported and the
checks that would confirm it lie outside the surface contract; the period before
09:23:04.074Z is unobserved rather than quiet, with no rotated backups to consult;
no end-user traffic appears in the window, so total unavailability is a service
state here and not a measured user impact; the caller of the operator endpoint is
identified only as "not the investigator"; `/metrics` was unscrapable because
nothing is listening, leaving the metric lens blind for the entire investigation;
and five of six triage lenses were never consulted, which was a deliberate choice
against a dead port rather than an oversight, but is a blind spot all the same.
