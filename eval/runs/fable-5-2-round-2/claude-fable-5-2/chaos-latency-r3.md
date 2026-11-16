---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-pages-slow
  trigger: 'manual (/konan, human profile). Complaint object: {"source": "human", "fingerprint": "human-1794767633", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."}, "startsAt": "2026-11-15T18:33:53Z"}. Investigation start 2026-11-15T18:34:01Z; trigger latency 8 s. No severity stated by the reporter.'
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-15T18:34:01Z
  concluded: 2026-11-15T18:38:11Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The target's internal chaos switch was turned on at 2026-11-15T18:33:36.767Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on it adds a variable delay of up to about 1.5 s to every shop request, with no errors, and leaves /health and /metrics undelayed."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode), turned on with extra_latency_ms 1500 and failure_rate 0.0, adds a variable delay to shop requests while it is on; /health and /metrics are not delayed."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E26]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code makes specific routes or specific inputs slow (a data-dependent slow path)."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8]
    evidence_against: [E4, E5, E9, E11, E18, E19, E20, E21]
  - id: H3
    statement: "A process lifecycle event or resource exhaustion (a restart, a cold start, memory growth) degraded the process."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E22]
    evidence_against: [E4, E5, E6, E23, E24, E25]
  - id: H4
    statement: "Demand exceeds the capacity of the process, so requests queue behind each other."
    incident_class: load-saturation
    state: invalidated
    evidence_for: [E12]
    evidence_against: [E13, E14, E15, E16, E24]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:36.767Z"
    quote: '{"ts": "2026-11-15T18:33:36.767Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "a581eedc339a", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:36.768Z"
    quote: '{"ts": "2026-11-15T18:33:36.768Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "a581eedc339a", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.756, "client": "127.0.0.1:54941"}'
  - id: E3
    type: metric
    source: "/metrics, request_id=konan-1794767736-16957 (logged at 2026-11-15T18:35:36.833Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:31.590Z"
    quote: '{"ts": "2026-11-15T18:33:31.590Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "5f194cea08dc", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.119, "client": "127.0.0.1:54938"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:32.647Z"
    quote: '{"ts": "2026-11-15T18:33:32.647Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "5bef00a48d52", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.0, "client": "127.0.0.1:54939"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:33.707Z"
    quote: '{"ts": "2026-11-15T18:33:33.707Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "29a3b2937e9c", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.927, "client": "127.0.0.1:54940"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:39.830Z"
    quote: '{"ts": "2026-11-15T18:33:39.830Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "1b3fe07ee1bd", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1002.892, "client": "127.0.0.1:54942"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:42.135Z"
    quote: '{"ts": "2026-11-15T18:33:42.135Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "d1d700930cb1", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1238.776, "client": "127.0.0.1:54943"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:43.212Z"
    quote: '{"ts": "2026-11-15T18:33:43.212Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "b085c6370630", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 9.65, "client": "127.0.0.1:54944"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:44.447Z"
    quote: '{"ts": "2026-11-15T18:33:44.447Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "19c7cfe7aaaa", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 179.895, "client": "127.0.0.1:54945"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:45.943Z"
    quote: '{"ts": "2026-11-15T18:33:45.943Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "ca3126f2d000", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 427.602, "client": "127.0.0.1:54946"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:48.328Z"
    quote: '{"ts": "2026-11-15T18:33:48.328Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "766145483e57", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1320.333, "client": "127.0.0.1:54947"}'
  - id: E13
    type: probe
    source: "/products, request_id=konan-1794767737-16962 (logged at 2026-11-15T18:35:37.853Z, duration_ms 461.239)"
    quote: "-- HTTP 200 in 0.463410s request_id=konan-1794767737-16962"
  - id: E14
    type: probe
    source: "/health, request_id=konan-1794767737-16967 (logged at 2026-11-15T18:35:37.938Z)"
    quote: |-
      {"status":"ok","uptime_seconds":127.11844733403996}
      -- HTTP 200 in 0.001339s request_id=konan-1794767737-16967
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:35:07.343Z"
    quote: '{"ts": "2026-11-15T18:35:07.343Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794767707-16919", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.828, "client": "127.0.0.1:54981"}'
  - id: E16
    type: metric
    source: "/metrics, request_id=konan-1794767736-16957 (logged at 2026-11-15T18:35:36.833Z); the complete http_requests_total block and the complete http_exceptions_total block, which has no series line"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 5
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E17
    type: log
    source: "lab/logs/app.log, whole file (39 lines, no rotated backups) read at 2026-11-15T18:35:38Z: exactly one switch event line, and no line with the event chaos_disabled"
    quote: '"message": "chaos mode enabled", "request_id": "a581eedc339a", "event": "chaos_enabled"'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:35:15.498Z"
    quote: '{"ts": "2026-11-15T18:35:15.498Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794767714-16930", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1207.692, "client": "127.0.0.1:54984"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:35:16.041Z"
    quote: '{"ts": "2026-11-15T18:35:16.041Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794767715-16934", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 505.924, "client": "127.0.0.1:54985"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:35:16.147Z"
    quote: '{"ts": "2026-11-15T18:35:16.147Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794767716-16938", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 73.053, "client": "127.0.0.1:54986"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:35:16.686Z"
    quote: '{"ts": "2026-11-15T18:35:16.686Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794767716-16942", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 523.392, "client": "127.0.0.1:54987"}'
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:33:30.834Z"
    quote: '{"ts": "2026-11-15T18:33:30.834Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E23
    type: metric
    source: "/metrics, request_id=konan-1794767648-16836 (logged at 2026-11-15T18:34:08.201Z)"
    quote: |-
      process_uptime_seconds 37.378402959089726
      process_max_rss_bytes 47251456
  - id: E24
    type: metric
    source: "/metrics, request_id=konan-1794767736-16957 (logged at 2026-11-15T18:35:36.833Z)"
    quote: |-
      process_uptime_seconds 126.01343262474984
      process_max_rss_bytes 47251456
  - id: E25
    type: probe
    source: "/health, request_id=konan-1794767647-16831 (logged at 2026-11-15T18:34:07.711Z)"
    quote: |-
      {"status":"ok","uptime_seconds":36.88863025000319}
      -- HTTP 200 in 0.003169s request_id=konan-1794767647-16831
  - id: E26
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:35:36.833Z"
    quote: '{"ts": "2026-11-15T18:35:36.833Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1794767736-16957", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.646, "client": "127.0.0.1:54988"}'
gaps:
  - "Who or what turned the switch on is not visible: the log records only the client 127.0.0.1:54941 and the request id a581eedc339a (E2). The switch endpoints are operator surface, outside the investigator's contract, and were not touched."
  - "No telemetry exists before the process start at 2026-11-15T18:33:30.834Z (one log file, no rotated backups). The complaint says 'the last few minutes'; telemetry shows the onset 17 s before the complaint, and cannot show whether an earlier process was also slow."
  - "The pre-switch baseline is small: three shop requests in about 2 s (E4, E5, E6). Peak memory was first scraped after the onset, so memory growth before 18:34:08Z is excluded only by the fast health requests."
  - "User impact is measured on six non-investigator requests after the switch (E7 to E12); the later slow requests are investigator probes. The share of real users affected is not measurable from this surface."
  - "The switch state was last read at 2026-11-15T18:35:36Z (E3). Whether it is still on after the conclusion was not checked."
  - "No load-saturation lens file exists; H4 was tested by the orchestrator from request counts and health latency, not by a dedicated lens."
usage:
  model: claude-fable-5-2
  tokens: 1178214
  wall_clock_seconds: 250
---

# Shop pages slow: the target's chaos switch adds latency to every shop request

## Summary

**Verdict: root cause identified** (class `infra-process`, cause `degradation-switch`).
At 2026-11-15T18:33:36.767Z the target's internal chaos switch was turned on with
`extra_latency_ms: 1500` and `failure_rate: 0.0` (E1, E2). From the next request on,
shop requests (`/products`, `/products/{id}`, `/orders`, `POST /orders`) take a variable
time of up to about 1.4 s, against about 1 to 2 ms before the switch (E4 to E12). No
request fails: all statuses are 200 or 201 and no exception is counted (E16), which
matches `failure_rate: 0.0`. `/health` and `/metrics` stay near 1 ms (E14, E15, E26),
which is why health checks are green and fast. The switch was still on at the last
scrape, 18:35:36Z (E3), and the log holds no disable event (E17), so the slowness was
ongoing at the conclusion.

Impact on users: of the six non-investigator requests after the switch, five were
delayed by 180 ms to 1320 ms and one took 9.65 ms (E7 to E12). Confidence is high: the
onset is sharp, the configured value bounds every observed duration, and the judge
validated the hypothesis and invalidated the three alternatives.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 18:33:30.834 | Process startup, the only one in the log | E22 |
| 18:33:31.590 – 18:33:33.707 | Shop requests take 1.0 to 1.9 ms | E4, E5, E6 |
| 18:33:36.767 | **Switch marker:** `chaos_enabled`, `extra_latency_ms` 1500, `failure_rate` 0.0, through `POST /chaos/enable` from 127.0.0.1:54941 | E1, E2 |
| 18:33:39.830 | First slow request: `GET /products`, 1002.892 ms, status 200 | E7 |
| 18:33:42.135 – 18:33:48.328 | User requests take 9.65 to 1320.333 ms, all 200/201 | E8 – E12 |
| 18:33:53 | Complaint raised (`startsAt`) | — |
| 18:34:01 | Investigation start (trigger latency 8 s) | — |
| 18:34:07 – 18:34:08 | Baseline: health 200 in 3 ms; uptime 37 s; switch gauge 1 | E25, E23 |
| 18:35:07.343 | Health 0.828 ms between two slow shop probes | E15 |
| 18:35:15 – 18:35:16 | Same input, different durations: `/products/1` 1207.692 ms then 505.924 ms; `/products/2` 73.053 ms then 523.392 ms | E18 – E21 |
| 18:35:36 – 18:35:37 | Switch gauge still 1; `/products` 463 ms; `/health` 1.3 ms; `/metrics` 0.646 ms | E3, E13, E14, E26 |

## Investigation

- **Trigger.** Manual, `/konan`. The complaint object is in the machine core
  (`investigation.trigger`), recorded verbatim with the investigation start.
- **Baseline.** `/health` 200 in 3 ms with uptime 36.9 s (E25). `/metrics`: only 200 and
  201 statuses, no exception series, switch gauge 1, uptime 37.4 s, peak memory
  47251456 bytes (E23). Log tail: one startup, one WARNING line (E1), fast access lines
  before it and slow ones after it.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. All three reported the same switch marker and the sharp
  onset after it. The software-defect lens found no exception and no per-input
  pattern. The infra-process lens found no restart and no memory growth. The lenses
  ran 14 read-only probes in total.
- **Deep-dive.** Skipped. The triage evidence for H1 was already deterministic and
  complete: a quoted change marker, a before/after latency contrast, a live gauge, and
  live probes. Per the skill, such a hypothesis goes straight to the judge.
- **Judge.** One fresh agent with the hypothesis list and verbatim evidence only.
  Verdicts: H1 validated; H2, H3, H4 invalidated. The judge marked one clause of H1
  ("`/metrics` is not delayed") as uncited; the log line of the scrape (E26, 0.646 ms)
  closes it.
- **Budget used.** One triage round, no deep-dive agent, one judge round.

## Hypotheses

### H1 — chaos switch adds latency to shop requests (validated)

The marker E1 carries the mechanism in its own fields: `extra_latency_ms: 1500`,
`failure_rate: 0.0`. Each arm of the prediction holds. Before the marker, shop requests
take 1.0 to 1.9 ms (E4, E5, E6). The first request after it takes 1002.892 ms (E7), and
later ones vary from 9.65 ms to 1320.333 ms (E8 to E12), none above 1500 ms. No error
status and no exception exist (E16). Health and metrics stay near 1 ms (E14, E15, E26).
The gauge reads 1 (E3) and no disable event exists (E17). A live probe confirms the
slowness continues (E13). Per the report contract, an internal degradation switch is
`infra-process` / `degradation-switch`, even though the symptom is latency.

### H2 — data-dependent slow path in the target's code (invalidated)

The slow requests E7 and E8 fit H1 equally and do not favour H2. The same input gives
different durations: `/products/1` took 1.0 ms (E5), 9.65 ms (E9), 1207.692 ms (E18) and
505.924 ms (E19); `/products/2` took 1238.776 ms (E8), 73.053 ms (E20) and 523.392 ms
(E21); `/products` took 1.119 ms (E4), 1002.892 ms (E7) and 427.602 ms (E11). The
slowness depends on the switch event, not on the input.

### H3 — restart, cold start, or memory growth (invalidated)

One startup exists (E22), about 6 s before the switch. Requests right after startup were
fast (E4, E5, E6), the opposite of a cold-start prediction. Uptime rises without a
reset from 36.9 s to 126.0 s (E25, E23, E24), and peak memory is identical at both
scrapes (E23, E24). The judge noted that both scrapes are after the onset; see Gaps.

### H4 — load saturation (invalidated)

The request block sums to 28 requests in 126 s of uptime, more than half of them
investigator probes (E16, E24). Health answers in about 1 ms between and right after
slow shop requests (E14, E15). The client time of a slow probe (463.4 ms, E13) equals
its server duration (461.239 ms), so no queue wait exists. E12 fits H1 equally.

## Safe next steps

Read-only only:

- Find the origin of the request `a581eedc339a` (`POST /chaos/enable` at
  18:33:36.768Z, client 127.0.0.1:54941) in operator records: who or what sent it, and
  whether it was planned.
- Keep reading the gauge `faultline_chaos_enabled` on `/metrics` and the log for an
  event `chaos_disabled`; the incident ends when the gauge reads 0.
- After the gauge reads 0, compare `duration_ms` of shop requests with the pre-switch
  values (about 1 to 2 ms) to confirm that nothing else adds latency.
- Count the non-investigator shop requests between the marker and the disable event
  to size the user impact.

## Gaps

- **Origin of the switch.** The log shows the client address and request id only (E2).
  The switch endpoints are operator surface and outside the investigator's contract.
- **No history before 18:33:30.834Z.** One log file, no backups, one process. The
  complaint's "last few minutes" cannot be checked against an earlier process; the
  telemetry onset is 17 s before the complaint.
- **Small baseline.** Three pre-switch shop requests. Peak memory before the onset was
  not scraped; the fast health requests are the only argument against early memory
  pressure.
- **User impact sample.** Six non-investigator requests after the switch; the rest of
  the slow requests are investigator probes (`konan-` request ids).
- **Current state.** The gauge was last read at 18:35:36Z.
- **No load-saturation lens.** H4 was tested by the orchestrator, not by a lens.
