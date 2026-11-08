---
konan_journal: 2
investigation:
  id: 2026-11-08-product-page-500s
  trigger: "manual (/konan adapter; complaint object: source human, fingerprint human-1794137139, labels.alertname human-report, no severity stated, startsAt 2026-11-08T11:25:39Z; investigation start 2026-11-08T11:25:46Z — trigger latency 7s)"
  complaint: 'support says customers get "Internal Server Error" on one product page today'
  started: "2026-11-08T11:25:46Z"
  concluded: "2026-11-08T11:39:10Z"
target:
  name: faultline
  surface_contract: docs/rims/grafana-cloud.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/3 fails with HTTP 500 on every request because get_product (shop.py line 64) divides units_ordered by product[\"units_in_stock\"], which is 0 for product 3, and the ZeroDivisionError is not handled."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The service's own code raises an unhandled ZeroDivisionError in get_product (shop.py line 64, turnover_score = units_ordered / product[\"units_in_stock\"]) for product_id 3, whose units_in_stock is 0, so every GET /products/3 returns HTTP 500 while other product ids return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "An internal chaos or degradation switch in the service injects the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E19, E8, E9, E10, E11, E17]
  - id: H3
    statement: "The process crashed or restarted, and the restarts produce the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E8, E15]
  - id: H4
    statement: "A gateway, proxy, or external dependency fails and the service relays the error."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E9, E13, E16, E17]
  - id: H5
    statement: "The stock record of product 3 holds an invalid zero (a corrupt or wrongly written value) rather than a legitimate out-of-stock state, and this bad record is the cause."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E9]
    evidence_against: [E12, E18]
evidence:
  - id: E1
    type: probe
    source: "check_datasources_health, uids grafanacloud-prom and grafanacloud-logs @ 2026-11-08T11:26Z — the rim's two datasources answer; the stack slug in the two names is redacted"
    quote: |-
      {"uid":"grafanacloud-logs","name":"grafanacloud-<stack>-logs","type":"loki","status":"OK","message":"Data source successfully connected."}
      {"uid":"grafanacloud-prom","name":"grafanacloud-<stack>-prom","type":"prometheus","status":"OK","message":"Successfully queried the Prometheus API."}
  - id: E2
    type: metric
    source: "query_prometheus instant, sum by (method, path, status) (http_requests_total), grafanacloud-prom @ 1794137200 = 2026-11-08T11:26:40Z — the process-life request counters; the only non-2xx series is the product page route at 500"
    quote: |-
      {method="GET",path="/metrics",status="200"} 184
      {method="GET",path="/products",status="200"} 3
      {method="GET",path="/health",status="200"} 4
      {method="GET",path="/products/{product_id}",status="200"} 9
      {method="GET",path="/products/{product_id}",status="500"} 13
      {method="POST",path="/orders",status="201"} 6
  - id: E3
    type: metric
    source: "query_prometheus instant, http_exceptions_total, grafanacloud-prom @ 2026-11-08T11:26:41Z — one exception type, equal to the 500 count of E2"
    quote: |-
      http_exceptions_total{instance="127.0.0.1:8000",job="prometheus.scrape.faultline",type="ZeroDivisionError"} 13
  - id: E4
    type: metric
    source: "query_prometheus instant, faultline_chaos_enabled, grafanacloud-prom @ 2026-11-08T11:26:42Z — the degradation switch is off at read time"
    quote: |-
      faultline_chaos_enabled{instance="127.0.0.1:8000",job="prometheus.scrape.faultline"} 0
  - id: E5
    type: metric
    source: "query_prometheus instant, {__name__=~\"process_.*\"}, grafanacloud-prom @ 2026-11-08T11:26:43Z — uptime 94184.6 s puts the process start near 2026-11-07T09:17Z; RSS 46.8 MB"
    quote: |-
      process_max_rss_bytes{instance="127.0.0.1:8000",job="prometheus.scrape.faultline"} 46809088
      process_uptime_seconds{instance="127.0.0.1:8000",job="prometheus.scrape.faultline"} 94184.60360216675
  - id: E6
    type: metric
    source: "query_prometheus range, process_uptime_seconds, now-2h to now, step 60, grafanacloud-prom, read 2026-11-08T11:28Z; and count_over_time(process_uptime_seconds[27h]) instant = 21 — the metric plane holds samples from 11:23:00Z only; uptime rises 60 s per minute across the failure window, no reset"
    quote: |-
      [1794136980,"93959.60914104199"] [1794137040,"94019.60192558262"] [1794137100,"94079.60044829175"] [1794137160,"94139.60029737465"] [1794137220,"94199.59999883268"] [1794137280,"94259.59987737471"]
      count_over_time(process_uptime_seconds[27h]) {instance="127.0.0.1:8000",job="prometheus.scrape.faultline"} 21
  - id: E7
    type: metric
    source: "query_prometheus range, sum by (status) (http_requests_total{path=\"/products/{product_id}\"}) and http_exceptions_total, now-12m to now, step 30, grafanacloud-prom, read 2026-11-08T11:31Z — between the 11:23:30Z and 11:24:00Z samples the route gains 3 × 200 and 4 × 500 and the exception counter gains 4; flat before and after"
    quote: |-
      status="200": [1794136980,"6"] [1794137010,"6"] [1794137040,"9"] then "9" at every sample to [1794137430,"9"]
      status="500": [1794136980,"9"] [1794137010,"9"] [1794137040,"13"] then "13" at every sample to [1794137430,"13"]
      http_exceptions_total{type="ZeroDivisionError"}: [1794136980,"9"] [1794137010,"9"] [1794137040,"13"] then "13" at every sample to [1794137430,"13"]
  - id: E8
    type: log
    source: "query_loki_logs, {job=\"faultline\", event=\"request\"} | json | path=\"/products/3\", now-7d to now, grafanacloud-logs — the four product-3 request lines of 2026-11-08; unstamped request ids (not konan-*), so not the investigator's traffic"
    quote: |-
      {"ts": "2026-11-08T11:23:46.472Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "88fcd2ede11f", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.315, "client": "127.0.0.1:61430"}
      {"ts": "2026-11-08T11:23:47.519Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "cc2b543d7d90", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.308, "client": "127.0.0.1:61431"}
      {"ts": "2026-11-08T11:23:50.610Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "10813d3b025a", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.957, "client": "127.0.0.1:61434"}
      {"ts": "2026-11-08T11:23:52.697Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "cf7b0bcb78b4", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 6.073, "client": "127.0.0.1:61436"}
  - id: E9
    type: log
    source: "query_loki_logs, {job=\"faultline\"}, now-1h to now, grafanacloud-logs, stream event=\"unhandled_exception\" — the four exception lines of 2026-11-08, one per request id of E8; the first line is quoted with its stack trimmed to the first and the throwing frame and with the checkout prefix of its file paths redacted, the other three carry an identical stack and are quoted on their leading fields"
    quote: |-
      {"ts": "2026-11-08T11:23:46.464Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "88fcd2ede11f", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  File \"<checkout>/src/faultline/middleware.py\", line 72, in _handle\n    return await call_next(request)\n ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
      {"ts": "2026-11-08T11:23:47.515Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "cc2b543d7d90", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", ...}
      {"ts": "2026-11-08T11:23:50.606Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "10813d3b025a", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", ...}
      {"ts": "2026-11-08T11:23:52.692Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "cf7b0bcb78b4", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", ...}
  - id: E10
    type: log
    source: "query_loki_logs, {job=\"faultline\"}, now-1h to now, grafanacloud-logs — the other product-route lines of 2026-11-08, interleaved with E8 in the same seconds; products 1 and 2 answer 200"
    quote: |-
      {"ts": "2026-11-08T11:23:40.296Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "f665daf278d1", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.654, "client": "127.0.0.1:61423"}
      {"ts": "2026-11-08T11:23:41.336Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "19bf1514b6fd", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 2.006, "client": "127.0.0.1:61425"}
      {"ts": "2026-11-08T11:23:42.380Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b0ffeb97d763", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.92, "client": "127.0.0.1:61426"}
      {"ts": "2026-11-08T11:23:49.563Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b048089f2b55", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.137, "client": "127.0.0.1:61432"}
  - id: E11
    type: metric
    source: "query_loki_logs instant, sum by (path, status) (count_over_time({job=\"faultline\", event=\"request\"} | json [7d])), grafanacloud-logs @ 2026-11-08T11:28:14Z — seven days of request lines: every /products/3 line is a 500, every other product line a 200"
    quote: |-
      {path="/metrics", status="200"} 174
      {path="/orders", status="201"} 4
      {path="/products", status="200"} 2
      {path="/products/1", status="200"} 2
      {path="/products/2", status="200"} 4
      {path="/products/3", status="500"} 9
  - id: E12
    type: log
    source: "query_loki_logs, {job=\"faultline\", event=\"request\"} | json | path=\"/products/3\", now-7d to now, grafanacloud-logs — the five product-3 lines of 2026-11-04 (four unstamped, one konan-stamped probe of the rim smoke test); the log plane holds no line between 2026-11-04T12:53:16Z and 2026-11-08T11:23:25Z"
    quote: |-
      {"ts": "2026-11-04T12:52:57.252Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "2229d4214c7b", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 14.288, "client": "127.0.0.1:56945"}
      {"ts": "2026-11-04T12:52:58.298Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "915abb560c24", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 6.667, "client": "127.0.0.1:56946"}
      {"ts": "2026-11-04T12:53:01.380Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "6595ef650246", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.593, "client": "127.0.0.1:56948"}
      {"ts": "2026-11-04T12:53:03.483Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "3228b25770b4", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.007, "client": "127.0.0.1:56951"}
      {"ts": "2026-11-04T12:53:03.514Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793796783-57269", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.909, "client": "127.0.0.1:56952"}
  - id: E13
    type: metric
    source: "query_loki_logs instant, sum by (exception_type) (count_over_time({job=\"faultline\", event=\"unhandled_exception\"} | json [7d])), grafanacloud-logs @ 2026-11-08T11:28:15Z — one exception type in seven days, equal to the /products/3 count of E11"
    quote: |-
      {exception_type="ZeroDivisionError"} 9
  - id: E14
    type: log
    source: "query_loki_logs, {job=\"faultline\", event=\"request\"} | json | request_id=~\"konan-.*\", now-7d to now, grafanacloud-logs — the investigator-stamped lines of the plane: two, both of 2026-11-04 (the first is the last line of E12); none today, so today's traffic is not the investigator's"
    quote: |-
      {"ts": "2026-11-04T12:53:16.886Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1793796796-57287", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.616, "client": "127.0.0.1:56957"}
  - id: E15
    type: log
    source: "list_loki_label_values, label event, matcher {job=\"faultline\"}, now-7d to now, grafanacloud-logs — the event types the plane holds; no startup, shutdown, config or deploy marker exists in the plane"
    quote: |-
      ["order_created","request","unhandled_exception"]
  - id: E16
    type: metric
    source: "query_prometheus instant, sum by (path, status) (http_request_duration_seconds_count) and (http_request_duration_seconds_sum), grafanacloud-prom @ 2026-11-08T11:30:47Z — 22 product-page requests took 0.1146 s in total, a mean of 5.2 ms; every route is in milliseconds"
    quote: |-
      count: {path="/health"} 4 | {path="/products"} 3 | {path="/orders"} 6 | {path="/metrics"} 201 | {path="/products/{product_id}"} 22
      sum: {path="/health"} 0.03212329186499119 | {path="/metrics"} 0.46814332669600844 | {path="/products"} 0.006639623548835516 | {path="/products/{product_id}"} 0.1145728756673634 | {path="/orders"} 0.026094832457602024
  - id: E17
    type: metric
    source: "query_prometheus instant, sum by (status) (http_requests_total), grafanacloud-prom @ 2026-11-08T11:30:35Z — the process life knows three statuses; no 502, 503 or 504"
    quote: |-
      {status="200"} 216
      {status="500"} 13
      {status="201"} 6
  - id: E18
    type: log
    source: "query_loki_logs, {job=\"faultline\", event=\"order_created\"}, now-7d to now, grafanacloud-logs — all four order lines of the plane; none names product 3; order ids 3 and 4 are absent against six POST /orders 201 in E2"
    quote: |-
      {"ts": "2026-11-04T12:52:55.197Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "6d302d6f1300", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-04T12:53:02.421Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "9112fe08b424", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"ts": "2026-11-08T11:23:44.425Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "0530a31c227a", "event": "order_created", "order_id": 5, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-08T11:23:51.650Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "3eaebe0f34a7", "event": "order_created", "order_id": 6, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E19
    type: metric
    source: "query_prometheus range, faultline_chaos_enabled, 2026-11-08T11:22:00Z to 11:26:00Z, step 15, grafanacloud-prom, read 11:39Z — the judge's settling check for H2: the switch is 0 at every sample across the failure window 11:23:46Z to 11:23:52Z"
    quote: |-
      [1794136980,"0"] [1794136995,"0"] [1794137010,"0"] [1794137025,"0"] [1794137040,"0"] [1794137055,"0"] [1794137070,"0"] [1794137085,"0"] [1794137100,"0"] [1794137115,"0"] [1794137130,"0"] [1794137145,"0"] [1794137160,"0"]
gaps:
  - "The metric plane holds samples from 2026-11-08T11:23:00Z only (E6: 21 samples in 27 h). The process-life counters (E2, E3, E17) cover about 26 h, but how the 9 route 500s and 9 exceptions before 11:23:00Z (E7) were distributed in time is not observable; no log line ties those 9 to product 3 — they are tied to the product page route and to ZeroDivisionError only."
  - "The log plane holds two windows in seven days, 2026-11-04T12:52:25Z to 12:53:16Z and 2026-11-08T11:23:25Z onward (E11, E12). The current process (start near 2026-11-07T09:17Z per E5) has no startup line in the plane (E15) and no request line before 11:23:25Z today; orders 3 and 4 fall in that gap (E18 against E2). The metric plane and the log plane therefore do not describe the same traffic; log shipping coverage is an operator matter, recorded here and not concluded."
  - "No probe surface exists under this rim. The current answer of GET /products/3, the catalogue value of units_in_stock for product 3, and its seed or last write cannot be read from the plane. H5 (an invalid zero rather than a legitimate out-of-stock state) stays inconclusive for that reason; the decisive evidence is outside the surface contract, so a second round could not buy it."
  - "Prometheus range queries over 12 h and 27 h returned no data through the tool while instant queries returned values; every range entry (E6, E7, E19) uses a window of 2 h or shorter. The empty long ranges are consistent with a plane that holds no sample before 11:23:00Z, but the cause was not determined."
  - "Only the software-defect lens was spawned. The infra-process and interfaces domains were excluded from baseline evidence (E4, E19, E5, E6, E15, E16, E17) and not swept independently; a latent signal in those domains outside what those entries cover was not examined."
  - "User-vs-investigator attribution rests on the request-id convention of the surface contract: today's product-3 requests carry unstamped ids from 127.0.0.1 (E8) and the plane holds no konan-stamped line today (E14), so they are read as user traffic or the eval-side staging; whether they were real customers cannot be verified from the plane."
  - "The complaint says 'today'; the plane shows the same failure on 2026-11-04 (E12), so the defect predates today. The first user-visible failure of today in the plane is 11:23:46Z (E8); user traffic earlier today, if any, is outside the log plane (gap 2)."
usage:
  model: claude-fable-5-1
  tokens: null
  wall_clock_seconds: 804
---

# Product page 3 returns HTTP 500 on every request — unhandled ZeroDivisionError in get_product

## Summary

Root cause identified. `GET /products/3` fails deterministically with HTTP 500: the
handler `get_product` (shop.py line 64) computes `units_ordered / product["units_in_stock"]`,
the stock of product 3 is 0, and the resulting `ZeroDivisionError` is not handled (E9).
Every product-3 request in the plane is a 500 — four today at 11:23:46Z to 11:23:52Z (E8)
and five on 2026-11-04 (E12) — while products 1 and 2 answer 200 in the same seconds (E10)
and no other route carries a 5xx (E2, E17). The exception counter and the route's 500
counter stand at 13 and 13 in the current process life and stepped 9 to 13 together in
the 11:23:30Z–11:24:00Z sample (E3, E7). Impact: the one product page is unusable for
every visitor; the other pages, the catalogue list and ordering are unaffected (E10, E18).
The chaos switch was off across the failure window (E19), the process has been up for
about 26 hours without a reset (E5, E6), and latency is in milliseconds (E16). Confidence
is high on the mechanism; whether the zero stock is a legitimate out-of-stock state or a
bad record (H5) cannot be settled from this rim, which has no probe surface. The defect
is not new today: the plane shows it on 2026-11-04.

## Timeline

All times UTC, from plane timestamps.

- 2026-11-04 12:52:57Z–12:53:03Z — five `GET /products/3 -> 500` lines, four unstamped and
  one investigator probe of the rim smoke test (E12). Products 1 and 2 answered 200 in the
  same minute and orders 1 and 2 were created (E18). The defect already exists.
- 2026-11-04 12:53:16Z → 2026-11-08 11:23:25Z — no log line in the plane (E12). The
  current process started near 2026-11-07 09:17Z (E5); its startup is not in the plane (E15).
- 2026-11-08 11:23:00Z — first metric sample of the plane: route 500 counter 9, exception
  counter 9, uptime 93959.6 s, chaos 0 (E6, E7, E19).
- 2026-11-08 11:23:40Z–11:23:52Z — a burst of unstamped traffic: `GET /products` 200,
  `GET /products/1` 200, `GET /products/2` 200 twice, two `POST /orders` 201 (E10, E18), and
  four `GET /products/3 -> 500` at 11:23:46.472Z, 11:23:47.519Z, 11:23:50.610Z,
  11:23:52.697Z (E8), each paired with an `unhandled_exception` ZeroDivisionError line of
  the same request id (E9).
- 2026-11-08 11:24:00Z — the counters show the burst: route 200s 6→9, route 500s 9→13,
  ZeroDivisionError 9→13 (E7). Chaos 0 at every 15 s sample through 11:26:00Z (E19).
- 2026-11-08 11:25:39Z — complaint raised (startsAt); 11:25:46Z investigation start.
- 2026-11-08 11:24:00Z–11:30:30Z — counters flat at 9 and 13 (E7); only `/metrics` scrapes
  in the log tail.

## Investigation

**Trigger.** Complaint object, verbatim: `{"source": "human", "fingerprint":
"human-1794137139", "labels": {"alertname": "human-report"}, "annotations": {"summary":
"support says customers get \"Internal Server Error\" on one product page today"},
"startsAt": "2026-11-08T11:25:39Z"}`. Investigation start 2026-11-08T11:25:46Z; trigger
latency 7 s. No severity was stated, none inferred.

**Setup.** `KONAN_RIM=docs/rims/grafana-cloud.md`: the surface is the Grafana Cloud rim,
read through the `mcp-grafana` tools on `grafanacloud-prom` and `grafanacloud-logs` (E1).
The lab's files and the probe script were out of bounds and not touched. Budget: one
triage round, at most 3 deep-dive agents per round, at most 2 rounds.

**Baseline (11:26Z–11:31Z).** Both datasources healthy (E1). Process-life counters: 13
route 500s against 9 route 200s, 13 ZeroDivisionError exceptions, chaos 0, uptime 94184.6 s,
RSS 46.8 MB (E2–E5). Data horizon: metric samples from 11:23:00Z only (E6); log lines in
two windows, 2026-11-04 and today from 11:23:25Z (E11, E12). Log tail: `/metrics` 200 every
15 s. Seven-day counts: every `/products/3` line a 500, every other product line a 200,
nine ZeroDivisionError lines (E11, E13). Two investigator-stamped lines in the plane, both
of 2026-11-04 (E14). Statuses in the process life: 200, 201, 500 only (E17). Mean request
duration 5.2 ms on the product page route (E16).

**Triage.** One lens spawned, software-defect, blind to this narrative, with the lens
file, the surface contract, the complaint verbatim and the baseline summary. It returned
three findings: the deterministic per-input 500 on `/products/3` with the paired
ZeroDivisionError at shop.py line 64 (E8, E9, E12); the data-dependent shape, products 1
and 2 at 200 in the same seconds and no 5xx elsewhere (E10, E2); and the lockstep of the
exception and 500 counters with 9 failures before the first plane sample (E7), plus the
absence of any order naming product 3 (E18). The infra-process and interfaces lenses were
not spawned: their domains were excluded with baseline evidence — chaos 0 (E4), no uptime
reset (E5, E6), no lifecycle or change marker in the plane (E15), millisecond latency
(E16), no gateway-shaped status (E17), and a failure that is per-input, not probabilistic
(E10, E11). This is recorded as gap 5.

**Hypotheses formed.** H1 unhandled exception in the target's own code; H2 degradation
switch; H3 process restart; H4 gateway or dependency failure; H5 invalid stock record.

**Deep-dive.** Skipped. H1's triage evidence is deterministic and complete (request-id
pairing, stack naming the operation, counter lockstep); H2–H4 are contradicted by
baseline entries; H5's decisive evidence is outside the surface contract.

**Judge.** A fresh agent received the five hypotheses with the verbatim evidence ledger
E1–E18 and no narrative. Verdicts: H1 validated; H2 invalidated, with the note that E4 is
an instant read three minutes after the last failure, settled by a range of
`faultline_chaos_enabled` across 11:23:30Z–11:24:00Z; H3 invalidated; H4 invalidated;
H5 inconclusive, settled only by the seed or last write of product 3's stock next to the
value the catalogue returns now. The judge also flagged that the metric plane and the log
plane do not describe the same traffic (gap 2). The settling query for H2 was run (E19):
0 at every 15 s sample from 11:23:00Z to 11:26:00Z. H5's settling evidence is not
reachable under this rim; no second round was opened.

## Hypotheses

### H1 — unhandled ZeroDivisionError in get_product for product 3 (software-defect) — validated

For: each of the four product-3 requests of today (E8) has an ERROR line with the same
request id, `exception_type` ZeroDivisionError and a stack that ends at shop.py line 64,
`"turnover_score": units_ordered / product["units_in_stock"]` (E9). Products 1 and 2
answered 200 between those failures (E10). The route's 500 counter and the exception
counter moved 9→13 in the same sample and stand equal (E7, E3, E2). Over seven days every
`/products/3` line is a 500 and the only exception type is ZeroDivisionError, 9 and 9
(E11, E13); the same failure is on record on 2026-11-04 (E12). Against: none. Cause id
`unhandled-exception`: the target's own code raises on one input and the request fails.

### H2 — internal degradation switch injects the 500s (infra-process) — invalidated

Against: the switch reads 0 at every 15 s sample across the failure window (E19) and at
read time (E4); the failures follow one rule, 9 of 9 on `/products/3` and none on any other
path (E11), only statuses 200, 201 and 500 exist (E17), and each 500 comes from one
arithmetic line in the handler (E9), not an injection point; products 1 and 2 succeed in
the same seconds (E10, E8). For: none.

### H3 — process crash or restart produces the errors (infra-process) — invalidated

Against: uptime rises 60 s per minute across the failure window with no reset (E6), 94184.6 s
at read time (E5); the failed requests were answered in 5–8 ms, not refused (E8). The
plane holds no lifecycle event (E15), which on its own is weak evidence, since a process
that logs no startup looks the same. For: none.

### H4 — gateway, proxy or external dependency failure (interfaces) — invalidated

Against: no 502, 503 or 504 in the process life (E17); ZeroDivisionError is the only
exception type (E3, E13); the stack raises at a local division, not inside a client or
driver call (E9); mean duration 5.2 ms on the route (E16). For: none.

### H5 — an invalid zero in product 3's stock record, not a legitimate out-of-stock state (data-db) — inconclusive

For: the divisor is zero (E9). Against: nothing shows a write to product 3's stock; no order
names product 3 (E18), and the failure already existed on 2026-11-04 (E12), before every
visible order and across the restart near 2026-11-07T09:17Z (E5). E18 does not exclude a
write either: order ids 3 and 4 fall in the log gap (E18 against E2). Zero stock is a legal
state for a shop, so E9 proves the value, not its validity. Settling evidence: the seed or
last write of `units_in_stock` for product 3 next to the catalogue's current value —
outside this rim's surface (gap 3). Whatever the answer, the mechanism of the 500 stays H1:
the handler divides by a stock value that can be zero.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Read the catalogue's current value of `units_in_stock` for product 3 and its seed or last
  write, through a surface that allows it (the lab rim's probe of `GET /products`, or the
  owning team's data view). This settles H5 without changing anything.
- Keep the log shipping continuous. The plane missed the current process's first 26 hours
  (gap 2); with the tail running, the next failure is tied to its input by a request line.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` next to
  `http_requests_total{path="/products/{product_id}",status="500"}`; as long as they step
  together, every product-page 500 is this defect.
- Count user impact from unstamped `GET /products/3` lines only; the one konan-stamped hit
  (E12) is the rim smoke test of 2026-11-04.

## Gaps

1. **Metric horizon.** Samples exist from 11:23:00Z only (E6). The 9 route 500s and 9
   exceptions before that (E7) are in the process-life counters but have no time
   distribution and no log line; they are tied to the product page route and to
   ZeroDivisionError, not to product 3 by any quote.
2. **Log horizon.** Two windows in seven days (E11, E12). No startup line for the current
   process (E15), no request line before 11:23:25Z today, orders 3 and 4 absent (E18 against
   E2). The metric plane and the log plane describe different spans of the same process.
3. **No probe surface.** The current answer of `GET /products/3` and the stock value of
   product 3 cannot be read under this rim; H5 stays inconclusive.
4. **Long range queries empty.** Ranges of 12 h and 27 h returned no data through the tool
   while instant queries answered; every range entry here is 2 h or shorter. Consistent with
   a plane that starts at 11:23:00Z; the cause was not determined.
5. **Lens coverage.** Only the software-defect lens was spawned; the other two domains were
   excluded from baseline evidence, not swept independently.
6. **Attribution.** Today's traffic is unstamped and from 127.0.0.1 (E8, E14); it is read as
   user traffic or the eval-side staging by the surface contract's convention. "Customers"
   cannot be verified from the plane.
7. **"Today".** The defect predates the complaint (E12). The first user-visible failure of
   today in the plane is 11:23:46Z (E8); earlier traffic today, if any, is outside the plane.
