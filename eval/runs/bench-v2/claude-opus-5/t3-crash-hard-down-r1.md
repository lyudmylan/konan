---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-total-outage
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-03T08:58:25Z
  concluded: 2026-11-03T09:08:33Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: >-
    The service process ended itself through its own code path at 08:58:04.992Z — a
    CRITICAL self-exit line from logger faultline.simulate, carrying the request id of a
    GET to the target's operator fault-injection route that had been answered 200 a half
    second earlier — and nothing started it again, so the listener on 127.0.0.1:8000 was
    absent and every later request failed at TCP connect before any application code ran.
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: >-
      The service process terminated itself through its own code path at 08:58:04.992Z,
      0.501 s after answering the triggering request with HTTP 200, and no process started
      again; with nothing listening on 127.0.0.1:8000, every request that reaches that port
      fails at TCP connect, so a client gets a refused connection and no HTTP status at all.
      The exit skipped the ASGI shutdown path, so there was no connection drain.
    incident_class: infra-process
    state: validated
    evidence_for: [E5, E4, E13, E11, E6, E7, E8, E9, E10, E3, E2]
    evidence_against: []
  - id: H2
    statement: >-
      An unhandled exception in the target's own request-handling code caused the outage.
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E5, E12, E13]
  - id: H3
    statement: >-
      Demand exceeded capacity — CPU, workers, connections or bandwidth exhausted under
      load — and the service stopped serving.
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E4, E1, E5]
  - id: H4
    statement: >-
      A proxy, load balancer or network path between the users and the service failed, or
      connectivity to the service was lost.
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E9, E10, E5, E11]
  - id: H5
    statement: >-
      An operational degradation switch inside the target (chaos / error injection) was
      turned on and is making requests fail.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E9, E10, E11, E15, E12, E14]
  - id: H6
    statement: >-
      The process was killed from outside after exhausting memory (an OOM kill), rather
      than exiting through its own code.
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E12]
  - id: H7
    statement: >-
      The platform refused the process a resource with no rise in demand — a disk, memory
      or descriptor cap — and the process died on that limit.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E12, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:57:58.509Z"
    quote: |-
      {"ts": "2026-11-03T08:57:58.509Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:57:58.510Z"
    quote: |-
      {"ts": "2026-11-03T08:57:58.510Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:58:02.432Z — last request line before the terminal event"
    quote: |-
      {"ts": "2026-11-03T08:58:02.432Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "a98a705e6e5f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.763, "client": "127.0.0.1:65389"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:58:04.491Z — request line sharing the terminal event's request id"
    quote: |-
      {"ts": "2026-11-03T08:58:04.491Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "14df82811c55", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.594, "client": "127.0.0.1:65390"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:58:04.992Z — final line of the file"
    quote: |-
      {"ts": "2026-11-03T08:58:04.992Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "14df82811c55", "event": "crash", "delay": 0.5}
  - id: E6
    type: probe
    source: "/health @ 2026-11-03T08:58:33Z, request id konan-1793696313-25737"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000199s request_id=konan-1793696313-25737
  - id: E7
    type: probe
    source: "/products @ 2026-11-03T09:01:10Z, request id konan-1793696470-25810"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000180s request_id=konan-1793696470-25810
  - id: E8
    type: probe
    source: "/orders @ 2026-11-03T09:01:10Z, request id konan-1793696470-25815"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000183s request_id=konan-1793696470-25815
  - id: E9
    type: probe
    source: "/openapi.json @ 2026-11-03T09:01:27Z, request id konan-1793696487-25830"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000196s request_id=konan-1793696487-25830
  - id: E10
    type: probe
    source: "/health @ 2026-11-03T09:02:43Z, request id konan-1793696563-25875 — 3 min 38 s after E5"
    quote: |-
      curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server
      -- HTTP 000 in 0.000166s request_id=konan-1793696563-25875
  - id: E11
    type: log
    source: "lab/logs/app.log — file state observed at 2026-11-03T09:02:44Z"
    quote: |-
      wc -l lab/logs/app.log -> 14 lab/logs/app.log; ls lab/logs/ -> app.log (no .1-.3 rotation backups); grep -c '"event": "startup"' lab/logs/app.log -> 1; no line in the file carries a timestamp later than 2026-11-03T08:58:04.992Z; a grep for any konan- request id returns 0 matches
  - id: E12
    type: log
    source: "lab/logs/app.log — complete request record 2026-11-03T08:57:59.239Z to 08:58:02.432Z (6 lines, all 2xx, all server-generated ids)"
    quote: |-
      GET /health -> 200 duration_ms 12.16; GET /health -> 200 duration_ms 1.717; GET /products -> 200 duration_ms 2.157; GET /products/1 -> 200 duration_ms 0.992; POST /orders -> 201 duration_ms 1.733, with {"ts": "2026-11-03T08:58:01.384Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "89525819df41", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5}; GET /orders -> 200 duration_ms 0.763
  - id: E13
    type: log
    source: "lab/server.out — 15 lines: one uv virtualenv warning plus the same 14 log lines"
    quote: |-
      present: "Started server process [25664]", "Waiting for application startup.", "Application startup complete.", "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"; absent anywhere in the file: "Shutting down", "Waiting for application shutdown", "Application shutdown complete", "Finished server process"
  - id: E14
    type: log
    source: "lab/logs/app.log — absence across all 14 lines"
    quote: |-
      no line carries "event": "unhandled_exception"; no line carries a "stack" field; no request line carries a 4xx or 5xx status
  - id: E15
    type: log
    source: "lab/logs/app.log — absence across all 14 lines; plus /metrics unreachable per E6-E10"
    quote: |-
      no line carries "event": "chaos_enabled", "event": "chaos_disabled" or "event": "chaos_failure"; the metric faultline_chaos_enabled could not be read at any point in this investigation, because /metrics shares the unreachable listener
gaps:
  - >-
    No telemetry of any kind exists before 2026-11-03T08:57:58.509Z (E1), so the
    reporter's "fine ten minutes ago" window (about 08:48 to 08:57:58) is unobservable and
    can be neither corroborated nor refuted. The log holds exactly one startup event and
    no rotation backups (E11), so an earlier process generation, if one existed, left no
    retained trace. The claim cannot describe this process instance, whose first request
    ran at 08:57:59.239Z, 12.5 s before the complaint was filed.
  - >-
    Nothing was observed between 08:58:04.992Z (E5) and 08:58:33Z (E6). The complaint was
    filed at 08:58:11Z, inside that 28.5 s window, so "already down when the human
    reported it" is an inference from log silence plus the later refusals, not an
    observation.
  - >-
    No /metrics snapshot exists from before the exit, and none can be taken now (E6-E10):
    process_max_rss_bytes, process_uptime_seconds, http_exceptions_total and
    faultline_chaos_enabled have no value at any point in this investigation. Memory
    exhaustion (H6) is therefore excluded by substitution — the process logged its own exit
    (E5) — and not by measurement; the chaos switch state stays unknown, though no
    injection mode inside a process can refuse a TCP connection.
  - >-
    The real exit status, and the fate of PID 25664 (E13), are outside the GET-only
    surface. "exiting with code 1" is the target's own statement of intent (E5), not an
    observed process status, and no evidence proves the process is gone — only that
    nothing listens.
  - >-
    The caller of the operator fault-injection route is unattributed. E4 records client
    127.0.0.1:65390 and a server-generated request id, which excludes investigator traffic
    (no konan- id appears anywhere in the log, E11) but names no operator, script or
    person.
  - >-
    One vantage point only: every probe ran from the loopback address of the host that runs
    the target, and no user-side telemetry exists. A second, redundant failure in a
    user-facing path in front of the service could not be excluded, and "down for everyone"
    rests on the mechanism — a connection refusal precedes any client-specific code — not
    on a count of affected users.
  - >-
    The absence signatures in E14 are read against the surface contract, which declares
    unhandled_exception (with exception_type) and stack among the log's event values and
    fields (docs/lab.md). No line in this window demonstrates that shape, so the absence is
    meaningful only as far as the contract is accurate.
usage:
  model: claude-opus-5
  tokens: 1762620
  wall_clock_seconds: 608
---

# Total outage: the service process exited on its own fault-injection route and nothing restarted it

## Summary

Root cause identified, and the outage is real and total. At 2026-11-03T08:58:04.992Z the
service wrote one CRITICAL line — `"crashing now: exiting with code 1"`, from logger
`faultline.simulate`, `"event": "crash"`, `"delay": 0.5` (E5) — and stopped. That line
carries the same request id, `14df82811c55`, as a GET to the target's operator
fault-injection route that had been answered **HTTP 200** half a second earlier, at
08:58:04.491Z (E4); the logged `"delay": 0.5` matches the 501 ms between the two lines.
Nothing was logged afterwards, the log holds exactly one startup event and no rotation
backups (E11), and five probes across four allowlisted routes over 3 min 38 s all failed
identically at TCP connect with `curl: (7)` and `HTTP 000` in about 0.2 ms (E6–E10). So:
one process generation, a deliberate self-exit through the target's own code, no restart,
no crash loop.

The mechanism explains the complaint exactly. A refused connection happens before any
application code runs, so there is no HTTP status to render — "not even an error page" is
the precise signature of a dead listener rather than a failing application. Impact is
total for every request that reaches port 8000 on this host: the failure cannot select
clients, because it precedes client-specific code. Confidence is high on the mechanism and
on the class. Two things are *not* established and should not be read into this report: the
real exit status (the exit code is the target's own claim, not an observed process status),
and who called the fault-injection route — the caller is an unidentified non-investigator
client (E4, E11). The route answered 200 to that caller before the process went away, so a
success status on it is not evidence that the service stayed healthy.

The exit also skipped the ASGI shutdown path: `lab/server.out` holds all four uvicorn
startup lines and none of the four shutdown lines (E13). There was no connection drain, so
clients get a refusal rather than a 503 from a graceful stop.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 08:57:58.509 | Process starts: `faultline 0.1.0 started`, one `"event": "startup"` — the earliest telemetry that exists | E1, E11 |
| 08:57:58.510 | Listener up on `http://127.0.0.1:8000` | E2 |
| 08:57:59.239–08:58:02.432 | Six requests, all 200/201, 0.763–12.16 ms, including `POST /orders -> 201` with an `order_created` line. Healthy business surface, not just health | E12 |
| 08:58:04.491 | GET to the operator fault-injection route from client `127.0.0.1:65390`, server-generated request id `14df82811c55`, answered **200** | E4 |
| 08:58:04.992 | CRITICAL `crashing now: exiting with code 1`, same request id, `"delay": 0.5`. Last line in the log; no uvicorn shutdown sequence follows | E5, E13 |
| 08:58:11 | *Human files the complaint* (inside the 28.5 s observation gap — nothing is observed between 08:58:04.992 and 08:58:33) | — |
| 08:58:33 | First probe: `/health` refused, `HTTP 000` | E6 |
| 09:01:10–09:01:27 | `/products`, `/orders`, `/openapi.json` refused identically | E7, E8, E9 |
| 09:02:43 | `/health` still refused, 3 min 38 s after the exit; log still 14 lines, still one startup event | E10, E11 |

No configuration, deploy or flag-change marker appears anywhere in the window: no
`chaos_enabled`, `chaos_disabled` or `chaos_failure` line exists (E15). The only
behaviour-changing marker in the timeline is the terminal crash event itself.

## Investigation

**Baseline.** The first probe settled the shape of the incident: `/health` refused at the
transport layer (E6), so there was no live state to snapshot and `/metrics` was
unreachable with it. The whole retained history is 14 log lines covering 6.5 s of traffic
plus a startup block.

**Triage, three lenses in parallel, each blind to the others.** infra-process, software-defect
and interfaces each got the lens file, the surface contract, the verbatim complaint and the
baseline. None was skipped, so no domain was accepted as a blind spot. They converged:
infra-process found a single process generation with no restart and no restart loop, and
could not test saturation because the metrics surface is gone; software-defect found no
exception signature at all and classified the stop as a deliberate self-logged exit, noting
the invoking surface is outside its domain; interfaces found a route-independent failure
with *no* HTTP status — not a gateway-shaped 502/503/504 — and no proxy tier to blame. Two
lenses ran extra probes of their own (`/products`, `/orders`, `/openapi.json`), which is
why E7–E9 exist. All three stayed read-only; nothing was started, stopped or restarted.

**Deep-dive: skipped, deliberately.** The triage evidence for H1 was already deterministic
and complete — a self-logged exit, log silence after it, and reproducible connect refusals
across four routes. Deep-dives exist to fill evidence gaps, not to re-prove; the remaining
unknowns (the real exit status, the caller's identity, pre-exit resource state) are outside
the GET-only surface, so no further probing could settle them. Budget spent: one triage
round, zero deep-dive agents, one judge.

**Judge.** A fresh judge received only the hypothesis list and the verbatim evidence — no
lens reasoning, no narrative. It validated H1 with class and cause id intact, and added the
reasoning that excludes `process-hung`: a live process holding its listen socket lets the
kernel complete the handshake, so a hang yields a hang or a reset, never a ~0.2 ms refusal.
It forced four corrections, all applied here: the exit code is self-reported, not observed;
"every subsequent request from every client" was trimmed to every request reaching port
8000 on this host, since one loopback vantage point cannot speak for a user path; the
caller of the fault-injection route must be named as unattributed; and H3 had to be split,
because memory exhaustion is refuted by substitution (E5) rather than by measurement — it
became H6. It also caught a ledger error: a lens had reported `lab/server.out` as 16 lines,
which did not reconcile with 14 log lines plus one warning. Re-counted: 15. E13 carries the
"no graceful shutdown" claim, so that count mattered. For completeness it named
`platform-limit` as an untested taxonomy neighbour; it is recorded as H7, closed by E5.

## Hypotheses

### H1 — self-exit through the target's own code, not restarted — **validated**

The chain is direct rather than circumstantial: E4 and E5 share request id `14df82811c55`,
the gap between them is 501 ms, and E5 records `"delay": 0.5`. E5 comes from the target's
own logger at CRITICAL, so the process announced its own exit. E13 shows the ASGI shutdown
path never ran. E11 shows one startup event, no line after 08:58:04.992Z, and no rotation
backups — a single stop, not a loop, and no supervisor brought it back within 3 min 38 s
(E10). E6–E10 show the refusal is immediate and route-independent, which also rules out
`process-hung`. E11's zero `konan-` matches prove the investigator's own probes never
reached application code, so none of this is self-inflicted. Against: nothing. The cause id
`process-crashed` fits in its "exited, once and not restarted" variant.

### H2 — unhandled exception in the target's code — **invalidated**

No line carries `"event": "unhandled_exception"`, none carries a `stack` field, and no
request line carries a 4xx or 5xx status (E14); all seven requests in the process's life
were 200/201 (E12, E4); `server.out` holds no traceback (E13); and E5 supplies a sufficient
alternative with an explicit code path. The weakness is honest: E14 is an absence, and its
force depends on the surface contract's declaration that this build writes that event and
field — recorded as a gap.

### H3 — demand-side saturation (CPU, workers, connections, bandwidth) — **invalidated**

The process's entire life was about 6.5 s (E1 to E5) and held seven requests (E12 plus E4)
at 0.763–12.16 ms, the slowest being the first — ordinary warm-up. There is no demand rise
and no latency trend to deteriorate. Directly refuted rather than argued away.

### H4 — a proxy, load balancer or network path between users and the service — **invalidated**

A refusal returned in about 0.2 ms (E6–E10) proves the loopback path works and the kernel
answered; lost connectivity gives a timeout or silence, not a refusal. And the failure
carries no HTTP status at all, which is not a gateway's shape. The origin has no listener
(E5, E11), which alone produces the exact reported symptom, so any tier in front would be a
second and redundant cause. The limit is real and recorded as a gap: the user-facing path
was never observed from a user's vantage point.

### H5 — an internal degradation switch injecting failures — **invalidated**

The decisive argument is the failure mode, not the switch state: code inside a process can
only inject errors or latency *while the process runs*, and the observed symptom is a
refusal at TCP connect with no HTTP status (E6–E10) and no application record of the attempt
(E11). No injection mode produces that. E15's log absence agrees, E14 shows no injected 5xx
and E12 no injected latency. This report does not claim the switch was off:
`faultline_chaos_enabled` was never readable (E15), so its state stays unknown and the
failure mode makes it unnecessary. The classification contest is noted for the record — the
triggering route is itself fault-injection surface — but `degradation-switch` wants a switch
that injects errors or latency while on, whereas this route ended the process once;
`process-crashed` is the mechanism the evidence proves.

### H6 — an OOM kill from outside the process — **invalidated (by substitution)**

An external kill writes no CRITICAL line from the target's own `faultline.simulate` logger
0.5 s after a request to the fault-injection route (E5), and the traffic record shows no
demand that could exhaust memory (E12). Stated as substitution, not measurement: no
`process_max_rss_bytes` reading exists from before the exit, and an OS-level kill record for
PID 25664 would settle the leg but lies outside the surface.

### H7 — a platform limit refused the process a resource — **invalidated**

Named for taxonomy completeness after the judge observed that a refused resource with no
demand rise belongs here rather than under saturation. E5 closes it: the process stated its
own exit through its own code path; no disk, descriptor or memory-cap error appears in the
log (E14), and demand never rose (E12).

## Safe next steps

Read-only, in the order that settles the most with the least:

1. Check the process table or the supervisor's records for PID 25664 (E13) after
   08:58:04.992Z. This is the one observation that converts the self-reported exit code into
   an observed process status, and it settles H6's remaining leg at the same time.
2. Identify the caller behind client `127.0.0.1:65390` (E4) — an operator shell, a test
   harness, a scheduled job, or a user-reachable path. Everything about intent hangs on
   this, and the log cannot answer it.
3. Confirm whether anything is expected to restart this service. Nothing did for 3 min 38 s
   (E10, E11), which is what turned a one-second exit into a sustained total outage.
4. Check whether the operator fault-injection surface is reachable from outside the host,
   and from which network positions. It answered an unauthenticated GET with 200 before
   exiting (E4).
5. Retain log history across process generations, or scrape `process_uptime_seconds` into a
   time series. Two gaps in this investigation — the reporter's ten-minute window and the
   pre-exit resource state — exist only because nothing survives a restart here.

Remediation is out of scope for this journal, including restarting the service.

## Gaps

The seven entries in the machine core, in short: there is **no telemetry at all** before
08:57:58.509Z, so "it was fine ten minutes ago" can be neither confirmed nor denied — and
it cannot describe *this* process instance, which first served traffic 12.5 s before the
complaint; a **28.5 s observation hole** covers the moment the complaint was filed, so
downness at that instant is inference, not observation; **no metrics exist** from any point
in this investigation, which is what forces H6 to rest on substitution and leaves the chaos
switch state unknown; the **real exit status and the process's fate** are outside a GET-only
surface; the **caller** of the fault-injection route is unattributed; there is **one
vantage point** (loopback), so a redundant user-path failure cannot be excluded and "for
everyone" rests on mechanism rather than on a user count; and the **absence signatures** of
E14 are read against the surface contract's declared log shape rather than against an
observed example.
