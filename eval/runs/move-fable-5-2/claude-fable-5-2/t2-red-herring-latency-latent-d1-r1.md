---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-wide-slowness
  trigger: "manual (/konan, human profile). Complaint object: source human; fingerprint human-1794753828; labels.alertname human-report; no severity stated; startsAt 2026-11-15T14:43:48Z. Investigation start 2026-11-15T14:43:54Z; trigger latency 6 s."
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-15T14:43:54Z
  concluded: 2026-11-15T14:51:50Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The chaos switch inside the target was turned on at 2026-11-15T14:43:31.413Z with extra latency of up to 1500 ms and a failure rate of 0; while it is on, it delays every request on the shop routes and leaves /health fast."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode) was turned on at 2026-11-15T14:43:31.413Z with extra latency of up to 1500 ms and a failure rate of 0; while it is on, it delays requests on the shop routes and not on /health. This is the cause of the reported slowness."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "The error page that some users saw comes from a defect in the target's own code: GET /products/3 raises ZeroDivisionError (division by units_in_stock, which is 0 for product 3) and returns HTTP 500."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E13, E14, E15, E16, E17]
    evidence_against: [E10, E18]
  - id: H3
    statement: "A process restart at 2026-11-15T14:43:25Z caused the slowness or the error page: requests failed while the process was down, or the process is slow after the start."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E11, E12]
    evidence_against: [E3, E12]
  - id: H4
    statement: "The switch of H1 also caused the reported error page by injecting error responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E1, E7, E10, E18]
latent_findings:
  - statement: "GET /products/3 fails on each attempt with HTTP 500 and ZeroDivisionError: the product detail code divides by units_in_stock, which is 0 for product 3. In the visible window only investigator probes triggered it; no user request reached product 3."
    evidence: [E13, E14, E15, E16, E17, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:43:31.413Z"
    quote: |-
      {"ts": "2026-11-15T14:43:31.413Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "c485007793b9", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:43:31.414Z"
    quote: |-
      {"ts": "2026-11-15T14:43:31.414Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "c485007793b9", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.622, "client": "127.0.0.1:53163"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:43:26.231Z to 14:43:28.353Z; all five non-investigator access lines before E1, each trimmed to four fields"
    quote: |-
      "ts": "2026-11-15T14:43:26.231Z" "message": "GET /health -> 200" "request_id": "935dc9b2ea9b" "duration_ms": 12.121
      "ts": "2026-11-15T14:43:26.253Z" "message": "GET /health -> 200" "request_id": "b07e78a5488c" "duration_ms": 0.74
      "ts": "2026-11-15T14:43:26.258Z" "message": "GET /products -> 200" "request_id": "9e4e4abf635b" "duration_ms": 1.14
      "ts": "2026-11-15T14:43:27.299Z" "message": "GET /products/1 -> 200" "request_id": "77b1f49331e6" "duration_ms": 0.566
      "ts": "2026-11-15T14:43:28.353Z" "message": "POST /orders -> 201" "request_id": "e705bf599765" "duration_ms": 1.939
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:43:34.819Z to 14:43:42.264Z; all five non-investigator access lines after E2 (log read to line 45), each trimmed to four fields"
    quote: |-
      "ts": "2026-11-15T14:43:34.819Z" "message": "GET /products -> 200" "request_id": "1f0b73c8bf3e" "duration_ms": 1347.179
      "ts": "2026-11-15T14:43:37.229Z" "message": "GET /products/2 -> 200" "request_id": "e6dd3a87599c" "duration_ms": 1348.37
      "ts": "2026-11-15T14:43:39.543Z" "message": "GET /products/1 -> 200" "request_id": "c3ba28a8df2a" "duration_ms": 1248.309
      "ts": "2026-11-15T14:43:41.044Z" "message": "POST /orders -> 201" "request_id": "667e705b1f89" "duration_ms": 436.119
      "ts": "2026-11-15T14:43:42.264Z" "message": "GET /orders -> 200" "request_id": "e604c0ddfceb" "duration_ms": 156.25
  - id: E5
    type: metric
    source: "/metrics @ 2026-11-15T14:44:01Z, request_id=konan-1794753841-2730"
    quote: "faultline_chaos_enabled 1"
  - id: E6
    type: metric
    source: "/metrics @ 2026-11-15T14:47:28Z, request_id=konan-1794754048-2977"
    quote: "faultline_chaos_enabled 1"
  - id: E7
    type: log
    source: "lab/logs/app.log, lines 1 to 45 (2026-11-15T14:43:25.512Z to 14:47:28.573Z); the only chaos event in the log is the line below, there is no chaos_disabled line and no chaos_failure line"
    quote: |-
      "ts": "2026-11-15T14:43:31.413Z" "logger": "faultline.chaos" "message": "chaos mode enabled" "event": "chaos_enabled"
  - id: E8
    type: probe
    source: "/health @ 2026-11-15T14:45:30Z, request_id=konan-1794753930-2852"
    quote: |-
      {"status":"ok","uptime_seconds":125.0341026247479}
      -- HTTP 200 in 0.001377s request_id=konan-1794753930-2852
  - id: E9
    type: probe
    source: "/products @ 2026-11-15T14:45:29Z, request_id=konan-1794753929-2846; trailer line"
    quote: "-- HTTP 200 in 0.636238s request_id=konan-1794753929-2846"
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-15T14:45:29Z, request_id=konan-1794753929-2840; the complete http_requests_total and http_exceptions_total sections, before any probe of product 3"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:43:25.513Z; the only startup event in the log, two lines after the first log line (14:43:25.512Z)"
    quote: |-
      {"ts": "2026-11-15T14:43:25.513Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E12
    type: metric
    source: "/metrics, three reads: 2026-11-15T14:44:01Z (konan-1794753841-2730), 14:45:29Z (konan-1794753929-2840), 14:47:28Z (konan-1794754048-2977)"
    quote: |-
      process_uptime_seconds 35.933983916882426
      process_max_rss_bytes 47972352
      process_uptime_seconds 123.80319237476215
      process_max_rss_bytes 48054272
      process_uptime_seconds 243.0761576667428
      process_max_rss_bytes 48054272
  - id: E13
    type: probe
    source: "/products/3 @ 2026-11-15T14:46:08Z, request_id=konan-1794753967-2894"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794753967-2894"}
      -- HTTP 500 in 1.195808s request_id=konan-1794753967-2894
  - id: E14
    type: probe
    source: "/products/3 @ 2026-11-15T14:46:14Z, second attempt, request_id=konan-1794753974-2910"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794753974-2910"}
      -- HTTP 500 in 0.069491s request_id=konan-1794753974-2910
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:46:08.336Z; the stack field is trimmed to its last frame at the [...] mark, with the checkout prefix of its file path redacted"
    quote: |-
      {"ts": "2026-11-15T14:46:08.336Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794753967-2894", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n [...] File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E16
    type: probe
    source: "/products @ 2026-11-15T14:45:29Z, request_id=konan-1794753929-2846; one object of the response body"
    quote: |-
      {"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}
  - id: E17
    type: probe
    source: "/products/1, /products/2, /products/4, /products/5 @ 2026-11-15T14:46:02Z to 14:46:11Z; trailer lines"
    quote: |-
      -- HTTP 200 in 0.831664s request_id=konan-1794753962-2874
      -- HTTP 200 in 0.016167s request_id=konan-1794753966-2889
      -- HTTP 200 in 1.045442s request_id=konan-1794753968-2899
      -- HTTP 200 in 1.488598s request_id=konan-1794753969-2904
  - id: E18
    type: metric
    source: "/metrics @ 2026-11-15T14:47:28Z, request_id=konan-1794754048-2977; every series with a status other than 200/201 and the complete http_exceptions_total section. The log has exactly two unhandled_exception lines, with request ids konan-1794753967-2894 and konan-1794753974-2910, and the 404 is the probe konan-1794753976-2920"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
gaps:
  - "Nothing before 2026-11-15T14:43:25.512Z is visible: the log starts there, there are no rotated backups, and the counters started at zero. The words 'the last few minutes' of the complaint reach back before that time, so slowness or an error page before the process start cannot be checked."
  - "The source of the reported error page was not found. No non-investigator request received a 4xx or 5xx in the visible window, and the complaint gives no URL, status, or time. A layer in front of the target (proxy, front end) is not part of the surface contract."
  - "Who or what turned the switch on is unknown. The telemetry shows only the request id c485007793b9 and a local client address. The operator surface is outside the probe allowlist, so the switch state was read only through the gauge and the log line."
  - "The write path was not probed (read-only rule). An order for product 3 or for product 4 (price null) is untested."
  - "Whether an earlier process existed, and why it stopped, cannot be read from the surface: no supervisor record, and the server output file is not in the surface list."
  - "The size of the delay rests on a small sample: five user requests and about ten investigator probes after the switch, 16 ms to 1489 ms."
usage:
  model: claude-fable-5-2
  tokens: 1861032
  wall_clock_seconds: 476
---

# Shop-wide slowness: the latency switch (chaos mode) is on since 14:43:31Z

## Summary

Root cause identified, with high confidence for the slowness. The chaos switch inside
faultline was turned on at 2026-11-15T14:43:31.413Z with `extra_latency_ms: 1500` and
`failure_rate: 0.0` (E1, E2). From the next user request on, every shop route answers in
156 ms to 1348 ms instead of about 1 ms (E3, E4). `/health` stays at about 1 ms (E8),
which is why the health checks are green and fast. The switch was still on at 14:47:28Z
(E6), and the log has no `chaos_disabled` line (E7). All users of the product and order
routes are affected; responses are slow, not wrong.

The error page is not explained. No user request received an error status in the visible
window (E10, E18), and the switch injects no errors (E1). One real defect exists:
`GET /products/3` fails on each attempt with a division by zero (E13 to E15). Only
investigator probes triggered it, so it is a latent finding, not the incident. The
visible window starts at the process start, 14:43:25.512Z; anything earlier is out of
reach.

## Timeline

- 14:43:25.512Z — the process starts; one `startup` event at 14:43:25.513Z (E11).
- 14:43:26Z to 14:43:28Z — five user requests, 0.566 ms to 12.121 ms, all 200/201 (E3).
- 14:43:31.413Z — **change marker**: `chaos mode enabled`, `failure_rate 0.0`,
  `extra_latency_ms 1500`, through `POST /chaos/enable` (E1, E2).
- 14:43:34.819Z — first slow request: `GET /products`, 1347.179 ms (E4).
- 14:43:37Z to 14:43:42Z — four more slow user requests, 156.25 ms to 1348.37 ms (E4).
- 14:43:48Z — the complaint is raised; 14:43:54Z — the investigation starts.
- 14:44:01Z — `faultline_chaos_enabled 1`; uptime 35.9 s (E5, E12).
- 14:45:29Z — investigator probe of `/products`: 200 in 0.636 s; `/health`: 200 in
  0.001 s (E9, E8). No error series in the metrics yet (E10).
- 14:46:08Z and 14:46:14Z — investigator probes of `/products/3`: 500,
  `ZeroDivisionError`, both times (E13, E14, E15).
- 14:47:28Z — the switch is still on; uptime 243 s with no reset (E6, E12).

## Investigation

Complaint object, as built by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794753828",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-15T14:43:48Z"
}
```

Investigation start: 2026-11-15T14:43:54Z (trigger latency 6 s). `KONAN_ADAPTER` was
unset, so the surface contract is `docs/lab.md`.

- **Baseline** (14:44:00Z): `/health` 200 in 2 ms; `/metrics` with only 200/201 series,
  no exception series, `faultline_chaos_enabled 1`, uptime 35.9 s; the log had 21 lines,
  with the `chaos_enabled` warning and the jump in durations after it.
- **Triage**: three lenses in parallel, blind to each other: infra-process, interfaces,
  software-defect. All three reported the same change marker (E1) and the same
  before/after durations (E3, E4). None found evidence of the error page.
- **Deep-dive**: one agent, on H2 (the error page as a code defect), through the
  software-defect lens. It probed each product id once, product 3 twice, two order ids,
  and one unknown id. It found the product 3 defect and no user impact from it. H1 had
  deterministic and complete evidence from triage and went to the judge with no
  deep-dive.
- **Judge**: H1 validated; H2 inconclusive (the defect is real, the link to users is
  unsupported); H3 invalidated for the slowness and inconclusive for the error page,
  recorded as inconclusive; H4 invalidated. The judge supported the latent-finding
  statement.
- **Round 2**: not run. The evidence that would settle H2 and H3 (the URL and time of
  the error page, a record from outside the process) is outside the surface contract.

Investigator traffic: the probes added two 500 responses, two `ZeroDivisionError`
counts, and one 404 to the target's counters (E18). These are not user errors. Token
totals were not captured for the session; the five subagents used about 198 000 tokens.

## Hypotheses

### H1 — the chaos switch adds latency (validated, root cause)

The marker (E1) sets up to 1500 ms of extra latency and a failure rate of 0. Its access
line (E2) shows the call that turned it on. Before the marker, shop requests took
0.566 ms to 1.939 ms (E3). After it, the same routes took 156.25 ms to 1348.37 ms (E4),
and an investigator probe of `/products` took 0.636 s (E9). The gauge reads 1 at
14:44:01Z and at 14:47:28Z (E5, E6), and no `chaos_disabled` line exists (E7). `/health`
stays at about 1 ms with the switch on (E8), which matches the complaint. The judge's
notes: the bound "up to 1500 ms" is read from the configuration and the spread of
durations, and the sample is small.

### H2 — the error page is a code defect on product 3 (inconclusive)

The defect is real and deterministic for one input: two probes of `/products/3`
returned 500 with `ZeroDivisionError` (E13, E14); the stack names the division by
`units_in_stock` (E15), which is 0 for product 3 (E16); the other four ids return 200
(E17). Against the link to users: before the investigator probes there was no 5xx series
and no exception series (E10), and afterwards both counts equal the two probes (E18). No
user request reached product 3 in the visible window (E3, E4). What would settle it: the
URL, status, and time of the error page that a user saw.

### H3 — a process restart caused the slowness or the error page (inconclusive)

The process started 23 seconds before the complaint (E11, E12). Against the slowness
part: requests right after the start were fast (E3), the slowness starts only after the
switch, uptime rises with no reset, and peak memory is flat (E12). The slowness part is
invalidated. The error-page part stays open: the target's log cannot record requests
that failed while no process was up. What would settle it: a record from outside the
process that shows an earlier instance and failed requests before 14:43:25.512Z.

### H4 — the switch also injected the error page (invalidated)

The switch has `error_status: 503` configured, but `failure_rate: 0.0` (E1). The log has
no `chaos_failure` line (E7), and the metrics show no 503 series before or after the
deep-dive (E10, E18).

## Safe next steps

- Tell the owner of the chaos switch that it is on since 14:43:31.413Z, with the request
  id `c485007793b9` (E1, E2), and ask who turned it on.
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` line; then compare
  the durations of the shop routes with E3.
- Ask the reporters for the URL and the time of the error page.
- Read the logs of any layer in front of the target for that time, if one exists.
- Give the product 3 finding (E13 to E16) to the owners of the product detail code for
  review.

## Gaps

- **Before the process start.** The log starts at 14:43:25.512Z with no rotated backups,
  and the counters started at zero. The complaint says "the last few minutes"; that
  period is mostly before the visible window.
- **The error page.** No user request received an error status in the visible window.
  The complaint gives no URL, status, or time, and a layer in front of the target is not
  in the surface contract.
- **The actor behind the switch.** Only the request id and a local client address are
  visible. The operator surface is outside the probe allowlist.
- **The write path.** `POST /orders` was not probed, so an order for product 3 or for
  product 4 (price null) is untested.
- **An earlier process.** No supervisor record is in the surface, and the server output
  file is not in the surface list.
- **Sample size.** The delay range rests on five user requests and about ten investigator
  probes after the switch.
