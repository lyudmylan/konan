---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-occasional-503
  trigger: "manual — /konan human report; complaint object: source=human, fingerprint=human-1794782122, labels.alertname=human-report (no severity stated), startsAt=2026-11-15T22:35:22Z; investigation start 2026-11-15T22:35:30Z (trigger latency 8 s)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-15T22:35:30Z
  concluded: 2026-11-15T22:39:08Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational error-injection switch inside the target (chaos mode) was turned on at 2026-11-15T22:35:14.209Z with failure_rate 0.08 and error_status 503; while it is on, a random share of requests fails with HTTP 503 and the same request succeeds on retry; it was still on at 22:37:01Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational error-injection switch inside the target (chaos mode) was turned on at 2026-11-15T22:35:14.209Z with failure_rate 0.08 and error_status 503; while it is on, it fails a random share of requests with HTTP 503 (seen on GET /orders and GET /products/1), and the same input succeeds at other times; it was still on at 22:37:01Z."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E10, E11, E12]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception on a specific input, and that input is what users hit."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E9, E10, E11, E12]
  - id: H3
    statement: "The process is unstable (crash, restart loop, or resource exhaustion), and users hit errors during restarts."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E8, E12, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:09.284Z"
    quote: |-
      {"ts": "2026-11-15T22:35:09.284Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:12.156Z"
    quote: |-
      {"ts": "2026-11-15T22:35:12.156Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "25a28e3ea665", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.996, "client": "127.0.0.1:56958"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:14.209Z"
    quote: |-
      {"ts": "2026-11-15T22:35:14.209Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "08c2c229fcf5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:14.209Z"
    quote: |-
      {"ts": "2026-11-15T22:35:14.209Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "08c2c229fcf5", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.47, "client": "127.0.0.1:56959"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:15.508Z"
    quote: |-
      {"ts": "2026-11-15T22:35:15.508Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "d1a310146f45", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-15T22:35:15.508Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "d1a310146f45", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.145, "client": "127.0.0.1:56976"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:15.633Z"
    quote: |-
      {"ts": "2026-11-15T22:35:15.633Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "9f388409cfb0", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.408, "client": "127.0.0.1:56985"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:35:15.716Z"
    quote: |-
      {"ts": "2026-11-15T22:35:15.716Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "aaa16bf4237e", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T22:35:15.716Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "aaa16bf4237e", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.131, "client": "127.0.0.1:56991"}
  - id: E8
    type: metric
    source: "/metrics, request_id=konan-1794782143-25683 @ 2026-11-15T22:35:43Z"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 33.87651791609824
      process_max_rss_bytes 46956544
  - id: E9
    type: metric
    source: "/metrics, request_id=konan-1794782143-25683 @ 2026-11-15T22:35:43Z (the exceptions counter has HELP and TYPE lines and no sample line)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:36:26.902Z (investigator probe, request id prefix konan-)"
    quote: |-
      {"ts": "2026-11-15T22:36:26.902Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794782186-25732", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T22:36:26.902Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "konan-1794782186-25732", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.373, "client": "127.0.0.1:57023"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T22:36:36.993Z (investigator probe, same path as E10, ten seconds later)"
    quote: |-
      {"ts": "2026-11-15T22:36:36.993Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794782196-25744", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.624, "client": "127.0.0.1:57025"}
  - id: E12
    type: metric
    source: "/metrics, request_id=konan-1794782221-25756 @ 2026-11-15T22:37:01Z"
    quote: |-
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 1
      process_uptime_seconds 112.26775666605681
      process_max_rss_bytes 46956544
  - id: E13
    type: probe
    source: "/health, request_id=konan-1794782142-25678 @ 2026-11-15T22:35:42Z"
    quote: |-
      {"status":"ok","uptime_seconds":33.33662270801142}
      -- HTTP 200 in 0.002718s request_id=konan-1794782142-25678
gaps:
  - "No telemetry before the process start at 2026-11-15T22:35:09.283Z: the log has no rotated backups. The complaint says 'over the last few minutes'; the surface covers 13 seconds before the complaint time. Errors that users saw before 22:35:09Z cannot be attributed, and the reason for the process start is unknown."
  - "Who turned the switch on, and why, is not visible: the log shows only the call (E4, client 127.0.0.1:56959). The switch's own endpoint is operator surface, outside the investigator's contract."
  - "The scope of the switch is not proven beyond two GET routes (GET /orders, GET /products/1). All 6 POST /orders requests returned 201; whether any route is exempt is not shown."
  - "The sample is small: 3 failures (2 user, 1 investigator probe) in about 40 requests. The 8% rate is the configured value in E3, not a measured rate."
  - "The complaint names no status code, route, or request id. The link between the complaint and the 503 responses is by fit (occasional, works on retry), not by a matched user request."
  - "The absence claims (no unhandled_exception line, one startup event, no chaos_disabled line) come from a full read of the 58-line log; they assume the target logs those events when they happen."
  - "Token totals were not captured (interactive session)."
usage:
  model: claude-fable-5-2
  tokens: 1266438
  wall_clock_seconds: 218
---

# Shop: occasional HTTP 503 from an error-injection switch that is on

## Summary

**Root cause identified, and the incident is active.** An operational error-injection
switch inside the target ("chaos mode") was turned on at 22:35:14.209Z with
`failure_rate` 0.08 and `error_status` 503 (E3, E4). Since then a random share of
requests fails with HTTP 503, and each failure carries a `chaos_failure` marker on the
same request id (E5, E7, E10). The same input succeeds at other times (E6 against E7,
E11 against E10), which matches "it works on retry". The switch was still on at
22:37:01Z (E12).

Impact on users, counted without investigator traffic: 2 of 32 requests after the
switch failed (6.25%) — one `GET /orders`, one `GET /products/1`. All 6 `POST /orders`
requests returned 201. No unhandled exception, no restart, no latency change.

Confidence: high for the mechanism (the target labels each failure itself). The
complaint is not "nothing": the error share is small by configuration, and it continues
while the switch is on. Class `infra-process`, cause `degradation-switch`.

## Timeline

All times UTC, 2026-11-15.

- 22:35:09.284 — process start, `startup` event (E1). Nothing earlier is visible.
- 22:35:12.156 — last request before the switch, `POST /orders -> 201` (E2). The 5
  requests before the switch all returned 200 or 201.
- **22:35:14.209 — switch on: `chaos_enabled`, `failure_rate` 0.08, `error_status` 503
  (E3), through `POST /chaos/enable -> 200` (E4). Configuration-change marker.**
- 22:35:15.508 — first failure, `GET /orders -> 503` with `chaos_failure` (E5).
- 22:35:15.633 — `GET /products/1 -> 200` (E6).
- 22:35:15.716 — `GET /products/1 -> 503` with `chaos_failure` (E7).
- 22:35:22 — complaint raised (`startsAt`).
- 22:35:30 — investigation start.
- 22:35:42–43 — baseline: `/health` 200 (E13); gauge `faultline_chaos_enabled 1`,
  uptime 33.9 s, no exception series (E8, E9).
- 22:36:26.902 — investigator probe `GET /products/1 -> 503` with `chaos_failure` (E10).
- 22:36:36.993 — investigator probe, same path, 200 (E11).
- 22:37:01 — second scrape: gauge still 1, uptime 112.3 s, peak memory unchanged, 503
  counters 1 + 2, no exception series (E12).

## Investigation

**Complaint object** (adapter `/konan`, `docs/triggers.md`):

```json
{
  "source": "human",
  "fingerprint": "human-1794782122",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-11-15T22:35:22Z"
}
```

Investigation start: 2026-11-15T22:35:30Z. Trigger latency: 8 s. No severity was stated,
so none is recorded.

**Baseline.** `/health` 200 (E13). `/metrics`: two 503 series, no exception series, the
chaos gauge at 1, uptime 33.9 s (E8, E9). Log: 54 lines from the process start, two
access lines with status 503.

**Triage.** Three lenses in parallel, each blind to the others: software-defect,
infra-process, interfaces. All three reported the same marker (E3) and the paired
`chaos_failure` lines. The software-defect lens found no exception evidence and ran
three read-only probes (E10, E11, and one `GET /orders` that returned 200). The
interfaces lens placed the mechanism outside its own class: an internal switch is
`infra-process`. The infra-process lens found one startup, no restart, no latency or
memory signal.

**Deep-dive.** None. The triage evidence for H1 was deterministic and complete (the
target marks each failure), so H1 went straight to the judge, as the skill allows.

**Judge.** One fresh judge, evidence only. H1 validated, H2 invalidated, H3
invalidated for the window 22:35:09Z–22:37:01Z. The judge narrowed H1: "on any route"
was not supported, so the statement now names the two GET routes seen. The judge also
received whole-log counts as a summary (58 lines; 0 `unhandled_exception`; 1 `startup`;
0 `chaos_disabled`; 3 access lines with 5xx; 32 non-investigator access lines after the
switch, 2 of them 503). Those counts are a summary, not a verbatim quote, so they are
not a ledger entry; they stand in Gaps as an assumption.

Budget used: one triage round, no deep-dive round, one judge.

## Hypotheses

### H1 — error-injection switch is on (validated)

The marker E3 sets a failure rate of 0.08 and an error status of 503; E4 is the call
that set it. Every 5xx in the log is a 503 with a `chaos_failure` line on the same
request id (E5, E7, E10), and the counters in E12 (1 + 2) agree with the log count.
The failure is not bound to an input: `GET /products/1` returns 200 and 503 within
83 ms (E6, E7), and again across a retry (E10, E11). The gauge reads 1 in both scrapes
(E8, E12). The clean period before the switch (E2) is weak support alone — 5 requests
in 5 seconds — the markers carry the attribution. No evidence against was found.

### H2 — unhandled exception on a specific input (invalidated)

The exception counter has no sample line in either scrape (E9, E12), and the log has no
`unhandled_exception` line. No input fails each time (E6/E7, E10/E11). Each 5xx is
explained by the switch. A 5xx access line with no `chaos_failure` marker, or any
`http_exceptions_total` sample, would reverse this.

### H3 — unstable process (invalidated for the visible window)

A process start 13 seconds before the complaint (E1) is the only support. Against it:
uptime rose from 33.9 s to 112.3 s across scrapes 78 s apart (E8, E12), peak memory is
identical in both, `/health` returned 200 (E13), and the log has one `startup` event.
All three failures happened inside this one process lifetime. What happened before
22:35:09Z is out of reach.

## Safe next steps

Read-only only:

- Ask the operator of the target whether the switch call at 22:35:14.209Z (request id
  `08c2c229fcf5`) was a planned test.
- Watch `faultline_chaos_enabled` and the `status="503"` series of
  `http_requests_total` in `/metrics`; look for a `chaos_disabled` line in the log.
- Ask the reporting users for the time and the page of an error, and match it to a
  `chaos_failure` request id in the log.
- If a 5xx access line appears with no `chaos_failure` marker, open a new investigation:
  that is a second cause.

## Gaps

- **History before the process start.** The log begins at 22:35:09.283Z with no rotated
  backups. "Over the last few minutes" is covered for 13 seconds only. Earlier user
  errors, and the reason for the process start, cannot be read.
- **Who and why.** The log shows the switch call and its client address, nothing more.
  The switch's own endpoint is outside the investigator's surface.
- **Scope of the switch.** Failures were seen on two GET routes. No POST request failed
  in 6; an exemption is not proven and not excluded.
- **Small sample.** 3 failures in about 40 requests. The 8% rate is the configured
  value, not a measurement.
- **Complaint-to-evidence link.** The complaint gives no status code, route, or request
  id. The match is by shape.
- **Absence claims.** They rest on a full read of a 58-line log and on the assumption
  that the target logs those events.
- **Tokens.** Not captured in this session.
