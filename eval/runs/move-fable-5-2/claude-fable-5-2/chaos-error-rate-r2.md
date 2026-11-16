---
konan_journal: 2
investigation:
  id: 2026-11-15-intermittent-503s
  trigger: 'manual — /konan human profile. Complaint object: {"source": "human", "fingerprint": "human-1794745553", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."}, "startsAt": "2026-11-15T12:25:53Z"}. Investigation start 2026-11-15T12:26:06Z; trigger latency 13 s.'
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-15T12:26:06Z
  concluded: 2026-11-15T12:32:07Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational switch inside the target (chaos mode) was turned on at 2026-11-15T12:25:36.289Z with failure_rate 0.4 and error_status 503; while it is on, the target answers a random share of business requests with an injected 503, and the health endpoint keeps answering 200."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode) was turned on at 12:25:36.289Z with failure_rate 0.4 and error_status 503. While it is on, the target answers a random share of business requests (product pages, the order list) with an injected 503, and the health endpoint still answers 200. This is the cause of the intermittent user-facing failures."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E17, E18, E19, E20, E21, E22, E23, E24]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled error on specific inputs (specific product ids or the order list), and those inputs fail every time."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E4, E6, E7]
    evidence_against: [E3, E5, E11, E13, E19, E20, E21, E22, E24]
  - id: H3
    statement: "The process crashes or restarts repeatedly, and requests that land in a restart window fail."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E14, E15]
    evidence_against: [E4, E5, E6, E7, E16, E17, E24]
  - id: H4
    statement: "A proxy or gateway tier in front of the target fails on its own and returns the 503 responses."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E8]
    evidence_against: [E3, E4, E5, E6, E7, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:36.289Z"
    quote: '{"ts": "2026-11-15T12:25:36.289Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "299cbf686b5d", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:36.290Z"
    quote: '{"ts": "2026-11-15T12:25:36.290Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "299cbf686b5d", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.964, "client": "127.0.0.1:51623"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:43.606Z"
    quote: '{"ts": "2026-11-15T12:25:43.606Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "43b475eaf52e", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:43.607Z"
    quote: '{"ts": "2026-11-15T12:25:43.607Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "43b475eaf52e", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 1.047, "client": "127.0.0.1:51630"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:45.716Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T12:25:45.716Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e2188b3a50b6", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T12:25:45.716Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "e2188b3a50b6", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.267, "client": "127.0.0.1:51632"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:46.771Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T12:25:46.771Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "4df6efbea459", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-15T12:25:46.771Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "4df6efbea459", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.308, "client": "127.0.0.1:51633"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:47.823Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T12:25:47.823Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5e11d799875f", "event": "chaos_failure", "method": "GET", "path": "/products/4"}
      {"ts": "2026-11-15T12:25:47.823Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 503", "request_id": "5e11d799875f", "event": "request", "method": "GET", "path": "/products/4", "status": 503, "duration_ms": 0.278, "client": "127.0.0.1:51634"}
  - id: E8
    type: metric
    source: "/metrics @ 2026-11-15T12:26:10Z, request_id konan-1794745570-94704 (the complete http_requests_total family)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/4",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 3
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-15T12:26:10Z, request_id konan-1794745570-94704"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-15T12:27:23Z, request_id konan-1794745643-94801"
    quote: "faultline_chaos_enabled 1"
  - id: E11
    type: metric
    source: "/metrics @ 2026-11-15T12:27:23Z, request_id konan-1794745643-94801 (the exceptions family: header lines only, no sample line follows)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E12
    type: probe
    source: "/health, request_id konan-1794745569-94699, 2026-11-15T12:26:09Z"
    quote: |-
      {"status":"ok","uptime_seconds":41.26611004117876}
      -- HTTP 200 in 0.001605s request_id=konan-1794745569-94699
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:39.400Z"
    quote: '{"ts": "2026-11-15T12:25:39.400Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "bd33044e8cf7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.872, "client": "127.0.0.1:51626"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:28.329Z (the only startup event; the log has no backup files)"
    quote: '{"ts": "2026-11-15T12:25:28.329Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-15T12:26:10Z, request_id konan-1794745570-94704"
    quote: |-
      process_uptime_seconds 41.835169916041195
      process_max_rss_bytes 47300608
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-15T12:27:23Z, request_id konan-1794745643-94801"
    quote: |-
      process_uptime_seconds 115.30580812506378
      process_max_rss_bytes 47300608
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:29.039Z–12:25:33.237Z (every access line between the startup event and the switch line)"
    quote: |-
      {"ts": "2026-11-15T12:25:29.039Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "82de9198ca88", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 11.568, "client": "127.0.0.1:51617"}
      {"ts": "2026-11-15T12:25:29.068Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e18d8f97a55f", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.707, "client": "127.0.0.1:51618"}
      {"ts": "2026-11-15T12:25:29.068Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "8d6691e4671b", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 2.055, "client": "127.0.0.1:51619"}
      {"ts": "2026-11-15T12:25:30.121Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "cbe652251e49", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.063, "client": "127.0.0.1:51620"}
      {"ts": "2026-11-15T12:25:31.177Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "fabeec3aeeca", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.738, "client": "127.0.0.1:51621"}
      {"ts": "2026-11-15T12:25:33.237Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "51464cb2c204", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.723, "client": "127.0.0.1:51622"}
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:25:38.342Z–12:25:44.663Z (every successful non-investigator access line after the switch line; with the four 503 lines of E4–E7 this is all ten non-investigator requests after the switch, and the log holds none after 12:25:47.823Z)"
    quote: |-
      {"ts": "2026-11-15T12:25:38.342Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "26aeb31bb3b0", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.766, "client": "127.0.0.1:51625"}
      {"ts": "2026-11-15T12:25:39.400Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "bd33044e8cf7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.872, "client": "127.0.0.1:51626"}
      {"ts": "2026-11-15T12:25:40.450Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "c0fb588f29f3", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.735, "client": "127.0.0.1:51627"}
      {"ts": "2026-11-15T12:25:41.499Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "47d41ace9a43", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.212, "client": "127.0.0.1:51628"}
      {"ts": "2026-11-15T12:25:42.552Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "b65f4843af51", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.771, "client": "127.0.0.1:51629"}
      {"ts": "2026-11-15T12:25:44.663Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d6eac378a901", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.527, "client": "127.0.0.1:51631"}
  - id: E19
    type: probe
    source: "/products/1, request_id konan-1794745613-94781, 2026-11-15T12:26:53.945Z (investigator probe by the interfaces lens, after three investigator probes of the same path returned 200); response body, then its two lines in lab/logs/app.log"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1794745613-94781"}
      {"ts": "2026-11-15T12:26:53.945Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794745613-94781", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T12:26:53.945Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "konan-1794745613-94781", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.161, "client": "127.0.0.1:51665"}
  - id: E20
    type: probe
    source: "/products/5, request_id konan-1794745618-94791, 2026-11-15T12:26:58.795Z (investigator probe by the software-defect lens); response body, then its line in lab/logs/app.log"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      {"ts": "2026-11-15T12:26:58.795Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "konan-1794745618-94791", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.638, "client": "127.0.0.1:51667"}
  - id: E21
    type: probe
    source: "/products/4, request_id konan-1794745791-94825, 2026-11-15T12:29:51.907Z"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.008113s request_id=konan-1794745791-94825
  - id: E22
    type: probe
    source: "/orders, request_id konan-1794745792-94830, 2026-11-15T12:29:52.478Z"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T12:25:31.176+00:00"},{"id":2,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T12:25:41.498+00:00"},{"id":3,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T12:25:44.663+00:00"}]
      -- HTTP 200 in 0.001691s request_id=konan-1794745792-94830
  - id: E23
    type: probe
    source: "/health, three probes, request_ids konan-1794745792-94835, konan-1794745793-94840, konan-1794745793-94845, 2026-11-15T12:29:52Z–12:29:53Z"
    quote: |-
      {"status":"ok","uptime_seconds":264.6445864578709}
      -- HTTP 200 in 0.001400s request_id=konan-1794745792-94835
      {"status":"ok","uptime_seconds":265.2162107080221}
      -- HTTP 200 in 0.001327s request_id=konan-1794745793-94840
      {"status":"ok","uptime_seconds":265.67400858318433}
      -- HTTP 200 in 0.001407s request_id=konan-1794745793-94845
  - id: E24
    type: metric
    source: "/metrics @ 2026-11-15T12:30:00Z, request_id konan-1794745800-94850 (selected lines; the exceptions family has header lines only)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 7
      http_requests_total{method="GET",path="/metrics",status="200"} 5
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 2
      http_requests_total{method="GET",path="/products/4",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 9
      http_requests_total{method="POST",path="/orders",status="201"} 3
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 1
      process_uptime_seconds 271.86182816606015
      process_max_rss_bytes 47300608
gaps:
  - "No telemetry exists before the process start at 2026-11-15T12:25:28.329Z: the log starts there and has no backup files. The complaint says 'a few minutes ago'; the telemetry shows the first failure 10 s before the complaint was raised. Failures before 12:25:28, and the reason the process started then, are out of reach."
  - "Who or what turned the switch on is unknown. The enabling request has a non-investigator request id and a loopback client address; the log carries no identity."
  - "The switch's own state endpoint is operator surface, outside the contract. The switch state comes from the gauge and the one chaos_enabled log line only; the current failure rate is the rate of that line."
  - "No failed order creation was observed: POST /orders returned 201 three times of three, two of them after the switch. Probes are GET-only, so order creation could not be tested. 'Orders error out' is confirmed for the order list (GET /orders) only."
  - "The sample is small: ten non-investigator requests after the switch, four failed. Non-investigator traffic stops in the log at 12:25:47.823Z, so the user impact after that time was not measured; later failures are investigator probes."
  - "That the health and metrics endpoints are exempt from the injection is an inference from 5 of 5 health answers and 5 of 5 metrics answers with status 200 after the switch; the list of exempt paths could not be read."
  - "No tier in front of the target is visible on this surface. A client-side or front-tier error count could not be compared with the application's count."
  - "Token totals were not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1521529
  wall_clock_seconds: 361
---

# Intermittent 503s on shop pages: an error-injection switch inside the service is on

## Summary

**Verdict: root cause identified.** An operational switch inside the target (chaos
mode) was turned on at 2026-11-15T12:25:36.289Z with `failure_rate` 0.4 and
`error_status` 503 (E1, E2). From that moment the service answers a random share of
business requests with an injected 503. Each of the four user-facing failures in the
log carries the service's own `chaos-injected failure` marker under the same request id
(E3–E7). Four of the ten user requests after the switch failed (E4–E7, E18), which
matches the configured rate. The same path succeeds and fails (E13 against E5; E4
against E20), so a retry often works. The health endpoint answered 200 in every sample
while the switch was on (E12, E23), which is why the health dashboard is green. The
switch was still on at 12:30:00Z (E24). Class `infra-process`, cause
`degradation-switch`. Confidence: high for the mechanism; the user sample is small.

Impact seen in telemetry: product pages `/products/1`, `/products/4`, `/products/5`
and the order list `GET /orders` returned 503 to users. Order creation (`POST /orders`)
did not fail in the log (E8, E18) — see Gaps.

## Timeline

All times UTC, 2026-11-15.

- 12:25:28.329 — process start, the only startup event in the log (E14).
- 12:25:29.039–12:25:33.237 — six user requests, all 200/201 (E17).
- 12:25:36.289 — **switch marker**: `chaos mode enabled`, `failure_rate` 0.4,
  `error_status` 503, through `POST /chaos/enable` (E1, E2).
- 12:25:38.342–12:25:42.552 — five user requests, all 200/201 (E18).
- 12:25:43.607 — first failure: `GET /products/5 -> 503` with the injection marker
  (E3, E4).
- 12:25:44.663 — `POST /orders -> 201` (E18).
- 12:25:45.716, 12:25:46.771, 12:25:47.823 — three more injected 503s on
  `/products/1`, `/orders`, `/products/4` (E5, E6, E7). Last user request in the log.
- 12:25:53 — complaint raised.
- 12:26:06 — investigation start.
- 12:26:09–12:26:10 — baseline: health 200 (E12), gauge `faultline_chaos_enabled 1`
  (E9), four 503 series and no exception series (E8).
- 12:26:53.945 — an investigator probe of `/products/1` got an injected 503 after
  three 200 answers (E19).
- 12:29:51–12:29:53 — `/products/4` and `/orders` answered 200 (E21, E22); three
  health probes answered 200 (E23).
- 12:30:00 — gauge still 1, uptime 271.86 s without a reset, no exception series (E24).

## Investigation

Trigger: manual, the `/konan` human profile. The complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794745553",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green." },
  "startsAt": "2026-11-15T12:25:53Z"
}
```

Investigation start: 2026-11-15T12:26:06Z (trigger latency 13 s). The reporter stated
no severity, so none is recorded.

- **Setup.** `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`.
  Budget: one triage round, at most three deep-dives per round, at most two rounds.
- **Baseline.** Health 200 with an uptime of 41 s (E12). Metrics: four 503 series on
  business paths, no exception series, `faultline_chaos_enabled 1` (E8, E9, E15). Log:
  one startup event, a `chaos_enabled` line, four `chaos_failure` lines (E1, E3–E7,
  E14).
- **Triage.** Three lenses ran in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the switch and its markers. The
  infra-process lens found no restart and no saturation. The interfaces lens reproduced
  an injected 503 by probe (E19) and found no contract violation. The software-defect
  lens found no exception and showed that the same input succeeds and fails (E20).
- **Deep-dive.** Skipped. The triage evidence for H1 was deterministic and complete,
  so H1 went straight to the judge.
- **Judge.** One fresh judge saw the hypothesis list and the verbatim evidence only.
  Verdicts: H1 validated, H2, H3 and H4 invalidated. The judge named three claims that
  the evidence did not carry: that health is exempt (one sample), that order creation
  fails (no such failure), and that the complaint time matches the switch time.
- **After the judge.** Five read-only probes answered the open points: `/products/4`
  200 (E21), `/orders` 200 (E22), three more health answers 200 (E23), and a final
  metrics read (E24). The hypothesis statements were narrowed to what the evidence
  carries; the two remaining points are recorded as gaps.

Investigator traffic: every request id that starts with `konan-` is an investigator
probe. The injected 503 of E19 is investigator traffic and does not count as user
impact; the four user failures are E4–E7.

## Hypotheses

### H1 — an error-injection switch inside the service is on (validated)

The switch line (E1) and its request (E2) precede every failure. No request failed
before it (E17). Every user failure is a 503 with a `chaos_failure` line under the
same request id (E3–E7), and the application's own counter holds exactly those four
(E8). The failure share after the switch is four of ten (E4–E7, E18) against a
configured rate of 0.4. The same path succeeds and fails: `/products/1` (E13, E5,
E19), `/products/5` (E4, E20), `/products/4` (E7, E21), `/orders` (E6, E22). The gauge
reads 1 at three scrapes over four minutes (E9, E10, E24). The exception counter has
no series (E11, E24). Health answered 200 in every sample after the switch (E12, E23).
No evidence against.

### H2 — a code defect on specific inputs (invalidated)

The failures name specific paths (E4, E6, E7), which is the only support. Against: no
status 500 and no exception series (E11, E24); every failure carries the injection
marker (E3, E5); and each failed input also succeeded — `/products/1` (E13),
`/products/5` (E20), `/products/4` (E21), `/orders` (E22). The injected 503 also hit an
investigator probe of a path that had answered 200 three times (E19).

### H3 — repeated crashes or restarts (invalidated)

The process was 41 s old at the baseline (E14, E15), which is the only support. Against:
one startup event only (E14); the uptime rises without a reset across three scrapes
(E15, E16, E24); six requests succeeded between the start and the switch (E17); every
failure has an application access line (E4–E7), so the process was serving when it
failed them. The young process is a fact of its own: see Gaps.

### H4 — a gateway tier in front of the service (invalidated)

503 is a gateway-shaped status (E8), which is the only support. Against: the
application itself produced and logged every observed 503, with its own marker (E3–E7,
E19), and the switch line sets `error_status` 503 (E1). No front tier is visible on
this surface.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Ask the operators who turned the switch on at 12:25:36 UTC, and whether it was
  intended. The enabling request is `299cbf686b5d` from a loopback client (E2).
- Read the operator view of the switch state to confirm the current rate and the list
  of exempt paths.
- Watch `faultline_chaos_enabled` and the 503 series of `http_requests_total` on
  business paths. The health endpoint does not show this failure.
- Ask the reporter for one failed order with its time. The log shows no failed order
  creation.
- Ask why the process started at 12:25:28 UTC, and whether users saw failures before
  that time.
- Observation, not a finding: product 4 has `"price":null` (E21). No failure is tied
  to it in the telemetry.

## Gaps

- **Before 12:25:28.329Z.** The log starts at the process start and has no backups.
  The complaint says "a few minutes ago"; the first failure in telemetry is 10 s before
  the complaint. What happened before the process start is out of reach.
- **Who turned the switch on.** The log holds a request id and a loopback address, no
  identity.
- **Switch state.** The operator endpoint is outside the contract. The state comes
  from the gauge and one log line.
- **Order creation.** `POST /orders` returned 201 three times of three. Probes are
  GET-only, so the investigator could not test it. "Orders error out" is confirmed for
  the order list only.
- **Sample size and current impact.** Ten user requests after the switch, four failed.
  User traffic stops in the log at 12:25:47.823Z, so the impact after that is not
  measured.
- **Exempt paths.** Health and metrics answered 200 in ten of ten samples after the
  switch. The exemption is an inference, not a read value.
- **Front tier.** None is visible; a client-side error count could not be compared.
- **Tokens.** Not captured in this session.
