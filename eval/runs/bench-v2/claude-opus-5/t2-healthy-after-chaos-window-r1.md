---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-handover-check
  trigger: "manual — /konan human-report adapter; fingerprint human-1793693554, labels.alertname human-report, no severity stated by the reporter; complaint startsAt 2026-11-03T08:12:34Z and the loop was entered from the same clock read, so trigger latency is under one second (not separately measured)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-03T08:12:34Z
  concluded: 2026-11-03T08:26:22Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal degradation switch inside the target was enabled at 08:11:57.500Z with failure_rate 0.6 and error_status 503, short-circuiting four non-investigator requests to 503 across the catalog and order routes, and was switched off again 6.35 seconds later at 08:12:03.850Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal operational degradation switch (chaos mode; configured failure_rate 0.6, error_status 503, extra_latency_ms 0) was on between 08:11:57.500Z and 08:12:03.850Z and produced the reported earlier noise: four 503 responses to non-investigator requests on GET /products, GET /products/1, GET /products/2 and POST /orders."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E12]
    evidence_against: []
  - id: H2
    statement: "Live traffic is being degraded right now — an active fault is affecting requests at the time of this check."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E13, E20, E21, E22]
  - id: H3
    statement: "A defect in the target's own code produced the reported earlier noise — the user-visible failures before this check came from the service's own exception path."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E6, E7, E16, E22]
  - id: H4
    statement: "An external dependency, proxy or gateway tier failing on its own produced the 503 responses."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E8]
  - id: H5
    statement: "The service currently violates its own declared response contract by serving a null price on the catalog routes, where /openapi.json declares price as a required non-nullable number."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E13]
    evidence_against: [E18, E19]
  - id: H6
    statement: "Demand exceeding capacity — queueing or resource exhaustion — produced the earlier failures."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E17, E20]
latent_findings:
  - statement: "GET /products/{product_id} fails with an unhandled ZeroDivisionError when the product's units_in_stock is 0, because the handler divides units_ordered by units_in_stock; product id 3 is the one catalog row with units_in_stock 0 and it returned 500 on every one of four attempts. No non-investigator request has ever reached it: all four occurrences carry the konan- probe prefix, and the log holds one startup marker with no rotated backups, so the counters cover the whole life of the process."
    evidence: [E13, E14, E15, E16, E22, E24]
  - statement: "The metrics path label is not templated on the switch's early-return path: the injected 503s are counted under raw paths (/products/1, /products/2) while successes and 500s on that same route are counted under /products/{product_id}. A per-route query on the templated label therefore silently omits those 503s from both numerator and denominator, and the label space gains one series per product id that fails while the switch is on."
    evidence: [E17]
  - statement: "GET /products/{product_id} answers with HTTP 500 and a body of shape {error, exception_type, request_id}, while /openapi.json declares only 200 and 422 for that route and carries no schema for that error body; the body also discloses the internal exception class name to the client. This is the contract-surface consequence of the zero-stock defect, not an independent fault."
    evidence: [E14, E18, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:11:53.624Z"
    quote: |
      {"ts": "2026-11-03T08:11:53.624Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:11:57.500Z"
    quote: |
      {"ts": "2026-11-03T08:11:57.500Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "79a110abe141", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:11:59.616Z"
    quote: |
      {"ts": "2026-11-03T08:11:59.616Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "c4644e8a70e0", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:11:59.616Z"
    quote: |
      {"ts": "2026-11-03T08:11:59.616Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "c4644e8a70e0", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.292, "client": "127.0.0.1:65057"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:12:00.673Z"
    quote: |
      {"ts": "2026-11-03T08:12:00.673Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "b82749d513b8", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:12:01.732Z"
    quote: |
      {"ts": "2026-11-03T08:12:01.732Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "c27ff92ce078", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:12:02.792Z"
    quote: |
      {"ts": "2026-11-03T08:12:02.792Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "2653aef1890a", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:12:03.850Z"
    quote: |
      {"ts": "2026-11-03T08:12:03.850Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "e25d29c48ba0", "event": "chaos_disabled"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:12:26.029Z"
    quote: |
      {"ts": "2026-11-03T08:12:26.029Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b8445b5dc3b4", "event": "order_created", "order_id": 1, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:12:26.030Z"
    quote: |
      {"ts": "2026-11-03T08:12:26.030Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b8445b5dc3b4", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.794, "client": "127.0.0.1:65064"}
  - id: E11
    type: metric
    source: "/metrics scrape, request id konan-1793694040-24486 (2026-11-03T08:20:40Z)"
    quote: |
      faultline_chaos_enabled 0
  - id: E12
    type: metric
    source: "/metrics scrape, request id konan-1793694040-24486 (2026-11-03T08:20:40Z)"
    quote: |
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 1
  - id: E13
    type: probe
    source: "/products, request id konan-1793694041-24491 (2026-11-03T08:20:41Z)"
    quote: |
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001361s request_id=konan-1793694041-24491
  - id: E14
    type: probe
    source: "/products/3, request id konan-1793693750-24340 (2026-11-03T08:15:51Z)"
    quote: |
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793693750-24340"}
      -- HTTP 500 in 0.008948s request_id=konan-1793693750-24340
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:15:50.994Z, request_id konan-1793693750-24340, event unhandled_exception, exception_type ZeroDivisionError — final frame of the stack field, quoted with the absolute checkout path trimmed (frame: src/faultline/shop.py line 64, in get_product)"
    quote: |
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
  - id: E16
    type: metric
    source: "/metrics scrape, request id konan-1793694040-24486 (2026-11-03T08:20:40Z)"
    quote: |
      http_exceptions_total{type="ZeroDivisionError"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
  - id: E17
    type: metric
    source: "/metrics scrape, request id konan-1793694040-24486 (2026-11-03T08:20:40Z)"
    quote: |
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_request_duration_seconds_count{method="GET",path="/products/1"} 1
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 11
  - id: E18
    type: probe
    source: "/openapi.json, request id konan-1793693908-24418 — the responses object declared for GET /products/{product_id}"
    quote: |
      "responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{"type":"object","additionalProperties":true,"title":"Response Get Product Products  Product Id  Get"}}}},"422":{"description":"Validation Error","content":{"application/json":{"schema":{"$ref":"#/components/schemas/HTTPValidationError"}}}}}
  - id: E19
    type: probe
    source: "/openapi.json, request id konan-1793693908-24418 — the 200 response schema declared for GET /products, and the complete components.schemas key set"
    quote: |
      "responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{"items":{"additionalProperties":true,"type":"object"},"type":"array","title":"Response List Products Products Get"}}}}}
      components.schemas keys: ChaosSettings, HTTPValidationError, OrderRequest, ValidationError
  - id: E20
    type: metric
    source: "/metrics scrapes, request ids konan-1793693595-24231 (08:13:15Z) and konan-1793694040-24486 (08:20:40Z)"
    quote: |
      process_uptime_seconds 82.02451558294706   ->   process_uptime_seconds 527.1755052909721
      process_max_rss_bytes 46792704             ->   process_max_rss_bytes 46792704
  - id: E21
    type: log
    source: "lab/logs/app.log, every non-investigator request after the switch was disabled (08:12:23.910Z–08:12:28.143Z)"
    quote: |
      {"ts": "2026-11-03T08:12:23.910Z", "message": "GET /products -> 200", "request_id": "d5f01d71c7ea", "status": 200, "duration_ms": 0.735}
      {"ts": "2026-11-03T08:12:24.968Z", "message": "GET /products/1 -> 200", "request_id": "e167eca68f77", "status": 200, "duration_ms": 0.796}
      {"ts": "2026-11-03T08:12:27.088Z", "message": "GET /orders -> 200", "request_id": "ce90a92931c3", "status": 200, "duration_ms": 0.853}
      {"ts": "2026-11-03T08:12:28.143Z", "message": "GET /products/5 -> 200", "request_id": "5b04447269c9", "status": 200, "duration_ms": 0.714}
  - id: E22
    type: log
    source: "lab/logs/app.log, census of all 56 lines: request-id prefixes by time"
    quote: |
      Last non-"konan-" request id in the file: 5b04447269c9 at 2026-11-03T08:12:28.143Z (status 200).
      Every request line after it — 08:13:14.974Z through 08:20:41.381Z — carries the "konan-" investigator prefix, including all four lines with "status": 500.
  - id: E23
    type: probe
    source: "/health, request id konan-1793693594-24226 (2026-11-03T08:13:14Z)"
    quote: |
      {"status":"ok","uptime_seconds":81.36250316584483}
      -- HTTP 200 in 0.002202s request_id=konan-1793693594-24226
  - id: E24
    type: log
    source: "lab/logs/app.log and lab/logs/ directory listing"
    quote: |
      The file carries exactly one "event": "startup" line (E1) and no shutdown, exit or second startup line; lab/logs/ holds app.log alone, with no .1-.3 rotated backups.
gaps:
  - "Impact cannot be attributed to real end users. The four requests that received 503s are non-investigator traffic, but so are the two calls that armed and disarmed the switch (79a110abe141, e25d29c48ba0) — operator-driven and organic traffic share one unstamped request-id space. The evidence supports \"four non-investigator requests failed\"; it does not support \"four users were harmed\"."
  - "No non-investigator request appears anywhere after 08:12:28.143Z (E22). The claim that the service is healthy now therefore rests on investigator probes plus the absence of live traffic, not on observed healthy user traffic."
  - "Who enabled the switch at 08:11:57.500Z, and whether it was an intentional drill, is outside the investigator's surface: the switch endpoints are operator surface and the probe allowlist refuses them by contract (docs/lab.md)."
  - "The log horizon starts at the 08:11:53.624Z startup marker with no rotated backups, so nothing before process start is observable. If the reporter's \"noise earlier\" predates that marker, this investigation cannot speak to it."
  - "Tying the four 503s to what the reporter saw is temporal inference, not testimony: the complaint records when it was filed (08:12:34Z, 31 seconds after the window closed) but not what was observed or when. The window is the only failure episode in the observable history, which is why the inference is strong, not certain."
  - "Two parts of the zero-stock finding are inferences, not observations: \"any product with units_in_stock 0\" generalizes from the quoted division expression (E15) plus one failing id, and \"the handler has no zero guard\" is read from the exception rather than from source — the target's source is outside the surface contract."
  - "Whether a null-priced product (id 4) corrupts an order total is untested; settling it needs POST /orders, which the GET-only probe allowlist does not permit. This is the most valuable test left undone."
  - "No CPU, connection-pool, file-descriptor or latency-percentile series exist on this surface, and process_max_rss_bytes is a high-water gauge that says nothing about current usage. Saturation was excluded by an alternative logged cause and sub-millisecond durations, not by direct resource telemetry."
  - "Lens coverage: three lenses exist (software-defect, infra-process, interfaces) and all three were spawned. The taxonomy classes third-party and data-db have no lens and no corresponding surface in this lab (no external provider, no database — docs/lab.md); load-saturation was covered inside the infra-process lens rather than by a dedicated one."
  - "Trigger latency was not measured: the adapter's startsAt and the loop-entry stamp came from a single clock read, so it is recorded as under one second rather than observed."
  - "The investigation's own probes moved the telemetry it reads: the four 500s and http_exceptions_total{type=\"ZeroDivisionError\"} 4 did not exist at baseline and are entirely investigator-made. Any later shift comparing counters should subtract them."
usage:
  model: claude-opus-5
  tokens: 2551187
  wall_clock_seconds: 828
---

# Shop service handover check — a closed 6-second error-injection window, and a latent zero-stock defect

## Summary

**Nothing is wrong with the shop service right now, and the earlier noise is fully
explained.** At 08:11:57.500Z an internal degradation switch inside the target was
enabled with `failure_rate 0.6`, `error_status 503` and no added latency (E2). For the
next 6.35 seconds it short-circuited four non-investigator requests to 503 — `GET
/products/2`, `GET /products/1`, `POST /orders` and `GET /products` — each one tagged by
the service itself as an injected failure (E3, E5, E6, E7). The switch was disabled at
08:12:03.850Z (E8). Twenty seconds later the same kind of traffic was succeeding again,
including a completed order with correct arithmetic (E9, E10). The gauge reads
`faultline_chaos_enabled 0` (E11), the four 503 counters have not moved since
(E12), the process never restarted (E20), and the catalog answers 200 in 1.4 ms (E13).
Confidence in the mechanism is high: the switch logged its own parameters, every failure
inside the window carries an injection event, and both window edges are explicit.

Two things deserve the next shift's attention, and neither is an outage. First, a **latent
defect**: `GET /products/{product_id}` raises an unhandled `ZeroDivisionError` whenever a
product's `units_in_stock` is 0, because the handler divides `units_ordered` by that field
(E15). Product 3 is the one such row in the catalog (E13) and it failed on all four
attempts (E16) — but **every one of those attempts was mine**. No real request has ever
hit it (E22), so it is a defect waiting on the right input, not the incident. Second, an
**observability gap** that would hide a repeat of today's window: the injected 503s are
counted under raw path labels while successes on the same route are counted under the
templated label (E17), so the natural per-route error-rate query omits them entirely.

One caveat the record must carry: the telemetry cannot tell organic user traffic from
operator-driven simulated traffic — the switch toggles share the same unstamped
request-id space as the requests that got 503s. "Four non-investigator requests failed"
is supported; "four users were harmed" is not.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 08:11:53.624Z | Process start — the only startup marker in the log, and the start of all observable history | E1, E24 |
| 08:11:54–55Z | Healthy traffic: `/health`, `/products`, `/products/1` all 200 | E21 (same pattern, pre-window) |
| **08:11:57.500Z** | **Configuration-change marker: degradation switch enabled**, `failure_rate 0.6`, `error_status 503`, `extra_latency_ms 0` | E2 |
| 08:11:58.559Z | `GET /products` -> 200 — the switch is probabilistic, not total | E12 |
| 08:11:59.616Z | First injected failure: `GET /products/2` -> 503 | E3, E4 |
| 08:12:00.673Z | `GET /products/1` -> 503 | E5 |
| 08:12:01.732Z | `POST /orders` -> 503 — the only failure on the order path | E6 |
| 08:12:02.792Z | `GET /products` -> 503 | E7 |
| **08:12:03.850Z** | **Configuration-change marker: degradation switch disabled** — window closes, 6.35 s wide | E8 |
| 08:12:23–28Z | Recovery confirmed on live traffic: `/products`, `/products/1`, `/orders`, `/products/5` all 200 | E21 |
| 08:12:26.029Z | Order created, `total_price 23.0` against catalog price 23.0 — the business path works end to end | E9, E10 |
| 08:12:28.143Z | **Last non-investigator request in the whole log** | E22 |
| 08:12:34Z | Complaint filed — 31 s after the window closed | — |
| 08:13:14Z | Investigation's first probe: `/health` 200 | E23 |
| 08:15:51Z–08:18:47Z | Investigator probes of `/products/3` return 500 four times — the latent defect, investigator-triggered only | E14, E15, E16, E22 |
| 08:20:40–41Z | Final state: switch off, 503 counters unchanged, uptime continuous, catalog 200 | E11, E12, E13, E20 |

## Investigation

**Baseline** (08:13:14–15Z): `/health` 200 (E23), a full `/metrics` scrape, and the log
read whole — 30 lines at that point, one startup marker, no rotated backups (E24). The
baseline was already not clean: the counters held four 503s and a switch enable/disable
pair, and `http_exceptions_total` had no series at all.

**Triage** — all three available lenses spawned in parallel, each blind to the others,
each given only its lens file, the surface contract, the verbatim complaint and the
baseline. The complaint was vague ("anything wrong?"), so no lens could be excluded on
evidence. All three converged on the switch window independently; the software-defect and
interfaces lenses additionally found the zero-stock defect and the metric-label split,
neither of which the complaint mentioned.

**Deep-dive** — one hypothesis, selected because it was the only live user-facing claim
that triage left unsettled: the null `price` on product 4 looked like a response-contract
violation. It was killed decisively — `/openapi.json` declares no product schema at all
(the 200 responses are unconstrained objects and `components.schemas` holds only
`ChaosSettings`, `HTTPValidationError`, `OrderRequest`, `ValidationError`), so there is no
declared constraint for a null to violate (E18, E19). H1 and the latent defect skipped
deep-dive: their triage evidence was already deterministic and complete, and deep-dives
exist to fill evidence gaps, not to re-prove.

**Judge** — one fresh judge, given only the hypothesis list and the verbatim evidence
ledger, no narrative. It earned its place three times: it caught that my ledger cited
injection events for only two of the four 503s (the other two existed in the log and are
now E5 and E7); it refused the original wording of H2 as conflating "live traffic is
degraded now" with "a fault exists now", since a deterministic 500 on product 3 is a
fault that exists now (H2 is restated here as the narrow claim actually tested, with the
other reading carried by the latent finding where it belongs); and it flagged that
"non-investigator" was being quietly upgraded to "users", which is now a gap rather than
a claim. It also caught that H5 cited the collection route's payload against the detail
route's schema — the deep-dive's verbatim quote of the collection route's own schema
(E19) closes that.

**Second round** — one targeted gathering step from the judge's "what would settle it"
list: a census of every request id and status in the log after the window closed. It
settled H2 and sharpened it into a gap: all live traffic after 08:12:03.850Z succeeded,
and there has been no non-investigator traffic at all since 08:12:28.143Z (E22). Budget
used: one triage round of three lenses, one deep-dive, one judge, one census — inside the
budget of two rounds and three deep-dives per round.

## Hypotheses

### H1 — degradation switch (infra-process) — **validated**

The strongest form of evidence available on this surface: the mechanism logged its own
configuration on the way in (E2), tagged each request it failed (E3, E5, E6, E7), and
logged its own exit (E8). The 503 counters show exactly one per affected route and method,
with no increment in the seven minutes since (E12). Classification follows the contract
explicitly — an internal operational switch is `infra-process` even though its symptom
wears a gateway-shaped 503 — and the cause id is `degradation-switch`. The one soft edge,
named here rather than hidden: tying this window to *what the reporter saw* is temporal
inference. The complaint arrived 31 seconds after the window closed, and this is the only
failure episode in the observable history, but the reporter never said what they saw.

### H2 — live traffic degraded right now (infra-process) — **invalidated**

Positive current evidence, not an absence: the switch gauge reads 0 (E11), the catalog
answers 200 in 1.4 ms (E13), uptime is continuous across the check with a flat RSS
high-water mark (E20), and every live request after the window succeeded (E21). The judge
rightly objected that the first wording of this hypothesis also implied "no fault exists
anywhere right now", which the deterministic product-3 500 contradicts. That reading is
not dismissed — it is the first latent finding. What is invalidated is the narrow,
operational claim: nothing is currently failing live traffic.

### H3 — the target's own code caused the earlier noise (software-defect) — **invalidated**

Refuted by alternative, not by absence: the service logged the 503s as injected (E3, E5,
E6, E7), and the exception path is severed from live traffic entirely — all four 500s and
all four `ZeroDivisionError` counts carry the investigator prefix (E16, E22). The counts
are internally consistent (7 × 200 + 4 × 500 = 11 templated requests, E17), so no pool of
unaccounted 500s hides behind the labels.

### H4 — external dependency or gateway tier (interfaces) — **invalidated**

The 503s are in-app responses, not a tier's own: they appear as `faultline.request` access
lines with sub-millisecond durations (E4: 0.292 ms) and two of them carry an explicit
self-injection event (E3, E6), with both window edges logged inside the process (E2, E8).
Part of this refutation is still an absence — nothing on this surface shows whether the
target has any external dependency at all — which is acceptable only because a positive
in-app cause is established.

### H5 — null price violates the declared contract (interfaces) — **invalidated**

Considered because a null price on a shop catalog route looks exactly like
contract drift, and it is live right now (E13). It fails on its premise: the OpenAPI
document declares no product schema on either catalog route — unconstrained objects with
`additionalProperties: true`, and a component set that contains no product model (E18,
E19). A permissive untyped object cannot be violated by a null field. The underlying
observation stands as data quality worth someone's attention; as a contract violation it
is unsupported. (If a product contract is declared somewhere outside `/openapi.json`, this
could be re-run against it — that source is outside the investigator's surface.)

### H6 — load saturation — **invalidated**

Killed from baseline evidence without spending a lens: the switch injected zero added
latency (E2), the busiest route saw 11 requests in the whole process lifetime (E17),
durations are sub-millisecond on both the 503s (E4) and the recovery traffic (E21), and
the RSS high-water mark did not move across the check (E20). The refutation rests on the
alternative cause and on microsecond-scale durations rather than on resource telemetry,
which this surface does not carry — recorded as a gap.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- Confirm with whoever armed the switch at 08:11:57.500Z that it was an intentional drill.
  The actor is not visible on the investigator's surface, and an unexplained toggle is a
  different handover item from a scheduled one.
- At the start of the next shift, read `/metrics` once and compare `faultline_chaos_enabled`
  and the four 503 series against the values quoted in E11 and E12. Any increment means a
  new window, not this one.
- Treat `GET /products/3` as a known-500 input. Every 500 in this record is
  investigator-made; adding it to a synthetic check will generate alerts that look like
  user impact.
- When reading or building a dashboard for the product-detail route, read the raw-path
  series alongside the templated one (E17), or injected 503s will be missed in exactly the
  window where they matter.
- A source review of the division at the frame quoted in E15, and of where the metrics
  `path` label is assigned, would close the two inferences this report leaves open. Both
  live in the target's own repo, outside this surface.
- The one high-value test left undone needs a write and so is out of bounds here: whether
  ordering the null-priced product (id 4) yields a null or garbage order total.

## Gaps

The frontmatter list, elaborated where it matters:

- **Impact attribution.** The four failed requests were not investigator probes, but the
  surface gives no way to separate organic users from operator-driven simulated traffic —
  the two switch toggles sit in the same unstamped id space as the requests that failed.
  Any statement about *users* in this incident is unsupported by what was observed.
- **The "healthy now" claim is narrower than it sounds.** There has been no
  non-investigator traffic at all since 08:12:28.143Z (E22), so health right now is
  established by investigator probes against an idle service, not by watching live traffic
  succeed.
- **History horizon.** The log begins at process start with no rotated backups, giving
  about nine minutes of history. Anything the reporter saw before 08:11:53.624Z is
  invisible to this investigation.
- **Operator surface is out of bounds by contract**, so the switch's origin and intent are
  unknown — that is the boundary working as designed, not a failure of the investigation.
- **Two inferences inside the latent defect**: the generalization to every zero-stock
  product (from the division expression plus one failing id) and the absence of a zero
  guard (from the exception rather than from source).
- **Untested write path**: whether the null-priced product corrupts an order total.
- **Missing resource telemetry**: no CPU, connection-pool, descriptor or percentile series
  exist; RSS is a high-water gauge only.
- **Lens coverage**: all three existing lenses ran. `third-party` and `data-db` have no
  lens and no surface in this lab; `load-saturation` was handled inside the infra-process
  lens.
- **Trigger latency** was recorded, not measured: the complaint stamp and the loop-entry
  stamp came from one clock read.
- **The investigation perturbed its own telemetry**: the four 500s and the
  `ZeroDivisionError` counter are entirely investigator-made and did not exist at baseline.
