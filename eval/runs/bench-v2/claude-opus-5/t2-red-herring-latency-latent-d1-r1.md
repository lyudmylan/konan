---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-slow-latency-switch
  trigger: "manual (human profile, /konan; complaint startsAt 2026-11-03T07:27:27Z, investigation start 2026-11-03T07:27:49Z, trigger latency 22s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: "2026-11-03T07:27:49Z"
  concluded: "2026-11-03T07:38:03Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational switch internal to the target, enabled at 2026-11-03T07:27:05.274Z with extra_latency_ms 1500 and never disabled, adds a variable delay of up to ~1.5s to every shop route while leaving /health and /metrics in the sub-millisecond range."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal operational switch enabled at 07:27:05.274Z injects a variable extra latency of up to 1500ms into the shop routes while the health and metrics endpoints stay unaffected; this is the reported slowness."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E11, E12, E19, E20, E21]
    evidence_against: []
  - id: H2
    statement: "A server-side error response reached end users inside the complaint window and produced the reported error page."
    incident_class: software-defect
    state: inconclusive
    evidence_for: []
    evidence_against: [E10, E11]
  - id: H3
    statement: "The reported error page was produced by the deterministic ZeroDivisionError on GET /products/{product_id} when units_in_stock is 0 (product id 3)."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E13, E14, E15]
    evidence_against: [E11]
  - id: H4
    statement: "Demand exceeded the target's capacity — queueing or resource exhaustion caused the slowness. Invalidated for the observed window 07:26:59.351Z-07:30:05.602Z only; no telemetry covers any earlier window."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E9, E11, E18, E19]
  - id: H5
    statement: "The process start at 07:26:59.351Z was a restart, and the slowness plus the error page are symptoms of that lifecycle event and the downtime before it."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1]
    evidence_against: [E2, E3]
  - id: H6
    statement: "The error page was client-side: a slow but successful origin response was abandoned by the user's client or an intermediary, which rendered its own error while the target recorded 200."
    incident_class: interfaces
    state: inconclusive
    evidence_for: [E5, E6, E11, E12]
    evidence_against: []
latent_findings:
  - statement: "GET /products/{product_id} raises ZeroDivisionError and returns HTTP 500 when the product's units_in_stock is 0 (product id 3); the same route succeeds for other ids. Only investigator-stamped probes ever triggered it, so it is latent, not the active incident."
    evidence: [E13, E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:26:59.351Z"
    quote: '{"ts": "2026-11-03T07:26:59.351Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:00.103Z"
    quote: '{"ts": "2026-11-03T07:27:00.103Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "0e87692fc5e0", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.578, "client": "127.0.0.1:64722"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:05.274Z"
    quote: '{"ts": "2026-11-03T07:27:05.274Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "b90508a112a5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:07.567Z"
    quote: '{"ts": "2026-11-03T07:27:07.567Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e4589649dbeb", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 234.985, "client": "127.0.0.1:64727"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:10.125Z"
    quote: '{"ts": "2026-11-03T07:27:10.125Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "5c1a48501cf5", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1495.299, "client": "127.0.0.1:64728"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:14.283Z"
    quote: '{"ts": "2026-11-03T07:27:14.283Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "c1484679e171", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1286.201, "client": "127.0.0.1:64730"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:16.182Z"
    quote: '{"ts": "2026-11-03T07:27:16.182Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "7955e9311a0c", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 834.737, "client": "127.0.0.1:64731"}'
  - id: E8
    type: metric
    source: "/metrics scraped 2026-11-03T07:27:53Z (request id konan-1793690873-22632)"
    quote: 'faultline_chaos_enabled 1'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:49.531Z"
    quote: '{"ts": "2026-11-03T07:27:49.531Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793690869-22624", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.85, "client": "127.0.0.1:64750"}'
  - id: E10
    type: metric
    source: "/metrics scraped 2026-11-03T07:27:53Z — the two header lines appear with no series lines following them"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E11
    type: metric
    source: "/metrics scraped 2026-11-03T07:27:53Z — complete set of http_requests_total series"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3\nhttp_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2"
  - id: E12
    type: probe
    source: "/products @ 2026-11-03T07:29:36.479Z (request id konan-1793690975-22670)"
    quote: '-- HTTP 200 in 1.207546s request_id=konan-1793690975-22670'
  - id: E13
    type: probe
    source: "/products/3 @ 2026-11-03T07:30:05.602Z (request id konan-1793691004-22697)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError"} -- HTTP 500 in 0.968075s'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:30:05.585Z (stack trimmed: intermediate framework frames and absolute host paths elided, kept frames unaltered)"
    quote: '{"ts": "2026-11-03T07:30:05.585Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793691004-22697", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n …\n  File \"src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E15
    type: probe
    source: "/products — catalog entry for id 3"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:29:52.482Z"
    quote: '{"ts": "2026-11-03T07:29:52.482Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1793690992-22691", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 227.891, "client": "127.0.0.1:64765"}'
  - id: E17
    type: metric
    source: "/metrics scraped 2026-11-03T07:27:53Z"
    quote: "http_request_duration_seconds_sum{method=\"GET\",path=\"/products/{product_id}\"} 2.237924291053787\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products/{product_id}\"} 3"
  - id: E18
    type: metric
    source: "/metrics scraped 2026-11-03T07:27:53Z"
    quote: "process_max_rss_bytes 47153152\nprocess_uptime_seconds 54.00910587515682"
  - id: E19
    type: probe
    source: "/health @ 2026-11-03T07:27:49Z (request id konan-1793690869-22624)"
    quote: '{"status":"ok","uptime_seconds":50.19144116714597} -- HTTP 200 in 0.002586s request_id=konan-1793690869-22624'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:27:53.348Z"
    quote: '{"ts": "2026-11-03T07:27:53.348Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1793690873-22632", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.613, "client": "127.0.0.1:64751"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:29:48.364Z"
    quote: '{"ts": "2026-11-03T07:29:48.364Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793690988-22686", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 330.707, "client": "127.0.0.1:64764"}'
gaps:
  - "No telemetry exists for any moment before 2026-11-03T07:26:59.351Z: lab/logs/app.log is a single unrotated file with no .1-.3 backups, and lab/server.out begins at the same process start. The earlier part of the complaint's 'last few minutes' cannot be checked at all, so the error-page report can be neither confirmed nor refuted there."
  - "Whether the 07:26:59.351Z start was a first start or a restart cannot be settled from the target's surface: exactly one start marker exists, and server.out is created with the launch, so a prior process would have left nothing readable here (H5)."
  - "Instrumentation is not total: /metrics has no http_requests_total series of its own although it was requested, so 'no non-2xx recorded' covers instrumented application routes only — not requests that never reached the application (refused connection, client abort, failure during startup)."
  - "Only one /metrics scrape was taken (07:27:53Z). Counter state after that moment is known only through individual probes, so a non-2xx served to a user between 07:27:53Z and now would not appear in E10/E11."
  - "No client-side or edge telemetry (browser, proxy, load balancer) is inside the surface contract, so a user-visible error page that the origin recorded as 200 cannot be verified (H6)."
  - "units_in_stock for product 3 could not be shown to have been 0 before the two recorded POST /orders, so whether the zero-stock defect was reachable earlier in the complaint window is unknown."
  - "The identity of the actor that enabled the switch is outside the surface: request id b90508a112a5 is unstamped, and the operator surface that serves /chaos is not investigator-readable by contract."
  - "load-saturation beyond the observed window, third-party and data-db have no component in this target (docs/lab.md, 'Known gaps of this lab'), so they are unexercisable here rather than cleared."
usage:
  model: claude-opus-5
  tokens: 2231723
  wall_clock_seconds: 614
---

# Shop-wide latency from an internal degradation switch, with the reported error page uncorroborated

## Summary

**Root cause identified for the slowness.** An operational switch internal to the target
was enabled at `07:27:05.274Z` with `extra_latency_ms: 1500` and has not been disabled
(E3, E8). Every shop route slowed at that instant and stayed slow: `GET /products` went
from 1.578 ms to 234.985 ms on the same route (E2, E4), and the window holds 1495.299 ms
on `/products/2`, 1286.201 ms on `POST /orders` and 834.737 ms on `GET /orders` (E5, E6,
E7). The delay is variable, not fixed — observed magnitudes run 0.23 s to 1.50 s, bounded
by the configured 1500 ms. It is still active: probes at `07:29:36Z` and `07:29:48Z`
returned 200 in 1.207546 s and 330.707 ms on a route that took 1.578 ms before the switch
(E12, E21). Incident class `infra-process`, cause `degradation-switch`.

The reporters' "health checks are green and fast" is **consistent** with the shop being
slow, not contradictory: `/health` answered in 0.85 ms and `/metrics` in 0.613 ms *after*
the switch and while `faultline_chaos_enabled 1` was live (E8, E9, E20). The health
contract does not traverse the degraded path and does not expose the switch, so green
health is not a valid refutation of the complaint. Confidence in this part: high — the
onset is a step change at a logged marker timestamp, the complaint was raised 22 s after
that marker, and the effect reproduces live.

**The "error page once" is not corroborated, and not refuted either.** Inside the covered
window no request of any kind returned a non-2xx status — every `http_requests_total`
series is 200 or 201, including the non-investigator traffic — and `http_exceptions_total`
had no series at all (E10, E11). The switch in force injects no errors by construction:
`failure_rate: 0.0` (E3). But the log begins at the process start `07:26:59.351Z`, roughly
28 s before the complaint was raised, while the complaint says "the last few minutes": for
the earlier part of that period no telemetry exists on this host. So the error page is
unexplained, with four live readings kept open as H2, H3, H5 and H6 rather than closed.

**One latent defect found, caused by this investigation's own traffic.** `GET
/products/{product_id}` raises `ZeroDivisionError` and returns 500 when the product's
`units_in_stock` is 0 — product id 3 (E13, E14, E15). No user request ever reached that
path in the recorded window, and the only 500 in the whole record carries a `konan-`
request id. It is a real defect and a plausible shape for a user-visible error page, but
claiming it caused this one would be a false attribution.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 07:26:59.351Z | Process start, faultline 0.1.0. All telemetry on this host begins here. | E1 |
| 07:27:00.103Z | Healthy baseline: `GET /products` 200 in **1.578 ms**. | E2 |
| 07:27:02.209Z | Healthy baseline: `POST /orders` 201 in 5.38 ms. | — |
| **07:27:05.274Z** | **Configuration-change marker.** Switch enabled: `extra_latency_ms: 1500`, `failure_rate: 0.0`, `error_status: 503`. Unstamped request id — not investigator traffic. | E3 |
| 07:27:07.567Z | First degraded user request: `GET /products` 200 in **234.985 ms**. | E4 |
| 07:27:10.125Z | `GET /products/2` 200 in **1495.299 ms** — at the configured bound. | E5 |
| 07:27:14.283Z | `POST /orders` 201 in **1286.201 ms** (was 5.38 ms). | E6 |
| 07:27:16.182Z | `GET /orders` 200 in **834.737 ms**. | E7 |
| 07:27:27Z | **Complaint raised** (`startsAt`) — 22 s after the switch marker, inside the degraded window. | trigger |
| 07:27:49Z | Investigation starts. `/health` 200 in 2.586 ms, uptime 50.19 s. | E19 |
| 07:27:53Z | `/metrics`: switch still on; zero exceptions; every status series 2xx; RSS 45 MiB. | E8, E10, E11, E18 |
| 07:29:36Z | Degradation confirmed live: `/products` 200 in **1.207546 s**. | E12 |
| 07:30:05.6Z | Investigator probe of `/products/3` triggers `ZeroDivisionError` → 500. Latent, self-induced. | E13, E14 |

## Investigation

### Complaint, as delivered

```json
{
  "source": "human",
  "fingerprint": "human-1793690847",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-03T07:27:27Z"
}
```

Investigation start `2026-11-03T07:27:49Z`; **trigger latency 22 s**. No severity was
stated by the reporter, so none was recorded. The complaint was treated as untrusted data
throughout: it framed where to look and is quoted here, and every claim above rests on
telemetry instead.

### Rounds

**Baseline.** `/health`, `/metrics` and the full log tail. Three facts shaped everything
after: the process was 50 s old, the operator endpoints were sub-millisecond, and the
business routes in the same period were two to three orders of magnitude slower. The
healthy-monitoring trap was the first thing the baseline ruled in.

**Triage — three lenses in parallel**, each blind to the others, each given only its lens
file, the surface contract, the verbatim complaint and the baseline. All three ran
read-only and reported no boundary denials. `infra-process` and `interfaces` independently
landed on the same marker at `07:27:05.274Z` and each confirmed the degradation live with
its own probe; `interfaces` additionally reconciled the per-path metric sums against the
logged durations, establishing that no request is missing from the record, and reported
that its own domain's suspects (gateway, upstream dependency, rollout) have no component
in this target at all. `software-defect` found user traffic 100 % successful and then found
the zero-stock 500 with its own probe — correctly filing it as latent rather than as the
incident.

**No deep-dive round was spawned.** H1's triage evidence was already deterministic and
complete, and the one missing item for the error page — telemetry from before
`07:26:59.351Z` — does not exist on this host, so no probe could have produced it. Running
agents to re-prove a step change, or to search a window that has no data, would have been
coverage theater.

**Judge.** One fresh judge saw the hypothesis list and the verbatim evidence only, with no
narrative. It refused to validate H1 as written, on the grounds that the ledger I gave it
contained no complaint artifact, so no hypothesis could be validated *as an explanation of
a report*. That was a real defect in my ledger, not in the finding: the complaint object
carries `startsAt 07:27:27Z`, which falls 22 s after the marker, and the judge named
exactly that as the item that would settle it. It also caught that my "/metrics stays fast"
claim had no citation behind it (now E20), that E17 mixes pre- and post-switch requests and
so cannot carry causation, that `E16` corroborates the zero-stock trigger instead of
opposing it, and that H4 must not be recorded as "load ruled out" without its time bound.
Its sharpest contribution was a hypothesis I had missed — that the start event itself could
be a restart (H5). All of these are reflected above. The judge's insistence on the
difference between "no error occurred" and "no error is recorded" is what keeps H2 at
inconclusive rather than invalidated.

## Hypotheses

### H1 — internal degradation switch (validated → root cause)

The switch marker (E3) sits between the last fast request (E2, 1.578 ms) and the first slow
one (E4, 234.985 ms) on the *same route* in the *same process*, 2.3 s apart. The magnitude
spread across E4-E7 and E12/E21 — 0.23, 0.33, 0.83, 1.21, 1.29, 1.50 s — is bounded by the
configured `extra_latency_ms: 1500`, which fits a randomized delay rather than a fixed one;
"up to ~1.5 s" is the claim the evidence carries, and "about 1.5 s on every request" is not.
The "never disabled" clause rests on E11, where `POST /chaos/enable` appears with count 1
and no disable counterpart, plus E8 showing the gauge still 1; E12 and E21 then show the
effect persisting ~2.5 minutes after the scrape. `/health` and `/metrics` stay sub-millisecond
in the same period (E9, E19, E20), which is what makes the complaint's three symptoms —
slow shop, green health, fast health — one coherent picture instead of a contradiction.
Per the contract this class is `infra-process` even though a latency injection could look
gateway-shaped: the switch is internal to the target, so it is not `interfaces`.

### H2 — a server-side error reached users (inconclusive)

E10 and E11 license exactly one statement: within `07:26:59.351Z`-`07:27:53Z`, on
instrumented application routes, this process served no 4xx and no 5xx and counted no
unhandled exception. They do not license "no error occurred". They say nothing about the
window before process start, which is where most of the complaint's "last few minutes"
lies; `/metrics` has no series of its own despite having been requested, so the
instrumentation is demonstrably not total; and a request that never reaches the application
leaves no series anywhere. The single piece of evidence that would settle this is one
request record with a non-`konan-` id and a 5xx status inside the complaint window — which
cannot exist on this host for any moment before `07:26:59.351Z`.

### H3 — the zero-stock ZeroDivisionError caused the error page (inconclusive)

The defect is established: 500 with `exception_type: ZeroDivisionError` (E13), the failing
expression `units_ordered / product["units_in_stock"]` at `shop.py:64` (E14), and id 3
carrying `units_in_stock: 0` (E15). The *attribution* fails. The only error in the entire
record is self-induced — E13 and E14 share request id `konan-1793691004-22697`, the
investigator's own prefix — and E11 shows all three `/products/{product_id}` user requests
returned 200, so nobody reached id 3 in the covered window. A probe that finds a latent bug
is not a sighting of the reported fault. It therefore rides along as a latent finding and is
not the root cause. Two further unknowns, recorded rather than glossed: whether id 3's stock
was 0 before the two recorded orders, and whether a user hit it before telemetry began.

### H4 — load saturation (invalidated, for the observed window only)

Twelve requests over 54 s (~0.22 req/s) with RSS at 45 MiB (E11, E18) is not saturation,
and the decisive point is that `/health` stayed at 0.85 ms and 2.586 ms while shop routes
took ~1 s (E9, E19): a saturated worker pool or event loop would have slowed health too.
E3 independently supplies a sufficient cause that needs no load at all. The time bound is
part of the verdict: the counters were born at `07:26:59.351Z`, `process_max_rss_bytes` is
a maximum since then, and a load spike before that moment would be invisible — so this is
"invalidated for 07:26:59.351Z-07:30:05.602Z", never "load ruled out".

### H5 — the start event was a restart (inconclusive)

Raised by the judge, and worth recording because the coverage fact points straight at it:
the record begins at a process start (E1) that the surface cannot classify as a first start
or as a recovery. For the *slowness* it is refuted — requests at `07:27:00`-`07:27:02` were
single-digit milliseconds (E2), so the shop was healthy after the start and degraded only at
the marker 6 s later (E3). For the *error page* it stays open: a restart implies downtime
before it, and downtime would produce exactly the "error page once" being reported. Nothing
on the surface can distinguish the two, since `server.out` is created with the launch.

### H6 — the error page was client-side (inconclusive)

This is the one reading that reconciles a reported error with an all-2xx server record
without appealing to missing data: a response the origin completed slowly (E5 1495.299 ms,
E6 1286.201 ms, E12 1.207546 s) and that the client or an intermediary abandoned, rendering
its own error page. Against it: ~1.5 s is short for a typical client timeout, so it needs
either a stricter client deadline or more latency than any observed request shows. No
client-side or edge telemetry is inside the surface contract, so it cannot be tested from
here at all.

## Safe next steps

Read-only, in order of what each would resolve:

1. **Ask the reporters for the clock time of the error page, the page they were on, and
   whether it carried a status code.** This is the single highest-value item and it is the
   only one that can place the error inside or before the covered window — the question H2,
   H3, H5 and H6 all turn on.
2. **Re-read `faultline_chaos_enabled` and the `http_requests_total` status series on
   `/metrics`** and compare against E8 and E11, to see whether the switch is still on and
   whether any non-2xx has appeared since `07:27:53Z`.
3. **Ask the operator who enabled the switch at `07:27:05.274Z`** (unstamped request id
   `b90508a112a5`) whether this was intentional and whether anything was configured before
   process start. The operator surface is outside konan's read-only contract by design, so
   this is a question for a human, not a probe.
4. **Look for client-side or edge telemetry** (browser reports, proxy or load-balancer
   logs) covering `07:25Z`-`07:28Z` — the only place a user-visible error with a 200 at the
   origin, or a pre-startup failure, could still be recorded.
5. **Note for whoever owns the catalog:** `/products/3` returns 500 deterministically while
   its `units_in_stock` is 0, so any user reaching a zero-stock product detail page will see
   an error. Stated as an observation; remediation is out of scope for this journal.

## Gaps

The frontmatter list, elaborated. The binding one is **coverage**: all eight gaps except the
last two reduce to the same fact — the record starts at `07:26:59.351Z` and the complaint
reaches further back than that. Within the covered window the evidence is unusually
complete (the metric sums reconcile exactly against the logged durations, so no request is
missing), which is precisely why the boundary of that window matters so much: everything
inside it is known, and nothing outside it is knowable from this host.

The remaining two are structural, not accidental. The actor behind the switch is
deliberately outside the investigator's surface, because the operator endpoints are
eval/operator surface by contract. And `load-saturation` beyond the observed window,
`third-party` and `data-db` have no component in this target at all — faultline is one
small service with no database, no external dependency and no distributed topology — so
they are recorded as unexercisable here, not as cleared.
