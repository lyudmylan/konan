---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-slow-latency-switch
  trigger: "manual (/konan, human profile); complaint object: source=human, fingerprint=human-1794774663, labels.alertname=human-report, no severity stated, startsAt=2026-11-15T20:31:03Z; investigation start 2026-11-15T20:31:15Z; trigger latency 12 s"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-15T20:31:15Z
  concluded: 2026-11-15T20:52:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A chaos switch inside the target was turned on at 20:30:49.566Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on it adds a variable delay below 1500 ms to the shop GET routes, and /health is not delayed."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was turned on at 20:30:49.566Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on it adds a variable delay of up to 1500 ms to the shop GET routes (/products, /products/{id}, /orders), /health is not affected, and this is the cause of the reported slowness."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8, E9, E10, E11, E12, E13, E19, E20]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code makes requests slow or fail for specific inputs."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E6, E9, E4, E10, E14, E15]
  - id: H3
    statement: "Demand exceeds the capacity of the target, and requests queue."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E13, E7, E12]
  - id: H4
    statement: "The process crashed or restarted shortly before the slowness, and the error page that some users saw once came from that outage window."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E16, E12]
    evidence_against: [E14]
  - id: H5
    statement: "The chaos switch of E1 also injected the error page that some users saw once."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:49.566Z"
    quote: '{"ts": "2026-11-15T20:30:49.566Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "3ea8b6053e0b", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:44.402Z"
    quote: '{"ts": "2026-11-15T20:30:44.402Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "8f8abbd8db0e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.924, "client": "127.0.0.1:56415"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:45.455Z"
    quote: '{"ts": "2026-11-15T20:30:45.455Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "dfa7ff0e876b", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.028, "client": "127.0.0.1:56416"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:52.342Z"
    quote: '{"ts": "2026-11-15T20:30:52.342Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "7c9a43a77cda", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 723.869, "client": "127.0.0.1:56419"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:53.684Z"
    quote: '{"ts": "2026-11-15T20:30:53.684Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "c98b862953dd", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 281.657, "client": "127.0.0.1:56420"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:55.348Z"
    quote: '{"ts": "2026-11-15T20:30:55.348Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c67d3d2bb9e3", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 605.714, "client": "127.0.0.1:56421"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:56.410Z"
    quote: '{"ts": "2026-11-15T20:30:56.410Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "9000b31ce54b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 6.203, "client": "127.0.0.1:56423"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:58.361Z"
    quote: '{"ts": "2026-11-15T20:30:58.361Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "95d5e4afa6a6", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 898.93, "client": "127.0.0.1:56424"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:32:11.880Z"
    quote: '{"ts": "2026-11-15T20:32:11.880Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794774730-24576", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1145.713, "client": "127.0.0.1:56453"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:31:57.143Z"
    quote: '{"ts": "2026-11-15T20:31:57.143Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794774716-24488", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 154.191, "client": "127.0.0.1:56449"}'
  - id: E11
    type: metric
    source: "/metrics @ request_id=konan-1794774764-24602 (2026-11-15T20:32:44Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: probe
    source: "/health @ request_id=konan-1794774680-24438"
    quote: |-
      {"status":"ok","uptime_seconds":36.482413958292454}
      -- HTTP 200 in 0.001995s request_id=konan-1794774680-24438
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:31:57.477Z"
    quote: '{"ts": "2026-11-15T20:31:57.477Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794774717-24493", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.444, "client": "127.0.0.1:56450"}'
  - id: E14
    type: metric
    source: "/metrics @ request_id=konan-1794774764-24602 (2026-11-15T20:32:44Z), the complete http_requests_total family"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E15
    type: metric
    source: "/metrics @ request_id=konan-1794774764-24602 (2026-11-15T20:32:44Z), the complete http_exceptions_total family; no series lines follow"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:43.633Z"
    quote: '{"ts": "2026-11-15T20:30:43.633Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E17
    type: metric
    source: "/metrics @ request_id=konan-1794774764-24602 (2026-11-15T20:32:44Z)"
    quote: |-
      process_uptime_seconds 120.55940070841461
      process_max_rss_bytes 47939584
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:46.509Z"
    quote: '{"ts": "2026-11-15T20:30:46.509Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "054a70675180", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.957, "client": "127.0.0.1:56417"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:32:12.528Z"
    quote: '{"ts": "2026-11-15T20:32:12.528Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794774731-24582", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 561.891, "client": "127.0.0.1:56454"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:30:49.566Z"
    quote: '{"ts": "2026-11-15T20:30:49.566Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "3ea8b6053e0b", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.791, "client": "127.0.0.1:56418"}'
gaps:
  - "The error page that some users saw once has no trace in the telemetry of this process: no non-2xx series, no exception series, no chaos_failure line. It stays unexplained and is not attributed to any hypothesis."
  - "Nothing before the process start at 20:30:43.633Z is readable: the log has no rotated backups and the counters start with the process. The complaint says 'the last few minutes'; the telemetry covers 20 s before the complaint."
  - "Whether the start at 20:30:43.633Z was a restart after a crash or a first start is unknown (H4). The record that would settle it, a client-side or proxy-side record of the error page with its time, or a supervisor record, is outside the surface contract."
  - "Who turned the switch on, and why, is not readable: the access line shows the client 127.0.0.1:56418 only, and the chaos surface is operator surface, out of bounds for the investigator."
  - "The scope of the delay on write routes rests on one sample: one POST /orders after the switch took 6.203 ms (E7). GET /orders has no sample before the switch."
  - "The sample is small: four slow user requests and three slow investigator probes after the switch."
  - "Only three lens files exist (infra-process, interfaces, software-defect). Load saturation was checked by the orchestrator from the metrics alone (H3); the lab has no database and no third-party dependency."
  - "No deep-dive round ran: the triage evidence for H1 was deterministic, and the evidence that would settle H4 is out of reach."
  - "usage.tokens is null: the session could not capture the orchestrator totals. The four subagents reported 148737 tokens together."
usage:
  model: claude-fable-5-2
  tokens: 1394784
  wall_clock_seconds: 1286
---

# Shop GET routes slow: a latency-injection switch inside the target is on

## Summary

**Root cause identified, for the slowness.** A chaos switch inside the target was
turned on at 20:30:49.566Z with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E1,
E20). From the first shop request after that marker, GET `/products`,
`/products/{id}` and `/orders` take 154 ms to 1146 ms (E4, E5, E6, E8, E9, E10, E19);
the same routes took about 1 ms before it (E2, E3). Every observed delay is below the
configured 1500 ms. The switch was still on at 20:32:44Z (E11). `/health` answers in
under 1 ms throughout (E12, E13), which is why the health checks stay green and fast.
Class `infra-process`, cause `degradation-switch`. Confidence: high for the mechanism;
the sample is small (four user requests, three investigator probes).

**User impact** (non-investigator traffic only): four shop GET requests between
20:30:52Z and 20:30:58Z took 282 ms to 899 ms (E4, E5, E6, E8). No user request
failed: every status of the process life is 200 or 201 (E14).

**The error page is not explained.** The telemetry of this process holds no error of
any kind (E14, E15), and the switch has `failure_rate: 0.0` (E1). The process started
only 20 s before the complaint (E16); anything earlier is not readable. See Gaps.

## Timeline

All times UTC, 2026-11-15.

- 20:30:43.633Z — process start, `faultline 0.1.0 started` (E16). No earlier telemetry exists.
- 20:30:44–20:30:46Z — shop requests are fast: GET `/products` 0.924 ms (E2), GET `/products/1` 1.028 ms (E3), POST `/orders` 1.957 ms (E18).
- 20:30:49.566Z — **switch marker**: `chaos mode enabled`, `failure_rate 0.0`, `error_status 503`, `extra_latency_ms 1500` (E1), through `POST /chaos/enable -> 200` with the same request id (E20).
- 20:30:52.342Z — first slow request, 2.8 s after the marker: GET `/products` 723.869 ms (E4).
- 20:30:53–20:30:58Z — GET `/products/2` 281.657 ms (E5), GET `/products/1` 605.714 ms (E6), POST `/orders` 6.203 ms (E7), GET `/orders` 898.93 ms (E8).
- 20:31:03Z — complaint raised (`startsAt`).
- 20:31:15Z — investigation start (trigger latency 12 s).
- 20:31:20Z — `/health` probe: 200 in 0.001995s, uptime 36.48 s (E12).
- 20:31:57–20:32:12Z — investigator probes are still slow: GET `/products` 154.191 ms (E10), GET `/products/1` 1145.713 ms (E9), GET `/orders` 561.891 ms (E19); `/health` 0.444 ms (E13).
- 20:32:44Z — `faultline_chaos_enabled 1` (E11); uptime 120.56 s, no reset (E17); no error series (E14, E15).

## Investigation

**Complaint object** (verbatim, from the `/konan` adapter):

```json
{
  "source": "human",
  "fingerprint": "human-1794774663",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-15T20:31:03Z"
}
```

Investigation start: 2026-11-15T20:31:15Z. `KONAN_ADAPTER` was unset, so the surface
contract is `docs/lab.md`.

**Baseline.** `/health` 200 in 2 ms (E12). `/metrics`: switch gauge 1, no exception
series, no non-2xx series. Log: one startup marker (E16), one WARNING line (E1), slow
shop GETs after it.

**Triage.** Three lenses in parallel, each blind to the others: infra-process,
software-defect, interfaces. All three reported the switch marker and the sharp onset
after it. The software-defect lens reported no anomaly in its domain. The interfaces
lens reported no contract violation and classed the switch as `infra-process`. No lens
found a trace of the error page.

**Deep-dive.** None. The triage evidence for H1 was deterministic and complete, and the
lens probes had already confirmed its prediction (E9, E10, E19). The evidence that
would settle H4 is outside the surface.

**Judge** (fresh agent, evidence only): H1 validated, H2 invalidated, H3 invalidated,
H4 inconclusive, H5 invalidated. The judge noted two limits on H1: the GET-only scope
rests on one POST sample (E7), and GET `/orders` has no sample before the marker. The
judge also ruled that E7 is not evidence against H1, and that the error page must not
be attributed to H4 by elimination.

## Hypotheses

### H1 — latency-injection switch is on (infra-process) — validated

The marker (E1, E20) sits between the last fast request (E3, 4.1 s before) and the
first slow one (E4, 2.8 s after). The same input `/products/1` took 1.028 ms before
(E3) and 605.714 ms and 1145.713 ms after (E6, E9). All seven slow samples stay below
the configured 1500 ms. The gauge still reads on (E11). `/health` is not delayed (E12,
E13). User requests were slow before the first investigator probe, so the probes are
not the cause. One POST `/orders` after the marker took 6.203 ms (E7): the delay did
not apply to that request, and one sample cannot say whether that is a rule.

### H2 — code defect bound to an input (software-defect) — invalidated

No exception series (E15) and no 5xx series (E14) for the life of the process. The
slowness is not bound to an input: the same input is fast before the marker and slow
after it (E3, E6, E9), and the same route varies between calls (E4, E10).

### H3 — demand exceeds capacity (load-saturation) — invalidated

20 requests in about 120 s of uptime (E14). `/health` took 0.444 ms during the slow
period (E13) and a POST took 6 ms (E7); queueing would slow every route.

### H4 — crash or restart caused the error page (infra-process) — inconclusive

The process started at 20:30:43.633Z (E16, E12), inside the "last few minutes" of the
complaint. A start is not proof of a restart: a log with no earlier lines fits a first
start equally well. No error exists after the start (E14). The window before the start
cannot be read.

### H5 — the switch injected the error page (infra-process) — invalidated

The switch line sets `failure_rate` to 0.0 (E1); the 503 is a configured status, not
an occurrence. One enable call only, and no 503 series (E14).

## Safe next steps

- Ask the owner of the chaos switch whether the enable call at 20:30:49.566Z (request id `3ea8b6053e0b`) was intended.
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` event; then compare the durations of the shop GET routes with the 1 ms level of E2 and E3.
- Get the client-side or proxy-side record of the error page with its time. Before 20:30:43.633Z supports H4; after it refutes H4.
- Read the supervisor or deploy record for a process start at 20:30:43.633Z, to learn whether it was a restart.

## Gaps

- **The error page.** No trace in this process: no non-2xx series, no exception series, no `chaos_failure` line. Unexplained, and not attributed.
- **Before the start.** No rotated logs; counters start with the process. The telemetry covers 20 s before the complaint, not "the last few minutes".
- **Restart or first start.** Unknown; the record that settles it is outside the surface contract.
- **Who turned the switch on.** The access line shows a local client only; the chaos surface is out of bounds for the investigator.
- **Scope on write routes.** One POST sample after the switch; no GET `/orders` sample before it.
- **Sample size.** Four slow user requests, three slow investigator probes.
- **Lens coverage.** Three lens files exist; load saturation was checked from metrics by the orchestrator. The lab has no database and no third party.
- **No deep-dive round.** By design here; see Investigation.
- **Token usage.** Not captured for the orchestrator; the four subagents used 148737 tokens together.
