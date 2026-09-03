---
konan_journal: 1
investigation:
  id: 2026-08-24-handover-chaos-window
  trigger: "manual (/konan, profile human). Complaint object: {source: human, fingerprint: human-1787590581, labels: {alertname: human-report}, annotations.summary: as below, startsAt: 2026-08-24T16:56:21Z}. Investigation start 2026-08-24T16:56:43Z; trigger latency 22 s."
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: "2026-08-24T16:56:43Z"
  concluded: "2026-08-24T17:00:31Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The earlier noise was an operator-initiated chaos injection (runtime configuration change): from 16:55:43.582Z to 16:55:49.962Z the service returned 503 on a configured 60% of requests; three user requests failed (GET /products, GET /products/1, POST /orders); the window was closed by an explicit chaos_disabled marker."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E10, E12]
    evidence_against: []
  - id: H2
    statement: "A defect or degradation in the shop service is active now (after 16:55:49.962Z): business routes fail or throw."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E20]
  - id: H3
    statement: "The process is unstable (crash/restart loop or resource exhaustion) and the earlier noise was a restart."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E17, E18, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:43.582Z"
    quote: "{\"ts\": \"2026-08-24T16:55:43.582Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"22d16bbc1f4e\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:44.646Z"
    quote: "{\"ts\": \"2026-08-24T16:55:44.646Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"b81320fd8257\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:44.646Z"
    quote: "{\"ts\": \"2026-08-24T16:55:44.646Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 503\", \"request_id\": \"b81320fd8257\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.299, \"client\": \"127.0.0.1:62897\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:46.773Z"
    quote: "{\"ts\": \"2026-08-24T16:55:46.773Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"e20e5623eabb\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} / {\"ts\": \"2026-08-24T16:55:46.773Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 503\", \"request_id\": \"e20e5623eabb\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.268, \"client\": \"127.0.0.1:62899\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:47.837Z"
    quote: "{\"ts\": \"2026-08-24T16:55:47.837Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"7a20d3068781\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"} / {\"ts\": \"2026-08-24T16:55:47.837Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 503\", \"request_id\": \"7a20d3068781\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.294, \"client\": \"127.0.0.1:62900\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:48.901Z"
    quote: "{\"ts\": \"2026-08-24T16:55:48.901Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"a222bb86af2c\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 0.848, \"client\": \"127.0.0.1:62901\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:49.962Z"
    quote: "{\"ts\": \"2026-08-24T16:55:49.962Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"00d7f3f3fa67\", \"event\": \"chaos_disabled\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:56:12.153Z"
    quote: "{\"ts\": \"2026-08-24T16:56:12.153Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"152731c1ee4f\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 2, \"quantity\": 1, \"total_price\": 23.0} / {\"ts\": \"2026-08-24T16:56:12.154Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"152731c1ee4f\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.721, \"client\": \"127.0.0.1:62907\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:56:11.088Z"
    quote: "{\"ts\": \"2026-08-24T16:56:11.088Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"b339ea530829\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.803, \"client\": \"127.0.0.1:62906\"}"
  - id: E10
    type: metric
    source: "/metrics request_id=konan-1787590695-26863 (second scrape, ~16:58:15Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E11
    type: metric
    source: "/metrics request_id=konan-1787590695-26863 (second scrape, ~16:58:15Z)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n# HELP faultline_chaos_enabled Whether chaos mode is active."
  - id: E12
    type: metric
    source: "/metrics request_id=konan-1787590603-26803 (16:56:43Z) and request_id=konan-1787590695-26863 (~16:58:15Z) — identical values in both scrapes"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
  - id: E13
    type: probe
    source: "/health request_id=konan-1787590603-26797"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":63.40398379205726}\n-- HTTP 200 in 0.002064s request_id=konan-1787590603-26797"
  - id: E14
    type: probe
    source: "/products request_id=konan-1787590694-26845"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":120},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]\n-- HTTP 200 in 0.003728s request_id=konan-1787590694-26845"
  - id: E15
    type: probe
    source: "/products/1 request_id=konan-1787590694-26851"
    quote: "{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":120,\"units_ordered\":0,\"turnover_score\":0.0}\n-- HTTP 200 in 0.001582s request_id=konan-1787590694-26851"
  - id: E16
    type: probe
    source: "/orders request_id=konan-1787590695-26857"
    quote: "[{\"id\":1,\"product_id\":2,\"quantity\":1,\"total_price\":23.0,\"created_at\":\"2026-08-24T16:56:12.153+00:00\"}]\n-- HTTP 200 in 0.001343s request_id=konan-1787590695-26857"
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-08-24T16:55:39.695Z (line 3 of 29; the only startup event in the file)"
    quote: "{\"ts\": \"2026-08-24T16:55:39.695Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E18
    type: metric
    source: "/metrics request_id=konan-1787590603-26803 (16:56:43Z) then request_id=konan-1787590695-26863 (~16:58:15Z)"
    quote: "process_uptime_seconds 64.01024591713212 / process_uptime_seconds 155.90732645918615 / process_max_rss_bytes 46841856 (both scrapes)"
  - id: E19
    type: log
    source: "lab/logs/ directory listing at 16:56:43Z"
    quote: "app.log (7095 bytes, 29 lines); no .1–.3 rotated backups present"
  - id: E20
    type: metric
    source: "/metrics request_id=konan-1787590695-26863 (~16:58:15Z) — complete http_requests_total series list"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/metrics\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 4\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 5\nhttp_requests_total{method=\"POST\",path=\"/chaos/disable\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
gaps:
  - "Nothing before 2026-08-24T16:55:39.695Z is visible: the log file begins at that startup line and no rotated backups exist (E19). Whether that start was a first start or a restart after an earlier exit cannot be determined from the surface; any 'noise' before 16:55:39Z is out of reach."
  - "The actor behind the chaos toggle (request_id 22d16bbc1f4e / 00d7f3f3fa67) is not named in telemetry; 'operator-initiated' rests on the surface contract's rule that /chaos is operator/eval surface and on the absence of a konan- prefix."
  - "The three triage lens subagents had their live scripts/probe.sh calls denied by the permission layer (they stopped, per the rule; no retries). Their findings rest on the full log read plus the orchestrator's baseline; the orchestrator's own probes (E13–E16, E18, E20) supply the live current-state check."
  - "No load-saturation, third-party, or data-db lens exists in this skill; those classes were covered only indirectly (flat RSS, sub-2 ms durations, no exceptions) and not by a dedicated lens."
usage:
  model: claude-fable-5
  tokens: 1111676
  wall_clock_seconds: 228
---

# Handover check: no active incident; earlier noise was a closed 6-second chaos window

## Summary

**Verdict: no active incident.** The shop service is healthy right now: `/health`, `/products`, `/products/1`, and `/orders` all return 200 (E13–E16), no unhandled exception has ever been counted (E11), chaos mode is off (E10), and the process has run continuously since 16:55:39Z (E17, E18). The "noise earlier" is fully explained: an operator-class request enabled chaos mode at 16:55:43.582Z with `failure_rate 0.6, error_status 503` (E1), three user requests received 503 in the next four seconds — GET /products, GET /products/1, POST /orders (E2–E5) — and a second operator-class request disabled it at 16:55:49.962Z (E7). The 503 counters have not moved since (E12, E20) and post-window user traffic succeeded, including a completed order (E8, E9). User impact: three failed requests, one of them an order attempt, inside a 6.4 s window. Confidence is high; the one open question (whether the 16:55:39Z start was itself a restart) is outside the visible surface and does not change the current-state verdict.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 16:55:39.695Z | `faultline 0.1.0 started` — only startup marker in the log | E17 |
| 16:55:43.582Z | **Config change:** `chaos_enabled`, failure_rate 0.6, error_status 503, extra_latency_ms 0 | E1 |
| 16:55:44.646Z | First failing user request: `GET /products -> 503`, paired `chaos_failure` | E2, E3 |
| 16:55:46.773Z | `GET /products/1 -> 503`, paired `chaos_failure` | E4 |
| 16:55:47.837Z | `POST /orders -> 503`, paired `chaos_failure` (a failed order attempt) | E5 |
| 16:55:48.901Z | `GET /products -> 200` inside the window (probabilistic failure, not total) | E6 |
| 16:55:49.962Z | **Config change:** `chaos_disabled` — window closes | E7 |
| 16:56:11–12Z | User traffic healthy: `GET /products/1 -> 200`, `POST /orders -> 201` (order_id 1) | E9, E8 |
| 16:56:43Z | Baseline probes: health 200, uptime 64 s, chaos 0, 503 counters = 1/1/1 | E13, E18, E12 |
| ~16:58:15Z | Business-surface probes 200; counters unchanged; uptime 156 s (no reset) | E14–E16, E20, E18 |

## Investigation

- **Baseline (16:56:43Z):** `/health` 200, `/metrics` snapshot, full log tail (29 lines). Process 64 s old, chaos gauge 0, no exception series, three 503 counters at 1 each, all inside a chaos-marker bracket.
- **Triage (one round, three lenses in parallel, each blind to the others):** infra-process, interfaces, software-defect. All three reported no current anomaly; interfaces attributed the earlier 503s to the config-change markers (E1/E7) with observed failure fraction 3/5 in the window vs configured 0.6; software-defect confirmed no exception, no `stack`, no data-dependent shape (same input `/products/1` succeeded before and after, `/products` succeeded inside the window); infra-process confirmed one startup, no uptime reset, flat RSS, sub-2 ms durations. The lenses' live probes were denied by the permission layer; they stopped as instructed.
- **Deep-dive:** none spawned. Triage evidence was deterministic and complete; the orchestrator ran the business-surface check directly (E14–E16, E20) to close the healthy-monitoring trap.
- **Judge:** H1 validated; H2 invalidated; H3 invalidated for the current state. The judge asked for the complete `http_requests_total` status list to close H2 without a gap — added as E20 (only 200/201/503 series exist; the 503s are the three chaos-window requests).

## Hypotheses

### H1 — operator-initiated chaos injection explains the earlier noise (validated)

For: E1 and E7 bracket a 6.38 s window with `failure_rate 0.6, error_status 503`; E2–E5 show three non-investigator requests each carrying a `chaos_failure` event and a 503 with sub-millisecond `duration_ms`; E6 shows a 200 inside the window, consistent with a partial rate; E12/E20 show exactly three 503 series at count 1, unchanged across two scrapes; E10 shows chaos off now. Against: none. Caveat from the judge: the log names no actor; "operator" follows from the surface contract (`/chaos` is operator/eval surface) and the request ids lacking the `konan-` prefix.

### H2 — an active defect or degradation right now (invalidated)

For: none. Against: post-window user traffic succeeded (E8 order created, E9), investigator probes on every business route returned 200 (E13–E16), no exception counter ever incremented (E11), the only non-2xx series are the three chaos-window 503s (E20), and those counters did not move between scrapes (E12).

### H3 — process instability / the noise was a restart (invalidated)

For: none. Against: one startup marker (E17); uptime 64.0 s → 155.9 s across a 92 s gap, so no reset (E18); RSS flat at 46.8 MB (E18); health 200 (E13); the 503s were served by a live process with durations, not connection refusals (E3–E5). Not disprovable from the surface: whether the 16:55:39Z start followed an earlier exit (see Gaps).

## Safe next steps

- If a handover note is required, record: closed chaos window 16:55:43.582Z–16:55:49.962Z, three user requests affected (two product reads, one order POST), no action needed on the service.
- Ask the operator/eval side whether the chaos toggle at 16:55:43Z (request_id `22d16bbc1f4e`) was intentional, to name the actor the log does not.
- Ask whether the process start at 16:55:39Z was a fresh start or a restart, if any earlier noise needs explaining.
- Optional read-only follow-up: `scripts/probe.sh /products/4` — the catalog serves `"price": null` for product 4 (E14). No failure was observed from it in this investigation; this is an observation, not a finding.

## Gaps

1. **Pre-16:55:39Z is invisible.** The log starts at the startup line and no rotated backups exist (E19). A restart before that time, and any noise before it, cannot be checked from the surface.
2. **Actor of the chaos toggle unnamed.** Telemetry shows the requests, not who sent them.
3. **Lens subagents could not probe live.** Their `scripts/probe.sh` calls were denied and, per the rule, not retried; the live current-state evidence comes from the orchestrator's own probes.
4. **No dedicated lens for load-saturation, third-party, or data-db.** These classes were covered only by the indirect signals noted (flat RSS, low durations, no exceptions, no dependency errors in the log).
