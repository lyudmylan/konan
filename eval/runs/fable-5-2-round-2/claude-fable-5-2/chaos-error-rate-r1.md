---
konan_journal: 2
investigation:
  id: 2026-11-15-intermittent-503-chaos-switch
  trigger: 'manual — /konan (human profile). Complaint object: {"source": "human", "fingerprint": "human-1794765680", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."}, "startsAt": "2026-11-15T18:01:20Z"}. Investigation start 2026-11-15T18:01:26Z; trigger latency 6 s. No severity stated by the reporter.'
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-15T18:01:26Z
  concluded: 2026-11-15T18:06:50Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational switch inside the target (chaos mode) was turned on at 18:01:02.602Z with failure_rate 0.4 and error_status 503; while it is on, the process itself rejects a random share of requests on the product and order routes with 503 before the handler runs, and it was still on at 18:06:44Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode) was turned on at 18:01:02.602Z with failure rate 0.4 and status 503; since then the process itself rejects a random share of requests on the business routes with 503, and the switch is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E20, E25, E26, E27]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code raises an unhandled exception on specific inputs, and this causes the errors the users report."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E21, E22, E23, E24]
    evidence_against: [E16, E17, E3, E5, E7, E8, E9, E10]
  - id: H3
    statement: "The process crashed, restarted, or ran out of resources, and this causes the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E18, E19, E15, E17, E5, E7]
  - id: H4
    statement: "A gateway or proxy tier, or a downstream dependency, fails on its own and returns the 503s."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E4, E5, E6, E7, E10, E11]
latent_findings:
  - statement: "GET /products/3 fails every time with an unhandled ZeroDivisionError: the product handler divides units_ordered by units_in_stock, and product 3 has units_in_stock 0. Only investigator probes triggered it (2 of 2); no non-investigator request to /products/3 is in the log, so it is not the reported incident."
    evidence: [E21, E22, E23, E24, E25]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:02.602Z"
    quote: |-
      {"ts": "2026-11-15T18:01:02.602Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "531f6b0a1c0d", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:02.602Z"
    quote: |-
      {"ts": "2026-11-15T18:01:02.602Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "531f6b0a1c0d", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.004, "client": "127.0.0.1:54520"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:00:59.537Z (last request before the marker E1)"
    quote: |-
      {"ts": "2026-11-15T18:00:59.537Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "8dcbe3885e14", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.658, "client": "127.0.0.1:54519"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:06.760Z"
    quote: |-
      {"ts": "2026-11-15T18:01:06.760Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "165e387c6d56", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:06.760Z (first 5xx in the file)"
    quote: |-
      {"ts": "2026-11-15T18:01:06.760Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "165e387c6d56", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.323, "client": "127.0.0.1:54523"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:07.812Z"
    quote: |-
      {"ts": "2026-11-15T18:01:07.812Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "02c9de0ebaf0", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:07.812Z"
    quote: |-
      {"ts": "2026-11-15T18:01:07.812Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "02c9de0ebaf0", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.269, "client": "127.0.0.1:54524"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:10.970Z"
    quote: |-
      {"ts": "2026-11-15T18:01:10.970Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8cb2b0d631e1", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.337, "client": "127.0.0.1:54527"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:05.707Z"
    quote: |-
      {"ts": "2026-11-15T18:01:05.707Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "57b106b6dae6", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.843, "client": "127.0.0.1:54522"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:12.023Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T18:01:12.023Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "47003e5af0ba", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T18:01:12.023Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "47003e5af0ba", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.275, "client": "127.0.0.1:54528"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:13.054Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T18:01:13.054Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "c71e68cde282", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-15T18:01:13.054Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "c71e68cde282", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.149, "client": "127.0.0.1:54529"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:01:09.918Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T18:01:09.918Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "a5773ff5b91e", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
      {"ts": "2026-11-15T18:01:09.918Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "a5773ff5b91e", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.279, "client": "127.0.0.1:54526"}
  - id: E13
    type: metric
    source: "/metrics, probe konan-1794765798-14756 @ 2026-11-15T18:03:18.581Z"
    quote: |-
      faultline_chaos_enabled 1
  - id: E14
    type: metric
    source: "/metrics, probe konan-1794765798-14756 @ 2026-11-15T18:03:18.581Z (every 5xx series of http_requests_total in the scrape)"
    quote: |-
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E15
    type: probe
    source: "/health, request id konan-1794765699-14659 @ 2026-11-15T18:01:39.864Z"
    quote: |-
      {"status":"ok","uptime_seconds":45.74740145821124}
      -- HTTP 200 in 0.002624s request_id=konan-1794765699-14659
  - id: E16
    type: metric
    source: "/metrics, probe konan-1794765699-14664 @ 2026-11-15T18:01:39.930Z (the exception counter has no series)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E17
    type: metric
    source: "/metrics, probe konan-1794765699-14664 @ 2026-11-15T18:01:39.930Z (the complete http_requests_total list)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:00:54.128Z (the only startup event; the log has no backup files)"
    quote: |-
      {"ts": "2026-11-15T18:00:54.128Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E19
    type: metric
    source: "/metrics, probe konan-1794765699-14664 @ 2026-11-15T18:01:39.930Z, then probe konan-1794765798-14756 @ 2026-11-15T18:03:18.581Z"
    quote: |-
      process_uptime_seconds 45.813576458022
      process_max_rss_bytes 47218688
      process_uptime_seconds 144.4678135830909
      process_max_rss_bytes 47218688
  - id: E20
    type: probe
    source: "/orders, request id konan-1794765799-14761 @ 2026-11-15T18:03:19.152Z"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T18:00:57.480+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T18:01:10.970+00:00"}]
      -- HTTP 200 in 0.001511s request_id=konan-1794765799-14761
  - id: E21
    type: probe
    source: "/products/3, request id konan-1794765799-14766 @ 2026-11-15T18:03:19.729Z"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794765799-14766"}
      -- HTTP 500 in 0.009685s request_id=konan-1794765799-14766
  - id: E22
    type: probe
    source: "/products/3, request id konan-1794765804-14776 @ 2026-11-15T18:03:24.669Z (repeat of E21)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794765804-14776"}
      -- HTTP 500 in 0.003534s request_id=konan-1794765804-14776
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:03:19.729Z (stack trimmed to its last frame; the local path prefix of the file is trimmed)"
    quote: |-
      {"ts": "2026-11-15T18:03:19.729Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794765799-14766", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n … ZeroDivisionError: division by zero"}
  - id: E24
    type: probe
    source: "/products, request id konan-1794765800-14771 @ 2026-11-15T18:03:20.209Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001357s request_id=konan-1794765800-14771
  - id: E25
    type: metric
    source: "/metrics, probe konan-1794765970-14879 @ 2026-11-15T18:06:10.821Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
      faultline_chaos_enabled 1
      process_uptime_seconds 316.7140114582144
      process_max_rss_bytes 47218688
  - id: E26
    type: probe
    source: "/products, request id konan-1794766004-15065 @ 2026-11-15T18:06:44.253Z"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1794766004-15065"}
      -- HTTP 503 in 0.000999s request_id=konan-1794766004-15065
  - id: E27
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:06:44.253Z"
    quote: |-
      {"ts": "2026-11-15T18:06:44.253Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794766004-15065", "event": "chaos_failure", "method": "GET", "path": "/products"}
gaps:
  - "No non-investigator traffic arrived after 18:01:14.102Z. The user failure rate rests on 10 requests (5 failed, against a configured rate of 0.4); after that time the active state rests on the gauge (E25) and on one rejected investigator probe (E26, E27)."
  - "Who or what turned the switch on is not visible on the surface: the log shows a local client and an unstamped request id only (E2)."
  - "The log starts at 18:00:54.127Z, 8.5 s before the switch, and the process was about 26 s old at the complaint time. The complaint says 'a few minutes ago'; nothing on the surface covers an earlier process instance or an earlier failure window."
  - "No client-side or gateway-side record is in the lab surface, so a failure that never reached the process is invisible here."
  - "Whether /health and /metrics are exempt from the switch is not proven: 2 health probes and 6 metrics probes after the switch all returned 200, which is a small sample."
  - "The automated schema check of this journal did not run (no interpreter is pre-approved in this session); the shape and the references were checked by hand."
usage:
  model: claude-fable-5-2
  tokens: 1528275
  wall_clock_seconds: 324
---

# Intermittent 503s on product and order routes: chaos switch turned on at 18:01:02Z

## Summary

**Root cause identified** (`infra-process` / `degradation-switch`). An operational
switch inside the target, chaos mode, was turned on at 18:01:02.602Z with
`failure_rate` 0.4 and `error_status` 503 (E1, E2). While it is on, the process itself
rejects a random share of requests with 503 before the handler runs: every 503 in the
log has a `chaos_failure` line with the same request id (E4–E7, E10–E12, E27), and no
5xx exists before the marker. Impact on users: 5 of the 10 non-investigator requests
between 18:01:04Z and 18:01:14Z failed, on `GET /products/{id}`, `GET /orders` and
`POST /orders`; a retry of the same route passed (E7→E8, E9→E10), which is the
"works again on retry" of the complaint. The health endpoint stayed 200 (E15), which
matches the green dashboard. The switch was still on at 18:06:44Z: the gauge reads 1
(E25) and one investigator probe of `GET /products` was rejected (E26, E27).
Confidence: high for the mechanism; the user failure rate rests on a small sample.

A second, separate finding is latent: `GET /products/3` fails every time with a
`ZeroDivisionError` (E21–E24). Only investigator probes triggered it. It is not the
reported incident.

## Timeline

All times UTC, 2026-11-15.

- 18:00:54.128 — the process starts; the only `startup` event (E18).
- 18:00:54–18:00:59 — 6 non-investigator requests, all 2xx; last one is E3.
- **18:01:02.602 — `chaos_enabled` marker**: `failure_rate` 0.4, `error_status` 503,
  `extra_latency_ms` 0, set by `POST /chaos/enable` from a local client (E1, E2).
- 18:01:05.707 — `GET /products/1` → 200 (E9).
- 18:01:06.760 — first 5xx: `GET /products/2` → 503 with `chaos_failure`, 4.2 s after
  the marker (E4, E5).
- 18:01:07.812 — `POST /orders` → 503 with `chaos_failure` (E6, E7).
- 18:01:09.918 — `GET /products/5` → 503 with `chaos_failure` (E12).
- 18:01:10.970 — `POST /orders` → 201 (E8).
- 18:01:12.023 — `GET /products/1` → 503 with `chaos_failure` (E10).
- 18:01:13.054 — `GET /orders` → 503 with `chaos_failure` (E11).
- 18:01:14.102 — last non-investigator request in the log.
- 18:01:20 — complaint raised; 18:01:26 — investigation starts.
- 18:01:39 — baseline: `/health` 200 (E15); no exception series (E16); five 503 series
  (E17); uptime 45.8 s (E19).
- 18:03:18 — gauge `faultline_chaos_enabled 1`; the 503 counters are unchanged (E13,
  E14); uptime 144.5 s, RSS unchanged (E19).
- 18:03:19, 18:03:24 — investigator probes of `/products/3` → 500 `ZeroDivisionError`
  (E21, E22, E23).
- 18:06:10 — gauge still 1 (E25).
- 18:06:44.253 — investigator probe `GET /products` → 503 with `chaos_failure`
  (E26, E27).

## Investigation

- **Trigger.** Manual, `/konan`. The complaint object is in the `trigger` field of the
  machine core, verbatim. `startsAt` 18:01:20Z, investigation start 18:01:26Z.
- **Baseline.** `/health`, `/metrics`, and the whole of `lab/logs/app.log` (one file,
  no backups). The baseline already showed the `chaos_enabled` marker, five 503s after
  it, no exception series, one startup event.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the same marker and the same pairing
  of each 503 with a `chaos_failure` line. The infra-process lens found no restart and
  no saturation. The software-defect lens found no exception on user traffic and showed
  that the failing inputs also succeed.
- **Deep-dive.** Skipped for H1: the triage evidence was deterministic and complete.
  The orchestrator collected the verbatim quotes and probed the business routes; the
  probe of `/products/3` found the latent defect.
- **Judge.** One fresh judge with the hypothesis list and the verbatim ledger only.
  Verdicts: H1 validated with two limits ("all business routes" and "still rejects"
  not proven), H2, H3 and H4 invalidated as the cause.
- **After the judge.** Five more read-only probes closed both limits: `GET /products`
  (the list) was rejected with a `chaos_failure` line at 18:06:44.253Z (E26, E27).
  Of 12 investigator probes of business routes after the switch, 1 was rejected.
- **Budget.** One triage round, no deep-dive agent, one judge round.

## Hypotheses

### H1 — chaos switch injects 503s (infra-process) — validated

The marker E1 states the mechanism in its own fields: rate 0.4, status 503. The
prediction held on each point. No 5xx exists before the marker (E3 is the last request
before it, E17 has no other 5xx series). Each of the five user 503s has a
`chaos_failure` line with the same request id (E4/E5, E6/E7, E10, E11, E12). The same
route and input both passes and fails after the marker: `/products/1` (E9, E10),
`POST /orders` (E7, E8), `GET /orders` (E11, E20). The rejected requests took 0.149 to
0.323 ms, less than the successes, and the 503 series carry the raw path while the 200
series carry the route template (E17); both point to a rejection before routing (an
inference). The gauge reads 1 at 18:03:18Z and 18:06:10Z (E13, E25), and a probe was
rejected at 18:06:44Z (E26, E27). Health stayed 200 (E15). No evidence against was
found.

### H2 — code defect on specific inputs (software-defect) — invalidated as the cause

A real defect exists: `/products/3` raises `ZeroDivisionError` at `shop.py` line 64,
where `units_ordered` is divided by `units_in_stock`, and product 3 has
`units_in_stock` 0 (E21–E24). But only investigator probes triggered it. After all
five user 503s the exception counter had no series (E16) and no 500 series existed
(E17). The user-facing failures are not per-input: the same inputs succeed and fail
(E3/E5, E9/E10, E7/E8). The defect is recorded under `latent_findings`.

### H3 — crash, restart, or resource exhaustion (infra-process) — invalidated

One startup event only (E18). Uptime grew from 45.8 s to 144.5 s between two scrapes
98.7 s apart, and to 316.7 s later (E19, E25), so no restart occurred. Peak RSS is the
same in all scrapes (E19, E25). The health probe is 200 (E15). The failed requests are
fast, not slow (E5, E7). Limit: the log starts 8.5 s before the switch.

### H4 — gateway, proxy, or dependency failure (interfaces) — invalidated

The only pointer was the gateway-shaped status 503, and E1 shows that 503 is the status
the switch was set to return. The process itself logged an in-process cause line for
each 503 (E4, E6, E10, E11) and counted each one (E17). The failed requests took under
0.33 ms (E5, E7), which excludes a timeout or a slow dependency. Limit: the surface has
no client-side or gateway-side record.

## Safe next steps

Read-only only.

- Ask the operator of the target whether the `POST /chaos/enable` at 18:01:02.602Z
  (request id `531f6b0a1c0d`, local client) was intended, for example a planned test,
  and read the current state of the switch on the operator side.
- Watch the gauge `faultline_chaos_enabled` and the count of `chaos_failure` events in
  the log to follow the impact while the switch is on.
- Compare a client-side count of 5xx for 18:01:02Z–18:01:14Z with the five 503s in the
  log, to exclude failures that never reached the process.
- Review what the health dashboard reads. `/health` returns 200 while business routes
  fail, and the 503s are counted under raw paths (`/products/1`), not under the route
  template (`/products/{product_id}`); a panel keyed on the template shows no errors
  for that route (E17).
- For the latent defect: read the product handler at `shop.py` line 64, and list the
  products with `units_in_stock` 0 from `GET /products` to size the exposure.

## Gaps

- **Small sample, no fresh user traffic.** No non-investigator request arrived after
  18:01:14.102Z. The user failure rate (5 of 10) rests on 12 seconds of traffic. After
  that, the active state rests on the gauge and on one rejected investigator probe.
- **The actor is unknown.** The surface shows that a local client sent the enable
  request, with an unstamped request id. It does not show who or what sent it.
- **Onset against the complaint.** The complaint says "a few minutes ago". The log
  starts at 18:00:54.127Z and the switch came 8.5 s later, 18 s before the complaint
  was raised. Nothing on the surface covers an earlier process instance.
- **No outside view.** No client-side or gateway-side record exists in the lab, so a
  failure that never reached the process is invisible.
- **Exempt paths not proven.** `/health` (2 probes) and `/metrics` (6 probes) returned
  200 each time after the switch. The sample is too small to prove an exemption.
- **Journal check by hand.** The automated schema check did not run in this session;
  the field shapes, the evidence references, the cause and class pair, and the wall
  clock were checked by hand.
