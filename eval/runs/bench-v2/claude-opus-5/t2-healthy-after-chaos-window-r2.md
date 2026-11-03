---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-handover-check
  trigger: "manual (/konan, human profile) — complaint object: source human, fingerprint human-1793694639, labels.alertname human-report, no severity stated by the reporter, startsAt 2026-11-03T08:30:39Z; investigation started 2026-11-03T08:30:47Z (trigger latency 8s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: "2026-11-03T08:30:47Z"
  concluded: "2026-11-03T08:40:23Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An operational fault-injection switch inside the target (chaos mode, failure_rate 0.6, error_status 503, extra_latency_ms 0) was on from 08:30:00.434Z to 08:30:06.786Z and returned 503 to 3 of the 5 non-investigator requests served in that window; it is off now and the window accounts for every non-investigator error in the observable history."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E19, E20]
    evidence_against: []
  - id: H2
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError and returns HTTP 500 for any product whose units_in_stock is 0, because the handler computes turnover_score = units_ordered / units_in_stock with no zero guard; product 3 is the only catalog row currently at 0 stock."
    incident_class: software-defect
    state: validated
    evidence_for: [E14, E15, E16, E17, E18, E19]
    evidence_against: []
  - id: H3
    statement: "Chaos-injected failures are recorded in http_requests_total with the raw request path as the path label while normally-routed requests use the templated path, so a sustained injection window across many product ids would grow metric label cardinality with the number of distinct ids."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E21]
    evidence_against: []
  - id: H4
    statement: "The published OpenAPI document declares no 5xx status for any route and leaves every product field untyped with additionalProperties true, so a consumer cannot learn from the contract that 500/503 occur or that price is nullable, while the service does serve a null price with HTTP 200."
    incident_class: interfaces
    state: validated
    evidence_for: [E22, E18, E23]
    evidence_against: []
  - id: H5
    statement: "Product 4 carries price null and the order path multiplies price by quantity, so an order for product 4 would fail or produce a null total."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E18, E23]
    evidence_against: []
latent_findings:
  - statement: "Deterministic HTTP 500 (ZeroDivisionError) on GET /products/3 — the only requests that have ever triggered it are investigator-stamped probes, so no user has been affected in this process lifetime. Ordinary order traffic decrements stock, so another product row can reach 0 and arm the same defect on a product users do browse."
    evidence: [E14, E15, E16, E17, E18, E19, E24]
  - statement: "Metric label inconsistency: the chaos-injected 503 on a parameterized route was recorded under path=\"/products/2\" while successes and exceptions on the same route were recorded under path=\"/products/{product_id}\"."
    evidence: [E21]
  - statement: "The served OpenAPI document declares only 200 and 422 for the product routes and types no product field, hiding both the real 5xx responses and the nullable price."
    evidence: [E22, E18, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:00.434Z"
    quote: '{"ts": "2026-11-03T08:30:00.434Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "a42dbc77a2b5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:06.786Z"
    quote: '{"ts": "2026-11-03T08:30:06.786Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "38e0b5b4b4e5", "event": "chaos_disabled"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:01.491Z"
    quote: '{"ts": "2026-11-03T08:30:01.491Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "099766aee122", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:01.491Z"
    quote: '{"ts": "2026-11-03T08:30:01.491Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "099766aee122", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.265, "client": "127.0.0.1:65167"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:02.549Z"
    quote: '{"ts": "2026-11-03T08:30:02.549Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "82dfd18acf2e", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.305, "client": "127.0.0.1:65169"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:05.727Z"
    quote: '{"ts": "2026-11-03T08:30:05.727Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "f334925ccf5d", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.268, "client": "127.0.0.1:65172"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:03.607Z"
    quote: '{"ts": "2026-11-03T08:30:03.607Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "9a299af34362", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.914, "client": "127.0.0.1:65170"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:04.668Z"
    quote: '{"ts": "2026-11-03T08:30:04.668Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "3d19d946eee1", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.762, "client": "127.0.0.1:65171"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:26.853Z"
    quote: '{"ts": "2026-11-03T08:30:26.853Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e59ebab0f636", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.002, "client": "127.0.0.1:65174"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:28.976Z"
    quote: '{"ts": "2026-11-03T08:30:28.976Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "00fa06e5b1fb", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.348, "client": "127.0.0.1:65176"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:30.037Z"
    quote: '{"ts": "2026-11-03T08:30:30.037Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "557f3300283f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.885, "client": "127.0.0.1:65177"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:30:31.093Z"
    quote: '{"ts": "2026-11-03T08:30:31.093Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "09bca9efb030", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.923, "client": "127.0.0.1:65178"}'
  - id: E13
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793694892-24941 (process_uptime_seconds 295.89)"
    quote: "faultline_chaos_enabled 0"
  - id: E14
    type: probe
    source: "GET /products/3 via scripts/probe.sh, request_id konan-1793694783-24860 (repeated as konan-1793694780-24853 and konan-1793694798-24891, same result)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793694783-24860"} -- HTTP 500'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:33:03.204Z"
    quote: '{"ts": "2026-11-03T08:33:03.204Z", "message": "unhandled exception: division by zero", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"} — throwing frame: shop.py", line 64, in get_product -> "turnover_score": units_ordered / product["units_in_stock"]'
  - id: E16
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793694892-24941"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 3'
  - id: E17
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793694655-24738 (baseline read, process_uptime_seconds 58.59, before any investigator probe beyond /health and /metrics)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no series)"
  - id: E18
    type: probe
    source: "GET /products via scripts/probe.sh, request_id konan-1793694689-24758"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}] -- HTTP 200'
  - id: E19
    type: log
    source: "lab/logs/app.log — every line with a 5xx status, grouped by request_id, whole process lifetime"
    quote: "1 \"request_id\": \"099766aee122\" (503); 1 \"request_id\": \"82dfd18acf2e\" (503); 1 \"request_id\": \"f334925ccf5d\" (503); 1 \"request_id\": \"konan-1793694780-24853\" (500); 1 \"request_id\": \"konan-1793694783-24860\" (500); 1 \"request_id\": \"konan-1793694798-24891\" (500)"
  - id: E20
    type: log
    source: "lab/logs/app.log — census of every status field, whole process lifetime (33 request events)"
    quote: "25 \"status\": 200; 2 \"status\": 201; 3 \"status\": 500; 3 \"status\": 503"
  - id: E21
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793694892-24941 (complete read; the templated counts 7+3 reconcile with the templated duration count of 10)"
    quote: "http_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 7\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 3\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products/2\"} 1\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products/{product_id}\"} 10"
  - id: E22
    type: probe
    source: "GET /openapi.json via scripts/probe.sh (interfaces lens)"
    quote: 'HTTP 200 — for /products/{product_id} the response schema is "schema":{"type":"object","additionalProperties":true} and the declared statuses are only 200 and 422; no 5xx is declared for any route and no product field is typed'
  - id: E23
    type: probe
    source: "GET /products/4 via scripts/probe.sh (software-defect lens)"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0} -- HTTP 200'
  - id: E24
    type: probe
    source: "GET /products/2 via scripts/probe.sh, request_id konan-1793694690-24768"
    quote: '{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39,"units_ordered":1,"turnover_score":0.02564102564102564} -- HTTP 200'
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-11-03T08:29:56.543Z — the only startup marker in the file; lab/logs/ holds no rotated backups"
    quote: '{"ts": "2026-11-03T08:29:56.543Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
gaps:
  - "The complaint names no time window, so nothing ties the 08:30:00–08:30:06Z injection window to the reporter's \"noise earlier\" by evidence. It is the only error episode in observable history, which makes it the only candidate — not a confirmed identification. Settling it needs the reporter, not telemetry."
  - "Observable history begins at the process start, 08:29:56.543Z (E25), and lab/logs/ holds no rotated backups. Any noise before that timestamp is unobservable, not absent — and the complaint says \"earlier\". If the reporter means an episode before 08:29:56Z, this investigation cannot see it."
  - "The actor who enabled chaos is not identified. The POST /chaos/enable and /chaos/disable request_ids are unstamped, which proves only that the caller was not the investigator; the eval harness and a human operator fit the same evidence equally."
  - "H1 explains errors, not slowness: E1 records extra_latency_ms 0 and every duration in the window is under 2 ms. If the \"noise\" the reporter means was slowness rather than errors, chaos mode does not explain it and the episode is unexplained."
  - "H3's mechanism rests on a single parameterized data point (E21): /products/2 is the only raw-path series, and the /products 503 series cannot distinguish raw from templated because that route has no parameter. The decisive test is the source line that sets the path label on the chaos-failure path — the target's source is outside the surface contract, so it was not read."
  - "H5 could not be tested. The decisive test is POST /orders for product 4, which the read-only boundary forbids by design; the alternative is reading the order handler's source, also outside the contract. A 422 rejection of a null-price order would be correct behaviour, so the hypothesis is an untested disjunction, not a defect."
  - "No non-investigator traffic was observed after 08:30:31.093Z — roughly ten minutes of silence to the conclusion. \"No user has been affected\" is evidenced; \"no user is being affected right now\" rests on an absence of traffic to observe, not on observed successes."
  - "4xx is fully censused for this process lifetime (E20 shows none), but user-visible wrongness that returns HTTP 200 — a wrong price, a wrong total — is not detectable from status codes and was not independently checked beyond the two orders whose totals match price x quantity (E8, E10, E18)."
  - "The process had run under 11 minutes at conclusion (E13). A slow memory climb, a restart loop with a long period, or any diurnal pattern cannot appear in a window this short."
usage:
  model: claude-opus-5
  tokens: 2288064
  wall_clock_seconds: 576
---

# Shop service handover check — no active incident, one latent defect found

## Summary

**No active incident.** The shop service is serving correctly as of 08:40Z: the business
surface — `/products`, `/products/{id}` for every stocked product, `/orders` — returns
2xx, and the complete error census for the whole process lifetime is six 5xx responses,
of which three were the closed injection window and three were my own probes (E19, E20).

The "noise earlier" has a strong candidate, with one honest caveat. An operational
fault-injection switch inside the target was enabled at 08:30:00.434Z with
`failure_rate 0.6, error_status 503` and disabled 6.35 s later at 08:30:06.786Z (E1, E2).
Inside that window 3 of 5 non-investigator requests returned 503 — exactly the declared
rate — each carrying its own `chaos_failure` attribution line (E3–E6), while other
requests in the same window succeeded (E7, E8). The switch reads off now (E13) and the
five non-investigator requests after it closed all returned 200/201 (E9–E12). The caveat:
the complaint gives no time window, and observable history starts only 3.9 s before the
switch opened (E25), so calling this window "the noise" is the only available inference,
not a proven identification. That is why the verdict is `no-active-incident` rather than
a root cause — see Gaps.

**One latent defect rides along, and it deserves a ticket.** `GET /products/{id}` raises
an unhandled `ZeroDivisionError` whenever a product's `units_in_stock` is 0, because the
handler computes `turnover_score = units_ordered / units_in_stock` with no guard (E14,
E15). Product 3 is the only row at 0 stock today (E18). It is **latent, not an incident**:
all three 500s carry my investigator stamp, and the exception counter was empty before I
probed (E16, E17, E19). But stock decrements with orders — product 2 shows
`units_in_stock 39` against `units_ordered 1` (E24) — so ordinary trade can drive a
popular product to 0 and arm the same defect on a page users actually browse. Confidence
high: deterministic, reproduced three times, with the throwing frame in the stack.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 08:29:56.543 | Process start, `faultline 0.1.0`. Observable history begins here; no rotated logs exist. | E25 |
| 08:29:57–08:29:58 | Healthy traffic: `/health` 200 x2, `/products` 200, `/products/1` 200. | — |
| **08:30:00.434** | **Config-change marker: chaos mode enabled**, `failure_rate 0.6`, `error_status 503`, `extra_latency_ms 0`. | E1 |
| 08:30:01.491 | `GET /products` -> 503, with `chaos_failure` attribution. | E3, E4 |
| 08:30:02.549 | `GET /products/2` -> 503. | E5 |
| 08:30:03.607 | `GET /products/1` -> 200 — success inside the window; failures are per-request, not per-input. | E7 |
| 08:30:04.668 | `POST /orders` -> 201, order 1 created. | E8 |
| 08:30:05.727 | `GET /products` -> 503. | E6 |
| **08:30:06.786** | **Config-change marker: chaos mode disabled.** Window closes, 6.35 s wide. | E2 |
| 08:30:26.853–08:30:31.093 | Five non-investigator requests, all 200/201: `/products`, `/products/1`, `POST /orders` (order 2), `/orders`, `/products/5`. | E9–E12 |
| 08:30:39 | Complaint raised (`startsAt`); investigation starts 08:30:47, 8 s later. | — |
| 08:30:54 onward | Investigator probes only. All `konan-` stamped. | E19 |
| ~08:33:03 | My own probe of `/products/3` triggers the latent `ZeroDivisionError`. | E14, E15 |
| 08:40:23 | Conclusion. Chaos still off, no new non-investigator traffic. | E13 |

## Investigation

**Baseline.** `/health` returned `{"status":"ok"}` with uptime 57.97 s — the process was
under a minute old, so every counter covers one short lifetime. The metrics read
immediately showed the shape of the story: `faultline_chaos_enabled 0` now, but a
`POST /chaos/enable` **and** a `POST /chaos/disable` in the counters, plus three 503s. I
did not stop at the green `/health` — the healthy-monitoring trap is a known shape — and
probed the business surface directly: `/products`, `/orders`, `/products/2` all 200.

**Triage.** The complaint is vague ("anything wrong"), so no lens domain could be excluded
by evidence and I spawned all three in parallel, each blind to the others:
`infra-process`, `interfaces`, `software-defect`. All three independently landed on the
chaos window and classed it `infra-process`. The `interfaces` and `software-defect` lenses
both discovered the `/products/3` 500 and both correctly labelled it latent on the
request-id stamp. `interfaces` added the OpenAPI contract gap.

**No deep-dive round.** H1 and H2 arrived from triage with deterministic, complete
evidence — config markers plus per-request attribution plus before/after rates for H1, a
stack frame plus three reproductions plus a corroborating counter for H2. The loop's rule
is that deep-dives fill evidence gaps rather than re-prove, so both went straight to the
judge. The one genuinely open hypothesis (H5, null price through the order path) has its
decisive test outside the read-only boundary, so a deep-dive agent would have been
coverage theater.

**Judge.** The adversarial judge, given only claims and verbatim evidence, earned its
place: it **invalidated** my original "the business surface serves correctly" wording as
self-contradictory against the `/products/3` finding, trimmed H1's "complete explanation"
claim, flagged that my error census covered only 5xx and left 4xx unexamined, and noted
that "unstamped means non-investigator" was asserted rather than proven.

**Targeted round after the judge.** Both of its cross-cutting doubts were cheap to settle
and I settled them myself rather than spawn agents. The full status census returned
25x200, 2x201, 3x500, 3x503 = 33, matching the 33 request events exactly: **zero 4xx**, so
the 5xx census is the complete error census and H1's "every non-investigator error" clause
holds (E20). And `scripts/probe.sh:21-24` unconditionally sets
`rid="konan-$(date +%s)-$$"` as `X-Request-ID` on every invocation, with no code path that
omits it — and it is konan's only route to the target — so the identity rule now rests on
code, not convention. One judge point was itself mistaken: it read E21 as an excerpt, but
the templated counts reconcile exactly (7 + 3 = the templated duration count of 10), so
that metrics read is complete. Everything else the judge asked for needs the target's
source or a `POST`; both are outside the surface contract, so they are recorded as Gaps
rather than pursued.

## Hypotheses

### H1 — chaos injection window (infra-process) — validated

The mechanism is not an inference from correlation: each 503 carries its own
`chaos_failure` line naming the injecting mechanism (E3), the window is bracketed by
explicit enable/disable markers (E1, E2), and the observed failure rate inside it — 3 of 5
non-investigator requests — matches the declared `failure_rate 0.6`. Successes interleaved
with failures (E7, E8) confirm a probabilistic per-request switch rather than a broken code
path. Before the marker: 4 requests, 0 errors. After the close: 5 requests, 0 errors
(E9–E12). The switch is off now (E13).

Classed `infra-process` per the contract's explicit instruction that an injected
degradation switch is `infra-process` even when its symptom is a gateway-shaped status.

What is **not** validated is the identification with the reporter's "noise", the identity
of the actor who flipped the switch, and the explanation of slowness if slowness is what
was meant. All three are in Gaps.

### H2 — unguarded division on zero stock (software-defect) — validated

The strongest finding in the investigation, and the only one with a complete mechanistic
chain. E15 names the throwing frame and the exact expression; E18 shows product 3 at
`units_in_stock: 0`; E23 is the control — a non-zero divisor returns 200 with
`turnover_score: 0.0`. Three probes gave the identical exception type (E14). The count
agrees across three independent surfaces: the exception counter at 3 (E16), the templated
500 counter at 3 (E21), and the request-id census at 3 (E19).

Latent, scoped honestly: "no user has hit this" holds **for this process lifetime only**,
since no rotated logs exist. And the defect is not frozen to product 3 — E24 shows stock
decrementing against orders, so another row can reach 0.

### H3 — raw path label on injected failures (software-defect) — inconclusive

The label discrepancy itself is a directly read fact (E21): the injected 503 on a
parameterized route sits under `path="/products/2"` while 200s and 500s on the same route
sit under `path="/products/{product_id}"`. What remains unproven is the *mechanism* and
the *projection*. One parameterized id is one data point; the `/products` series cannot
distinguish raw from templated, having no parameter. The cardinality consequence is a
reasonable extrapolation, not an observation. Reported as a latent observability finding
at the strength of the fact, not of the inference.

### H4 — OpenAPI contract gap (interfaces) — validated

E22 is a direct read of the served artifact and establishes each clause. The load-bearing
half is the untyped nullable `price`: the spec types no product field and sets
`additionalProperties: true`, while the service really serves `"price":null` with HTTP 200
(E18, E23) — a consumer cannot generate a correct client, and a client that multiplies
`price` has no warning from the contract. The missing 5xx declarations are weaker as a
defect, since omitting them is framework-default behaviour.

### H5 — null price through the order path (software-defect) — inconclusive

Only the premise is in evidence: product 4 carries `price: null` (E18, E23). Nothing
observed shows the order handler's arithmetic. The two completed orders have totals
consistent with price x quantity (E8, E10, E18), but that is consistency, not the
computation. "Would fail or produce a null total" is an untested disjunction, and one
branch — a 422 rejection — would be correct behaviour rather than a defect. The decisive
test is forbidden by the read-only boundary and was not attempted.

## Safe next steps

Read-only suggestions only.

1. **Ask the reporter for the time window and the symptom** of the noise they saw, and
   whether it was errors or slowness. This is the single highest-value next step: it either
   confirms H1 or reveals an episode in the unobservable period before 08:29:56Z. One
   question settles what no probe here could.
2. **File the `/products/{id}` zero-stock defect** against the target as a real bug with
   E14/E15/E18 attached. It is latent today and deterministic — the cheapest possible fix
   window is before a traded product reaches 0 stock, not after.
3. **Check whether any product is trending toward 0 stock** by reading `/products`
   periodically. This is the early-warning signal for H2 becoming user-visible, and it
   costs one GET.
4. **Read the target's `shop.py` around line 64 and the order handler** (in the target's
   own repository, outside this investigation's surface) to settle H3's label mechanism and
   H5's null-price question. Both are code reads, not probes.
5. **Confirm with whoever operates the lab** that the 08:30:00Z chaos window was
   intentional. The evidence proves the caller was not the investigator and nothing more;
   an unexplained injection switch flip would itself be worth a ticket.
6. **Re-check during real traffic.** The service has been quiet since 08:30:31Z, so the
   current all-clear rests partly on an absence of traffic to observe.

## Gaps

The frontmatter list, elaborated. Three of these are boundary-bound rather than oversights:
the target's source and any `POST` are outside the read-only surface contract by design, so
H3's mechanism and H5 cannot be settled from inside an investigation — they are handed off
as code reads instead.

The two that most limit this verdict:

- **Observable history is 3.9 seconds older than the injection window.** The process
  started at 08:29:56.543Z with no rotated logs (E25). The complaint says "earlier". If the
  reporter means anything before process start, this investigation is structurally blind to
  it and H1 is the wrong answer rather than an incomplete one.
- **The all-clear is partly an absence.** No non-investigator request has been served since
  08:30:31.093Z. "No user was affected" is evidenced by the census; "nothing is wrong right
  now" is evidenced for every surface I could probe myself, but the service has had no real
  traffic for about ten minutes, and silence is not the same as observed success.

Also open: 4xx is fully censused and empty for this lifetime (E20), but HTTP 200 responses
carrying wrong values are invisible to a status census and were not independently verified
beyond the two orders whose totals match price x quantity. And at under 11 minutes of
uptime, no slow leak, restart loop, or diurnal pattern could appear.
