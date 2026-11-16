---
konan_journal: 2
investigation:
  id: 2026-11-15-occasional-shop-503s
  trigger: 'manual — /konan human profile. Complaint object: {"source": "human", "fingerprint": "human-1794755092", "labels": {"alertname": "human-report"}, "annotations": {"summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"}, "startsAt": "2026-11-15T15:04:52Z"}. Investigation start 2026-11-15T15:05:09Z; trigger latency 17 s. No severity stated by the reporter.'
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-15T15:05:09Z
  concluded: 2026-11-15T15:08:59Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos switch inside the target was turned on at 2026-11-15T15:04:45.224Z with failure_rate 0.08 and error_status 503; while it is on, the target injects 503 responses on a fraction of requests independent of input, and it was still on at 15:06:45Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target, turned on at 15:04:45.224Z with failure_rate 0.08 and error_status 503, injects 503 responses on a fraction of requests independent of input; it is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E10, E11, E12, E13, E14, E18]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled error for specific product inputs (a data-dependent failure on /products/1 or /products/2)."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E4, E6]
    evidence_against: [E3, E5, E9, E11, E12, E13, E14]
  - id: H3
    statement: "The process crashes or restarts in a loop, and requests fail around the restarts."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E10, E16, E17, E19]
  - id: H4
    statement: "A gateway or upstream tier in front of the target fails on its own and returns 503 without the target's involvement."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E4, E6]
    evidence_against: [E1, E3, E5]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:45.224Z"
    quote: '{"ts": "2026-11-15T15:04:45.224Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "1d23dc936241", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:45.225Z"
    quote: '{"ts": "2026-11-15T15:04:45.225Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "1d23dc936241", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 1.338, "client": "127.0.0.1:53370"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:46.677Z"
    quote: '{"ts": "2026-11-15T15:04:46.677Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "d32b2ac5f489", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:46.677Z"
    quote: '{"ts": "2026-11-15T15:04:46.677Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "d32b2ac5f489", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.148, "client": "127.0.0.1:53397"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:46.748Z"
    quote: '{"ts": "2026-11-15T15:04:46.748Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "59670d85387d", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:46.748Z"
    quote: '{"ts": "2026-11-15T15:04:46.748Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "59670d85387d", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.144, "client": "127.0.0.1:53402"}'
  - id: E7
    type: metric
    source: "/metrics, scrape request_id=konan-1794755110-3828 (2026-11-15T15:05:10Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E8
    type: metric
    source: "/metrics, scrape request_id=konan-1794755205-3923 (2026-11-15T15:06:45Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E9
    type: metric
    source: "/metrics, scrape request_id=konan-1794755205-3923; the same three consecutive lines in scrape konan-1794755110-3828 (no http_exceptions_total series in either)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E10
    type: metric
    source: "/metrics, scrape request_id=konan-1794755205-3923; the two 503 lines carry the same values in scrape konan-1794755110-3828 and are the only non-2xx series in both scrapes"
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 17
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:46.663Z"
    quote: '{"ts": "2026-11-15T15:04:46.663Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "9fda053adbf0", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.411, "client": "127.0.0.1:53396"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:46.590Z"
    quote: '{"ts": "2026-11-15T15:04:46.590Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "d7eade3ca830", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.445, "client": "127.0.0.1:53391"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:06:08.733Z (investigator probe)"
    quote: '{"ts": "2026-11-15T15:06:08.733Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794755168-3898", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.555, "client": "127.0.0.1:53431"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:06:09.347Z (investigator probe)"
    quote: '{"ts": "2026-11-15T15:06:09.347Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794755169-3903", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.462, "client": "127.0.0.1:53432"}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:40.303Z (the only startup event in the file; no rotated backups exist)"
    quote: '{"ts": "2026-11-15T15:04:40.303Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E16
    type: metric
    source: "/metrics, scrape request_id=konan-1794755110-3828 (15:05:10Z), then scrape request_id=konan-1794755205-3923 (15:06:45Z)"
    quote: |-
      process_uptime_seconds 30.01238283328712
      process_uptime_seconds 125.01562787499279
  - id: E17
    type: probe
    source: "/health request_id=konan-1794755109-3823"
    quote: |-
      {"status":"ok","uptime_seconds":29.52842600038275}
      -- HTTP 200 in 0.002067s request_id=konan-1794755109-3823
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T15:04:43.171Z (the last access line before E1; the 5 access lines before E1 all carry status 200 or 201)"
    quote: '{"ts": "2026-11-15T15:04:43.171Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "ed36beaef7e5", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.969, "client": "127.0.0.1:53369"}'
  - id: E19
    type: metric
    source: "/metrics, scrapes request_id=konan-1794755110-3828 and request_id=konan-1794755205-3923 (same value in both)"
    quote: "process_max_rss_bytes 47005696"
gaps:
  - "Nothing before 2026-11-15T15:04:40.302Z is visible: the process started 29 s before the first probe and lab/logs holds no rotated backups. The complaint says 'the last few minutes'; errors before that start, and an earlier process instance, cannot be confirmed or excluded from this surface."
  - "Who turned the switch on, and why, is not visible: the telemetry shows one unstamped POST /chaos/enable from 127.0.0.1 (E2). The chaos state endpoint is operator surface, outside the investigator's contract, so the switch state is read from the gauge and the log only."
  - "The sample is small: 32 non-investigator requests in about 0.5 s after the switch, 2 failed. The 0.08 rate comes from the configuration line (E1) only; the observed 2 of 32 fits it and does not measure it."
  - "No non-investigator traffic exists after 15:04:46.748Z, so present user impact is not observed. 'Still on' holds as of the last scrape, 15:06:45Z."
  - "All evidence is target-side. A failure that never reached the target (client side, network path) would not appear in this ledger."
  - "Why the process started at 15:04:40 is unknown: no supervisor record is on the surface."
  - "Lenses run: infra-process, interfaces, software-defect. No lens exists for load-saturation, third-party or data-db; the infra-process lens read the resource gauges and durations (flat), and the lab contract states the target has no database and no third-party dependency."
  - "Token usage was not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1235323
  wall_clock_seconds: 230
---

# Occasional 503 responses in the shop — an error-injection switch is on

## Summary

**Root cause identified, not "nothing".** An operational chaos switch inside the target
was turned on at 15:04:45.224Z (UTC) with `failure_rate` 0.08 and `error_status` 503
(E1, E2). While it is on, the target itself rejects a fraction of requests with 503,
independent of the input. Both errors in the telemetry are such injected failures: each
503 access line has a `chaos_failure` line with the same request id (E3/E4, E5/E6), and
they are the only non-2xx responses the target ever counted (E10). The switch was still
on at the last scrape, 15:06:45Z (E8), so the errors continue for as long as traffic
arrives.

Impact: 2 of 32 non-investigator requests after the switch failed (6.25 %), both on
product pages; the same pages answered 200 milliseconds before (E11, E12) and later
(E13, E14). That matches "works on retry, most people notice nothing". The process is
healthy otherwise: one startup, uptime without a reset, no unhandled exception, flat
memory, sub-2 ms durations (E9, E15–E17, E19).

Confidence: high for the two recorded failures and for the mechanism. Open: the
telemetry starts at 15:04:40Z, so the part of "the last few minutes" before that is
not covered (Gaps).

Class `infra-process`, cause `degradation-switch`: an internal operational switch, not a
defect in the code path and not a gateway tier.

## Timeline

All times UTC, 2026-11-15.

- 15:04:40.303 — the process starts; the only startup event in the log (E15).
- 15:04:41.031 – 15:04:43.171 — 5 requests, all 200/201 (E18 is the last of them).
- 15:04:45.224 — **switch marker**: `chaos mode enabled`, failure_rate 0.08,
  error_status 503, extra_latency_ms 0 (E1), by `POST /chaos/enable -> 200` from
  127.0.0.1 (E2).
- 15:04:46.590, 15:04:46.663 — `/products/2` and `/products/1` answer 200 (E12, E11).
- 15:04:46.677 — first failure: `chaos-injected failure`, `GET /products/2 -> 503`
  (E3, E4), 1.45 s after the marker.
- 15:04:46.748 — second failure: `GET /products/1 -> 503` (E5, E6). Last
  non-investigator request in the log.
- 15:04:52 — the complaint arrives (`startsAt`).
- 15:05:09 — investigation start; `/health` 200, uptime 29.5 s (E17).
- 15:05:10 — first metrics scrape: `faultline_chaos_enabled 1` (E7), two 503 series,
  no exception series (E9, E10).
- 15:06:08 – 15:06:09 — investigator probes of `/products/1` and `/products/2`: 200
  (E13, E14).
- 15:06:45 — second scrape: the gauge is still 1 (E8), uptime 125.0 s, no reset (E16),
  503 counters unchanged (E10).

## Investigation

- **Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.
  Complaint recorded verbatim; the reporter stated no severity.
- **Baseline.** `/health` 200; one metrics scrape; the full log (54 lines at that time,
  one file). The baseline already showed the gauge at 1 and two 503 series.
- **Triage, one round, three lenses in parallel, each blind to the others.**
  - infra-process: the switch is on and accounts for every error; no crash, restart
    loop, saturation or latency anomaly; the evidence window is shorter than the
    complaint's.
  - interfaces: the switch marker sits directly before the first failure; failures
    are per-request, not per-input; no boundary component is involved, so the class is
    `infra-process`.
  - software-defect: no exception evidence anywhere; the two failures are not
    data-dependent; both carry an injection marker.
- **Deep-dive: skipped.** The triage evidence for H1 was deterministic and complete
  (marker line, per-failure attribution by request id, gauge). The orchestrator re-read
  the log and took a second scrape to confirm the prediction (gauge still 1, counters
  unchanged, uptime continuous).
- **Judge, one fresh agent, hypotheses and verbatim evidence only.** H1 validated;
  H2, H3, H4 invalidated. The judge's notes on weak points are in Gaps.

## Hypotheses

### H1 — chaos switch injects 503 (infra-process, degradation-switch): validated

The target attributes both failures itself: E3 and E4 share request id
`d32b2ac5f489`, E5 and E6 share `59670d85387d`. E10 bounds the total: two non-2xx
series, count 1 each, in both scrapes — no 5xx is unexplained. E1 sets the status
(503) and the rate; E2 shows the request that turned the switch on. E7 and E8 show the
gauge at 1 across 95 s. No failure exists among the 5 requests before the marker
(E18). The same inputs succeed before (E11, E12) and after (E13, E14). The failed
requests took about 0.14 ms against 0.41–0.56 ms for successes, which fits a rejection
before the route handler ran (an inference, not a logged fact).

### H2 — data-dependent defect in the product code (software-defect): invalidated

Its only support is the two 503 lines (E4, E6), which E3 and E5 attribute to the
switch. `http_exceptions_total` has no series in either scrape (E9); the full log (61
lines at the last read) holds no `unhandled_exception` event. The same product ids
answer 200 before and after (E11–E14) — the opposite of a per-input failure. Limit: a
defect that no request in this window exercised would not show.

### H3 — crash or restart loop (infra-process): invalidated for 15:04:40Z – 15:06:45Z

One startup event, no rotated logs (E15). Uptime grew by 95.0 s over 95 s of clock
time (E16) and agrees with `/health` (E17). The 503 counters did not reset (E10);
peak memory is constant (E19, weak). A single startup 29 s before the first probe is
not a loop; why it happened is a gap.

### H4 — gateway or upstream tier fails on its own (interfaces): invalidated

The prediction was a 503 with no record inside the target. The target logged both
failures with its own injection marker (E3, E5) and the 503 status is the configured
one (E1). The surface shows no boundary component.

## Safe next steps

Read-only only.

- Ask the owner of the operational switches whether the `POST /chaos/enable` at
  15:04:45.224Z (request id `1d23dc936241`) was intended, and by whom.
- Keep reading `faultline_chaos_enabled` and the 503 series of `http_requests_total`;
  watch the log for a `chaos_disabled` event and for further `chaos_failure` lines.
- Compare the times of the user reports with 15:04:45Z. A report from before that
  time points to a second cause that this telemetry cannot show.
- Read the process supervisor's record for the start at 15:04:40Z (start count,
  previous exit status).

## Gaps

- **The window before 15:04:40.302Z.** The process started 29 s before the first
  probe and there are no rotated logs. "The last few minutes" in the complaint is
  longer than the visible window; earlier errors, and an earlier process instance,
  can be neither confirmed nor excluded.
- **Who and why.** One unstamped POST from 127.0.0.1 turned the switch on (E2). The
  chaos state endpoint is operator surface and outside the investigator's contract.
- **Small sample.** 32 non-investigator requests in about 0.5 s after the switch, 2
  failures. The 0.08 rate is the configured value, not a measured one.
- **Present impact not observed.** No non-investigator traffic after 15:04:46.748Z;
  "still on" holds as of 15:06:45Z.
- **Target-side evidence only.** A failure that never reached the target would not
  appear here.
- **The start at 15:04:40.** No supervisor record on the surface.
- **Lens coverage.** infra-process, interfaces, software-defect ran. No lens exists
  for load-saturation, third-party or data-db; resource gauges and durations were flat,
  and the lab contract states no database and no third-party dependency.
- **Tokens.** Not captured in this session.
