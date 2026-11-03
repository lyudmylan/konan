---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-latency
  trigger: "manual — /konan human report; complaint object source=human, fingerprint human-1793684034, labels.alertname=human-report, no severity stated, startsAt 2026-11-03T05:33:54Z; investigation started 2026-11-03T05:34:22Z (trigger latency 28 s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-03T05:34:22Z
  concluded: 2026-11-03T05:42:25Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational degradation switch inside the target was enabled at 05:33:38.438Z with a 1500 ms latency bound and a 0.0 failure rate, and is still on; it adds a randomized server-side delay to the shop routes while leaving the health route untouched."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal operational degradation switch was enabled at 2026-11-03T05:33:38.438Z with extra_latency_ms 1500 and failure_rate 0.0 and has stayed on since; it adds a randomized server-side delay of up to about 1.5 s to the shop routes and none to /health, so shop requests take hundreds of milliseconds to over a second while every status stays 2xx."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E11, E12, E13, E14, E15, E16, E17]
    evidence_against: []
  - id: H2
    statement: "Demand exceeded the target's capacity — CPU, memory, workers or connections — and queueing produced the latency."
    incident_class: load-saturation
    state: invalidated
    evidence_for: [E5, E8, E9]
    evidence_against: [E13, E14, E18]
  - id: H3
    statement: "A defect in the target's own application code produces a slow path or a wrong result on the shop endpoints."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E1, E2, E3, E4, E17, E18]
  - id: H4
    statement: "A process lifecycle fault — a crash, a restart loop, or a hang — explains the symptom."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E10, E18]
  - id: H5
    statement: "A boundary component — proxy, load balancer or gateway — or an external provider added the latency between the users and the target."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E8, E14]
  - id: H6
    statement: "The product catalogue holds a wrong or missing value that degrades the shop."
    incident_class: data-db
    state: invalidated
    evidence_for: [E16]
    evidence_against: [E2, E13, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:32.332Z"
    quote: '{"ts": "2026-11-03T05:33:32.332Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:33.278Z"
    quote: '{"ts": "2026-11-03T05:33:33.278Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "595459bc3bd3", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.31, "client": "127.0.0.1:63956"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:35.380Z"
    quote: '{"ts": "2026-11-03T05:33:35.380Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "aa8541062017", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.007, "client": "127.0.0.1:63958"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:38.438Z"
    quote: '{"ts": "2026-11-03T05:33:38.438Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "0b9fc0985483", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:41.103Z"
    quote: '{"ts": "2026-11-03T05:33:41.103Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "80e8d962e982", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 612.021, "client": "127.0.0.1:63960"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:44.020Z"
    quote: '{"ts": "2026-11-03T05:33:44.020Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "eca1f8e18fab", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 545.53, "client": "127.0.0.1:63962"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:45.303Z"
    quote: '{"ts": "2026-11-03T05:33:45.303Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b1df15d06e14", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 225.619, "client": "127.0.0.1:63963"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:47.429Z"
    quote: '{"ts": "2026-11-03T05:33:47.429Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "de5e0080f9f1", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1077.746, "client": "127.0.0.1:63964"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:33:48.984Z"
    quote: '{"ts": "2026-11-03T05:33:48.984Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "1f8b2375b27f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 511.417, "client": "127.0.0.1:63965"}'
  - id: E10
    type: probe
    source: "GET /health, request_id konan-1793684063-18925, 2026-11-03T05:34:23Z"
    quote: |-
      {"status":"ok","uptime_seconds":51.30511254188605}
      -- HTTP 200 in 0.001708s request_id=konan-1793684063-18925
  - id: E11
    type: metric
    source: "GET /metrics, request_id konan-1793684530-19114, 2026-11-03T05:42:10Z"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: metric
    source: "GET /metrics, request_id konan-1793684530-19114 — the exceptions counter carries its header and no series at all"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E13
    type: metric
    source: "GET /metrics, request_id konan-1793684530-19114 — the complete request counter; the single 404 carries an investigator request id (E17)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 3
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E14
    type: metric
    source: "GET /metrics, request_id konan-1793684530-19114"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products"} 3.6387760003563017
      http_request_duration_seconds_count{method="GET",path="/products"} 6
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.015992709435522556
      http_request_duration_seconds_count{method="GET",path="/health"} 4
  - id: E15
    type: probe
    source: "GET /products, request_id konan-1793684169-18995, 2026-11-03T05:36:10Z"
    quote: "-- HTTP 200 in 1.498564s request_id=konan-1793684169-18995"
  - id: E16
    type: probe
    source: "GET /products, request_id konan-1793684263-19046, 2026-11-03T05:37:43Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.169635s request_id=konan-1793684263-19046
  - id: E17
    type: probe
    source: "GET /products/999, request_id konan-1793684193-19026, 2026-11-03T05:36:33Z"
    quote: |-
      {"detail":"no such product: 999"}
      -- HTTP 404 in 0.900010s request_id=konan-1793684193-19026
  - id: E18
    type: metric
    source: "GET /metrics, process_uptime_seconds across four reads: konan-1793684063-18925 (05:34:23Z), konan-1793684165-18989 (05:36:05Z), konan-1793684174-19004 (05:36:14Z), konan-1793684530-19114 (05:42:10Z)"
    quote: |-
      process_uptime_seconds 51.30511254188605
      process_uptime_seconds 153.1754499580711
      process_uptime_seconds 161.80650116689503
      process_uptime_seconds 518.0334124169312
  - id: E19
    type: metric
    source: "GET /metrics, process_max_rss_bytes, identical across konan-1793684067-18931 (05:34:27Z) and konan-1793684530-19114 (05:42:10Z)"
    quote: "process_max_rss_bytes 47857664"
gaps:
  - "No counterfactual. The decisive test — the switch off, then one shop request — needs the operator surface, which is outside the investigator's read-only boundary. The attribution rests on the step change at the marker plus the flag still reading 1, not on a disable-and-recover observation."
  - "No utilization telemetry exists on this surface: no CPU, worker, thread or connection-pool gauge. Saturation is excluded by request volume (E13) and by /health staying fast while the shop routes crawled (E14), not by a utilization reading inside the slow window."
  - "process_max_rss_bytes (E19) is a high-water mark, so a flat value rules out a new memory peak only. Live memory growth below the earlier peak would be invisible."
  - "Whether \"price\": null on product 4 (E16) breaks any code path that reads a price could not be tested: order creation is a POST, outside the GET-only probe allowlist."
  - "Every client address in the log is 127.0.0.1 and the probes run locally, so a proxy or gateway in a real user's path could add a further increment that the target's own timers never see. H5 is refuted as the cause of the observed delay, not as an additional contributor."
  - "User impact is bounded by what the log holds: six non-investigator request lines after the marker. There is no client-side timing and no user-session data on this surface, so \"every page\" is corroborated route by route (/products, /products/{id}, GET /orders, POST /orders) and never measured per user."
  - "process_uptime_seconds is self-reported by the process. No external supervisor view — pid start time, restart count — is on this surface, so the lifecycle argument in H4 rests on the target's own gauge plus the single startup marker."
usage:
  model: claude-opus-5
  tokens: 1701870
  wall_clock_seconds: 483
---

# Shop routes slowed by an internal degradation switch, errors never raised

## Summary

**Root cause identified.** At 2026-11-03T05:33:38.438Z an operational degradation switch
inside the target was enabled with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E4).
It injects a randomized server-side delay into the shop routes and raises no errors. The
step change is sharp and inside one process lifetime: `GET /products` ran at 1.31 ms
before the marker (E2) and 612.021 ms on the first user request after it (E5), rising to
1077.746 ms (E8), with `POST /orders` going 2.007 ms → 225.619 ms (E3, E7) and
`GET /orders` at 511.417 ms (E9). Every status stayed 2xx and no exception ever fired
(E12, E13) — which is why nothing errors out. `/health` is exempt: 4 calls total 15.99 ms
(E14), the post-onset probe answering in 1.708 ms (E10) — so the green, fast health check
is exactly what this configuration predicts and carries no information about the shop.

The switch was still on at the end of the investigation, 518 s into the process uptime
(E11, E18), so **the degradation is live, not past**. Confidence is high on the mechanism
and on the timing. Two limits the judge insisted on, and they stand: the configured
1500 ms is a **bound, not an increment** — the observed delays scatter from 169.635 ms to
1498.564 ms (E15, E16), so some requests still land near normal and user experience is
variable rather than uniformly slow; and no counterfactual was run, because turning the
switch off is outside the read-only boundary.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 05:33:32.332Z | Process starts, `faultline 0.1.0`, the only startup marker in the log | E1 |
| 05:33:33.278Z | Normal user traffic: `GET /products` in 1.31 ms | E2 |
| 05:33:35.380Z | Normal user traffic: `POST /orders -> 201` in 2.007 ms | E3 |
| **05:33:38.438Z** | **Configuration marker — `chaos_enabled`, `failure_rate: 0.0`, `extra_latency_ms: 1500`** | **E4** |
| 05:33:41.103Z | First slow user request, 2.7 s after the marker: `GET /products` 612.021 ms | E5 |
| 05:33:44.020Z | `GET /products/1` 545.53 ms | E6 |
| 05:33:45.303Z | `POST /orders -> 201` 225.619 ms | E7 |
| 05:33:47.429Z | `GET /products` 1077.746 ms | E8 |
| 05:33:48.984Z | `GET /orders` 511.417 ms | E9 |
| 05:33:54Z | Human raises the complaint (`startsAt`) | — |
| 05:34:22Z | Investigation starts (trigger latency 28 s) | — |
| 05:34:23Z | Baseline probe: `/health` 200 in 1.708 ms, uptime 51.3 s | E10 |
| 05:36:10Z | Investigator probe `/products` 200 in 1.498564 s — the worst sample, just under the bound | E15 |
| 05:36:33Z | Investigator probe `/products/999` 404 in 0.900010 s — the delay lands before route logic | E17 |
| 05:37:43Z | Investigator probe `/products` 200 in 0.169635 s — a near-normal sample under the same switch | E16 |
| 05:42:10Z | Final read: switch still 1, uptime 518 s, no exceptions, no 5xx | E11, E12, E13, E18 |

## Investigation

The complaint object, as the `/konan` adapter synthesized it:

```json
{
  "source": "human",
  "fingerprint": "human-1793684034",
  "labels": { "alertname": "human-report" },
  "annotations": {
    "summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  },
  "startsAt": "2026-11-03T05:33:54Z"
}
```

Investigation start: `2026-11-03T05:34:22Z` — trigger latency 28 s. No severity was stated
by the reporter, so none was recorded.

**Baseline.** `/health` (E10), a `/metrics` snapshot, and the full 22-line log tail. The
baseline already carried the decisive marker (E4) and the still-on gauge, plus the shape
that matched the complaint word for word: elevated durations, zero error series.

**Triage.** All three available lenses ran in parallel, each blind to the others:
`infra-process`, `software-defect`, `interfaces`. Three classes of the taxonomy have no
lens file in this repo — `load-saturation`, `third-party`, `data-db` — so H2, H5 and H6
were formed and tested by the orchestrator against the same surface rather than by a
dedicated lens. The infra-process lens named the switch and ruled out the crash/restart
family. The software-defect lens reported its domain empty and handed over the observation
that the degradation spreads across every shop route *including the 404 error path* (E17),
which places it before route logic. The interfaces lens reported no contract violation and
classed the mechanism as an internal switch, not a boundary fault.

**Deep-dive: skipped.** The triage evidence for H1 was deterministic and complete — a
configuration marker with its parameters, a step change in durations across it inside one
process lifetime, and the flag still on. Deep-dives exist to fill evidence gaps, not to
re-prove; the hypotheses went straight to the judge.

**Judge.** The judge saw the hypothesis list and the verbatim evidence only. It validated
H1's mechanism and struck three overclaims from the statement as written: a flat "1500 ms
per request" (no sample equals 1500 ms; the samples scatter under it), "every shop page is
slow" (E16 is a 169.635 ms success under the same switch), and "/metrics unaffected" (no
pre-onset `/metrics` latency exists in the ledger to compare against). It also flagged
"nothing returns an error" as false as written, since E17 is a 404 — correct behavior for a
missing id, and investigator traffic. The statement above is the narrowed version. The
judge rejected three of the five citations originally offered against H3 as misapplied, and
named one cheap missing item: the counter snapshot was 55 s old and covered none of the
later probes. One final `/metrics` read closed that (E11–E14, E18, E19).

## Hypotheses

### H1 — internal degradation switch · **validated**

For: the marker names the mechanism and its parameters (E4), the step change brackets it
(E2, E3 before; E5–E9 after), the flag still reads 1 after 518 s of uptime (E11, E18), the
error side is empty exactly as `failure_rate: 0.0` predicts (E12, E13), and the split
between the shop routes and `/health` is in the duration summary (E14). The delay is
server-side because E5–E9 and E14 are the target's own measurements. The delay lands
before route logic, since the 404 path is delayed too (E17). The scatter — 169.635 ms
(E16) to 1498.564 ms (E15) — identifies it as a randomized delay bounded by the configured
1500 ms, not a fixed increment.

Against: nothing. The clauses the judge struck were overclaims in the phrasing, not
contrary evidence; E16 reads as *for* the narrowed statement, since variability is what a
randomized delay produces.

Impact: the non-investigator request lines after the marker (E5–E9) all carry unstamped
request ids, so this is real user impact and not an artifact of probing.

### H2 — load saturation · **invalidated**

E5, E8 and E9 are the symptom and discriminate nothing. Against: the target handled 13
instrumented requests in the first 55 s of uptime, six of them investigator traffic (E13,
E18) — queueing is not credible at roughly a quarter of a request per second. The stronger
item is E14: `/health` averaged about 4 ms while `/products` averaged hundreds of
milliseconds in the same window. A saturated CPU or worker pool would have delayed
`/health` too. Note the weakness the judge named: E19 is a high-water mark and was
therefore left out of this list — see Gaps.

### H3 — software defect in the target's code · **invalidated**

E15 is kept honestly as evidence *for*: a slow HTTP 200 is consistent with a slow code
path. The refutation is not the absence of exceptions — a slow path does not throw — but
the step change itself: the same version `0.1.0` (E1) inside one continuous process (E18)
served `/products` at 1.31 ms (E2) and `POST /orders` at 2.007 ms (E3), then hundreds of
milliseconds, at the second of an external configuration flip (E4). Application code does
not change inside a running process. The delay does execute in the target's own code — a
degradation switch is target code — so H1 and H3 differ in intent, not in location: the
behavior here is declared, parameterized and switchable, which makes it `infra-process`
per the taxonomy, not a defect.

### H4 — process lifecycle fault · **invalidated**

`process_uptime_seconds` rises with the wall clock across the whole degraded window: the
four reads imply a start at 05:33:32.3Z, within milliseconds of the single startup marker
(E1, E18). No counter reset, no second incarnation, no rotated log file. The process also
answered every probe through the window (E10), which excludes a hang — a hung process
keeps its uptime but stops serving.

### H5 — boundary component or external provider · **invalidated**

The target's own instrumentation measured the delay (E5, E8, E14), and a component in
front of the target cannot add latency that the server's own timer already sees. E4 names a
better explanation on top of that. Refuted as the cause of the observed delay; see Gaps for
the increment this does not exclude.

### H6 — catalogue data fault · **invalidated**

`"price": null` on product 4 is real (E16), and the same catalogue was served in 1.31 ms
before the marker (E2) — the data did not change at 05:33:38. The payload serializes
completely and returns 200 (E16), with no 5xx anywhere (E13). Invalidated as the cause of
this incident; whether the null price breaks a checkout path is untested, in Gaps.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Ask who enabled the switch at 05:33:38.438Z and whether the change was intended — the
   log records `request_id 0b9fc0985483` for the enabling call (E4), which is the handle
   for correlating it with operator activity.
2. Keep reading `faultline_chaos_enabled` (E11): the gauge is the live state of the
   incident, and it flipping to 0 is the recovery signal to watch for.
3. Treat the green health check as uninformative for this failure mode. A monitor that
   samples a shop route — not only `/health` — would have caught this; the duration summary
   per path (E14) is the signal that already separates them.
4. If the switch is expected to be part of normal operation, consider whether its enabling
   event deserves an alert of its own: it is logged at WARNING (E4) and is visible as a
   gauge, so detection needs no new instrumentation.
5. Separately from this incident, check how `"price": null` (E16) is handled by any path
   that computes a total.

## Gaps

- **No counterfactual.** The test that would convert correlation into causation — switch
  off, then one shop request — needs the operator surface, which the investigator may not
  touch. The attribution rests on the step change at the marker and the still-on flag.
- **No utilization telemetry.** This surface exposes no CPU, worker, thread, or
  connection-pool gauge. H2 is excluded by request volume and by the `/health` versus
  shop-route split, not by a utilization reading inside the slow window.
- **Peak-only memory.** `process_max_rss_bytes` (E19) cannot fall, so a flat value proves
  no new peak, not flat live memory.
- **Untested data path.** Whether `"price": null` on product 4 breaks an order total could
  not be checked: order creation is a POST, outside the GET-only probe allowlist.
- **Local vantage point only.** Every client address in the log is 127.0.0.1 and the probes
  run locally, so a proxy or gateway on a real user's path could add a further increment
  invisible to the target's own timers.
- **User impact is log-bounded.** Six non-investigator request lines after the marker, no
  client-side timings, no session data. "Every page" is corroborated route by route —
  `/products`, `/products/{id}`, `GET /orders`, `POST /orders` — and never measured per
  user.
- **Self-reported lifecycle.** `process_uptime_seconds` comes from the process itself; no
  supervisor view (pid start time, restart count) is on this surface.
- **Three taxonomy classes have no lens file** in this repo — `load-saturation`,
  `third-party`, `data-db`. H2, H5 and H6 were tested by the orchestrator against the same
  telemetry rather than by a dedicated discipline lens.
