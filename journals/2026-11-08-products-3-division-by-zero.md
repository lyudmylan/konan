---
konan_journal: 2
investigation:
  id: 2026-11-08-products-3-division-by-zero
  trigger: "manual: /konan adapter, profile human. Complaint object: source human; fingerprint human-1794146815; labels.alertname human-report (no severity stated by the reporter); annotations.summary = the complaint below, verbatim; startsAt 2026-11-08T14:06:55Z. Investigation start 2026-11-08T14:07:04Z; trigger latency 9 s."
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: "2026-11-08T14:07:04Z"
  concluded: "2026-11-08T14:22:12Z"
target:
  name: faultline
  surface_contract: docs/adapters/grafana-cloud.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler get_product divides units_ordered by product[\"units_in_stock\"] with no guard for a zero divisor; product 3 holds units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and answers 500, while the other product ids on the same route answer 200."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "get_product computes turnover_score as units_ordered / product[\"units_in_stock\"] without a zero guard; product 3 has units_in_stock 0, so each GET /products/3 raises ZeroDivisionError and fails with 500, deterministically per input, across process lifetimes."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E16, E17]
    evidence_against: []
  - id: H2
    statement: "The process restart at 14:03:35Z (old process gone without a shutdown line, new process 2946) introduced the failure, for example by starting a different build or by losing state."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E10, E11, E12]
    evidence_against: [E4, E5, E8, E9, E17]
  - id: H3
    statement: "An internal chaos or degradation switch injects the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E5, E13, E21]
  - id: H4
    statement: "The stock record of product 3 is wrong (corrupt, or depleted to zero by orders), and the wrong data rather than the code is the cause."
    incident_class: data-db
    state: invalidated
    evidence_for: [E2]
    evidence_against: [E1, E9, E16, E17]
evidence:
  - id: E1
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\"} | json | status=~\"5..\", now-2h to now (now = 2026-11-08T14:07:45Z); line ts 2026-11-08T14:05:23.792Z"
    quote: |-
      {"ts": "2026-11-08T14:05:23.792Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "10c3bf72f201", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 13.821, "client": "127.0.0.1:63806"}
  - id: E2
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\"}, now-15m to now (now = 2026-11-08T14:07:45Z); line ts 2026-11-08T14:05:23.778Z; framework frames of the stack trimmed as [...]; local checkout path prefix redacted as <checkout>"
    quote: |-
      {"ts": "2026-11-08T14:05:23.778Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "10c3bf72f201", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  File \"<checkout>/faultline/src/faultline/middleware.py\", line 72, in _handle\n    return await call_next(request)\n [...] \n  File \"<checkout>/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E3
    type: log
    source: "query_loki_logs instant, datasource grafanacloud-logs, sum by (path, status) (count_over_time({job=\"faultline\"} | json | event=\"request\" [6h])), evaluated at 1794146921.068 (2026-11-08T14:08:41Z)"
    quote: |-
      {"path":"/health","status":"200"} 4; {"path":"/metrics","status":"200"} 656; {"path":"/orders","status":"201"} 4; {"path":"/products","status":"200"} 2; {"path":"/products/1","status":"200"} 2; {"path":"/products/2","status":"200"} 4; {"path":"/products/3","status":"500"} 8
  - id: E4
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\"} | json | path=\"/products/3\", now-12h to now (now = 2026-11-08T14:08:41Z), forward; 8 lines returned, all \"GET /products/3 -> 500\", ts 11:23:46.472Z, 11:23:47.519Z, 11:23:50.610Z, 11:23:52.697Z, 14:05:23.792Z, 14:05:24.846Z, 14:05:27.932Z, 14:05:30.018Z; the first quoted"
    quote: |-
      {"ts": "2026-11-08T11:23:46.472Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "88fcd2ede11f", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.315, "client": "127.0.0.1:61430"}
  - id: E5
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\", level=~\"ERROR|WARNING|CRITICAL\"}, now-12h to now (now = 2026-11-08T14:08:41Z), forward; line ts 2026-11-08T11:23:46.464Z; framework frames trimmed as [...]; local checkout path prefix redacted as <checkout>"
    quote: |-
      {"ts": "2026-11-08T11:23:46.464Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "88fcd2ede11f", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  File \"<checkout>/faultline/src/faultline/middleware.py\", line 72, in _handle\n [...] \n  File \"<checkout>/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E6
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\", event=\"request\"} | json | path!=\"/metrics\", now-12h to now (now = 2026-11-08T14:10:08Z), forward; line ts 2026-11-08T14:05:26.889Z"
    quote: |-
      {"ts": "2026-11-08T14:05:26.889Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "66086b39bd6f", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.019, "client": "127.0.0.1:63809"}
  - id: E7
    type: log
    source: "same query as E6; line ts 2026-11-08T14:05:18.629Z"
    quote: |-
      {"ts": "2026-11-08T14:05:18.629Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "17b341d17dd0", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.762, "client": "127.0.0.1:63801"}
  - id: E8
    type: metric
    source: "query_prometheus range, datasource grafanacloud-prom, http_exceptions_total, now-3h to now (now = 2026-11-08T14:07:42Z), step 60 s; the only series returned; the samples between 11:25:00Z and 14:05:00Z, all \"13\", trimmed as ..."
    quote: |-
      {"__name__":"http_exceptions_total","instance":"127.0.0.1:8000","job":"prometheus.scrape.faultline","type":"ZeroDivisionError"} values: [1794136980,"9"],[1794137040,"13"],[1794137100,"13"], ... ,[1794146700,"13"],[1794146760,"4"],[1794146820,"4"],[1794146880,"4"]
  - id: E9
    type: metric
    source: "query_prometheus instant, datasource grafanacloud-prom, sum by (path, status) (http_requests_total{path=~\"/products.*\"}), evaluated at 2026-11-08T11:23:00Z (1794136980)"
    quote: |-
      {"path":"/products","status":"200"} [1794136980,"2"]; {"path":"/products/{product_id}","status":"200"} [1794136980,"6"]; {"path":"/products/{product_id}","status":"500"} [1794136980,"9"]
  - id: E10
    type: metric
    source: "query_prometheus range, datasource grafanacloud-prom, process_uptime_seconds, now-3h to now (now = 2026-11-08T14:10:08Z), step 60 s; samples between 11:24Z and 14:03Z (climbing by 60 s per step) trimmed as ..."
    quote: |-
      {"__name__":"process_uptime_seconds","instance":"127.0.0.1:8000","job":"prometheus.scrape.faultline"} values: [1794136980,"93959.60914104199"], ... ,[1794146580,"103559.6015519579"],[1794146640,"103574.60110979201"],[1794146700,"103574.60110979201"],[1794146760,"140.05989241600037"],[1794146820,"200.05343079101294"]
  - id: E11
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\", event=\"startup\"}, now-12h to now (now = 2026-11-08T14:08:41Z); the only line; Loki entry timestamp 1794146699020757000 (14:04:59.02Z)"
    quote: |-
      {"ts": "2026-11-08T14:03:35.281Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E12
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\"} != \"faultline.request\" != \"faultline.shop\", now-12h to now (now = 2026-11-08T14:10:08Z); 5 lines returned, all with ts 14:03:35.280Z or 14:03:35.281Z (Started server process, Waiting for application startup, Application startup complete, Uvicorn running, faultline 0.1.0 started); no shutdown, exit, or signal line; the first quoted"
    quote: |-
      {"ts": "2026-11-08T14:03:35.280Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [2946]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
  - id: E13
    type: metric
    source: "query_prometheus range, datasource grafanacloud-prom, faultline_chaos_enabled, now-3h to now (now = 2026-11-08T14:07:42Z), step 300 s; 33 samples"
    quote: |-
      {"__name__":"faultline_chaos_enabled","instance":"127.0.0.1:8000","job":"prometheus.scrape.faultline"} value "0" at every sample from [1794137100,"0"] through [1794146700,"0"]
  - id: E14
    type: metric
    source: "query_prometheus range, datasource grafanacloud-prom, process_max_rss_bytes, now-3h to now (now = 2026-11-08T14:10:08Z), step 300 s"
    quote: |-
      {"__name__":"process_max_rss_bytes","instance":"127.0.0.1:8000","job":"prometheus.scrape.faultline"} value "46809088" at every sample from [1794137100] through [1794146700]; [1794147000,"46759936"]
  - id: E15
    type: metric
    source: "query_prometheus instant, datasource grafanacloud-prom, sum by (path) (increase(http_request_duration_seconds_sum[6h])) / sum by (path) (increase(http_request_duration_seconds_count[6h])), evaluated at 1794147008.019 (2026-11-08T14:10:08Z); seconds"
    quote: |-
      {"path":"/health"} 0.0029158538673073053; {"path":"/metrics"} 0.0021215367695373117; {"path":"/products"} 0.0018228748813271523; {"path":"/products/{product_id}"} 0.004391258981611047; {"path":"/orders"} 0.002312989323399961
  - id: E16
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\", event=\"order_created\"}, now-12h to now (now = 2026-11-08T14:10:08Z), forward; all 4 lines"
    quote: |-
      {"ts": "2026-11-08T11:23:44.425Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "0530a31c227a", "event": "order_created", "order_id": 5, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-08T11:23:51.650Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "3eaebe0f34a7", "event": "order_created", "order_id": 6, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"ts": "2026-11-08T14:05:21.725Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "9bfacd460e29", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-08T14:05:28.973Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "fc3702dca144", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E17
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\", level=~\"ERROR|WARNING|CRITICAL\"}, now-12h to now (now = 2026-11-08T14:08:41Z); response metadata quoted; all 8 lines are in the stream {event=\"unhandled_exception\", level=\"ERROR\"} with \"exception_type\": \"ZeroDivisionError\", ts 11:23:46.464Z, 11:23:47.515Z, 11:23:50.606Z, 11:23:52.692Z, 14:05:23.778Z, 14:05:24.840Z, 14:05:27.929Z, 14:05:30.014Z, request_id 88fcd2ede11f, cc2b543d7d90, 10813d3b025a, cf7b0bcb78b4, 10c3bf72f201, 3848d702f204, 4b581ff42d23, a2f6b894390f"
    quote: |-
      "linesReturned":8,"maxLinesAllowed":50,"resultsTruncated":false,"totalLinesScanned":8
  - id: E18
    type: log
    source: "query_loki_logs, datasource grafanacloud-logs, {job=\"faultline\", event=\"request\"} | json | path=\"/metrics\", 2026-11-08T14:02:30Z to 14:05:30Z, forward; 5 lines, ts 14:02:40.097Z, 14:02:55.095Z, 14:03:10.095Z, 14:05:10.332Z, 14:05:25.321Z; the two around the gap quoted"
    quote: |-
      {"ts": "2026-11-08T14:03:10.095Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "2fedadd0e86c", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 3.862, "client": "127.0.0.1:63756"}
      {"ts": "2026-11-08T14:05:10.332Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "c401ad76b8a1", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 4.024, "client": "127.0.0.1:63797"}
  - id: E19
    type: log
    source: "same query as E6; Loki entry timestamps 1794146699022850000 and 1794146699023069000 (both 2026-11-08T14:04:59.02Z) against line ts 14:03:35.933Z and 14:04:43.286Z"
    quote: |-
      {"ts": "2026-11-08T14:03:35.933Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "e44fe3ec3df0", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 6.701, "client": "127.0.0.1:63768"}
      {"ts": "2026-11-08T14:04:43.286Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "d3c006260526", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.561, "client": "127.0.0.1:63785"}
  - id: E20
    type: metric
    source: "query_prometheus range, datasource grafanacloud-prom, up{job=\"prometheus.scrape.faultline\"}, now-3h to now (now = 2026-11-08T14:08:41Z), step 60 s"
    quote: |-
      {"__name__":"up","instance":"127.0.0.1:8000","job":"prometheus.scrape.faultline"} value "1" at every sample from [1794136980] through [1794146880]
  - id: E21
    type: metric
    source: "query_prometheus range, datasource grafanacloud-prom, faultline_chaos_enabled, 2026-11-08T14:05:00Z to 14:06:00Z, step 15 s; samples from the new process 2946 (its scrapes at 14:05:10.332Z and 14:05:25.321Z, E18)"
    quote: |-
      {"__name__":"faultline_chaos_enabled","instance":"127.0.0.1:8000","job":"prometheus.scrape.faultline"} values: [1794146700,"0"],[1794146715,"0"],[1794146730,"0"],[1794146745,"0"],[1794146760,"0"]
gaps:
  - "Nine exceptions and nine 500s on the product route precede the plane's first sample at 11:23:00Z (E8, E9) and have no log lines in the plane; the metric carries only the route template, so they are not shown to be /products/3."
  - "The value and the origin of units_in_stock for product 3 cannot be read on this surface: no probe is sent under this adapter and the data store is out of reach. Whether 0 is the intended stock is unknown; the mechanism of H1 holds for any zero."
  - "The version of the process that ran before 14:03:35Z is unknown: its startup line predates the plane window. 'No deploys that we know of' can be neither confirmed nor refuted from the plane; H2 is invalidated on other grounds."
  - "The cause of the restart at 14:03:35Z is unknown: no shutdown, exit, or signal line in 12 h (E12). The collector paused at the same time (E18, E19), so metric samples between 14:03:10Z and 14:05:10Z are carry-forward, not measurements (E10 flat at 14:04Z and 14:05Z, E20)."
  - "The interfaces lens was not spawned. Excluded on evidence: no gateway-shaped status in 6 h (E3), a deterministic per-input shape (E3, E6, E7), and a stack that shows no dependency call (E2). A blind spot accepted on that evidence."
  - "No deep-dive round was run: H1's triage evidence was deterministic and complete; H2 and H3 were refuted by baseline data; H4's decisive test (the product-3 record) is off this surface. One targeted query (E21) answered the judge's single open item."
  - "The plane cannot separate real customers from staged traffic; all 8 failures are non-investigator traffic, since no probe is sent under this adapter."
  - "usage.tokens is null: interactive session; the orchestrator's total was not exposed. The three subagents reported 77185, 86160, and 48978 tokens."
usage:
  model: claude-fable-5-1
  tokens: 3269531
  wall_clock_seconds: 908
---

# GET /products/3 answers 500: unguarded division by units_in_stock in get_product

## Summary

Root cause identified. The product-detail handler divides `units_ordered` by the product's `units_in_stock` to compute a turnover score and has no guard for a zero divisor. Product 3 holds a stock of zero, so every request for `/products/3` raises `ZeroDivisionError` in the target's own code and answers 500; products 1 and 2 on the same route answer 200 in the same minute. The plane shows 8 of 8 requests for product 3 failing in 6 h (E3), each paired by request id with one `ZeroDivisionError` from the same line (E1, E2, E4, E5, E17), and no failure on any other path. The failure survived the process restart at 14:03:35Z unchanged, so it is not transient state. Impact in the plane: 8 failed page loads in 6 h, all for product 3, including four refreshes within 7 s at 14:05Z; other pages were unaffected. Confidence is high: deterministic per-input failure, the throwing line named by the stack, the exception counter matching the 500 count one to one, and the judge validated H1 and invalidated the three alternatives.

Two statements of the complaint do not match the plane. "Started within the last hour": the same failure occurred at 11:23:46Z (E4, E5), and nine more failures sit before the plane's first sample (E8, E9). "No deploys that we know of": the process did restart at 14:03:35Z (E10, E11, E12), but the failure predates the restart, so the restart is not the cause.

## Timeline

All times UTC, 2026-11-08, from plane timestamps.

- Before 11:23:00Z: the plane's first samples already hold 9 `ZeroDivisionError` exceptions and 9 × 500 against 6 × 200 on the product route (E8, E9). The previous process had been up about 26 h at that point (E10).
- 11:23:40Z to 11:23:52Z: first burst in the plane. Four `GET /products/3` answer 500, each with a `ZeroDivisionError` at `shop.py` line 64 in `get_product` (E4, E5, E17); products 1 and 2 answer 200; orders 5 and 6 are created for products 1 and 2 (E16). The exception counter goes from 9 to 13 (E8).
- 11:24Z to 14:03Z: the counter stays at 13 (E8), the chaos gauge stays 0 (E13), the memory gauge is flat (E14), only scrapes and two health checks are served.
- 14:03:10Z: last scrape served by the old process (E18).
- 14:03:35Z: a new server process 2946 starts, version 0.1.0 (E11, E12); the old process left no shutdown line (E12); uptime resets (E10).
- 14:03:10Z to 14:05:10Z: no scrape and no log shipping; the new process served `/health` at 14:03:35.933Z and 14:04:43.286Z, and those lines reached Loki at 14:04:59Z (E18, E19).
- 14:05:17Z to 14:05:30Z: second burst, the same sequence. Four `GET /products/3` answer 500 with the identical exception (E1, E2, E17); products 1 and 2 answer 200 (E6, E7); orders 1 and 2 are created for products 1 and 2 (E16); the chaos gauge reads 0 from the new process (E21). The counter reads 4 after the reset (E8).
- 14:06:55Z: the complaint is raised. 14:07:04Z: investigation start. 14:22:12Z: concluded.

## Investigation

Baseline (orchestrator, Grafana MCP tools only): datasource health, request and exception counters for the last 2 h and 6 h, chaos and process gauges over 3 h, the 5xx lines over 2 h, the recent tail, the full non-scrape request history over 12 h, order lines, lifecycle lines, and latency per path. The baseline already showed one deterministic failure on one input, a restart two minutes before the second burst, and the same failure before the restart.

Triage: two lenses spawned in parallel, blind to each other, each given the lens file, the surface contract, the complaint verbatim, and the baseline summary.

- software-defect: three findings. The deterministic data-dependent defect at `shop.py` line 64; the spread (one route, one exception type, survived the restart, counter one to one with the 500s); and the age of the defect (already 9 failures before the plane window).
- infra-process: three findings. One restart at 14:03:35Z with no shutdown marker and not a loop, which neither caused nor cleared the symptom; the collector paused with the application from 14:03:10Z to 14:05:10Z, so `up=1` in that window is carry-forward; no saturation, no latency degradation, no chaos switch.
- interfaces: not spawned; excluded on evidence (see Gaps).

Hypotheses formed: H1 to H4 above. Deep-dive: none spawned. H1's triage evidence was deterministic and complete; H2 and H3 were already contradicted by baseline data; H4's decisive test is off this surface.

Judge: one fresh subagent received only the hypothesis list and the evidence ledger E1 to E20, with no lens reasoning. Verdicts: H1 validated; H2 invalidated (failures 2 h 40 min before the restart, same line, same expression); H3 invalidated (8 of 8 on one input and 0 of 672 elsewhere is not an injector's shape; the exception is raised in the application handler, not in middleware); H4 invalidated (no order for product 3 in 12 h; the store re-initialised at the restart and the fresh process still failed 108 s after startup, before any order for product 3; the exception only shows the divisor was zero and does not favour data over code). The judge named one open item for H3, a chaos sample from the new process inside the burst; one targeted query answered it (E21, all 0).

Subagent usage: 77185, 86160, and 48978 tokens; the orchestrator's own total was not exposed.

## Hypotheses

### H1: unguarded division by units_in_stock in get_product (software-defect, unhandled-exception). Validated.

For: the stack names the line and the expression (E2, E5); the request ids tie each exception to a `GET /products/3` 500 (E1 with E2, E4 with E5); all eight 500s in 6 h are on `/products/3` and all eight ERROR lines are this exception (E3, E17); products 1 and 2 answer 200 in the same minute (E6, E7); the exception counter rises by exactly the number of 500s and reads 4 for the four post-restart failures (E8); the failure is identical in the old process and in the new one (E4, E1, E8); the order ids restart at 1 after the restart (E16), so the zero stock is present in freshly initialised state before any order. Nine earlier failures on the route agree with the pattern (E9). Against: none.

### H2: the 14:03:35Z restart introduced the failure (infra-process). Invalidated.

For: a restart did happen (E10, E11, E12). Against: the same exception from the same line at 11:23:46Z, before the restart (E4, E5, E17); 13 exceptions and 9 earlier 500s in the old process (E8, E9). The restart explains the counter drop from 13 to 4, nothing more. Its own cause and the old process's version are not in the plane (Gaps).

### H3: a chaos or degradation switch injects the 500s (infra-process). Invalidated.

For: none. Against: the failure shape is 8 of 8 on one input and 0 of 672 on the other paths (E3), not a probabilistic spread; the exception is raised in the application handler after the middleware frame (E2, E5); the chaos gauge reads 0 at every sample over 3 h (E13) and at every 15 s sample from the new process across the 14:05Z burst (E21).

### H4: wrong stock data for product 3 is the cause (data-db). Invalidated.

For: the divisor was zero (E2). Against: no order for product 3 in 12 h (E16); the fresh process failed 108 s after startup, before any order for product 3 (E1, E16); the exception is identical in both bursts, so the value did not change (E17); the pre-window failures show the state predates everything in the plane (E9). A zero stock is a reachable state for any product, and the handler fails on any zero; whether this zero is the intended value is a gap, not a cause.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Read the product-3 record, or the `GET /products` listing, to learn the stored `units_in_stock` and whether zero is intended.
- Review `get_product` at the stack's line for the behaviour on a zero stock, and check which other products can reach zero stock through orders, since the same path would then fail for them.
- Look in the operator's records for the cause of the 14:03:35Z restart and for the version of the previous process; the plane holds no shutdown line and no earlier startup line.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the 500 count on `/products/{product_id}` for further failures.

## Gaps

- The nine exceptions before 11:23:00Z (E8, E9) have no log lines in the plane; the metric carries only the route template, so they are not shown to be `/products/3`, though they agree with the pattern.
- The value and origin of `units_in_stock` for product 3 cannot be read on this surface: no probe is sent under this adapter and the data store is out of reach. The mechanism of H1 holds for any zero.
- The previous process's version is unknown: its startup line predates the plane window. "No deploys that we know of" can be neither confirmed nor refuted from the plane.
- The cause of the 14:03:35Z restart is unknown: no shutdown, exit, or signal line in 12 h (E12). The collector paused with the application (E18, E19), so metric samples between 14:03:10Z and 14:05:10Z are carry-forward (E10 flat at 14:04Z and 14:05Z, E20).
- The interfaces lens was not spawned, on the evidence of E3, E6, E7, and E2; a blind spot accepted on that evidence.
- No deep-dive round was run, for the reasons in the Investigation section.
- The plane cannot separate real customers from staged traffic; all eight failures are non-investigator traffic, since no probe is sent under this adapter.
- `usage.tokens` is null: interactive session; the orchestrator's total was not exposed.
