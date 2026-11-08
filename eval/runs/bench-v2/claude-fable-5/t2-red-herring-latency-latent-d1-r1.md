---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-slowness
  trigger: "manual (/konan): fingerprint human-1793705079, startsAt 2026-11-03T11:24:39Z, investigation start 2026-11-03T11:24:49Z, trigger latency 10s"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: "2026-11-03T11:24:49Z"
  concluded: "2026-11-03T11:32:50Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode — faultline's runtime degradation switch — was enabled at 11:24:15.492Z via the operator-surface POST /chaos/enable in latency-only form (declared extra_latency_ms 1500, failure_rate 0.0) and was still enabled at last observation; it adds a variable per-request delay to business endpoints (observed 22.8–1398.2 ms server-side, every sample under the declared ceiling) while health and metrics stay unaffected — so the whole shop is slow while health checks stay green and fast."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "A latency-only degradation switch (chaos mode, declared extra_latency_ms 1500 with failure_rate 0.0) enabled at 11:24:15.492Z via the operator-surface POST /chaos/enable adds a variable per-request delay to business endpoints while health and metrics stay unaffected; the same route and input flips from ~1.3 ms to ~1222 ms across the marker, investigator probes reproduce the delay, and the gauge stays at 1 with no disable event."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E11, E13, E14]
    evidence_against: []
  - id: H2
    statement: "The single 'error page' that users report is recorded nowhere in the reachable telemetry; it happened before the process start at 11:24:09.571Z (a restart gap or the prior process) or outside the server (client-side), and cannot be attributed from this surface."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E9, E10]
    evidence_against: []
  - id: H3
    statement: "A data-dependent defect in the target's own code: GET /products/3 raises ZeroDivisionError at shop.py line 64 ('turnover_score': units_ordered / product['units_in_stock']) because product 3 has units_in_stock 0; the 500 is deterministic for that input, other probed products return 200, and only investigator probes have triggered it in the reachable telemetry."
    incident_class: software-defect
    state: validated
    evidence_for: [E9, E13, E15, E16, E17]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 fails deterministically with HTTP 500: shop.py line 64 divides units_ordered by product['units_in_stock'] and product 3 (Unobtainium Ingot) has units_in_stock 0. Any user who opens product 3 gets an error page regardless of chaos settings. No user request to /products/3 appears in the reachable telemetry — only investigator probes (konan-*) have triggered it, so it rides along as latent, not as the active incident."
    evidence: [E13, E15, E16, E17]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:24:09.571Z — first line of the only log file; lab/logs/ holds no rotated backups (.1–.3 absent) and lab/server.out shows this single startup, so no telemetry exists from before this instant"
    quote: |-
      {"ts": "2026-11-03T11:24:09.571Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:24:15.492Z — the configuration-change marker; the only WARNING in the pre-probe log"
    quote: |-
      {"ts": "2026-11-03T11:24:15.492Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "c0d35e6b0cb2", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:24:15.492Z — same request_id as E2: this POST changed the config; 12-hex id, not an investigator probe"
    quote: |-
      {"ts": "2026-11-03T11:24:15.492Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "c0d35e6b0cb2", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.4, "client": "127.0.0.1:50183"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:24:12.433Z — last user request before the marker; all pre-marker business durations are 1.218–1.93 ms"
    quote: |-
      {"ts": "2026-11-03T11:24:12.433Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "10885f3e7c63", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.93, "client": "127.0.0.1:50182"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:24:18.827Z — first user request after the marker: ~1000x slower, still 200"
    quote: |-
      {"ts": "2026-11-03T11:24:18.827Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "1aa11849d4b8", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1275.284, "client": "127.0.0.1:50184"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 11:24:11.384Z and 11:24:23.020Z — the same route and input, fast before the marker, slow after; both user traffic, both 200"
    quote: |-
      {"ts": "2026-11-03T11:24:11.384Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "20c8228186d2", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.269, "client": "127.0.0.1:50181"}
      {"ts": "2026-11-03T11:24:23.020Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "52cc5ff6117e", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1222.2, "client": "127.0.0.1:50186"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 11:24:20.724Z and 11:24:27.428Z — post-marker user durations vary 825.9–1398.2 ms (also 877.36 ms on POST /orders), every one under the declared 1500 ms, none erroring"
    quote: |-
      {"ts": "2026-11-03T11:24:20.724Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "efef88414ed2", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 825.937, "client": "127.0.0.1:50185"}
      {"ts": "2026-11-03T11:24:27.428Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "41325916b78f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1398.207, "client": "127.0.0.1:50188"}
  - id: E8
    type: metric
    source: "probe /metrics, request_id=konan-1793705105-30924 @ 2026-11-03T11:25:05Z — still 1 at konan-1793705281-31053 (process_uptime_seconds 232.257, ~11:28:01Z); no chaos_disabled event exists anywhere in the log"
    quote: |-
      faultline_chaos_enabled 1
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1793705105-30924 @ 2026-11-03T11:25:05Z — only 200/201 series exist; no 4xx, no 5xx; the declared error_status 503 never fired, matching failure_rate 0.0"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E10
    type: metric
    source: "probe /metrics, request_ids konan-1793705105-30924 @ 11:25:05Z and konan-1793705281-31053 @ ~11:28:01Z — zero sample lines at both reads, before the investigator's own 500 at 11:28:17Z"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E11
    type: log
    source: "lab/logs/app.log @ 11:25:04.732Z and 11:25:05.304Z — health and metrics under 1 ms while chaos is on and business routes run ~1 s in the same window"
    quote: |-
      {"ts": "2026-11-03T11:25:04.732Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793705104-30919", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.518, "client": "127.0.0.1:50206"}
      {"ts": "2026-11-03T11:25:05.304Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1793705105-30924", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.644, "client": "127.0.0.1:50207"}
  - id: E12
    type: probe
    source: "probe /health, request_id=konan-1793705104-30919 @ ~11:25:04Z — green and fast; uptime back-computes to E1's start, proving the same process serves health and the slow shop routes"
    quote: |-
      {"status":"ok","uptime_seconds":55.17206595907919}
      -- HTTP 200 in 0.001539s request_id=konan-1793705104-30919
  - id: E13
    type: probe
    source: "probe /products, request_id=konan-1793705502-31202 @ ~11:31:42Z — investigator's own shop probe drew ~0.87 s with a clean, complete body; the body also shows product 3 with units_in_stock 0 (and product 4 with price null, which returned 200 on probe konan-1793705297-31118 @ ~11:28:17Z)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.869440s request_id=konan-1793705502-31202
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:26:18.716Z — investigator probe on the same route drew 22.797 ms while the gauge read 1 before and after: the added delay varies per request, bounded by the declared ceiling, not fixed"
    quote: |-
      {"ts": "2026-11-03T11:26:18.716Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793705178-30958", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 22.797, "client": "127.0.0.1:50212"}
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:28:17.116Z — triggered by the investigator's own deep-dive probe (konan-* id); stack trimmed to the first and final frames, kept frames verbatim"
    quote: |-
      {"ts": "2026-11-03T11:28:17.116Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793705296-31113", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  File \"<checkout>/src/faultline/middleware.py\", line 72, in _handle\n    return await call_next(request)\n  […]\n  File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:28:17.134Z — the access line for E15's exception; the only 5xx in the log, investigator-stamped"
    quote: |-
      {"ts": "2026-11-03T11:28:17.134Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793705296-31113", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 751.965, "client": "127.0.0.1:50229"}
  - id: E17
    type: probe
    source: "probe /products/3, request_id=konan-1793705565-31228 @ ~11:32:45Z — repeat probe, same input, same 500: the defect is deterministic, not a one-off"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793705565-31228"}
      -- HTTP 500 in 0.372593s request_id=konan-1793705565-31228
gaps:
  - "Actor and intent behind the switch are outside this surface: telemetry names the endpoint (POST /chaos/enable) and a localhost client, not an identity."
  - "No telemetry exists from before the process start at 11:24:09.571Z (no rotated logs, single startup in server.out), so the users' 'error page once' cannot be confirmed or attributed; edge/proxy/load-balancer logs or the prior process's logs covering ~11:15–11:24:39Z would settle H2."
  - "The delay mechanism is characterized from samples (22.797–1398.207 ms, all under the declared 1500 ms ceiling); that it is a per-request random draw is inference. 'Remains enabled' holds through the last observation (~11:31:42Z, E13 still ~0.87 s), not indefinitely."
  - "The decisive intervention — disable the switch and watch the same route return to ~1–2 ms — is a mutation and therefore outside konan's read-only boundary; the causal case is abductive (config marker + ceiling-respecting delays + held-constant controls), not interventional."
  - "User-vs-investigator attribution rests on the request-id convention: all observed traffic originates from 127.0.0.1; unstamped 12-hex ids are read as end-user or operator per the surface contract."
  - "Product 5 was never probed on the detail route; 'other products return 200' rests on products 1, 2, and 4 — a sample, not a full check."
usage:
  model: claude-fable-5
  tokens: 1662206
  wall_clock_seconds: 481
---

# Shop-wide slowness with green health — latency-only chaos mode left enabled; latent /products/3 crash found en route

## Summary

Root cause identified. faultline's degradation switch was enabled at 11:24:15.492Z
via the operator-surface `POST /chaos/enable` in **latency-only** form — declared
`extra_latency_ms 1500`, `failure_rate 0.0` (E2, E3) — and was still on at last
observation (E8, E13). Every business request after the marker succeeds but slowly:
the same route and input flips from 1.269 ms to 1222.2 ms across the marker (E6),
post-marker user durations vary 825.9–1398.2 ms with every sample under the declared
ceiling (E5, E7), and konan's own probes drew 22.8 ms–1.03 s on shop routes while
health answered in under 1 ms in the same window (E11, E12, E14). No user-facing
errors exist anywhere in the reachable telemetry (E9, E10), matching the declared
zero failure rate — health and metrics are unaffected, which is why health checks
stayed green and fast. The users' single "error page" could not be attributed: the
process started at 11:24:09.571Z and nothing earlier survives (H2, inconclusive).
A **latent defect** rode along: `GET /products/3` deterministically returns 500 via
`ZeroDivisionError` (division by `units_in_stock: 0` at shop.py line 64) — real,
user-reachable, but triggered only by investigator probes in the visible window
(H3, latent finding).

## Timeline

All times UTC, from telemetry.

- **11:24:09.571Z** — process start, faultline 0.1.0 (E1); no telemetry before it.
- **11:24:10–12Z** — healthy user traffic: all 200/201, durations 1.218–1.93 ms;
  last known-good at 11:24:12.433Z (E4).
- **11:24:15.492Z** — **configuration-change marker**: WARNING `chaos_enabled`,
  failure_rate 0.0, extra_latency_ms 1500 (E2), request-id-tied to
  `POST /chaos/enable` → 200 from a localhost client (E3).
- **11:24:18.827Z** — first post-marker user request: `GET /products` → 200 in
  1275.284 ms, ~1000x the pre-marker norm (E5).
- **11:24:18–27Z** — every user request slow-but-successful, 825.9–1398.2 ms,
  reads and writes alike (E6, E7); zero errors.
- **11:24:39Z** — complaint raised (`startsAt`); investigation started 11:24:49Z.
- **11:25:04–05Z** — baseline: health 0.518 ms and `{"status":"ok"}` (E11, E12),
  gauge `faultline_chaos_enabled 1` (E8), counters 200/201-only (E9, E10).
- **11:26:18–32Z** — triage probes: same route draws 22.797 ms then ~1.03 s —
  the delay varies under the ceiling (E14).
- **11:28:17Z** — deep-dive disconfirmation probe `GET /products/3` → 500,
  `ZeroDivisionError` at shop.py line 64 (E15, E16). Investigator-triggered: from
  this instant the metrics carry a 500 series and an exception entry stamped
  `konan-*` — probe noise, not user impact.
- **11:31:42Z** — `/products` probe still ~0.87 s: degradation live (E13).
- **11:32:45Z** — repeat `/products/3` probe: same 500 — deterministic (E17).
- **11:32:50Z** — concluded.

## Investigation

Baseline showed the known healthy-monitoring trap shape: health green in 1.5 ms,
counters 200/201-only, empty exception counter — but the chaos gauge at 1, a
one-minute-old process, and post-marker business durations ~1000x their pre-marker
values, with the enable marker sitting in the log three seconds before the first
slow request.

Triage ran three lenses in parallel (infra-process, interfaces, software-defect),
blind to each other. All three converged on the chaos latency switch as the
slowness mechanism; all three independently reported the same two residues: no
trace of the users' "error page" anywhere, and no telemetry from before the
11:24:09.571Z start. Software-defect found no exception, no 5xx, and no
input-correlated failure in its domain at triage time.

Selection: **H1 skipped deep-dive** — the marker (E2, E3), the before/after flip on
a held-constant route and input (E6), the ceiling-respecting variable delays (E5,
E7, E14), the health/shop contrast from one process (E11, E12), and the persistent
gauge (E8) were already deterministic and complete. **One deep-dive ran on H2**,
tasked to confirm and refute "the error page is recorded nowhere reachable." It
confirmed the negative half across the full log, server.out, and metrics — and its
disconfirmation probing found H3: `GET /products/3` → 500 via `ZeroDivisionError`,
a data-dependent defect (product 3 has `units_in_stock: 0` — E13), which the lens
correctly flagged as triggered only by its own stamped probe.

The judge (fresh context, cited evidence only) **validated H1**, held **H2
inconclusive** (the negative finding stands; "before start or client-side" is
unevidenced remainder — a restart-gap 502/503 from an upstream tier is equally
plausible and equally invisible from this surface), and **validated H3** with one
caveat — single reproduction — which a repeat probe then closed (E17). The judge
explicitly rejected re-attributing the users' error page to H3: E9/E16 show no
non-investigator request ever reached `/products/3` in the visible window.

Budget: one triage round (3 lenses), one deep-dive of a permitted three, one judge
round — concluded in round 1. The round-2 evidence the judge named for H2
(edge/proxy or prior-process logs) does not exist on this surface, so it is a gap,
not a next round. Tokens: subagent totals are not capturable from an interactive
orchestrator; the machine core records `tokens: null`.

## Hypotheses

### H1 — latency-only degradation switch enabled (validated)

Temporal correlation upgraded to causation by three independent fingerprints:
**attribution** — the config event and the POST share request id `c0d35e6b0cb2`
(E2, E3); **parameter match** — every post-marker delay sits under the declared
1500 ms ceiling (E5, E6, E7, E13, E14) and zero user-facing errors appeared (E9,
E10), matching the declared failure_rate 0.0 — generic slowness has no reason to
respect a config-declared ceiling or to be perfectly error-free; **controls** —
same route and input across the marker (E6), reproduction on investigator probes
(E13, E14), and contemporaneous selectivity (shop ~1 s while health sub-millisecond
from the same process — E11, E12) with the enabled state persisting across the
window (E8).

### H2 — the reported "error page" predates the telemetry or happened client-side (inconclusive)

The negative half is solid: no non-investigator 4xx/5xx or exception exists
anywhere reachable (E9, E10), and nothing survives from before the process start
(E1 — single startup, no rotated logs). The causal half is unevidenced: nothing
shows a pre-start error, a client-side timeout (the ~1.4 s max delay is well under
browser timeouts), or an upstream restart-gap page — and the complaint itself is
untrusted, so the error page may not have happened at all. What would settle it:
edge/proxy/load-balancer access logs or the prior process's logs for
~11:15–11:24:39Z. Out of reach on this surface (gap 2).

### H3 — /products/3 crashes with ZeroDivisionError (validated; latent)

Code and data match: the stack ends at shop.py line 64,
`units_ordered / product["units_in_stock"]` (E15), and product 3 has
`units_in_stock: 0` (E13). Deterministic: two probes, same 500 (E16, E17). Not
chaos: the event is `unhandled_exception` in business code with failure_rate 0.0.
Latent, not the incident: every trigger is investigator-stamped; no user request
to `/products/3` exists in the visible window (E9, E16). It cannot explain the
shop-wide slowness (it fails one input; the slowness spans all routes) and cannot
be shown to explain the users' error page (see H2).

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Hand to the operators: disable chaos mode and re-probe E6's route — recovery to
  ~1–2 ms converts the causal case from abductive to interventionally proven
  (gap 4). Until then the degradation is live.
- Trace the change: who called `POST /chaos/enable` at 11:24:15.492Z (E3) —
  telemetry has the endpoint and a localhost client, not an identity (gap 1).
- Report the latent defect to the owning team: any user who opens product 3 gets a
  500 while its stock is 0 (E13, E15–E17) — a real error page waiting for its
  first user. Zero stock is a normal business state, not an edge case.
- For the unexplained user error page: pull edge/proxy/load-balancer or
  prior-process logs for ~11:15–11:24:39Z (gap 2).
- Dashboard blind spots: this incident class is latency-only and health-exempt —
  put the `faultline_chaos_enabled` gauge and a shop-route duration percentile on
  the dashboard, and alert on `chaos_enabled` WARNING events; add per-route 5xx
  rate so a single `/products/3` user hit becomes visible.

## Gaps

The machine core lists six. In brief: the actor is unattributable read-only (1);
pre-start history does not exist on this surface, so the users' error page stays
unexplained (2); the jitter mechanism and "still enabled" are bounded inferences
(3); the interventional proof is a mutation and therefore an operator action, not
konan's (4); user attribution rests on the request-id convention (5); product 5's
detail route went unprobed (6).
