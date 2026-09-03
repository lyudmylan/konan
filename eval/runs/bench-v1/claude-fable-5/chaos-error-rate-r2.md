---
konan_journal: 1
investigation:
  id: 2026-08-19-intermittent-503s-chaos-enabled
  trigger: "manual (/konan; complaint object: source=human, fingerprint=human-1787159258, labels.alertname=human-report, startsAt=2026-08-19T17:07:38Z; investigation start 2026-08-19T17:07:42Z; trigger latency 4s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-19T17:07:42Z
  concluded: 2026-08-19T17:09:52Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change at 17:07:21Z enabled chaos mode (failure_rate 0.4, error_status 503), which injects 503 responses probabilistically on shop requests while /health stays 200, producing intermittent user-facing failures that succeed on retry."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode enabled at 17:07:21Z (failure_rate 0.4, error_status 503) injects 503 failures probabilistically on shop requests; /health is unaffected, so the dashboard stays green."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E9]
    evidence_against: [E7, E8]
  - id: H2
    statement: "An unhandled exception in request handling produces the user-visible errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E10]
  - id: H3
    statement: "A process crash/restart loop causes the intermittent failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:07:21.796Z"
    quote: "{\"ts\": \"2026-08-19T17:07:21.796Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"e139b87de8a2\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:07:23.895Z"
    quote: "{\"ts\": \"2026-08-19T17:07:23.895Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"34a0de55d338\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} / {\"ts\": \"2026-08-19T17:07:23.895Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 503\", \"request_id\": \"34a0de55d338\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.361, \"client\": \"127.0.0.1:63312\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:07:24.963Z and 2026-08-19T17:07:26.030Z"
    quote: "{\"ts\": \"2026-08-19T17:07:24.963Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"2acbfbf68fcb\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} / {\"ts\": \"2026-08-19T17:07:24.963Z\", ... \"message\": \"GET /products/1 -> 503\", \"request_id\": \"2acbfbf68fcb\", ... \"status\": 503, \"duration_ms\": 0.317, \"client\": \"127.0.0.1:63313\"} / {\"ts\": \"2026-08-19T17:07:26.030Z\", ... \"message\": \"chaos-injected failure\", \"request_id\": \"5a253ae4f51d\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/2\"} / {\"ts\": \"2026-08-19T17:07:26.030Z\", ... \"message\": \"GET /products/2 -> 503\", \"request_id\": \"5a253ae4f51d\", ... \"status\": 503, \"duration_ms\": 0.291, \"client\": \"127.0.0.1:63314\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:07:27.096Z–2026-08-19T17:07:33.499Z"
    quote: "\"message\": \"POST /orders -> 201\", \"request_id\": \"4993fd97ad38\" / \"message\": \"GET /products -> 200\", \"request_id\": \"7cd4f991f848\" / \"message\": \"GET /products/5 -> 200\", \"request_id\": \"76e275ce676d\" / \"message\": \"POST /orders -> 201\", \"request_id\": \"14e968a6ab40\" / \"message\": \"GET /products/1 -> 200\", \"request_id\": \"0f1697c8760e\" / \"message\": \"GET /orders -> 200\", \"request_id\": \"5862c890b534\" / \"message\": \"GET /products/4 -> 200\", \"request_id\": \"1bba0d94efc9\""
  - id: E5
    type: metric
    source: "/metrics @ request_id=konan-1787159280-66914 (2026-08-19T17:08:00Z)"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1 / faultline_chaos_enabled 1 / # TYPE http_exceptions_total counter (no series follow)"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:07:14.464Z–2026-08-19T17:07:18.699Z"
    quote: "\"message\": \"GET /health -> 200\", \"request_id\": \"ff7f2a3a8d45\" / \"message\": \"GET /health -> 200\", \"request_id\": \"bb9e1a7ad9a8\" / \"message\": \"GET /products -> 200\", \"request_id\": \"b3eaeed751f0\" / \"message\": \"GET /products/1 -> 200\", \"request_id\": \"37cec70ae79e\" / \"message\": \"POST /orders -> 201\", \"request_id\": \"6ba633bb23ef\" / \"message\": \"GET /products/2 -> 200\", \"request_id\": \"47feacf6f0ca\""
  - id: E7
    type: probe
    source: "/products, /products/1, /products/2, /products/5, /orders @ request_id=konan-1787159302-66929 … konan-1787159334-66980 (2026-08-19T17:08:22Z–17:08:54Z)"
    quote: "-- HTTP 200 in 0.001316s request_id=konan-1787159302-66929 / -- HTTP 200 in 0.001375s request_id=konan-1787159305-66936 / -- HTTP 200 in 0.001290s request_id=konan-1787159307-66942 / -- HTTP 200 in 0.001325s request_id=konan-1787159309-66948 / -- HTTP 200 in 0.001343s request_id=konan-1787159311-66954 / -- HTTP 200 in 0.001409s request_id=konan-1787159329-66967 / -- HTTP 200 in 0.001325s request_id=konan-1787159331-66973 / -- HTTP 200 in 0.001406s request_id=konan-1787159334-66980"
  - id: E8
    type: metric
    source: "/metrics @ request_id=konan-1787159318-66961 (2026-08-19T17:08:38Z)"
    quote: "faultline_chaos_enabled 1 / http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 5"
  - id: E9
    type: probe
    source: "/health @ request_id=konan-1787159278-66908 (2026-08-19T17:07:58Z)"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":44.489512792089954} -- HTTP 200 in 0.001684s request_id=konan-1787159278-66908"
  - id: E10
    type: log
    source: "lab/logs/app.log (entire file, 31 lines, read at 2026-08-19T17:08:05Z)"
    quote: "no line contains \"unhandled_exception\", \"stack\", or \"level\": \"ERROR\"; the only WARNING lines are \"chaos mode enabled\" and the three \"chaos-injected failure\" lines"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:07:13.704Z"
    quote: "{\"ts\": \"2026-08-19T17:07:13.704Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E12
    type: metric
    source: "/metrics @ konan-1787159280-66914 (17:08:00Z) and konan-1787159318-66961 (17:08:38Z)"
    quote: "process_uptime_seconds 47.021224749973044 / process_uptime_seconds 85.07434225012548"
gaps:
  - "Triage lenses were not spawned: the baseline (E1–E6, E10–E12) already excluded the software-defect and infra-process domains with evidence and exposed the interfaces-domain cause; this is a deliberate skip, not coverage theater."
  - "Whether chaos is still injecting failures at conclusion time is not reproduced: all eight stamped investigator probes (E7) returned 200 (p≈0.017 at a 0.4 rate), while the gauge still reads 1 (E8). Unstamped user traffic after 17:07:33Z is absent from the log, so ongoing user impact cannot be measured from telemetry; the operator surface (/chaos) is outside the investigator's read-only contract."
  - "The issuer of the POST /chaos/enable at 17:07:21Z (client 127.0.0.1:63311) is not identifiable from the surface; the lab has no audit trail beyond the access line."
usage:
  model: claude-fable-5
  tokens: 1398170
  wall_clock_seconds: 130
---

# Intermittent 503s on shop routes after chaos mode was enabled at 17:07:21Z

## Summary

**Root cause identified** (class: interfaces). At 2026-08-19T17:07:21.796Z a runtime
configuration change enabled chaos mode with `failure_rate 0.4` and `error_status 503`
(E1). Two seconds later the first user request failed with a `chaos_failure` event and a
503 (E2), followed by two more (E3); subsequent user requests succeeded (E4), which is
the "fails, then works on retry" shape users reported. `/health` is not subject to the
injection and returns 200 (E9), so the health dashboard stays green — the
healthy-monitoring trap. No exceptions (E5, E10) and no restarts (E11, E12). Impact
observed in telemetry: 3 of 10 non-investigator shop requests after the marker returned
503. Confidence: high on the mechanism; the judge validated H1. Uncertain: whether the
injection is still firing — the gauge still reads 1 (E8), but eight investigator probes
all passed (E7).

## Timeline

- 17:07:13.704Z — process start, single `startup` marker (E11).
- 17:07:14–17:07:18Z — all user traffic 200/201 (E6). Last known-good.
- 17:07:21.796Z — **config-change marker**: `chaos_enabled`, failure_rate 0.4, 503 (E1).
- 17:07:23.895Z — first user 503, `chaos_failure`, GET /products (E2). First known-bad.
- 17:07:24.963Z, 17:07:26.030Z — 503s on /products/1, /products/2 (E3).
- 17:07:27–17:07:33Z — seven user requests succeed, incl. two orders (E4).
- 17:07:38Z — complaint received; 17:07:42Z — investigation start.
- 17:07:58Z–17:08:54Z — investigator probes: /health 200 (E9); metrics show gauge 1 and
  three 503 series, no exceptions (E5); eight shop probes all 200 (E7); gauge still 1,
  503 counters unchanged (E8); uptime monotonic (E12).

## Investigation

Baseline: `/health` (E9), `/metrics` (E5), full log (31 lines). The baseline already
contained the change marker and the chaos-tagged failures; software-defect and
infra-process domains were excluded from the same data (E10, E11, E12), so triage lenses
were not spawned (recorded under Gaps). Confirmation probes of the business surface (E7,
E8) tested the "still active" prediction. No deep-dive agents were needed; the judge
(fresh agent, claims plus verbatim evidence only) returned: H1 validated, H2 invalidated,
H3 invalidated.

## Hypotheses

### H1 — chaos mode enabled injects 503s (interfaces) — validated
For: marker precedes first failure (E1→E2), every failure carries `chaos_failure` (E2,
E3), gauge reads 1 (E5, E8), clean before the marker (E6), successes interleaved after
(E4), /health unaffected (E9). Against: eight stamped probes all 200 (E7) and 503
counters unchanged (E8) — low probability at rate 0.4 but not a refutation while the
gauge is 1; it leaves the "still active" question open (Gaps).

### H2 — unhandled exception (software-defect) — invalidated
`http_exceptions_total` has no series (E5); no `unhandled_exception`, `stack`, or ERROR
lines in the log (E10).

### H3 — crash/restart loop (infra-process) — invalidated
One startup marker, before all traffic (E11); uptime monotonic 47s→85s across 38s (E12).

## Safe next steps

- Re-read `/metrics` and compare `faultline_chaos_enabled` and the `status="503"`
  counters over the next minutes to see whether injection is still firing on user traffic.
- Tail `lab/logs/app.log` for further `chaos_failure` lines with non-`konan-` request ids
  (user impact) and for a `chaos_disabled` marker.
- Ask who issued the POST /chaos/enable at 17:07:21.796Z (client 127.0.0.1:63311).

## Gaps

See frontmatter: lenses deliberately skipped on baseline evidence; "still active" not
reproduced by investigator probes; change issuer not identifiable from the surface.
