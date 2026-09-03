---
konan_journal: 1
investigation:
  id: 2026-08-20-routine-handover-check
  trigger: "manual (/konan human-report; fingerprint human-1787204932; startsAt 2026-08-20T05:48:52Z; investigation start 2026-08-20T05:49:01Z; trigger latency 9s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: "2026-08-20T05:49:01Z"
  concluded: "2026-08-20T05:55:53Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An operator-surface chaos-injection window caused the earlier noise: POST /chaos/enable at 05:48:09.230Z set failure_rate 0.6 / error_status 503 / no added latency, producing exactly three 503s to non-investigator traffic (GET /products/1, POST /orders, GET /products) between 05:48:12Z and 05:48:14Z, and POST /chaos/disable closed the window at 05:48:15.575Z."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E14]
    evidence_against: []
  - id: H2
    statement: "A software defect (unhandled exception or data-dependent failure) caused the earlier errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E4, E9, E10]
  - id: H3
    statement: "A process or infrastructure problem (crash, restart, resource saturation, or latency degradation) caused, or is causing, errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E16, E17, E18, E5]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:05.351Z"
    quote: "{\"ts\": \"2026-08-20T05:48:05.351Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:09.230Z"
    quote: "{\"ts\": \"2026-08-20T05:48:09.230Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"e184b1873eb0\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:09.230Z (request_id e184b1873eb0 — unstamped, so not an investigator probe)"
    quote: "{\"ts\": \"2026-08-20T05:48:09.230Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /chaos/enable -> 200\", \"request_id\": \"e184b1873eb0\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 3.006, \"client\": \"127.0.0.1:52321\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:12.402Z"
    quote: "{\"ts\": \"2026-08-20T05:48:12.402Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"46d9ceaf123d\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:12.403Z (same request_id as E4)"
    quote: "{\"ts\": \"2026-08-20T05:48:12.403Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 503\", \"request_id\": \"46d9ceaf123d\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.275, \"client\": \"127.0.0.1:52325\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:13.460Z"
    quote: "{\"ts\": \"2026-08-20T05:48:13.460Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"056dc060f8d9\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:14.517Z"
    quote: "{\"ts\": \"2026-08-20T05:48:14.517Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"5db7cb1fe8c2\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:15.575Z"
    quote: "{\"ts\": \"2026-08-20T05:48:15.575Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"e4b9f9d1ecfb\", \"event\": \"chaos_disabled\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:07.167Z (same input as E5, before the window)"
    quote: "{\"ts\": \"2026-08-20T05:48:07.167Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"9ed0e58cd673\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.013, \"client\": \"127.0.0.1:52319\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:36.695Z (same input as E5, after the window)"
    quote: "{\"ts\": \"2026-08-20T05:48:36.695Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"b66aeb85609f\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.797, \"client\": \"127.0.0.1:52332\"}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:48:37.753Z (order flow succeeds after the window)"
    quote: "{\"ts\": \"2026-08-20T05:48:37.753Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"aae941d69080\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.742, \"client\": \"127.0.0.1:52333\"}"
  - id: E12
    type: probe
    source: "/health @ 2026-08-20T05:49:23Z, request_id konan-1787204963-80180"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":78.59326533298008} -- HTTP 200 in 0.001767s"
  - id: E13
    type: metric
    source: "/metrics @ 2026-08-20T05:54:34Z, probe konan-1787205274-80322"
    quote: "faultline_chaos_enabled 0"
  - id: E14
    type: metric
    source: "/metrics @ 2026-08-20T05:54:34Z, probe konan-1787205274-80322 (the only non-2xx series in the scrape; values unchanged since the 05:49:30Z scrape)"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
  - id: E15
    type: metric
    source: "/metrics @ 2026-08-20T05:54:34Z, probe konan-1787205274-80322 (HELP/TYPE lines only — zero exception samples followed)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E16
    type: metric
    source: "/metrics @ 2026-08-20T05:49:30Z, probe konan-1787204970-80186"
    quote: "process_uptime_seconds 84.73314679088071"
  - id: E17
    type: metric
    source: "/metrics @ 2026-08-20T05:54:34Z, probe konan-1787205274-80322 (monotonic vs E16 — no restart; counters only grew)"
    quote: "process_uptime_seconds 389.62287866603583"
  - id: E18
    type: metric
    source: "/metrics @ 2026-08-20T05:54:34Z, probe konan-1787205274-80322 (identical value at the 05:49:30Z scrape — peak RSS flat)"
    quote: "process_max_rss_bytes 46694400"
  - id: E19
    type: probe
    source: "/health @ 2026-08-20T05:54:22Z, request_id konan-1787205262-80315 (freshness re-probe after the judge round)"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":377.22312970785424} -- HTTP 200 in 0.001572s"
gaps:
  - "Who or what called the operator surface cannot be identified from the telemetry: the chaos enable/disable requests (E3, E8) show only client 127.0.0.1 and an unstamped request id. The operator surface (/chaos, /simulate) is outside the investigator's probe allowlist by contract."
  - "Telemetry is observed through 2026-08-20T05:54:34Z (E17); a fault that starts after the last scrape is not excluded — inherent to any point-in-time no-incident claim."
  - "Post-window non-investigator traffic is thin (five requests, 05:48:35Z-05:48:39Z, E10/E11 among them); the current-health claim rests partly on investigator probes (E12, E19), which the contract says to weigh separately from user traffic."
usage:
  model: claude-fable-5
  tokens: 1692933
  wall_clock_seconds: 412
---

# Routine handover check: earlier 503 noise was a closed chaos-injection window; no active incident

## Summary

**No active incident.** The service is healthy: health returns 200 (E19), chaos is off (E13), no unhandled exception has ever been counted in this process (E15), latency is sub-2 ms, and memory is flat (E18). The "noise earlier" in the complaint is fully accounted for: an operator-surface chaos-injection window, enabled at 05:48:09.230Z with failure rate 0.6 and error status 503 (E2, E3) and disabled 6.3 seconds later at 05:48:15.575Z (E8), injected exactly three 503s into non-investigator traffic — GET /products/1, POST /orders, GET /products (E4–E7, E14). Those three requests were real user-facing failures at the time, but the window is closed and the error counters have not moved since. Confidence is high: the log is the complete, unrotated history of the only process instance, and metrics corroborate the log line-for-line.

## Timeline

- **05:48:05.351Z** — process start, faultline 0.1.0, the only startup marker in the full log (E1).
- **05:48:09.230Z** — configuration change: chaos mode enabled via POST /chaos/enable, failure_rate 0.6, error_status 503, extra_latency_ms 0; unstamped request id, client 127.0.0.1 (E2, E3).
- **05:48:12.402Z** — chaos-injected 503 on GET /products/1 (E4, E5).
- **05:48:13.460Z** — chaos-injected 503 on POST /orders (E6).
- **05:48:14.517Z** — chaos-injected 503 on GET /products (E7).
- **05:48:15.575Z** — configuration change: chaos mode disabled via POST /chaos/disable (E8).
- **05:48:35Z–05:48:39Z** — non-investigator traffic all succeeds, including the previously failing paths (E10, E11).
- **05:48:52Z** — human complaint raised (`startsAt`); investigation starts 05:49:01Z.
- **05:49:23Z–05:54:34Z** — investigator baseline and freshness probes: health ok, chaos gauge 0, error counters frozen at the three window 503s, uptime monotonic (E12, E13, E14, E17, E19).

## Investigation

Baseline (05:49Z): health 200 (E12), chaos gauge 0, no exception series, three 503 counters, complete 29-line log in view. Triage fanned out three parallel lenses — infra-process, interfaces, software-defect — each given only the lens file, the surface contract, the verbatim complaint, and the baseline. All three converged: the only anomaly in the process history is the bounded chaos window; nothing is anomalous now. Triage evidence was deterministic and complete (explicit chaos_enabled / chaos_failure / chaos_disabled markers bracketing every error), so the hypotheses skipped deep-dive and went straight to the adversarial judge. The judge validated H1 and the no-active-incident conclusion, invalidated H2 and H3, and asked for one freshness re-probe, which was done at 05:54Z (E17, E19) — counters unchanged, chaos still off.

## Hypotheses

### H1 — chaos-injection window caused the noise (validated)

Every clause has direct evidence: the enable marker with exact parameters (E2) tied to the operator-surface call (E3), three failures each self-labeled `chaos_failure` on the same request id as its 503 response (E4–E7), the disable marker (E8), and metrics counting exactly one 503 per affected path and nothing else non-2xx (E14). The failing request ids are unstamped, so the impact was on non-investigator traffic. In-window successes alongside failures match the configured 0.6 probability. No evidence contradicts it.

### H2 — software defect (invalidated)

Zero exception series across the process lifetime (E15); every error carries an explicit injection marker (E4); and the identical input GET /products/1 succeeds both before (E9) and after (E10) the window, ruling out a data-dependent deterministic defect. The three 503s spread across three unrelated routes in 2 seconds — an injection shape, not a failing unit.

### H3 — process/infrastructure problem (invalidated)

One startup marker in a complete log (E1), monotonic uptime across scrapes with no counter reset (E16, E17), flat peak RSS ~46.7 MB (E18), and no latency component anywhere — the chaos config added 0 ms (E2) and a failing request completed in 0.275 ms (E5).

## Safe next steps

- If the chaos enable was not an expected drill or eval action, review who has access to the operator surface on 127.0.0.1 — the telemetry cannot identify the caller (read-only follow-up: correlate the 05:48:09Z timestamp with operator/eval activity records outside this service).
- Optionally re-scrape /metrics at shift end and confirm the three 503 counters (E14) are still the only non-2xx series.

## Gaps

- The identity of the operator-surface caller is outside the telemetry surface; the log shows only client 127.0.0.1 with an unstamped request id, and /chaos is outside the probe allowlist by contract. (Prior journals in git history were also out of bounds for this run under the eval blinding boundary.)
- Telemetry is observed through 05:54:34Z; any fault arising after that is unobserved — inherent to a point-in-time no-incident verdict.
- Only five non-investigator requests arrived after the window closed, so current health rests partly on investigator probes, which the contract counts separately from user traffic.
