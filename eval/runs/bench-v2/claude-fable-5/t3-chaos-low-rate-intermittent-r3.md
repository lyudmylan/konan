---
konan_journal: 2
investigation:
  id: 2026-11-03-intermittent-shop-503s-chaos-switch
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-03T13:03:46Z
  concluded: 2026-11-03T13:08:56Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos switch was enabled on faultline at 2026-11-03T13:03:24Z with failure_rate 0.08 and error_status 503; while on, it injects HTTP 503 into ~8% of shop requests, so users see occasional errors that succeed on retry."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal operational chaos switch, enabled at 2026-11-03T13:03:24Z (failure_rate 0.08, error_status 503), injects HTTP 503 responses into roughly 8% of shop requests, causing occasional user-visible errors that succeed on retry."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E10, E11, E12]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code (an unhandled exception or a data-dependent failure) causes the intermittent errors users see."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E4, E8]
    evidence_against: [E9, E3, E6, E11, E5, E7]
  - id: H3
    statement: "An external dependency or a gateway tier in front of the target fails intermittently, producing the 503s."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E4, E8]
    evidence_against: [E1, E3, E6, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:24.236Z"
    quote: |-
      {"ts": "2026-11-03T13:03:24.236Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "2321f1b9cd48", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: metric
    source: "/metrics scrape, request_id=konan-1793711038-34916 @ 2026-11-03T13:03:58Z"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:25.434Z (unstamped user traffic)"
    quote: |-
      {"ts": "2026-11-03T13:03:25.434Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "edfb81e967f1", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:25.434Z (same request as E3)"
    quote: |-
      {"ts": "2026-11-03T13:03:25.434Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "edfb81e967f1", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.14, "client": "127.0.0.1:51033"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:25.523Z (same path ~90 ms after E4, unstamped user traffic)"
    quote: |-
      {"ts": "2026-11-03T13:03:25.523Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "3668a51afbc7", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.398, "client": "127.0.0.1:51039"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:25.538Z (unstamped user traffic)"
    quote: |-
      {"ts": "2026-11-03T13:03:25.538Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "8afc9a6b6600", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:25.627Z (same path ~89 ms after E6, unstamped user traffic)"
    quote: |-
      {"ts": "2026-11-03T13:03:25.627Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "a837cb97f7b7", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.575, "client": "127.0.0.1:51046"}
  - id: E8
    type: metric
    source: "/metrics scrape, request_id=konan-1793711038-34916 @ 2026-11-03T13:03:58Z (the only non-2xx series in http_requests_total at scrape time)"
    quote: |-
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
  - id: E9
    type: metric
    source: "/metrics scrape, request_id=konan-1793711038-34916 @ 2026-11-03T13:03:58Z (the complete http_exceptions_total section; zero series follow the headers)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E10
    type: probe
    source: "GET /products/1, burst of 30 sequential probes @ ~2026-11-03T13:05:53Z; 27 returned HTTP 200 and 3 returned HTTP 503; first 503 trailer, request_id=konan-1793711153-35014"
    quote: "-- HTTP 503 in 0.000969s request_id=konan-1793711153-35014"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:05:53.913Z (correlates the E10 probe id)"
    quote: |-
      {"ts": "2026-11-03T13:05:53.913Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793711153-35014", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
  - id: E12
    type: probe
    source: "GET /products/1, same burst as E10; the other two 503 trailers"
    quote: |-
      -- HTTP 503 in 0.000973s request_id=konan-1793711154-35041
      -- HTTP 503 in 0.000919s request_id=konan-1793711154-35062
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T13:03:19.304Z"
    quote: |-
      {"ts": "2026-11-03T13:03:19.304Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
gaps:
  - "No telemetry exists before the process start at 2026-11-03T13:03:19Z (E13): lab/logs/ holds a single 54-line app.log and no rotated backups. The complaint window ('the last few minutes') partly precedes observable history, so errors before 13:03:19Z can neither be confirmed nor excluded."
  - "The triage lens fan-out was skipped: the complete telemetry surface (the full 54-line log, the full metrics scrape, health) was read directly, and the software-defect and interfaces domains were excluded with cited evidence (E9; E3/E6/E11; E5/E7). The accepted blind spot is the absence of an independent per-lens pass over the same data."
  - "The initiator of the POST /chaos/enable call is outside the investigator's surface; only the operator-endpoint request line in the log is visible. Who or what enabled the switch cannot be determined from this surface."
  - "The claim that every 503 in the log pairs with a chaos_failure line on the same request_id rests on a manual read of the complete current log file; no independent cross-check exists beyond the 503 counters in E8 matching the two user-traffic failures."
usage:
  model: claude-fable-5
  tokens: 647465
  wall_clock_seconds: 310
---

# Intermittent shop 503s: chaos degradation switch enabled

## Summary

Root cause identified. This is not "nothing": an internal chaos switch was enabled on
faultline at 13:03:24Z with `failure_rate 0.08` and `error_status 503` (E1), and it is
still on (E2). While it is on, roughly 8% of shop requests get an injected HTTP 503;
the next attempt usually succeeds, which matches the report "occasional error, works on
retry, most people notice nothing." Real user traffic was hit at least twice
(E3/E4, E6), and a 30-probe burst confirmed the injection is live right now
(3 of 30 probes returned 503, each explicitly marked `chaos_failure` — E10, E11, E12).
Confidence is high: the target itself attributes every 503 to the chaos mechanism on a
per-request basis, so the link is the system's own attribution, not a timing
correlation. User impact stays low-grade but ongoing until the switch is turned off.

## Timeline

- **13:03:19.304Z** — process start, faultline 0.1.0 (E13). Telemetry history begins here.
- **13:03:20–13:03:25Z** — normal traffic: products, orders, all 2xx; sub-millisecond latencies (baseline).
- **13:03:24.236Z** — configuration-change marker: `chaos mode enabled`, failure_rate 0.08, error_status 503, extra_latency_ms 0 (E1).
- **13:03:25.434Z** — first user-visible failure: GET /products/2 → 503, marked `chaos_failure` (E3, E4). Retry of the same path → 200 ~90 ms later (E5).
- **13:03:25.538Z** — second user-visible failure: GET /products/5 → 503, marked `chaos_failure` (E6). Retry → 200 ~89 ms later (E7).
- **13:03:38Z** — complaint `startsAt` (manual report, fingerprint human-1793711018).
- **13:03:46Z** — investigation start; trigger latency 8 seconds.
- **13:03:57–58Z** — baseline probes: health 200, uptime ~38 s; metrics show `faultline_chaos_enabled 1` (E2) and exactly two 503s total (E8), zero unhandled exceptions (E9).
- **13:05:53–54Z** — validation burst: 30 probes to /products/1; 27×200, 3×503 (E10, E12), each 503 paired with a `chaos_failure` log line on the probe's request id (E11).
- **13:08:56Z** — investigation concluded.

## Investigation

Complaint object (manual trigger adapter, recorded verbatim):

```
source: human
fingerprint: human-1793711018
labels.alertname: human-report
annotations.summary: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
startsAt: 2026-11-03T13:03:38Z
```

Investigation start: 2026-11-03T13:03:46Z (trigger latency 8 s).

**Baseline.** Health 200 (uptime 38 s), full metrics scrape, full log read. The log is
54 lines with no rotated backups, so the baseline read covered the complete available
telemetry. The baseline itself contained the anomaly: a `chaos_enabled` WARNING (E1),
the live gauge (E2), and two chaos-injected 503s on unstamped user traffic (E3–E7).

**Triage.** No lens fan-out was spawned: the complete surface had been read directly,
and two of three lens domains were excluded with cited evidence — software-defect by
E9 (zero exception series), E3/E6 (failures explicitly chaos-marked) and E5/E7
(same inputs succeed on retry); interfaces by E1 (internal config marker precedes the
first failure) and the in-target `chaos_failure` attribution (E3, E6, E11). Spawning
agents to re-read the same 54 lines would have been coverage theater. The skip is
recorded as a gap.

**Validation probe.** H1 predicts new requests fail at ~8% while the gauge reads 1.
A 30-probe burst against /products/1 returned 3×503 (E10, E12), each correlated to a
`chaos_failure` line on the konan-stamped request id (E11). Prediction confirmed against
the baseline's normal (all-2xx traffic before 13:03:24Z).

**Judge.** A fresh adversarial judge received only the hypothesis list and verbatim
evidence. Verdicts: H1 validated ("the per-request chaos_failure pairing is the
system's own causal attribution, not correlation"); H2 invalidated; H3 invalidated.
The judge noted that "succeeds on retry" is an inference (different request ids), while
the quoted fact is: the same path returns 200 within ~90 ms of a 503 (E5, E7).

## Hypotheses

### H1 — chaos degradation switch (infra-process) — validated

An internal chaos switch, enabled at 13:03:24Z with failure_rate 0.08 and error_status
503, injects 503s into ~8% of shop requests. For: the switch event (E1), the live gauge
(E2), per-request `chaos_failure` attribution on both user-traffic 503s (E3/E4, E6) and
on all three probe 503s (E10–E12), the counters matching exactly two user-visible 503s
(E8), and immediate same-path recovery (E5, E7). Against: nothing. The observed probe
rate (3/30) is consistent with the configured 0.08.

### H2 — software defect — invalidated

The 503s exist (E4, E8), but nothing points at the target's code: the exception counter
section is empty (E9), every 503 carries an explicit chaos-injection marker (E3, E6,
E11), and the same inputs succeed ~90 ms later (E5, E7), which rules out a
deterministic data-dependent failure. The judge's reopening condition: one 5xx while
the gauge reads 0, or one 5xx log line with no paired `chaos_failure` line.

### H3 — external dependency or gateway (interfaces) — invalidated

503 is gateway-shaped by convention only. Here the target's own logger records each 503
as a completed request with sub-millisecond duration and a `chaos_failure` marker on
the same request id (E3, E6, E11), and the internal configuration marker immediately
precedes the first failure (E1). A gateway-generated 503 would not appear in the
target's log as a completed request. The judge's reopening condition: one
client-observed 503 whose request id is absent from the target's request log.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- Watch `faultline_chaos_enabled` on /metrics; the incident condition ends when it
  reads 0 and a `chaos_disabled` event appears in the log.
- Re-scrape the 503 counters periodically while the switch stays on, to measure
  accumulating user impact (count only unstamped traffic).
- Audit, on the operator side, who or what called POST /chaos/enable at 13:03:24Z —
  that surface is outside this investigation's contract.

## Gaps

1. **Pre-start blindness.** Telemetry begins at the process start 13:03:19Z (E13);
   there are no rotated log backups. The complaint window partly precedes this point,
   so earlier errors can neither be confirmed nor excluded.
2. **No independent lens pass.** The triage fan-out was skipped because the complete
   54-line log and full metrics were read directly and two lens domains were excluded
   with cited evidence. The accepted blind spot: no independent reader swept the same
   data.
3. **Switch initiator unknown.** The operator endpoint is outside the investigator's
   surface; only the request log line of POST /chaos/enable is visible.
4. **Completeness by manual read.** "Every 503 pairs with a chaos_failure line" rests
   on reading the whole current log; the only cross-check is that the E8 counters match
   the two user-traffic failures.
