---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-slowness
  trigger: 'manual (human profile, /konan). Complaint object: {"source": "human", "fingerprint": "human-1794754339", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."}, "startsAt": "2026-11-15T14:52:19Z"}. Investigation start: 2026-11-15T14:52:40Z. Trigger latency: 21 s.'
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-15T14:52:40Z
  concluded: 2026-11-15T14:56:12Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational switch inside the target (chaos mode) was turned on at 2026-11-15T14:52:02.479Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on, it adds a variable delay of up to about 1500 ms to every business request, and the health route is not affected."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode), turned on at 14:52:02.479Z with extra_latency_ms 1500 and failure_rate 0.0, adds latency to every business route while the health route stays fast; this is the cause of the user-facing slowness."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's code on the product detail route (a division by zero for product 3) is the cause of the user-facing incident, including the error page that some users saw."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E13, E14, E15, E16]
    evidence_against: [E17, E18]
  - id: H3
    statement: "The process restarted (startup at 14:51:56.538Z) and the slowness is a consequence of the restart or of resource pressure in the process."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E2, E3, E19]
latent_findings:
  - statement: "GET /products/3 fails with an unhandled ZeroDivisionError (division by units_in_stock in get_product) on every request, 2 of 2; only investigator probes triggered it in the visible window, so it is not the active incident."
    evidence: [E13, E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:51:56.538Z (the only startup event in the file; the file has no rotated backups and begins at this timestamp)"
    quote: '{"ts": "2026-11-15T14:51:56.538Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:51:57.301Z"
    quote: '{"ts": "2026-11-15T14:51:57.301Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "902296547507", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.06, "client": "127.0.0.1:53238"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:51:58.358Z and @ 2026-11-15T14:51:59.419Z (the last business requests before the marker of E4)"
    quote: |-
      {"ts": "2026-11-15T14:51:58.358Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c3d836ad61d2", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.004, "client": "127.0.0.1:53239"}
      {"ts": "2026-11-15T14:51:59.419Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "edf7ef8413f7", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.956, "client": "127.0.0.1:53240"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:52:02.479Z"
    quote: '{"ts": "2026-11-15T14:52:02.479Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "fca631f00292", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:52:04.735Z (the first business request after the marker of E4)"
    quote: '{"ts": "2026-11-15T14:52:04.735Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "9d6d4ca1676c", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 196.306, "client": "127.0.0.1:53243"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:52:06.488Z and @ 2026-11-15T14:52:08.717Z"
    quote: |-
      {"ts": "2026-11-15T14:52:06.488Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "80643a7e911d", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 686.598, "client": "127.0.0.1:53244"}
      {"ts": "2026-11-15T14:52:08.717Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "63ccf5e48991", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1164.083, "client": "127.0.0.1:53245"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:52:11.204Z"
    quote: '{"ts": "2026-11-15T14:52:11.204Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "4228bd50b576", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1421.057, "client": "127.0.0.1:53246"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:52:13.634Z"
    quote: '{"ts": "2026-11-15T14:52:13.634Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "53a44405d2ba", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1362.745, "client": "127.0.0.1:53247"}'
  - id: E9
    type: metric
    source: "/metrics read at 2026-11-15T14:54:14Z, request_id=konan-1794754454-3283 (the log has no chaos_disabled event up to 14:54:14.720Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: probe
    source: "/health, request_id=konan-1794754361-3183, at 2026-11-15T14:52:41Z (after the marker of E4)"
    quote: |-
      {"status":"ok","uptime_seconds":44.602709458675236}
      -- HTTP 200 in 0.002147s request_id=konan-1794754361-3183
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:53:25.837Z (investigator probe of a business route)"
    quote: '{"ts": "2026-11-15T14:53:25.837Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794754404-3240", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1465.704, "client": "127.0.0.1:53276"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:53:28.133Z (investigator probe of the same route, 3 seconds after E11)"
    quote: '{"ts": "2026-11-15T14:53:28.133Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794754408-3245", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 48.388, "client": "127.0.0.1:53277"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:53:37.267Z (the stack field is trimmed to its last frame, the trim is marked with an ellipsis, and the checkout prefix of its file path is redacted as <checkout>)"
    quote: '{"ts": "2026-11-15T14:53:37.267Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794754416-3263", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:53:37.284Z"
    quote: '{"ts": "2026-11-15T14:53:37.284Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794754416-3263", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1020.966, "client": "127.0.0.1:53280"}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:53:49.637Z"
    quote: '{"ts": "2026-11-15T14:53:49.637Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794754429-3276", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 545.882, "client": "127.0.0.1:53283"}'
  - id: E16
    type: metric
    source: "/metrics read at 2026-11-15T14:54:14Z, request_id=konan-1794754454-3283"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E17
    type: metric
    source: "/metrics read at 2026-11-15T14:52:41Z, request_id=konan-1794754361-3188, before any investigator probe of a business route (the complete list of request series and the exceptions block, which has no series)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E18
    type: log
    source: "lab/logs/app.log, whole file from 2026-11-15T14:51:56.538Z to 14:54:14.720Z, read for 5xx access lines, unhandled_exception events and chaos_failure events: the file has two unhandled_exception events and two 5xx access lines (E14, E15), all four with investigator request ids, and no chaos_failure event; the quote is the two unhandled_exception events, trimmed to the fields kept"
    quote: |-
      "ts": "2026-11-15T14:53:37.267Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794754416-3263", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"
      "ts": "2026-11-15T14:53:49.627Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794754429-3276", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"
  - id: E19
    type: metric
    source: "/metrics, two reads: at 2026-11-15T14:52:41Z (request_id=konan-1794754361-3188, the first two lines) and at 14:54:14Z (request_id=konan-1794754454-3283, the last two lines)"
    quote: |-
      process_uptime_seconds 44.928688041865826
      process_max_rss_bytes 47497216
      process_uptime_seconds 138.1950435419567
      process_max_rss_bytes 48611328
gaps:
  - "The error page that some users saw is not explained: the visible window (from 14:51:56.538Z) has no 5xx response and no exception with a non-investigator request id, and the switch has failure_rate 0.0."
  - "No telemetry exists before 14:51:56.538Z: the log begins at the process start, it has no rotated backups, and the counters began at zero. An event before that time (an earlier error page, an earlier process) is out of reach."
  - "Who turned the switch on, and why, is not visible: the log shows only the marker and its request (request_id fca631f00292, client 127.0.0.1:53241). The operator surface is outside the surface contract, so the current parameters of the switch were read only through the gauge and the marker."
  - "The size of the added delay is inferred from the 9 quoted requests after the marker (48 ms to 1466 ms, all below the configured 1500 ms). The code of the switch is out of reach, so the distribution of the delay is not known."
  - "The load-saturation, third-party and data-db classes have no lens in this repo. The request counters show a low volume (fewer than 30 requests in the window), which is the only check on load."
  - "Product ids other than 1, 2 and 3 were not probed, so the extent of the latent defect on the product detail route is not known."
  - "The journal was checked against the schema by hand; no interpreter was available to this session for an automated check."
usage:
  model: claude-fable-5-2
  tokens: 1474477
  wall_clock_seconds: 212
---

# Shop-wide slowness from an operational switch that injects latency

## Summary

**Verdict: root cause identified.** An operational switch inside the target (chaos mode)
was turned on at 14:52:02.479Z with `extra_latency_ms: 1500` and `failure_rate: 0.0`
(E4). From the next business request onward, every business route answered in 196 ms to
1421 ms instead of 1 ms to 2 ms, with 2xx statuses (E2, E3, E5 to E8). The delay is
variable, up to about 1500 ms (E11, E12). The health route is not affected (E10), which
is why health checks are green and fast. The switch was still on at 14:54:14Z (E9).
Class `infra-process`, cause `degradation-switch`. Confidence is high for the slowness:
the onset is sharp, it follows the marker by 2 seconds, and live probes reproduced it.

The error page in the complaint is **not explained**. The switch injects no errors
(`failure_rate: 0.0`, no `chaos_failure` event), and the visible window has no 5xx
response to a user (E17, E18). The investigation found one latent defect that can produce
an error page: `GET /products/3` raises an unhandled `ZeroDivisionError` on every request
(E13 to E16). Only investigator probes triggered it, so it is a latent finding and not
the active incident.

## Timeline

All times are UTC, 2026-11-15.

- 14:51:56.538 — process startup, the only one in the log (E1).
- 14:51:57 to 14:51:59 — business requests answer in 1 ms to 2 ms (E2, E3).
- 14:52:02.479 — **change marker**: `chaos mode enabled`, `failure_rate` 0.0,
  `error_status` 503, `extra_latency_ms` 1500 (E4).
- 14:52:04.735 — first business request after the marker: 196 ms (E5).
- 14:52:06 to 14:52:13 — business requests answer in 687 ms to 1421 ms on the product,
  order and order-list routes, all 2xx (E6, E7, E8).
- 14:52:19 — the complaint is raised (`startsAt`).
- 14:52:40 — the investigation starts.
- 14:52:41 — health answers in 2 ms (E10); the counters show 2xx only and no exception
  (E17).
- 14:53:25 to 14:53:28 — investigator probes of `/products`: 1466 ms, then 48 ms
  (E11, E12).
- 14:53:37 and 14:53:49 — investigator probes of `/products/3` return 500 with a
  `ZeroDivisionError` (E13, E14, E15).
- 14:54:14 — the gauge of the switch still reads 1 (E9); the exception counter reads 2,
  equal to the two investigator probes (E16); one process, flat memory (E19).

## Investigation

**Complaint object** (manual trigger, human profile), verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794754339",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-15T14:52:19Z"
}
```

Investigation start: 2026-11-15T14:52:40Z. Trigger latency: 21 seconds. The reporter
stated no severity.

**Baseline.** `/health` 200 in 2 ms (E10). `/metrics`: 2xx series only, no exception
series, `faultline_chaos_enabled 1`, uptime 45 s (E17, E19). The log: one startup, fast
business requests, then the marker of E4, then slow business requests.

**Triage.** Three lenses ran in parallel, each blind to the others: infra-process,
interfaces, software-defect. The infra-process lens and the interfaces lens each found
the marker and the before/after latency change, and each reproduced the slowness with
live probes. The interfaces lens named the class as `infra-process`, because the switch
is internal to the target. The software-defect lens found the `ZeroDivisionError` on
`/products/3` with its own probes and reported that no user request had triggered it.

**Deep-dive.** None. The triage evidence for H1 was deterministic and complete (marker,
gauge, before/after durations, live reproduction), so H1 went straight to the judge.

**Judge.** One fresh judge saw the three hypotheses and the verbatim evidence only.
Verdicts: H1 validated, H2 invalidated, H3 invalidated. The judge required the wording
"up to 1500 ms" for the delay, because E12 shows a 48 ms response while the switch is on.
The judge also removed E4 from the evidence against H2: a failure rate of 0.0 shows only
that H1 does not explain the error page either.

## Hypotheses

### H1 — an operational switch injects latency (validated)

The marker of E4 sits between the last fast business request (E3, 14:51:59.419Z, 2 ms)
and the first slow one (E5, 14:52:04.735Z, 196 ms). After it, every business request in
the log is slow, on every business route, with a 2xx status (E5 to E8). The same input
went from 1 ms to 1164 ms (`GET /products/1`, E3 against E6). Health stayed at 2 ms
(E10). The gauge reads 1 and the log has no `chaos_disabled` event (E9). Live probes
reproduced the delay and its variability: 1466 ms, then 48 ms, on the same route (E11,
E12). All observed delays are below the configured 1500 ms. No evidence contradicts the
hypothesis. The causal link rests on the timing and on the upper bound, not on the code
of the switch.

### H2 — a code defect on the product detail route causes the incident (invalidated)

The defect is real and deterministic: `GET /products/3` failed 2 of 2 times with a
`ZeroDivisionError` at `shop.py` line 64 (E13, E14, E15), and the counters agree (E16).
It is not the incident. Before the first investigator probe, no 5xx series and no
exception series existed (E17). The whole log has no 5xx access line and no exception
with a non-investigator request id (E18). The defect also cannot explain slowness on
every route. It is recorded as a latent finding. One 5xx access line with a
non-investigator request id at the time of the reported error page would settle whether
this defect produced that page.

### H3 — a process restart or resource pressure causes the slowness (invalidated)

The process started at 14:51:56.538Z (E1), 23 seconds before the complaint. The requests
after the startup and before the marker were fast (E2, E3), so the slowness does not
start at the startup. Uptime advanced by 93 s between two reads 93 s apart, so there was
no second start, and peak memory grew by about 1 MB (E19). The log does not show whether
an earlier process existed.

## Safe next steps

- Ask the owner of the operator surface to read the state of the switch and to confirm
  the change of request `fca631f00292` at 14:52:02.479Z (who, why, for how long).
- Watch the log for a `chaos_disabled` event, and compare the durations of business
  requests before and after it; a return to 1 ms to 2 ms confirms the mechanism.
- Ask the reporters for the time and the page of the error. Look for a 5xx access line
  with a non-investigator request id at that time, in this log and in any log kept from
  before 14:51:56.538Z.
- Watch `http_requests_total{path="/products/{product_id}",status="500"}` and
  `http_exceptions_total{type="ZeroDivisionError"}` for growth from user traffic, and
  hand the latent finding with E13 to the owner of the code.

## Gaps

- **The error page is unexplained.** No user-facing 5xx and no exception from user
  traffic exist in the visible window, and the switch injects no errors.
- **No telemetry before 14:51:56.538Z.** The log begins at the process start, with no
  rotated backups, and the counters began at zero. "The last few minutes" of the
  complaint reach further back than the telemetry does.
- **The actor behind the switch is not visible.** The log shows the marker and its
  request only. The operator surface is outside the surface contract.
- **The distribution of the delay is inferred** from the 9 quoted requests; the code of the switch
  is out of reach.
- **No lens for load-saturation, third-party or data-db.** The low request volume in the
  counters is the only check on load.
- **Other product ids were not probed**, so the extent of the latent defect is unknown.
- **Schema check by hand.** No interpreter was available for an automated check of this
  journal.
