---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-intermittent-503-chaos-switch
  trigger: "manual (/konan, human profile); complaint object: source human, fingerprint human-1794766148, labels.alertname human-report, no severity stated, startsAt 2026-11-15T18:09:08Z; investigation start 2026-11-15T18:09:23Z; trigger latency 15 s"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-15T18:09:23Z
  concluded: 2026-11-15T18:13:21Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational error-injection switch inside the target (chaos mode) was turned on at 2026-11-15T18:08:51.587Z with failure_rate 0.4 and error_status 503; while it is on, the target answers a random share of product and order requests with an injected 503, independent of the input, and the switch was still on at 18:13:17Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational error-injection switch inside the target (chaos mode) was turned on at 18:08:51.587Z (failure_rate 0.4, error_status 503) and injects 503 responses on a random share of requests on the business routes, independent of the input, while the health endpoint keeps returning 200; the switch is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E15, E16, E17, E18, E19, E20, E21, E23, E24, E25, E26, E27]
    evidence_against: []
  - id: H2
    statement: "The target's own code fails on specific inputs (for example product 4, which had one failure and no success on record at triage time), and those inputs cause the errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E18]
    evidence_against: [E6, E7, E8, E9, E10, E15, E16, E17]
  - id: H3
    statement: "The process crashes, restarts, or runs out of a resource, and that causes the intermittent failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E12]
    evidence_against: [E4, E6, E12, E13, E14, E22, E27]
latent_findings:
  - statement: "The request counter labels an injected 503 with the raw path and a success with the route template, so the error rate of the product-detail route is split across several series and no single series shows it."
    evidence: [E20, E28]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:51.587Z"
    quote: '{"ts": "2026-11-15T18:08:51.587Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "b37c8c62bc91", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:51.588Z"
    quote: '{"ts": "2026-11-15T18:08:51.588Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "b37c8c62bc91", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.939, "client": "127.0.0.1:54628"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:53.638Z"
    quote: '{"ts": "2026-11-15T18:08:53.638Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "eccf06473a17", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:53.638Z"
    quote: '{"ts": "2026-11-15T18:08:53.638Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "eccf06473a17", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.356, "client": "127.0.0.1:54629"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:56.802Z"
    quote: '{"ts": "2026-11-15T18:08:56.802Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "879ac494bba6", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:56.802Z"
    quote: '{"ts": "2026-11-15T18:08:56.802Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "879ac494bba6", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.339, "client": "127.0.0.1:54632"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:59.954Z"
    quote: '{"ts": "2026-11-15T18:08:59.954Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "5689c67265f6", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.322, "client": "127.0.0.1:54635"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:48.532Z"
    quote: '{"ts": "2026-11-15T18:08:48.532Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "8554df1e62c5", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.787, "client": "127.0.0.1:54627"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:55.744Z"
    quote: '{"ts": "2026-11-15T18:08:55.744Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "54656fd5174b", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.284, "client": "127.0.0.1:54631"}'
  - id: E10
    type: metric
    source: "/metrics, request_id konan-1794766270-15407 @ 2026-11-15T18:11:10Z (the exceptions counter family has a header and no sample line)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E11
    type: metric
    source: "/metrics, request_id konan-1794766270-15407 @ 2026-11-15T18:11:10Z"
    quote: 'faultline_chaos_enabled 1'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:43.621Z (the only startup event in the log)"
    quote: '{"ts": "2026-11-15T18:08:43.621Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E13
    type: metric
    source: "/metrics, request_id konan-1794766164-15268 @ 2026-11-15T18:09:24Z"
    quote: |-
      process_uptime_seconds 40.4044102919288
      process_max_rss_bytes 47513600
  - id: E14
    type: metric
    source: "/metrics, request_id konan-1794766270-15407 @ 2026-11-15T18:11:10Z"
    quote: |-
      process_uptime_seconds 146.57673749979585
      process_max_rss_bytes 47513600
  - id: E15
    type: probe
    source: "/products/4, request_id konan-1794766261-15380"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001522s request_id=konan-1794766261-15380
  - id: E16
    type: probe
    source: "/products/4, request_id konan-1794766262-15385"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1794766262-15385"}
      -- HTTP 503 in 0.000992s request_id=konan-1794766262-15385
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:11:02.165Z"
    quote: '{"ts": "2026-11-15T18:11:02.165Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794766262-15385", "event": "chaos_failure", "method": "GET", "path": "/products/4"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:09:03.099Z"
    quote: '{"ts": "2026-11-15T18:09:03.099Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "c5051e3eb993", "event": "chaos_failure", "method": "GET", "path": "/products/4"}'
  - id: E19
    type: probe
    source: "/health, request_id konan-1794766163-15263"
    quote: |-
      {"status":"ok","uptime_seconds":40.00399537477642}
      -- HTTP 200 in 0.001492s request_id=konan-1794766163-15263
  - id: E20
    type: metric
    source: "/metrics, request_id konan-1794766164-15268 @ 2026-11-15T18:09:24Z (all 503 series; before any investigator probe of a business route)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/4",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E21
    type: probe
    source: "/orders, request_id konan-1794766263-15400"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1794766263-15400"}
      -- HTTP 503 in 0.000897s request_id=konan-1794766263-15400
  - id: E22
    type: metric
    source: "/metrics, request_id konan-1794766270-15407 @ 2026-11-15T18:11:10Z"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products"} 0.0022860411554574966
      http_request_duration_seconds_count{method="GET",path="/products"} 4
      http_request_duration_seconds_sum{method="POST",path="/orders"} 0.0035624168813228607
      http_request_duration_seconds_count{method="POST",path="/orders"} 3
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:55.744Z"
    quote: '{"ts": "2026-11-15T18:08:55.744Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "54656fd5174b", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:08:57.850Z"
    quote: '{"ts": "2026-11-15T18:08:57.850Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ecaffe1d4105", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E25
    type: metric
    source: "/metrics, request_id konan-1794766397-15543 @ 2026-11-15T18:13:17Z (the only /health series; 10 of the 12 requests came after the switch, all investigator probes)"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 12'
  - id: E26
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:11:03.685Z"
    quote: '{"ts": "2026-11-15T18:11:03.685Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794766263-15400", "event": "chaos_failure", "method": "GET", "path": "/orders"}'
  - id: E27
    type: metric
    source: "/metrics, request_id konan-1794766397-15543 @ 2026-11-15T18:13:17Z"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 273.7044284166768
      process_max_rss_bytes 47513600
  - id: E28
    type: metric
    source: "/metrics, request_id konan-1794766164-15268 @ 2026-11-15T18:09:24Z"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5'
gaps:
  - "Who or what turned the switch on is unknown: the log shows only the enabling request from client 127.0.0.1:54628 (E2); the operator surface is outside the investigator contract."
  - "The log starts at the process start, 18:08:43.620Z, with no rotated backups. The complaint says 'a few minutes ago', but the first failure on record is 15 s before the complaint; failures before this process start, and whether this start was itself a restart, cannot be checked."
  - "No non-investigator traffic arrived after 18:09:03.099Z. That users still fail rests on the gauge (E27) and on investigator probes (E16, E21), not on user requests."
  - "The health endpoint's exemption from injection is statistical, not proven from configuration: 10 of 10 health probes after the switch returned 200 (chance about 0.6% if the route were subject to a 0.4 rate)."
  - "The sample is small: 5 of 10 user requests failed after the switch against a configured rate of 0.4; the real failure rate is not measured with precision."
  - "Order creation (POST) is outside the read-only probe allowlist; it was observed in user traffic only (one injected 503, two successes). The order path for product 4, whose price is null (E15), was not exercised and is not assessed."
  - "Token usage was not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1546729
  wall_clock_seconds: 238
---

# Intermittent 503s on shop pages and orders: error-injection switch is on

## Summary

**Verdict: root cause identified.** An operational error-injection switch inside the
target ("chaos mode") was turned on at 18:08:51.587Z with `failure_rate` 0.4 and
`error_status` 503 (E1, E2). From that moment the target answers a random share of
requests on the product and order routes with an injected 503; every 503 on record
carries a `chaos_failure` log line with the same request id (E3–E6, E9, E18, E23, E24),
and there is no unhandled exception (E10). The same input succeeds and fails
(E8/E9, E6/E7, E15/E16), which is why a retry works. The health endpoint returned 200
on all 10 probes after the switch (E19, E25), which is why the health dashboard is
green. User impact on record: 0 of 6 user requests failed before the switch, 5 of 10
after it, across `GET /products`, `GET /products/{id}` and `POST /orders`. The switch
was still on at 18:13:17Z (E27). Class `infra-process`, cause `degradation-switch`.
Confidence: high for the mechanism; who turned the switch on is not known.

Complaint object, as received from the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794766148",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green." },
  "startsAt": "2026-11-15T18:09:08Z"
}
```

Investigation start: 2026-11-15T18:09:23Z (trigger latency 15 s).

## Timeline

All times 2026-11-15, UTC.

- 18:08:43.621 — the process starts; the only startup event in the log (E12).
- 18:08:44–18:08:48 — six user requests, all 200/201; last known-good `GET /products/2 -> 200` (E8).
- **18:08:51.587 — configuration marker: chaos mode enabled, failure_rate 0.4, error_status 503** (E1), by `POST /chaos/enable -> 200` from client 127.0.0.1:54628 (E2).
- 18:08:53.638 — first failure: injected 503 on `GET /products` (E3, E4).
- 18:08:55.744 — injected 503 on `GET /products/2`, the input that returned 200 seven seconds earlier (E23, E9).
- 18:08:56.802 — injected 503 on `POST /orders` (E5, E6); 18:08:59.954 the next `POST /orders` returns 201 (E7).
- 18:08:57.850 — injected 503 on `GET /products` (E24).
- 18:09:03.099 — injected 503 on `GET /products/4`; last user request on record (E18).
- 18:09:08 — complaint raised; 18:09:23 investigation starts; `/health` 200 (E19).
- 18:09:24 — baseline scrape: five 503s counted, uptime 40.4 s (E20, E13).
- 18:11:01–18:11:03 — investigator probes: `/products/4` 200 then 503 (E15, E16, E17); `/orders` 503 (E21, E26).
- 18:11:10 — gauge 1, no exception series, uptime 146.6 s, memory unchanged (E11, E10, E14).
- 18:13:17 — gauge still 1; `/health` 200 count 12, no 503 series for `/health` (E27, E25).

## Investigation

- **Baseline.** `/health` 200 (E19); `/metrics` showed 503 series on product and order
  routes, `faultline_chaos_enabled 1`, no exception series, uptime 40 s (E20, E13); the
  log showed clean traffic until a `chaos_enabled` marker, then mixed 503/200.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the same switch marker and the
  one-to-one pairing of 503s with `chaos_failure` lines. Infra-process: one startup,
  uptime monotonic, memory flat, no latency change. Software-defect: no exception, no
  stack; open point — product 4 had failed twice and never succeeded. Interfaces: the
  failures are per-request, not per-input; 503s carry raw-path metric labels.
- **Deep-dive.** None spawned. H1's triage evidence was deterministic and complete.
  The one open point (product 4) was closed by the orchestrator with three direct
  probes of `/products/4`: 200, 503 with a `chaos_failure` line, 200 (E15–E17).
- **Judge.** One fresh judge, evidence only. H1 validated, with the note that the
  health clause rested on one probe; H2 invalidated; H3 invalidated.
- **After the judge.** Eight more `/health` probes, all 200 (E25), to answer the
  judge's note. The exemption stays a statistical statement (see Gaps).

Budget used: one triage round, no deep-dive agent, one judge round.

## Hypotheses

### H1 — error-injection switch is on (validated)

The switch marker (E1, E2) sits between the last known-good request (E8) and the first
failure (E3, E4). Every user 503 has a paired `chaos_failure` line: `/products` (E3/E4,
E24), `/products/2` (E23/E9), `/orders` POST (E5/E6), `/products/4` (E18); the baseline
counters hold exactly these five (E20). The prediction "same input succeeds and fails"
holds on three inputs (E8/E9, E6/E7, E15/E16), and investigator probes reproduce the
injection with the same signature (E16/E17, E21/E26). No exception is counted (E10).
The gauge reads 1 at 18:11:10Z and 18:13:17Z (E11, E27). `/health` returned 200 on all
probes after the switch (E19, E25). No evidence against was found.

### H2 — input-specific code defect (invalidated)

Its only support, the failure on product 4 (E18), carries the injection marker.
Product 4 returned 200 and 503 within 0.6 s (E15, E16, E17), product 2 and order
creation also succeed and fail (E8/E9, E6/E7), and no unhandled exception exists
(E10). The failures are not deterministic per input.

### H3 — crash, restart, or resource exhaustion (invalidated)

Its only support is timing: the process started 8 s before the switch (E12). Against
it: one startup event only (E12), uptime grows 40.4 → 146.6 → 273.7 s with no reset
(E13, E14, E27), peak memory is constant (E13, E14, E27), and requests take about 1 ms
or less, the injected 503s less than the successes (E4, E6, E22).

### Latent finding — metric labels split the error rate

Injected 503s are counted under the raw path (`/products/2`, `/products/4`), successes
under the route template (`/products/{product_id}`) (E20, E28). A dashboard on the
template series does not show these errors. This is not the incident.

## Safe next steps

Read-only only.

- Ask the operators who sent `POST /chaos/enable` at 18:08:51.587Z (client
  127.0.0.1:54628, request id `b37c8c62bc91`) and whether a test was planned.
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` event; watch the
  503 series for the moment they stop growing.
- Read the user-facing error rate from `http_requests_total` over all `status="503"`
  series (raw-path labels included), not from `/health`.
- When user traffic returns, check that each new 503 still has a `chaos_failure` line;
  a 503 without one, or a sample in `http_exceptions_total`, would be a second cause.

## Gaps

- **Who turned the switch on.** The log shows the enabling request and its client
  address only (E2). The operator surface is outside the investigator contract.
- **History before 18:08:43.620Z.** The log starts at the process start and has no
  rotated backups. The complaint says "a few minutes ago"; the first failure on record
  is 15 s before the complaint. Earlier failures, and whether this start was a
  restart, cannot be checked.
- **Current user impact.** No user request arrived after 18:09:03.099Z. That users
  still fail rests on the gauge (E27) and investigator probes (E16, E21).
- **Health exemption.** 10 of 10 `/health` probes after the switch returned 200 — a
  chance of about 0.6% if the route were subject to the 0.4 rate. Not proven from
  configuration.
- **Failure rate.** 5 of 10 user requests failed against a configured 0.4; the sample
  is too small to measure the real rate.
- **Order path.** POST is outside the probe allowlist. Order creation was seen in user
  traffic only. Product 4 has `price: null` (E15); an order for it was not observed
  and is not assessed.
- **Usage.** Token totals were not captured.
