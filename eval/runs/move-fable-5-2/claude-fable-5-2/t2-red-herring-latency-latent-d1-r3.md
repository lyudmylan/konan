---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-slowness-latency-switch
  trigger: "manual (/konan, human profile); fingerprint human-1794754715; alertname human-report; no severity stated; startsAt 2026-11-15T14:58:35Z; investigation start 2026-11-15T14:58:47Z; trigger latency 12 s"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-15T14:58:47Z
  concluded: 2026-11-15T15:02:58Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The chaos switch inside the target was turned on at 2026-11-15T14:58:19.701Z with extra_latency_ms 1500 and failure_rate 0.0; while on, it adds a variable delay of up to about 1.5 s to every shop route and leaves /health fast."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode) was turned on at 2026-11-15T14:58:19.701Z with extra_latency_ms 1500 and failure_rate 0.0; while on, it adds a variable delay of up to about 1500 ms to the shop routes (/products, /products/{id}, /orders) and not to /health. This is the slowness that users report, and it is still active."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E14, E20]
    evidence_against: [E13]
  - id: H2
    statement: "The target's own code raised an unhandled exception for some user input since the process start, and that is the error page some users saw."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E16, E19]
  - id: H3
    statement: "The process crashed or restarted, and the error page (or the slowness) comes from that lifecycle event."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E17, E11]
    evidence_against: [E17, E18, E19, E2, E3, E4]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:19.701Z"
    quote: '{"ts": "2026-11-15T14:58:19.701Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "4b91d94bcf1e", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:14.545Z"
    quote: '{"ts": "2026-11-15T14:58:14.545Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "f69c84d56110", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.108, "client": "127.0.0.1:53303"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:15.602Z"
    quote: '{"ts": "2026-11-15T14:58:15.602Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "998ec65a29d6", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.004, "client": "127.0.0.1:53304"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:16.644Z"
    quote: '{"ts": "2026-11-15T14:58:16.644Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "2eb1bfd70c18", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.996, "client": "127.0.0.1:53305"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:22.678Z"
    quote: '{"ts": "2026-11-15T14:58:22.678Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "78cdc15d0907", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 918.274, "client": "127.0.0.1:53307"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:23.931Z"
    quote: '{"ts": "2026-11-15T14:58:23.931Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b079e29dc550", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 184.912, "client": "127.0.0.1:53308"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:25.890Z"
    quote: '{"ts": "2026-11-15T14:58:25.890Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "5ec7a0f7c788", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 891.883, "client": "127.0.0.1:53309"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:28.349Z"
    quote: '{"ts": "2026-11-15T14:58:28.349Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "7fc2b0cfc6df", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1391.961, "client": "127.0.0.1:53310"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:30.712Z"
    quote: '{"ts": "2026-11-15T14:58:30.712Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "23ecdaf84ec7", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1298.288, "client": "127.0.0.1:53311"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:52.647Z"
    quote: '{"ts": "2026-11-15T14:58:52.647Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794754732-3463", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.692, "client": "127.0.0.1:53330"}'
  - id: E11
    type: probe
    source: "/health, request_id konan-1794754732-3463"
    quote: |-
      {"status":"ok","uptime_seconds":38.890178540721536}
      -- HTTP 200 in 0.002425s request_id=konan-1794754732-3463
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:59:42.588Z"
    quote: '{"ts": "2026-11-15T14:59:42.588Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794754781-3531", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1308.01, "client": "127.0.0.1:53341"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:59.786Z"
    quote: '{"ts": "2026-11-15T14:58:59.786Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794754739-3478", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 67.88, "client": "127.0.0.1:53333"}'
  - id: E14
    type: metric
    source: "/metrics, request_id konan-1794754818-3552 (about 2026-11-15T15:00:18Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E15
    type: metric
    source: "/metrics, request_id konan-1794754818-3552 (about 2026-11-15T15:00:18Z); the complete http_requests_total family"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E16
    type: metric
    source: "/metrics, request_id konan-1794754818-3552 (about 2026-11-15T15:00:18Z); the complete http_exceptions_total family, no series"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:58:13.767Z (the only startup event in the file)"
    quote: '{"ts": "2026-11-15T14:58:13.767Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E18
    type: metric
    source: "/metrics, request_id konan-1794754732-3468 (about 14:58:52Z), then request_id konan-1794754818-3552 (about 15:00:18Z)"
    quote: |-
      process_uptime_seconds 39.11248766584322
      process_max_rss_bytes 47464448
      process_uptime_seconds 124.26431470783427
      process_max_rss_bytes 47513600
  - id: E19
    type: log
    source: "lab/logs/app.log, scan of the whole file (28 lines, no backup files) from 2026-11-15T14:58:13.767Z to the quoted last line @ 2026-11-15T14:59:49.280Z: every status value is 200 or 201; no event unhandled_exception, chaos_failure, simulated_exception or chaos_disabled; no stack field; one WARNING (E1), no ERROR"
    quote: '{"ts": "2026-11-15T14:59:49.280Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1794754789-3544", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.51, "client": "127.0.0.1:53345"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:59:41.193Z"
    quote: '{"ts": "2026-11-15T14:59:41.193Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794754780-3525", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 613.336, "client": "127.0.0.1:53340"}'
gaps:
  - "The error page that some users report has no trace: no telemetry exists from before the process start at 2026-11-15T14:58:13.767Z (one log file, no backups, counters start at zero), and the report says 'the last few minutes'."
  - "Whether the process start at 14:58:13.767Z was a restart of an earlier instance cannot be read from the surface contract; a supervisor or platform record is outside it. A refused connection during a restart never reaches the application log."
  - "Who turned the switch on, and why, is not visible: the log shows only the request POST /chaos/enable from 127.0.0.1 with request_id 4b91d94bcf1e. The switch surface is operator surface and was not probed."
  - "The post-switch sample is small: 5 non-investigator shop requests and 3 investigator probes. The exact delay distribution and the exemption of /health are read from behaviour, not from a statement of what the switch does."
  - "Token totals were not captured (interactive session)."
usage:
  model: claude-fable-5-2
  tokens: 1160218
  wall_clock_seconds: 251
---

# Shop-wide slowness from the chaos latency switch; error page not corroborated

## Summary

**Verdict: root cause identified (infra-process, degradation-switch).** The chaos
switch inside the target was turned on at 2026-11-15T14:58:19.701Z with
`extra_latency_ms: 1500` and `failure_rate: 0.0` (E1). From that moment every shop
route (`/products`, `/products/{id}`, `GET /orders`, `POST /orders`) went from about
1 ms (E2, E3, E4) to between 68 ms and 1392 ms per request (E5–E9, E12, E13, E20).
`/health` stayed under 1 ms (E10, E11), which is why the health checks are green and
fast. The switch was still on at the last scrape (E14) and no `chaos_disabled` event
exists (E19). Impact: all 5 non-investigator shop requests after the switch were
slow (185–1392 ms); none failed. Confidence in the slowness cause: high — the
judge validated it.

The **error page is not corroborated**. Since the process start at 14:58:13.767Z
there is no 5xx response (E15), no unhandled exception (E16), and no error line in
the log (E19); the switch injects no failures (`failure_rate: 0.0`, E1). The process
was only about 39 s old at the first probe (E11), so an error page from before that
start is out of reach (see Gaps).

## Timeline

- **14:58:13.767Z** — process start, `faultline 0.1.0 started`; the only startup
  event in the log (E17).
- **14:58:14.545Z – 14:58:16.644Z** — shop requests take about 1 ms (E2, E3, E4).
- **14:58:19.701Z** — **flag-change marker**: `chaos mode enabled`, `failure_rate 0.0`,
  `error_status 503`, `extra_latency_ms 1500`, by a non-investigator request (E1).
- **14:58:22.678Z** — first slow shop request, `GET /products` 918.274 ms (E5).
- **14:58:23.931Z – 14:58:30.712Z** — every further user request is slow:
  184.912 ms, 891.883 ms, 1391.961 ms, 1298.288 ms (E6, E7, E8, E9).
- **14:58:35Z** — complaint raised; **14:58:47Z** — investigation start.
- **14:58:52.647Z** — `/health` probe answers in 0.692 ms with the switch on (E10, E11).
- **14:58:59.786Z – 14:59:42.588Z** — investigator probes of shop routes are slow
  as well: 67.88 ms, 613.336 ms, 1308.01 ms (E13, E20, E12).
- **about 15:00:18Z** — `faultline_chaos_enabled 1`; uptime 124.26 s, no reset;
  request counters hold only 200 and 201 (E14, E18, E15).

## Investigation

- **Complaint.** The complaint object, as the `/konan` adapter synthesized it:

  ```json
  {
    "source": "human",
    "fingerprint": "human-1794754715",
    "labels": { "alertname": "human-report" },
    "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
    "startsAt": "2026-11-15T14:58:35Z"
  }
  ```

  Investigation start: 2026-11-15T14:58:47Z (trigger latency 12 s).
- **Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.
  Budget: one triage round, at most 3 deep-dives per round, at most 2 rounds.
- **Baseline.** `/health` 200 in 2.4 ms (E11); the first `/metrics` scrape showed
  only 2xx series, an empty exception family, `faultline_chaos_enabled 1`, uptime
  39.11 s (E18); `/products` 200 in 69 ms (E13); the log showed the startup, a
  ~1 ms period, the `chaos_enabled` warning, then slow shop requests.
- **Triage.** Three lenses ran in parallel, blind to each other: infra-process,
  software-defect, interfaces. All three pointed at the same marker (E1) and the
  latency step after it. The software-defect lens found no anomaly in its domain.
  The interfaces lens found none in its domain and classed the switch as
  infra-process. No lens found evidence of the error page.
- **Deep-dive.** None. The triage evidence for H1 was deterministic and complete
  (marker, before/after durations on the same routes, live gauge, live probes), so
  H1 went straight to the judge. The decisive checks for H2 and H3 (status
  counters, exception family, startup events, uptime) were already in hand.
- **Judge.** A fresh judge saw only the hypotheses and the verbatim evidence.
  H1 validated; H2 invalidated; H3 inconclusive on a narrow remainder (whether the
  14:58:13 start was itself a restart). The settling evidence for H3 is a
  supervisor record, which is outside the surface contract, so no second round ran.

## Hypotheses

### H1 — the chaos switch adds latency to the shop routes — validated

The marker E1 carries the parameters: latency 1500 ms, failure rate 0.0. Before it,
`/products`, `/products/1` and `POST /orders` took about 1 ms (E2, E3, E4). After it,
the same routes took 918.274 ms, 891.883 ms and 1391.961 ms (E5, E7, E8), and
`/products/2` and `GET /orders` were slow too (E6, E9). The first slow request came
3 s after the marker. Investigator probes later show the same (E12, E20). All delays
stay under 1500 ms. `/health` stays under 1 ms with the switch on (E10, E11), which
matches the complaint. The gauge still reads 1 (E14).

Against: one shop request after the marker took only 67.88 ms (E13). The judge held
that this fits a variable delay — it is still about 60 times the pre-switch value
for the same route (E2) — and does not refute the hypothesis.

Limits the judge set: the validated scope is the slowness from 14:58:19.701Z on;
"variable" and "not /health" are read from behaviour.

### H2 — an unhandled exception in the target's own code produced the error page — invalidated

All three predictions fail on independent sources: the complete request counter
family has only 200 and 201 series (E15); the exception family has no series (E16);
the whole log has no error status, no `unhandled_exception` event and no `stack`
field (E19). The scope is "since the process start"; the log covers exactly that
window.

### H3 — a crash or restart produced the error page or the slowness — inconclusive

For: the process started at 14:58:13.767Z (E17), only 6 s before the switch, and was
38.89 s old at the first probe (E11), while the report speaks of "the last few
minutes". Against: there is one startup event only (E17); uptime rises from 39.11 s
to 124.26 s without a reset and memory is flat (E18); shop requests were fast right
after the start (E2, E3, E4), so the slowness does not come from the start. Open:
whether an earlier instance ran and stopped before 14:58:13.767Z. The surface cannot
answer that.

## Safe next steps

Read-only suggestions only:

- Read the state of the chaos switch on the operator side and identify who sent
  `POST /chaos/enable` at 14:58:19.701Z (request_id `4b91d94bcf1e`, client
  127.0.0.1).
- Watch `faultline_chaos_enabled` and the shop route durations in `/metrics`; the
  prediction is that durations return to about 1 ms when the gauge reads 0.
- Read the supervisor or platform record for the process start at 14:58:13.767Z, to
  learn whether an earlier instance stopped before it (settles H3 and may explain
  the error page).
- Ask the reporters for the time and the page of the error they saw, and compare
  with the log window.

## Gaps

- **The error page has no trace.** Telemetry starts at the process start
  (14:58:13.767Z): one log file, no backups, counters from zero. An error before
  that time is not visible, and the report says "the last few minutes".
- **Restart question.** Whether the 14:58:13.767Z start replaced an earlier instance
  needs a supervisor or platform record, which is outside `docs/lab.md`. A refused
  connection during a restart never reaches the application log.
- **Who and why.** The log shows only that a non-investigator request from
  127.0.0.1 turned the switch on. The switch surface is operator surface and was
  not probed.
- **Small sample.** 5 non-investigator shop requests and 3 investigator probes after
  the switch. The delay distribution and the `/health` exemption are read from
  behaviour.
- **Usage.** Token totals were not captured in this interactive session.
