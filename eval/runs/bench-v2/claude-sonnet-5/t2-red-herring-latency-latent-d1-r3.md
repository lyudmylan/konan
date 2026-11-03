---
konan_journal: 2
investigation:
  id: 2026-11-02-chaos-latency-slowdown
  trigger: "manual (human report via /konan, fingerprint human-1793655550)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-02T21:39:14Z
  concluded: 2026-11-02T21:51:13Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A chaos toggle injecting 1500ms of extra latency into faultline's business routes (/products, /products/{id}, /orders) was switched on via POST /chaos/enable at 21:38:54.043Z, making the shop painfully slow while /health and /metrics — outside the injected path — stayed fast."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos/latency-injection toggle (extra_latency_ms=1500, failure_rate=0.0) was switched on and added roughly 0.5-1.3s to business-route requests (/products, /products/{id}, /orders), producing shop-wide slowness while /health and /metrics stayed fast and no errors were generated."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "The reported 'error page once' was produced by the same chaos toggle's configured error-injection path (error_status=503) actually firing, i.e. failure_rate was nonzero at some point in the complaint window."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E11, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:38:54.043Z"
    quote: '{"ts": "2026-11-02T21:38:54.043Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "5842755f8fe3", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:38:48.863Z"
    quote: '{"ts": "2026-11-02T21:38:48.863Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "ca44096b8ca7", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.298, "client": "127.0.0.1:61499"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:38:49.919Z"
    quote: '{"ts": "2026-11-02T21:38:49.919Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "ca2517d1d833", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.991, "client": "127.0.0.1:61500"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:38:50.977Z"
    quote: '{"ts": "2026-11-02T21:38:50.977Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "505fff669fa4", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.936, "client": "127.0.0.1:61502"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:38:56.683Z"
    quote: '{"ts": "2026-11-02T21:38:56.683Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "15fbf521596e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 582.747, "client": "127.0.0.1:61504"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:38:59.068Z"
    quote: '{"ts": "2026-11-02T21:38:59.068Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "3f62759f12bf", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1322.897, "client": "127.0.0.1:61505"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:39:01.014Z"
    quote: '{"ts": "2026-11-02T21:39:01.014Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "113670415c8e", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 884.354, "client": "127.0.0.1:61506"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:39:02.701Z"
    quote: '{"ts": "2026-11-02T21:39:02.701Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "4dc1e5aa7a70", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 620.215, "client": "127.0.0.1:61508"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:39:04.338Z"
    quote: '{"ts": "2026-11-02T21:39:04.338Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "a5ebac4d1462", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 572.434, "client": "127.0.0.1:61509"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:40:00.046Z"
    quote: '{"ts": "2026-11-02T21:40:00.046Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793655600-6961", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.919, "client": "127.0.0.1:61529"}'
  - id: E11
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-02T21:40:04Z, request_id konan-1793655604-6972"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 1
      process_uptime_seconds 76.35132545791566
      process_max_rss_bytes 47300608
  - id: E12
    type: probe
    source: "scripts/probe.sh /products/1 (run during triage, later timestamp), request_id konan-1793655845-7176"
    quote: "-- HTTP 200 in 1.490688s request_id=konan-1793655845-7176"
  - id: E13
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-02T21:43:10Z (approx), request_id konan-1793656190-7275"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/metrics",status="200"} 5
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 1
      process_uptime_seconds 662.3446042919531
      process_max_rss_bytes 47300608
      -- HTTP 200 in 0.003720s request_id=konan-1793656190-7275
gaps:
  - "No corroborating server-side evidence (non-2xx status, exception, or chaos_failure event) was found for the complaint's 'saw an error page once' detail, despite reading the full process log (one continuous file since process startup, no rotated backups) and reconfirming with two /metrics snapshots ~10 minutes apart (E11, E13). If the error page was a client-side timeout render rather than a server response, this surface cannot see it."
  - "The investigator's surface (docs/lab.md) does not expose who or what called POST /chaos/enable — only the resulting log line (E1). Attribution of the toggle to a specific actor (operator, scenario script, or otherwise) is out of reach from telemetry alone."
  - "The service's only startup marker is at 2026-11-02T21:38:47.880Z, 22 seconds before the complaint was lodged (started: 21:39:14Z per this journal). The full observable history of the current process is captured; any state from a prior process instance, if one ever existed, is unavailable (no rotated log backups)."
usage:
  model: claude-sonnet-5
  tokens: 3150468
  wall_clock_seconds: 719
---

# Chaos latency toggle slows the shop while health stays green

## Summary

**Root cause identified.** At 21:38:54.043Z faultline's internal chaos toggle was switched on
with `extra_latency_ms=1500` and `failure_rate=0.0` (E1). Within 2.6 seconds, every probed
business route — `/products`, `/products/{id}`, `/orders` — went from sub-2ms responses (E2-E4)
to 572-1323ms responses (E5-E9), a jump that lines up exactly with the complaint's "whole shop
got painfully slow in the last few minutes." `/health` kept answering in under 1ms the entire
time (E10), which is why health checks stayed "green and fast" even as the business surface
degraded — the toggle's injected delay is scoped to business routes, not the whole process.
Two `/metrics` snapshots 10 minutes apart (E11, E13) show the toggle still active, uptime
climbing continuously with no reset, and RSS unchanged — this is a standing configuration
state, not a crash, restart, or resource leak. The complaint's "error page once" detail has
no corroborating server-side evidence anywhere in the available log or metrics (zero non-2xx
statuses, zero exception samples, checked twice, ~10 minutes apart) — see Gaps. Confidence:
high for the slowdown's cause; the single error-page mention stays unexplained by this surface.

## Timeline (UTC)

- `21:38:47.880Z` — process startup (single `startup` event; no restart loop in the log).
- `21:38:48.863Z`-`21:38:50.977Z` — baseline traffic, sub-2ms responses (E2, E3, E4).
- `21:38:54.043Z` — **config-change marker**: chaos toggle enabled, `extra_latency_ms=1500`,
  `failure_rate=0.0` (E1).
- `21:38:56.683Z`-`21:39:04.338Z` — first business requests after the marker, all 572-1323ms
  (E5-E9); first slow request lands 2.6s after the marker.
- `21:39:10Z` — complaint lodged (this journal's trigger timestamp).
- `21:40:00.046Z` — `/health` probed, still 0.919ms (E10).
- `21:40:04Z` — first `/metrics` snapshot: toggle still on, uptime 76.35s (E11).
- `~21:41:45Z` (request_id `konan-1793655845-7176`) — live reproduction: `/products/1` still
  slow, 1.49s, still 200 (E12).
- `~21:43:10Z` — second `/metrics` snapshot: toggle still on, uptime 662.34s (continuous, no
  reset), RSS unchanged, `/metrics` itself still fast (E13).

## Investigation

1. **Baseline** — `/health` and `/metrics` probed; process uptime 72-76s, `faultline_chaos_enabled 1`
   already set. Log tail read in full (single file, no rotated backups).
2. **Triage** — all three lenses fanned out in parallel (complaint was too vague to exclude any):
   - `infra-process`: found the chaos toggle as a config-change event, confirmed no restart/leak
     via two independent `/metrics` probes.
   - `interfaces`: found the same toggle as a config marker with a sharp onset, confirmed the
     slowdown is route-scoped (business routes only, not `/health`/`/metrics`), flagged the
     error-page report as uncorroborated on this surface.
   - `software-defect`: read the complete log, found zero exceptions and zero non-2xx statuses;
     reproduced the slowdown live with its own probe (E12).
3. **Deep-dive skipped** — all three lenses independently converged on the same mechanism with
   live-reproduced, deterministic evidence; per the loop's rule, a hypothesis with complete
   evidence goes straight to judge rather than being re-proven.
4. **Judge** — fresh adversarial subagent, given only the hypotheses and verbatim evidence (no
   lens narrative): **H1 validated** (tight timing, targeted scope, ruled out restart/leak
   alternatives); **H2 invalidated** for the evidence's window, with one caveat about whether
   the error-page report fell inside that window.
5. **Gap closed** — the complaint's own timestamp (21:39:10Z) falls inside the single continuous
   log's coverage (process started 21:38:47.880Z, log never rotated), so the judge's residual
   concern about an earlier, unlogged process instance doesn't apply here: the full window the
   complaint could refer to is covered, and it is clean of any error signal.

## Hypotheses

### H1 — chaos latency toggle (validated)

An internal chaos/latency-injection toggle (`extra_latency_ms=1500`, `failure_rate=0.0`) was
switched on and added roughly 0.5-1.3s to business-route requests, producing shop-wide
slowness while `/health`/`/metrics` stayed fast. Evidence for: the config marker itself (E1),
the clean before/after latency split on the same routes (E2-E9), the unaffected health check
(E10), and persistence/no-restart/no-leak confirmation across two metrics snapshots and one
live reproduction 10+ minutes apart (E11, E12, E13). No evidence against. The judge's one
reservation — that the observed added latency (572-1323ms) runs under the configured
`extra_latency_ms=1500` ceiling — doesn't break the causal link; it suggests the toggle applies
latency up to a ceiling rather than a flat add, which is a detail of the mechanism, not a
competing cause.

### H2 — error page from the toggle's own error path (invalidated)

Tested whether the complaint's "error page once" came from the same toggle's configured
error-injection path (`error_status=503`) actually firing. Invalidated: the toggle's own log
line records `failure_rate: 0.0` at the moment it was set (E1), and two full-log reads plus two
`/metrics` snapshots taken ~10 minutes apart show zero non-2xx statuses and zero exception
samples throughout (E11, E13) — including across the exact window the complaint's timestamp
falls in. No second `chaos_enabled` event (reconfiguration) appears anywhere in the log, so
`failure_rate` never left 0.0.

## Safe next steps

- Re-probe `/metrics` periodically (read-only) to confirm whether `faultline_chaos_enabled`
  reverts to `0` on its own, or stays on indefinitely — this bounds how long the slowdown lasts.
- If the error-page report recurs, capture its wall-clock time immediately so a future
  investigation can correlate it against `lab/logs/app.log` while the window is still live.
- No destructive or mutating action is suggested here; toggling chaos off is operator/eval
  surface (`scripts/scenario.sh chaos-off`), out of scope for a read-only investigation.

## Gaps

- No corroborating server-side evidence (non-2xx status, exception, or `chaos_failure` event)
  was found for the "saw an error page once" detail, despite reading the full process log (one
  continuous file since startup, no rotated backups) and reconfirming with two `/metrics`
  snapshots ~10 minutes apart (E11, E13). If it was a client-side timeout render rather than a
  server response, this surface cannot see it.
- The investigator's surface (`docs/lab.md`) does not expose who or what called
  `POST /chaos/enable` — only the resulting log line (E1). Attribution to a specific actor is
  out of reach from telemetry alone.
- The service's only startup marker is at `2026-11-02T21:38:47.880Z`, 22 seconds before this
  investigation's `started` timestamp. The full observable history of the current process is
  captured; any state from a prior process instance, if one ever existed, is unavailable.
