---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-connection-refused
  trigger: "manual — /konan adapter (human profile). Complaint object: source=human, fingerprint=human-1787157877, labels.alertname=human-report (no severity stated by the reporter), startsAt=2026-08-19T16:44:37Z. Investigation started 2026-08-19T16:44:46Z; trigger latency 9s."
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-19T16:44:46Z
  concluded: 2026-08-19T16:50:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The service process terminated itself through the /simulate/crash self-exit path 0.5s after serving that request, and nothing restarted it, so 127.0.0.1:8000 has no listener and every user request is refused at TCP before any HTTP response can exist."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The service process exited via the /simulate/crash self-exit path at 16:44:31.069Z (same request_id as the /simulate/crash access line, 0.5s later, matching that line's delay field), and no supervisor restarted it — the listener is gone, so all traffic is refused at connect."
    incident_class: infra-process
    state: validated
    evidence_for: [E8, E9, E5, E1, E2, E3, E4, E10]
    evidence_against: []
  - id: H2
    statement: "The outage is caused by an unhandled exception in the application's request-handling code."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E7, E11, E1]
  - id: H3
    statement: "The outage is caused by a chaos/config layer separate from the /simulate/* endpoints — an injected fault rate or a runtime flag change."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E1, E2, E3, E4]
  - id: H4
    statement: "The process died from load saturation or resource exhaustion."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E7, E10]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /health @ 2026-08-19T16:44:58Z, request_id=konan-1787157898-65731"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000196s request_id=konan-1787157898-65731"
  - id: E2
    type: probe
    source: "scripts/probe.sh /metrics @ 2026-08-19T16:45:26Z, request_id=konan-1787157926-65768"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000200s request_id=konan-1787157926-65768"
  - id: E3
    type: probe
    source: "scripts/probe.sh /products, request_id=konan-1787157976-65816"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000191s request_id=konan-1787157976-65816"
  - id: E4
    type: probe
    source: "scripts/probe.sh /orders, request_id=konan-1787157977-65824"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000213s request_id=konan-1787157977-65824"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:44:24.521Z"
    quote: "{\"ts\": \"2026-08-19T16:44:24.521Z\", \"level\": \"INFO\", \"logger\": \"uvicorn.error\", \"message\": \"Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:44:24.521Z"
    quote: "{\"ts\": \"2026-08-19T16:44:24.521Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:44:28.495Z"
    quote: "{\"ts\": \"2026-08-19T16:44:28.495Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"e3384e617c40\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 0.909, \"client\": \"127.0.0.1:63010\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:44:30.569Z"
    quote: "{\"ts\": \"2026-08-19T16:44:30.569Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"4a6b7c82d799\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.666, \"client\": \"127.0.0.1:63012\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:44:31.069Z (final line of the file)"
    quote: "{\"ts\": \"2026-08-19T16:44:31.069Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"4a6b7c82d799\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E10
    type: log
    source: "lab/logs/app.log — structural read of the whole file (14 lines, 16:44:24.520Z–16:44:31.069Z) and of lab/logs/"
    quote: "exactly one \"event\": \"startup\" line; zero unhandled_exception events; zero exception_type fields; zero stack fields; zero non-2xx statuses; zero chaos_enabled / chaos_disabled / chaos_failure events; no uvicorn \"Shutting down\" / \"Application shutdown complete\" / \"Finished server process\" lines after the CRITICAL line; lab/logs/ holds app.log alone, with no .1-.3 rotated backups"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:44:25.257Z–16:44:28.495Z, request duration fields"
    quote: "\"duration_ms\": 17.063, \"duration_ms\": 0.943, \"duration_ms\": 1.102, \"duration_ms\": 1.039, \"duration_ms\": 2.218, \"duration_ms\": 0.909"
gaps:
  - "The complaint's \"it was fine ten minutes ago\" can be neither confirmed nor refuted: the log covers only 16:44:24.520Z-16:44:31.069Z and lab/logs/ has no rotated .1-.3 backups (E10), so no telemetry exists for ~16:34-16:35. The in-window signal supports only the much smaller claim that the shop was healthy for ~4 seconds before the exit (E7, E11)."
  - "\"Exiting with code 1\" is the process's own log assertion (E9), not an observed wait status. Process-table and supervisor state (ps, lsof, systemd) are outside the investigator surface in docs/lab.md, so the actual exit status and the absence of a supervisor were not checked directly — only inferred from the frozen log and the continuing refusals (E10, E1-E4)."
  - "/metrics is unreachable (E2), so no counter or gauge could be read at all this investigation: http_requests_total, http_exceptions_total, faultline_chaos_enabled, process_uptime_seconds and process_max_rss_bytes are all absent from the ledger. Every metric-domain check was blind."
  - "Total user impact could not be quantified. Requests refused at TCP never reach the application and so are never logged, and the only post-onset observations are the investigator's own konan-* probes (E1-E4)."
usage:
  model: claude-opus-5
  tokens: 952873
  wall_clock_seconds: 314
---

# Shop fully down: the service process self-exited and never came back

## Summary

**Root cause identified.** The faultline process terminated itself at 16:44:31.069Z through
the `/simulate/crash` self-exit path, half a second after serving that request (E8, E9),
and nothing restarted it. With the process gone, nothing is bound to `127.0.0.1:8000`
(E5 is the last moment it was listening), so every request is refused at the TCP layer
before any HTTP response can be produced — four different allowlisted paths all fail in
under 0.25 ms with `curl` exit code 7 and no status at all (E1, E2, E3, E4).

That is exactly the shape the reporter described: "not even an error page." A connection
refusal produces no page, because no HTTP conversation ever happens. Impact is total and
does not self-heal — every route, every user, and still failing at the last probe roughly
five minutes after the exit (E10 shows the log frozen with no second startup line).

Confidence is high. The application-layer evidence (the crash line, its matching request
id, and its `delay: 0.5` matching the 500 ms gap exactly) and the transport-layer
evidence (the refusals) are independent measurements that agree. The trigger was not
investigator traffic: konan's probes carry a `konan-` request-id prefix, the triggering
request `4a6b7c82d799` does not, and `/simulate/crash` is mechanically outside konan's
probe allowlist.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 16:44:24.521 | Process starts; uvicorn binds `127.0.0.1:8000` | E6, E5 |
| 16:44:25.257–16:44:28.495 | Normal traffic: `/health`, `/products`, `/products/1`, `POST /orders` (201), `/orders` — all 2xx, all ≤17 ms | E7, E11 |
| 16:44:30.569 | `GET /simulate/crash` served 200, request id `4a6b7c82d799`, client `127.0.0.1:63012` — the only change marker in the file | E8 |
| 16:44:31.069 | CRITICAL "crashing now: exiting with code 1", same request id, `delay: 0.5` matching the 500 ms gap. **Last line written; the log is frozen here.** | E9, E10 |
| 16:44:58 | First probe after the complaint: `/health` refused, HTTP 000 | E1 |
| 16:45:26 | `/metrics` refused, HTTP 000 — the metrics surface is blind | E2 |
| ~16:46 | `/products` and `/orders` also refused, HTTP 000 | E3, E4 |

No configuration or flag-change marker appears anywhere in the window: the file carries
zero `chaos_enabled` / `chaos_disabled` / `chaos_failure` events (E10). The crash is the
only change event.

## Investigation

**Baseline.** The first probe never reached the target — `/health` refused at connect
(E1), then `/metrics` the same (E2). So the usual baseline could not be taken from the
live surface; the log tail became the baseline instead, and it showed a short, entirely
healthy process life ending in a CRITICAL crash line (E6, E7, E11, E9).

**Triage.** Because the complaint was vague and its framing untrusted, all three lenses
ran in parallel and blind to each other: infra-process, software-defect, interfaces. No
lens was skipped. All three converged independently on the same conclusion — the listener
is gone rather than sick, the failure is transport-level rather than application-level,
and the only change marker is the `/simulate/crash` request. The interfaces lens reported
that its probes were not pre-approved in its session, so it argued from the log and the
baseline trailers; that did not change its finding, since the other two lenses did probe
and got identical refusals across four paths (E1–E4).

**Deep-dive: skipped, deliberately.** The triage evidence was already deterministic and
complete — a request id linking trigger to exit, an arithmetic match between `delay: 0.5`
and the 500 ms gap, and four independent refusals. Deep-dives exist to fill evidence gaps,
not to re-prove settled ones. This is recorded so the budget decision is auditable.

**Judge.** A fresh judge saw only the hypothesis list and the verbatim evidence, with no
narrative, and was told to refute. It validated H1 and killed H2, H3 and H4 on mechanism
rather than on absence. Three of its corrections are carried into this journal rather than
argued away: (1) "exit code 1" is the log's own assertion, not an observed wait status, so
it is a gap; (2) H3 only stands as a rival hypothesis under the narrow reading "a chaos or
config layer separate from `/simulate/*`" — read broadly, `/simulate/crash` *is* fault
injection and H3 would be a relabelling of H1, so the statement was narrowed explicitly;
(3) the claim "was fine ten minutes ago" cannot be tested here, and the absence of
telemetry for that window is a property of this environment, not evidence that the
reporter is wrong.

## Hypotheses

### H1 — self-exit via `/simulate/crash`, no restart — **validated**

Three links close the chain. The `/simulate/crash` access line (E8) and the crash line
(E9) carry the same request id `4a6b7c82d799`; the crash line's `delay: 0.5` matches the
gap between them (30.569 → 31.069) exactly; and the listener proven live at 16:44:24.521Z
(E5) is now absent, since four paths refuse at connect in ~0.2 ms (E1–E4). Sub-millisecond
`curl` exit 7 is a refusal at the socket, not a timeout and not a 5xx — a live process
cannot produce it, and neither can a hung one, because a bound socket keeps accepting into
the backlog. The "nothing restarted it" leg rests on E10: exactly one startup line, the log
frozen at the crash, and refusals continuing minutes later. A restart would have written a
second startup line and made E1–E4 succeed.

### H2 — unhandled exception in the request path — **invalidated**

Refuted on mechanism, which does not depend on absence at all: an unhandled exception in a
FastAPI/uvicorn handler returns 500 and the worker keeps serving. It does not unbind the
socket, so it cannot produce E1–E4. The supporting absence is also probative here, because
the log demonstrably records above-INFO severity (E9 is CRITICAL) and a status on every
request line (E7, E11) — the sinks that would carry an exception are proven live, and they
show zero `exception_type`, zero `stack`, zero `unhandled_exception` (E10).

### H3 — separate chaos layer or runtime config change — **invalidated**

Scoped narrowly, as the judge required: a chaos toggle or flag change distinct from the
`/simulate/*` endpoints. Refuted on mechanism — request-level fault injection and config
changes act on a *live* listener and yield errors, latency or bad responses; none of them
removes the socket, and E1–E4 show the socket removed. The zero-count of `chaos_*` events
in E10 is reported as corroboration only, not as proof, since a zero count cannot by itself
establish that the event would have been emitted.

### H4 — load saturation or resource exhaustion — **invalidated**

Saturation has a shape, and this has none: six requests in 6.5 seconds, durations flat at
about 1 ms after a 17 ms cold first request, with no ramp and no queueing (E11, E7). The
process's whole observable life is 14 log lines (E10). A resource kill also arrives as a
signal — it does not log `"crashing now: exiting with code 1"` at CRITICAL tagged with the
request id of the endpoint whose job is to exit (E9). Note that no resource telemetry was
available at all (`/metrics` unreachable, E2), so this refutation is indirect.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Confirm the process state directly from the operator side (`scripts/lab.sh status`, or
   process-table inspection) — that closes the one gap between "the log stopped" and "the
   process exited," and confirms whether a supervisor exists at all.
2. Ask the operator who called `GET /simulate/crash` at 16:44:30.569Z from
   `127.0.0.1:63012` (E8). The trigger is external to konan; identifying the caller is the
   remaining unknown in the causal chain.
3. Once the service is listening again, read `/metrics` for `process_uptime_seconds` —
   a low value confirms a fresh process, and the counter reset marks the restart boundary
   for any later comparison.
4. Treat the absent restart as its own question for the operator: whether this deployment
   is expected to have a supervisor is a design fact, not something telemetry can settle.

## Gaps

- **The "ten minutes ago" window has no telemetry.** The log covers 6.5 seconds and there
  are no rotated backups (E10), so roughly 16:34–16:35 is unobservable. This is an artifact
  of how this environment was started, not evidence against the reporter. What is supported
  is narrower: the shop was healthy for about four seconds before the exit (E7, E11).
- **The exit status was not observed.** "Exiting with code 1" is the process's own log
  assertion (E9). Process-table and supervisor state are outside the surface contract in
  `docs/lab.md`, so the real wait status and the absence of a supervisor were inferred from
  the frozen log and the continuing refusals (E10, E1–E4), never read directly.
- **The whole metrics domain was blind.** `/metrics` is unreachable (E2), so
  `http_requests_total`, `http_exceptions_total`, `faultline_chaos_enabled`,
  `process_uptime_seconds` and `process_max_rss_bytes` contributed nothing. Any check that
  depends on counters was skipped, not passed.
- **User impact is unquantified.** Requests refused at TCP never reach the application and
  are therefore never logged; the only post-onset observations are konan's own probes
  (E1–E4). "Everyone" is consistent with the mechanism but is not measured.
