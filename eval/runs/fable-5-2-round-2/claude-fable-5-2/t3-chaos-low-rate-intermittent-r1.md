---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-intermittent-503
  trigger: 'manual — /konan human profile. Complaint object: {"source": "human", "fingerprint": "human-1794778099", "labels": {"alertname": "human-report"}, "annotations": {"summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"}, "startsAt": "2026-11-15T21:28:19Z"}. Investigation start 2026-11-15T21:28:25Z; trigger latency 6 s. No severity stated by the reporter.'
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-15T21:28:25Z
  concluded: 2026-11-15T22:03:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational error-injection switch inside the target (chaos mode) was enabled at 2026-11-15T21:28:11.342Z with failure_rate 0.08 and error_status 503; while on, it fails a fraction of requests with HTTP 503 before the request logic runs, and it was still on at 22:01:41Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational error-injection switch inside the target (chaos mode) was enabled at 21:28:11.342Z with failure_rate 0.08 and error_status 503; it injects HTTP 503 on a fraction of requests and produced the recorded user error; the switch is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E8, E12, E14]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception on some order input, and that request fails."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E6]
  - id: H3
    statement: "The process crashed or restarted, and requests failed during the restart."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E7]
    evidence_against: [E5, E8, E9, E12]
  - id: H4
    statement: "A gateway tier or a downstream dependency failed on its own and returned the 503."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E5]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:11.342Z"
    quote: '{"ts": "2026-11-15T21:28:11.342Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "a7c2dc1f88b1", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:12.657Z"
    quote: '{"ts": "2026-11-15T21:28:12.657Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "f9d96d93767a", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:12.657Z"
    quote: '{"ts": "2026-11-15T21:28:12.657Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "f9d96d93767a", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.143, "client": "127.0.0.1:56696"}'
  - id: E4
    type: metric
    source: "/metrics @ 2026-11-15T22:01:41Z (request id konan-1794780101-25324)"
    quote: "faultline_chaos_enabled 1"
  - id: E5
    type: metric
    source: "/metrics @ 2026-11-15T22:01:41Z (request id konan-1794780101-25324); same values @ 2026-11-15T21:28:38Z (request id konan-1794778118-25103)"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 5 / http_requests_total{method="POST",path="/orders",status="503"} 1'
  - id: E6
    type: metric
    source: "/metrics @ 2026-11-15T22:01:41Z (request id konan-1794780101-25324) — the exception counter has a header and no series"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter / # HELP faultline_chaos_enabled Whether chaos mode is active."
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:06.407Z"
    quote: '{"ts": "2026-11-15T21:28:06.407Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:09.284Z"
    quote: '{"ts": "2026-11-15T21:28:09.284Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d79f5b8af115", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.591, "client": "127.0.0.1:56677"}'
  - id: E9
    type: probe
    source: "/health (request id konan-1794778117-25098)"
    quote: '{"status":"ok","uptime_seconds":31.046417917124927} -- HTTP 200 in 0.001517s request_id=konan-1794778117-25098'
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-15T22:01:41Z (request id konan-1794780101-25324)"
    quote: "process_uptime_seconds 149.71978725027293 / process_max_rss_bytes 48087040"
  - id: E11
    type: probe
    source: "/orders (request id konan-1794780101-25329)"
    quote: '[{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T21:28:09.284+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T21:28:12.488+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T21:28:12.573+00:00"},{"id":4,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T21:28:12.741+00:00"},{"id":5,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T21:28:12.826+00:00"}] -- HTTP 200 in 0.001503s request_id=konan-1794780101-25329'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:12.741Z"
    quote: '{"ts": "2026-11-15T21:28:12.741Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "ab59dfd65902", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.68, "client": "127.0.0.1:56702"}'
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-15T21:28:38Z (request id konan-1794778118-25103)"
    quote: "process_uptime_seconds 31.713119499851018 / process_max_rss_bytes 48087040"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T21:28:11.342Z"
    quote: '{"ts": "2026-11-15T21:28:11.342Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "a7c2dc1f88b1", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 1.925, "client": "127.0.0.1:56678"}'
gaps:
  - "The complaint says 'the last few minutes', but the log starts at 21:28:06.407Z (13 s before the complaint) and has no rotated backups; nothing before that start is observable on this surface."
  - "The complaint names no time, route, or status, so the reported errors cannot be matched one-to-one with request f9d96d93767a; the link rests on that request being the only non-2xx response on record."
  - "No user traffic after 21:28:12.854Z; the current failure rate cannot be measured, only the switch state (on at 22:01:41Z)."
  - "Who or what sent the enable request is not on the surface: the access line shows only client 127.0.0.1:56678 and no caller identity."
  - "The enable marker carries no route field; with one failure on record, the surface does not show whether the switch affects only POST /orders or every route."
  - "The uptime gauge moved 118 s (E13 to E10) while the wall clock moved 1983 s; counters and peak RSS did not reset, so a suspended process or host fits, but no host sleep record is on the surface. The gauge is not a reliable clock for this timeline."
  - "The failure was not reproduced by the investigator: probes are GET-only, and no probe received a 503."
  - "A gateway error that never reached the target would not appear in this log or these metrics; the lab contract lists no gateway tier."
  - "The journal was not validated mechanically against journal.schema.json in this session; it was checked by hand."
usage:
  model: claude-fable-5-2
  tokens: 1488182
  wall_clock_seconds: 2118
---

# Intermittent 503 on orders — error-injection switch enabled in the shop

## Summary

**Root cause identified, not "nothing".** An operational error-injection switch inside
the target (chaos mode) was enabled at 21:28:11.342Z with `failure_rate` 0.08 and
`error_status` 503 (E1, E14). From that moment the target fails a fraction of requests
with HTTP 503 before the request logic runs. One user order request failed this way at
21:28:12.657Z, tagged `chaos_failure` (E2, E3); the next order request succeeded (E12),
which matches "works on retry". The switch was still on at 22:01:41Z (E4).

Impact on record: 1 of 6 user order requests (E5), 1 of 32 user requests after the
switch went on. The failed order left no partial write (E11). No unhandled exception
(E6), no restart (E5, E9). Confidence is high for the mechanism; the match between the
reported errors and the recorded 503 is by exclusion (see Gaps).

Complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794778099",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-11-15T21:28:19Z"
}
```

Investigation start: 2026-11-15T21:28:25Z (trigger latency 6 s).

## Timeline

- 21:28:06.407Z — process start, the only `startup` event in the log (E7).
- 21:28:09.284Z — `POST /orders -> 201`, the only order request before the switch (E8).
- 21:28:11.342Z — **switch marker**: `chaos_enabled`, `failure_rate` 0.08,
  `error_status` 503, through `POST /chaos/enable -> 200` from 127.0.0.1:56678 (E1, E14).
- 21:28:12.657Z — `chaos_failure` on `POST /orders`, then `POST /orders -> 503` in
  0.143 ms, same request id (E2, E3).
- 21:28:12.741Z — next `POST /orders -> 201` (E12).
- 21:28:12.854Z — last user request on record.
- 21:28:19Z — complaint raised.
- 21:28:37Z–21:28:38Z — baseline: `/health` 200 (E9), uptime 31.7 s (E13).
- 22:01:41Z — `faultline_chaos_enabled 1`, order counters unchanged, exception counter
  empty, orders 1–5 present (E4, E5, E6, E10, E11).

## Investigation

- **Baseline**: `/health`, `/metrics`, full log (52 lines at that time). The baseline
  already showed the switch marker, one 503, and the gauge at 1.
- **Triage**: three lenses in parallel, blind to each other — infra-process,
  interfaces, software-defect. All three reported the same switch marker and injected
  failure. The software-defect lens found no exception evidence. The interfaces lens
  found no contract violation and no orphan order. The infra-process lens found no
  restart or saturation and reported the uptime gauge gap.
- **Deep-dive**: skipped. The triage evidence for H1 was deterministic and complete;
  the orchestrator verified the quotes with a fresh `/metrics` and `/orders` probe.
- **Judge**: H1 validated; H2, H3, H4 invalidated. The judge rejected E3 as support
  for H2 and H4 (every hypothesis predicts it) and rejected E10 as proof of continuous
  uptime; both corrections are applied in the machine core.
- Budget used: one triage round, no deep-dive round.

## Hypotheses

### H1 — error-injection switch (validated)

The marker (E1) precedes the first failure by 1.3 s, and its access line shows the
enable request (E14). The failed request carries the injection tag and the 503 under
one request id (E2, E3). The 503 took 0.143 ms against 0.66–0.69 ms for successful
orders, so it was rejected before the order logic. Successes surround it on the same
route (E8, E12). It is the only non-2xx response on record (E5), and the gauge still
reads 1 (E4). Nothing found against.

### H2 — unhandled exception in the target's code (invalidated)

The exception counter has no series (E6), the log has no `unhandled_exception` event,
and the only 503 is tagged as injected (E2).

### H3 — crash or restart (invalidated)

One startup marker (E7) is the only support, and it precedes all traffic. Counters did
not reset (E5), health answered 200 (E9), and the live process served the 503 between
two 201 responses (E8, E12). The uptime gauge gap (E13, E10) is recorded under Gaps,
not as a restart.

### H4 — gateway or dependency failure (invalidated)

The target's own request logger produced the 503 with an injection tag (E2, E3), and
no untagged 503 exists (E5).

## Safe next steps

- Ask the operators whether the enable request at 21:28:11.342Z (request id
  `a7c2dc1f88b1`) was intended.
- Read `faultline_chaos_enabled` and the `POST /orders` 503 counter again when user
  traffic resumes; an 8 % rate predicts more 503 responses on new traffic.
- Read the log for a `chaos_disabled` event to mark the end of the impact window.
- Ask the reporters for the time, page, and error text of one failure, to match it
  with request `f9d96d93767a`.

## Gaps

- **History before 21:28:06Z**: the log starts 13 s before the complaint and has no
  backups. "The last few minutes" cannot be checked.
- **Complaint match**: by exclusion only; the complaint names no time, route, or status.
- **Current impact**: no user traffic after 21:28:12.854Z. Only the switch state is
  confirmed.
- **Caller of the switch**: client address only, no identity.
- **Scope of the switch**: one failure on one route; the marker has no route field.
- **Uptime gauge**: 118 s of uptime across 1983 s of wall clock, with no counter or
  RSS reset. A suspended process or host fits; not proven.
- **No reproduction**: probes are GET-only and none received a 503.
- **Gateway**: an error that never reached the target is invisible here.
- **Schema check**: by hand only, not mechanical.
