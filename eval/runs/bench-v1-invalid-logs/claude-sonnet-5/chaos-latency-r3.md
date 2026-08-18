---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-latency-injection
  trigger: "manual (human profile, /konan adapter; fingerprint human-1787078396)"
  complaint: |-
    {"source": "human", "fingerprint": "human-1787078396", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."}, "startsAt": "2026-08-18T18:39:56Z"}
  started: "2026-08-18T18:40:04Z"
  concluded: "2026-08-18T18:44:42Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's chaos/fault-injection flag was enabled on the live process at 2026-08-18T18:39:38.833Z with extra_latency_ms=1500 and failure_rate=0.0, injecting synthetic (jittered, bounded well under 1.5s) latency into every business-surface response (/products, /products/{id}, /orders) while /health is exempt and no request ever fails — the mechanism behind the reported shop-wide slowness."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "faultline's chaos/fault-injection flag was enabled on the live process at 2026-08-18T18:39:38.833Z (failure_rate=0.0, extra_latency_ms=1500), injecting synthetic latency into /products, /products/{id}, and /orders responses while /health stays sub-millisecond and every request still returns 200/201."
    incident_class: interfaces
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
  - id: H2
    statement: "The slowness is process-level degradation — a restart loop, resource exhaustion, or worker/thread starvation — rather than injected latency."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E2, E6, E7, E8, E9]
  - id: H3
    statement: "The slowness is a data-dependent code defect triggered by specific inputs, not a uniform injected effect."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E2]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1787078423-17672 (2026-08-18T18:40:23Z) — first investigator probe"
    quote: |-
      {"status":"ok","uptime_seconds":51.09098899993114}
      -- HTTP 200 in 0.002023s request_id=konan-1787078423-17672
  - id: E2
    type: metric
    source: "/metrics @ request_id konan-1787078424-17678 (2026-08-18T18:40:24Z)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total (no data series present — no exception type has ever incremented)
      faultline_chaos_enabled 1
      process_uptime_seconds 51.47855491703376
      process_max_rss_bytes 47300608
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:33.654Z (pre-chaos, current process)"
    quote: |-
      {"ts": "2026-08-18T18:39:33.654Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d567e8ada9e4", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.139, "client": "127.0.0.1:49859"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:35.771Z (pre-chaos, current process — last known-good business request)"
    quote: |-
      {"ts": "2026-08-18T18:39:35.771Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1c13d5ca310c", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.95, "client": "127.0.0.1:49861"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:38.833Z — the config-change marker, same request_id as the following access line"
    quote: |-
      {"ts": "2026-08-18T18:39:38.833Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "59b2268e88a7", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
      {"ts": "2026-08-18T18:39:38.833Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "59b2268e88a7", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.721, "client": "127.0.0.1:49864"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:42.055Z — first business request after the marker"
    quote: |-
      {"ts": "2026-08-18T18:39:42.055Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "31596c2ccb84", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1161.851, "client": "127.0.0.1:49866"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:43.932Z — a second, distinct product id, still 200"
    quote: |-
      {"ts": "2026-08-18T18:39:43.932Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "9aba918529e6", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 811.379, "client": "127.0.0.1:49867"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:45.133Z — a third product id, still 200, non-monotonic duration versus E6/E7"
    quote: |-
      {"ts": "2026-08-18T18:39:45.133Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "b27cf18a383f", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 136.906, "client": "127.0.0.1:49868"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:50.562Z — /orders read, still 200"
    quote: |-
      {"ts": "2026-08-18T18:39:50.562Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "eac294a13c0f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1364.433, "client": "127.0.0.1:49871"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:40:23.960Z — investigator /health probe (E1), post-marker, still sub-millisecond"
    quote: |-
      {"ts": "2026-08-18T18:40:23.960Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787078423-17672", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.628, "client": "127.0.0.1:49897"}
  - id: E11
    type: probe
    source: "/health @ request_id konan-1787078670-17848 (2026-08-18T18:44:30Z) — confirmatory round, ~5 min into the incident, no restart since E1 (uptime climbed continuously)"
    quote: |-
      {"status":"ok","uptime_seconds":297.8615022080485}
      -- HTTP 200 in 0.001496s request_id=konan-1787078670-17848
  - id: E12
    type: probe
    source: "/products @ request_id konan-1787078671-17854 (2026-08-18T18:44:31Z) — confirmatory round"
    quote: "-- HTTP 200 in 0.246694s request_id=konan-1787078671-17854"
  - id: E13
    type: probe
    source: "/products/1 @ request_id konan-1787078671-17860 (2026-08-18T18:44:31Z) — confirmatory round"
    quote: "-- HTTP 200 in 0.619833s request_id=konan-1787078671-17860"
  - id: E14
    type: probe
    source: "/orders @ request_id konan-1787078672-17866 (2026-08-18T18:44:32Z) — confirmatory round"
    quote: "-- HTTP 200 in 1.211644s request_id=konan-1787078672-17866"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:39:31.554Z–18:39:32.880Z — the one process restart in the visible tail, a clean shutdown/startup pair"
    quote: |-
      {"ts": "2026-08-18T18:39:31.554Z", "level": "INFO", "logger": "uvicorn.error", "message": "Shutting down"}
      {"ts": "2026-08-18T18:39:31.657Z", "level": "INFO", "logger": "uvicorn.error", "message": "Finished server process [17154]"}
      {"ts": "2026-08-18T18:39:32.880Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [17553]"}
gaps:
  - "extra_latency_ms=1500 (E5) is the configured ceiling, but every observed post-marker duration (E6-E9, E12-E14: 136ms-1364ms) fell short of it — consistent with jittered/sampled injection rather than a flat add, but the injection's exact distribution is not documented on the read-only surface and was not directly confirmed, only inferred from the scatter."
  - "Sampling is thin relative to the incident's duration: business-surface evidence comes from two windows (onset, 18:39:42-50Z; confirmatory, 18:44:30-32Z), roughly 4.5 minutes apart, not a continuous stream — the injected-latency distribution over the full incident is not fully characterized."
  - "Traffic origin is outside the surface: all non-investigator requests in the log carry only loopback client ports. How many distinct end users experienced the slowness, versus fewer sessions issuing repeated requests, cannot be determined from target-side telemetry alone; the complaint's 'users say' is taken as reported, not independently corroborated by client identity."
  - "A prior process incarnation (started 2026-08-18T18:29:17Z, per app.log) shows the identical shape — chaos enabled ~7s after startup, immediately followed by the same slow-but-error-free business-endpoint pattern. Whether that is a separate, earlier occurrence of the same class of incident or scenario setup from a prior session cannot be distinguished from the read-only surface; it was not used as evidence for H1 to avoid conflating two process lifetimes, but is recorded here for audit honesty."
usage:
  model: claude-sonnet-5
  tokens: 2441519
  wall_clock_seconds: 278
---

# Shop-wide slowness: chaos flag injected latency-only degradation on the business surface

## Summary

Verdict: **root-cause-identified**. The complaint — every page slow, nothing errors,
health checks green and fast — is confirmed and fully explained: at
2026-08-18T18:39:38.833Z the target's own chaos-injection subsystem logged a flag flip,
`chaos_enabled` with `failure_rate: 0.0` and `extra_latency_ms: 1500` (E5). Every
business-surface request logged afterward — `/products`, `/products/{id}` (two distinct
product ids), `/orders` GET and POST — jumped from sub-2ms (E3, E4) to 136-1364ms
(E6-E9), while remaining HTTP 200/201 throughout; `/health` stayed sub-millisecond both
immediately after the flip (E10) and roughly five minutes later (E11), and the counters
confirm zero exceptions and no non-2xx status anywhere (E2). A confirmatory round
five minutes on (E11-E14) reproduced the same shape — `/health` fast, business paths
elevated but bounded under the configured 1.5s ceiling — ruling out a one-off blip.
Two alternative explanations were considered and killed by the same evidence:
process-level degradation (H2 — the one restart in the log precedes and is decoupled
from the slow window, uptime and RSS gauges are stable, durations are scattered not
ramping) and a data-dependent code defect (H3 — two different product ids are both
slow but both succeed, and no exception counter ever increments). Confidence: high.

## Timeline

- **18:39:32.880Z** — clean process restart, immediately followed by fast requests (E15).
- **18:39:33-35Z** — pre-incident baseline: `/products` 1.139ms, `POST /orders` 1.95ms (E3, E4).
- **18:39:38.833Z** — `chaos_enabled` flag flip: `failure_rate=0.0`, `extra_latency_ms=1500` (E5).
- **18:39:42-50Z** — onset: business-surface requests jump to 136-1364ms, all still 200/201 (E6-E9).
- **18:40:23-24Z** — investigator baseline: `/health` still sub-ms; metrics confirm `faultline_chaos_enabled 1`, zero exceptions, no 5xx (E1, E2, E10).
- **18:44:30-32Z** — confirmatory round, ~5 min later: `/health` still sub-2ms, business paths still elevated-but-bounded, no restart in between (E11-E14).

## Investigation

Baseline (health + metrics probe, log tail read) surfaced the chaos-flag log line and
the latency split almost immediately. Triage fanned out all three discipline lenses
(infra-process, interfaces, software-defect) in parallel, each blind to the others, given
the same baseline summary. All three independently converged on the same mechanism:
interfaces flagged the config-change marker as the prime hypothesis; infra-process
confirmed the process was alive-and-degraded, not crashed or saturating, and that the
one restart present was decoupled from the slow window; software-defect found no
exceptions and a route-agnostic, input-agnostic spread, ruling out a per-input defect.
No lens found evidence for its own domain as the cause. Because the interfaces evidence
was already deterministic (a timestamped, parameterized config-change log line whose
predicted effect matched observed durations exactly), deep-dive was skipped and the
hypothesis list went straight to an adversarial judge.

The judge validated H1 but flagged two gaps: the injected-latency magnitude
(observed durations never reached the configured 1500ms ceiling) and thin post-marker
sampling (one data point each for `/products` and `/orders` at onset). Both were cheap
to close with more read-only probes while chaos was still active — E11-E14 confirm the
same shape five minutes later with `/health` still exempt and business paths still
bounded well under 1.5s, closing both items without overturning the verdict.

## Hypotheses

### H1 — chaos flag injected latency-only degradation (validated)

Statement: the target's own fault-injection flag was flipped on at 18:39:38.833Z with
`extra_latency_ms=1500` and `failure_rate=0.0`, adding synthetic latency to every
business-surface response while `/health` is exempt and nothing fails. Supported by the
config-change marker itself (E5), the clean before/after bracketing on both `/products`
and `/orders` (E3, E4 vs E6, E9), a second product id showing the same shape (E7), the
persistently-fast `/health` path across two separate time windows (E10, E11), the
metrics confirming the flag is still active with zero exceptions and no non-2xx status
(E2), and the confirmatory-round reproduction (E12-E14). No evidence against.

### H2 — process-level degradation (invalidated)

Statement: a restart loop, resource exhaustion, or worker starvation, not injected
latency. Invalidated: the only restart in the visible log is a single clean
shutdown/startup pair that precedes the slow window by ~6s and is immediately followed
by fast requests (E15) — not a loop. `process_uptime_seconds` and
`process_max_rss_bytes` show no elevation or growth pattern (E2), and per-request
durations after the marker are scattered (1161.851ms, 811.379ms, 136.906ms, 1364.433ms
— E6-E9) rather than a rising saturation ramp.

### H3 — data-dependent code defect (invalidated)

Statement: specific inputs failing or degrading, not a uniform injected effect.
Invalidated: two distinct product ids (1 and 2) both show elevated-but-successful
responses (E7, E8), all business routes moved together at the same marker boundary, and
`http_exceptions_total` carries no data series at any point (E2) — no exception type has
ever incremented, which the software-defect lens's own criteria treat as ruling out a
code-defect signature.

## Safe next steps

- Continue read-only monitoring of `/metrics` for `faultline_chaos_enabled` — it will
  read `0` once the flag is turned off, which is the expected resolution signal on this
  surface.
- If the slowness persists past the current chaos window, re-probe the same four paths
  (`/health`, `/products`, `/products/{id}`, `/orders`) to check whether the shape holds
  or a second, independent cause has layered on top.
- No remediation action is proposed here — flipping the chaos flag off is outside the
  investigator's read-only surface and is an operator/eval-side action, not this
  investigation's to take.

## Gaps

- `extra_latency_ms=1500` (E5) is the configured ceiling, but every observed post-marker
  duration (E6-E9, E12-E14: 136ms-1364ms) fell short of it — consistent with
  jittered/sampled injection rather than a flat add, but the injection's exact
  distribution isn't documented on the read-only surface and was inferred from the
  scatter, not directly confirmed.
- Sampling is thin relative to the incident's duration: business-surface evidence comes
  from two windows (onset, 18:39:42-50Z; confirmatory, 18:44:30-32Z) roughly 4.5 minutes
  apart, not a continuous stream.
- Traffic origin is outside the surface: all non-investigator requests carry only
  loopback client ports, so the number of distinct end users affected cannot be
  independently corroborated from target-side telemetry — the complaint's "users say"
  is taken as reported.
- A prior process incarnation (started 2026-08-18T18:29:17Z) shows the identical shape —
  chaos enabled ~7s after startup, then the same slow-but-error-free pattern. Whether
  that is an earlier, separate occurrence or scenario setup from a prior session can't be
  distinguished from the read-only surface; it was not used as evidence for H1 to avoid
  conflating two process lifetimes, but is recorded here for audit honesty.
