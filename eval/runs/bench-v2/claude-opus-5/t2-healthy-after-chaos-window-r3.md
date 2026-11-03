---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-handover-check
  trigger: "manual — /konan adapter, profile human; fingerprint human-1793695484, alertname human-report, no severity stated by the reporter; startsAt 2026-11-03T08:44:44Z, loop entered 2026-11-03T08:44:57Z (trigger latency 13s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-03T08:44:57Z
  concluded: 2026-11-03T08:54:50Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An internal operational degradation switch (chaos mode, failure_rate 0.6, error_status 503, extra_latency_ms 0) was enabled at 08:44:09.695Z and disabled at 08:44:16.037Z; all five 503 responses of the process lifetime were injected by it inside that window, and all five landed on non-investigator traffic."
    incident_class: infra-process
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E9, E10, E11, E14, E15, E29]
    evidence_against: []
  - id: H2
    statement: "GET /products/{product_id} raises an unhandled ZeroDivisionError and returns HTTP 500 for a product whose units_in_stock is 0, with the degradation switch off; the zero divisor is the discriminator, not a zero dividend."
    incident_class: software-defect
    state: validated
    evidence_for: [E17, E18, E19, E20, E21, E22, E23]
    evidence_against: []
  - id: H3
    statement: "That ZeroDivisionError defect produced no non-investigator failure through the observed process lifetime (uptime 0s to 240.3s): both recorded exceptions were raised by investigator probes."
    incident_class: software-defect
    state: validated
    evidence_for: [E16, E23, E17, E18]
    evidence_against: []
  - id: H4
    statement: "The earlier noise was resource exhaustion or load-driven degradation of the target."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E28, E3, E10]
  - id: H5
    statement: "The earlier noise originated at a contract surface between parties — an external dependency, a gateway tier, or schema drift."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E3, E10]
  - id: H6
    statement: "The ZeroDivisionError defect is actively failing real users at handover time."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E17, E18]
    evidence_against: [E12, E13, E25]
latent_findings:
  - statement: "GET /products/{product_id} returns HTTP 500 for the one catalog product whose units_in_stock is 0 (id 3, 'Unobtainium Ingot'). Live and deterministic with the degradation switch off, reproduced twice; triggered so far only by investigator probes, so the next real customer who opens that product detail gets a 500."
    evidence: [E17, E18, E19, E20, E23]
  - statement: "Injected-failure responses are counted in http_requests_total under the raw URL path, while handled 200s and unhandled-exception 500s on the same logical route are counted under the route template. Per-route error rate read from the templated series therefore omits injected failures, and the path label is unbounded for them."
    evidence: [E24]
  - statement: "A null price is served at HTTP 200 for product 4 while the served OpenAPI document declares no product response schema and no price property at all — an undocumented response contract rather than a drift from a declared one."
    evidence: [E20, E26]
  - statement: "The degradation switch was enabled and disabled by callers whose request ids carry no investigator prefix. The switch is reachable on the running process; this investigation cannot identify the caller or bound the risk of it being flipped again."
    evidence: [E3, E9]
evidence:
  - id: E1
    type: probe
    source: "GET /health, request id konan-1793695506-25239"
    quote: |-
      {"status":"ok","uptime_seconds":60.75258595892228}
      -- HTTP 200 in 0.001769s request_id=konan-1793695506-25239
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:05.820Z"
    quote: |-
      {"ts": "2026-11-03T08:44:05.820Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:09.695Z"
    quote: |-
      {"ts": "2026-11-03T08:44:09.695Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "dc7128ff42a2", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:10.752Z"
    quote: |-
      {"ts": "2026-11-03T08:44:10.752Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "abdc596d8beb", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:11.810Z"
    quote: |-
      {"ts": "2026-11-03T08:44:11.810Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "75443899a6de", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:12.868Z"
    quote: |-
      {"ts": "2026-11-03T08:44:12.868Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "8533c6e660a4", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:13.923Z"
    quote: |-
      {"ts": "2026-11-03T08:44:13.923Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "eb2973b4f12c", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:14.983Z"
    quote: |-
      {"ts": "2026-11-03T08:44:14.983Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "7162eb2efd1c", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:16.037Z"
    quote: |-
      {"ts": "2026-11-03T08:44:16.037Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "0a05f19225d0", "event": "chaos_disabled"}
  - id: E10
    type: metric
    source: "GET /metrics, request id konan-1793695507-25244 (first scrape, process_uptime_seconds 61.37766387499869) — every non-2xx series then present"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E11
    type: metric
    source: "GET /metrics, later scrape past process_uptime_seconds 240.30268833390437 — the same four 503 series, unchanged totals"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:38.219Z–08:44:38.220Z, request id 31907f85abd9 (no investigator prefix)"
    quote: |-
      {"ts": "2026-11-03T08:44:38.219Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "31907f85abd9", "event": "order_created", "order_id": 1, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"ts": "2026-11-03T08:44:38.220Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "31907f85abd9", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.854, "client": "127.0.0.1:65284"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:36.104Z, request id 2ab246cad70a (no investigator prefix) — first success after the window closed"
    quote: |-
      {"ts": "2026-11-03T08:44:36.104Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "2ab246cad70a", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.962, "client": "127.0.0.1:65282"}
  - id: E14
    type: metric
    source: "GET /metrics, request id konan-1793695507-25244"
    quote: "faultline_chaos_enabled 0"
  - id: E15
    type: metric
    source: "GET /metrics, later scrape"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 240.30268833390437
  - id: E16
    type: metric
    source: "GET /metrics, request id konan-1793695507-25244 — the exception counter block as scraped, carrying no series line"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E17
    type: probe
    source: "GET /products/3, request id konan-1793695629-25390"
    quote: |-
      GET /products/3 -> HTTP 500
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793695629-25390"}
  - id: E18
    type: probe
    source: "GET /products/3, request id konan-1793695634-25407 (second attempt, ~5s later)"
    quote: |-
      GET /products/3 -> HTTP 500
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793695634-25407"}
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:47:09.028Z (base fields; the line's stack field trimmed to its throwing frame)"
    quote: |-
      {"ts": "2026-11-03T08:47:09.028Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793695629-25390", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
      File ".../faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
      ZeroDivisionError: division by zero
  - id: E20
    type: probe
    source: "GET /products, request id konan-1793695625-25375"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001333s request_id=konan-1793695625-25375
  - id: E21
    type: probe
    source: "GET /products/2, request id konan-1793695625-25380 — same route as E17, non-zero divisor"
    quote: |-
      {"id":2,"name":"Toaster","price":23.0,"units_in_stock":39,"units_ordered":1,"turnover_score":0.02564102564102564}
      -- HTTP 200 in 0.001341s request_id=konan-1793695625-25380
  - id: E22
    type: probe
    source: "GET /products/4, request id konan-1793695622-25359 — zero dividend, non-zero divisor"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      HTTP 200
  - id: E23
    type: metric
    source: "GET /metrics, later scrape"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2'
  - id: E24
    type: metric
    source: "GET /metrics, later scrape — label shape of one logical route"
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E25
    type: probe
    source: "GET /orders/1, request id konan-1793695673-25443"
    quote: |-
      {"id":1,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-03T08:44:38.219+00:00"}
      -- HTTP 200 in 0.001428s request_id=konan-1793695673-25443
  - id: E26
    type: probe
    source: "GET /openapi.json, request id konan-1793695667-25437"
    quote: "The served document declares components ChaosSettings, HTTPValidationError, OrderRequest and ValidationError only; every shop response schema is {\"additionalProperties\":true,\"type\":\"object\"} and the document contains no price property."
  - id: E27
    type: log
    source: "lab/logs/app.log — file-level check of history depth"
    quote: 'grep -c ''"event": "startup"'' lab/logs/app.log -> 1; ls lab/logs/app.log.* -> no matches (no rotated backups)'
  - id: E28
    type: metric
    source: "GET /metrics, request id konan-1793695507-25244"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products"} 0.0025214161723852158
      http_request_duration_seconds_count{method="GET",path="/products"} 4
      process_max_rss_bytes 46727168
  - id: E29
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:44:13.924Z, request id eb2973b4f12c (no investigator prefix)"
    quote: |-
      {"ts": "2026-11-03T08:44:13.924Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "eb2973b4f12c", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.296, "client": "127.0.0.1:65277"}
gaps:
  - "No telemetry exists before 2026-11-03T08:44:05.820Z. The log holds exactly one startup event and no rotated backups (E27), so if the reporter's 'noise earlier' predates that process start, this investigation can say nothing about it. The degradation switch was flipped 3.9s after startup, so the whole investigated burst sits inside one freshly started process."
  - "No non-investigator request has been observed since 2026-11-03T08:44:40.337Z. 'Nothing is failing users right now' therefore rests on an absence of user traffic, not on observed healthy user traffic — which is why H6 is inconclusive rather than invalidated."
  - "The mechanism behind the metric label split could not be confirmed. Distinguishing 'the injected-failure path returns before routing populates the template' from a more general labelling rule needs the target's middleware source, which is outside the investigator's surface contract."
  - "Who flipped the degradation switch, and under what authorization, could not be checked: the switch's own endpoints are operator surface, excluded from the investigator's probe allowlist."
  - "Whether order creation decrements units_in_stock could not be tested — order creation is a POST and the investigator is GET-only. If it does, any product drained to zero stock becomes a fresh instance of the H2 defect. Product 2 is both the only product with an order and the only one with a non-round stock count (39, E20, E21), which is suggestive but is inference, not evidence."
  - "POST /orders for product 4, whose price is null (E20), could not be tested for the same read-only reason, so whether a null price breaks order creation is unknown."
  - "Load and saturation were excluded on a narrow base: one route's duration summary and a peak-RSS gauge (E28). No CPU-time, file-descriptor, connection-pool or queue-depth series exists on this target's metrics surface."
usage:
  model: claude-opus-5
  tokens: 2225723
  wall_clock_seconds: 593
---

# Shop service handover check — closed injection window, and one live defect nobody has hit yet

## Summary

**No active incident, but the handover is not clean.** Two separate things are true, and
the reporter's framing joins them only by accident.

The earlier noise is explained and over. An internal operational degradation switch
(chaos mode, `failure_rate` 0.6, `error_status` 503) was enabled at 08:44:09.695Z and
disabled at 08:44:16.037Z (E3, E9). Every 503 of the whole process lifetime — five of
them — carries its own `chaos_failure` event inside that 6.34s window (E4–E8), and the
counters still read exactly those five past uptime 240s (E10, E11). The switch is off
(E14, E15). Recovery is witnessed by real traffic, not only by probes: a customer order
succeeded 22s after the window closed (E12). Impact was real but small — all five
rejected requests were non-investigator traffic, including one `POST /orders` that a
real client lost (E29). This is why nobody filed a report: five requests over six
seconds, self-resolved before anyone looked.

What is wrong *now* is unrelated and was not reported at all: `GET /products/3` returns
HTTP 500 with an unhandled `ZeroDivisionError`, deterministically, with chaos off
(E17, E18, E19). The mechanism is a zero divisor — `turnover_score` divides by
`units_in_stock`, and product 3 ('Unobtainium Ingot') is the one catalog row at 0 stock
(E20). Controls isolate it: a non-zero divisor returns 200 (E21), and a zero *dividend*
with a non-zero divisor also returns 200 (E22), so the divisor is the discriminator.
Confidence is high on the mechanism; it rests on a named throwing frame, not on
correlation.

That defect is **latent, not inactive**. No user has hit it — the exception counter was
empty at the start of this investigation (E16) and reads exactly 2 now, both raised by
investigator probes (E23). Latent is not the same as harmless: the route fails for every
caller, so the next customer who opens that product detail page gets a 500. Treat it as
the one thing to carry into the next shift.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 08:44:05.820Z | Process starts. Only startup event in the log; no rotated history exists before this point. | E2, E27 |
| 08:44:06–08:44:07Z | Healthy traffic: `/health` 200, `/products` 200, `/products/1` 200. | — |
| **08:44:09.695Z** | **Change marker:** degradation switch enabled, `failure_rate` 0.6, `error_status` 503, `extra_latency_ms` 0. Flipped by request id `dc7128ff42a2` — not an investigator id. | E3 |
| 08:44:10.752Z | First injected 503, `GET /products`. | E4 |
| 08:44:11.810Z | Injected 503, `GET /products/2`. | E5 |
| 08:44:12.868Z | Injected 503, `GET /products/1`. | E6 |
| 08:44:13.923Z | Injected 503, `POST /orders` — a real client's order rejected. | E7, E29 |
| 08:44:14.983Z | Injected 503, `GET /products`. Five in total; no sixth ever appears. | E8, E11 |
| **08:44:16.037Z** | **Change marker:** degradation switch disabled, by request id `0a05f19225d0` — also not an investigator id. | E9 |
| 08:44:36.104Z | First non-investigator success after the window. | E13 |
| 08:44:38.219Z | Customer order succeeds end to end, `order_id` 1. Recovery confirmed by real traffic. | E12 |
| 08:44:40.337Z | **Last non-investigator request of the observation window.** Everything after is probes. | — |
| 08:44:44Z | Complaint raised (`startsAt`); loop entered 08:44:57Z. | — |
| 08:45:06–08:45:07Z | Baseline: health ok, chaos gauge 0, exception counter carries no series. | E1, E14, E16 |
| 08:47:09.028Z | `GET /products/3` raises `ZeroDivisionError`; reproduced ~5s later. | E17, E18, E19 |
| 08:48:45Z onward | Counters re-read: still five 503s, exceptions exactly 2, switch still off. | E11, E15, E23 |

## Investigation

**Baseline** (step 1): health, a metrics scrape, and the full log tail — 31 lines at the
time, one process lifetime. The short uptime (60.75s, E1) was read as
process-lifecycle evidence first, before theorising.

**Triage** (step 2): three lenses in parallel, each blind to the others and to my
reading — infra-process, software-defect, interfaces. None was skipped, because a
handover complaint this open excludes no domain by evidence. infra-process and
interfaces independently converged on the closed switch window and both returned
explicit negatives (no restart, monotonic uptime, flat peak RSS, no latency drift, no
dependency or gateway fault). software-defect declined the obvious cause and found the
`/products/3` 500 instead — the secondary cause hiding behind the loud one.

**Deep-dive** (step 3): skipped deliberately. Both surviving hypotheses already had
deterministic, complete triage evidence — change markers with paired per-request events
for H1, a named throwing frame with positive and negative controls for H2. Deep-dives
fill evidence gaps; neither had one worth an agent.

**Judge** (step 4): one fresh judge, evidence and claims only, no narrative. It did its
job and cost me two overclaims:

- H1 originally cited *one* `chaos_failure` event while claiming all five 503s were
  injected — the other four were attributed by temporal proximity alone, which is
  correlation doing causation's work. It also noted my 503 counters came from a scrape
  covering only the first 61s of a 240s lifetime.
- My original H6 claimed no user-affecting fault was active, resting on stale probes of
  *healthy* routes while a different route was provably broken. The judge was right:
  latent is not inactive, and `/products/2` succeeding says nothing about
  `/products/3`.

**Round 2** (step 5): targeted gathering on the judge's settling items that the surface
contract can reach. All five `chaos_failure` events are now cited individually with
timestamps inside the window (E4–E8); the 503 series was re-scraped past uptime 240s and
is unchanged at five (E11); the log was checked for history depth — exactly one startup
event, no rotated backups (E27). H1 now holds as worded. H6 was reworded to what the
evidence supports and marked **inconclusive**: there has been no non-investigator
traffic since 08:44:40.337Z, so current user experience is unobserved either way.

The judge also flagged two things I could not settle and have recorded as gaps rather
than quietly dropped: the mechanism of the metric label split needs the target's
middleware source (outside the surface contract), and the identity of whoever flipped
the switch is operator surface.

## Hypotheses

### H1 — degradation switch injected the burst · *validated* · infra-process

All five 503s of the process lifetime each carry their own `chaos_failure` event, and
all five timestamps (08:44:10.752Z–08:44:14.983Z, E4–E8) fall inside the enable/disable
markers (E3, E9). The counter totals are identical in a scrape at uptime 61s (E10) and a
scrape past uptime 240s (E11), so no 503 occurred outside the observed window. The
switch reports off in both scrapes (E14, E15). Nothing argues against it: the injected
responses were also the fastest of the run, consistent with a short-circuit ahead of the
handlers rather than contention, and `extra_latency_ms` was 0 so no latency was added.
Per the contract's class definitions an internal operational switch is `infra-process`
even though its symptom is a gateway-shaped 503; the mechanism id would be
`degradation-switch`. It is recorded as a hypothesis, not as a `root_cause`, because the
window is closed and there is no active incident to attribute.

### H2 — zero-divisor 500 on product detail · *validated* · software-defect

The chain is complete: a 500 with `exception_type` `ZeroDivisionError` (E17), reproduced
(E18), a log line whose `request_id` matches the first probe byte-for-byte and whose
stack names the throwing expression `units_ordered / product["units_in_stock"]` at
`shop.py:64` (E19), and the triggering datum present in served state —
`"id":3 … "units_in_stock":0` (E20). Two controls on the same route separate divisor from
dividend: non-zero divisor → 200 (E21), zero dividend with non-zero divisor → 200 and
`turnover_score: 0.0` (E22). Chaos is excluded by mechanism, not merely by gauge: the
exception propagated out of application code and no `chaos_failure` event accompanies
either 500. "Deterministic" rests on n=2 plus fixed-divisor arithmetic — sound here,
since the divisor cannot vary without a stock change, and product 3 has no orders.

### H3 — the defect has produced no user failure yet · *validated* · software-defect

The accounting closes arithmetically. The exception counter carried no series at all at
uptime 61s (E16) and reads exactly 2 past uptime 240s (E23); both raises are the
investigator probes E17 and E18. A user-triggered raise in that interval would make the
count 3 or more. Scoped honestly: this covers the observed lifetime to uptime 240.3s, not
all time.

### H4 — load or saturation · *invalidated* · load-saturation

Nothing to support it and a sufficient alternative cause. Peak RSS is a lifetime
maximum, so 46,727,168 bytes rules out memory growth across the window rather than at an
instant; mean service time is sub-millisecond; the switch added zero latency (E28, E3,
E10). Rejected on a narrow base, which is recorded under Gaps — this target exposes no
CPU, descriptor, pool or queue series.

### H5 — a contract surface between parties · *invalidated* · interfaces

The failures were self-inflicted in-process: each 503 carries an internal
`chaos_failure` event (E4), and the trigger is an internal switch (E3). No external
party, no gateway tier, no malformed payload. The `price: null` observation (E20, E26)
surfaced under this lens but is not a cause and not schema drift — the served document
declares no product response schema to drift from, so it rides along as a latent finding
about an undocumented response contract.

### H6 — the defect is failing real users now · *inconclusive* · software-defect

Genuinely unresolved, and the honest state of the handover question. For: the route
fails every caller deterministically, and the probes proving it were taken within
~3 minutes of the complaint (E17, E18) — a live broken route, not a historical one.
Against: the last observed real traffic succeeded (E12, E13) and the persisted order is
intact and arithmetically consistent (E25). Neither side settles it, because no
non-investigator request has arrived since 08:44:40.337Z. Absence of traffic is not
evidence of health, and a healthy probe of a different route is not evidence about this
one. It would be settled by one real request to `/products/3` — which is exactly the
event to avoid wanting.

## Safe next steps

Read-only, in priority order:

1. **Watch `http_exceptions_total{type="ZeroDivisionError"}`.** It reads 2 now, both
   investigator-caused (E23). Any value above 2 means a real user has hit the broken
   product detail page, and the latent finding has become an incident.
2. **Check whether the catalog can grow more zero-stock rows.** Product 3 is at 0 now;
   whether order creation drains stock toward 0 is untested and read-only probing cannot
   settle it (see Gaps). A watch on `units_in_stock` across `/products` would answer it
   over time without writing anything.
3. **Ask the operator surface owner who flipped the switch at 08:44:09.695Z**, and
   whether that was planned. Both toggle calls came from non-investigator request ids
   (E3, E9); recurrence risk is not bounded by any evidence here.
4. **Read per-route error rate from both label shapes, not just the template.** Until
   the labelling is reconciled, a dashboard on
   `path="/products/{product_id}"` would have shown zero errors during the burst while
   `/products/1` and `/products/2` carried them (E24).
5. **Note the log's history depth** before the next investigation: one process lifetime,
   no rotated backups (E27). Anything older than the current process start is
   unavailable.

Remediation is out of scope for this journal.

## Gaps

The frontmatter list, elaborated:

- **No history before 08:44:05.820Z.** One startup event, no rotated backups (E27, E2).
  The switch was flipped 3.9s after startup, so the entire burst sits inside a freshly
  started process. If the "noise earlier" the reporter heard about predates that start,
  its telemetry is in a previous process's output and is simply gone. The complaint gave
  no onset time, so this cannot be ruled in or out.
- **No user traffic to observe.** Nothing non-investigator since 08:44:40.337Z, so the
  "right now" in the complaint is answered for probe traffic and left open for user
  traffic (H6).
- **Label-split mechanism unconfirmed.** Reading it would need the target's middleware
  source, outside the surface contract. What is observed is only the label shapes (E24)
  — notably that unhandled-exception 500s *are* templated while injected 503s are not,
  which narrows the mislabelling to the injection path without proving why.
- **Switch provenance unknown.** The toggle endpoints are operator surface, excluded
  from the probe allowlist by the lab boundary.
- **Stock-decrement behaviour untested.** Order creation is a POST; the investigator is
  GET-only. Product 2 being both the only ordered product and the only non-round stock
  count (39) is suggestive of a decrement, but that is inference and is not treated as
  evidence.
- **Null-price order path untested**, for the same read-only reason.
- **Saturation excluded on a narrow base** — one route's duration summary and a peak-RSS
  gauge (E28); this target exposes no CPU, descriptor, pool or queue metrics.
