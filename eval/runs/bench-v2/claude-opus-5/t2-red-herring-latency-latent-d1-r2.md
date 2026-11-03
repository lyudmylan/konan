---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-latency-degradation-switch
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-03T07:42:28Z
  concluded: 2026-11-03T07:53:50Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational degradation switch inside the target was enabled at 07:41:47.042Z with a configured extra_latency_ms of 1500 and is still enabled; it adds a variable per-request delay, bounded by that value, to the user-facing business routes while leaving the health and metrics routes at their normal sub-2 ms latency."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal operational degradation switch, enabled at 2026-11-03T07:41:47.042Z with extra_latency_ms 1500 and never disabled, injects a variable per-request delay bounded by that value into the user-facing business routes (/products, /products/{id}, /orders, POST /orders) while the /health and /metrics monitoring routes keep their pre-switch sub-2 ms latency; this is the cause of the reported shop-wide slowness."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E26, E27]
    evidence_against: []
  - id: H2
    statement: "The error page some users reported was a 5xx response served by the target to a user inside the window the telemetry record covers."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E16, E17, E20, E21]
  - id: H3
    statement: "The deterministic product-detail defect (division by a zero units_in_stock) was serving error pages to users and is the active incident."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E16, E17, E18, E20, E21]
  - id: H4
    statement: "Demand exceeding the service's capacity — queueing, worker or memory exhaustion — caused the slowdown."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E12, E13, E14, E16, E28]
  - id: H5
    statement: "A process lifecycle event — crash, restart, or hang — caused the slowness and the error page."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E13, E16, E24, E28]
  - id: H6
    statement: "The one-off error page originated outside the target — an edge or gateway timeout on a multi-second response, or the client's own handling of it — rather than from a status the target itself returned."
    incident_class: interfaces
    state: inconclusive
    evidence_for: [E6, E12, E27]
    evidence_against: [E16]
  - id: H7
    statement: "The latency injection was initiated by a client other than the investigator, through the target's own operational switch endpoint, about 23 seconds before the complaint was raised."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E16]
    evidence_against: []
latent_findings:
  - statement: "The product-detail route divides units_ordered by units_in_stock without guarding zero, so every request for a product with zero stock returns 500. Product 3 has zero stock and is listed in the public product listing, so the route is reachable from normal browsing; in this record only investigator probes ever exercised it, which makes it latent in this window but not unexercisable."
    evidence: [E19, E20, E21, E22, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:47.042Z"
    quote: |-
      {"ts": "2026-11-03T07:41:47.042Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "20377fdeea2c", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:47.043Z"
    quote: |-
      {"ts": "2026-11-03T07:41:47.043Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "20377fdeea2c", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.502, "client": "127.0.0.1:64806"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:41.873Z (user traffic, before the switch)"
    quote: |-
      {"ts": "2026-11-03T07:41:41.873Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "99f0e3b3441a", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.186, "client": "127.0.0.1:64803"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:42.928Z (user traffic, before the switch)"
    quote: |-
      {"ts": "2026-11-03T07:41:42.928Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "e4a7b13f9c7c", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.995, "client": "127.0.0.1:64804"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:43.984Z (user traffic, before the switch)"
    quote: |-
      {"ts": "2026-11-03T07:41:43.984Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "bb300c2e840b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.799, "client": "127.0.0.1:64805"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:50.306Z (user traffic, after the switch)"
    quote: |-
      {"ts": "2026-11-03T07:41:50.306Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "12c6a0a89aae", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1206.543, "client": "127.0.0.1:64809"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:53.609Z (user traffic, after the switch; same route as E4)"
    quote: |-
      {"ts": "2026-11-03T07:41:53.609Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "aa9f1d3b831d", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 558.368, "client": "127.0.0.1:64811"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:55.590Z (user traffic, after the switch; same route as E5)"
    quote: |-
      {"ts": "2026-11-03T07:41:55.590Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "df16c02c7dee", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 917.456, "client": "127.0.0.1:64813"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:51.986Z (user traffic, after the switch)"
    quote: |-
      {"ts": "2026-11-03T07:41:51.986Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "81b09ab55688", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 616.99, "client": "127.0.0.1:64810"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:41:56.754Z (user traffic, after the switch; the last non-investigator request in the record)"
    quote: |-
      {"ts": "2026-11-03T07:41:56.754Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "49ebb50a582e", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 101.902, "client": "127.0.0.1:64814"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:44:36.396Z (investigator traffic)"
    quote: |-
      {"ts": "2026-11-03T07:44:36.396Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793691876-23105", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.824, "client": "127.0.0.1:64857"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:44:37.892Z (investigator traffic, 1.496 s after E11)"
    quote: |-
      {"ts": "2026-11-03T07:44:37.892Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793691876-23110", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 989.595, "client": "127.0.0.1:64858"}
  - id: E13
    type: metric
    source: "/metrics @ request_id konan-1793691978-23284 (2026-11-03T07:46:18.966Z, 271.9 s after E1)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 277.8884156248532
      process_max_rss_bytes 47972352
  - id: E14
    type: metric
    source: "/metrics @ request_id konan-1793691978-23284"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.01463233307003975
      http_request_duration_seconds_count{method="GET",path="/health"} 5
      http_request_duration_seconds_sum{method="GET",path="/products"} 3.8256892492063344
      http_request_duration_seconds_count{method="GET",path="/products"} 5
  - id: E15
    type: metric
    source: "/metrics @ request_id konan-1793691978-23284"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/metrics"} 0.004045793088153005
      http_request_duration_seconds_count{method="GET",path="/metrics"} 5
  - id: E16
    type: metric
    source: "/metrics @ request_id konan-1793691978-23284 (complete http_requests_total breakdown)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 5
      http_requests_total{method="GET",path="/metrics",status="200"} 5
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E17
    type: metric
    source: "/metrics @ request_id konan-1793691748-22986 (2026-11-03T07:42:28.824Z, the investigation's first scrape, 18 s after the complaint was raised and before any investigator request to a product-detail path)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E18
    type: metric
    source: "/metrics @ request_id konan-1793691978-23284"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:44:24.410Z (investigator traffic; stack trimmed to its final frames)"
    quote: |-
      {"ts": "2026-11-03T07:44:24.410Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793691863-23088", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:44:24.427Z (investigator traffic)"
    quote: |-
      {"ts": "2026-11-03T07:44:24.427Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793691863-23088", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1059.384, "client": "127.0.0.1:64855"}
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:44:34.763Z (investigator traffic, a determinism repeat of E20)"
    quote: |-
      {"ts": "2026-11-03T07:44:34.763Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793691873-23096", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 869.885, "client": "127.0.0.1:64856"}
  - id: E22
    type: probe
    source: "GET /products @ request_id konan-1793692422-23441"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:44:17.957Z (investigator traffic; the nonzero-stock control case for E19)"
    quote: |-
      {"ts": "2026-11-03T07:44:17.957Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1793691857-23082", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 98.718, "client": "127.0.0.1:64854"}
  - id: E24
    type: log
    source: "lab/logs/app.log lines 1 and 3 — the first lines of the file, and the only startup event in the record"
    quote: |-
      {"ts": "2026-11-03T07:41:41.124Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [22881]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
      {"ts": "2026-11-03T07:41:41.125Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E25
    type: log
    source: "lab/logs/ directory listing — the extent of the retained record"
    quote: |-
      $ ls lab/logs/
      app.log
  - id: E26
    type: probe
    source: "GET /orders @ request_id konan-1793692309-23369"
    quote: |-
      -- HTTP 200 in 0.153803s request_id=konan-1793692309-23369
  - id: E27
    type: probe
    source: "GET /products @ request_id konan-1793692422-23441"
    quote: |-
      -- HTTP 200 in 1.121649s request_id=konan-1793692422-23441
  - id: E28
    type: metric
    source: "/metrics @ request_id konan-1793691748-22986 (the investigation's first scrape, 2026-11-03T07:42:28.824Z)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 47.71181549993344
      process_max_rss_bytes 47972352
gaps:
  - "The retained record begins at the process start, 2026-11-03T07:41:41.124Z (E24), with no rotated log backups (E25), and every counter resets there. The complaint's window — 'the last few minutes' from 07:42:10Z — reaches further back than the record does. Any response served before 07:41:41.124Z, including an error page, is unobservable on this surface."
  - "No per-request attribution of the injected delay exists on this surface: the log's event vocabulary (docs/lab.md) has no per-request switch event, and the switch emits nothing after the enable line. H1's causation therefore rests on the step change at the marker, the business/monitoring route split, the sub-cap spread of the delays, and the elimination of the rival mechanisms — not on a direct mechanism quote."
  - "The user-impact sample is five requests inside a 6.4-second window (07:41:50.306Z to 07:41:56.754Z, E6 to E10); all non-investigator traffic stops there. Route coverage is good — all four business routes — but impact breadth across the complaint's full window is not measurable."
  - "No edge, proxy, gateway, CDN, or client-side telemetry is in the surface contract, so H6 can be neither confirmed nor refuted here. Every status accounted for in E16 is one the target itself returned."
  - "Telemetry cannot distinguish an operator's scenario call from an end user's request: both are unstamped by the lab contract's design, and only the investigator's own traffic carries a konan- prefix. So the actor behind the switch call (E2) is not identifiable from this surface, only the fact that it was not the investigator."
  - "Whether that switch call was intended or authorized is not a telemetry question at all; it needs the operator's own change record."
  - "The per-route magnitude of the injected delay is unexplained: the two /orders samples (101.902 ms in E10, 153.803 ms in E26) cluster far below the /products samples (558.368 ms to 1206.543 ms), with too few samples per route to separate a per-route rule from the spread of a bounded random draw."
  - "The target has no database, third-party dependency, or distributed tier (docs/lab.md, 'Known gaps of this lab'). A slow-dependency rival to H1 — which would fit the timing and the route split equally well — is therefore excluded by the target's declared shape rather than by measurement."
  - "process_max_rss_bytes is a high-water mark, so the two identical readings (E28, E13) prove no new peak rather than a flat memory curve. No CPU metric exists on this surface, so CPU exhaustion was excluded by request volume (E16), not measured directly."
usage:
  model: claude-opus-5
  tokens: 2213633
  wall_clock_seconds: 682
---

# Shop-wide latency from an enabled degradation switch

## Summary

**Root cause identified.** An operational degradation switch inside the target was
enabled at 07:41:47.042Z with a configured `extra_latency_ms` of 1500 and a
`failure_rate` of 0.0 (E1). It adds a variable per-request delay, bounded by that
configured value, to the user-facing business routes, and it was still enabled at the
last reading, 271.9 s later (E13). No `chaos_disabled` event appears anywhere in the
record.

The effect is a 100x to 1000x latency step on identical routes: `GET /products` went
from 1.186 ms to 1206.543 ms (E3, E6), `GET /products/1` from 0.995 ms to 558.368 ms
(E4, E7), `POST /orders` from 1.799 ms to 917.456 ms (E5, E8). Every affected user
request still returned 200 or 201 — the degradation is latency only, not errors.

**The reporter's own observation is the most important finding here.** "Health checks
are green and fast" is true, and it is the reason this incident is invisible to
monitoring. The switch spares exactly the two routes monitoring watches: at one
instant 1.496 s apart, `/health` answered in 0.824 ms while `/products` took 989.595 ms
(E11, E12). Across the window the means are `/health` 2.9 ms and `/metrics` 0.81 ms
against `/products` 765 ms (E14, E15). Any alert bound to `/health` cannot see this.

**The reported error page is not explained, and that is an honest gap, not a finding.**
Inside the record no user request ever received a non-2xx status: the only two 500s in
the entire breakdown are the investigator's own probes (E16, E20, E21), the exception
counter was empty 18 s after the complaint was raised (E17), and the switch's
`failure_rate` is 0.0 (E1). But the record begins at the process start, 29 s before the
complaint, with no rotated backups (E24, E25) — an error page served before that is
unobservable. H6 (an edge timeout or client-side handling of a multi-second response)
remains inconclusive because this surface has no telemetry outside the target at all.

**Confidence:** high on the slowness and its mechanism; the sub-cap spread of the
delays is the strongest single piece of mechanism evidence, since a coincidental
external cause has no reason to respect the switch's configured number. Low-to-none on
the error page, which is recorded as unresolved.

One finding beyond the complaint: the switch was turned on by a client that was **not**
the investigator (E2), about 23 s before the complaint. Telemetry cannot say who.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 07:41:41.124Z | Process start — the left edge of all retained telemetry | E24 |
| 07:41:41.873Z–07:41:43.984Z | Normal user traffic: 0.995–1.799 ms across shop routes | E3, E4, E5 |
| 07:41:47.042Z | **Configuration-change marker:** degradation switch enabled, `extra_latency_ms: 1500`, `failure_rate: 0.0`, `error_status: 503` | E1 |
| 07:41:47.043Z | The enabling call itself — unstamped request id, client port 64806, so not investigator traffic | E2 |
| 07:41:50.306Z | First degraded user request, 3.26 s after the marker: `/products` at 1206.543 ms | E6 |
| 07:41:51.986Z–07:41:56.754Z | Remaining degraded user traffic, all 200/201: 616.99, 558.368, 917.456, 101.902 ms | E7, E8, E9, E10 |
| 07:42:10Z | Complaint raised by a human (adapter `startsAt`) | — |
| 07:42:28.824Z | Investigation's first scrape: switch still on, exception counter empty | E17, E28 |
| 07:44:24.427Z | Investigator probe triggers the latent zero-stock defect — the first non-2xx in the record | E19, E20 |
| 07:44:36.396Z–07:44:37.892Z | Monitoring-vs-business split captured 1.496 s apart: 0.824 ms against 989.595 ms | E11, E12 |
| 07:46:18.966Z | Switch still enabled at uptime 277.9 s; peak RSS unchanged from the first scrape | E13 |
| 07:53:42Z | Last probe: `/products` still at 1121.649 ms — the incident is ongoing | E27 |

## Investigation

**Baseline.** `/health` returned `{"status":"ok"}` in 1.95 ms; the first `/metrics`
scrape showed the switch gauge already at 1 and the exception counter empty (E28, E17);
`lab/logs/app.log` held 21 lines covering the whole process lifetime.

**Triage — three lenses in parallel, each blind to the others.** `infra-process`,
`software-defect`, and `interfaces`. The vague complaint excluded no lens by evidence,
so all available lenses ran. All three converged on the switch independently, and the
two non-infra lenses each classified it out of their own domain and said so.
`software-defect` additionally found the zero-stock defect and correctly labelled it
investigator-triggered.

**No deep-dive round was spent.** The triage evidence for H1 was already deterministic
and complete — a marker, same-route before/after pairs, a live gauge, and reproduction
by the investigator's own probes. Per the loop's rule, deep-dives fill evidence gaps
rather than re-prove, so the hypothesis list went straight to the judge.

**Judge.** The judge validated H1 and invalidated H2, H3, H4, H5 — and corrected the
report in four ways that are reflected above: it rejected "injects 1500 ms" as refuted
by the cited data (every observed delay is below the cap, the signature of a bounded
random draw, not a fixed addition); it rejected the unevidenced claim that `/metrics`
was unaffected, which was then closed with E15; it caught citing the investigator's own
500s as evidence of user impact, the clearest misattribution in the draft; and it
corrected a 41-second arithmetic error in an evidence annotation. It also raised three
hypotheses the draft had missed — H6 and H7, now carried above, and the point that the
zero-stock defect must survive refutation as a latent finding rather than disappear with
H3. After the judge, one targeted probe (E26) and one listing probe (E22, E27) closed
the reachable gaps; the rest are recorded as gaps because this surface cannot reach them.

## Hypotheses

### H1 — degradation switch injecting latency · **validated**

Four independent legs support it. The step change sits 3.26 s after the marker, with
zero overlap between the pre-switch (0.995–1.799 ms) and post-switch (101.902–1206.543
ms) populations on the same routes (E3–E10). The split is route-selective within a
single instant, which excludes a whole-process stall (E11, E12). Both rival mechanism
classes are eliminated (H4, H5). And the switch self-declares a latency parameter while
no other latency control appears anywhere on the surface.

The delay distribution corroborates rather than weakens the claim: the observed values
(101.902, 153.803, 558.368, 616.99, 869.885, 917.456, 989.595, 1059.384, 1121.649,
1206.543 ms) are spread through the interval below the configured 1500 ms and none
exceeds it. The statement was narrowed accordingly — "variable, bounded by" rather than
"of" 1500 ms.

What is missing: per-request attribution. No log event ties an individual delay to the
switch, so causation is inferential, resting on the four legs above. A read-only way to
settle it does not exist on this surface; a flip test is outside the boundary.

### H2 — a 5xx reached a user · **invalidated** (within the record)

E16 is a complete status breakdown and its only non-2xx series counts 2; E20 and E21
identify both as investigator probes. E17 is the load-bearing quote: the exception
counter had no series at all at 07:42:28.824Z, which is *after* the 07:42:10Z complaint.
E1's `failure_rate: 0.0` supports only the narrower point that the switch injected no
503s. Invalidated for the window the record covers — which is not the window the
complaint describes. See the first gap.

### H3 — the zero-stock defect is the active incident · **invalidated**

The defect is real and deterministic (E19 names the frame, E22 shows product 3 at zero
stock, E23 is the nonzero-stock control returning 200). The *incident* claim is refuted
with exact arithmetic: E16 counts two 500s, E18 counts two `ZeroDivisionError`, and both
carry `konan-` ids; E17 shows the counter empty beforehand. No request to that path from
non-investigator traffic exists anywhere in the record. It moves to `latent_findings`,
with the reachability caveat stated there: "latent" describes this window, not the
route's reachability — the product is in the public listing (E22).

### H4 — load saturation · **invalidated**

E16 totals 25 requests across the whole process lifetime, about 0.09 req/s — there is no
demand to saturate. Queueing cannot be route-selective in the way E11 and E12 show.
Peak RSS is byte-identical across the two scrapes (E28, E13). The caveats on what those
metrics actually prove are in the gaps.

### H5 — process crash, restart, or hang · **invalidated**

A single `startup` event, and it is the file's first line (E24). Counters grow from 12
to 25 requests between the two scrapes with no reset (E28, E16) — a cleaner no-restart
proof than uptime alone. Not a hang: a 0.824 ms `/health` lands in the middle of the
degraded window (E11). This holds *after* 07:41:41.124Z; whether this process replaced
an earlier one is unknowable here.

### H6 — the error page came from outside the target · **inconclusive**

The precondition is established — users saw multi-second responses (E6 at 1206.543 ms,
E12 at 989.595 ms, E27 at 1121.649 ms) — and E16 shows the target itself returned no
error to a user. At 0.6–1.2 s a browser timeout is unlikely, so this is weak. But with
H2 and H3 both refuted inside the service, it is the only remaining path to a
user-visible error, and this surface has no instrumentation outside the target to test
it either way.

### H7 — the switch was flipped by a non-investigator client · **validated**

E2's enable call carries the unstamped request id `20377fdeea2c` from client port 64806,
inside the same ephemeral range as the user traffic; E16 counts exactly one such call.
The investigator's traffic is prefixed `konan-` without exception, so the call was not
the investigator's. Beyond that, attribution stops: the lab contract makes operator
calls and simulated user traffic alike unstamped, so telemetry cannot separate an
intended operator action from anything else. This is carried as a validated hypothesis
rather than folded into H1 because it changes who needs to be asked next.

## Safe next steps

Read-only only; remediation is deliberately out of scope for this journal.

1. **Ask the operator whether the enable call at 07:41:47.042Z was intended** (E1, E2 —
   unstamped request id `20377fdeea2c`, client `127.0.0.1:64806`). This is the one
   question the telemetry cannot answer and the one that decides what kind of incident
   this is.
2. **Stop reading `/health` as a user-facing signal while the switch gauge reads 1.** For
   latency, read `http_request_duration_seconds_sum` and `_count` per business path
   instead (E14, E15) — the health route is provably exempt.
3. **Ask the reporters of the error page for the URL and the approximate time.** A
   product-detail URL for a zero-stock product would connect the report to the latent
   finding; a timestamp before 07:41:41.124Z would place it outside the retained record
   for good.
4. **If an error page needs confirming, it must come from outside this surface** — an
   edge or proxy access log, or a client-side artifact, covering roughly 07:40–07:42Z.
   Nothing inside the target can supply it.
5. **Watch for the first non-investigator request to a zero-stock product id.** The
   latent defect becomes real user impact with no new change to the target.
6. **Keep watching the switch gauge for a `chaos_disabled` event**, which has not
   appeared in the record; the incident was still ongoing at the last probe (E27).

## Gaps

The nine entries in the machine core, grouped by what they cost:

**The record is shorter than the complaint.** The retained log begins at the process
start and keeps no backups, and all counters reset there (E24, E25). The complaint
reaches back further. This single limitation is what keeps the error page unresolved —
H2 is invalidated only for the window that is observable, and that window starts 29 s
before the complaint was raised.

**The impact sample is thin.** Five user requests in 6.4 seconds (E6–E10), after which
all non-investigator traffic stops. Breadth across the complaint's window is not
measurable, and the per-route delay pattern — `/orders` consistently low, `/products`
high — has too few samples per route to interpret.

**Causation has no mechanism quote.** Neither for H1's delay injection (no per-request
switch event exists in the log's vocabulary) nor against the slow-dependency rival,
which is excluded by the target's declared shape in `docs/lab.md` rather than by
measurement. Both exclusions are stated as what they are.

**Attribution stops at "not the investigator."** The lab contract leaves operator and
end-user traffic alike unstamped by design, so E2 identifies a non-investigator client
and nothing more.

**Two metrics prove less than they appear to.** `process_max_rss_bytes` is a high-water
mark, so identical readings rule out a new peak, not growth; and no CPU metric exists at
all, so CPU was excluded by request volume rather than measured.

**Nothing outside the target is instrumented.** No edge, proxy, gateway, or client
telemetry is in the surface contract, which is why H6 stays inconclusive rather than
being settled in either direction.
