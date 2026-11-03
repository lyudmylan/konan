---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-down-process-exit
  trigger: "manual — /konan, human profile (docs/triggers.md); complaint startsAt 2026-11-03T09:11:36Z, investigation entered 2026-11-03T09:11:48Z, trigger latency 12 s"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-03T09:11:48Z
  concluded: 2026-11-03T09:20:10Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The serving process (pid 26013) logged a commanded exit through the target's operator-surface crash route at 09:11:27.227Z and never logged a restart, so nothing accepts a TCP connection on 127.0.0.1:8000 and every request now fails at connect, before any HTTP status can exist."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The target process terminated by a commanded self-exit at 2026-11-03T09:11:27.227Z and nothing restarted it; with no listener on 127.0.0.1:8000 every request fails at TCP connect, so no HTTP response — not even an error page — is produced."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own application code (an unhandled exception on some request) caused the outage."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E8]
  - id: H3
    statement: "A boundary or dependency tier failed on its own — a proxy/gateway tier, an upstream dependency, or injected probabilistic degradation at an edge."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E5, E6, E9, E10, E11]
  - id: H4
    statement: "Demand exceeded the target's capacity (resource exhaustion, queueing, worker starvation) and the process died or stopped serving under load."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E8, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:20.723Z (line 1 of 14)"
    quote: '{"ts": "2026-11-03T09:11:20.723Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [26013]"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:20.724Z (line 3 of 14; the only startup event in the retained log)"
    quote: '{"ts": "2026-11-03T09:11:20.724Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:20.724Z (line 5 of 14)"
    quote: '{"ts": "2026-11-03T09:11:20.724Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:21.491Z (line 8 of 14)"
    quote: '{"ts": "2026-11-03T09:11:21.491Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "7291cb918e0e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.164, "client": "127.0.0.1:65459"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:23.604Z (line 11 of 14)"
    quote: '{"ts": "2026-11-03T09:11:23.604Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8bae036b57b2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.991, "client": "127.0.0.1:65461"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:24.661Z (line 12 of 14; last end-user request served)"
    quote: '{"ts": "2026-11-03T09:11:24.661Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "ece3b9cb440d", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.832, "client": "127.0.0.1:65462"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:26.725Z (line 13 of 14; access line for a route docs/lab.md classifies as operator/eval surface, which scripts/probe.sh refuses mechanically)"
    quote: '{"ts": "2026-11-03T09:11:26.725Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "fdedaa58aaa9", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.098, "client": "127.0.0.1:65463"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:11:27.227Z (line 14 of 14; the last line in the file)"
    quote: '{"ts": "2026-11-03T09:11:27.227Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "fdedaa58aaa9", "event": "crash", "delay": 0.5}'
  - id: E9
    type: probe
    source: "/health, request id konan-1793697128-26096, run 2026-11-03T09:12:08Z"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000213s request_id=konan-1793697128-26096
  - id: E10
    type: probe
    source: "/products, request id konan-1793697150-26106, run 2026-11-03T09:12:30Z"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000195s request_id=konan-1793697150-26106
  - id: E11
    type: probe
    source: "/openapi.json, request id konan-1793697413-26258, run 2026-11-03T09:16:53Z"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000185s request_id=konan-1793697413-26258
  - id: E12
    type: probe
    source: "/metrics, request id konan-1793697413-26263, run 2026-11-03T09:16:53Z"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000205s request_id=konan-1793697413-26263
  - id: E13
    type: log
    source: "lab/logs/ state, read twice — 2026-11-03T09:11:50Z and 2026-11-03T09:16:57Z — byte-identical both times"
    quote: |-
      14 lab/logs/app.log
      -rw-r--r--@ 1 lyudmylan  staff  3182 Nov  3 11:11 app.log
gaps:
  - "No telemetry exists before 2026-11-03T09:11:20.723Z. lab/logs/ holds app.log only; the rotation backups .1–.3 that docs/lab.md names do not exist (E13), so the retained window is 6.504 s wide and the reporter's \"fine ten minutes ago\" (≈09:07Z) can be neither confirmed nor contradicted — an earlier process generation that served fine cannot be distinguished from no process at all."
  - "/metrics is unreadable while the target is down (E12), so process_uptime_seconds and process_max_rss_bytes could not corroborate the lifecycle or rule resource pressure in or out from gauges. H4 was killed on traffic counts and log content, not on gauge data."
  - "No OS-level evidence of the exit. \"exiting with code 1\" is the process's own log text (E8), not a process-table entry, supervisor record, or exit status. docs/lab.md (\"The investigator's surface — all of it\") lists probes, lab/logs/app.log and /metrics only, so lab/server.out and lab/faultline.pid were deliberately not read although both exist on disk and server.out would likely carry the shell-level exit. Widening the surface is a contract change, not an investigator's call."
  - "\"Down for everyone\" is not established. All four probes came from one host over loopback (E9–E12). Path-independence is established across four allowlisted paths and the failure is at TCP connect, so it is path-shaped; vantage-point independence was never testable from inside this surface."
  - "Socket state was not inspected directly: a refused connect was not distinguished from a packet filter or a rejecting listener, because lsof/netstat-class evidence is outside the surface contract."
  - "The actor behind the crash request is unidentified. E7 records only client 127.0.0.1:65463, with no auth or user field. The evidence places it outside investigator traffic — scripts/probe.sh refuses that route mechanically, and konan request ids begin only at 09:12:08Z, after the exit — but says nothing about who or what sent it."
  - "The last negative observation is 09:16:53Z (E11, E12), with the log unchanged at 09:16:57Z (E13). The target's state after that time was not probed."
usage:
  model: claude-opus-5
  tokens: 1707716
  wall_clock_seconds: 502
---

# Shop unreachable: the serving process exited on command and never came back

## Summary

**Root cause identified, high confidence: the process is dead, not degraded.** At
2026-11-03T09:11:27.227Z the target logged `crashing now: exiting with code 1`
(E8) and wrote nothing further — that line is the last of 14 in the log. The exit
was commanded, not spontaneous: it is tied by a shared `request_id`
(`fdedaa58aaa9`) to a GET on the target's operator-surface crash route 502 ms
earlier (E7), and the gap matches that line's own `"delay": 0.5`. Nothing
restarted the process: the log holds exactly one startup marker (E1, E2) and was
byte-identical 5.5 minutes after the exit (E13). Four probes on four allowlisted
paths, spanning 09:12:08Z to 09:16:53Z, all failed at TCP connect with
`HTTP 000` (E9–E12).

That failure mode explains the complaint precisely, including its strangest
detail. `HTTP 000` after a refused connect means no HTTP exchange happened at
all — there is no process to serve an error page, which is why the reporter saw
none. It also means user impact is invisible in the target's own logs: the last
logged end-user request succeeded (E6), and every user request after the exit
fails before reaching anything that could log it. The shop was healthy right up
to the exit — six end-user requests, all 200/201, 0.832–12.047 ms (E4, E5, E6) —
so there is no degradation ramp, no error spike, and no failing route to chase.

Two scoping limits belong in the same breath as the verdict. The exit **code** is
the process's own claim about itself, quoted from the log, not an OS exit status
(E8). And "it was fine ten minutes ago" is unverifiable: the retained log begins
6.504 s before the exit, with no rotated backups (E13), so nothing covers ~09:07Z.
The reporter's interval is also roughly half the real one — the outage began at
09:11:27.227Z, about 5.5 minutes before this journal closed. Anchor the incident
on the log timestamp, not on the complaint's clock.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 09:11:20.723Z | Serving process starts, pid 26013. The retained log begins here — nothing earlier exists. | E1 |
| 09:11:20.724Z | `faultline 0.1.0 started`, the only `startup` event in the file. | E2 |
| 09:11:20.724Z | uvicorn binds 127.0.0.1:8000 directly — no proxy tier in the observed path. | E3 |
| 09:11:21.491Z – 09:11:24.661Z | Healthy end-user traffic: six access lines, all 200/201, 0.832–12.047 ms. The 12.047 ms maximum is the first `/health`, a cold start. | E4, E5, E6 |
| 09:11:24.661Z | **Last end-user request served.** | E6 |
| 09:11:26.725Z | **Change marker:** GET on the operator-surface crash route → 200 in 1.098 ms, request_id `fdedaa58aaa9`, unstamped client 127.0.0.1:65463. | E7 |
| 09:11:27.227Z | **Onset.** `CRITICAL … crashing now: exiting with code 1`, `event: crash`, `delay: 0.5`, same request_id. Logging stops permanently. | E8 |
| 09:12:08Z | First investigator probe: `/health` → `HTTP 000`, connect refused. Onset therefore bracketed to a 41 s window by E6 and this probe. | E9 |
| 09:12:30Z | `/products` → `HTTP 000`. The business surface is as dead as the health surface. | E10 |
| 09:16:53Z | `/openapi.json` and `/metrics` → `HTTP 000`. Outage continuous, path-independent. | E11, E12 |
| 09:16:57Z | Log still 14 lines / 3182 bytes, unchanged since 09:11:50Z — no restart logged in 5.5 minutes. | E13 |

## Investigation

Trigger — the complaint object as synthesized by the `/konan` adapter
(`docs/triggers.md`), recorded verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1793697096",
  "labels": { "alertname": "human-report" },
  "annotations": {
    "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  },
  "startsAt": "2026-11-03T09:11:36Z"
}
```

No `severity`: the reporter stated none, and the adapter never infers one.
Investigation entered at **2026-11-03T09:11:48Z** — trigger latency 12 s.

**Baseline.** A live baseline was impossible: the first probe (`/health`) already
failed at connect (E9), so health, metrics, and the business surface were all
unreachable. The baseline had to come from the log, which turned out to be the
whole life of one process in 14 lines — and that log *contains* its own normal
(E4–E6: steady sub-2 ms successes) and its own onset (E8) in the same file.

**Triage.** Three lenses ran in parallel, each blind to the others, each given
only its lens file, the surface contract path, the verbatim complaint, and the
baseline: infra-process, software-defect, interfaces. All three converged on the
same marker-and-exit pair and three independently ruled their own domain out.
The interfaces lens corrected a counting error in my baseline summary (six
end-user access lines plus an `order_created` event, not seven requests; the
seventh access line is the crash-route marker itself) — the corrected count is
what this journal carries. Two lenses independently flagged `lab/server.out` as
desirable and out of contract; see Gaps.

**Deep-dive: deliberately skipped.** Deep-dives exist to fill evidence gaps, not
to re-prove. The decisive evidence was already deterministic and complete — a
shared request id, a matching delay field, the last line of the file, an
unchanged file 5.5 minutes later, four refused connects — and the only
evidence that *could* have advanced the case (OS exit status, pre-09:11:20
history, metrics gauges) is unreachable through this surface, not under-probed.
Spawning agents to re-read a 14-line log would have been coverage theater.

**Judge.** One fresh judge saw the four hypotheses with the verbatim evidence
ledger and nothing else — no lens reasoning, no narrative. It validated H1,
invalidated H2, H3 and H4, ruled on the mechanism id, and returned seven
overreach corrections against H1's wording. Every one is applied above: the exit
code is attributed to the log text rather than asserted as an exit status, the
listener claim is stated as "nothing accepted a TCP connection at the four probed
times", "nothing restarted it" is scoped to what app.log can show, and the
present-tense claims are anchored to 09:16:53Z. The judge also independently
refused the complaint's "ten minutes ago" as unverifiable.

Budget used: one triage round, three lenses, zero deep-dives, one judge.

## Hypotheses

### H1 — commanded process exit, nothing restarted it → **validated**

The causal chain is tight. E7 and E8 share request_id `fdedaa58aaa9`, and the
measured 502 ms between them matches the `"delay": 0.5` field in E8 itself — so
the crash event is the effect of that one request, not a coincidence standing
near it. E8 is line 14 of 14, so the log covers the full life of the process and
ends at its exit. E1–E3 fix the single start (pid 26013) and the direct socket
bind. E13 carries the restart argument: a restart would have written a new
`Started server process` banner, as E1 did; the file gained no bytes in the 5.5
minutes between two readings. E9–E12 close it from the client side — four paths,
four refused connects, `HTTP 000`, spanning 4 minutes 45 s.

Per the judge, two phrasings stay deliberately weaker than the raw log: "code 1"
is what the process said about itself, and "nothing restarted it" holds for any
restart that would log to app.log. Neither weakening changes the verdict or the
mechanism.

**Mechanism: `process-crashed`, not `degradation-switch`.** The judge ruled on
this explicitly. A degradation switch injects errors or latency *while on*: the
socket stays bound, requests get HTTP statuses, and you observe failures or
inflated latency. Here nothing is bound, there is no HTTP status at all, no
`chaos_enabled` / `chaos_disabled` / `chaos_failure` event appears anywhere in the
14 lines, and the last served requests took 0.832–1.991 ms, so no latency
injection was in flight. The mechanism id names what happened inside the target —
a single exit that nothing restarted — not what triggered it. An operator-surface
trigger (E7) does not turn a terminal one-shot exit into a persistent switch
state. The one thing the id cannot express is that the exit was *commanded*
rather than spontaneous; that lives in this prose, as the contract's list offers
no id for it.

### H2 — application code defect → **invalidated**

All seven access lines in the process lifetime are 200 or 201 (E4, E5, E6 quote
three; the rest are two `/health` 200s, a `/products/1` 200, and the marker).
Across all 14 lines there is no `unhandled_exception` event, no `exception_type`
field, no `stack` field, and no status other than 200/201. The terminal line is
not an exception (E8): its `event` is `crash`, its logger is the target's
simulation surface rather than `faultline.shop` or `faultline.request`, and the
request owning that id had already returned 200 normally (E7). A handler that
returns 200 and then exits on a declared timer is executing an intended path, not
failing. There is no failing route or input, so the data-dependent signature is
absent too. What would revive it: an OS-level termination record for pid 26013
showing a traceback or fatal signal instead of a clean exit through that path.

### H3 — boundary, dependency, or injected edge degradation → **invalidated**

E3 shows the application binding the very socket the probes address, so the
observed path contains no proxy tier — and a failed gateway answers 502/503/504,
whereas E9–E12 fail before any HTTP exchange exists. E4–E6 show `/products`,
`/orders`, and `POST /orders` answering in 0.832–1.991 ms immediately before the
exit, so nothing upstream was degrading. No `chaos_*` event and no 5xx appears in
the file; the failure rate before onset was 0/7. What would settle it: an access
log from a tier in front of the application for 09:11Z–09:17Z, or one probe from
a non-loopback vantage point — if no such tier exists, the hypothesis has no
subject.

### H4 — capacity exceeded → **invalidated**

Seven requests in a 6.5 s lifetime, durations 0.832–12.047 ms, the maximum being
a cold-start `/health` (E4, E5, E6). No 503, no queue growth, no worker restart,
and the death has a documented trigger (E8). Demand of this size cannot exhaust
capacity. Note what this hypothesis died on: traffic counts and the log, not
resource data — E12 proves the gauges are unreachable. What would settle it
properly: a kernel-level record for 09:11Z (an OOM-killer line) or an RSS / fd /
worker snapshot for pid 26013.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- **Settle the exit outside the target's own claim.** The supervisor or
  service-manager record for pid 26013 and its exit status would confirm or
  refute the logged "code 1" (E8). This is outside the current surface contract —
  it needs a contract change, not an ad-hoc widening mid-incident.
- **Name `lab/server.out` in `docs/lab.md` or consciously leave it out.** Two
  lenses and the orchestrator independently wanted it, it exists on disk, and it
  would likely carry the shell-level exit. Right now the contract's "all of it"
  list excludes it, so it stayed unread in three separate places. That recurring
  friction is a contract question worth closing.
- **Watch for the return of the listener.** Re-probe `/health`; the first new
  `Started server process` / `startup` pair in `lab/logs/app.log` is the restart
  marker to watch for. The last negative observation here is 09:16:53Z.
- **Ask whether this target has any restart policy at all.** No second startup
  marker appeared in 5.5 minutes (E13), which suggests nothing supervises the
  process. That is a resilience question for the operator; this journal only
  records the absence of a logged restart.
- **Review who can reach the operator-surface routes.** One unauthenticated GET
  ended the service (E7 → E8), and the log records no auth or user field for the
  caller. Access control there is an operator decision; the finding recorded here
  is simply that the route was reachable and effective.
- **Consider log retention.** The whole retained history was 6.504 s wide with no
  rotation backups (E13), which is why the reporter's "ten minutes ago" could not
  be checked. Retention is what makes onset claims testable.

## Gaps

1. **Nothing before 09:11:20.723Z.** `lab/logs/` holds `app.log` alone; the
   `.1`–`.3` backups named in `docs/lab.md` do not exist (E13). The retained
   window is 6.504 s. The reporter's "fine ten minutes ago" (≈09:07Z) is
   therefore neither confirmed nor contradicted — the evidence cannot distinguish
   an earlier healthy process generation from no process at all.
2. **No metrics.** `/metrics` lives on the dead target (E12), so
   `process_uptime_seconds`, `process_max_rss_bytes`, `http_requests_total` and
   `http_exceptions_total` contributed nothing. H4 died on traffic counts, not on
   gauge data, and the lifecycle rests on log lines alone.
3. **No OS-level evidence.** "exiting with code 1" is the process's own log text
   (E8), not a process-table entry, supervisor record, or exit status.
   `lab/server.out` and `lab/faultline.pid` exist on disk but sit outside the
   enumerated surface, so they were deliberately not read.
4. **"Down for everyone" is unproven.** Four probes, one host, loopback only
   (E9–E12). Path-independence is established and the failure is at connect, so
   it is path-shaped by nature; a second vantage point was never available.
5. **Socket state not inspected directly.** A refused connect was not
   distinguished from a packet filter or a rejecting listener — that class of
   evidence (`lsof`, `netstat`) is outside the surface contract.
6. **The actor is unidentified.** E7 records only `client 127.0.0.1:65463`, with
   no auth or user field. The evidence excludes investigator traffic —
   `scripts/probe.sh` refuses that route mechanically, and `konan-` request ids
   begin only at 09:12:08Z, after the exit — but it does not say who sent it.
7. **State after 09:16:53Z unknown.** That is the last probe (E11, E12), with the
   log confirmed unchanged at 09:16:57Z (E13).
