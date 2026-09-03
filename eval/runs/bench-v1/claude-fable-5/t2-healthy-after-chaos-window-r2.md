---
konan_journal: 1
investigation:
  id: 2026-08-24-routine-handover-check
  trigger: "manual (/konan, profile human; alertname human-report; fingerprint human-1787590140; startsAt 2026-08-24T16:49:00Z; investigation start 2026-08-24T16:49:11Z; trigger latency 11s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-24T16:49:11Z
  concluded: 2026-08-24T16:53:22Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The earlier noise was a runtime configuration change: chaos mode was enabled (failure_rate 0.6, error_status 503) at 16:48:21.418Z and disabled at 16:48:27.791Z, injecting 503 responses into three non-investigator requests during a 6.4 s window; the flag is off now and the service answers normally."
    incident_class: interfaces
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E2, E8, E9, E10, E11, E16, E17, E18, E20, E21]
    evidence_against: []
  - id: H2
    statement: "A code defect in the shop service (data-dependent failure on specific product ids or on order creation) is causing 5xx responses."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E2, E8, E9, E16, E17, E4, E5, E6, E20]
  - id: H3
    statement: "The process crashed or restarted, or is degraded by resource saturation or rising latency."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13, E14, E15, E19, E21]
latent_findings:
  - statement: "Metric label shape is inconsistent: chaos-failed requests are counted under the raw path (path=\"/products/1\", path=\"/products/2\") while successful requests to the same route are counted under the route template (path=\"/products/{product_id}\"), which makes per-route error-rate math from /metrics unreliable."
    evidence: [E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:17.132Z (only startup event in the file; no rotated backups exist)"
    quote: "{\"ts\": \"2026-08-24T16:48:17.132Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:19.354Z"
    quote: "{\"ts\": \"2026-08-24T16:48:19.354Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"79baa11a9c78\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.012, \"client\": \"127.0.0.1:62815\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:21.418Z"
    quote: "{\"ts\": \"2026-08-24T16:48:21.418Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"e42eb08d1fe7\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:23.541Z (two lines, same request_id)"
    quote: "{\"ts\": \"2026-08-24T16:48:23.541Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"5d9dc8fc72d4\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/2\"} / {\"ts\": \"2026-08-24T16:48:23.541Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/2 -> 503\", \"request_id\": \"5d9dc8fc72d4\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 503, \"duration_ms\": 0.324, \"client\": \"127.0.0.1:62818\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:24.601Z (two lines, same request_id)"
    quote: "{\"ts\": \"2026-08-24T16:48:24.601Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"5b2c1a491157\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} / {\"ts\": \"2026-08-24T16:48:24.601Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 503\", \"request_id\": \"5b2c1a491157\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.479, \"client\": \"127.0.0.1:62819\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:25.664Z (two lines, same request_id)"
    quote: "{\"ts\": \"2026-08-24T16:48:25.664Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"048ae136c017\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"} / {\"ts\": \"2026-08-24T16:48:25.665Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 503\", \"request_id\": \"048ae136c017\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.31, \"client\": \"127.0.0.1:62820\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:27.791Z"
    quote: "{\"ts\": \"2026-08-24T16:48:27.791Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"a8e83e092e96\", \"event\": \"chaos_disabled\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:48.909Z"
    quote: "{\"ts\": \"2026-08-24T16:48:48.909Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"2736f747831d\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.846, \"client\": \"127.0.0.1:62826\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:48:49.967Z (two lines, same request_id)"
    quote: "{\"ts\": \"2026-08-24T16:48:49.967Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"a7314021e381\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 2, \"quantity\": 1, \"total_price\": 23.0} / {\"ts\": \"2026-08-24T16:48:49.968Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"a7314021e381\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.971, \"client\": \"127.0.0.1:62827\"}"
  - id: E10
    type: metric
    source: "scripts/probe.sh /metrics request_id=konan-1787590162-26434 @ 2026-08-24T16:49:22Z"
    quote: "faultline_chaos_enabled 0"
  - id: E11
    type: metric
    source: "scripts/probe.sh /metrics request_id=konan-1787590162-26434 @ 2026-08-24T16:49:22Z"
    quote: "http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1 / http_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1 / http_requests_total{method=\"POST\",path=\"/chaos/disable\",status=\"200\"} 1 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 1"
  - id: E12
    type: metric
    source: "scripts/probe.sh /metrics request_id=konan-1787590162-26434 @ 2026-08-24T16:49:22Z (no sample lines follow the header)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter / # HELP faultline_chaos_enabled Whether chaos mode is active."
  - id: E13
    type: probe
    source: "scripts/probe.sh /health request_id=konan-1787590162-26428 @ 2026-08-24T16:49:22Z"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":65.25719041703269} -- HTTP 200 in 0.004590s request_id=konan-1787590162-26428"
  - id: E14
    type: metric
    source: "scripts/probe.sh /metrics request_id=konan-1787590162-26434 @ 2026-08-24T16:49:22Z"
    quote: "process_uptime_seconds 65.51593200000934 / process_max_rss_bytes 48119808"
  - id: E15
    type: metric
    source: "scripts/probe.sh /metrics request_id=konan-1787590215-26489 @ 2026-08-24T16:50:15Z (infra-process triage lens)"
    quote: "process_uptime_seconds 118.27506637503393 / process_max_rss_bytes 48119808 / http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 4"
  - id: E16
    type: probe
    source: "scripts/probe.sh /products/1 request_id=konan-1787590233-26551 @ 2026-08-24T16:50:33Z (software-defect triage lens)"
    quote: "-- HTTP 200 in 0.001861s request_id=konan-1787590233-26551"
  - id: E17
    type: probe
    source: "scripts/probe.sh /products/2 request_id=konan-1787590233-26557 @ 2026-08-24T16:50:33Z (software-defect triage lens)"
    quote: "-- HTTP 200 in 0.001267s request_id=konan-1787590233-26557"
  - id: E18
    type: probe
    source: "scripts/probe.sh /orders request_id=konan-1787590224-26535 @ 2026-08-24T16:50:24Z (interfaces triage lens; GET, read path only)"
    quote: "-- HTTP 200 in 0.001438s request_id=konan-1787590224-26535"
  - id: E19
    type: log
    source: "lab/logs/app.log, first access line after startup @ 2026-08-24T16:48:17.816Z (largest duration_ms in the file; every other access line is below 3 ms)"
    quote: "{\"ts\": \"2026-08-24T16:48:17.816Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /health -> 200\", \"request_id\": \"84a9bf9ca200\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/health\", \"status\": 200, \"duration_ms\": 15.418, \"client\": \"127.0.0.1:62812\"}"
  - id: E20
    type: log
    source: "lab/logs/app.log, full file @ 2026-08-24T16:53Z: grep -c '\"event\": \"request\"'; grep '\"event\": \"request\"' | grep -v '\"status\": 20[01]'; grep -c '\"event\": \"chaos_failure\"'; grep -cE '\"event\": \"(unhandled_exception|simulated_exception)\"'"
    quote: "28 / GET /products/2 -> 503 (2026-08-24T16:48:23.541Z, 5d9dc8fc72d4); GET /products/1 -> 503 (2026-08-24T16:48:24.601Z, 5b2c1a491157); POST /orders -> 503 (2026-08-24T16:48:25.665Z, 048ae136c017) / 3 / 0"
  - id: E21
    type: metric
    source: "scripts/probe.sh /metrics request_id=konan-1787590402-26633 @ 2026-08-24T16:53:22Z"
    quote: "faultline_chaos_enabled 0 / process_uptime_seconds 305.64619425009005 / process_max_rss_bytes 48119808 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 7 / http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1"
gaps:
  - "Who or what sent POST /chaos/enable and POST /chaos/disable is outside the investigator's surface (the operator surface is not probeable and the log carries only client 127.0.0.1 ports); the change is attributed to the flag, not to an actor."
  - "The log begins at the process startup line (16:48:17.131Z) and there are no rotated backups, so any noise before this process start is unobservable; the only noise visible is the 16:48:21–16:48:27Z chaos window."
  - "Before the chaos window, only GET /products/1 has a logged success; GET /products/2 and POST /orders have no pre-window sample, so 'same input succeeded before' is shown for /products/1 only (both succeed after the window: E8, E9, E16, E17)."
  - "The three failed requests are unstamped (non-konan) traffic; whether they were real users or eval-harness traffic cannot be told apart from the surface."
  - "process_max_rss_bytes was flat across ~4 minutes only; long-term memory trend is not observable in this process lifetime."
usage:
  model: claude-fable-5
  tokens: 1074036
  wall_clock_seconds: 251
---

# Routine handover check: past 6-second chaos window, nothing wrong now

## Summary

**Verdict: no active incident.** The shop service is healthy at conclusion time: health 200, `faultline_chaos_enabled 0`, no exception counters, all business routes (`/products`, `/products/{id}`, `/orders`) answering 200 in under 2 ms, one process with monotonic uptime (305 s at 16:53:22Z) and flat RSS. The "noise earlier" is fully explained: at 16:48:21.418Z chaos mode was enabled through the operator surface (`failure_rate 0.6`, `error_status 503`, no extra latency), and at 16:48:27.791Z it was disabled. Inside that 6.4 s window, three of five non-investigator requests received an injected 503 — `GET /products/2`, `GET /products/1`, `POST /orders` — each tagged `chaos_failure` with the same request id as its access line. Those three are the only non-2xx responses in the whole log. The same routes succeed before (where sampled), after, and now. Confidence is high; the evidence is deterministic (explicit flag markers with tagged failures), not statistical. Impact: three failed requests over ~6 s, including one lost order attempt; the follow-up order at 16:48:49Z succeeded.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 16:48:17.132 | Process start, `faultline 0.1.0 started` (only startup event) | E1 |
| 16:48:19.354 | `GET /products/1 -> 200` (pre-window success) | E2 |
| 16:48:21.418 | **Config change:** `chaos mode enabled`, failure_rate 0.6, error_status 503 | E3 |
| 16:48:23.541 | `GET /products/2 -> 503`, `chaos_failure` | E4 |
| 16:48:24.601 | `GET /products/1 -> 503`, `chaos_failure` | E5 |
| 16:48:25.665 | `POST /orders -> 503`, `chaos_failure` | E6 |
| 16:48:27.791 | **Config change:** `chaos mode disabled` | E7 |
| 16:48:48.909 | `GET /products/1 -> 200` (post-window success) | E8 |
| 16:48:49.967 | `order created` order_id 1, `POST /orders -> 201` | E9 |
| 16:49:00 | Complaint raised (`startsAt`) | — |
| 16:49:11 | Investigation start (trigger latency 11 s) | — |
| 16:49:22 | Baseline: health ok, chaos gauge 0, no exceptions | E10, E12, E13, E14 |
| 16:50:15–16:50:33 | Triage probes: /products/1, /products/2, /orders all 200; uptime monotonic; RSS flat | E15–E18 |
| 16:53:22 | Final snapshot: chaos gauge 0, uptime 305 s, RSS unchanged | E21 |

## Investigation

Complaint object (verbatim, as synthesized by the `/konan` adapter):

```json
{
  "source": "human",
  "fingerprint": "human-1787590140",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-08-24T16:49:00Z"
}
```

Investigation start: 2026-08-24T16:49:11Z (trigger latency 11 s). No severity was stated, so none was recorded.

- **Baseline (16:49:22Z):** `/health` 200 with uptime 65 s; `/metrics` snapshot; full read of `lab/logs/app.log` (29 lines, covering the whole process lifetime). The baseline already showed the closed chaos window and three tagged 503s.
- **Triage (one round, three lenses in parallel, blind to each other):** infra-process — no anomalies (one startup, monotonic uptime and counters, flat RSS, all durations under 16 ms). interfaces — one past, closed episode: config-change marker followed by probabilistic 503s (3 of 5 requests, matching `failure_rate 0.6`), flag off now, fresh probes 200. software-defect — no anomalies (no exception events, no exception counter series, previously failing inputs return 200 on read-only reproduction); one latent metrics-label observation.
- **Deep-dive:** skipped. H1's triage evidence was already deterministic and complete; H2 and H3 were killed by triage evidence.
- **Judge (fresh, evidence-only):** H1 validated; H2 invalidated; H3 invalidated for the observed span. The judge named one closing check — a full-log count of all non-2xx access lines paired with `chaos_failure` lines — which was run (E20: exactly 3 non-2xx, 3 `chaos_failure`, 0 exception events). The judge's over-claim notes were folded into the wording and the gaps: "same inputs succeed before" holds only for `/products/1`; E18 is a GET on `/orders`, not the write path; the three failed requests are non-investigator traffic, not necessarily end users.

## Hypotheses

### H1 — chaos-mode configuration window caused the earlier noise (validated, interfaces)

The `chaos_enabled` marker (E3) precedes the first failure by 2.1 s; all three failures (E4, E5, E6) carry `chaos_failure` with the same request id as their 503 access lines and sit inside the window closed by E7. Counters agree: one 503 per failing path and one call each to `/chaos/enable` and `/chaos/disable` (E11). The full-log count (E20) shows these three are the only non-2xx responses in the file. The flag reads 0 at baseline and at conclusion (E10, E21). The same routes succeed before (E2, for `/products/1`), after (E8, E9), and under current probes (E16, E17, E18). Nothing argues against it.

### H2 — software defect causing 5xx (invalidated, software-defect)

No `unhandled_exception` or `simulated_exception` events exist (E20) and `http_exceptions_total` has no series (E12). Failure is not deterministic per input: `/products/1` returns 200 before, after, and now (E2, E8, E16); `/products/2` returns 200 now (E17) and is orderable (E9). Every 5xx has a competing, explicit cause (E4–E6).

### H3 — process crash/restart or resource/latency degradation (invalidated, infra-process)

One startup event (E1); uptime is monotonic and consistent with the log start (E13, E14, E15, E21); counters did not reset; RSS is identical across ~4 minutes (E14, E15, E21); the largest request duration in the file is the 15 ms cold-start health check (E19) and every other request is under 3 ms; the chaos window injected no latency (`extra_latency_ms 0`, E3).

### Latent finding — inconsistent metric path labels

Chaos-failed requests are counted under raw paths (`path="/products/1"`, `path="/products/2"`) while successes use the template `path="/products/{product_id}"` (E11). Not user-impacting, but it makes per-route error rates from `/metrics` unreliable and inflates label cardinality.

## Safe next steps

- Confirm on the operator side who ran `POST /chaos/enable` at 16:48:21Z and `POST /chaos/disable` at 16:48:27Z (a drill, a test, or an eval scenario) — read the operator audit trail, not the service.
- If the reporter's "noise earlier" refers to a time before 16:48:17Z, ask them for the time; the current log cannot see before that process start.
- Watch `faultline_chaos_enabled` on the dashboard during the handover; a non-zero value is the signal that the window re-opened.
- Note the label-shape quirk for whoever owns the metrics code; it is an observation, not an incident.

## Gaps

- The actor behind the chaos flag change is not visible from the investigator's surface; the log shows only `127.0.0.1` client ports.
- The log has no history before the process start at 16:48:17.131Z and no rotated backups; earlier noise, if any, is unobservable here.
- Pre-window success is sampled only for `GET /products/1`; `GET /products/2` and `POST /orders` have no pre-window request in the log (both succeed after the window).
- The three failed requests are unstamped, non-investigator traffic; whether real users or harness traffic cannot be distinguished from the surface.
- RSS was observed flat for about four minutes only; longer memory trends are not observable in this process lifetime.
