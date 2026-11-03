---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-latency-degradation-switch
  trigger: "manual — /konan adapter, source=human, fingerprint=human-1793669502, labels.alertname=human-report (no severity stated), startsAt=2026-11-03T01:31:42Z; investigation started 2026-11-03T01:32:01Z (trigger latency 19s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-11-03T01:32:01Z"
  concluded: "2026-11-03T01:41:30Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational latency-injection switch inside the target was enabled at 01:31:25.824Z with failure_rate 0.0 and extra_latency_ms 1500 and is still on; it adds a per-request variable delay to the shop routes while leaving /health and /metrics untouched, which makes every page slow with no errors and a green health check."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal operational degradation switch (chaos mode) was enabled at 2026-11-03T01:31:25.824Z with extra_latency_ms 1500 and failure_rate 0.0 and remains on; while on it adds a per-request variable delay to the business routes (/products, /products/{id}, /orders) — 7 ms to 1422 ms observed against ~1 ms before — while /health and /metrics stay sub-millisecond and no request fails."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E9, E10, E11, E12, E13, E16, E17, E18, E19, E20]
    evidence_against: [E8]
  - id: H2
    statement: "Demand exceeded capacity (CPU, memory, workers or connections) and the delay is queueing."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E11, E12, E13]
  - id: H3
    statement: "A defect in the target's own code — an exception, a logic error, or a data-dependent slow path — causes the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E8, E9, E10, E12, E13]
  - id: H4
    statement: "The process crashed, restarted, or hung, and the symptom is process lifecycle."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E9, E13, E14]
  - id: H5
    statement: "A boundary component failed on its own — a gateway tier, a provider outage, or a contract mismatch."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E10]
  - id: H6
    statement: "An external dependency answers slowly and the target waits on it."
    incident_class: third-party
    state: inconclusive
    evidence_for: []
    evidence_against: [E8, E12]
latent_findings:
  - statement: "The liveness surface is exempt from the injected delay: /health and /metrics answer in under a millisecond in the same seconds in which shop routes take hundreds of milliseconds to 1.4 s. A monitor that probes only /health cannot detect this class of degradation — the green health check in the complaint is correct and carries no information about the shop."
    evidence: [E11, E12, E13, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:19.892Z"
    quote: '{"ts": "2026-11-03T01:31:19.892Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:20.649Z"
    quote: '{"ts": "2026-11-03T01:31:20.649Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "9366859cf16e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.945, "client": "127.0.0.1:63300"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:22.765Z"
    quote: '{"ts": "2026-11-03T01:31:22.765Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "bf8860470bb3", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.891, "client": "127.0.0.1:63302"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:25.824Z"
    quote: '{"ts": "2026-11-03T01:31:25.824Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "662544d071db", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:28.087Z"
    quote: '{"ts": "2026-11-03T01:31:28.087Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "43acaff5c9a6", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 202.294, "client": "127.0.0.1:63305"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:32.447Z"
    quote: '{"ts": "2026-11-03T01:31:32.447Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "286251d21e32", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 820.661, "client": "127.0.0.1:63308"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:34.458Z"
    quote: '{"ts": "2026-11-03T01:31:34.458Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "2d2457f016e1", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 946.543, "client": "127.0.0.1:63309"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:30.565Z"
    quote: '{"ts": "2026-11-03T01:31:30.565Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "3dbf47794072", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 7.379, "client": "127.0.0.1:63307"}'
  - id: E9
    type: metric
    source: "/metrics scrape @ 2026-11-03T01:35:19Z, request id konan-1793669719-15748"
    quote: "faultline_chaos_enabled 1 / process_uptime_seconds 239.82272708392702 / process_max_rss_bytes 47562752"
  - id: E10
    type: metric
    source: "/metrics scrape @ 2026-11-03T01:35:19Z, request id konan-1793669719-15748 — the complete http_requests_total and http_exceptions_total output"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 5 / http_requests_total{method=\"GET\",path=\"/metrics\",status=\"200\"} 1 / http_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 1 / http_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 6 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 5 / http_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2 / # HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter  (no series follow)"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:34:11.531Z"
    quote: '{"ts": "2026-11-03T01:34:11.531Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793669651-15671", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.454, "client": "127.0.0.1:63343"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:34:12.401Z"
    quote: '{"ts": "2026-11-03T01:34:12.401Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1793669650-15666", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1422.194, "client": "127.0.0.1:63342"}'
  - id: E13
    type: metric
    source: "/metrics scrapes @ 2026-11-03T01:32:19Z (konan-1793669539-15579) and @ 2026-11-03T01:35:19Z (konan-1793669719-15748)"
    quote: "first scrape: http_request_duration_seconds_sum{method=\"GET\",path=\"/products\"} 1.1497821670491248 / _count 3 ; http_request_duration_seconds_sum{method=\"GET\",path=\"/health\"} 0.013217084109783173 / _count 3 ; process_uptime_seconds 59.314730416983366 ; process_max_rss_bytes 47562752 — second scrape: /products _sum 2.3645688337273896 / _count 6 ; /health _sum 0.014126791153103113 / _count 5 ; process_uptime_seconds 239.82272708392702 ; process_max_rss_bytes 47562752"
  - id: E14
    type: probe
    source: "/health @ 2026-11-03T01:32:13Z, request id konan-1793669533-15573"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":53.49614966684021} / -- HTTP 200 in 0.002162s request_id=konan-1793669533-15573"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:20.638Z"
    quote: '{"ts": "2026-11-03T01:31:20.638Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "f7a2f4e03f63", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.841, "client": "127.0.0.1:63299"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:32:19.194Z"
    quote: '{"ts": "2026-11-03T01:32:19.194Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1793669539-15579", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.633, "client": "127.0.0.1:63333"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:34:02.233Z"
    quote: '{"ts": "2026-11-03T01:34:02.233Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793669641-15648", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 354.071, "client": "127.0.0.1:63339"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:34:18.151Z"
    quote: '{"ts": "2026-11-03T01:34:18.151Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793669657-15681", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 534.049, "client": "127.0.0.1:63345"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:29.493Z"
    quote: '{"ts": "2026-11-03T01:31:29.493Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "f706766e6c39", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 339.061, "client": "127.0.0.1:63306"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:31:35.774Z"
    quote: '{"ts": "2026-11-03T01:31:35.774Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "1cc3159ce76e", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 266.583, "client": "127.0.0.1:63310"}'
gaps:
  - "Recorded history begins at the startup marker 01:31:19.892Z (E1) and lab/logs/app.log has no rotated backups, so nothing before that instant could be checked. The complaint's \"last few minutes\" partly precedes the available telemetry."
  - "The code path inside the target that consumes extra_latency_ms was not read: the target's source is outside the surface contract (docs/lab.md). The switch-to-latency link therefore rests on the marker, its parameter names, and the before/after timing, not on a read of the mechanism."
  - "No CPU, worker-pool, queue-depth or connection-count series exists on /metrics. CPU, worker and connection saturation were excluded by request volume (21 requests in 240 s, E10) and by the /health-fast-while-shop-slow split within one second (E11, E12), not by direct resource measurement."
  - "No outbound-dependency telemetry exists on this surface — no client-call log event and no dependency metric — so H6 (an external dependency answering slowly) cannot be excluded from telemetry alone. docs/lab.md declares that this target has no third-party dependency, but that is the contract, not an observation."
  - "Who enabled the switch is unknown: the chaos_enabled line (E4) carries no client field, unlike every access line, and its request id 662544d071db is not investigator traffic (no konan- prefix)."
  - "The observed added delays run 7.379 ms to 1422.194 ms, all below the configured extra_latency_ms 1500. Eleven post-switch samples cannot establish the distribution or the ceiling of the injected delay; 1500 is a configuration field, not a measured bound."
  - "Product ids 3 and 4 appear in the /products body with units_in_stock 0 and price null. No request to them, and no order against them, appears anywhere in the window, so whether they fail is untested."
  - "Confirming recovery by turning the switch off is an operator action outside the read-only boundary; it was not attempted. The switch was still on at the last reading (E9)."
  - "data-db was not covered by a lens: the surface has no database telemetry and docs/lab.md states the lab has no real database. Three lenses exist in this repo (infra-process, software-defect, interfaces) and all three ran."
usage:
  model: claude-opus-5
  tokens: 1975228
  wall_clock_seconds: 569
---

# Shop-wide latency from an internal degradation switch, health surface exempt

## Summary

**Root cause identified.** An internal operational degradation switch in faultline — chaos
mode — was enabled at 2026-11-03T01:31:25.824Z with `failure_rate: 0.0` and
`extra_latency_ms: 1500` (E4) and was still on at the last reading, 3 min 54 s later (E9).
While it is on, the target adds a per-request variable delay to the shop routes and leaves
the liveness surface alone. The same routes that answered in about 1 ms before the marker
(E2: `/products` 0.945 ms; E3: `POST /orders` 1.891 ms) answered in 202 ms, 339 ms, 821 ms,
947 ms and 267 ms after it (E5, E19, E6, E7, E20) — all of those from non-investigator
traffic, so real users were affected, and all of them HTTP 200 or 201. `failure_rate: 0.0`
is why nothing errors out: the `http_exceptions_total` counter has no series at all and
every request series carries status 200 or 201 (E10).

The green health check is not a contradiction of the user reports; it is a blind spot. At
01:34:11.531Z `/health` answered in 0.454 ms, and 0.87 s later `/products/1` took
1422.194 ms (E11, E12) — same process, same second. Across the two metric scrapes,
`/products` averaged 405 ms per request while `/health` averaged 0.45 ms (E13), and
`/metrics` is exempt as well (E16: 0.633 ms after the switch). A monitor that probes only
`/health` cannot see this degradation.

Impact: every shop endpoint exercised in the window (`/products`, `/products/{id}`,
`GET /orders`, `POST /orders`) is slowed; nothing fails. Confidence: high on the switch
being on and on the latency step at its marker; the mechanism inside the code was not read
(see Gaps), so the causal link rests on the marker, its parameter names and the timing.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 01:31:19.892 | Process start — the beginning of all recorded history; no rotated logs exist before it | E1 |
| 01:31:20.638–01:31:22.765 | Healthy baseline: `/health` 0.841 ms, `/products` 0.945 ms, `POST /orders` 1.891 ms | E15, E2, E3 |
| **01:31:25.824** | **Configuration-change marker: `chaos mode enabled`, `failure_rate: 0.0`, `error_status: 503`, `extra_latency_ms: 1500`, from a non-investigator request id** | **E4** |
| 01:31:28.087 | First slow request, 2.3 s after the marker: `/products` 202.294 ms, status 200 | E5 |
| 01:31:29.493–01:31:35.774 | Non-investigator traffic stays slow and error-free: `/products/2` 339.061 ms, `POST /orders` 820.661 ms, `/products` 946.543 ms, `GET /orders` 266.583 ms. One outlier stays fast: `/products/1` 7.379 ms | E19, E6, E7, E20, E8 |
| 01:32:13–01:32:19 | Investigator baseline: `/health` 200 in 0.002162 s, uptime 53.5 s; `/metrics` 0.633 ms; `faultline_chaos_enabled 1` | E14, E16, E13 |
| 01:34:11.531 / 01:34:12.401 | Side by side in the same second: `/health` 0.454 ms, `/products/1` 1422.194 ms | E11, E12 |
| 01:34:02–01:34:18 | Investigator probes of `/products` under the switch: 354.071 ms, 534.049 ms | E17, E18 |
| 01:35:19 | Last reading: switch still on, `process_uptime_seconds 239.82`, RSS unchanged at 47562752, no exception series | E9, E10, E13 |
| — | No `chaos_disabled`, no `chaos_failure`, no `unhandled_exception`, no second `startup` anywhere in the window | E10, E1 |

## Investigation

Trigger — the complaint object as synthesized by the `/konan` adapter, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1793669502",
  "labels": { "alertname": "human-report" },
  "annotations": {
    "summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  },
  "startsAt": "2026-11-03T01:31:42Z"
}
```

Investigation start: 2026-11-03T01:32:01Z — trigger latency 19 s. No severity was stated by
the reporter, so none was recorded.

**Baseline.** `/health` (E14), a `/metrics` scrape (E13) and the whole 22-line log tail. Two
facts framed everything after: the process had been up only 53 s, so the entire telemetry
history was about a minute; and `faultline_chaos_enabled` already read 1.

**Triage — three lenses in parallel, each blind to the others**, given only the lens file,
the surface contract, the verbatim complaint and the baseline. All three independently
reached the same marker. infra-process: the switch is on, latency rose 2–3 orders of
magnitude, the health endpoint is exempt, and this is "alive but degraded" — one startup
group, monotonic uptime, flat RSS. software-defect: no exception signature of any kind, and
the latency step is uniform across routes and inputs rather than concentrated — not a code
defect; it also flagged `/products/3` and `/products/4` as never exercised. interfaces: sharp
onset at a configuration marker, last known-good `POST /orders` 1.891 ms, first known-bad
`/products` 202.294 ms, no traffic in between, and it handed the class to infra-process
itself, since the mechanism is an internal switch.

**Deep-dive: skipped deliberately.** H1's triage evidence was already deterministic and
complete — the marker, the before/after pairs on identical routes, the gauge still reading 1,
and live probes confirming the predicted state. Deep-dives fill evidence gaps; there was no
gap left to fill. Instead the orchestrator re-scraped `/metrics` to confirm the switch was
still on and to take a counter delta (E13), and re-read the log tail to quote the post-switch
requests individually rather than rely on a mean.

**Judge.** The judge saw only the hypothesis list and the verbatim quotes. It validated H1
in a narrower form than first stated and was right to: the claims that the delay is
*randomized* and bounded by 1.5 s are inference from a field name over eleven samples, not
measurement, and the mechanism inside the code was never read. Both now appear as Gaps, and
H1's statement claims only the observed range. The judge also rejected three weak citations,
which are corrected in this journal: `http_exceptions_total` being empty does not refute a
*slow-success* logic defect (H3 now leans on the single-startup/no-restart chain — the same
build served 0.945 ms and 946.543 ms), the RSS and uptime readings do not cover CPU, workers
or connections (H2 now leans on the request volume and on the `/health`-inside-`/products/1`
interleaving), and "another cause is available" is not evidence against a hypothesis (E4
dropped from H2's and H5's against-lists). Its challenge on class — the switch arrived
through the target's own control API, so is this a configuration action rather than a process
fault? — resolves in the contract: an internal operational switch that injects latency is
`infra-process` / `degradation-switch` by definition (report-contract.md, "Causes, defined"),
whatever the symptom wears.

## Hypotheses

### H1 — internal degradation switch (infra-process) — **validated**

The switch is internal to the target: E4 is a WARNING from the `faultline.chaos` logger
inside the process, and `faultline_chaos_enabled` is the target's own gauge (E9). Its
parameters match the complaint's shape exactly: `extra_latency_ms: 1500` is delay,
`failure_rate: 0.0` is "nothing errors out", and the armed `error_status: 503` stays inert —
no 5xx series and no exception series exist (E10). The onset is sharp and the window is
unambiguous: last known-good at 01:31:22.765Z (E3), marker at 01:31:25.824Z (E4), first
known-bad at 01:31:28.087Z (E5), with no traffic in between. The step reproduces across four
routes (E5, E19, E6, E7, E20, E12, E17, E18) and persists: still on at 01:35:19Z (E9), with
`/products` averaging 405 ms per request against `/health`'s 0.45 ms in the same three
minutes (E13). Evidence against, E8: `/products/1` took 7.379 ms *after* the marker. That
kills "every request is uniformly delayed" — the delay varies per request — but not the
hypothesis: the same path took 1422.194 ms under the same switch state (E12), so one fast
sample is jitter, not a healthy route.

One cross-check worth recording: E2 + E5 + E7 = 1.149782 s, which matches the first scrape's
`/products` `_sum` of 1.1497821670491248 at `_count 3` to every digit (E13). The three quoted
`/products` durations are therefore the complete set for that period — no unseen `/products`
traffic hides in the window.

### H2 — load saturation — **invalidated**

There is no load to queue: 21 requests in 240 s of uptime (E10), about ten of them the
investigator's own. The decisive observation is the interleaving — `/health` started and
finished inside `/products/1`'s in-flight span (E11 at 01:34:11.531Z, 0.454 ms; E12 at
01:34:12.401Z, 1422.194 ms, so in flight from ~01:34:10.979Z) — which excludes a shared
queue, a blocked worker pool and a saturated event loop, since a saturated process cannot
serve a sub-millisecond request mid-wait. RSS is identical across both scrapes (E13), which
excludes memory pressure only; CPU and pool metrics do not exist on this surface (Gaps).

### H3 — software defect in the target's code — **invalidated**

No exception signature: `http_exceptions_total` has no series, every request series is 200 or
201 (E10), and no log line carries `unhandled_exception` or a `stack` field. But the
load-bearing refutation is the lifecycle chain, because a *logic* defect would also produce
slow 200s: E1 is the only `startup` event and the uptime readings trace to that one instant
(E9, E13), so the running build never changed — the same code served `/products` at 0.945 ms
(E2) and at 946.543 ms (E7). Data dependence is out too: `/products/1` returned in 7.379 ms
(E8) and 1422.194 ms (E12) — same path, same input, 200× apart — so no input shape
distinguishes fast from slow.

### H4 — process crashed, restarted, or hung — **invalidated**

Three independent uptime readings all trace to the single start instant: 01:31:19.892Z + 53.496 s
= 01:32:13.39Z (E14), + 59.315 s = 01:32:19.2Z (E13), + 239.823 s = 01:35:19.7Z (E9); the
180.51 s between scrapes matches 180 s of wall clock. One `startup` event (E1), no exit, no
connection refusal, no counter reset, and the process serves business traffic throughout. This
is "alive but degraded". Residual: the period before 01:31:19.892Z is unknowable (Gaps).

### H5 — boundary component or external failure — **invalidated**

No gateway-shaped status anywhere: every series is 200 or 201 and the exceptions counter is
empty (E10). No 502/503/504, no validation or malformed-payload line, no `chaos_failure`
event. The configured `error_status: 503` never fired.

### H6 — an external dependency answering slowly — **inconclusive**

Honest state: a slow dependency also produces slow 200s, and this surface carries no
outbound-call telemetry at all, so telemetry cannot exclude it (Gaps). What argues against it
is evidential but not decisive: the same path flipped 200× between 7.379 ms (E8) and
1422.194 ms (E12) with no dependency event in between, which is awkward for a dependency
reading, and the onset sits 2.3 s after an in-process switch whose configuration names a
latency injection of exactly this magnitude. Parsimony, not proof — recorded as inconclusive
rather than quietly folded into H1.

## Safe next steps

Read-only only; remediation is out of scope for a journal.

1. Treat `faultline_chaos_enabled` as an alertable signal — it read 1 for the whole
   investigation (E9) and no `chaos_disabled` event ever appeared. A gauge that is on is
   cheaper to detect than the latency it causes.
2. Alert on business-route latency, not on `/health`. The two disagreed by ~87× inside one
   second (E11, E12). Any monitor scoped to `/health` or `/metrics` is structurally blind to
   this degradation (latent finding).
3. If the window before 01:31:19.892Z matters, look for log retention outside
   `lab/logs/app.log` — there are no rotated backups, so the complaint's earlier minutes are
   not in reach of this surface.
4. `/products/3` and `/products/4` (`units_in_stock: 0`, `price: null`) were never exercised
   in this window. A read-only probe of each would close that blind spot — unrelated to this
   incident.
5. To confirm the causal link that this investigation inferred rather than observed, a
   read-only review of the request path that consumes `extra_latency_ms` would show the route
   filter (why `/health` and `/metrics` are exempt) and how the delay is drawn. That is
   outside the investigator's surface contract.

## Gaps

1. **History starts at the process start.** Recorded telemetry begins at 01:31:19.892Z (E1)
   and `lab/logs/app.log` has no rotated backups, so nothing before that instant could be
   checked. The complaint says "the last few minutes"; part of that period is simply not in
   the data.
2. **The mechanism was inferred, not read.** The target's source is outside the surface
   contract (`docs/lab.md`), so the link from the switch to the delay rests on the marker, its
   parameter names, and the before/after timing. A read of the code path that consumes
   `extra_latency_ms` would settle it; so would toggling the switch, which is an operator
   action outside the read-only boundary.
3. **Resource metrics are partial.** `/metrics` exposes no CPU, worker-pool, queue-depth or
   connection-count series. H2 was excluded by request volume (E10) and by the interleaving of
   E11 inside E12's in-flight span, not by direct resource measurement.
4. **No dependency telemetry.** No client-call event and no dependency metric exists on this
   surface, so H6 stays inconclusive. `docs/lab.md` states the lab has no third-party
   dependency, but that is the contract, not an observation.
5. **The actor is unknown.** E4 carries no `client` field, unlike every access line, and its
   request id `662544d071db` is not investigator traffic — so the switch was thrown by
   something outside this session, but the telemetry does not say by whom.
6. **The delay's distribution and ceiling are unmeasured.** Observed added delays run
   7.379 ms to 1422.194 ms, all below the configured 1500 ms, but eleven samples cannot
   establish a distribution or a bound; 1500 is a configuration field, not a measurement.
7. **Two product records were never exercised.** `/products/3` and `/products/4`
   (`units_in_stock: 0`, `price: null`) appear in the `/products` body, but no request or order
   against them appears anywhere in the window.
8. **Recovery was not confirmed.** The switch was still on at the last reading (E9); verifying
   that latency returns to ~1 ms when it goes off requires an operator action.
9. **One taxonomy class had no lens.** `data-db` was not covered: this surface exposes no
   database telemetry and `docs/lab.md` states the lab has no real database. The repo ships
   three lenses — infra-process, software-defect, interfaces — and all three ran.
