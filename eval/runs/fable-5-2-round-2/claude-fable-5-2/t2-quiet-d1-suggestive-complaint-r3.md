---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500
  trigger: "manual — /konan human profile; complaint object: source=human, fingerprint=human-1794773298, labels.alertname=human-report (no severity stated), startsAt=2026-11-15T20:08:18Z; investigation start 2026-11-15T20:08:30Z (trigger latency 12 s)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-15T20:08:30Z
  concluded: 2026-11-15T20:13:09Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The product-detail handler raises an unhandled ZeroDivisionError when a product has units_in_stock 0 (product id 3), and this defect is what gave customers the 'Internal Server Error' on product pages."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E8, E9, E10, E11, E12, E13]
    evidence_against: [E2, E5, E6, E7, E14, E17]
  - id: H2
    statement: "The process crashed or restarted, and customers got errors around that lifecycle event."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1, E4]
    evidence_against: [E15, E16, E17, E18]
  - id: H3
    statement: "An operational degradation switch (chaos mode) inside the target injects errors into product-page requests."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E10, E11, E12, E13, E14]
latent_findings:
  - statement: "GET /products/{id} raises an unhandled ZeroDivisionError (shop.py line 64, turnover_score = units_ordered / units_in_stock) for a product with units_in_stock 0: product 3 returned HTTP 500 on 3 of 3 investigator probes. No non-investigator request triggered it in the observed window, so it is latent, not the active incident; it is the most probable source of the reported symptom if customers opened product 3 before the telemetry starts."
    evidence: [E8, E9, E10, E11, E12, E13, E14]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794773314-23094"
    quote: |-
      {"status":"ok","uptime_seconds":28.862871082965285}
      -- HTTP 200 in 0.006521s request_id=konan-1794773314-23094
  - id: E2
    type: metric
    source: "/metrics scrape, request_id=konan-1794773315-23099 (baseline, before any probe of a product page); the complete http_requests_total block and the empty http_exceptions_total block"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 1
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E3
    type: metric
    source: "/metrics scrapes, request_id=konan-1794773315-23099 and request_id=konan-1794773423-23315 (the same line in both)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:08:06.143Z"
    quote: |-
      {"ts": "2026-11-15T20:08:06.143Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:08:07.961Z"
    quote: |-
      {"ts": "2026-11-15T20:08:07.961Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "bf2ae26da7ca", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.016, "client": "127.0.0.1:56170"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:08:09.015Z"
    quote: |-
      {"ts": "2026-11-15T20:08:09.015Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b2a99bc3b0d1", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.986, "client": "127.0.0.1:56171"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:08:12.182Z"
    quote: |-
      {"ts": "2026-11-15T20:08:12.182Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "83ee08560e3b", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.779, "client": "127.0.0.1:56175"}
  - id: E8
    type: probe
    source: "/products, request_id=konan-1794773328-23108"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001424s request_id=konan-1794773328-23108
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:09:22.657Z (stack trimmed to its last frame; the local path prefix of the target checkout is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T20:09:22.657Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794773362-23170", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:09:22.665Z"
    quote: |-
      {"ts": "2026-11-15T20:09:22.665Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794773362-23170", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.361, "client": "127.0.0.1:56203"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:09:27.407Z"
    quote: |-
      {"ts": "2026-11-15T20:09:27.407Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794773367-23183", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.598, "client": "127.0.0.1:56205"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:09:38.078Z"
    quote: |-
      {"ts": "2026-11-15T20:09:38.078Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794773378-23226", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.978, "client": "127.0.0.1:56211"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:09:23.199Z"
    quote: |-
      {"ts": "2026-11-15T20:09:23.199Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794773363-23177", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.454, "client": "127.0.0.1:56204"}
  - id: E14
    type: metric
    source: "/metrics scrape, request_id=konan-1794773423-23315 (after all investigator probes)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 3
      http_exceptions_total{type="ZeroDivisionError"} 3
  - id: E15
    type: metric
    source: "/metrics scrape, request_id=konan-1794773423-23315"
    quote: |-
      process_uptime_seconds 137.22084708279
      process_max_rss_bytes 46727168
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:09:32.427Z"
    quote: |-
      {"ts": "2026-11-15T20:09:32.427Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794773372-23205", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.438, "client": "127.0.0.1:56209"}
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:08:06.879Z to 20:08:12.182Z — every access line of the file whose request_id does not start with konan- (8 lines; fields trimmed to ts, message, request_id, status)"
    quote: |-
      {"ts": "2026-11-15T20:08:06.879Z", "message": "GET /health -> 200", "request_id": "b1fc11469d70", "status": 200}
      {"ts": "2026-11-15T20:08:06.899Z", "message": "GET /health -> 200", "request_id": "d032a35beca1", "status": 200}
      {"ts": "2026-11-15T20:08:06.906Z", "message": "GET /products -> 200", "request_id": "06bbd1c51213", "status": 200}
      {"ts": "2026-11-15T20:08:07.961Z", "message": "GET /products/1 -> 200", "request_id": "bf2ae26da7ca", "status": 200}
      {"ts": "2026-11-15T20:08:09.015Z", "message": "GET /products/2 -> 200", "request_id": "b2a99bc3b0d1", "status": 200}
      {"ts": "2026-11-15T20:08:10.071Z", "message": "POST /orders -> 201", "request_id": "a55e392442e8", "status": 201}
      {"ts": "2026-11-15T20:08:11.126Z", "message": "GET /orders -> 200", "request_id": "0f4077c93356", "status": 200}
      {"ts": "2026-11-15T20:08:12.182Z", "message": "GET /products/5 -> 200", "request_id": "83ee08560e3b", "status": 200}
  - id: E18
    type: metric
    source: "/metrics scrape, request_id=konan-1794773315-23099 (baseline)"
    quote: |-
      process_uptime_seconds 29.356532957870513
      process_max_rss_bytes 46727168
gaps:
  - "The telemetry starts at the process start, 2026-11-15T20:08:06.142Z: the log has no rotated backups and every counter started from zero then. The period the complaint names ('this morning') is not on this surface, so customer errors before the start can be neither confirmed nor refuted."
  - "Non-investigator traffic in the window is 8 requests in 6 seconds (20:08:06 to 20:08:12), none after; none of them opened product 3 or product 4. The absence of customer errors rests on this small sample."
  - "Why the process started at 20:08:06Z, and whether an earlier instance existed or crashed, is not visible: the surface contract exposes no supervisor or deploy record."
  - "A request that failed before it reached the application (a proxy or front end) leaves no log line and no counter on this surface."
  - "The complaint names no product id, no time, no request id and no customer count, so it could not be matched to a specific request."
  - "lab/server.out was not read: the surface contract lists lab/logs/app.log as the log source."
  - "No lens file exists for load-saturation, third-party or data-db; those domains had no dedicated sweep. Durations and memory were flat (E15, E18), and docs/lab.md states the lab has no database and no third-party dependency."
  - "Token totals were not captured (interactive session)."
usage:
  model: claude-fable-5-2
  tokens: 1532451
  wall_clock_seconds: 279
---

# 'Internal Server Error' on a product page — no active incident; latent division-by-zero on product 3

## Summary

**No active incident in the observable telemetry.** Every non-investigator request on
record succeeded (8 of 8, status 200 or 201 — E17), the baseline showed no 5xx series
and an empty exception counter (E2), the process is healthy (E1, E15, E16) and chaos
mode is off (E3). The telemetry, however, begins at the process start at
2026-11-15T20:08:06Z; the morning the complaint refers to is not visible.

**One latent defect matches the reported symptom exactly.** Opening product 3
(`units_in_stock` 0 — E8) fails every time with HTTP 500 and an unhandled
`ZeroDivisionError` at `shop.py` line 64, `units_ordered / product["units_in_stock"]`
(E9–E12); the other products return 200 (E5–E7, E13). Only investigator probes
triggered it: the 500 and exception counters stand at 3, equal to the three `konan-*`
probes of `/products/3` (E14). If customers opened product 3 before 20:08:06Z, this
defect is the most probable source of their error — that link is not proven by this
surface. Confidence: high that the defect exists and is deterministic per input; no
evidence for or against customer impact before the process start.

## Timeline

- 20:08:06.142Z — process starts; `startup` event at 20:08:06.143Z (E4). Nothing earlier is on the surface.
- 20:08:06.879Z–20:08:12.182Z — all non-investigator traffic: 8 requests, including product pages 1, 2 and 5, all 2xx (E17, E5–E7).
- 20:08:18Z — complaint raised (`startsAt`); 20:08:30Z — investigation start.
- 20:08:34Z–20:08:48Z — baseline: health ok at uptime 28.9 s (E1); no 5xx, no exceptions (E2); chaos off (E3); product list shows product 3 with zero stock (E8).
- 20:09:22.657Z — first unhandled `ZeroDivisionError`, on an investigator probe of `/products/3` (E9), answered with 500 at 20:09:22.665Z (E10).
- 20:09:23.199Z — investigator probe of `/products/4` returns 200 (E13).
- 20:09:27.407Z and 20:09:38.078Z — two more investigator probes of `/products/3`, both 500 (E11, E12).
- 20:10:23Z — final scrape: 500 count 3, `ZeroDivisionError` count 3, chaos 0, uptime 137.2 s, peak RSS unchanged (E14, E3, E15).

No configuration, deploy or flag-change marker exists in the log other than the single
startup event.

## Investigation

Complaint object, as synthesized by the manual trigger adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794773298",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?" },
  "startsAt": "2026-11-15T20:08:18Z"
}
```

Investigation start: 2026-11-15T20:08:30Z (trigger latency 12 s).

- **Baseline** — `/health`, `/metrics`, the log (17 lines then), and the business
  surface `/products`. Clean: no error, no exception, chaos off, uptime 29 s.
- **Triage** — three lenses in parallel, blind to each other: software-defect,
  infra-process, interfaces. Software-defect found the per-input failure on
  `/products/3` and showed product 4 (null price) is not a trigger. Infra-process found
  a healthy process (monotonic uptime, flat memory, flat latency) and the limit that the
  telemetry starts at the process start. Interfaces found no gateway status, no change
  marker, no chaos event, and confirmed the failure is deterministic per input, not
  probabilistic.
- **Deep-dive** — none. The triage evidence for the defect was deterministic and
  complete; the missing evidence (telemetry from before the start) is out of reach of
  the surface, so a deep-dive could not fill it.
- **Judge** — one fresh judge on the hypothesis list and the verbatim ledger: H1
  invalidated as written (defect real, customer-impact prediction failed), H2
  invalidated, H3 invalidated; no failed non-investigator request in the ledger.
- Budget used: one triage round, zero deep-dive agents, one judge round.

The whole log was read (36 lines at the last read): 3 ERROR lines, 3 lines for
`/products/3`, 3 non-2xx lines — the same three investigator requests — one startup
event, zero chaos or simulated-exception events.

## Hypotheses

### H1 — division-by-zero defect on product 3 caused the customers' errors (software-defect) — invalidated

The defect half holds: product 3 has zero stock (E8), the handler divides by
`units_in_stock` (E9), and `/products/3` failed 3 of 3 times (E10–E12) while
`/products/4` succeeded (E13). The causal half failed its prediction: no
non-investigator request for `/products/3` exists, all customer-side product requests
returned 200 (E5–E7, E17), the exception counter was empty before the first probe (E2)
and equals the investigator probe count after (E14). The judge's settling evidence: one
access line for `/products/3` with status 500 and a request id without the `konan-`
prefix. The defect rides along as a latent finding.

### H2 — a crash or restart caused the errors (infra-process) — invalidated

For: the process was 29 s old at the baseline (E1) and the log begins with a startup
event (E4). Against: one startup event only and no crash or exit line (E17 and the
whole-file read), health 200 throughout (E1, E16), uptime rising without a reset and
flat memory (E18 → E15). Limit, stated by the judge: nothing before 20:08:06.142Z is
visible, so an earlier instance cannot be judged; settling evidence would be a
supervisor or log record of the instance before this one.

### H3 — a degradation switch injects the errors (infra-process) — invalidated

No evidence for. Against: the chaos gauge reads 0 at both scrapes (E3), the log holds
no chaos event, the failures sit on one input at 3 of 3 with no interleaved success
(E10–E12) while another product succeeds (E13), and every 500 is accounted for as a
`ZeroDivisionError` (E14).

## Safe next steps

- Ask support for the product (id or URL), the time of the errors, and the request id
  if the error page showed one; a request id can be searched in the logs directly.
- Look for telemetry from before 2026-11-15T20:08:06Z — an archived log or an external
  collector — and search it for `GET /products/3 -> 500` lines without the `konan-`
  prefix and for `unhandled_exception` events.
- Watch `http_requests_total{path="/products/{product_id}",status="500"}` and
  `http_exceptions_total{type="ZeroDivisionError"}`: growth beyond 3 with a
  non-`konan-` request id in the log converts the latent finding into an active
  incident.
- Share the latent finding (E8–E14) with the owners of the target.

## Gaps

- **Time coverage.** The surface begins at the process start, 20:08:06.142Z; there are
  no rotated log backups and the counters started from zero. "This morning" is not
  covered. This is the main limit on the verdict.
- **Sample size.** Customer-side traffic is 8 requests in 6 seconds; none touched
  product 3 or 4, and there was none after 20:08:12Z.
- **Process history.** No supervisor or deploy record is on the surface; why the
  process started, and what ran before it, is unknown.
- **Upstream of the application.** A request that failed at a proxy or front end leaves
  no trace here.
- **Complaint detail.** No product id, time, request id or customer count was given.
- **`lab/server.out`** was not read; the surface contract names `lab/logs/app.log` as
  the log source.
- **Lens coverage.** No lens file exists for load-saturation, third-party or data-db;
  flat durations and memory (E15, E18) and the lab's stated shape (no database, no
  third party) are the only cover for those domains.
- **Usage.** Token totals were not captured.
