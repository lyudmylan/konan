---
konan_journal: 2
investigation:
  id: 2026-11-15-occasional-shop-errors
  trigger: 'manual — /konan human report. Complaint object: {"source": "human", "fingerprint": "human-1794755764", "labels": {"alertname": "human-report"}, "annotations": {"summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"}, "startsAt": "2026-11-15T15:16:04Z"}. Investigation start 2026-11-15T15:16:22Z; trigger latency 18 s.'
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-15T15:16:22Z
  concluded: 2026-11-15T15:21:17Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational error-injection switch inside the target (chaos mode) was turned on at 2026-11-15T15:15:56.681Z with failure_rate 0.08 and error_status 503; while it is on, the target rejects a random share of requests on every route with HTTP 503, and it is still on."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational error-injection switch inside the target (chaos mode) was turned on at 2026-11-15T15:15:56.681Z with failure_rate 0.08 and error_status 503; while on, it rejects a random share of requests with HTTP 503, and it is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception on specific inputs, and those requests fail."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E11, E12, E3, E5, E7, E9]
  - id: H3
    statement: "The process crashed or restarted, and requests failed around the restart."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E14]
    evidence_against: [E15, E16, E3, E5, E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:56.681Z"
    quote: '{"ts": "2026-11-15T15:15:56.681Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "ee0116db1ea3", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: metric
    source: "/metrics, request id konan-1794755908-4634 (scraped 2026-11-15T15:18:28.581Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:57.874Z"
    quote: '{"ts": "2026-11-15T15:15:57.874Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ad4a1cdbc4f9", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:57.875Z"
    quote: '{"ts": "2026-11-15T15:15:57.875Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "ad4a1cdbc4f9", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.139, "client": "127.0.0.1:53551"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:57.946Z"
    quote: '{"ts": "2026-11-15T15:15:57.946Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "67843af90f3a", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:57.946Z"
    quote: '{"ts": "2026-11-15T15:15:57.946Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "67843af90f3a", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.133, "client": "127.0.0.1:53556"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:58.178Z"
    quote: '{"ts": "2026-11-15T15:15:58.178Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "30db7f34201d", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:58.178Z"
    quote: '{"ts": "2026-11-15T15:15:58.178Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "30db7f34201d", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.135, "client": "127.0.0.1:53572"}'
  - id: E9
    type: metric
    source: "/metrics, request id konan-1794755908-4634 — the complete set of non-2xx series in http_requests_total"
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E10
    type: metric
    source: "/metrics, request id konan-1794755908-4634 — the exception counter section, complete (no series between the headers)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:57.785Z"
    quote: '{"ts": "2026-11-15T15:15:57.785Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "bdb7b81489b6", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.474, "client": "127.0.0.1:53545"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:57.960Z"
    quote: '{"ts": "2026-11-15T15:15:57.960Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "75317a3b5009", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.453, "client": "127.0.0.1:53557"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:54.621Z"
    quote: '{"ts": "2026-11-15T15:15:54.621Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8b7e4e8818d7", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.954, "client": "127.0.0.1:53541"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:51.718Z"
    quote: '{"ts": "2026-11-15T15:15:51.718Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: probe
    source: "/health, request id konan-1794755782-4515"
    quote: |-
      {"status":"ok","uptime_seconds":30.62056454177946}
      -- HTTP 200 in 0.002024s request_id=konan-1794755782-4515
  - id: E16
    type: metric
    source: "/metrics, request id konan-1794755908-4634 (scraped 2026-11-15T15:18:28.581Z)"
    quote: "process_uptime_seconds 156.87752762483433"
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:15:58.206Z"
    quote: '{"ts": "2026-11-15T15:15:58.206Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "66d71241a070", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.448, "client": "127.0.0.1:53574"}'
  - id: E18
    type: probe
    source: "/orders, request id konan-1794755804-4538"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T15:15:54.620+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T15:15:57.831+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T15:15:57.917+00:00"},{"id":4,"product_id":2,"quantity":2,"total_price":46.0,"created_at":"2026-11-15T15:15:58.004+00:00"},{"id":5,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T15:15:58.091+00:00"}]
      -- HTTP 200 in 0.001322s request_id=konan-1794755804-4538
gaps:
  - "The complaint says 'over the last few minutes', but the telemetry starts at 2026-11-15T15:15:51.718Z (the startup line; no rotated log backups; counters cover this process life only). Errors before that time can be neither confirmed nor excluded on this surface."
  - "An earlier instance of the process, and failures as refused connections before 15:15:51.718Z, would not reach this log or these counters. Launcher or supervisor records are outside the surface contract."
  - "Who turned the switch on, and why, is not on the surface. The log shows only the request id ee0116db1ea3 and a local client address."
  - "'Still on' rests on the gauge faultline_chaos_enabled, read 1 on every scrape up to 15:18:28.581Z. User traffic stopped at 15:15:58.206Z, so no injected failure was observed after 15:15:58.178Z; all 12 investigator probes returned 200, which an 8% rate allows."
  - "The sample is small: 32 user requests in about 1.5 s after the switch. The observed rate (3 of 32) is consistent with the configured 0.08 and cannot pin it more exactly."
  - "User traffic touched product ids 1, 2 and 5 only. No statement is made about ids 3 and 4; the investigator did not probe them."
usage:
  model: claude-fable-5-2
  tokens: 1253075
  wall_clock_seconds: 295
---

# Occasional HTTP 503 in the shop: error-injection switch (chaos mode) is on

## Summary

Verdict: root cause identified. This is not "probably nothing": it is a real, active, low-rate
degradation. An operational error-injection switch inside the target (chaos mode) was turned on at
15:15:56.681Z with `failure_rate` 0.08 and `error_status` 503 (E1), and the gauge still reads 1
(E2). While it is on, the target rejects a random share of requests with HTTP 503 before the route
code runs. Every non-2xx response in this process life is one of three 503s (E9), and each one has a
`chaos_failure` line on the same request id (E3/E4, E5/E6, E7/E8). The same input succeeds 90 ms
before and 85 ms after a failure (E11, E12), which matches "works on retry".

Impact, user traffic only: 3 of 32 user requests failed after the switch (about 9%), on three
routes. One was an order placement (E8); the order list holds orders 1 to 5 only (E18), so that
order was not created. No exception was raised (E10) and no latency was added (E1,
`extra_latency_ms` 0). Class `infra-process`, cause `degradation-switch`. Confidence: high for the
mechanism of the observed errors. The telemetry starts at 15:15:51.718Z, so errors earlier in the
"last few minutes" are outside the evidence (Gaps).

## Timeline

All times UTC, 2026-11-15.

- 15:15:51.718 — process start, the only startup marker (E14).
- 15:15:52.472 to 15:15:54.621 — 5 requests, all 200 or 201 (E13 is the last of them).
- 15:15:56.681 — **switch marker**: chaos mode enabled, failure_rate 0.08, error_status 503 (E1).
- 15:15:57.785 — `GET /products/2` → 200 (E11).
- 15:15:57.874 — first injected failure, `GET /products/2` → 503, 1.19 s after the marker (E3, E4).
- 15:15:57.946 — injected failure, `GET /products/1` → 503 (E5, E6).
- 15:15:57.960 — `GET /products/2` → 200 again (E12).
- 15:15:58.178 — injected failure, `POST /orders` → 503 (E7, E8).
- 15:15:58.206 — last user request in the log (E17).
- 15:16:04 — complaint raised (`startsAt`).
- 15:16:22 — investigation start; `/health` 200, uptime 30.6 s (E15).
- 15:18:28.581 — final scrape: switch gauge 1 (E2), uptime 156.9 s with no reset (E16), 503
  counters unchanged (E9), no exception series (E10).

## Investigation

Complaint object, as delivered by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794755764",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-11-15T15:16:04Z"
}
```

Investigation start: 2026-11-15T15:16:22Z (trigger latency 18 s). No severity was stated.

- **Baseline.** `/health` 200 (E15); `/metrics` showed three 503 series, no exception series, the
  switch gauge at 1, uptime 31 s; the business probes `/products` and `/orders` returned 200 (E18).
  The log held 54 lines from 15:15:51.718Z, with no rotated backups.
- **Triage.** Three lenses ran in parallel, each blind to the others: infra-process, interfaces,
  software-defect. All three found the switch marker and the three paired `chaos_failure` lines.
  The software-defect lens found no anomaly in its domain. The interfaces lens found a sharp onset
  after the marker and classed the mechanism as an internal switch, so `infra-process`. The
  infra-process lens found one startup, no restart, flat memory, and no latency change.
- **Deep-dive.** None. The triage evidence for H1 was deterministic and complete, so it went
  straight to the judge.
- **Judge.** One fresh judge saw the hypotheses and the verbatim evidence only. H1 validated; H2
  and H3 invalidated. The judge named two weak points of H1, both recorded under Gaps: "still on"
  rests on the gauge alone, and the evidence window is shorter than the complaint window. The judge
  also rated E13 as weak support and E17 as no support for H1; E17 stays in the ledger as a timeline
  fact only.
- One round, inside the budget.

## Hypotheses

### H1 — error-injection switch (chaos mode) is on — validated

The marker E1 gives the time and the parameters. Each of the three 503s is paired with a
`chaos_failure` line on its request id (E3/E4, E5/E6, E7/E8), and E9 shows that these three are the
complete non-2xx set of this process life. The failures spread over three routes and two methods,
and the same input succeeds before and after (E11, E12): probabilistic per request, not per input.
The 503s took about 0.13 ms against about 0.45 ms for successes (E4 against E11), so the rejection
happens before the route code. The observed rate is 3 of 32 user requests after the marker, against
a configured 0.08. No request failed before the marker (E13, weak: five requests only). The gauge
reads 1 (E2). No evidence against was found.

### H2 — unhandled exception on specific inputs — invalidated

The exception counter has no series for the whole process life (E10), and the log holds no
`unhandled_exception` line. The prediction "the same input fails every time" is refuted by E11 and
E12. Every 5xx carries an injection marker (E3, E5, E7), and E9 leaves no other 5xx. Limit: only
the inputs that users sent were exercised.

### H3 — process crash or restart — invalidated

E14 is the only startup marker, and one marker is a start, not a restart. Uptime rose from 30.6 s
(E15) to 156.9 s (E16) in step with the wall clock, so no reset happened in the window. The three
failures were answered by a live process with an injection marker (E3, E5, E7). Blind spot: an
earlier instance before 15:15:51.718Z is not visible on this surface (Gaps).

## Safe next steps

Read-only only.

- Ask the operator of the target whether the switch was turned on by intent, and by whom; the
  request id of the switch call is `ee0116db1ea3` (E1).
- Watch `faultline_chaos_enabled` and the three 503 series of `http_requests_total` on `/metrics`.
  New 503s with `chaos_failure` lines confirm that the degradation continues under user traffic.
- For any later 5xx, check that its request id has a `chaos_failure` line. A 5xx without one, or an
  `unhandled_exception` line, is a second cause and reopens H2.
- Read the launcher or supervisor records for an instance that ran before 15:15:51.718Z, to cover
  the part of the "last few minutes" that this telemetry does not hold.
- Check with the user who placed the failed order (request id `30db7f34201d`, E8) whether the retry
  created the order.

## Gaps

- **Window.** The complaint covers "the last few minutes". The telemetry starts at the startup line
  15:15:51.718Z; there are no rotated log backups, and the counters cover this process life only.
  Earlier errors can be neither confirmed nor excluded.
- **Earlier instance.** Refused connections before the startup would not reach this log or these
  counters. Launcher or supervisor records are outside the surface contract.
- **Who and why.** The surface shows that the switch was turned on, not who did it or for what
  reason.
- **"Still on".** This rests on the gauge, read 1 on every scrape up to 15:18:28.581Z. User traffic
  stopped at 15:15:58.206Z, so no injected failure was observed after 15:15:58.178Z. All 12
  investigator probes returned 200, which an 8% rate allows.
- **Sample size.** 32 user requests in about 1.5 s after the switch. The observed rate is
  consistent with 0.08 and cannot pin it more exactly.
- **Inputs not exercised.** User traffic touched product ids 1, 2 and 5 only. No statement is made
  about ids 3 and 4; the investigator did not probe them.
