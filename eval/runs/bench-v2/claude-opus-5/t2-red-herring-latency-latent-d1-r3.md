---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-wide-latency
  trigger: >-
    manual — /konan human report. Complaint object: source human; fingerprint
    human-1793692685; labels.alertname human-report (no severity stated by the
    reporter, none inferred); startsAt 2026-11-03T07:58:05Z. Investigation
    started 2026-11-03T07:58:15Z — trigger latency 10 s.
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-03T07:58:15Z
  concluded: 2026-11-03T08:08:20Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: >-
    An operational degradation switch inside the target was enabled at
    07:57:51.563Z with extra_latency_ms 1500 and is still on; while on it adds a
    variable per-request delay, bounded by that value, to every business route,
    which is the shop-wide slowness. The two monitoring routes were not delayed,
    so the health check stayed green throughout.
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: >-
      A degradation switch inside the target, enabled at 07:57:51.563Z with
      extra_latency_ms 1500, injects a variable per-request delay into the
      business routes while it stays on; the monitoring routes were not delayed.
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16]
    evidence_against: []
  - id: H2
    statement: >-
      Demand exceeded capacity: queueing or resource exhaustion under volume
      caused the slowness.
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E12, E17]
  - id: H3
    statement: >-
      A defect in the target's own code caused the shop-wide slowness.
    incident_class: software-defect
    state: invalidated
    evidence_for: [E19, E20]
    evidence_against: [E6, E9, E10, E17, E23]
  - id: H4
    statement: >-
      The degradation switch was also injecting its configured error status
      (503), and that is the error page the reporters saw.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E16, E17, E23]
  - id: H5
    statement: >-
      The ZeroDivisionError on the zero-stock product detail page is what the
      reporters saw as an error page.
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E19, E20, E21]
    evidence_against: [E17, E23]
latent_findings:
  - statement: >-
      GET /products/{id} divides by the product's units_in_stock without a zero
      guard, so the zero-stock product (id 3) returns 500 deterministically.
      That product is in the public catalogue listing, so the page is reachable
      by any user right now; in this process lifetime only investigator probes
      are recorded as having hit it. Mechanism-backed by the stack trace, not
      generalized from repetition — id 3 is the only zero-stock row available to
      test.
    evidence: [E19, E20, E21, E22, E23]
evidence:
  - id: E1
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:45.459Z (first line of the file; lab/logs/ holds no rotated backups)
    quote: '{"ts": "2026-11-03T07:57:45.459Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [23653]"}'
  - id: E2
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:46.403Z (pre-switch, non-investigator)
    quote: '{"ts": "2026-11-03T07:57:46.403Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "23347abd697d", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.304, "client": "127.0.0.1:64958"}'
  - id: E3
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:47.463Z (pre-switch, non-investigator)
    quote: '{"ts": "2026-11-03T07:57:47.463Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "86845fcebe01", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.276, "client": "127.0.0.1:64959"}'
  - id: E4
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:48.515Z (pre-switch, non-investigator)
    quote: '{"ts": "2026-11-03T07:57:48.515Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "155eb89936d1", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.599, "client": "127.0.0.1:64960"}'
  - id: E5
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:51.563Z (the configuration-change marker; non-investigator request id)
    quote: '{"ts": "2026-11-03T07:57:51.563Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "90cf1be38619", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E6
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:54.833Z (post-switch, non-investigator)
    quote: '{"ts": "2026-11-03T07:57:54.833Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "05196dfb5b8f", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1214.064, "client": "127.0.0.1:64962"}'
  - id: E7
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:56.180Z (post-switch, non-investigator)
    quote: '{"ts": "2026-11-03T07:57:56.180Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "2584f0bce82f", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 286.768, "client": "127.0.0.1:64963"}'
  - id: E8
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:57.590Z (post-switch, non-investigator; same path as E3)
    quote: '{"ts": "2026-11-03T07:57:57.590Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "db18cc050221", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 339.781, "client": "127.0.0.1:64964"}'
  - id: E9
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:57:59.422Z (post-switch, non-investigator; same path as E4)
    quote: '{"ts": "2026-11-03T07:57:59.422Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "53c7b36beb1e", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 773.242, "client": "127.0.0.1:64965"}'
  - id: E10
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:58:01.486Z (post-switch; the last non-investigator request line in the file)
    quote: '{"ts": "2026-11-03T07:58:01.486Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "d770596c5956", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 997.36, "client": "127.0.0.1:64966"}'
  - id: E11
    type: metric
    source: /metrics @ 2026-11-03T08:02:20Z (request id konan-1793692940-23931)
    quote: faultline_chaos_enabled 1
  - id: E12
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:59:54.487Z (investigator probe; no other traffic in flight since 07:58:01.486Z)
    quote: '{"ts": "2026-11-03T07:59:54.487Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793692793-23820", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 562.153, "client": "127.0.0.1:64997"}'
  - id: E13
    type: log
    source: lab/logs/app.log @ 2026-11-03T08:00:24.596Z (investigator probe; same path as E12)
    quote: '{"ts": "2026-11-03T08:00:24.596Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793692824-23866", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 101.452, "client": "127.0.0.1:65003"}'
  - id: E14
    type: log
    source: lab/logs/app.log @ 2026-11-03T07:58:25.805Z (investigator probe, switch on)
    quote: '{"ts": "2026-11-03T07:58:25.805Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793692705-23762", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.694, "client": "127.0.0.1:64985"}'
  - id: E15
    type: metric
    source: /metrics @ 2026-11-03T08:02:20Z (cumulative sums over the whole process lifetime, pre- and post-switch requests mixed)
    quote: >-
      http_request_duration_seconds_sum{method="GET",path="/health"}
      0.01897587371058762 / http_request_duration_seconds_count{method="GET",path="/health"} 4 ;
      http_request_duration_seconds_sum{method="GET",path="/metrics"}
      0.002821667119860649 / http_request_duration_seconds_count{method="GET",path="/metrics"} 5 ;
      http_request_duration_seconds_sum{method="GET",path="/products"}
      1.8789731240831316 / http_request_duration_seconds_count{method="GET",path="/products"} 4
  - id: E16
    type: metric
    source: >-
      /metrics @ 2026-11-03T08:02:20Z — the complete http_requests_total family of
      that scrape; no status="503" series is present in it, and the
      POST /chaos/enable count is unchanged from the 07:58:06Z scrape (E17)
    quote: >-
      http_requests_total{method="GET",path="/health",status="200"} 4 ;
      http_requests_total{method="GET",path="/metrics",status="200"} 5 ;
      http_requests_total{method="GET",path="/orders",status="200"} 2 ;
      http_requests_total{method="GET",path="/products",status="200"} 4 ;
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4 ;
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2 ;
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 ;
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E17
    type: metric
    source: >-
      /metrics @ 2026-11-03T07:58:06Z (request id konan-1793692706-23767; before any
      investigator probe of a business route) — the complete http_requests_total family
      of that scrape: no non-2xx series is present in it, and the http_exceptions_total
      header carried no series at all
    quote: >-
      http_requests_total{method="GET",path="/health",status="200"} 3 ;
      http_requests_total{method="GET",path="/orders",status="200"} 1 ;
      http_requests_total{method="GET",path="/products",status="200"} 2 ;
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3 ;
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 ;
      http_requests_total{method="POST",path="/orders",status="201"} 2 ;
      # HELP http_exceptions_total Unhandled exceptions by Python class name. ;
      # TYPE http_exceptions_total counter
  - id: E18
    type: metric
    source: /metrics @ 2026-11-03T08:02:20Z (process_max_rss_bytes is a high-water-mark gauge; the same value was read at 07:58:06Z and 07:59:57Z)
    quote: process_uptime_seconds 275.1794202090241 ; process_max_rss_bytes 47480832
  - id: E19
    type: probe
    source: /products/3 (request ids konan-1793692834-23884 and konan-1793692848-23891 — two probes, identical outcome)
    quote: 'HTTP 500 — {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793692834-23884"}'
  - id: E20
    type: log
    source: lab/logs/app.log @ 2026-11-03T08:00:34.685Z (investigator request id; stack trimmed — intermediate framework frames and the machine-local path prefix removed, kept frames unaltered)
    quote: >-
      {"ts": "2026-11-03T08:00:34.685Z", "level": "ERROR", "logger": "faultline.request",
      "message": "unhandled exception: division by zero", "request_id":
      "konan-1793692834-23884", "event": "unhandled_exception", "exception_type":
      "ZeroDivisionError", "stack": "Traceback (most recent call last): … File
      \".../src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\":
      units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
  - id: E21
    type: probe
    source: /products (request id konan-1793692824-23866)
    quote: 'HTTP 200 — [{"id":1,…,"units_in_stock":119},{"id":2,…,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,…,"units_in_stock":500}]'
  - id: E22
    type: probe
    source: /products/4 (request id konan-1793692830-23878)
    quote: 'HTTP 200 — {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
  - id: E23
    type: metric
    source: >-
      /metrics @ 2026-11-03T08:02:20Z — these are the only two 500s and the only
      exception count of the process lifetime; both 500s carry investigator request ids
      (E19, E20), and neither series existed at the 07:58:06Z scrape (E17)
    quote: >-
      http_exceptions_total{type="ZeroDivisionError"} 2 ;
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
gaps:
  - >-
    The time of the reported error page is unknown, so H5 cannot be settled from
    telemetry. The reporters hold the one fact that would decide it: a timestamp
    or a request id. Inside 07:57:45Z–08:02:20Z, E16 and E23 close it; before
    07:57:45Z, this surface cannot speak.
  - >-
    Readable history starts at process start, 2026-11-03T07:57:45.459Z (E1),
    with no rotated log backups — about 20 s before the complaint was raised.
    Any user-facing error older than the process left no artifact on the
    investigator surface.
  - >-
    All counters are per-process: every "this never happened" statement here
    covers the 275 s of this process life (E18), and the non-investigator
    request lines cover only 07:57:46.173Z–07:58:01.486Z. Nothing in this
    journal is a claim about longer history.
  - >-
    No off-state re-measurement. The decisive counterfactual — a business-route
    duration taken with the switch off after the onset — needs the switch
    toggled, which is a mutation outside konan's read-only surface. E2–E4 are
    the only off-state samples, and they predate the onset.
  - >-
    The switch's current failure rate is not on the investigator surface:
    /metrics exposes only faultline_chaos_enabled, not the rate. A silent
    reconfiguration could not be observed directly; the unchanged
    POST /chaos/enable count and the absent status="503" series (E16) are the
    closest available checks.
  - >-
    No CPU, event-loop-lag, thread-pool or connection-pool metric exists on the
    surface — process_max_rss_bytes is a high-water-mark gauge (E18). Saturation
    was therefore excluded by traffic volume and concurrency (E12, E17), not by
    resource telemetry.
  - >-
    No client-side or edge telemetry. An error page rendered by a browser or an
    intermediary that gave up on a slow response would not appear in the
    target's logs at all.
  - >-
    All non-investigator traffic arrives from 127.0.0.1 on ports 64956–64966, so
    "users" in this journal means that local traffic. The POST /chaos/enable
    call that flipped the switch (E5) sits in the same client band: a local
    actor enabled it: the target did not do this to itself.
usage:
  model: claude-opus-5
  tokens: 2205017
  wall_clock_seconds: 605
---

# Shop-wide latency from an operational degradation switch left on

## Summary

**Root cause identified.** An operational degradation switch inside the target was
enabled at 07:57:51.563Z and is still on. While on it adds a variable per-request
delay — bounded by the configured `extra_latency_ms` of 1500 — to every business
route. Business-route latency stepped from 1.3–1.6 ms before the switch (E2, E3, E4)
to 287–1214 ms after it (E6, E7, E8, E9, E10), with no deploy, no restart and no
change in traffic across the boundary. The reporters' observation that health checks
stay green is accurate and is the trap here: `/health` and `/metrics` were not
delayed — 0.694 ms at 07:58:25Z with the switch on (E14) — so every signal that reads
the health endpoint stayed green through the whole event. Confidence is high on the
mechanism and on the onset time; the delay is randomized per request, not a fixed
1500 ms addition, which is why the shop feels unevenly slow and why a single lucky
probe can look healthy (101 ms at 08:00:24Z, E13).

The second half of the complaint does not resolve. **No user-facing error exists
anywhere on the readable surface**: zero non-2xx responses and no exception series at
all before the investigation's own probes (E17), and no `status="503"` series even
now (E16). The switch's error injection was configured but disarmed — `failure_rate:
0.0` alongside `error_status: 503` (E5) — so it cannot be the error page. A real,
deterministic 500 does exist on the zero-stock product detail page (E19, E20), but in
this process lifetime only the investigation's own probes are recorded as having hit
it (E23). Whether a user met it earlier cannot be decided: the log begins at process
start, roughly 20 s before the complaint. One fact from the reporters — the time of
the error page — would settle it.

Impact, counting only non-investigator traffic: every business request in
07:57:54Z–07:58:01Z succeeded but ran 200–900× slower than baseline. No failed user
request is recorded. Non-investigator traffic stops at 07:58:01.486Z (E10), so no
statement can be made about user impact after that moment — only that the cause of
it is still active (E11).

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 07:57:45.459 | Process starts; the only lifecycle marker in the file, and uptime climbed monotonically afterwards — one process throughout | E1, E18 |
| 07:57:46.173–07:57:48.515 | Healthy user traffic: business routes answer in 1.3–1.6 ms | E2, E3, E4 |
| **07:57:51.563** | **Configuration-change marker: the degradation switch is enabled — `failure_rate: 0.0`, `error_status: 503`, `extra_latency_ms: 1500`. Non-investigator request id `90cf1be38619`** | **E5** |
| 07:57:54.833–07:58:01.486 | Every user business request still 200/201, now 287–1214 ms. Last non-investigator line at 07:58:01.486 | E6, E7, E8, E9, E10 |
| 07:58:05 | Complaint raised by a human | trigger |
| 07:58:15 | Investigation starts (trigger latency 10 s) | trigger |
| 07:58:25.805 | Investigator `/health` answers in 0.694 ms with the switch on — the monitoring blind spot, observed | E14 |
| 07:59:54.487 | Investigator `/products` takes 562 ms as the sole request in flight — no queue can form | E12 |
| 08:00:24.596 | Investigator `/products` takes 101 ms — the injected delay varies per request | E13 |
| 08:00:34.685 | Investigator probe of the zero-stock product page raises `ZeroDivisionError` → 500; the first error of the process lifetime, and it is ours | E19, E20 |
| 08:02:20 | Switch still on; no 503 series; enable count still 1, so no second reconfiguration | E11, E16 |

## Investigation

**Baseline** (07:58:25Z–07:58:26Z): `/health` 200 in 2 ms, `/metrics` 200, and the
full 21-line log. The baseline read already carried the answer —
`faultline_chaos_enabled 1` and a `chaos_enabled` marker sitting between fast and
slow request lines — so the rest of the loop was spent trying to break that reading
rather than to decorate it.

**Triage**, three lenses in parallel, each blind to the others and to the
investigation narrative: infra/process, interfaces, software-defect. All three
independently located the same onset marker and the same health-endpoint exemption.
The software-defect lens additionally found and reproduced the zero-stock 500. No
lens was skipped, so no discipline-shaped blind spot was accepted.

**Deep-dive: deliberately skipped.** H1's triage evidence was already deterministic
and complete — a configuration marker, a step change across it on four route
families, a live probe confirming the degradation two minutes later, and the gauge
still at 1. H2 and H3 were already dead on triage evidence. H5's missing evidence is
structurally unavailable: it lives with the reporters or in pre-process-start history
that no probe can reach. A deep-dive round would have re-proved what was proven and
could not have touched what was not. Budget used: one triage round of three lenses,
one judge.

**Judge** (fresh, evidence-only): it validated H1's mechanism and sharpened four
things, all of which changed this journal:

1. `extra_latency_ms: 1500` is a *setting*, not a measurement — every observed delay
   is below it. The journal now states a variable delay bounded by 1500 ms. The
   101 ms probe (E13) is the clearest proof.
2. H2's refutation originally leaned on `process_max_rss_bytes`. That is a
   high-water-mark gauge and shows no such thing. The refutation now rests on traffic
   volume and on E12 — one request in flight, still 562 ms. A queue cannot form with
   one request.
3. H3 was over-claimed as a single invalidated hypothesis. It was two claims; the
   slowness clause is invalidated, the error-page clause is not. It is now split into
   H3 (invalidated) and H5 (inconclusive).
4. "Latent" under-states the zero-stock defect: the product is in the public listing
   and the fault is deterministic for anyone who opens its page. The latent finding
   now says *unreached by logged user traffic in a 15-second window*, not *unreachable*.

Two of the judge's residual gaps could be closed with evidence already in hand: the
`POST /chaos/enable` count is still 1 at 08:02:20Z and no `status="503"` series exists
(E16), which excludes a second reconfiguration through that endpoint; and user-side
duration lines for the product-detail route do exist (E7, E8), so "shop-wide" rests
on four route families, not three. Its remaining cautions are recorded as Gaps
verbatim in substance, including its correct observation that "users" here means local
traffic, and that the switch was flipped from that same client band.

## Hypotheses

### H1 — degradation switch injecting latency (infra-process) — **validated**

The switch was enabled at 07:57:51.563Z and was still on 4.5 minutes later (E5, E11).
The step change brackets it within 3 s on the same route: `/products` 1.304 ms at
07:57:46.403Z (E2) against 1214.064 ms at 07:57:54.833Z (E6). The same pattern holds
on `/products/{id}` (1.276 ms → 339.781 ms, E3 → E8), on `POST /orders` (1.599 ms →
773.242 ms, E4 → E9) and on `GET /orders` (997.36 ms, E10). Nothing else changed
across that boundary: one process throughout, uptime monotonic, no second startup
marker (E1, E18).

The degradation is still reproducible, and on investigator traffic: `/products` at
562 ms (E12) and 101 ms (E13) while `/health` and `/metrics` stayed between 0.52 and
0.69 ms in the same window (E14, E15). That spread across the two route groups is the
prediction H1 makes, and it held on every sample.

Two honest limits. The pre-switch baseline is three requests in a 6-second window;
the correlation is strong because of the declared configuration event and the
three-orders-of-magnitude step, not because of sample size. And whether the monitoring
routes are exempt *by design* is not in evidence — what is in evidence is that they
were not delayed.

### H2 — load saturation — **invalidated**

Demand never rose. About a dozen user requests crossed the whole window, seconds
apart, every one 2xx (E17). The onset is a step at a configuration marker, not a
gradual degradation under volume (E5, E6). The decisive point is E12: a single
investigator request, with nothing else in flight since 07:58:01.486Z, still took
562 ms. Queueing cannot explain a lone request. This refutation rests on traffic
shape and concurrency; the surface carries no CPU, event-loop or pool telemetry, and
`process_max_rss_bytes` being flat proves only that the peak did not grow.

### H3 — a code defect caused the shop-wide slowness — **invalidated**

The slow responses are successes: 200 and 201 (E6, E9, E10). A code defect of the kind
found here fails fast rather than answering slowly. There was no exception series at
all before the investigation's own probes (E17), so nothing in the code was raising
during the slow window, and the only two 500s of the process lifetime are
investigator-triggered (E23). A real defect exists (E19, E20) — it is simply not this
incident.

### H4 — the switch's configured 503 is the error page — **invalidated**

The error path was configured but disarmed: `failure_rate: 0.0` beside
`error_status: 503` (E5). No 503 appears anywhere: no such series at 07:58:06Z (E17)
and none at 08:02:20Z (E16), and the enable count is unchanged between those reads, so
no second configuration call raised the rate in between. Worth carrying forward
without overstating it: the 503 remains configured and armed, and would fire if the
failure rate were ever raised.

### H5 — the zero-stock 500 is the error page the reporters saw — **inconclusive**

For: the defect is real, deterministic and reproducible — two probes, two identical
500s (E19) — and the stack names the unguarded division at `shop.py` line 64 on
`product["units_in_stock"]` (E20). The affected product is id 3, `units_in_stock: 0`,
and it is listed in the public catalogue (E21), so a user browsing the shop can reach
it. A stocked product returns 200 with `turnover_score: 0.0` (E22), so a zero
numerator is not the trigger — zero stock is.

Against: no non-investigator 500 is recorded anywhere (E17, E23). But that negative is
window-scoped — 275 s of process life, and only 15 s of it with user traffic in it —
and the log starts at process start, about 20 s before the complaint (E1). So the
evidence neither supports nor refutes the attribution. The single fact that settles
it: the time, or the request id, of the error page the reporters saw.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. **Ask the reporters when they saw the error page** — a timestamp or a request id.
   Inside 07:57:45Z–08:02:20Z, E16 and E23 refute H5 outright. Before 07:57:45Z, the
   zero-stock defect becomes the leading candidate and this surface cannot adjudicate it.
2. **Confirm with whoever operates the switch why it was enabled at 07:57:51.563Z.**
   The enable call came from a local non-investigator client (E5); its operator knows
   the intent, and the journal should not guess it.
3. **Read the business routes, not `/health`, when judging whether this is over.**
   `faultline_chaos_enabled` (E11) and a `/products` probe are the two signals that
   actually track the fault; the health endpoint did not move at any point.
4. **Watch for a `status="503"` series in `http_requests_total` and for growth in
   `http_exceptions_total` carrying non-investigator request ids.** Either would mean
   the situation changed character from slow-but-succeeding to failing.
5. **Watch the zero-stock product detail page.** A 500 there with a non-investigator
   request id converts the latent finding into a live user-facing incident.

## Gaps

Elaborating the frontmatter list:

- **The error page cannot be attributed.** Its time is unknown and it is the one fact
  that would decide H5.
- **History is 20 seconds deep at the moment of the complaint.** The log begins at
  process start 07:57:45.459Z with no rotated backups (E1). Anything older left no
  artifact.
- **Every negative here is per-process and window-scoped.** Counters cover 275 s
  (E18); non-investigator request lines cover 07:57:46.173Z–07:58:01.486Z. No claim in
  this journal reaches further back.
- **No off-state re-measurement after onset.** That counterfactual needs the switch
  toggled — a mutation, and outside the read-only surface. E2–E4 are the only off-state
  samples and they predate the onset.
- **The switch's live failure rate is invisible.** `/metrics` exposes only the enabled
  gauge. The unchanged enable count and the absent 503 series (E16) are the nearest
  available substitutes.
- **No resource telemetry.** No CPU, event-loop-lag, thread-pool or connection-pool
  metric exists; `process_max_rss_bytes` is a high-water mark (E18). Saturation was
  excluded on traffic shape, not on resource readings.
- **No client-side or edge telemetry.** A browser or intermediary error page on a slow
  response would be invisible to the target's logs — a live alternative explanation for
  the error report that this surface can never confirm or deny.
- **"Users" means local traffic.** All non-investigator requests come from 127.0.0.1
  ports 64956–64966, and the switch-enabling call sits in that same band (E5).
