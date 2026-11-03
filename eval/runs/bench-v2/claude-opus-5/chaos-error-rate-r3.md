---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-intermittent-503s
  trigger: "manual — /konan adapter, profile human; complaint object: source human, fingerprint human-1793668660, labels.alertname human-report (no severity stated by the reporter), startsAt 2026-11-03T01:17:40Z; investigation start 2026-11-03T01:17:45Z; trigger latency 5s"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-03T01:17:45Z
  concluded: 2026-11-03T01:27:42Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational degradation switch inside the target was enabled at 01:17:18.465Z with failure_rate 0.4 and error_status 503, and was still injecting failures at the last read (01:19:40.838Z); while on it returns a self-declared 503 for a random share of requests, which is why shop requests fail intermittently and succeed on retry."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational degradation switch inside the target (enabled 01:17:18.465Z, failure_rate 0.4, error_status 503, extra_latency_ms 0) returns 503 for a random share of requests without executing the product-lookup path, producing intermittent failures that succeed on retry."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E15, E16, E17, E18, E19]
    evidence_against: []
  - id: H2
    statement: "The failures come from a defect in the target's own code — an unhandled exception, or a deterministic per-input defect on specific products."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E9, E10, E15, E16]
  - id: H3
    statement: "The failures come from a boundary component or an external dependency — a proxy or gateway tier failing on its own, or an upstream provider."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E5, E9, E15]
  - id: H4
    statement: "The order failures the complaint reports have a cause of their own, separate from H1."
    incident_class: software-defect
    state: inconclusive
    evidence_for: []
    evidence_against: [E13]
  - id: H5
    statement: "The failures are load-driven — demand exceeding capacity through saturation, queueing, or resource exhaustion."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E12, E18]
latent_findings:
  - statement: "The health endpoint reports process liveness only and carries no field for the degradation state, so a green health dashboard is not evidence against an incident of this shape — it stayed 200 throughout while shop traffic was failing."
    evidence: [E8, E9, E10, E11]
  - statement: "Failures on a parameterized route are counted under the literal request path while successes are counted under the route template, so each product id mints its own 503 series: failure-series cardinality is unbounded, and per-id failures do not aggregate with the successes of the same route."
    evidence: [E10, E20]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:10.481Z"
    quote: '{"ts": "2026-11-03T01:17:10.481Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:15.407Z — last non-investigator request before the marker"
    quote: '{"ts": "2026-11-03T01:17:15.407Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "9b329fde9473", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.764, "client": "127.0.0.1:63209"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:18.465Z — the behavior-change marker"
    quote: '{"ts": "2026-11-03T01:17:18.465Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "0f37c8283ba0", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:18.465Z — the request that set the switch, same request_id as E3"
    quote: '{"ts": "2026-11-03T01:17:18.465Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "0f37c8283ba0", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.495, "client": "127.0.0.1:63210"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:20.520Z — first failure after the marker, non-investigator traffic"
    quote: '{"ts": "2026-11-03T01:17:20.520Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "8f58f4187a3b", "event": "chaos_failure", "method": "GET", "path": "/products"} / {"ts": "2026-11-03T01:17:20.520Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "8f58f4187a3b", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.271, "client": "127.0.0.1:63211"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:21.582Z–01:17:21.583Z — non-investigator traffic"
    quote: '{"ts": "2026-11-03T01:17:21.582Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "1fe22b12e5c2", "event": "chaos_failure", "method": "GET", "path": "/products/1"} / {"ts": "2026-11-03T01:17:21.583Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "1fe22b12e5c2", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.722, "client": "127.0.0.1:63212"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:27.928Z — same path as E6, 6.3s later, non-investigator traffic"
    quote: '{"ts": "2026-11-03T01:17:27.928Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "6b308c6be83c", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.013, "client": "127.0.0.1:63218"}'
  - id: E8
    type: metric
    source: "/metrics @ request_id konan-1793668680-15195 (2026-11-03T01:18:00.495Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E9
    type: metric
    source: "/metrics @ request_id konan-1793668680-15195 (01:18:00.495Z); re-read by the software-defect lens at 01:19:35.852Z after four further 503s — still no series"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter"
  - id: E10
    type: metric
    source: "/metrics @ request_id konan-1793668680-15195 (01:18:00.495Z) — complete http_requests_total block"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 3 / http_requests_total{method="GET",path="/orders",status="200"} 1 / http_requests_total{method="GET",path="/products",status="200"} 1 / http_requests_total{method="GET",path="/products",status="503"} 2 / http_requests_total{method="GET",path="/products/1",status="503"} 1 / http_requests_total{method="GET",path="/products/2",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 3'
  - id: E11
    type: probe
    source: "/health @ request_id konan-1793668785-15275 (2026-11-03T01:19:45.160Z) — 105s after the E8 scrape, not the same read; the fresh 503s of E14 (01:19:27–01:19:29Z) and the empty-counter re-read of E9 (01:19:35.852Z) fall between the two, which is what carries the overlap"
    quote: '{"status":"ok","uptime_seconds":154.69458875013515} / -- HTTP 200 in 0.000449s request_id=konan-1793668785-15275'
  - id: E12
    type: metric
    source: "/metrics @ request_id konan-1793668780-15267 (2026-11-03T01:19:40.838Z)"
    quote: "process_uptime_seconds 150.372302667005 / process_max_rss_bytes 46710784"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:13.346Z, 01:17:23.698Z, 01:17:26.870Z — every POST /orders in the file, with timestamps; two of the three fall after the marker of E3"
    quote: '{"ts": "2026-11-03T01:17:13.346Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "ec9d6604ab08", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.959, "client": "127.0.0.1:63208"} / {"ts": "2026-11-03T01:17:23.698Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "aa657aca32b9", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.265, "client": "127.0.0.1:63214"} / {"ts": "2026-11-03T01:17:26.870Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d52b72449bcf", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.189, "client": "127.0.0.1:63217"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:30.041Z and 01:19:27.241Z — the last non-investigator request in the file, and a later failure that is investigator traffic (konan- prefix); every line after 01:18:00.495Z carries a konan- request_id"
    quote: '{"ts": "2026-11-03T01:17:30.041Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "77a9edc9de9d", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.79, "client": "127.0.0.1:63220"} / {"ts": "2026-11-03T01:19:27.241Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "konan-1793668767-15234", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.346, "client": "127.0.0.1:63255"}'
  - id: E15
    type: log
    source: "lab/logs/app.log (whole file, 46 lines) — pairing check over every 503: 7 chaos_failure events against 7 responses with status 503, request_ids matching one-to-one, no unpaired 503 and no unpaired event; the investigator-side pair is quoted"
    quote: '{"ts": "2026-11-03T01:19:29.070Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793668769-15254", "event": "chaos_failure", "method": "GET", "path": "/products"} / {"ts": "2026-11-03T01:19:29.071Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "konan-1793668769-15254", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.156, "client": "127.0.0.1:63259"}'
  - id: E16
    type: probe
    source: "/products/1 — the two 503 probes of the software-defect lens at 2026-11-03T01:19:27Z (request_ids konan-1793668767-15234 and konan-1793668767-15244); the body is the error envelope they returned, the trailer is the first of the two"
    quote: '{"error":"service temporarily degraded"} / -- HTTP 503 in 0.001114s request_id=konan-1793668767-15234'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:22.639Z and 01:17:24.756Z — the third and fourth non-investigator failures after the marker"
    quote: '{"ts": "2026-11-03T01:17:22.639Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "2856efb0db4e", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.239, "client": "127.0.0.1:63213"} / {"ts": "2026-11-03T01:17:24.756Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "34251c418e00", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.243, "client": "127.0.0.1:63215"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:25.813Z, 01:17:28.984Z, 01:17:30.041Z — non-investigator successes interleaved with the failures, all sub-millisecond"
    quote: '{"ts": "2026-11-03T01:17:25.813Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "96e7e086e830", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.793, "client": "127.0.0.1:63216"} / {"ts": "2026-11-03T01:17:28.984Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "a03ac98f5c99", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.814, "client": "127.0.0.1:63219"} / {"ts": "2026-11-03T01:17:30.041Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "77a9edc9de9d", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.79, "client": "127.0.0.1:63220"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:17:11.230Z and 01:17:12.287Z — shop-path requests before the marker, both clean"
    quote: '{"ts": "2026-11-03T01:17:11.230Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "95e67e2bded4", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.926, "client": "127.0.0.1:63206"} / {"ts": "2026-11-03T01:17:12.287Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c30e30ec242c", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.002, "client": "127.0.0.1:63207"}'
  - id: E20
    type: metric
    source: "/metrics, read by the software-defect lens at 2026-11-03T01:19:35.852Z (request_id konan-1793668775-15260), after its own probes of /products/1"
    quote: 'http_requests_total{method="GET",path="/products/1",status="503"} 3 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6'
gaps:
  - "Human impact is not established by telemetry. The failing requests are non-investigator traffic, but that class is not the same as real users: the same unstamped class contains the POST that set the switch (E4), which no shop user calls, and the client ports of the shop requests and of that POST are sequential (63206–63220), which suggests one driver process behind both. The complaint text is the only source for human impact."
  - "Telemetry begins at the process start, 2026-11-03T01:17:10.480Z — 29.5s before the complaint was filed — and no rotated backup (app.log.1–.3) exists. Anything users saw earlier, including the complaint's \"a few minutes ago\" and the reported order failures, is outside the observable window in both directions."
  - "No evidence explains why the process started 29.5s before the complaint; a previous process could have carried a different fault, and nothing in the surface can confirm or exclude that."
  - "The reported order failures were never reproduced. Only two orders were placed while the switch was on, both succeeded (E13), and at the configured rate two clean orders in a row is an ordinary outcome, so the sample neither shows orders failing nor shows them exempt. The surface is GET-only, so an order cannot be exercised read-only."
  - "The switch state is known only up to the last read, 2026-11-03T01:19:40.838Z (E12). One request can clear it (E4 shows the shape), so the state after that moment is unmeasured."
  - "The decisive experiment for H1 — clear the switch and watch the failures stop — is out of bounds: konan is read-only and only the eval harness may trigger scenarios."
  - "The observed failure share (4 of 10 non-investigator requests after the marker) is consistent with the configured 0.4 but is far too small a sample to measure the rate; the rate in the root cause is quoted from the switch's own configuration, not measured."
  - "Who set the switch, and why, is not in the surface: the request that set it (E4) carries a loopback client address and no actor identity."
usage:
  model: claude-opus-5
  tokens: 2362790
  wall_clock_seconds: 597
---

# Intermittent 503s across shop traffic while an internal degradation switch is on

## Summary

**Root cause identified.** An operational degradation switch inside the target — faultline's
chaos mode — was enabled at 01:17:18.465Z with `failure_rate: 0.4`, `error_status: 503`,
`extra_latency_ms: 0` (E3), set by a `POST /chaos/enable` from a loopback client (E4). While
it is on, the target itself mints a 503 for a random share of requests and logs each one as
`chaos_failure` before the response (E5, E6, E15). That is the whole mechanism behind the
reported shape: failures are per-request, not per-input, so the same URL fails and then
succeeds seconds later (E6 then E7), which is exactly "work again on retry".

Incident class is `infra-process` and the cause is `degradation-switch`: the switch lives
inside the target, and the class follows the discipline that owns it even though the symptom
wears a gateway-shaped 503.

**Observed impact.** In the only window with non-investigator traffic — 01:17:20.520Z to
01:17:30.041Z — 4 of 10 such requests returned 503 (E5, E6, E17 against E7, E13, E18); the
6 requests before the marker were clean (E2, E19). Failures hit `/products`, `/products/1`
and `/products/2`. The share agrees with the configured 0.4, but 10 requests cannot measure
a rate — the 0.4 in the root cause is quoted from the switch's configuration, not derived
from the sample.

**Confidence: high on the mechanism, with two honest limits.** First, the switch was still
injecting at the last read (01:19:40.838Z) — a 503 at 01:19:27.241Z (E14) and the exception
counter still empty after it (E9) — but no user traffic has arrived since 01:17:30.041Z, so
"still live" is proved and "still affecting users" is not. Second, the failing traffic is
non-investigator traffic, which is not proof of human users: the same unstamped class
contains the POST that set the switch (E4). Human impact rests on the complaint text alone.

**On the green dashboard.** `/health` returned 200 throughout, with a body carrying only
`status` and `uptime_seconds` (E11) — no field can express the degradation state that
`faultline_chaos_enabled 1` exposes (E8). The green dashboard is consistent with this
incident, not evidence against it.

**The reported order failures are not reproduced.** Every `POST /orders` in the file returned
201, and two of the three fell after the marker (E13). Two clean orders at the configured
rate is an ordinary outcome, so this neither corroborates the reported order failures nor
shows orders exempt from the injection. Orders stay out of the confirmed effect set.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 01:17:10.481Z | Process starts — `faultline 0.1.0 started`. Telemetry begins here; nothing earlier exists. | E1 |
| 01:17:11.230Z–01:17:15.407Z | Shop traffic clean: `/products`, `/products/1`, `/products/2` all 200, one order 201. | E2, E13, E19 |
| **01:17:18.465Z** | **Behavior-change marker** — `chaos_enabled`, `failure_rate: 0.4`, `error_status: 503`, set by `POST /chaos/enable` -> 200 from 127.0.0.1:63210. | E3, E4 |
| 01:17:20.520Z | First failure, 2.1s after the marker: `GET /products -> 503`, preceded by its own `chaos_failure` event. | E5 |
| 01:17:21.583Z | `GET /products/1 -> 503`. | E6 |
| 01:17:22.639Z, 01:17:24.756Z | `GET /products/2 -> 503`, `GET /products -> 503`. Four failures of ten requests in the window. | E17 |
| 01:17:23.698Z, 01:17:26.870Z | Two orders placed while the switch is on — both 201. | E13 |
| 01:17:27.928Z | `GET /products/1 -> 200` — the path that failed at 01:17:21.583Z now succeeds. | E7 |
| 01:17:30.041Z | Last non-investigator request in the file. | E14 |
| 01:17:40Z | Complaint filed (`startsAt`), 21.5s after the marker and 29.5s after process start. | — |
| 01:17:45Z | Investigation starts; baseline captured at 01:17:59.788Z–01:18:00.495Z. | E8, E9, E10, E11 |
| 01:19:27.241Z–01:19:40.838Z | Investigator probes still drawing 503s; `faultline_chaos_enabled` still 1; exception counter still empty. Last read of the switch state. | E9, E12, E14 |

## Investigation

**Baseline** (01:17:59.788Z–01:18:00.495Z): `/health` 200, one startup marker and a single
monotonic uptime (no restart), `http_exceptions_total` with no series, and 503 counters on
three shop paths against successes on the same paths — abnormal against a clean first window.

**Triage**, three lenses in parallel, each blind to the others: software-defect, infra-process,
interfaces. None was skipped, so no lens appears under Gaps. All three converged on the
marker of E3 and all three disowned it: software-defect found no exception signature and
nondeterminism per identical input; interfaces found no external party or boundary component;
infra-process claimed it as an internal operational switch.

**No deep-dive round was spawned.** H1's triage evidence was already deterministic — an
explicit switch marker with its parameters, a `chaos_failure` event on each failure, and the
gauge still set — and H2, H3 and H5 were already refuted by evidence rather than by argument.
Spawning agents to re-prove them would have been coverage theater.

**Judge** (fresh, evidence-only, no narrative). It validated H1 and invalidated H2, H3 and H5,
and it corrected this report in four ways, each folded in above:

1. It refused "non-konan traffic = human users" and pointed at E4 — the switch-setting POST
   is itself unstamped traffic — plus the sequential client ports. Impact is now stated as
   non-investigator traffic, with human impact listed as a gap.
2. It rejected H4 as "refuted": the order metric had no timestamps and could not place the
   orders relative to the marker. Re-read from the log (E13), two of three orders do fall
   after it and both succeeded — which narrows H4 without settling it, so it stays
   inconclusive.
3. It flagged that H1 had passed a test never run: only one 503 was shown paired with its
   `chaos_failure` event. The pairing check now covers the whole file — 7 events against 7
   503s, request_ids one-to-one, no unpaired 503 (E15). Had an unpaired 503 existed, it would
   have shown a second failure source and H1 would not be sufficient.
4. It trimmed three over-claims: "before handler execution" (an inference — restated as
   "without executing the product-lookup path"), the 0.40 share as a measured rate, and
   "still on" as a present-tense fact. It also caught a misattributed uptime value in the
   first ledger (two different reads conflated), corrected in E11 and E12, and a dashboard
   claim in the second latent finding that the evidence could not carry — restated as the
   series-cardinality finding the same evidence does support.

## Hypotheses

### H1 — internal degradation switch — **validated**

The switch marker (E3) sits between a clean window (E2, E19) and a failing one (E5, E6, E17),
and every 503 in the file is immediately preceded by a `chaos_failure` event with the same
request_id (E15; quoted instances E5, E6). The target declares its own failures; nothing
infers them. The same path fails then succeeds 6.3s later (E6, E7), so the failure is drawn
per request. Failures are sub-millisecond (0.239ms in E17) while successes run slower (1.013ms
in E7), and `http_exceptions_total` has no series at all even after fresh failures (E9) — the
503 is returned without executing the product-lookup path, consistent with injection ahead of
the route. Metric labels agree: failures carry the literal path, successes the route template
(E10, E20). Evidence against: none found. Nothing in the surface could refute it except an
unpaired 503, and the check found none.

### H2 — defect in the target's own code — **invalidated**

`http_exceptions_total` is declared and empty, including a re-read after four further 503s
(E9), and no line in the file carries `stack`, `exception_type` or `unhandled_exception`. A
per-input defect is excluded too: the same input returns 503 and then 200 (E6, E7), and the
failures spread across three different paths (E10, E17). The error body is a generic envelope,
`{"error":"service temporarily degraded"}`, with no exception type or field-level detail (E16).
Every 503 is accounted for by a `chaos_failure` event (E15), so no second source remains for
code to own.

### H3 — boundary component or external dependency — **invalidated**

The 503 is minted by the target's own logger (E5) and governed by a switch set through the
target's own endpoint (E3, E4). Clients are direct loopback addresses throughout (E2, E5,
E6), so no proxy tier sits in the path, and a 0.271ms failure leaves no room for an upstream
hop. No log line from a boundary component exists, and no 503 carries a gateway or upstream
signature.

### H4 — the reported order failures have a separate cause — **inconclusive**

All three `POST /orders` returned 201, and two of them fell after the marker (E13), so orders
were exercised during the fault and did not fail. But two clean orders at the configured rate
is an ordinary outcome, and order failures from before 01:17:10.480Z are unobservable, so the
evidence neither finds a separate order fault nor clears orders of the injection. What would
settle it: `POST /orders` traffic during the fault in volume — which the read-only, GET-only
surface cannot produce. H1 predicts orders fail at the same rate; that prediction is untested.

### H5 — load-driven — **invalidated**

Traffic ran at roughly one request per second (10 requests across 9.5s: E5, E6, E17, E18),
all durations stayed under 2.5ms with no upward drift, peak RSS was flat at 46710784 bytes
across reads (E12), and the switch itself declares `extra_latency_ms: 0` (E3). Saturation
raises durations and queues; these durations do not move, and the failures are faster than
the successes.

## Safe next steps

Read-only only; remediation is out of scope and deliberately absent.

1. Re-read `/metrics` for `faultline_chaos_enabled` to learn whether the switch is still set —
   the journal's claim stops at 01:19:40.838Z.
2. Ask whoever owns the switch about the `POST /chaos/enable` at 01:17:18.465Z from
   127.0.0.1:63210 (E4). The surface carries no actor identity, so attribution has to come
   from outside it.
3. Treat the health dashboard's green state as uninformative for this incident shape, and read
   `faultline_chaos_enabled` and the 503 counters alongside it (E8, E10, E11).
4. Confirm with the reporter whether the failures predate 01:17:10.480Z and whether any order
   failure was actually seen — both lie outside the observable window, and the process start
   29.5s before the complaint is itself unexplained.
5. When sizing impact from `http_requests_total`, exclude `konan-*` traffic: the per-id 503
   counters include investigator probes (E20 against E10).

## Gaps

- **Human impact is not in the telemetry.** The failing requests are non-investigator traffic,
  but that class is not identical with real users: the POST that set the switch is in the same
  unstamped class (E4) and no shop user calls that endpoint, and the client ports across the
  shop requests and that POST are sequential (63206–63220), which points at a single driver
  process. The complaint text is the only source for human impact.
- **Nothing before 01:17:10.480Z is observable.** The log starts at the process start and no
  rotated backup exists, so the complaint's "a few minutes ago" can be neither confirmed nor
  contradicted. The observable onset is 01:17:18.465Z; that is not the same claim as the
  incident's beginning.
- **The restart is unexplained.** A process that started 29.5s before a complaint is itself a
  signal, and no evidence in the surface speaks to why, or to what a previous process served.
- **Orders were never reproduced** (see H4), and the GET-only surface cannot place an order.
- **Switch state is known only to 01:19:40.838Z** (E12); one request can clear it (E4).
- **The decisive experiment is out of bounds** — clearing the switch to watch the failures stop
  is a write, and scenario triggering is eval-side only.
- **The failure share is not a measured rate**: 4 of 10 requests is consistent with 0.4 and far
  too small to establish it.
- **No actor identity** for the switch change: E4 carries a loopback address and nothing else.
