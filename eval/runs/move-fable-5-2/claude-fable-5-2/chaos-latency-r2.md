---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-wide-slowness
  trigger: "manual (/konan, human profile; fingerprint human-1794746756; alertname human-report; no severity stated; startsAt 2026-11-15T12:45:56Z; investigation start 2026-11-15T12:46:07Z; trigger latency 11 s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-15T12:46:07Z
  concluded: 2026-11-15T12:49:56Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The chaos switch inside the target was turned on at 2026-11-15T12:45:37.802Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on, every business request (products, orders) gets an added delay of up to about 1.5 s with no error status, and /health is not delayed."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was turned on at 12:45:37.802Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on, it adds a delay to every business request (products, orders) and no errors; /health is not delayed."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E20, E21]
    evidence_against: []
  - id: H2
    statement: "The target's own code has a slow path for specific inputs, and that code path causes the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E8, E6, E10, E16, E7, E9, E11]
  - id: H3
    statement: "Demand exceeds the capacity of the target, and requests wait in a queue."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14]
  - id: H4
    statement: "A process lifecycle event (a restart, a warm-up after the start at 12:45:31Z, or a hang) causes the slowness."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E18]
    evidence_against: [E3, E4, E5, E16, E17, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:37.802Z"
    quote: '{"ts": "2026-11-15T12:45:37.802Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "dff42aaf7227", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:37.803Z"
    quote: '{"ts": "2026-11-15T12:45:37.803Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "dff42aaf7227", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.762, "client": "127.0.0.1:51845"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:32.623Z"
    quote: '{"ts": "2026-11-15T12:45:32.623Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "0a39248772c4", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.108, "client": "127.0.0.1:51841"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:33.681Z"
    quote: '{"ts": "2026-11-15T12:45:33.681Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "e8d7066af49d", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.006, "client": "127.0.0.1:51842"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:34.740Z"
    quote: '{"ts": "2026-11-15T12:45:34.740Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d1bc256fb2c0", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.76, "client": "127.0.0.1:51843"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:40.894Z"
    quote: '{"ts": "2026-11-15T12:45:40.894Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "b239a57bf371", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1033.779, "client": "127.0.0.1:51848"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:42.102Z"
    quote: '{"ts": "2026-11-15T12:45:42.102Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "adeb1b9292b0", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 140.409, "client": "127.0.0.1:51849"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:44.385Z"
    quote: '{"ts": "2026-11-15T12:45:44.385Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "2446ee0b95b2", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1213.875, "client": "127.0.0.1:51850"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:46.157Z"
    quote: '{"ts": "2026-11-15T12:45:46.157Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "19355f593d67", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 704.482, "client": "127.0.0.1:51851"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:48.333Z"
    quote: '{"ts": "2026-11-15T12:45:48.333Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "1a5c7c436473", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1115.539, "client": "127.0.0.1:51852"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:49.650Z"
    quote: '{"ts": "2026-11-15T12:45:49.650Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "cd564e826495", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 252.945, "client": "127.0.0.1:51853"}'
  - id: E12
    type: metric
    source: "/metrics, scrape request_id=konan-1794746853-95943 @ 2026-11-15T12:47:33Z"
    quote: "faultline_chaos_enabled 1"
  - id: E13
    type: metric
    source: "/metrics, scrape request_id=konan-1794746853-95943 @ 2026-11-15T12:47:33Z (the complete http_requests_total family and the complete, empty http_exceptions_total family)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 6
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E14
    type: probe
    source: "/health request_id=konan-1794746785-95870 @ 2026-11-15T12:46:25Z"
    quote: |-
      {"status":"ok","uptime_seconds":53.600878624711186}
      -- HTTP 200 in 0.001345s request_id=konan-1794746785-95870
  - id: E15
    type: probe
    source: "/products request_id=konan-1794746783-95855 @ 2026-11-15T12:46:24Z"
    quote: "-- HTTP 200 in 0.813855s request_id=konan-1794746783-95855"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:47:09.409Z (investigator probe)"
    quote: '{"ts": "2026-11-15T12:47:09.409Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794746827-95928", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1443.186, "client": "127.0.0.1:51886"}'
  - id: E17
    type: metric
    source: "/metrics, scrape request_id=konan-1794746772-95841 @ 2026-11-15T12:46:12Z"
    quote: |-
      process_uptime_seconds 40.22393195796758
      process_max_rss_bytes 47136768
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:45:31.862Z (the only startup event in the log)"
    quote: '{"ts": "2026-11-15T12:45:31.862Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E19
    type: metric
    source: "/metrics, scrape request_id=konan-1794746853-95943 @ 2026-11-15T12:47:33Z"
    quote: |-
      process_uptime_seconds 121.76625012466684
      process_max_rss_bytes 47136768
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:46:24.873Z (investigator probe)"
    quote: '{"ts": "2026-11-15T12:46:24.873Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794746784-95860", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 107.892, "client": "127.0.0.1:51877"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:46:25.191Z (investigator probe)"
    quote: '{"ts": "2026-11-15T12:46:25.191Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794746784-95865", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 236.206, "client": "127.0.0.1:51878"}'
gaps:
  - "No telemetry before 2026-11-15T12:45:31.862Z: the log starts at the process start and has no rotated backups, so the complaint's 'last few minutes' cannot be checked beyond the 24 s of history before the complaint; slowness in an earlier process life is out of reach."
  - "The 'fast before the switch' sample is small: three business requests (GET /products, GET /products/1, POST /orders) in the 6 s between startup and the switch; there is no GET /orders sample before the switch."
  - "The delay rule is inferred, not read: observed added delays range from 108 ms to 1443 ms and stay below the configured 1500 ms, but no telemetry states how the switch picks the delay."
  - "Who or what sent POST /chaos/enable (client 127.0.0.1:51845) is not on the surface; the chaos state endpoint is operator surface and was not read."
  - "No CPU, in-flight request, or worker gauge exists on this surface; load saturation is excluded from request volume and the fast /health only."
  - "Paths not probed: /products/3, /products/4, /products/5, /orders/{id}, /openapi.json; the complaint is about latency on all pages, and the sampled paths cover each business route once or more."
usage:
  model: claude-fable-5-2
  tokens: 1241320
  wall_clock_seconds: 229
---

# Shop-wide slowness: latency-injecting chaos switch is on

## Summary

**Root cause identified.** The chaos switch inside faultline was turned on at
2026-11-15T12:45:37.802Z with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E1, E2),
and it is still on (E12). Since that moment every business request — product list,
product page, order list, order creation — takes between about 0.1 s and 1.4 s, against
about 1 ms before the switch (E3–E5 before; E6–E11, E15, E16, E20, E21 after). No request
fails: every status is 200 or 201 and the exception counter has no series (E13), which
matches `failure_rate: 0.0`. `/health` is not delayed and answers in about 1 ms (E14) —
the healthy-monitoring shape the complaint describes. Class `infra-process`, cause
`degradation-switch`.

Impact: all six non-investigator business requests after the switch were slow
(140 ms to 1214 ms; E6–E11); none errored. Confidence is high: the marker, the gauge, the
before/after durations on the same input (E4 against E8), and the investigator's own
probes all agree, and the judge validated H1 and invalidated the three alternatives.
The limits are the short history (the process was 24 s old at the complaint) and the
inferred delay rule — see Gaps.

## Timeline

- **12:45:31.862Z** — process start, the only startup event in the log (E18).
- **12:45:32.623Z – 12:45:34.740Z** — business requests take 1.0 ms to 1.8 ms (E3, E4, E5).
- **12:45:37.802Z** — **configuration-change marker**: `chaos mode enabled`,
  `failure_rate 0.0`, `extra_latency_ms 1500`, through `POST /chaos/enable -> 200`
  (E1, E2).
- **12:45:40.894Z** — first slow user request: `GET /products` in 1033.779 ms (E6).
- **12:45:42.102Z – 12:45:49.650Z** — five more user requests, 140 ms to 1214 ms, all
  200/201 (E7, E8, E9, E10, E11).
- **12:45:56Z** — complaint raised (`startsAt`).
- **12:46:07Z** — investigation start (trigger latency 11 s).
- **12:46:12Z** — first metrics scrape: uptime 40.2 s (E17).
- **12:46:24Z – 12:46:25Z** — investigator probes: `/products` 0.814 s, `/products/1`
  108 ms, `/orders` 236 ms, `/health` 1.3 ms (E15, E20, E21, E14).
- **12:47:09.409Z** — investigator probe `GET /products` in 1443.186 ms (E16).
- **12:47:33Z** — gauge still `faultline_chaos_enabled 1`; uptime 121.8 s, no reset;
  all counters 200/201; no exception series (E12, E19, E13).

## Investigation

**Trigger.** Manual, `/konan`. The complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794746756",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast." },
  "startsAt": "2026-11-15T12:45:56Z"
}
```

Investigation start: 2026-11-15T12:46:07Z. Surface contract: `docs/lab.md`
(`KONAN_ADAPTER` unset).

**Baseline.** `/health` 200 in about 1–2 ms; metrics: all statuses 200/201, no exception
series, `faultline_chaos_enabled 1`, uptime 40.2 s; log: 22 lines from 12:45:31.862Z, no
ERROR line, one WARNING line. Business surface checked, not just health: `/products`
0.814 s, `/products/1` 0.109 s, `/orders` 0.239 s.

**Triage.** Three lenses in parallel, each blind to the others: infra-process,
software-defect, interfaces. All three independently cited the `chaos_enabled` marker
at 12:45:37.802Z and the before/after duration split. The software-defect lens found no
anomaly in its domain (no exception, no error status, latency not input-dependent). The
interfaces lens found no contract violation or gateway status and classed the marker as
a switch inside the target. The infra-process lens found one startup, no restart, flat
peak memory.

**Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete
(marker, gauge, before/after on the same input, probes confirming the prediction).

**Judge.** One fresh judge, evidence-only. Verdicts: H1 validated; H2, H3, H4
invalidated. The judge named three limits on H1 (complaint text not shown to it, small
pre-switch sample, delay rule fitted to data); the last two are recorded under Gaps.
The judge marked three citations as weak (the status counters against H2, peak memory
against H3, completed-request counters against a hang in H4); the machine core drops the
first two. Ledger note: the judge received two summary entries — one combining both
uptime scrapes (here E17 and E19) and one whole-file log summary (no ERROR line, no
`chaos_disabled` or `chaos_failure` event, post-switch business durations 107.892 ms to
1443.186 ms, health and metrics below 13 ms). This journal replaces the summary with the
verbatim lines E20 and E21; the whole-file facts were re-read from the log at 12:47:33Z.

One round, no second round needed.

## Hypotheses

### H1 — chaos switch injects latency (validated)

The marker (E1) names the mechanism and its parameters; its access line (E2) shows the
request that turned it on. Predictions and results: business requests fast before
(E3, E4, E5: 1.0–1.8 ms) and slow after (E6–E11, E16, E20, E21: 108–1443 ms); added
delay at or below 1500 ms (maximum 1443.186 ms, E16); no error status (E13); health
stays fast (E14); gauge reads 1 (E12). The same input, `/products/1`, took 1.006 ms
before and 1213.875 ms after (E4, E8). No evidence against.

### H2 — slow code path for specific inputs (invalidated)

The same input is fast, then slow (E4 against E8), and one input varies while slow:
`/products` took 1033.779, 1115.539, and 1443.186 ms (E6, E10, E16). Every business
route is slow (E7, E9, E11), so no input-specific path explains it. It would reopen on
one business request that stays near 1 ms after the marker.

### H3 — load saturation (invalidated)

24 requests in total in about two minutes (E13), and `/health` answers in 1.3 ms while
business requests take up to 1.4 s (E14) — a queue would delay health too. It would
reopen on an in-flight or CPU metric that shows contention; this surface has none.

### H4 — process lifecycle event (invalidated)

The process did start 24 s before the complaint (E18), but requests 1–3 s after the
start took about 1 ms (E3, E4, E5), the slowest request came 97 s after the start (E16),
so nothing fades, and uptime rises from 40.2 s to 121.8 s without a reset (E17, E19).
It would reopen on a second startup line or an uptime reset.

## Safe next steps

Read-only only:

- Ask the operator who turned the switch on (request id `dff42aaf7227`, client
  `127.0.0.1:51845`, 12:45:37.802Z) whether it was intended — a planned test or drill
  would explain it.
- Watch `faultline_chaos_enabled` on `/metrics` and the log for a `chaos_disabled`
  event; business durations should return to about 1 ms when the gauge reads 0.
- Compare `http_request_duration_seconds_sum`/`_count` per path over a few scrapes to
  follow the average latency without adding business probes.
- If rotated logs or an earlier process's logs exist elsewhere, read them to check the
  complaint's "last few minutes" against the 24 s of history visible here.

## Gaps

- **History.** The log starts at the process start (12:45:31.862Z) with no rotated
  backups. The complaint says "the last few minutes"; the telemetry shows the onset 18 s
  before the complaint and nothing earlier. Slowness in an earlier process life cannot
  be confirmed or excluded.
- **Small pre-switch sample.** Three business requests in 6 s, none of them
  `GET /orders`.
- **Delay rule inferred.** Delays vary from 108 ms to 1443 ms under a configured 1500;
  "variable, up to the configured value" fits, but no telemetry states the rule.
- **Who turned it on.** The actor behind `POST /chaos/enable` is not on the
  investigator's surface, and the chaos state endpoint is operator surface.
- **No saturation gauges.** No CPU, in-flight, or worker metric; H3 is excluded from
  volume and health latency only.
- **Paths not probed.** `/products/3`, `/products/4`, `/products/5`, `/orders/{id}`,
  `/openapi.json` — not needed for a latency complaint that every sampled route
  reproduces.
