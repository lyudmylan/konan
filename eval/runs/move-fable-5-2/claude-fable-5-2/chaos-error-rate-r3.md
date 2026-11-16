---
konan_journal: 2
investigation:
  id: 2026-11-15-intermittent-503s
  trigger: 'manual — /konan adapter (human profile). Complaint object: {"source": "human", "fingerprint": "human-1794746001", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."}, "startsAt": "2026-11-15T12:33:21Z"}. Investigation start 2026-11-15T12:33:35Z; trigger latency 14 s.'
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-15T12:33:35Z
  concluded: 2026-11-15T12:37:28Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The chaos switch inside the target was turned on at 2026-11-15T12:33:04.517Z with failure_rate 0.4 and error_status 503, and while it is on it injects HTTP 503 into a random fraction of requests, observed on POST /orders and GET /products/5."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was turned on at 2026-11-15T12:33:04.517Z (failure_rate 0.4, error_status 503); while it is on it injects HTTP 503 into a random fraction of requests, which users see as page loads and orders that fail and then work on retry."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E19, E20, E21, E22, E23, E24, E25]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled error for specific inputs (product 5, or specific orders), and that error is the cause of the failures."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E20]
    evidence_against: [E6, E13, E19, E21, E23, E24, E25, E10]
  - id: H3
    statement: "The process crashes, restarts, or runs out of a resource, and that is the cause of the intermittent failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E16, E17, E18, E1]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794746016-95080"
    quote: |-
      {"status":"ok","uptime_seconds":39.71341245807707}
      -- HTTP 200 in 0.003929s request_id=konan-1794746016-95080
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:04.517Z"
    quote: '{"ts": "2026-11-15T12:33:04.517Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "29befc6fb8b5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:04.517Z"
    quote: '{"ts": "2026-11-15T12:33:04.517Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "29befc6fb8b5", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.499, "client": "127.0.0.1:51706"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:09.721Z"
    quote: '{"ts": "2026-11-15T12:33:09.721Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ce88bb8d87b7", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:09.721Z"
    quote: '{"ts": "2026-11-15T12:33:09.721Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "ce88bb8d87b7", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.166, "client": "127.0.0.1:51710"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:11.834Z"
    quote: '{"ts": "2026-11-15T12:33:11.834Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "6bce807a0556", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:11.834Z"
    quote: '{"ts": "2026-11-15T12:33:11.834Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "6bce807a0556", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.295, "client": "127.0.0.1:51712"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:12.893Z"
    quote: '{"ts": "2026-11-15T12:33:12.893Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "65c6375a9241", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:12.893Z"
    quote: '{"ts": "2026-11-15T12:33:12.893Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "65c6375a9241", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.266, "client": "127.0.0.1:51713"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:32:59.393Z"
    quote: '{"ts": "2026-11-15T12:32:59.393Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1ccbd488b2bc", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.953, "client": "127.0.0.1:51703"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:01.453Z"
    quote: '{"ts": "2026-11-15T12:33:01.453Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "061fbd18c79c", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.78, "client": "127.0.0.1:51704"}'
  - id: E12
    type: metric
    source: "/metrics, request_id=konan-1794746111-95178 (about 2026-11-15T12:35:11Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E13
    type: metric
    source: "/metrics, request_id=konan-1794746111-95178 (about 2026-11-15T12:35:11Z)"
    quote: |-
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E14
    type: metric
    source: "/metrics, request_id=konan-1794746016-95085 (about 2026-11-15T12:33:36Z)"
    quote: |-
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 2
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:32:56.492Z"
    quote: '{"ts": "2026-11-15T12:32:56.492Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E16
    type: metric
    source: "/metrics, request_id=konan-1794746016-95085 (about 2026-11-15T12:33:36Z)"
    quote: "process_uptime_seconds 40.298836917150766"
  - id: E17
    type: metric
    source: "/metrics, request_id=konan-1794746111-95178 (about 2026-11-15T12:35:11Z)"
    quote: "process_uptime_seconds 135.16564870812"
  - id: E18
    type: metric
    source: "/metrics, request_id=konan-1794746016-95085 and request_id=konan-1794746111-95178 (same value in both)"
    quote: "process_max_rss_bytes 47284224"
  - id: E19
    type: probe
    source: "/products/5, request_id=konan-1794746106-95166"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001453s request_id=konan-1794746106-95166
  - id: E20
    type: probe
    source: "/products/5, request_id=konan-1794746105-95156"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1794746105-95156"}
      -- HTTP 503 in 0.001012s request_id=konan-1794746105-95156
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:35:05.125Z"
    quote: '{"ts": "2026-11-15T12:35:05.125Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794746105-95156", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:33:13.951Z"
    quote: '{"ts": "2026-11-15T12:33:13.951Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "3e99238f44ae", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.824, "client": "127.0.0.1:51714"}'
  - id: E23
    type: metric
    source: "/metrics, request_id=konan-1794746111-95178 (about 2026-11-15T12:35:11Z)"
    quote: |-
      http_requests_total{method="GET",path="/products/5",status="503"} 4
      http_requests_total{method="POST",path="/orders",status="503"} 2
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:34:31.477Z"
    quote: '{"ts": "2026-11-15T12:34:31.477Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794746071-95147", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:35:05.662Z"
    quote: '{"ts": "2026-11-15T12:35:05.662Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794746105-95161", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
gaps:
  - "Who or what sent POST /chaos/enable is not visible: the log shows only client 127.0.0.1:51706, and the operator surface is outside the investigator's contract."
  - "The telemetry starts at the process start, 2026-11-15T12:32:56.492Z. Nothing before it is visible, so the complaint's 'a few minutes ago' cannot be compared with an earlier period, and the reason for that start (planned start or a restart after a crash) is not in the log."
  - "No non-investigator request appears in the log after 2026-11-15T12:33:16.068Z. The claim that the injection continues rests on the gauge and on the investigator's own probes."
  - "The user-impact sample is small: 10 non-investigator requests after the switch-on. No successful order after the switch-on was observed (2 of 2 failed); the investigator cannot send an order (read-only)."
  - "The switch state was read from the gauge and the log only; the chaos status endpoint is operator surface. The configured values (0.4, 503, 0 ms) come from the switch-on log line and may have changed without a new log line only if the target does not log such a change."
  - "Only product ids 1, 2, 4 and 5 were requested in the window; product 3 was not requested and was not probed."
usage:
  model: claude-fable-5-2
  tokens: 1605937
  wall_clock_seconds: 233
---

# Intermittent 503s on orders and product pages: the chaos switch is on

## Summary

**Verdict: root cause identified.** The target's internal chaos switch was turned on at
2026-11-15T12:33:04.517Z with `failure_rate 0.4` and `error_status 503` (E2), through a
`POST /chaos/enable` request (E3). From then on a random fraction of requests gets an
injected HTTP 503; each 503 in the log has a `chaos_failure` line with the same request
id (E4–E9, E21, E24, E25), and the six paired lines account for all six 503s the metrics
count (E23). Class `infra-process`, cause `degradation-switch`.

Impact on users: 3 of the 10 non-investigator requests after the switch-on failed — both
orders (E5, E9) and one product page (E7). Before the switch-on, all 6 requests succeeded
(E10, E11). The same input fails and then succeeds: product 5 returned 503 and, 1.1 s
later, 200 (E20, E19). That is the "fails, then works on retry" of the complaint.

The health dashboard is green because the health endpoint still returns 200 (E1): the
process is alive, did not restart (E15, E16, E17), and shows no memory growth (E18). No
unhandled exception was counted (E13). The switch was still on at about 12:35:11Z (E12).

Confidence: high. The evidence is deterministic (a logged switch-on marker, a paired
marker on every failure, a live gauge). Who turned the switch on is not visible.

## Timeline

All times UTC, 2026-11-15.

- 12:32:56.492 — the process starts; the only `startup` event in the log (E15).
- 12:32:57–12:33:01 — six requests, all 2xx, including an order with 201 (E10, E11).
- **12:33:04.517 — chaos switch turned on**: `failure_rate 0.4`, `error_status 503`,
  `extra_latency_ms 0`, via `POST /chaos/enable` from `127.0.0.1:51706` (E2, E3).
- 12:33:09.721 — first failure: `POST /orders -> 503`, chaos-injected (E4, E5).
- 12:33:11.834 — `GET /products/5 -> 503`, chaos-injected (E6, E7).
- 12:33:12.893 — `POST /orders -> 503`, chaos-injected (E8, E9).
- 12:33:13.951 — `GET /products/1 -> 200`: successes interleave with failures (E22).
- 12:33:21 — the complaint is raised (`startsAt`).
- 12:33:35 — the investigation starts (trigger latency 14 s).
- 12:33:36 — `/health` 200 (E1); three 503s counted (E14); uptime 40.3 s (E16).
- 12:34:31–12:35:06 — investigator probes of `/products/5`: 503, 503, 503, then 200
  (E24, E20, E21, E25, E19). These are investigator traffic, not user impact.
- 12:35:11 — the gauge still reads 1 (E12); uptime 135.2 s, no reset (E17); six 503s
  counted in total (E23); the exception counter has no sample (E13).

## Investigation

Complaint object, as synthesized by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794746001",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green." },
  "startsAt": "2026-11-15T12:33:21Z"
}
```

Investigation start: 2026-11-15T12:33:35Z. Surface contract: `docs/lab.md`
(`KONAN_ADAPTER` unset).

- **Baseline.** `/health` 200 (E1). `/metrics`: `faultline_chaos_enabled 1`, three 503s
  on two routes (E14), no exception samples, uptime 40.3 s (E16). Log: one startup (E15),
  a `chaos_enabled` marker (E2), all durations under 13 ms.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the chaos switch-on marker at the
  onset and the paired `chaos_failure` lines. The infra-process lens reported no
  restart and no memory or latency change. The software-defect lens reported no
  exception, and one open point: product 5 had no successful request yet.
- **Deep-dive.** No subagent: the triage evidence for H1 was deterministic and complete.
  The orchestrator ran one cheap test that could kill H2 — three probes of
  `/products/5` (503, 503, 200; E20, E25, E19) — plus one `/products` probe and a second
  `/metrics` snapshot (E12, E13, E17, E23).
- **Judge.** One fresh judge, evidence only. H1 validated; H2 invalidated; H3
  invalidated. The judge's limits on H1 are honoured: the statement names the routes
  on which injection was observed, not "any route". The judge asked for a join of all
  5xx access lines against `chaos_failure` lines to settle H2; the whole log was read,
  and all six 503 access lines have a paired line (E4, E6, E8, E21, E24, E25 against the
  six counted in E23).
- One round; budget not exhausted.

## Hypotheses

### H1 — the chaos switch injects 503s (validated)

The switch-on marker (E2) and its request (E3) sit between the last good request (E11)
and the first failure (E4, E5). No 5xx exists before the marker. Every 503 carries a
`chaos_failure` line with the same request id (E4–E9, E21, E24, E25), and the metric
total of six 503s (E23) equals the six paired lines. Failures and successes interleave on
the same route (E7, E22) and on the same input (E20, E19). The gauge reads 1 (E12) and no
exception was counted (E13). The observed user failure rate, 3 of 10, is consistent with
the configured 0.4 on a small sample. Nothing found against.

### H2 — a defect in the target's code for specific inputs (invalidated)

For: product 5 failed on its first four observed requests (E7, E24, E20, E25). Against:
each of those failures is marked as chaos-injected (E6, E24, E21, E25); the same input
then returned 200 (E19); the exception counter has no sample (E13); orders succeeded
before the switch-on (E10); the metrics count no 503 outside the six paired ones (E23).

### H3 — a crash, restart, or resource exhaustion (invalidated)

For: the process started only 8 s before the switch-on (E15). Against: one startup
event only; uptime rose from 40.3 s to 135.2 s with no reset (E16, E17); peak memory is
identical in both snapshots (E18); health is 200 (E1). The process is alive and
degraded, not dying. Why it started at 12:32:56Z is not in the telemetry (see Gaps).

## Safe next steps

Read-only suggestions:

- Ask the operators who sent `POST /chaos/enable` at 12:33:04.517Z (request id
  `29befc6fb8b5`, client `127.0.0.1:51706`) and whether a test or a drill was planned.
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` event; after it,
  confirm that the 503 counters stop growing.
- Add the business routes (orders, product pages) to the health dashboard view: the
  health endpoint stays green while the switch is on.
- Check the launcher record for the process start at 12:32:56Z.

## Gaps

- **Who turned the switch on.** The log shows the client address only. The operator
  surface is outside the investigator's contract.
- **History before 12:32:56Z.** The log begins at the process start. The complaint says
  "a few minutes ago"; the telemetry shows the onset 17 s before the complaint, and
  nothing earlier can be checked.
- **Current user impact.** No non-investigator request exists after 12:33:16.068Z. The
  continuing injection is shown by the gauge (E12) and by investigator probes only.
- **Small sample.** Ten user requests after the switch-on. No order succeeded after the
  switch-on in the window, and a read-only investigator cannot send one; that orders
  "work again on retry" is consistent with the mechanism but was not observed.
- **Switch configuration.** Read from the switch-on log line and the gauge; the chaos
  status endpoint is operator surface.
- **Unexercised inputs.** Product 3 was not requested and not probed.
