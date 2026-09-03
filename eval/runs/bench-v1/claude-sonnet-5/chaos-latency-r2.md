---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-latency-chaos-flag
  trigger: manual
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-08-18T22:58:01Z"
  concluded: "2026-08-18T23:04:36Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime chaos/latency-injection switch was enabled via the operator-surface POST /chaos/enable at 2026-08-18T22:57:41.826Z (declared extra_latency_ms=1500, failure_rate=0.0), which added 150-1334ms of per-request latency to business routes (products, orders) while leaving /health unaffected — explaining shop-wide slowness with no errors and green, fast health checks."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime latency-injection switch (chaos mode) was enabled via POST /chaos/enable at 22:57:41.826Z (declared extra_latency_ms=1500, failure_rate=0.0). After it, business routes — products list, product detail, orders — began responding slowly (observed 150-1334ms, up from a 1-2ms pre-marker baseline on the same routes) while /health stayed fast throughout the same window, and no error status ever appeared."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8, E14, E15, E16, E17]
    evidence_against: []
  - id: H2
    statement: "A process crash/restart loop or resource (memory) saturation caused the slowdown."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11, E12, E13]
  - id: H3
    statement: "A software defect — an unhandled exception or a data-dependent per-input failure — caused the slowdown."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E4, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:41.826Z — the configuration-change marker, the only WARNING in the log"
    quote: |-
      {"ts": "2026-08-18T22:57:41.826Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "3109491a58d3", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:38.765Z — last known-good business request before the marker"
    quote: |-
      {"ts": "2026-08-18T22:57:38.765Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "39cf1fdfc7e0", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.805, "client": "127.0.0.1:52817"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:44.037Z — first business request after the marker, ~2.2s later"
    quote: |-
      {"ts": "2026-08-18T22:57:44.037Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "bded972d2694", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 150.887, "client": "127.0.0.1:52820"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:48.612Z — same route family as E16, ~1300x slower post-marker"
    quote: |-
      {"ts": "2026-08-18T22:57:48.612Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "085e9e7fef03", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1333.665, "client": "127.0.0.1:52822"}
  - id: E5
    type: probe
    source: "probe /health, request_id=konan-1787093927-32410 @ ~2026-08-18T22:58:47Z"
    quote: |-
      {"status":"ok","uptime_seconds":71.79198587499559} -- HTTP 200 in 0.001745s request_id=konan-1787093927-32410
  - id: E6
    type: metric
    source: "probe /metrics, request_id=konan-1787093927-32416 @ ~2026-08-18T22:58:47Z"
    quote: |-
      faultline_chaos_enabled 1
  - id: E7
    type: metric
    source: "probe /metrics, request_id=konan-1787093927-32416 — zero data lines in this series; log tail has zero unhandled_exception/simulated_exception events"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:58:47.674Z — konan's own health probe, same process, well inside the slow window"
    quote: |-
      {"ts": "2026-08-18T22:58:47.674Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787093927-32410", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.614, "client": "127.0.0.1:52851"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:35.894Z — the only startup line in the log"
    quote: |-
      {"ts": "2026-08-18T22:57:35.894Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E10
    type: metric
    source: "probe /metrics, request_id=konan-1787093927-32416 @ ~2026-08-18T22:58:47Z"
    quote: |-
      process_uptime_seconds 71.84069262514822
  - id: E11
    type: metric
    source: "probe /metrics, request_id=konan-1787094061-32572 @ ~2026-08-18T23:01:21Z — monotonically increasing from E10, no reset"
    quote: |-
      process_uptime_seconds 205.57793225022033
  - id: E12
    type: metric
    source: "probe /metrics, request_id=konan-1787093927-32416 @ ~2026-08-18T22:58:47Z"
    quote: |-
      process_max_rss_bytes 47349760
  - id: E13
    type: metric
    source: "probe /metrics, request_id=konan-1787094061-32572 @ ~2026-08-18T23:01:21Z — flat vs E12, +0.1% over 134s"
    quote: |-
      process_max_rss_bytes 47398912
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:46.213Z — a different product id than E4, same slow-but-success shape"
    quote: |-
      {"ts": "2026-08-18T22:57:46.213Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "d2bedcc92abf", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1112.44, "client": "127.0.0.1:52821"}
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:36.651Z — pre-marker baseline for the /products route"
    quote: |-
      {"ts": "2026-08-18T22:57:36.651Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "91e70931b2f9", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.892, "client": "127.0.0.1:52815"}
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:37.705Z — pre-marker baseline for the /products/{id} route"
    quote: |-
      {"ts": "2026-08-18T22:57:37.705Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "e860ea04b28e", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.039, "client": "127.0.0.1:52816"}
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:57:50.418Z — post-marker orders sample, ~400x the E2 baseline"
    quote: |-
      {"ts": "2026-08-18T22:57:50.418Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "306a3b3d2d0d", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 737.599, "client": "127.0.0.1:52823"}
gaps:
  - "Actor and intent behind POST /chaos/enable are outside this surface: telemetry names the endpoint and a localhost client, not an identity."
  - "The delay mechanism is characterized from 5 post-marker samples (150-1334ms, all under the declared 1500ms ceiling): that it is a per-request random draw is inference, not a documented mechanism."
  - "Health/metrics being unaffected is a behavioral observation across the sampled window; whether the switch deliberately exempts those paths by design is not visible in telemetry."
  - "The decisive interventional test — disable chaos mode and watch the same route return to ~1-2ms — is a mutation and therefore outside konan's read-only boundary; the causal case here is abductive (marker + parameter match + held-constant controls), not interventional."
  - "User-vs-investigator traffic attribution rests on the request-id convention: konan's own probes carry a konan-* prefix; unstamped ids in the log are read as end-user or operator traffic per the surface contract, not independently verified."
usage:
  model: claude-sonnet-5
  tokens: 2797280
  wall_clock_seconds: 395
---

# Shop-wide slowness with zero errors — latency-only chaos switch left enabled

## Summary

Root cause identified. faultline's runtime degradation switch was enabled at
22:57:41.826Z via the operator-surface `POST /chaos/enable`, in latency-only form —
declared `extra_latency_ms 1500`, `failure_rate 0.0` (E1). Every business request
after that marker still succeeds, just slowly: the same routes flip from a 1-2ms
pre-marker baseline (E15, E16) to 150-1334ms afterward (E3, E4, E14, E17), while
`/health` stays sub-millisecond throughout the same window on the same process
(E5, E8). No errors appear anywhere — the exception counter is empty and no 5xx
status was ever recorded (E7) — matching the declared zero failure rate, which is
why health checks stayed green and fast while the shop felt "painfully slow."
Process lifecycle and resource use are unremarkable (single startup, flat RSS,
monotonic uptime — E9-E13), and no exception or data-dependent-input signature
exists (E7, and E4/E14 show two different product ids both slow and both
succeeding) — ruling out a code defect or resource saturation as the cause.

## Timeline

All times UTC, from telemetry.

- **22:57:35.894Z** — process start, faultline 0.1.0 (E9); no telemetry before it.
- **22:57:36-38Z** — healthy business traffic: 1-2ms responses on `/products`,
  `/products/1`, `POST /orders` (E15, E16, E2).
- **22:57:41.826Z** — **configuration-change marker**: WARNING `chaos_enabled`,
  `failure_rate 0.0`, `extra_latency_ms 1500` (E1).
- **22:57:44.037Z** — first post-marker business request: `GET /products` -> 200
  in 150.887ms (E3).
- **22:57:44-50Z** — every subsequent business request slow-but-successful:
  150-1334ms across `/products`, `/products/{id}`, `POST /orders` (E4, E14, E17);
  zero errors.
- **22:58:47Z** — investigation baseline: `faultline_chaos_enabled 1` (E6),
  `/health` still sub-millisecond (E5, E8), exception counter empty (E7).
- **23:01:21Z** — confirmation read: uptime climbed monotonically to 205.6s (E11)
  and RSS stayed flat (E13) — no restart, no leak, chaos still enabled.

## Investigation

Baseline already showed the shape: `/health` fast (0.6-1.7ms), `/metrics` showing
elevated duration sums on `/products`, `/products/{id}`, `/orders` against a
near-zero `/health` sum, `faultline_chaos_enabled 1`, and an empty
`http_exceptions_total` series. The log tail put a `chaos_enabled` WARNING three
seconds before the first slow business request.

Triage ran three lenses in parallel, blind to each other. **Software-defect**
found nothing in its domain: zero exception events, zero exception-counter
activity, and slowness spread uniformly across routes and inputs rather than
concentrated on one input — the opposite of a data-dependent defect shape.
**Infra-process** confirmed the process itself was healthy — single startup
marker, flat RSS, no restart — and framed the latency step as "alive but
degraded," anchored to the same marker. **Interfaces** built the onset timeline:
sharp step-function jump immediately after the marker (not gradual saturation
creep), `/health` exempt from the injected latency, and no 502/503/504 anywhere
despite the switch declaring `error_status 503` (matching `failure_rate 0.0`).

Selection: triage evidence was already deterministic and complete — the marker,
the before/after duration flip on the same routes, and the health-vs-shop
contrast — so no deep-dive agents were spawned; all three hypotheses went
straight to the judge. The first judge pass flagged two gaps in H1: no
post-marker `POST /orders` sample was cited, and one post-marker `/products`
sample (150.887ms) looked inconsistent with a flat "+1500ms" framing. Both were
closed with evidence already in hand — E17 (orders, 737.599ms post-marker) and
E15/E16 (pre-marker baselines for the affected routes, confirming the 1-2ms
starting point) — reframing the claim as an observed range under the declared
ceiling rather than a fixed addition. A second judge pass validated H1 cleanly
and invalidated H2 and H3.

Budget: one triage round (3 lenses), zero deep-dives of a permitted three, two
judge passes (the second closing gaps from the first with evidence already
gathered) — concluded within round 1.

## Hypotheses

### H1 — latency-injection switch enabled (validated)

The causal case rests on independent fingerprints, not just proximity in time:
**onset match** — the last known-good sample (E2, 1.805ms) precedes the marker
(E1) by 3 seconds, and the first post-marker sample (E3) follows it by 2.2
seconds with a >100x jump; **parameter match** — every post-marker delay sample
(E3, E4, E14, E17: 150.887, 1333.665, 1112.44, 737.599ms) sits under the declared
1500ms ceiling, and zero errors appeared anywhere (E7), matching the declared
`failure_rate 0.0` exactly; **controls held constant** — the same routes that
were 1-2ms pre-marker (E15, E16) are the ones slow post-marker (E3, E4), on the
same process (E9-E13 show no restart), with `/health` on that same process
staying fast the entire time (E5, E8).

### H2 — process crash/restart or resource saturation (invalidated)

Only one startup line exists in the log (E9) — no restart or crash-loop
signature. `process_uptime_seconds` rose monotonically across two probes 134
seconds apart, 71.8s -> 205.6s (E10, E11), with no reset. `process_max_rss_bytes`
was essentially flat, +0.1% over the same window (E12, E13) — no memory-pressure
signature to explain a slowdown.

### H3 — software defect (invalidated)

`http_exceptions_total` carries zero data lines (E7) — no exception of any type
has fired since startup. Two different product ids on the same route (E4:
`/products/1` at 1333.665ms, E14: `/products/2` at 1112.44ms) are both slow and
both succeed — a uniform-latency signature across inputs, not the
one-input-fails-consistently shape a data-dependent code defect would produce.

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Hand to operators: disabling chaos mode and re-probing an affected route (e.g.
  `/products/1`) to confirm recovery to ~1-2ms would convert this from an
  abductive case to an interventionally proven one (gap 4). Until then the
  degradation is live.
- Trace the change: identify who/what called `POST /chaos/enable` at
  22:57:41.826Z (E1) — telemetry has the endpoint and a localhost client, not an
  identity (gap 1).
- Dashboard blind spot: neither health status nor error rate can see this
  incident class — it is latency-only and health-exempt. Consider surfacing the
  `faultline_chaos_enabled` gauge and a shop-route duration percentile on the
  same dashboard as health, and alerting on `chaos_enabled` WARNING log events.

## Gaps

The machine core lists five. In brief: the actor behind the config change is
unattributable from this surface (1); the per-request delay mechanism (bounded,
apparently variable) is inferred from 5 samples, not documented (2); whether
`/health` exemption is deliberate design or incidental is not visible in
telemetry (3); the interventional proof — disable and re-probe — is a mutation
outside konan's read-only boundary (4); and user-vs-investigator traffic
attribution relies on the request-id stamping convention rather than independent
verification (5).
