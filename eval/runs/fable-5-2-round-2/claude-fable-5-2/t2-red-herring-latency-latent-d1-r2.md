---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-slow-latency-switch
  trigger: "manual (/konan human report; fingerprint human-1794774157; startsAt 2026-11-15T20:22:37Z; investigation start 2026-11-15T20:22:50Z; trigger latency 13 s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-15T20:22:50Z
  concluded: 2026-11-15T20:30:27Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos switch inside the target was turned on at 2026-11-15T20:22:19.831Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on it adds a variable delay of up to about 1.5 s to every business route, and it leaves the health route fast."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target, turned on at 2026-11-15T20:22:19.831Z with extra_latency_ms 1500 and failure_rate 0.0 and still on, injects a variable delay into every business route (/products, /products/{id}, /orders); /health and /metrics are exempt. This is the cause of the slowness that users report."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E24, E25]
    evidence_against: [E17]
  - id: H2
    statement: "The target's own code raises an unhandled ZeroDivisionError on GET /products/3 (units_in_stock 0), and this defect is the active cause of the error page that users saw."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E19, E20, E21, E23]
    evidence_against: [E11, E13, E18, E24]
  - id: H3
    statement: "The chaos switch also injects error responses (status 503), and these are the error page that users saw."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E13, E18, E24]
  - id: H4
    statement: "Process lifecycle or resource pressure after startup (a restart, a crash loop, memory growth) causes the slowness."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3, E4, E12, E13, E18, E24]
latent_findings:
  - statement: "GET /products/3 fails with HTTP 500 on every call: the product detail code divides units_ordered by units_in_stock, and product 3 has units_in_stock 0 (ZeroDivisionError). Only investigator probes triggered it; no user request touched product 3 since the startup."
    evidence: [E19, E20, E21, E23, E24]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:13.912Z"
    quote: '{"ts": "2026-11-15T20:22:13.912Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:14.667Z"
    quote: '{"ts": "2026-11-15T20:22:14.667Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "f267fb6b3191", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.1, "client": "127.0.0.1:56326"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:15.721Z"
    quote: '{"ts": "2026-11-15T20:22:15.721Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "692129183d5d", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.022, "client": "127.0.0.1:56327"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:16.775Z"
    quote: '{"ts": "2026-11-15T20:22:16.775Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d7322906ec24", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.962, "client": "127.0.0.1:56328"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:19.831Z"
    quote: '{"ts": "2026-11-15T20:22:19.831Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "147ad5e27744", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:19.832Z"
    quote: '{"ts": "2026-11-15T20:22:19.832Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "147ad5e27744", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.67, "client": "127.0.0.1:56329"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:22.589Z"
    quote: '{"ts": "2026-11-15T20:22:22.589Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "136d83e6d799", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 703.36, "client": "127.0.0.1:56330"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:25.063Z"
    quote: '{"ts": "2026-11-15T20:22:25.063Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "967d341abbb1", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1413.02, "client": "127.0.0.1:56331"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:26.705Z"
    quote: '{"ts": "2026-11-15T20:22:26.705Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "fd7c4c764f60", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 575.891, "client": "127.0.0.1:56332"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:29.099Z"
    quote: '{"ts": "2026-11-15T20:22:29.099Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "ccb51818c60e", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1336.391, "client": "127.0.0.1:56333"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:31.291Z (the last line with a non-investigator request id; 42 lines read, to 20:25:35.440Z; no chaos_disabled and no chaos_failure event in them)"
    quote: '{"ts": "2026-11-15T20:22:31.291Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "d143e7e98756", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1131.738, "client": "127.0.0.1:56334"}'
  - id: E12
    type: probe
    source: "/health, request_id=konan-1794774176-23994 (logged 2026-11-15T20:22:56.928Z)"
    quote: |-
      {"status":"ok","uptime_seconds":43.02765054209158}
      -- HTTP 200 in 0.001619s request_id=konan-1794774176-23994
  - id: E13
    type: metric
    source: "/metrics scrape, request_id=konan-1794774177-23999 (logged 2026-11-15T20:22:57.238Z); the complete http_requests_total and http_exceptions_total blocks, then the gauges"
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
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 1
      process_uptime_seconds 43.33702833438292
      process_max_rss_bytes 47349760
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:23:53.429Z (investigator probe)"
    quote: '{"ts": "2026-11-15T20:23:53.429Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794774232-24078", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1103.075, "client": "127.0.0.1:56366"}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:23:54.198Z (investigator probe)"
    quote: '{"ts": "2026-11-15T20:23:54.198Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794774233-24083", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 681.993, "client": "127.0.0.1:56367"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:23:54.292Z (investigator probe)"
    quote: '{"ts": "2026-11-15T20:23:54.292Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794774234-24089", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.46, "client": "127.0.0.1:56368"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:24:02.269Z (investigator probe)"
    quote: '{"ts": "2026-11-15T20:24:02.269Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794774242-24108", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 39.305, "client": "127.0.0.1:56372"}'
  - id: E18
    type: metric
    source: "/metrics scrape, request_id=konan-1794774306-24166 (logged 2026-11-15T20:25:06.941Z), before any probe of product 3 or 4; lines trimmed to the relevant series"
    quote: |-
      http_requests_total{method="GET",path="/products",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      faultline_chaos_enabled 1
      process_uptime_seconds 173.04324566712603
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:25:18.895Z (investigator probe; the first ERROR line in the log; stack trimmed to its last frame; the local path prefix of the target's checkout is redacted to <checkout>)"
    quote: '{"ts": "2026-11-15T20:25:18.895Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794774318-24182", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:25:18.911Z (investigator probe; the first non-2xx access line in the log)"
    quote: '{"ts": "2026-11-15T20:25:18.911Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794774318-24182", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 105.765, "client": "127.0.0.1:56386"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:25:26.471Z (investigator probe)"
    quote: '{"ts": "2026-11-15T20:25:26.471Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794774325-24194", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 925.885, "client": "127.0.0.1:56388"}'
  - id: E22
    type: probe
    source: "/products/4, request_id=konan-1794774321-24187 (logged 2026-11-15T20:25:21.975Z)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.182061s request_id=konan-1794774321-24187
  - id: E23
    type: probe
    source: "/products, request_id=konan-1794774330-24201 (logged 2026-11-15T20:25:31.499Z)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.824665s request_id=konan-1794774330-24201
  - id: E24
    type: metric
    source: "/metrics scrape, request_id=konan-1794774373-24216 (about 2026-11-15T20:26:13Z), the latest scrape; lines trimmed to the relevant series; no other non-2xx series in the scrape"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
      faultline_chaos_enabled 1
      process_uptime_seconds 239.1931290421635
      process_max_rss_bytes 47349760
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:22:57.238Z (investigator probe)"
    quote: '{"ts": "2026-11-15T20:22:57.238Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1794774177-23999", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.558, "client": "127.0.0.1:56355"}'
gaps:
  - "The 'error page once' in the complaint has no support in the telemetry: no non-investigator request returned a non-2xx status since the startup at 2026-11-15T20:22:13.912Z, and the switch has failure_rate 0.0."
  - "No telemetry exists from before 2026-11-15T20:22:13.912Z: one log file, no rotated backups, counters from zero. The complaint says 'the last few minutes', and the process was 24 s old at the complaint time; what happened before the startup, and why the process started then, is out of reach."
  - "An error page made on the client side or by a tier in front of the target (for example a timeout under the added delay) is not visible on this surface."
  - "Who or what sent POST /chaos/enable is unknown: the log gives a request id and a local client address only, and the chaos status surface is operator surface, outside the probe allowlist."
  - "User traffic after the switch covers 12 s and 5 requests (20:22:22Z to 20:22:31Z); the proof that the slowness continues after that comes from investigator probes only."
  - "The shape of the delay (variable, up to extra_latency_ms) is an inference from 12 samples between 39 ms and 1413 ms, not a reading of the switch's code or configuration."
  - "Order creation for product 4 (price null) is untested: the probe surface is GET-only."
  - "Lenses exist for three classes only (infra-process, interfaces, software-defect). Load, third-party and data-layer causes had no lens; the baseline shows 11 requests in 43 s and flat peak memory, and the lab has no database and no third party."
  - "The investigator's own probes of /products/3 left 2 status-500 counts and 2 ZeroDivisionError counts in the target's counters; they are not user impact."
  - "The journal's machine core was not run through the schema validator in this session."
usage:
  model: claude-fable-5-2
  tokens: 2006182
  wall_clock_seconds: 457
---

# Shop-wide slowness from an injected-latency chaos switch

## Summary

**Root cause identified (infra-process, degradation-switch).** At 2026-11-15T20:22:19.831Z
a non-investigator request to `POST /chaos/enable` turned on the target's chaos switch
with `extra_latency_ms` 1500 and `failure_rate` 0.0 (E5, E6). Before the marker, business
requests took 1–2 ms (E2–E4). After it, every business request took between 39 ms and
1413 ms, on all business routes and independent of the input (E7–E11, E14, E15, E17).
The health route stayed at about 0.5 ms (E12, E16), which is why the health checks are
green and fast. The switch was still on at the latest scrape (`faultline_chaos_enabled 1`,
E24) and the log has no `chaos_disabled` event. Confidence is high for the slowness.

The "error page once" is **not explained**: no user request returned a non-2xx status
since the process started at 20:22:13.912Z, and the switch injects no errors as
configured. One latent defect was found on the way (`GET /products/3` returns 500, a
division by zero), but only investigator probes triggered it.

### Complaint block

```json
{
  "source": "human",
  "fingerprint": "human-1794774157",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-15T20:22:37Z"
}
```

Investigation start: 2026-11-15T20:22:50Z (trigger latency 13 s).

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 20:22:13.912 | Process startup, faultline 0.1.0. No telemetry before this point. | E1 |
| 20:22:14–20:22:16 | Business requests take 1–2 ms. | E2, E3, E4 |
| 20:22:19.831 | **Change marker:** chaos mode enabled, `failure_rate` 0.0, `error_status` 503, `extra_latency_ms` 1500, by `POST /chaos/enable` (request id `147ad5e27744`, not an investigator id). | E5, E6 |
| 20:22:22–20:22:31 | User requests on `/products`, `/products/{id}`, `POST /orders`, `/orders` take 576–1413 ms, all 2xx. Last user request in the log. | E7–E11 |
| 20:22:37 | Complaint raised. | complaint block |
| 20:22:50 | Investigation starts. | — |
| 20:22:56–20:22:57 | Baseline: `/health` 200 in 1.6 ms; metrics all 2xx, no exception series, chaos gauge 1, uptime 43 s. | E12, E13, E25 |
| 20:23:53–20:24:02 | Investigator probes: `/products` 1103 ms, `/orders` 682 ms, `/health` 0.46 ms, `/products/2` 39 ms. | E14–E17 |
| 20:25:06 | Scrape before the edge-input probes: still no exception series, no non-2xx series. | E18 |
| 20:25:18, 20:25:26 | Investigator probes of `/products/3` return 500 (ZeroDivisionError), twice. `/products/4` returns 200. | E19–E22 |
| ~20:26:13 | Latest scrape: chaos gauge still 1; the two 500s and two exceptions equal the two investigator probes; peak memory unchanged. | E24 |

## Investigation

- **Setup.** `KONAN_ADAPTER` unset, so the surface contract is `docs/lab.md`. Budget: one
  triage round, at most 3 deep-dives per round, at most 2 rounds. Used: one triage round,
  one deep-dive, one judge round.
- **Baseline.** `/health`, `/metrics`, and the full log (22 lines at that time). The
  baseline already showed the change marker (E5) between the fast and the slow requests.
- **Triage.** Three lenses in parallel, blind to each other: infra-process, interfaces,
  software-defect. All three reported the same marker and the same before/after step.
  Infra-process ruled out restart and resource pressure. Interfaces found no boundary
  failure and assigned the mechanism to infra-process. Software-defect found no exception
  and no non-2xx, and named two untested edge inputs (product 3 with stock 0, product 4
  with price null).
- **Deep-dive.** One agent, software-defect lens, on H2 (edge inputs as the source of the
  error page). It scraped metrics first (E18), then probed: `/products/3` fails with 500
  twice, `/products/4` and the list route return 200. H1 skipped the deep-dive because its
  triage evidence was already complete.
- **Judge.** One fresh agent with the hypotheses and the verbatim evidence only. Verdicts:
  H1 validated, H2 invalidated as stated (the defect is real, the user impact is not),
  H3 invalidated, H4 invalidated. The judge removed E5 as support for H3 and E1/E12 as
  support for H4; the machine core follows that.

## Hypotheses

### H1 — chaos switch injects latency on every business route — validated

The step is sharp: 1–2 ms before the marker (E2–E4), 576–1413 ms for the five user
requests after it (E7–E11), and the same on investigator probes minutes later (E14, E15).
The same input is fast before and slow after (`/products/1`: E3 against E9), so the delay
does not depend on the data. Every sample is below the configured 1500 ms (E5). The health
and metrics routes are not delayed (E12, E16, E25). The gauge reads 1 at the baseline and
at the latest scrape (E13, E24). One sample is short (39 ms, E17); the judge held that it
is still about 40 times the pre-marker value and fits a variable delay. The "variable"
shape is an inference from samples.

### H2 — division by zero on product 3 is the users' error page — invalidated

The defect exists and is deterministic: `GET /products/3` returns 500 twice, with
`ZeroDivisionError` at `shop.py` line 64 (E19–E21); product 3 has `units_in_stock` 0 (E23).
But no user request touched product 3: the exception series and the 500 series did not
exist after the last user request (E13) or just before the probes (E18), and their final
counts of 2 equal the two investigator probes (E24). It is recorded as a latent finding.
One non-investigator 500 on `/products/3` would reverse this; it could only be in a record
from before the startup.

### H3 — chaos switch injects 503 errors — invalidated

The switch has `failure_rate` 0.0 (E5). There is no `chaos_failure` event in the log and no
503 series in any scrape (E13, E18, E24). The configured `error_status` 503 shows a
capability only.

### H4 — restart or resource pressure — invalidated

One startup event (E1); every uptime reading resolves to that one start (E12, E13, E18,
E24). Peak memory is identical at the baseline and at the latest scrape (E13, E24).
Requests right after the startup were fast (E2–E4). Why the process started at 20:22:13 is
not answered by the telemetry.

## Safe next steps

Read-only suggestions only.

- Ask the operator who sent `POST /chaos/enable` at 20:22:19.831Z (request id
  `147ad5e27744`), and whether the switch is intended to be on.
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` event; compare
  business `duration_ms` before and after it.
- Ask the reporters for the time, the page, and the text of the error page. Compare with
  the access log by time; look in client-side or front-tier logs for timeouts.
- Look for any record from before 20:22:13.912Z (an earlier log, a supervisor record) to
  learn why the process started then.
- Record the `/products/3` division by zero for the target's owners as a separate defect.

## Gaps

- **Error page.** No support in the telemetry since the startup; the switch injects no
  errors as configured. Not explained.
- **Before the startup.** One log file, no backups, counters from zero. The complaint's
  "last few minutes" reaches back past the 20:22:13.912Z startup.
- **Client side and front tiers.** A timeout page made outside the target is not visible
  here.
- **Origin of the switch change.** Request id and local client address only; the chaos
  status surface is outside the probe allowlist.
- **Short user window.** 5 user requests in 12 s after the switch; later samples are
  investigator probes.
- **Delay shape.** Inferred from 12 samples, not read from the switch.
- **Order creation with product 4.** POST is outside the probe surface.
- **Lens coverage.** Three lens files exist; load, third-party and data-layer causes had
  no lens. The baseline shows low volume and flat memory, and the lab has no database or
  third party.
- **Investigator footprint.** 2 status-500 counts and 2 ZeroDivisionError counts in the
  target's counters come from this investigation.
- **Schema check.** The machine core was not run through the validator in this session.
