---
konan_journal: 2
investigation:
  id: 2026-11-15-handover-check-chaos-window
  trigger: "manual: /konan human profile; source human; fingerprint human-1794771617; labels.alertname human-report; no severity stated; startsAt 2026-11-15T19:40:17Z; investigation start 2026-11-15T19:40:23Z; trigger latency 6 s"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-15T19:40:23Z
  concluded: 2026-11-15T19:45:01Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An operational degradation switch inside the service (chaos mode) was on from 19:39:41.074Z to 19:39:47.392Z and injected the HTTP 503 responses into non-investigator requests; the switch was off at every later reading, so this failure is over."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E24]
    evidence_against: []
  - id: H2
    statement: "A failure of non-investigator traffic is active now: continued degradation after the switch went off, or a process crash, hang, or restart."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E8, E9, E10, E11, E12, E13, E14, E15, E21]
  - id: H3
    statement: "The product detail endpoint raises an unhandled ZeroDivisionError for product 3, whose units_in_stock is 0, and returns HTTP 500; the defect is reproducible, and in this process lifetime only investigator probes triggered it."
    incident_class: software-defect
    state: validated
    evidence_for: [E14, E16, E17, E18, E19, E20, E22, E23]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 fails with HTTP 500 and an unhandled ZeroDivisionError (division by units_in_stock, which is 0 for product 3). Only investigator probes triggered it; a user request for product 3 would fail the same way."
    evidence: [E14, E16, E17, E18, E19, E20, E23]
  - statement: "The request counter labels the injected 503 responses with the raw path (/products/1, /products/2) and all other product detail responses with the route template (/products/{product_id}); an error-rate query on the route template misses the injected failures."
    evidence: [E7, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:37.209Z (the only line with event startup in the file)"
    quote: |-
      {"ts": "2026-11-15T19:39:37.209Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:41.074Z"
    quote: |-
      {"ts": "2026-11-15T19:39:41.074Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "713adb7a6996", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:42.125Z (first of five chaos_failure lines)"
    quote: |-
      {"ts": "2026-11-15T19:39:42.125Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "fe9285a33bc0", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:42.125Z"
    quote: |-
      {"ts": "2026-11-15T19:39:42.125Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "fe9285a33bc0", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.297, "client": "127.0.0.1:55785"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:46.339Z (the last line with status 503 in the file)"
    quote: |-
      {"ts": "2026-11-15T19:39:46.339Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "8e5e0aad95a6", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.265, "client": "127.0.0.1:55790"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:47.392Z"
    quote: |-
      {"ts": "2026-11-15T19:39:47.392Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "2c32daf30dc2", "event": "chaos_disabled"}
  - id: E7
    type: metric
    source: "/metrics scrape @ 2026-11-15T19:40:35Z, request id konan-1794771635-21165 (all series with status 503)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E8
    type: metric
    source: "/metrics scrape @ 2026-11-15T19:42:18Z, request id konan-1794771738-21325"
    quote: |-
      faultline_chaos_enabled 0
  - id: E9
    type: metric
    source: "/metrics scrape @ 2026-11-15T19:42:18Z, request id konan-1794771738-21325 (all series with status 503)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:40:07.446Z (first non-investigator request after the switch went off)"
    quote: |-
      {"ts": "2026-11-15T19:40:07.446Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "0af6ad4a2a14", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.761, "client": "127.0.0.1:55792"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:40:09.548Z"
    quote: |-
      {"ts": "2026-11-15T19:40:09.548Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "2304b0659c0b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.975, "client": "127.0.0.1:55794"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:40:11.652Z (the last non-investigator line in the file)"
    quote: |-
      {"ts": "2026-11-15T19:40:11.652Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "9b34aa4a0788", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.773, "client": "127.0.0.1:55796"}
  - id: E13
    type: probe
    source: "/health, request id konan-1794771635-21160"
    quote: |-
      {"status":"ok","uptime_seconds":58.13277962477878}
      -- HTTP 200 in 0.001462s request_id=konan-1794771635-21160
  - id: E14
    type: probe
    source: "/products, request id konan-1794771643-21174"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001429s request_id=konan-1794771643-21174
  - id: E15
    type: probe
    source: "/orders, request id konan-1794771644-21184"
    quote: |-
      [{"id":1,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T19:40:09.548+00:00"}]
      -- HTTP 200 in 0.001473s request_id=konan-1794771644-21184
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:41:35.013Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T19:41:35.013Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794771695-21250", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:41:35.022Z"
    quote: |-
      {"ts": "2026-11-15T19:41:35.022Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794771695-21250", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.916, "client": "127.0.0.1:55829"}
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:41:40.385Z"
    quote: |-
      {"ts": "2026-11-15T19:41:40.385Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794771700-21276", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.682, "client": "127.0.0.1:55834"}
  - id: E19
    type: metric
    source: "/metrics scrape @ 2026-11-15T19:42:18Z, request id konan-1794771738-21325"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E20
    type: metric
    source: "/metrics scrape @ 2026-11-15T19:40:35Z, request id konan-1794771635-21165 (the exception counter had no series before the investigator probed product 3)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E21
    type: metric
    source: "/metrics scrape @ 2026-11-15T19:42:18Z, request id konan-1794771738-21325"
    quote: |-
      process_uptime_seconds 161.29422645783052
      process_max_rss_bytes 47513600
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:41:34.487Z"
    quote: |-
      {"ts": "2026-11-15T19:41:34.487Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794771694-21245", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.572, "client": "127.0.0.1:55828"}
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:41:40.382Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T19:41:40.382Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794771700-21276", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:39:45.285Z"
    quote: |-
      {"ts": "2026-11-15T19:39:45.285Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "c6f3a399bcd0", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.289, "client": "127.0.0.1:55789"}
gaps:
  - "Telemetry starts at the process start, 19:39:37.208Z: the log has no rotated backups and the counters are per process. Any noise before that time is not visible, and the surface cannot show whether this start replaced an earlier process."
  - "No non-investigator request exists after 19:40:11.652Z. The current state for user traffic rests on the five user requests of 19:40:07 to 19:40:11 and on investigator GET probes."
  - "Order creation (POST /orders) is outside the read-only probe surface. Its state after the window rests on one user request (E11). The effect of the null price of product 4 on an order is untested."
  - "The telemetry does not say who turned the switch on and off, or why. Both requests came from 127.0.0.1 with non-investigator request ids; the operator surface is out of bounds."
  - "The gauge and the 503 counters were last read at 19:42:18Z (earlier readings: 19:40:35Z, and two lens scrapes at 19:41:18Z and 19:41:32Z). Nothing excludes a later re-enable."
  - "Lenses run: infra-process, software-defect, interfaces. The repo has no lens file for load-saturation, third-party or data-db; saturation was checked at the baseline only (peak RSS steady at 47513600 bytes, all request durations below 13 ms), and the lab has no database and no third-party dependency (docs/lab.md)."
  - "lab/server.out was not read: the surface contract names lab/logs/app.log as the log surface."
usage:
  model: claude-fable-5-2
  tokens: 1463007
  wall_clock_seconds: 278
---

# Handover check: a closed chaos window, no active incident, one latent defect

## Summary

**No active incident.** The noise was a 6.3-second window, 19:39:41.074Z to
19:39:47.392Z, in which an operational degradation switch inside the service (chaos
mode, failure rate 0.6, status 503) was on (E2, E6). Five user requests failed with
HTTP 503 in that window, among them one order creation (E3, E4, E5, E7, E24). The
switch read 0 at every scrape since (E8), the 503 counters did not move (E7, E9), and
the five user requests after the window all succeeded (E10, E11, E12). One process ran
throughout (E1, E13, E21). Confidence is high for the telemetry window, which starts at
the process start, 19:39:37Z; nothing earlier is visible.

One **latent defect** rides along: `GET /products/3` fails with HTTP 500 and an
unhandled `ZeroDivisionError`, because product 3 has zero stock (E14, E16, E17). Only
investigator probes triggered it (E19, E20), so it is not the incident; a user who
opens product 3 would get the same failure.

## Timeline

All times UTC, 2026-11-15.

- 19:39:37.209 — process start, version 0.1.0; the only startup marker (E1).
- 19:39:41.074 — **change marker:** chaos mode enabled, `failure_rate 0.6`,
  `error_status 503`, `extra_latency_ms 0` (E2).
- 19:39:42.125 — first injected 503, `GET /products` (E3, E4).
- 19:39:45.285 — injected 503 on `POST /orders` (E24).
- 19:39:46.339 — last 503 in the log (E5). Five 503 responses in total (E7).
- 19:39:47.392 — **change marker:** chaos mode disabled (E6).
- 19:40:07.446 to 19:40:11.652 — five user requests, all 2xx, one order created (E10,
  E11, E12).
- 19:40:17 — complaint raised; 19:40:23 — investigation start.
- 19:40:35 to 19:40:44 — baseline probes: health, metrics, products, orders, all 200
  (E13, E14, E15); 503 counters at five (E7); no exception series (E20).
- 19:41:35.013 and 19:41:40.382 — investigator probes of `/products/3` raise
  `ZeroDivisionError`, HTTP 500 (E16, E17, E23, E18).
- 19:42:18 — last scrape: gauge 0, 503 counters unchanged, exception counter 2, uptime
  161 s (E8, E9, E19, E21).

## Investigation

Complaint object, as synthesized by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794771617",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-11-15T19:40:17Z"
}
```

Investigation start: 2026-11-15T19:40:23Z (trigger latency 6 s).

- **Baseline.** Health 200 (E13), metrics snapshot (E7, E20), full log read (31 lines
  at that time), then the business surface: `/products`, `/products/1`, `/orders`, all
  200 (E14, E15). The baseline already showed the chaos markers and the gauge at 0.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  software-defect, interfaces. All three reported the closed chaos window. The
  software-defect lens probed `/products/3` twice and found the `ZeroDivisionError`.
  The interfaces lens reported the label difference in the request counter.
- **Deep-dive.** None. The triage evidence for each hypothesis was deterministic and
  complete, so the list went straight to the judge.
- **Judge.** A fresh agent with the hypotheses and verbatim evidence only. H1
  validated, H2 invalidated, H3 validated. The judge narrowed two claims: "off now"
  holds up to the last scrape at 19:42:18Z, and "not user impact" holds for this
  process lifetime only. Both limits are in Gaps.

## Hypotheses

### H1 — the 503 responses came from the chaos switch, and it is over (validated)

The enable marker sets status 503 (E2). The first failed request carries a
`chaos_failure` line and a 503 access line under one request id (E3, E4). The log has
five `chaos_failure` lines, and the counters show five 503 responses on the same
methods and paths (E7), one of them an order creation (E24). All five lie between the
enable and disable markers (E2, E6). After the disable marker there is no 503 in the
log (E5 is the last), the counters did not move between 19:40:35Z and 19:42:18Z (E7,
E9), and the gauge reads 0 (E8). One open detail: all five requests in the window
failed against a configured rate of 0.6; the sample is too small to read anything
into that.

### H2 — a failure is active now (invalidated)

Every prediction failed. The five user requests after the window succeeded in under
2 ms each (E10, E11, E12). Health and business probes returned 200 (E13, E14, E15).
There is one startup marker (E1), and the start time derived from uptime is the same
at 19:40:35Z and 19:42:18Z (E13, E21), so the process did not restart. The 503
counters did not move and the gauge is 0 (E9, E8).

### H3 — `GET /products/3` raises ZeroDivisionError (validated, latent)

Product 3 has `units_in_stock` 0 (E14). The last stack frame divides by
`product["units_in_stock"]` in `get_product`, `shop.py` line 64 (E16, E23). Two
probes gave two 500 responses (E17, E18). Product 4 on the same route returned 200
(E22), as did products 1 and 5 for users (E12). The exception counter had no series
before the probes (E20) and reads 2 after them (E19), which equals the two
investigator probes. So no user request triggered the defect in this process
lifetime. It is a latent finding, not the incident.

## Safe next steps

- Ask the outgoing on-call who turned chaos mode on at 19:39:41Z and off at
  19:39:47Z, and whether it was planned. Telemetry does not say.
- At the next check, read `faultline_chaos_enabled` and the 503 series of
  `http_requests_total` again; a gauge of 1 or a moving 503 counter reopens H2.
- Hand the product 3 defect to the service owner with E16 as the pointer, and watch
  `http_exceptions_total{type="ZeroDivisionError"}` for increases that are not
  investigator probes.
- When reading error rates for product detail requests, sum the raw-path series and
  the route-template series (second latent finding).
- Ask the service owner what an order for product 4 (null price) returns; the
  read-only surface cannot test it.

## Gaps

- **History before 19:39:37Z.** The log starts at the process start, has no rotated
  backups, and the counters are per process. If the "noise earlier" was before this
  process, it is not visible here. Whether an earlier process existed is not visible
  either.
- **No user traffic after 19:40:11.652Z.** "Healthy now" for users rests on five user
  requests and on investigator GET probes.
- **Order creation.** POST is outside the read-only surface; one user order after the
  window succeeded (E11). The null price of product 4 is untested for orders.
- **Who and why.** The switch requests came from 127.0.0.1 with non-investigator ids;
  the operator surface is out of bounds for the investigator.
- **Later state.** The last reading of the gauge and the counters is 19:42:18Z.
- **Lenses.** Three lenses exist and ran. There is no lens for load-saturation,
  third-party or data-db; the lab has no database and no third-party dependency, and
  saturation was checked at the baseline only.
- **`lab/server.out`** was not read; the surface contract names only
  `lab/logs/app.log`.
