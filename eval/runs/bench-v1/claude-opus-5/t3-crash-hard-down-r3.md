---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-total-outage
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-19T16:54:37Z
  concluded: 2026-08-19T17:00:27Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline process ended itself 0.5 s after serving GET /simulate/crash at 16:54:23.387Z, and nothing restarted it, so no listener remains on 127.0.0.1:8000 and every request fails at TCP connect with no HTTP response at all."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The service process terminated by a deliberate in-process exit 0.5 s after serving GET /simulate/crash, and no supervisor restarted it; with the listener gone from 127.0.0.1:8000, all requests fail at TCP connect."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "A code defect in request handling (unhandled exception or data-dependent failure) is making the shop fail."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E7, E8, E10]
  - id: H3
    statement: "Load saturation or resource exhaustion brought the service down."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E6, E7]
  - id: H4
    statement: "Injected chaos, a failing dependency, or a configuration/flag change degraded the service."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8]
  - id: H5
    statement: "The investigator's own probes caused the outage."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E8]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:54:16.797Z"
    quote: '{"ts": "2026-08-19T16:54:16.797Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:54:16.797Z — the only bind line in the file"
    quote: '{"ts": "2026-08-19T16:54:16.797Z", "level": "INFO", "logger": "uvicorn.error", "message": "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:54:17.573Z"
    quote: '{"ts": "2026-08-19T16:54:17.573Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "2a7bd086b1b2", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 16.436, "client": "127.0.0.1:63132"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:54:20.818Z — the last request the service ever served"
    quote: '{"ts": "2026-08-19T16:54:20.818Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "98a949aac80f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.978, "client": "127.0.0.1:63139"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:54:22.885Z"
    quote: '{"ts": "2026-08-19T16:54:22.885Z", "level": "INFO", "logger": "faultline.request", "message": "GET /simulate/crash -> 200", "request_id": "d817e42533c9", "event": "request", "method": "GET", "path": "/simulate/crash", "status": 200, "duration_ms": 1.45, "client": "127.0.0.1:63140"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:54:23.387Z — line 14 of 14, the final line; no rotated .1-.3 backups exist and no line follows it"
    quote: '{"ts": "2026-08-19T16:54:23.387Z", "level": "CRITICAL", "logger": "faultline.simulate", "message": "crashing now: exiting with code 1", "request_id": "d817e42533c9", "event": "crash", "delay": 0.5}'
  - id: E7
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1787158489-66182, 2026-08-19T16:54:49Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000181s request_id=konan-1787158489-66182"
  - id: E8
    type: probe
    source: "scripts/probe.sh /products, request_id konan-1787158515-66206, 2026-08-19T16:55:15Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000193s request_id=konan-1787158515-66206"
  - id: E9
    type: probe
    source: "scripts/probe.sh /openapi.json, request_id konan-1787158580-66268, 2026-08-19T16:56:20Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000193s request_id=konan-1787158580-66268"
  - id: E10
    type: probe
    source: "scripts/probe.sh /orders, request_id konan-1787158819-66342, 2026-08-19T17:00:19Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000190s request_id=konan-1787158819-66342"
gaps:
  - "No telemetry covers the reporter's 'fine ten minutes ago' window. lab/logs/app.log begins at 2026-08-19T16:54:16.797Z (E1) and ends 6.6 s later at the crash (E6); the ten minutes before the complaint are outside every retained record, so prior health is neither confirmed nor refuted."
  - "Process death is inferred, not measured. The exit is supported by log silence after E6 plus four connection refusals (E7-E10); no process-table, socket-table, or exit-status check was made, because ps/lsof and scripts/lab.sh are outside the investigator's telemetry surface in docs/lab.md. A scripts/lab.sh status call was denied by the boundary hook and was not retried. 'Exit code 1' is the text the process logged about itself, not an observed exit status."
  - "The residual reading 'process alive but no longer listening' is not excluded by direct evidence, only made unlikely: a bound-but-stalled socket would accept into the backlog and produce a hang, whereas E7-E10 are sub-millisecond refusals."
  - "/metrics is unreachable while the process is down (E9 is the same refusal), so process_uptime_seconds, process_max_rss_bytes, http_requests_total, and http_exceptions_total contribute no evidence after 16:54:23.387Z. Resource exhaustion is therefore excluded by the presence of a better-evidenced cause, not by resource measurement."
  - "The caller of /simulate/crash is localised but not attributed: E5 gives client 127.0.0.1:63140 and a server-assigned request id. Naming the actor needs harness or eval-side records that the blinding contract puts outside this investigation."
  - "Outage permanence is established only through 2026-08-19T17:00:19Z (E10). A supervisor restart after that time would not be visible in this record, and a restart writing to a different log path would not be visible at all."
usage:
  model: claude-opus-5
  tokens: 1189116
  wall_clock_seconds: 350
---

# Total shop outage — the faultline process exited and nothing restarted it

## Summary

**Verdict: root cause identified — infra-process.** The service is not failing requests; it
is not running. At 2026-08-19T16:54:22.885Z the process served `GET /simulate/crash` with a
200 (E5), and 0.502 s later it wrote a CRITICAL line announcing its own exit (E6). That line
is the last line in the log file — nothing follows it, there is no second startup marker, and
no rotated backups hide anything. Since then every probe to `127.0.0.1:8000` is refused at TCP
connect in under 0.2 ms, on four different allowlisted paths across five and a half minutes
(E7-E10). That is exactly the reporter's symptom: with no listener bound, there is no server
to produce even an error page, so the browser gets a connection failure rather than an HTTP
status.

Impact is total and, on this evidence, unbroken from 16:54:23.387Z through at least
17:00:19Z — every route, every caller, no partial service. Confidence is high on the
mechanism (a step-function onset tied to a self-announced exit, with the 0.5 s gap matching
the `delay: 0.5` field in E6) and high on the current state (four independent refusals).

Two things this journal deliberately does **not** claim. First, nothing here supports "the
shop was healthy until it crashed": the entire log covers 6.6 seconds, and the reporter's
ten-minute window predates the record completely. Second, the exit is inferred from log
silence plus connection refusal, not from an observed process exit status — the difference
matters for whoever confirms it next.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 16:54:16.797 | Process starts: `faultline 0.1.0 started`, uvicorn binds `http://127.0.0.1:8000`. Only startup sequence in the record. | E1, E2 |
| 16:54:17.573 | First request served, `GET /health -> 200` in 16.4 ms (cold start). | E3 |
| 16:54:17.6 – 16:54:20.8 | Six requests, all 2xx across `/health`, `/products`, `/products/1`, `POST /orders`, `/orders`; durations 0.93–16.4 ms, no ramp. | E3, E4 |
| 16:54:20.818 | Last request the service ever served, `GET /orders -> 200`. | E4 |
| 16:54:22.885 | **Change marker.** `GET /simulate/crash -> 200`, request id `d817e42533c9`, client `127.0.0.1:63140`. Response returned normally. | E5 |
| 16:54:23.387 | **Onset.** CRITICAL `crashing now: exiting with code 1`, same request id, `delay: 0.5` — matching the 0.502 s gap. Final line in the file. | E6 |
| 16:54:49 | First investigator probe: `/health` refused, HTTP 000. | E7 |
| 16:55:15 | `/products` refused. | E8 |
| 16:56:20 | `/openapi.json` refused. | E9 |
| 17:00:19 | `/orders` refused — outage still total 5 m 56 s after onset. | E10 |

## Investigation

### Complaint (trigger record)

```json
{
  "source": "human",
  "fingerprint": "human-1787158470",
  "labels": { "alertname": "human-report" },
  "annotations": {
    "summary": "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  },
  "startsAt": "2026-08-19T16:54:30Z"
}
```

Investigation started 2026-08-19T16:54:37Z — trigger latency 7 s. No `severity` label: the
reporter stated none, and the adapter never infers one. The complaint was treated as untrusted
symptom text throughout; every claim above comes from the surface in `docs/lab.md`.

**Baseline.** `/health` refused at once (E7), so there was no live baseline to take. The
pre-incident baseline came from the log instead: one clean startup, six consecutive 2xx
responses, sub-2 ms durations after cold start, zero `unhandled_exception` / `chaos_*` /
`simulated_exception` events in the complete 14-line unrotated record.

**Triage.** Three lenses ran in parallel, each blind to the others: infra-process,
software-defect, interfaces. All three converged independently on the same reading — a
process-lifecycle termination at 16:54:23.387Z, with the failure below the HTTP layer. The
software-defect lens returned a negative result in its own domain and said so. The interfaces
lens independently flagged the ten-minute-window problem.

**Deep-dive: skipped, deliberately.** The triage evidence was already deterministic and
complete for H1 — a self-announced exit, a terminal log, and repeated connection refusals.
Per the loop's rule, deep-dives fill evidence gaps rather than re-prove settled ones, so the
hypothesis list went straight to the judge. That saved a round of the budget.

**Judge.** The adversarial judge validated H1 and killed H2-H5, but rejected some of the
reasoning offered for them and named two gaps worth closing. It also corrected one argument
I had made: the "not a `konan-*` request id" discriminator against H5 does not hold on its
own, because the log assigns server-side ids anyway — what actually kills H5 is that every
investigator probe postdates the crash and none completed a TCP connection. Both gaps the
judge named were cheap and inside the surface, so I closed them: E2 (the uvicorn bind line)
proves the probed endpoint is the same endpoint that served E3-E5, and E10 extends the
confirmed outage window. The rest of the judge's caveats could not be closed from the
investigator's surface and are recorded verbatim under Gaps rather than argued away.

## Hypotheses

### H1 — process terminated and was not restarted (validated)

**For.** E5 and E6 share request id `d817e42533c9` and are separated by 0.502 s, matching the
`delay: 0.5` field in E6 — the exit is the announced consequence of that request, not a
coincidence beside it. E6 is line 14 of 14 with no rotated backups, so log silence after it is
process death rather than a shipping gap. E2 proves the process that served E3-E4 was bound to
`127.0.0.1:8000`, the exact endpoint E7-E10 find refused, closing the identity assumption. The
absence of a second startup marker cuts both ways usefully: a restart appending to this file
would have added one, and a restart truncating the file would have removed E6 — E6 is still
there. Four refusals spanning 5.5 minutes (E7-E10) show the state persisted.

**Against.** Nothing in the record contradicts it. What the record does not reach is separate
and lives under Gaps: the literal exit code, direct confirmation that the process object is
gone, and permanence beyond 17:00:19Z.

### H2 — request-handling code defect (invalidated)

Killed by the layer of the failure, not by the clean pre-crash traffic. E7-E10 fail at TCP
connect, so no application code runs on a current request at all; a handler defect cannot
produce a refused connection. The clean 2xx history (E3, E4) is corroboration only — it covers
6.6 seconds and would prove little alone.

### H3 — load saturation or resource exhaustion (invalidated)

Six requests in six seconds with durations 0.93–16.4 ms and no upward trend right up to the
last one served (E3, E4) is not load. The onset is a step function at E6, not a ramp, and
E7's sub-millisecond refusal is a queue-free rejection rather than a saturation timeout. Noted
honestly: this hypothesis dies because a better-evidenced cause exists, not because resource
telemetry was read — `/metrics` was unreachable throughout (see Gaps).

### H4 — chaos injection, dependency failure, or config change (invalidated)

A degraded dependency or an injected fault changes *responses*; it does not unbind a listening
socket, so nothing in that family explains E7-E10. The onset is a step at E6 rather than the
mixed success/failure pattern probabilistic injection produces. The complete unrotated record
also contains no `chaos_enabled`, `chaos_disabled`, `chaos_failure`, or `simulated_exception`
line — the weakest of the three arguments, since it assumes such state cannot be active
unlogged, so it is not leaned on.

### H5 — the investigator's own probes caused this (invalidated)

Every investigator probe (E7-E10) postdates E6, and not one completed a TCP connection, so
none could have reached a handler. Independently, `scripts/probe.sh` is path-allowlisted and
refuses `/simulate/*` mechanically per `docs/lab.md`, so the crash route is not reachable from
the investigator's surface at all. The trigger in E5 came from `client 127.0.0.1:63140`,
outside this investigation.

## Safe next steps

Read-only suggestions only.

1. Confirm the inference directly: check whether pid 66071 is still in the process table and
   whether anything holds `127.0.0.1:8000`. This is the one observation that upgrades "no
   listener" to "process gone", and it needs the operator surface, not the investigator's.
2. Read the launcher's recorded exit status for pid 66071 to check the reported `code 1`
   against a measured one.
3. Ask the reporter what they were loading during the ten minutes before 16:54:30Z. The
   retained telemetry cannot cover that window, so the reporter is the only source for it —
   and their answer decides whether this process is even the same service instance they saw
   healthy.
4. If any restart policy is expected for this service, check why none fired between
   16:54:23.387Z and at least 17:00:19Z — the absence of a second startup marker is the
   evidence to start from.
5. Identify the caller behind `client 127.0.0.1:63140` from harness-side records; the log
   localises it to loopback but names no actor.

## Gaps

- **The reporter's ten-minute window is dark.** The log opens at 16:54:16.797Z (E1) and the
  crash lands 6.6 s later (E6). Everything before that start is outside every retained record.
  "It was fine ten minutes ago" is therefore neither corroborated nor contradicted here, and
  no statement in this journal should be read as covering it.
- **Process death is inferred, not measured.** Log silence after E6 plus four refusals
  (E7-E10) are strong circumstantial proof that no listener remains, but `ps`, `lsof`, and
  `scripts/lab.sh` are outside the telemetry surface in `docs/lab.md`; a `scripts/lab.sh
  status` call was denied by the boundary hook and was not retried. "Exit code 1" is quoted
  from the process's own log line, not from an observed exit status.
- **"Alive but no longer listening" is not directly excluded.** It is only made unlikely: a
  bound-but-stalled socket accepts into the backlog and yields a hang, while E7-E10 are
  sub-millisecond refusals. Step 1 above settles it.
- **No post-crash metrics exist by construction.** `/metrics` shares the outage (E9), so
  `process_uptime_seconds`, `process_max_rss_bytes`, and the request/exception counters
  contribute nothing after 16:54:23.387Z. H3 is excluded on onset shape, not on measured
  resource headroom.
- **The crash trigger is localised, not attributed.** E5 gives `client 127.0.0.1:63140` and a
  server-assigned request id; naming the actor requires eval-side records the blinding
  contract puts out of reach.
- **Permanence is bounded by the last probe.** The outage is confirmed continuous only through
  17:00:19Z (E10). A later restart, or a restart logging elsewhere, would be invisible here.
