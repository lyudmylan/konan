---
konan_journal: 2
investigation:
  id: 2026-11-15-occasional-shop-errors
  trigger: "manual — /konan human report; source human; fingerprint human-1794755431; labels.alertname human-report; no severity stated; startsAt 2026-11-15T15:10:31Z; investigation start 2026-11-15T15:10:44Z (trigger latency 13 s)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-15T15:10:44Z
  concluded: 2026-11-15T15:15:34Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational switch inside the target (chaos mode) was turned on at 2026-11-15T15:10:23.881Z with failure_rate 0.08 and error_status 503; while on, it injects HTTP 503 into a random share of requests (observed on three GET routes), and the gauge still read 1 at 2026-11-15T15:13:57Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode), turned on at 2026-11-15T15:10:23.881Z with failure_rate 0.08 and error_status 503, injects HTTP 503 into a random share of requests (observed on three GET routes); the switch was still on at 2026-11-15T15:13:57Z."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception on some input, and that request fails."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E9, E11, E12, E13]
  - id: H3
    statement: "A gateway tier or an upstream dependency fails on its own and returns 503 to the users."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E9]
    evidence_against: [E1, E4, E5, E6]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:23.881Z"
    quote: |-
      {"ts": "2026-11-15T15:10:23.881Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "df779f69aa62", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:23.881Z"
    quote: |-
      {"ts": "2026-11-15T15:10:23.881Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "df779f69aa62", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.082, "client": "127.0.0.1:53457"}
  - id: E3
    type: metric
    source: "/metrics, probe request_id=konan-1794755637-4312 (2026-11-15T15:13:57Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:25.188Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T15:10:25.188Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "6e5c3283ecc2", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-15T15:10:25.188Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "6e5c3283ecc2", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.151, "client": "127.0.0.1:53474"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:25.328Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T15:10:25.328Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5bf909859596", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-11-15T15:10:25.328Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "5bf909859596", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.14, "client": "127.0.0.1:53482"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:25.428Z (two lines, one request id)"
    quote: |-
      {"ts": "2026-11-15T15:10:25.428Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "42af226b284c", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T15:10:25.428Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "42af226b284c", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.137, "client": "127.0.0.1:53489"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:25.342Z (the input of E6, 86 ms earlier, after the switch)"
    quote: |-
      {"ts": "2026-11-15T15:10:25.342Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "42e0be40a647", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.456, "client": "127.0.0.1:53483"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:20.762Z (a request before the switch; all 5 requests before the switch succeeded)"
    quote: |-
      {"ts": "2026-11-15T15:10:20.762Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "737d98386c8a", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.003, "client": "127.0.0.1:53455"}
  - id: E9
    type: metric
    source: "/metrics, probe request_id=konan-1794755448-4163 (2026-11-15T15:10:48Z), the complete http_requests_total family"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products",status="200"} 6
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 16
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 6
  - id: E10
    type: metric
    source: "/metrics, probe request_id=konan-1794755637-4312 (2026-11-15T15:13:57Z), the complete set of non-2xx samples of http_requests_total"
    quote: |-
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
  - id: E11
    type: metric
    source: "/metrics, probe request_id=konan-1794755637-4312 (2026-11-15T15:13:57Z); the exceptions counter family has a header and no sample line"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E12
    type: probe
    source: "/products/1, request_id=konan-1794755499-4254 (investigator traffic), access line in lab/logs/app.log @ 2026-11-15T15:11:39.700Z"
    quote: |-
      {"ts": "2026-11-15T15:11:39.700Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794755499-4254", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.547, "client": "127.0.0.1:53519"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:10:18.946Z (the only startup line in the file)"
    quote: |-
      {"ts": "2026-11-15T15:10:18.946Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E14
    type: metric
    source: "/metrics, probe request_id=konan-1794755637-4312 (2026-11-15T15:13:57Z)"
    quote: "process_uptime_seconds 218.64383050007746"
  - id: E15
    type: probe
    source: "/health, request_id=konan-1794755448-4158"
    quote: |-
      {"status":"ok","uptime_seconds":29.36132683325559}
      -- HTTP 200 in 0.002026s request_id=konan-1794755448-4158
gaps:
  - "No telemetry exists before 2026-11-15T15:10:18.946Z: the log starts at the process start and has no backup files. The complaint says 'the last few minutes'; errors under an earlier process instance can be neither confirmed nor excluded."
  - "Who turned the switch on is not in the telemetry: the log shows the POST /chaos/enable request from a local client (E2), not an identity or a reason."
  - "User traffic stops at 2026-11-15T15:10:25.428Z. The share of failing requests rests on 32 requests in about half a second after the switch; the user impact after that time could not be measured."
  - "Injected failures were seen on three GET routes only. Five POST /orders requests after the switch succeeded; whether the switch also fails order creation or the health endpoint is not evidenced."
  - "All evidence is the target's own log and metrics. The lab has no tier in front of the target, so an error produced outside the process would not be visible on this surface."
  - "Token totals were not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1351104
  wall_clock_seconds: 290
---

# Occasional shop errors: an error-injection switch inside the target is on

## Summary

**Verdict: root cause identified — this is not "nothing".** An operational switch inside the
target, chaos mode, was turned on at 15:10:23.881Z with `failure_rate` 0.08 and
`error_status` 503 (E1, E2). From that moment the target answers a random share of
requests with HTTP 503: three user requests failed, on `/orders`, `/products`, and
`/products/1`, and each one carries a `chaos_failure` log line with its own request id
(E4, E5, E6). That is 3 of the 32 user requests after the switch, about 9 %, in line with
the configured 8 %; all 5 requests before the switch succeeded (E8, E9). The same input
succeeds on another request (E7, E12), which is the "works on retry" of the complaint.
The switch was still on at 15:13:57Z (E3). No exception, no restart, and no status 500
exist on the surface (E10, E11, E13, E14). Class `infra-process`, cause
`degradation-switch`. Confidence: high for the mechanism; the size of the user impact
rests on a small sample (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 15:10:18.946 — the process starts; the only startup line in the log (E13).
- 15:10:19.677–15:10:21.822 — 5 requests, all succeed (E8, E9).
- 15:10:23.881 — **configuration marker:** `chaos mode enabled`, failure_rate 0.08,
  error_status 503, extra_latency_ms 0, through `POST /chaos/enable` (E1, E2).
- 15:10:25.188 — first failure: `GET /orders -> 503`, with a `chaos_failure` line (E4).
- 15:10:25.328 — `GET /products -> 503`, with a `chaos_failure` line (E5).
- 15:10:25.342 — `GET /products/1 -> 200` (E7).
- 15:10:25.428 — `GET /products/1 -> 503`, with a `chaos_failure` line; the last user
  request in the log (E6).
- 15:10:31 — the complaint is raised (`startsAt`).
- 15:10:44 — the investigation starts.
- 15:10:48 — baseline: `/health` 200 (E15); `/metrics` shows three 503 samples (E9).
- 15:11:39 — investigator probe `GET /products/1 -> 200` (E12).
- 15:13:57 — `faultline_chaos_enabled 1`, uptime 218.6 s without a reset, no new 503,
  no exception sample (E3, E10, E11, E14).

## Investigation

**Trigger.** The manual adapter (`/konan`) built this complaint object:

```json
{
  "source": "human",
  "fingerprint": "human-1794755431",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-11-15T15:10:31Z"
}
```

Investigation start: 2026-11-15T15:10:44Z (trigger latency 13 s). The reporter stated no
severity. `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`.

**Baseline.** `/health` returned 200 with an uptime of 29 s (E15). `/metrics` showed
three 503 samples on three routes, no exception sample, and `faultline_chaos_enabled 1`
(E9). The log held one startup line, INFO and WARNING lines only, and a `chaos_enabled`
WARNING 1.3 s before the first 503 (E1, E13).

**Triage.** Three lenses ran in parallel, each blind to the others: infra-process,
interfaces, software-defect. All three reported the same anomaly, the chaos switch and
its three paired 503s. The software-defect lens found no exception evidence and probed
`/products/1` once with a 200 (E12). The interfaces lens found no upstream failure and
no contract violation. The infra-process lens found one startup, no uptime reset, a flat
RSS, and no latency change.

**Deep-dive.** Skipped. The triage evidence for H1 was already deterministic and
complete: every 503 has its own cause marker with the same request id.

**Judge.** One fresh judge saw the hypotheses and the quoted evidence only. Verdicts:
H1 validated, H2 invalidated, H3 invalidated. The judge narrowed two clauses of H1:
"on all routes" became "observed on three GET routes", and "still on" now carries the
time of the last gauge reading. A final `/metrics` probe at 15:13:57Z then confirmed the
gauge at 1 (E3). The investigation used one round.

## Hypotheses

### H1 — an internal degradation switch injects 503s (validated)

The `chaos_enabled` line gives the time and the parameters (E1), and the access line of
the same request id shows how the switch was reached (E2). Each of the three 503s has a
`chaos_failure` line with the same request id and timestamp (E4, E5, E6). The metrics
hold exactly three non-2xx samples, the same three (E9, E10). No request failed before
the switch (E8). The same input, `/products/1`, succeeded 86 ms before it failed (E7).
The gauge read 1 at 15:13:57Z (E3). Nothing on the surface speaks against H1.

### H2 — an unhandled exception in the target's code (invalidated)

Every prediction failed. The exceptions counter has no sample (E11). No status 500
exists; the only failures are the three 503s (E9). The failing input succeeds on other
requests, from a user and from the investigator (E7, E12). One startup line means no
restart hid earlier exceptions (E13). Limit: this covers one process of a few minutes
and the inputs that received traffic.

### H3 — a gateway or upstream failure (invalidated)

The only support is the status code itself, 503 (E9), and it does not discriminate: the
switch is configured to answer with 503 (E1). The prediction "a 503 without an internal
cause marker" has no instance: all three 503s carry a `chaos_failure` line (E4, E5, E6).
The 503s took 0.137–0.151 ms, less than a success on the same route (E7), which fits an
early return inside the process and not a call to an upstream.

## Safe next steps

Read-only suggestions:

- Ask the operator of the target whether the switch at 15:10:23.881Z (request id
  `df779f69aa62`, E2) was intended, and who set it.
- Keep reading `faultline_chaos_enabled` and the 503 samples of `http_requests_total`
  on `/metrics`; a gauge of 0 and flat 503 counters mark the end of the injection.
- Read `lab/logs/app.log` for a `chaos_disabled` event and for further `chaos_failure`
  lines; count them against the non-`konan-` request lines to size the user impact.
- If errors were reported before 15:10:18Z, look for telemetry of the earlier process
  instance; this surface does not hold it.

## Gaps

- **Before the process start.** The log starts at 15:10:18.946Z and has no backups. The
  complaint says "the last few minutes", and the complaint arrived 12 s after the start.
  Errors under an earlier process instance can be neither confirmed nor excluded.
- **Who set the switch.** The telemetry shows a local `POST /chaos/enable` (E2), no
  identity and no reason.
- **Size of the impact.** User traffic stops at 15:10:25.428Z. The 9 % share rests on
  32 requests in about half a second; nothing measures the impact after that.
- **Routes.** Injection was seen on three GET routes. Five `POST /orders` requests after
  the switch succeeded; whether order creation or `/health` can fail is not evidenced.
- **Outside the process.** All evidence is the target's own log and metrics; the lab has
  no tier in front of the target.
- **Tokens.** Not captured in this session.
