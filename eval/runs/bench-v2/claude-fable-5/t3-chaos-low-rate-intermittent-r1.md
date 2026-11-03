---
konan_journal: 2
investigation:
  id: 2026-11-03-chaos-switch-intermittent-503s
  trigger: "manual (/konan; fingerprint human-1793710012; alertname human-report; startsAt 2026-11-03T12:46:52Z; investigation start 2026-11-03T12:47:04Z; trigger latency 12s)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-03T12:47:04Z
  concluded: 2026-11-03T12:53:28Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos switch inside faultline, enabled at 2026-11-03T12:46:37.821Z with failure_rate 0.08 and error_status 503, injects probabilistic 503 failures into the shop routes while it stays on — and it is still on."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was enabled at 2026-11-03T12:46:37.821Z (failure_rate 0.08, error_status 503) and injects probabilistic 503s into /products, /products/{id}, and POST /orders; identical requests succeed moments later; the switch is still enabled."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E8, E13, E14, E16]
    evidence_against: []
  - id: H2
    statement: "The target's own code fails deterministically on specific inputs or routes (data-dependent defect or unhandled exception)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E2, E14]
  - id: H3
    statement: "The process crashed or restart-looped, and the errors come from the lifecycle event."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E12, E15]
  - id: H4
    statement: "An external dependency or a gateway tier in front of the target produces the 503s."
    incident_class: third-party
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3, E5]
latent_findings:
  - statement: "GET /products returns \"price\": null for product id 4 (Mystery Box); no request failed on it in this window."
    evidence: [E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:37.821Z"
    quote: |-
      {"ts": "2026-11-03T12:46:37.821Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "a734c6606fa5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:38.973Z"
    quote: |-
      {"ts": "2026-11-03T12:46:38.973Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e4fa7519e996", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:38.973Z"
    quote: |-
      {"ts": "2026-11-03T12:46:38.973Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "e4fa7519e996", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.145, "client": "127.0.0.1:50808"}
  - id: E4
    type: metric
    source: "/metrics @ 2026-11-03T12:47:26Z (request_id konan-1793710046-34175)"
    quote: "faultline_chaos_enabled 1"
  - id: E5
    type: metric
    source: "/metrics @ 2026-11-03T12:47:26Z (request_id konan-1793710046-34175)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 2
      http_requests_total{method="POST",path="/orders",status="503"} 2
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:39.060Z and 12:46:39.147Z"
    quote: |-
      {"ts": "2026-11-03T12:46:39.060Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "1996ad6eea54", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.124, "client": "127.0.0.1:50814"}
      {"ts": "2026-11-03T12:46:39.147Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b980be78f5d9", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.723, "client": "127.0.0.1:50820"}
  - id: E7
    type: metric
    source: "/metrics @ 2026-11-03T12:47:26Z (request_id konan-1793710046-34175); the counter carries no sample lines"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:39.118Z and 12:46:39.293Z (same input, interleaved outcomes)"
    quote: |-
      {"ts": "2026-11-03T12:46:39.118Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "7815aa260077", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.407, "client": "127.0.0.1:50818"}
      {"ts": "2026-11-03T12:46:39.293Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "0bfe3504d8d3", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.119, "client": "127.0.0.1:50830"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:32.869Z (the only startup event in the complete 55-line log; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-03T12:46:32.869Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:33.643Z and 12:46:35.766Z (clean traffic between startup and the chaos marker)"
    quote: |-
      {"ts": "2026-11-03T12:46:33.643Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "f355c2d956fb", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.428, "client": "127.0.0.1:50799"}
      {"ts": "2026-11-03T12:46:35.766Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "44d2ca114dd4", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.21, "client": "127.0.0.1:50801"}
  - id: E11
    type: probe
    source: "/products (request_id konan-1793710164-34213)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":37},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.003718s request_id=konan-1793710164-34213
  - id: E12
    type: probe
    source: "/health (request_id konan-1793710045-34170)"
    quote: |-
      {"status":"ok","uptime_seconds":53.071228249929845}
      -- HTTP 200 in 0.009570s request_id=konan-1793710045-34170
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-03T12:52:51Z (request_id konan-1793710371-34264, second scrape)"
    quote: "faultline_chaos_enabled 1"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:39.293Z"
    quote: |-
      {"ts": "2026-11-03T12:46:39.293Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "0bfe3504d8d3", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-03T12:52:51Z (request_id konan-1793710371-34264, second scrape); 503 counters unchanged vs the first scrape, uptime continuous"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 2
      http_requests_total{method="POST",path="/orders",status="503"} 2
      process_uptime_seconds 378.91661379206926
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T12:46:37.821Z"
    quote: |-
      {"ts": "2026-11-03T12:46:37.821Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "a734c6606fa5", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.418, "client": "127.0.0.1:50802"}
gaps:
  - "Operator identity is not observable from this surface: the enable call came from 127.0.0.1:50802 (E16), but which operator or script issued it lives outside the telemetry contract."
  - "Triage ran inline instead of as parallel lens subagents: the complete telemetry surface (the full 55-line log, full metrics, health, and business probes) was already captured at baseline, so each lens (infra-process, interfaces, software-defect) was applied over it in place; no telemetry remained unread."
  - "A literal retry of a failed request id is not observable; subsequent identical requests succeeding (E6, E8) stand in for the reported works-on-retry behavior."
  - "No log history exists before the process start at 12:46:32.869Z (no rotated backups); nothing in this incident required it."
usage:
  model: claude-fable-5
  tokens: 898155
  wall_clock_seconds: 384
---

# Chaos switch injects intermittent 503s across the shop

## Summary

Root cause identified. An operational chaos switch inside faultline was enabled at
2026-11-03T12:46:37.821Z with `failure_rate: 0.08` and `error_status: 503` (E1, E16).
While it is on, roughly 8% of requests on the shop routes fail with a 503; the five
failures in this window hit `GET /products`, `GET /products/5`, and `POST /orders`
(E5), and identical requests succeed moments later (E6, E8) — which matches the
reported "occasional error, works on retry". The complaint is **not** nothing: the
switch is still enabled (E13), so every new request carries the same failure chance,
including order placement. Two orders failed on first attempt in this window (E5).
Confidence is high: every 503 in the complete log is bound to a `chaos_failure`
marker by its request id (E2+E3, E14), the exception counter is empty (E7), and the
process ran continuously (E9, E12, E15). The in-loop judge validated H1 and
invalidated the three alternatives.

## Timeline

All times UTC, 2026-11-03.

- 12:46:32.869 — faultline 0.1.0 starts; the log begins here (E9).
- 12:46:33.6–12:46:35.8 — clean traffic: 200s and a 201 order (E10). Last known-good.
- 12:46:37.821 — **config-change marker**: chaos mode enabled, failure_rate 0.08,
  error_status 503, extra_latency_ms 0; `POST /chaos/enable -> 200` from
  127.0.0.1:50802 (E1, E16).
- 12:46:38.973 — first injected failure: `POST /orders -> 503`, request id
  e4fa7519e996, tagged `chaos_failure` (E2, E3). First known-bad.
- 12:46:38.987–12:46:39.293 — four more injected 503s across `/products`,
  `/products/5`, `POST /orders`; identical requests succeed in between (E5, E6, E8,
  E14). Five user-facing 503s in total.
- 12:46:52 — complaint raised (`startsAt`).
- 12:47:04 — investigation starts (trigger latency 12s).
- 12:47:25–26 — health ok, uptime 53s; gauge `faultline_chaos_enabled 1` (E12, E4).
- 12:49:24–25 — business probes `/products`, `/products/5`, `/orders` all 200 (E11).
- 12:52:51 — second scrape: gauge still 1; 503 counters unchanged, so no new user
  failures since 12:46:39 — but only because no new user traffic arrived (E13, E15).

## Investigation

The complaint object, verbatim, as synthesized by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1793710012",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-11-03T12:46:52Z"
}
```

Investigation start: 2026-11-03T12:47:04Z.

- **Baseline**: health 200 (E12), full `/metrics` scrape (E4, E5, E7), and the log —
  which at 55 lines was the complete history since startup, read whole. The baseline
  already contained the config-change marker (E1) and the five tagged failures.
- **Triage**: because the entire telemetry surface was in hand, the three lenses ran
  inline over it rather than as subagents (recorded under Gaps). Infra-process:
  chaos toggle found (E1, E4), lifecycle clean (E9, E12). Interfaces: sharp onset
  immediately after the marker, probabilistic shape (E10 before, E5/E8 after).
  Software-defect: nothing — empty exception counter (E7), no stacks, interleaved
  outcomes on the same input (E8). Four hypotheses formed.
- **Deep-dive**: skipped — the triage evidence for H1 was deterministic and complete
  (every 503 request id pairs with a `chaos_failure` event), so the hypothesis list
  went straight to the judge. Business-surface probes (E11) checked the
  healthy-monitoring trap: the surface mostly works, as the complaint says.
- **Judge** (fresh subagent, evidence-only): H1 validated; H2, H3, H4 invalidated.
  The judge asked for one reconfirmation — a fresh gauge read, since the state
  evidence was older than the newest probe — delivered as E13/E15.

## Hypotheses

### H1 — chaos switch enabled (infra-process / degradation-switch) — validated

The marker (E1) names the mechanism and its parameters; E2+E3 bind a `chaos_failure`
event and a 503 response to the same request id; E14 does the same for the last
failure; E5 shows the blast radius across three routes; E8 shows the same input
succeed and fail in interleaved order — probabilistic, exactly rate-shaped; E6 shows
the next identical request succeed; E4 and E13 show the switch on at both scrapes.
Nothing contradicts it.

### H2 — software defect — invalidated

The exception counter has no samples (E7), no stack traces appear in the log, and
the same input returns 200 and 503 interleaved (E8) — a deterministic per-input
defect cannot produce that. The failures carry an explicit injected-failure tag
(E2, E14).

### H3 — crash or restart loop — invalidated

One startup event in the complete log (E9), corroborated independently by uptime
(E12: 53s at 12:47:25 puts the start at ~12:46:32; E15: 379s at the second scrape,
continuous). All 503s fall inside a single uptime window, after six seconds of clean
traffic (E10).

### H4 — external dependency or gateway — invalidated

The target's own request logger emits the 503s with sub-millisecond durations and
loopback clients (E3), its own counters record them (E5), and its own chaos module
logs the mechanism (E1, E2). The responses originate inside the application, not in
front of it.

## Safe next steps

Read-only; remediation is out of scope for this journal.

- Watch `faultline_chaos_enabled`: while it reads 1, the injection continues and new
  traffic — including orders — keeps the ~8% failure chance.
- Re-scrape `/metrics` periodically; growth in the 503 counters from non-`konan-*`
  traffic means continuing user impact.
- Check operator-side records for who issued the enable call at 12:46:37.821Z from
  127.0.0.1:50802 — that is outside this telemetry surface.

## Gaps

- **Operator identity**: the log shows the enable request and its client address
  (E16) but not the actor; operator attribution lives outside the surface contract.
- **Inline triage**: the lens sweep ran inline over the complete captured surface
  instead of as parallel subagents. Accepted deliberately: the full log (55 lines),
  full metrics, health, and business probes were already read whole, so a subagent
  had no unread telemetry to examine. Each lens domain was still applied and is
  accounted for above.
- **Retry semantics**: the users report "works on retry"; telemetry shows subsequent
  identical requests succeeding (E6, E8), not a literal client retry of the same
  request id.
- **Pre-startup history**: no rotated log backups exist, so nothing before
  12:46:32.869Z is observable; the incident onset is well inside the window.
