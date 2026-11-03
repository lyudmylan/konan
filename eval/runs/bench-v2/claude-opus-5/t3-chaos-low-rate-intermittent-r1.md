---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-intermittent-503s
  trigger: "manual — /konan human report; source human, fingerprint human-1793698231, alertname human-report, no severity stated; startsAt 2026-11-03T09:30:31Z, investigation start 2026-11-03T09:30:41Z (trigger latency 10s)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-03T09:30:41Z
  concluded: 2026-11-03T09:36:23Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational degradation switch inside the target — chaos mode — was enabled at 09:30:26.453Z with error_status 503 and failure_rate 0.08 and is still armed at conclusion, so the target returns 503 to a subset of requests while identical requests succeed on retry."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational degradation switch inside the target (chaos mode), enabled at 09:30:26.453Z with failure_rate 0.08 and error_status 503 and still armed, makes the target return 503 to a subset of requests; identical requests succeed on retry."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E15]
    evidence_against: []
  - id: H2
    statement: "The errors come from a defect in the target's own code raising an unhandled exception on some specific input (a data-dependent failure)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E9, E18, E3, E5, E7]
  - id: H3
    statement: "The errors come from the process dying, restarting, or hanging — a lifecycle fault."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E14, E15]
  - id: H4
    statement: "The errors come from demand exceeding capacity (resource exhaustion or queueing under load), with added latency for users."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E16, E4, E6, E8, E9]
  - id: H5
    statement: "The 503s originate in a boundary component outside the target's own code — a proxy, load balancer, or gateway tier failing on its own."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E7, E2]
  - id: H6
    statement: "Secondary, not the incident: the target counts failures on a parametrized route under the raw request path while counting successes under the route template, so the two never join one series and a per-route error rate cannot be read from a single label set."
    incident_class: software-defect
    state: validated
    evidence_for: [E17, E12]
    evidence_against: []
latent_findings:
  - statement: "Metrics label split on parametrized routes: failures are counted under the raw path (/products/2) and successes under the template (/products/{product_id}), for both the request counter and the duration counter. An alert built on the templated label would not have seen these 503s, and each failing id adds a new series. Observed only on chaos-injected failures — whether a handler-raised failure escapes templating the same way is untested."
    evidence: [E17, E12]
gaps:
  - "The whole telemetry window begins at process start 09:30:21.509Z (E1) and lab/logs/app.log has no rotated backups (.1–.3 absent), so the complaint's 'last few minutes' is almost entirely earlier than any available log line; errors before 09:30:21.509Z can be neither confirmed nor excluded."
  - "The reporter gave no first-error time, no affected user, and no order or product id, so the complaint cannot be tied to specific logged requests — the match rests on symptom shape (intermittent, succeeds on retry) only."
  - "Every logged client is loopback (127.0.0.1) and non-investigator traffic is deliberately unstamped, so attribution reaches 'not the investigator's probes' and no further; that the affected requests were real end users is not shown by telemetry."
  - "Who enabled the switch and why is outside the investigator's surface: the enabling request is logged with request_id e373a18ebcf1 (E2), but the operator surface that served it is not investigator-readable, so intent (deliberate exercise vs accident) is unknown."
  - "The surface offers no CPU, queue-depth, or concurrency metric, so H4 was refuted from durations, an unchanged RSS gauge, and the switch's extra_latency_ms 0 rather than from a direct saturation reading."
  - "No 503 response body was captured: the failures fell on non-investigator traffic and none of the investigator's own probes were selected by the switch, so the error payload users saw is unknown."
  - "Error counters did not move between 09:30:28Z and conclusion at 09:36:23Z (E12), but no non-investigator traffic is logged in that span either — so whether the switch is still hitting live requests is untested, not shown to be quiet."
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:21.509Z"
    quote: '{"ts": "2026-11-03T09:30:21.509Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:26.453Z"
    quote: '{"ts": "2026-11-03T09:30:26.453Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "e373a18ebcf1", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.645Z"
    quote: '{"ts": "2026-11-03T09:30:27.645Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "c3b4521d022c", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.645Z"
    quote: '{"ts": "2026-11-03T09:30:27.645Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "c3b4521d022c", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.137, "client": "127.0.0.1:49202"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.688Z"
    quote: '{"ts": "2026-11-03T09:30:27.688Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "d48890764b7e", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.688Z"
    quote: '{"ts": "2026-11-03T09:30:27.688Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "d48890764b7e", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.135, "client": "127.0.0.1:49205"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.817Z"
    quote: '{"ts": "2026-11-03T09:30:27.817Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "9a7db00736e6", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.818Z"
    quote: '{"ts": "2026-11-03T09:30:27.818Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "9a7db00736e6", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.132, "client": "127.0.0.1:49214"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:27.904Z"
    quote: '{"ts": "2026-11-03T09:30:27.904Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "59edaedb3c97", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.441, "client": "127.0.0.1:49217"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:30:24.399Z"
    quote: '{"ts": "2026-11-03T09:30:24.399Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "fd6e834b3dec", "event": "request", "method": "POST", "path": "/orders", "status": 201}'
  - id: E11
    type: metric
    source: "/metrics @ request_id=konan-1793698263-26714, re-read at conclusion 09:36:23Z"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: metric
    source: "/metrics @ request_id=konan-1793698263-26714"
    quote: 'http_requests_total{method="GET",path="/products/2",status="503"} 2 / http_requests_total{method="POST",path="/orders",status="503"} 1 — the only non-2xx series in the scrape'
  - id: E13
    type: metric
    source: "/metrics @ request_id=konan-1793698263-26714, two scrapes 150s apart"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      (no series line follows)
  - id: E14
    type: probe
    source: "/health @ request_id=konan-1793698258-26701"
    quote: |-
      {"status":"ok","uptime_seconds":37.00431754090823}
      -- HTTP 200 in 0.004519s request_id=konan-1793698258-26701
  - id: E15
    type: metric
    source: "/metrics, three scrapes between 09:30:43Z and 09:36:23Z"
    quote: "process_uptime_seconds 42.38826450007036 → 150.8181704999879 → 361.2063906660769 (monotonic; no reset)"
  - id: E16
    type: metric
    source: "/metrics, three scrapes between 09:30:43Z and 09:36:23Z"
    quote: "process_max_rss_bytes 47431680 (byte-identical in every scrape)"
  - id: E17
    type: metric
    source: "/metrics @ request_id=konan-1793698263-26714"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 15 / http_requests_total{method="GET",path="/products/2",status="503"} 2 / http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 15 / http_request_duration_seconds_count{method="GET",path="/products/2"} 2'
  - id: E18
    type: probe
    source: "/products/2 @ request_id=konan-1793698402-26807"
    quote: |-
      {"id":2,"name":"Toaster","price":23.0,"units_in_stock":36,"units_ordered":4,"turnover_score":0.1111111111111111}
      -- HTTP 200 in 0.001642s request_id=konan-1793698402-26807
usage:
  model: claude-opus-5
  tokens: 1761243
  wall_clock_seconds: 342
---

# Intermittent shop 503s from an armed degradation switch

## Summary

**Not nothing — and still active at the time of writing.** An operational degradation
switch inside the target (chaos mode) was enabled at 09:30:26.453Z, configured to answer
a share of requests with HTTP 503 and no added latency (`failure_rate: 0.08`,
`error_status: 503`, `extra_latency_ms: 0`, E2). Every 503 in the observed window is the
target labelling its own injected failure: each `chaos_failure` warning shares a
`request_id` and a timestamp with the 503 access line it belongs to (E3/E4, E5/E6,
E7/E8). The gauge `faultline_chaos_enabled 1` still read 1 on a re-scrape at conclusion,
about six minutes after the switch went on (E11), so the condition had not cleared.

The reporter's symptom description is accurate and the reporter's conclusion is not. The
mechanism is random per request, not per input: `GET /products/2` returned
200, 503, 200, 503, 200 inside 350 ms (E4, E8, E9), so a retry genuinely does work and
most requests genuinely are unaffected — which is exactly why this hides from the people
looking at it. `/health` answered 200 throughout (E14): the healthy-monitoring shape,
where the health endpoint is green while business traffic fails.

Impact is understated by the complaint in one respect worth naming: a **write** failed,
not only reads. `POST /orders` returned 503 (E5, E6) — an order attempt lost, where a
read failure costs only a reload. Confidence in the mechanism is high (the target
declares its own configuration and labels every injected failure). Confidence in the
blast radius is low: see Gaps — the telemetry window is about 15 minutes old in total and
begins after the complaint's "last few minutes" had already started.

## Timeline

- **09:30:21.509Z** — process starts, faultline 0.1.0 (E1). This is the earliest
  telemetry of any kind; nothing before it is observable.
- **09:30:21.5Z – 09:30:26.4Z** — five requests, all 200 or 201. Last clean write:
  `POST /orders -> 201` at 09:30:24.399Z (E10). No failure precedes the switch.
- **09:30:26.453Z** — **configuration-change marker**: chaos mode enabled by request
  `e373a18ebcf1`, with `failure_rate 0.08`, `error_status 503`, `extra_latency_ms 0`
  (E2). The behaviour change begins here.
- **09:30:27.645Z** — first injected failure, 1.2 s after the marker:
  `GET /products/2 -> 503` (E3, E4).
- **09:30:27.688Z** — `POST /orders -> 503` (E5, E6): a write path fails.
- **09:30:27.817Z** — `GET /products/2 -> 503` again (E7, E8).
- **09:30:27.904Z** — `GET /products/2 -> 200`, 86 ms after the previous 503 on the
  identical path (E9). The retry-succeeds behaviour, in the record.
- **09:30:31Z** — the human complaint is raised (`startsAt`).
- **09:30:41Z** — investigation starts (trigger latency 10 s).
- **09:36:23Z** — conclusion. Switch still armed (E11); uptime 361 s and monotonic, one
  process, never restarted (E15).

## Investigation

**Baseline** — `/health` green (E14), metrics scraped, 54-line log read. The baseline was
itself already non-clean: the error counters and `faultline_chaos_enabled 1` were
visible in the first scrape, and the process was only 42 s old.

**Triage** — all three available lenses (infra-process, software-defect, interfaces) were
spawned in parallel, blind to each other, each given only its lens file, the surface
contract, the verbatim complaint, and the baseline summary. The complaint is vague, so no
lens could be excluded by evidence beforehand. All three independently reached the switch
and all three independently reported no evidence in their own primary failure families.
Two of the three independently flagged the metrics label split (H6).

**Deep-dive** — skipped deliberately. The loop budgets deep-dives to fill evidence gaps;
H1's triage evidence is deterministic and complete (the switch declares its own
configuration, and every 503 carries a same-`request_id` injected-failure label), so
there was no gap for a deep-dive to fill. One read-only confirmation probe of the failing
route was taken instead (E18).

**Judge** — one fresh judge, given the hypothesis list and the verbatim evidence ledger
only, with no lens reasoning or narrative. It validated H1 and H6, invalidated H2–H5, and
trimmed three over-readings from the H1 wording, which this journal honours: the switch's
**position in the request path** ("ahead of the handlers") is an inference from log order
and from failures being faster than successes (0.132–0.137 ms against 0.441 ms), not a
proven fact, so no stack position is claimed above; **0.08 is the configured value**, not
a measured rate, so no observed error rate is asserted; and **"user-visible" overstates
the evidence**, since all logged clients are loopback. Its settling-evidence requests all
named telemetry outside the surface contract or outside the retained window, so a second
round could not have obtained them — they are recorded as Gaps rather than pursued.

## Hypotheses

### H1 — degradation switch (chaos mode) — **validated**

For: the switch marker with its full configuration (E2); three injected-failure warnings
each sharing a `request_id` with its 503 access line (E3/E4, E5/E6, E7/E8); the gauge on
at first scrape and still on at conclusion (E11); the only non-2xx series matching the
three labelled failures exactly (E12); a clean pre-marker window (E1, E10); the identical
path succeeding 86 ms after failing (E9); one unrestarted process throughout (E15).
Against: nothing found. The failing request ids carry no `konan-` prefix, so these are not
the investigator's own probes.

### H2 — data-dependent unhandled exception — **invalidated**

`http_exceptions_total` is registered but emits no series at all, in two scrapes 150 s
apart, and no log line in the window carries an `unhandled_exception` event, an
`exception_type` field, or a `stack` field (E13). The "specific input" premise dies
separately: the same id both fails and succeeds (E9), and the investigator's own read of
that exact route returned 200 (E18). Every observed 503 already has an injected-failure
partner line (E3, E5, E7).

### H3 — process lifecycle fault — **invalidated**

One `startup` event only, at the head of the log (E1); `process_uptime_seconds` rising
monotonically 42 → 151 → 361 across three scrapes with no reset (E15); `/health`
answering in 4.5 ms and the business route in 1.6 ms, so not hung (E14, E18).

### H4 — load saturation — **invalidated**

The switch declares `extra_latency_ms: 0` (E2); peak RSS is byte-identical across the
window (E16); all durations are sub-millisecond (E4, E6, E8, E9); and successes are
interleaved between failures inside the same 350 ms (E9), which no queueing or exhaustion
model produces. Note the judge's caveat: the surface has no CPU or queue-depth metric, so
this rests on durations, RSS, and the declared configuration (recorded under Gaps).

### H5 — boundary component (proxy, gateway) — **invalidated**

The 503s are written by the target's own loggers, `faultline.request` and
`faultline.chaos` (E2, E3, E5, E7), with each injected-failure id matching the id on the
503 response line. A tier outside the target could not write those lines, so the target
produced these 503s itself. This matters for classification: an internal operational
switch is `infra-process`, not `interfaces`, even though 503 is a gateway-shaped status.

### H6 — metrics label split — **validated**, secondary

Successes on the parametrized route are counted under the template and failures under the
raw path, for both the counter and the duration series (E17, E12). The two label values
never join, so a per-route error rate is not readable from one series, and each failing id
adds cardinality. Carried as a latent finding, not as the incident. Scope limit, per the
judge: only chaos-injected failures were observed, so whether a handler-raised failure
also escapes templating is untested.

## Safe next steps

Read-only only; remediation is out of scope for this journal and for konan.

1. **Escalate the switch state to whoever owns the target's operational toggles.** The
   enabling request is identified (`request_id e373a18ebcf1`, E2) but intent is not
   observable from telemetry — confirm with that owner whether this was a deliberate
   exercise or an accident left armed. That answer, not more telemetry, decides whether
   this is an incident or a test.
2. **Re-scrape `faultline_chaos_enabled` to establish current state before acting on this
   journal** — it was 1 at 09:36:23Z (E11) and the state can change without any log line
   that the investigator can see other than a `chaos_disabled` event.
3. **Watch `chaos_failure` events and the non-2xx `http_requests_total` series for new
   increments** to measure live user impact; the counters stood still after 09:30:28Z, but
   no non-investigator traffic is logged in that span either, so nothing is yet shown to
   have stopped.
4. **Ask the reporter for a first-error time and any order id**, which would test whether
   impact predates process start at 09:30:21.509Z (E1) — the one question that could close
   the biggest gap below, and it is answerable only by a human.
5. **Check any alerting built on the templated path label** against H6 (E17): on this
   evidence such a rule would not have fired for these 503s, which is consistent with the
   incident reaching a human by word of mouth rather than by alert.

## Gaps

1. **The telemetry window is shorter than the complaint.** Everything observable starts at
   process start 09:30:21.509Z (E1), and `lab/logs/app.log` has no rotated backups, so the
   "last few minutes" the reporter describes is mostly earlier than any line that exists.
   Errors before 09:30:21.509Z can be neither confirmed nor excluded — including the
   possibility of a second, earlier cause.
2. **The complaint cannot be tied to specific requests.** No first-error time, no affected
   user, no order or product id was given; the match rests on symptom shape (intermittent,
   succeeds on retry, mostly unnoticed) agreeing with the mechanism.
3. **Attribution stops at "not the investigator".** All logged clients are loopback and
   non-investigator traffic is deliberately unstamped, so telemetry shows these were not
   konan's probes, and does not show that they were real end users.
4. **Intent behind the switch is outside the surface.** The operator surface that served
   the enabling request is not investigator-readable, by the lab boundary.
5. **No saturation metric exists.** The surface offers no CPU, queue-depth, or concurrency
   gauge, so H4 was refuted indirectly.
6. **H6's general mechanism is assumed.** Only injected failures were observed escaping
   path templating; a handler-raised failure was never produced to test.
7. **No 503 body was captured.** The failures fell on traffic that is not the
   investigator's, and no investigator probe was selected by the switch, so what the
   affected requests actually received is unknown.
