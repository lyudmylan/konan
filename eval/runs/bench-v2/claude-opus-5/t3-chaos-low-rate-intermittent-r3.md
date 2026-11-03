---
konan_journal: 2
investigation:
  id: 2026-11-03-intermittent-shop-503s
  trigger: "manual — /konan adapter, human profile (docs/triggers.md). Complaint object: source=human, fingerprint=human-1793699395, labels.alertname=human-report, no severity stated by the reporter. startsAt=2026-11-03T09:49:55Z; investigation started 2026-11-03T09:50:11Z; trigger latency 16s."
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-03T09:50:11Z
  concluded: 2026-11-03T10:00:10Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational degradation switch inside the target was enabled at 09:49:50.058Z with failure_rate 0.08 and error_status 503, and short-circuits a share of incoming requests to 503 before handler work; it was still enabled at 09:59:48Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational degradation switch inside the target (chaos mode), enabled mid-window, injects 503 responses into a share of requests before handler work, and remains on."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E4, E5, E6, E7, E10, E11, E12, E14, E19, E20]
    evidence_against: []
  - id: H2
    statement: "A data-dependent defect in the target's own code fails on specific inputs (a particular product id or order payload), which is why only some users see errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7]
    evidence_against: [E6, E8, E9, E16, E13]
  - id: H3
    statement: "Demand during the traffic burst exhausted a resource and the errors are saturation under load."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E5, E7, E15, E21]
  - id: H4
    statement: "A process lifecycle fault — crash, restart loop, or hang — produced the intermittent errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E14, E22]
  - id: H5
    statement: "A boundary component — gateway, proxy, or an upstream/downstream party — produced the 503 responses."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E6, E5, E7, E13]
latent_findings:
  - statement: "The injected failures are invisible to three of the target's own observability surfaces at once: the request counter labels them with the raw path while handled requests use the route template, the latency summary's count for the templated route excludes them, and the exception counter has no series. An error-ratio or latency alert built on the templated label reads clean while the target is failing live traffic."
    evidence: [E13, E18, E21]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:45.104Z"
    quote: '{"ts": "2026-11-03T09:49:45.104Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:50.058Z"
    quote: '{"ts": "2026-11-03T09:49:50.058Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "59ed004e96fa", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:47.996Z"
    quote: '{"ts": "2026-11-03T09:49:47.996Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "585d62f1654d", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.947}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.294Z"
    quote: '{"ts": "2026-11-03T09:49:51.294Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "1d6c2b962897", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.294Z"
    quote: '{"ts": "2026-11-03T09:49:51.294Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "1d6c2b962897", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.135}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.424Z"
    quote: '{"ts": "2026-11-03T09:49:51.424Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "4a90109f91d0", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.424Z"
    quote: '{"ts": "2026-11-03T09:49:51.424Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "4a90109f91d0", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.128}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.337Z"
    quote: '{"ts": "2026-11-03T09:49:51.337Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "6e8ba5bb10ab", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.442}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.510Z"
    quote: '{"ts": "2026-11-03T09:49:51.510Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "8b91a770ff11", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.449}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.366Z"
    quote: '{"ts": "2026-11-03T09:49:51.366Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "15c07d571505", "event": "chaos_failure", "method": "GET", "path": "/orders"} / {"ts": "2026-11-03T09:49:51.366Z", "message": "GET /orders -> 503", "request_id": "15c07d571505", "status": 503, "duration_ms": 0.145}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:51.553Z"
    quote: '{"ts": "2026-11-03T09:49:51.553Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "6ffb929dd159", "event": "chaos_failure", "method": "POST", "path": "/orders"} / {"ts": "2026-11-03T09:49:51.554Z", "message": "POST /orders -> 503", "request_id": "6ffb929dd159", "status": 503, "duration_ms": 0.142}'
  - id: E12
    type: metric
    source: "/metrics @ 2026-11-03T09:59:48Z, request_id konan-1793699988-27594"
    quote: "faultline_chaos_enabled 1"
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-03T09:59:48Z, request_id konan-1793699988-27594"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter — header present, no series lines follow"
  - id: E14
    type: metric
    source: "/metrics @ 2026-11-03T09:50:20Z and @ 2026-11-03T09:59:48Z"
    quote: "process_uptime_seconds 35.882267334032804 (09:50:20Z), then process_uptime_seconds 602.9938139170408 (09:59:48Z)"
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-03T09:50:20Z and @ 2026-11-03T09:59:48Z"
    quote: "process_max_rss_bytes 47104000 — identical value in both reads"
  - id: E16
    type: probe
    source: "/products/2, request_id konan-1793699546-27479"
    quote: '-- HTTP 200 in 0.001478s; body {"id":2,"name":"Toaster","price":23.0,...}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:50:17.517Z"
    quote: '{"ts": "2026-11-03T09:50:17.517Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793699417-27406", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 1.345}'
  - id: E18
    type: metric
    source: "/metrics @ 2026-11-03T09:59:48Z, request_id konan-1793699988-27594"
    quote: 'http_requests_total{method="GET",path="/products/2",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 17'
  - id: E19
    type: metric
    source: "/metrics @ 2026-11-03T09:50:20Z and @ 2026-11-03T09:59:48Z"
    quote: 'http_requests_total{method="GET",path="/orders",status="503"} 1 / http_requests_total{method="GET",path="/products/2",status="503"} 1 / http_requests_total{method="POST",path="/orders",status="503"} 2 — the same three series, unchanged across both reads'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-03T09:49:50.059Z"
    quote: '{"ts": "2026-11-03T09:49:50.059Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "59ed004e96fa", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.745, "client": "127.0.0.1:49383"}'
  - id: E21
    type: metric
    source: "/metrics @ 2026-11-03T09:59:48Z, request_id konan-1793699988-27594"
    quote: 'http_request_duration_seconds_sum{method="POST",path="/orders"} 0.004363373853266239 / http_request_duration_seconds_count{method="POST",path="/orders"} 6 / http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 17'
  - id: E22
    type: probe
    source: "/health, request_id konan-1793699417-27406"
    quote: '{"status":"ok","uptime_seconds":32.423068459145725} -- HTTP 200 in 0.003837s'
gaps:
  - "No telemetry exists before 2026-11-03T09:49:45.104Z: the log's first line is the startup marker and no rotation backups are present. The complaint names 'the last few minutes', so part of the complained-of window is unobserved. Either this process served no traffic before startup, or an earlier instance's log is gone — the evidence cannot separate those, so errors before the switch cannot be excluded."
  - "Nothing identifies the origin of the POST /chaos/enable call that flipped the switch (E20). The client field reads 127.0.0.1 and the request id carries no investigator prefix, but konan's surface shows no caller identity, no actor and no authorization. In a real incident this, not the 503s, is the open question."
  - "No edge, proxy or client-side telemetry is in scope. Errors returned to users without reaching the target would leave no trace in this log, so H5 is refuted only for the four 503s that were logged, not for the user reports as a class."
  - "The observed failure share (4 of 31 post-switch user requests) is consistent with the configured failure_rate of 0.08 but far too small a sample to measure it; at n=31 the interval spans roughly 5%–29%. The rate in this journal is the configured value, never a measured one."
  - "Whether the injection roll applies to every route is unknown: /health, /metrics and the operator paths may be exempt, so the denominator above may be wrong in kind as well as in count."
  - "The error counters have not moved since 09:49:51.582Z (E19) because no non-investigator traffic has arrived since. Current impact per unit of live traffic is therefore unmeasured — the switch is armed, but exposure depends on traffic the window does not contain."
  - "Only one resource series is exposed (process_max_rss_bytes, a high-water mark) and no platform limits are readable. Saturation is excluded by the latency shape of the failures rather than by demonstrated headroom; no CPU, descriptor, worker or queue-depth metric exists on this surface."
  - "Three of the taxonomy's six classes have no lens file in this repo (load-saturation, third-party, data-db). load-saturation was covered by the metrics above; third-party and data-db were excluded because docs/lab.md records that the target has no database and no third-party dependency. No dedicated lens examined them."
usage:
  model: claude-opus-5
  tokens: 1858591
  wall_clock_seconds: 599
---

# Intermittent 503s in the shop from an enabled degradation switch

## Summary

**This is an active incident, not noise.** An operational degradation switch inside
faultline — chaos mode — was enabled at 09:49:50.058Z with `failure_rate: 0.08`,
`error_status: 503` and `extra_latency_ms: 0` (E2), and it was still enabled at
09:59:48Z, ten minutes later (E12). While it is on, the target returns 503 to a share
of incoming requests, short-circuiting them at the request layer before any handler
work: the failures completed in 0.128–0.145 ms against 0.44 ms for successful responses
on the same route (E5, E7, E10, E11 vs E8, E9).

Attribution is direct rather than circumstantial. Every one of the four 503s in the log
carries a `chaos_failure` line written by the target's own logger with the **same
`request_id` at the same millisecond** (E4/E5, E6/E7, E10, E11), and the whole 54-line
file contains exactly four `chaos_failure` lines and exactly four 503 responses — the
accounting closes with nothing unexplained.

The reporter's description fits the mechanism precisely, which is why it is misleading.
"Works on retry" holds because the failure is rolled per request and is not sticky to
input, route or client: `GET /products/2` returned 200, then 503, then 200 again inside
173 ms (E8, E7, E9). "Most people notice nothing" is true of the aggregate and hides the
shape of the damage — two of the four failures were `POST /orders` (E4/E5, E11), which
is a lost order rather than a blink, and a client that retries a failed non-idempotent
write risks a duplicate order. Confidence in the mechanism is high; confidence that
these four logged failures are the same errors the users saw is lower, because no
quoted line carries a user or session identity and the logged traffic is a 465 ms burst.

Impact in evidence: 4 failures among 31 post-switch user requests. That is consistent
with the configured 8% and does not measure it (see Gaps). None of the failures was
caused by this investigation — two are POSTs, which the GET-only probe cannot issue,
and both investigator probes ran 25 s and 155 s after the last 503.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 09:49:45.104Z | Process starts, `faultline 0.1.0`. No telemetry exists before this line. | E1 |
| 09:49:45.854–09:49:47.996Z | Five user requests, all 200/201. Last known-good: `POST /orders -> 201`. | E3 |
| **09:49:50.058Z** | **Switch marker: chaos mode enabled, `failure_rate` 0.08, `error_status` 503, `extra_latency_ms` 0.** | E2 |
| 09:49:50.059Z | The enabling call itself: `POST /chaos/enable -> 200`, same request id as the marker. Caller unidentified. | E20 |
| 09:49:51.294Z | First user-visible failure, 1.24 s after the switch: `POST /orders -> 503`. | E4, E5 |
| 09:49:51.337Z | `GET /products/2 -> 200`. | E8 |
| 09:49:51.366Z | `GET /orders -> 503`. | E10 |
| 09:49:51.424Z | `GET /products/2 -> 503` — same input that just succeeded. | E6, E7 |
| 09:49:51.510Z | `GET /products/2 -> 200` — and succeeds again. | E9 |
| 09:49:51.553Z | `POST /orders -> 503`, the fourth and last logged failure. | E11 |
| 09:50:17.517Z | First investigator probe, `/health` 200, uptime 32.4 s. | E17, E22 |
| 09:59:48Z | Switch still on; 503 counters unchanged; uptime 603 s on the same process. | E12, E14, E19 |

Onset is a step, not a ramp: zero failures before the marker, four after it. The marker
is the configuration-change event the timeline turns on.

## Investigation

**Baseline** (09:50:11Z onward) read `/health`, `/metrics` and the full 54-line log.
Two facts in the baseline shaped everything after: `faultline_chaos_enabled 1`, and
`http_exceptions_total` carrying no series at all — errors without exceptions.

**Triage** spawned all three available lenses in parallel, each blind to the others
(software-defect, infra-process, interfaces), with no hint of a conclusion in their
prompts. They converged independently on the switch. The software-defect lens settled
data-dependence as negative and found the latent instrumentation defect; the
infra-process lens established no-restart and no-saturation arithmetically; the
interfaces lens settled the boundary question and classified the mechanism back to
infra-process, outside its own domain. Three of six taxonomy classes have no lens file
here — recorded under Gaps rather than assumed clean.

**Deep-dive was skipped deliberately.** The skill reserves it for filling evidence
gaps, not re-proving; same-`request_id` attribution on all four failures plus the
parameterised switch marker is already deterministic, so the hypotheses went straight
to the judge.

**Judge.** The adversarial judge received only the hypothesis list and the verbatim
evidence, no lens reasoning and no narrative. It confirmed H1's mechanism and
invalidated H2–H5, and it found four real defects in the ledger, all of which changed
this journal:

1. The rate claim was overstated — corrected to "consistent with the configured value",
   with the arithmetic in Gaps.
2. The liveness claim rested on a 09:50:20Z gauge read while a later scrape existed
   whose value had not been quoted. Closed with a fresh read at 09:59:48Z (E12).
3. The origin of the enabling call was unevidenced and unmentioned. Now a gap, and the
   open question of this incident.
4. "Most people notice nothing" was being carried as a finding when no user identity
   exists in the telemetry. Reworded to what the evidence supports.

It also noted that the `konan-` prefix test for probe attribution was vacuous as stated,
because no log line carrying such an id had been quoted; E17 now closes that, and it
independently confirms investigator traffic does appear in this log.

**One judge correction is rejected, on the record.** The judge argued `infra-process` is
the wrong class, since the switch is an application feature in the application's own
logger namespace reached through its own HTTP endpoint. That reasoning is sound in
general and wrong against this contract: `report-contract.md` defines `infra-process` to
include "internal operational switches … configuration/feature/chaos toggles that change
runtime behavior", states that "an injected degradation switch is `infra-process` even
when its symptom is gateway-shaped statuses or added latency", and defines the cause id
`degradation-switch` as "an operational switch inside the target (chaos, kill switch,
feature flag)". `journal.schema.json` enforces the pair, rejecting `degradation-switch`
under any other class. The definitions were written against exactly this disagreement
(benchmark finding 2026-08-19, #63). The judge could not see the contract by design, so
the call is the orchestrator's: class `infra-process`, cause `degradation-switch`.

## Hypotheses

### H1 — degradation switch injecting 503s · **validated**

The switch marker names its own parameters (E2) and the per-failure markers name the
mechanism on each request id (E4, E6, E10, E11). Declared `error_status` 503 matches
every observed failure status. Failures are an order of magnitude faster than successes
on the same routes (E5, E7 vs E8, E9) and `extra_latency_ms` is 0 — the request is
rejected at the request layer with no handler latency. The switch was still on at the
final read (E12) with no `chaos_disabled` event anywhere in the log.

Two sub-claims were explicitly weakened. The *rate*: 8% is the configured value, not a
measurement (Gaps). *Randomness*: the field is named `failure_rate` and the behaviour is
consistent with a per-request roll, but four events cannot distinguish a random roll
from a fixed every-Nth rule, and no sampling logic is in evidence — so this journal
claims "a share of requests", not "a uniformly random 8%".

### H2 — data-dependent software defect · **invalidated**

The shape of the complaint made this the leading rival: "most inputs succeed, specific
inputs fail" is a real defect shape, and E7 is a 503 on a specific product id. It dies
on the same input alternating: `GET /products/2` gave 200 at .337Z, 503 at .424Z, 200 at
.510Z (E8, E7, E9) and 200 again under probe (E16). No input-keyed defect alternates on
the same input within 173 ms. The decisive evidence is E6, which names the cause on that
exact request id. Note that E13 (no exception series) is *weak* support here, as the
judge pointed out: a defect returning 503 deliberately would also leave that counter
empty. The attribution, not the counter, kills H2.

### H3 — load saturation · **invalidated**

Failures were *faster* than successes (E5, E7 vs E8, E9); saturation makes requests
slower, not quicker. Mean latencies stayed sub-millisecond (E21: 0.73 ms for POST
/orders over 6 requests), peak RSS was identical across reads nine minutes apart (E15),
and the switch marker declares `extra_latency_ms: 0` (E2). The weaker form — "no
resource was under any pressure" — is *not* established: max RSS is a high-water mark,
no limit is readable, and only one resource is instrumented. Recorded under Gaps.

### H4 — process lifecycle fault · **invalidated**

One startup marker and one pid in the whole file (E1), and uptime advanced monotonically
and consistently: 32.42 s at 09:50:17Z (E22) and 35.88 s → 602.99 s across reads nine
minutes apart (E14). Startup time plus uptime lands back on E1's timestamp from two
independent readings. No counter reset. Valid for the observed window only — it says
nothing about the minutes before 09:49:45.104Z.

### H5 — boundary or gateway component · **invalidated for the logged errors**

The 503s are generated inside the target process: the target's own `faultline.request`
logger writes the attribution line for each failing request id (E4, E6), which no proxy
could do, and the fast-fail timing is the opposite of a timing-out dependency (E5, E7).
`docs/lab.md` records that the target has no database and no third-party dependency.
Refuted for the four logged failures; **untested** for any error that never reached the
target, since no edge telemetry is in scope (Gaps).

## Safe next steps

Read-only. Remediation — including any change to the switch state — is an operator
decision outside this investigation's boundary, and outside konan's.

1. Re-read `/metrics` for `faultline_chaos_enabled` to confirm whether the switch is
   still on at the time of reading; the gauge, not the frozen 503 counters, is the live
   signal. The counters will not move until real traffic arrives.
2. Establish the origin of the `POST /chaos/enable` call at 09:49:50.059Z (E20) — who or
   what flipped the switch, through which path, and whether that was intended. This is
   the unanswered question of the incident; the 503s downstream of it are fully
   explained.
3. Check whether retained history exists for the complaint's earlier minutes — a rotated
   log, an earlier instance's file, or any counter scrape taken before 09:49:45Z — to
   determine whether that window is dark or genuinely empty.
4. Read `POST /orders` outcomes for the burst window against order ids (`order_created`
   events show ids 1–4) to size how many order submissions were rejected, and check for
   duplicate orders from client-side retries of the failed writes.
5. Treat the latent finding as an observability gap worth verifying independently:
   confirm whether an error-ratio alert on the templated route label would have fired at
   all during this window.

## Gaps

The frontmatter list, in short: telemetry begins at process startup, so part of the
complained-of window cannot be seen and pre-switch errors cannot be excluded; the caller
that enabled the switch is unidentified; no edge telemetry exists, so H5 is refuted only
for errors that reached the target; the observed failure share is consistent with the
configured rate but cannot measure it, and the denominator may be wrong in kind if some
routes are exempt from the roll; live impact per unit traffic is unmeasured because no
user traffic has arrived since the burst; saturation is excluded by latency shape rather
than demonstrated headroom, with one high-water-mark resource series and no readable
limits; and three of six taxonomy classes have no lens in this repo, two of them
excluded by the lab contract rather than by examination.
