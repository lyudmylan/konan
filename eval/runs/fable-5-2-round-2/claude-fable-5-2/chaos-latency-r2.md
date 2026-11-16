---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-latency-chaos-switch
  trigger: "manual — /konan human profile; source human; fingerprint human-1794767315; alertname human-report; no severity stated; startsAt 2026-11-15T18:28:35Z; investigation start 2026-11-15T18:28:52Z; trigger latency 17 s"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-15T18:28:52Z
  concluded: 2026-11-15T18:32:12Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos switch inside the target was turned on at 2026-11-15T18:28:17.427Z with failure_rate 0.0 and extra_latency_ms 1500; from that moment each observed shop request took 128 to 1321 ms instead of 1 to 2 ms, with no error statuses, while the health route stayed under 1 ms; the switch was still on at the last reading."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target, turned on at 2026-11-15T18:28:17.427Z with extra_latency_ms 1500 and failure_rate 0.0, adds delay to shop requests while it is on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E15]
    evidence_against: [E16]
  - id: H2
    statement: "The target's own code is slow for specific inputs."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E6, E7, E8, E9, E16]
  - id: H3
    statement: "User demand exceeds the capacity of the process, so requests queue."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E10, E12, E13, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:12.250Z"
    quote: '{"ts": "2026-11-15T18:28:12.250Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d93e2f494bb3", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.229, "client": "127.0.0.1:54872"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:13.306Z"
    quote: '{"ts": "2026-11-15T18:28:13.306Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a7fd3323fb37", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.031, "client": "127.0.0.1:54873"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:14.366Z"
    quote: '{"ts": "2026-11-15T18:28:14.366Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1dc2d18c7b41", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.896, "client": "127.0.0.1:54874"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:17.427Z"
    quote: '{"ts": "2026-11-15T18:28:17.427Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "c3f485ffcfbd", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:17.427Z"
    quote: '{"ts": "2026-11-15T18:28:17.427Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "c3f485ffcfbd", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.603, "client": "127.0.0.1:54875"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:20.689Z"
    quote: '{"ts": "2026-11-15T18:28:20.689Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "8c4e6d29862b", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1203.611, "client": "127.0.0.1:54876"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:25.347Z"
    quote: '{"ts": "2026-11-15T18:28:25.347Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "3ef1fa427613", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1320.647, "client": "127.0.0.1:54879"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:27.255Z"
    quote: '{"ts": "2026-11-15T18:28:27.255Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "538ece026251", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 840.307, "client": "127.0.0.1:54880"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:30.565Z"
    quote: '{"ts": "2026-11-15T18:28:30.565Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "c870935f66f1", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 128.445, "client": "127.0.0.1:54882"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:52.600Z"
    quote: '{"ts": "2026-11-15T18:28:52.600Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794767332-16505", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.532, "client": "127.0.0.1:54901"}'
  - id: E11
    type: metric
    source: "/metrics, request_id=konan-1794767418-16622 (about 2026-11-15T18:30:18Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: metric
    source: "/metrics, request_id=konan-1794767418-16622 (about 2026-11-15T18:30:18Z); the complete http_requests_total section, and the http_exceptions_total section, which has no series lines"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 6
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E13
    type: metric
    source: "/metrics, request_id=konan-1794767418-16622 (about 2026-11-15T18:30:18Z); the earlier reading at request_id=konan-1794767333-16511 was process_uptime_seconds 41.73137079086155 and the same process_max_rss_bytes"
    quote: |-
      process_uptime_seconds 127.30431045778096
      process_max_rss_bytes 48431104
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:28:11.470Z"
    quote: '{"ts": "2026-11-15T18:28:11.470Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: probe
    source: "/products, request_id=konan-1794767337-16522"
    quote: "-- HTTP 200 in 1.270322s request_id=konan-1794767337-16522"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:29:53.193Z"
    quote: '{"ts": "2026-11-15T18:29:53.193Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794767393-16599", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 143.733, "client": "127.0.0.1:54916"}'
gaps:
  - "No off period after the marker was observed: the only off-state samples are three shop requests in the three seconds before the switch, so 'fast again when the switch is off' is untested."
  - "Who or what sent POST /chaos/enable is not established: the log shows a local client (127.0.0.1:54875) and an unstamped request id only."
  - "How extra_latency_ms 1500 maps to the per-request delay is not visible on the surface: observed delays vary from 128 to 1321 ms, all below 1500 ms."
  - "The process was 41 s old at the first probe and the log has no rotated backups, so the baseline before the switch rests on three shop requests."
  - "/orders/{id} and /openapi.json were not probed; 6 of the 15 shop requests in the counters have no duration quoted in the ledger."
  - "The surface has no CPU, thread, or queue-depth metrics; load saturation was excluded from request volume, health latency, and memory only."
  - "The journal was not machine-validated against journal.schema.json in this session."
usage:
  model: claude-fable-5-2
  tokens: 1121918
  wall_clock_seconds: 200
---

# Shop routes slow, no errors: latency-injection switch on in the target

## Summary

**Root cause identified (infra-process, degradation-switch).** An operational chaos
switch inside the target was turned on at 2026-11-15T18:28:17.427Z with
`failure_rate: 0.0` and `extra_latency_ms: 1500` (E4, E5). Before the marker, shop
requests took 1.0 to 1.9 ms (E1, E2, E3). After it, each observed shop request took
128 to 1321 ms (E6, E7, E8, E9, E15, E16). All statuses stayed 200/201 and no exception
was counted (E12), which matches "nothing errors out". The health route stayed at
0.5 ms (E10), which matches "health checks are green and fast". The switch gauge still
read 1 at about 18:30:18Z (E11) and the log holds no `chaos_disabled` event.

User impact, non-investigator traffic only: six user requests after the marker, all
successful, all slow (four are quoted: E6, E7, E8, E9). Confidence is high for the
mechanism; the judge could not refute it. Two limits apply: the claim covers each
*observed* shop request, and the delay size is stated only as observed.

## Timeline

- 18:28:11.470Z — the process starts; the only startup event (E14).
- 18:28:12.250Z to 18:28:14.366Z — last known-good: three user shop requests in 1.0 to 1.9 ms (E1, E2, E3).
- 18:28:17.427Z — **change marker**: `chaos mode enabled`, `failure_rate 0.0`, `extra_latency_ms 1500`, through `POST /chaos/enable -> 200` from 127.0.0.1:54875 (E4, E5).
- 18:28:20.689Z — first known-bad: `GET /products` in 1203.611 ms (E6).
- 18:28:25.347Z to 18:28:30.565Z — more slow user requests: 1320.647 ms, 840.307 ms, 128.445 ms (E7, E8, E9).
- 18:28:35Z — the complaint is raised (`startsAt`).
- 18:28:52Z — the investigation starts; health probe 200, 0.532 ms server-side (E10).
- 18:28:57Z — investigator probe of `/products`: 200 in 1.270322 s (E15).
- 18:29:53.193Z — investigator probe of `/products/1`: 143.733 ms, the delay varies per request (E16).
- about 18:30:18Z — `faultline_chaos_enabled 1`; no restart, peak memory unchanged (E11, E13).

## Investigation

Complaint object, as synthesized by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794767315",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast." },
  "startsAt": "2026-11-15T18:28:35Z"
}
```

Investigation start: 2026-11-15T18:28:52Z (trigger latency 17 s).

- **Baseline.** `/health` 200 in 1.6 ms; `/metrics` all 2xx, no exception series,
  `faultline_chaos_enabled 1`, uptime 41.7 s; `/products` 200 in 1.27 s; log of 23
  lines with one WARNING line and no ERROR line.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three found the same change marker and the same
  latency step. The interfaces lens found no dependency or contract anomaly and handed
  the class to infra-process. The software-defect lens found no exception and showed
  that the same input is fast before the marker and slow after it.
- **Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete.
- **Judge.** H1 validated, H2 invalidated, H3 invalidated. The judge set two wording
  limits on H1 (observed requests only; no delay size beyond the observed range) and
  named the untested off period. One round; budget not exhausted.

## Hypotheses

### H1 — chaos switch adds latency (infra-process) — validated

The marker (E4, E5) sits 3.3 s before the first slow request (E6). Every prediction
holds: fast before (E1, E2, E3), slow after on `/products`, `/products/{id}`,
`POST /orders` and `GET /orders` (E6, E7, E8, E9, E15), no error status and no
exception (E12), health unaffected (E10), gauge at 1 (E11). Against: the delay is not
a fixed 1500 ms (E16 shows 143.733 ms); this refutes only a fixed delay, not the
switch.

### H2 — code slow for specific inputs (software-defect) — invalidated

The same input `/products/1` took 1.031 ms before the marker (E2), 1320.647 ms after
it (E7) and 143.733 ms later (E16). Slowness follows time, not input. Other inputs
slowed at the same moment (E6, E8, E9).

### H3 — demand exceeds capacity (load-saturation) — invalidated

The counters hold 26 requests in about 127 s, part of them investigator probes (E12,
E13). The health route took 0.532 ms during the slow period (E10). Peak memory did not
move and the process did not restart (E13, E14). The quoted slow requests do not
overlap in time (E6, E7, E8), so no queue existed among them.

## Safe next steps

- Read the switch state on the operator side and find who owns the request at 18:28:17.427Z from 127.0.0.1:54875.
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` event.
- After the gauge reads 0, read the duration of the next shop requests in the log; a return to about 1 ms closes the untested off period.

## Gaps

- **No off period observed.** The off state has three samples, all in the three seconds before the marker.
- **Actor unknown.** The enable request has a local client and an unstamped request id; the surface shows no more.
- **Delay mapping unknown.** The setting is 1500 ms; observed delays are 128 to 1321 ms. The surface does not show how the target applies the setting.
- **Short history.** The process was 41 s old at the first probe; there are no rotated log backups.
- **Partial route coverage.** `/orders/{id}` and `/openapi.json` were not probed; 6 of 15 counted shop requests are not quoted.
- **No CPU, thread or queue metrics.** Load saturation was excluded from volume, health latency and memory.
- **No machine validation.** The journal was not run through the schema in this session.
