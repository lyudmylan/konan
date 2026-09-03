---
konan_journal: 1
investigation:
  id: 2026-08-25-occasional-shop-503s-chaos-enabled
  trigger: "manual (human profile, /konan). Complaint object: source=human, fingerprint=human-1787635208, labels.alertname=human-report (no severity stated), startsAt=2026-08-25T05:20:08Z. Investigation start 2026-08-25T05:20:25Z; trigger latency 17 s."
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-25T05:20:25Z
  concluded: 2026-08-25T05:23:35Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change enabled chaos mode at 2026-08-25T05:19:59.021Z with failure_rate 0.08 and error_status 503; it is still active and injects a 503 on a random ~8% of requests before the handler runs, which is the occasional retry-able error users see."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled at 05:19:59.021Z (failure_rate 0.08, error_status 503) and remains active, injecting probabilistic 503s on user requests."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E7, E8, E10, E14]
    evidence_against: []
  - id: H2
    statement: "A defect in the application's own code throws on GET /products for some inputs, producing 5xx."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E6, E7, E8, E10, E13]
  - id: H3
    statement: "The process restarted or is resource-saturated, causing intermittent errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E9, E10, E11, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:19:59.021Z"
    quote: "{\"ts\": \"2026-08-25T05:19:59.021Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"ef46530d1d4d\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:20:00.370Z"
    quote: "{\"ts\": \"2026-08-25T05:20:00.370Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"4a3448aa054c\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:20:00.370Z"
    quote: "{\"ts\": \"2026-08-25T05:20:00.370Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 503\", \"request_id\": \"4a3448aa054c\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.133, \"client\": \"127.0.0.1:49359\"}"
  - id: E4
    type: metric
    source: "/metrics @ request_id konan-1787635332-38821"
    quote: "faultline_chaos_enabled 1"
  - id: E5
    type: metric
    source: "/metrics @ request_id konan-1787635332-38821"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 8"
  - id: E6
    type: metric
    source: "/metrics @ request_id konan-1787635332-38821"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter (no series follow)"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:20:00.283Z"
    quote: "{\"ts\": \"2026-08-25T05:20:00.283Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"783baeb72058\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 0.369, \"client\": \"127.0.0.1:49353\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:20:00.456Z"
    quote: "{\"ts\": \"2026-08-25T05:20:00.456Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"e8d987b0fbbf\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 0.437, \"client\": \"127.0.0.1:49365\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:19:54.060Z"
    quote: "{\"ts\": \"2026-08-25T05:19:54.060Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log (57 lines, no .1-.3 backups) @ grep at 2026-08-25T05:22:12Z for event in {chaos_enabled, chaos_disabled, chaos_failure, unhandled_exception, startup} or status 5xx"
    quote: "3:{\"ts\": \"2026-08-25T05:19:54.060Z\", ... \"event\": \"startup\" ...} / 12:{\"ts\": \"2026-08-25T05:19:59.021Z\", ... \"event\": \"chaos_enabled\" ...} / 35:{\"ts\": \"2026-08-25T05:20:00.370Z\", ... \"event\": \"chaos_failure\" ...} / 36:{\"ts\": \"2026-08-25T05:20:00.370Z\", ... \"status\": 503 ...} (exactly 4 matching lines; no chaos_disabled, no unhandled_exception, no second startup, no other 5xx)"
  - id: E11
    type: metric
    source: "/metrics @ request_id konan-1787635332-38821"
    quote: "process_uptime_seconds 138.26664637494832 / process_max_rss_bytes 47038464"
  - id: E12
    type: probe
    source: "/health @ request_id konan-1787635226-38689"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":32.481837374856696} / -- HTTP 200 in 0.009442s request_id=konan-1787635226-38689"
  - id: E13
    type: probe
    source: "/products @ request_id konan-1787635287-38797"
    quote: "-- HTTP 200 in 0.001340s request_id=konan-1787635287-38797"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:19:56.951Z (last request line before E1)"
    quote: "{\"ts\": \"2026-08-25T05:19:56.951Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"5663ddde8479\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.917, \"client\": \"127.0.0.1:49339\"}"
gaps:
  - "Only one user-facing 503 exists in the window (E3), so the pairing rule 'every 5xx after the marker carries a chaos_failure event' was confirmed with n=1; the ~8% rate is the configured value (E1), not a measured one. The lab had only ~37 user requests in the window."
  - "Who or what issued POST /chaos/enable (request_id ef46530d1d4d, client 127.0.0.1:49340) is not visible on the telemetry surface; the operator surface /chaos is outside the investigator's allowlist."
  - "RSS was sampled at a single steady value (E11); growth over time was not assessed. The infra-process lens's own probes were refused by the permission layer (absolute script path), so it argued from the baseline sample and the log."
usage:
  model: claude-fable-5
  tokens: 1259176
  wall_clock_seconds: 190
---

# Occasional shop 503s after chaos mode was enabled with failure_rate 0.08

## Summary

**Root cause identified (interfaces / runtime configuration change).** At 2026-08-25T05:19:59.021Z chaos mode was enabled on faultline with `failure_rate 0.08`, `error_status 503`, `extra_latency_ms 0` (E1), and it is still active (`faultline_chaos_enabled 1`, E4; no `chaos_disabled` marker, E10). Since then a random ~8% of requests are rejected before the handler runs with a 503 — the first and so far only user-facing hit was `GET /products` at 05:20:00.370Z, explicitly logged as `chaos-injected failure` on the same request id (E2, E3). The same route returned 200 immediately before and after (E7, E8), which is why users see "works on retry". Impact so far: 1 of 9 user `GET /products` requests failed (E5); orders and product-detail routes had no failures in the window, but the injection is route-agnostic and remains on. Confidence: high — the failing request is causally tagged by the service, not merely correlated. The complaint is not "nothing": the error rate is configured, not transient, and will continue until the chaos flag is turned off.

## Timeline

- 05:19:54.060Z — process start, single startup marker (E9).
- 05:19:56.951Z — last known-good request before the change: `POST /orders -> 201` (E14). Zero non-2xx before this point (E10).
- **05:19:59.021Z — configuration change marker: `chaos mode enabled`, `failure_rate 0.08`, `error_status 503` (E1).**
- 05:20:00.283Z — `GET /products -> 200`, user traffic (E7).
- 05:20:00.370Z — first known-bad: `chaos-injected failure` + `GET /products -> 503`, request id `4a3448aa054c`, user traffic, 0.133 ms (E2, E3).
- 05:20:00.456Z — `GET /products -> 200`, user traffic (E8).
- 05:20:08Z — complaint raised (`startsAt`); 05:20:25Z investigation start.
- 05:20:26Z — `/health` ok, uptime 32.5 s (E12).
- 05:22:12Z — `/metrics`: chaos gauge still 1, uptime 138 s, no exception series (E4, E6, E11). No `chaos_disabled` at any point (E10).

## Investigation

- **Baseline** (05:20:26–27Z): `/health` 200 (E12); `/metrics` with `faultline_chaos_enabled 1`, one `/products` 503, no exception series; whole log read (53 lines then, no rotated backups).
- **Triage**, three lenses in parallel, each blind: interfaces (found E1→E2/E3 onset, before/after rate 0/5 → 1/32), software-defect (no exceptions, non-deterministic on identical input, reproduction probe 200 = E13), infra-process (one startup, uptime consistent, RSS 45 MiB, fast failure).
- **Deep-dive**: skipped — H1's triage evidence was deterministic and complete (the service tags the failing request as injected). One cheap orchestrator refresh confirmed the state unchanged (E4, E5, E10, E11).
- **Judge** (evidence-only, adversarial): H1 validated; H2 invalidated; H3 invalidated. Residual weakness noted: n=1 for the 503/chaos_failure pairing; recorded under Gaps.

## Hypotheses

### H1 — chaos mode enabled at 05:19:59Z injects ~8% 503s (interfaces) — validated

For: the change marker (E1) precedes the first and only 5xx (E3) by 1.35 s; that 5xx carries a `chaos_failure` event on the same request id (E2); the gauge is still 1 (E4) with no disable marker (E10); the route succeeds on both sides of the failure with identical input (E7, E8); no 5xx existed before the marker (E10, E14); counts agree (E5). The 0.133 ms duration (E3) — faster than any success on the route — matches a short-circuit before the handler. Against: none.

### H2 — application code defect on GET /products (software-defect) — invalidated

For: none. Against: no `unhandled_exception` or stack lines in the whole log (E10); `http_exceptions_total` has no series (E6); the failure is non-deterministic on a route with no input (E7, E3, E8; investigator reproduction 200, E13); the one 5xx names its cause as injected (E2).

### H3 — process restart or saturation (infra-process) — invalidated

For: none. Against: one startup marker only (E9, E10); uptime in E12 and E11 both point to the 05:19:54Z start; RSS 47 MB (E11); the failing request was the fastest in the log at 0.133 ms (E3), not a timeout shape.

## Safe next steps

Read-only suggestions only:

- Watch `faultline_chaos_enabled` and `http_requests_total{status="503"}` on `/metrics`; the incident ends when the gauge reads 0 and the 503 counters stop growing.
- Grep `lab/logs/app.log` for `"event": "chaos_disabled"` to confirm any rollback, and for `"event": "chaos_failure"` to count further user hits (exclude `konan-` request ids).
- Ask the operator who issued `POST /chaos/enable` (request id `ef46530d1d4d`, 05:19:59Z) whether it was intentional — the flag is operator surface and outside what konan may touch.

## Gaps

- **Sample size.** Only one user-facing 503 exists in the window, so the "every 5xx pairs with a `chaos_failure`" rule was confirmed with n=1, and the ~8% rate is the configured value (E1) rather than a measured one. A second paired 503 on user traffic would close this.
- **Actor.** Who or what issued `POST /chaos/enable` is not on the telemetry surface; `/chaos` is operator surface outside the probe allowlist.
- **RSS trend.** A single RSS sample (E11) cannot show growth. The infra-process lens's own probes were refused by the permission layer (it used an absolute script path); it argued from the baseline sample and the full log instead. No other signal suggested resource pressure.
