---
konan_journal: 2
investigation:
  id: 2026-11-02-chaos-degradation-switch
  trigger: "manual (/konan adapter; complaint fingerprint human-1793644420, startsAt 2026-11-02T18:33:40Z, investigation start 2026-11-02T18:33:44Z — trigger latency 4s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: "2026-11-02T18:33:44Z"
  concluded: "2026-11-02T18:40:45Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos/degradation switch inside faultline was turned on via POST /chaos/enable (failure_rate=0.4, error_status=503), and while it stays on it injects probabilistic 503 failures on /products, /products/{id}, and /orders — the business routes — while /health keeps returning 200 because it is not instrumented by the switch, producing the reported 'fails then works on retry, dashboard stays green' pattern."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos/degradation switch inside faultline was turned on via POST /chaos/enable (failure_rate=0.4, error_status=503), and while it stays on it injects probabilistic 503 failures on /products, /products/{id}, and /orders while /health remains unaffected."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E18, E19]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:18.511Z"
    quote: |-
      {"ts": "2026-11-02T18:33:18.511Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "724a34780831", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:18.511Z"
    quote: |-
      {"ts": "2026-11-02T18:33:18.511Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "724a34780831", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.518, "client": "127.0.0.1:60184"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:22.685Z"
    quote: |-
      {"ts": "2026-11-02T18:33:22.685Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "3544f8cd070b", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:22.686Z"
    quote: |-
      {"ts": "2026-11-02T18:33:22.686Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "3544f8cd070b", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.301, "client": "127.0.0.1:60187"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:24.798Z"
    quote: |-
      {"ts": "2026-11-02T18:33:24.798Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "abb64c315a2e", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:24.798Z"
    quote: |-
      {"ts": "2026-11-02T18:33:24.798Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "abb64c315a2e", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.257, "client": "127.0.0.1:60189"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:29.024Z"
    quote: |-
      {"ts": "2026-11-02T18:33:29.024Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "0dfe8806fe7c", "event": "chaos_failure", "method": "GET", "path": "/orders"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:29.024Z"
    quote: |-
      {"ts": "2026-11-02T18:33:29.024Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "0dfe8806fe7c", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.261, "client": "127.0.0.1:60193"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:30.080Z"
    quote: |-
      {"ts": "2026-11-02T18:33:30.080Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "74fb34eae4b0", "event": "chaos_failure", "method": "GET", "path": "/products/4"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:30.080Z"
    quote: |-
      {"ts": "2026-11-02T18:33:30.080Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 503", "request_id": "74fb34eae4b0", "event": "request", "method": "GET", "path": "/products/4", "status": 503, "duration_ms": 0.272, "client": "127.0.0.1:60194"}
  - id: E11
    type: metric
    source: "probe /metrics, request_id=konan-1793644496-99440 @ 2026-11-02T18:34:56.829Z"
    quote: |-
      faultline_chaos_enabled 1
  - id: E12
    type: metric
    source: "probe /metrics, request_id=konan-1793644496-99440 @ 2026-11-02T18:34:56.829Z"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:10.520Z (only startup line in the full tail through 18:34:56.829Z)"
    quote: |-
      {"ts": "2026-11-02T18:33:10.520Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E14
    type: probe
    source: "probe /health, request_id=konan-1793644489-99431 @ 2026-11-02T18:34:49.997Z"
    quote: |-
      {"status":"ok","uptime_seconds":99.48888258403167}
      -- HTTP 200 in 0.004005s
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:33:21.629Z and 18:33:23.742-743Z — successes on routes that fail elsewhere in the window"
    quote: |-
      {"ts": "2026-11-02T18:33:21.629Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "2a97bde2f2ba", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.769, "client": "127.0.0.1:60186"}
      {"ts": "2026-11-02T18:33:23.743Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "f3131b2d90a2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.266, "client": "127.0.0.1:60188"}
  - id: E16
    type: metric
    source: "probe /metrics, request_id=konan-1793644496-99440 @ 2026-11-02T18:34:56.829Z"
    quote: |-
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="GET",path="/orders",status="503"} 1
  - id: E17
    type: probe
    source: "probe /health, request_id=konan-1793644830-99557 @ 2026-11-02T18:40:30Z (sustained-window re-sample, ~6.5 min after chaos was enabled, while faultline_chaos_enabled was still 1)"
    quote: |-
      {"status":"ok","uptime_seconds":440.3557714589406}
      -- HTTP 200 in 0.001489s
  - id: E18
    type: probe
    source: "probe /health, request_id=konan-1793644833-99563 @ 2026-11-02T18:40:33Z"
    quote: |-
      {"status":"ok","uptime_seconds":442.684706750093}
      -- HTTP 200 in 0.001353s
  - id: E19
    type: metric
    source: "probe /metrics, request_id=konan-1793644837-99568 @ 2026-11-02T18:40:37Z — closing snapshot"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 5
      faultline_chaos_enabled 1
      process_uptime_seconds 447.4710218340624
      process_max_rss_bytes 46628864
gaps:
  - "The configured failure_rate=0.4 is taken directly from the chaos_enabled event's own logged parameters (E1), not independently re-derived by statistical sampling; no large volley of extra probes was sent to empirically measure the rate, to avoid adding investigator load beyond what was needed to confirm the mechanism."
  - "The caller that invoked POST /chaos/enable is not identifiable beyond its socket address (127.0.0.1:60184, E2) — the surface contract exposes no auth/identity field on this route, so whether this was an authorized operator/scenario action or an unauthorized toggle cannot be determined from telemetry alone."
  - "Rotated log backups (lab/logs/app.log.1–.3) were not read: the live app.log already covers the full process lifetime (single startup at E13, no gap to the present), so there was no indication of missing history, but an earlier chaos-toggle event predating this process is not ruled out by this journal."
  - "Total real-user impact beyond the four observed chaos_failure events (E3/E5/E7/E9) is not separately quantified: http_requests_total is cumulative since process start and the surface contract does not expose a per-source breakdown other than the konan-* request-id convention used to exclude investigator traffic."
usage:
  model: claude-sonnet-5
  tokens: 3450833
  wall_clock_seconds: 421
---

# Intermittent shop 503s — chaos degradation switch left on

## Summary

Root cause identified. `POST /chaos/enable` was called at 18:33:18.511Z with
`failure_rate=0.4, error_status=503` (E1, E2), and the switch was still on at the
close of this investigation (E19). While it is on, faultline injects a 503 on
roughly 2 in 5 requests to the business routes — `/products`, `/products/{id}`,
`/orders` — chosen independently per request, so some loads/orders fail and an
immediate retry on the same route typically succeeds (E3–E10, E15, E16): exactly
the "fails, then works on retry" shape reported. `/health` is not instrumented by
the switch and returned 200 on every one of 5 probes spanning the whole window,
including two resamples 6.5 minutes after the toggle (E14, E17, E18, E19) —
explaining why the health dashboard stayed green throughout. No unhandled
exceptions (E12) and no restart/crash activity (E13) were found, ruling out a code
defect or process instability as competing explanations. Confidence is high: the
mechanism is read directly from the application's own structured log line, not
inferred from timing or correlation.

## Timeline

All times UTC, from telemetry.

- **18:33:10.520Z** — process start, faultline 0.1.0 (E13); the only startup event
  in the observed window.
- **18:33:11–17Z** — healthy baseline traffic: /health, /products, /products/{id}
  all 200, one order 201.
- **18:33:18.511Z** — **config-change marker**: `POST /chaos/enable` → 200, logged
  as `chaos_enabled` with `failure_rate=0.4, error_status=503, extra_latency_ms=0`
  (E1, E2). This is the onset event.
- **18:33:22.685Z** — first chaos-injected failure, `GET /products/2` → 503 (E3, E4),
  ~4.2s after the toggle.
- **18:33:24.798Z** — `GET /products` → 503 (E5, E6).
- **18:33:29.024Z** — `GET /orders` → 503 (E7, E8).
- **18:33:30.080Z** — `GET /products/4` → 503 (E9, E10).
- Interleaved with the above: successful `GET /products/1` → 200 and
  `POST /orders` → 201 on the same routes (E15) — the retry-succeeds pattern.
- **18:34:49.997Z–18:34:56.829Z** — investigation baseline: `/health` 200
  (uptime 99.5s, E14); `/metrics` shows `faultline_chaos_enabled 1` (E11), the
  mixed 200/503 counter breakdown (E16), and an empty `http_exceptions_total`
  series (E12).
- **18:40:30Z–18:40:37Z** — closing re-samples, ~6.5 minutes after the toggle:
  `/health` still 200 twice (E17, E18); `/metrics` confirms the switch is still on
  (`faultline_chaos_enabled 1`), uptime still monotonic, RSS unchanged (E19) — the
  switch has not been turned off and the process has not restarted.

## Investigation

Baseline (`/health`, `/metrics`, log tail) already surfaced the mechanism directly:
a `WARNING`-level `chaos_enabled` log line naming its own parameters, immediately
followed in the counters by a mixed 200/503 pattern on exactly the business routes.
This is the "healthy-monitoring trap" the skill warns about — `/health` green while
business traffic fails — so the business surface was checked explicitly rather than
trusting the complaint's "dashboard is green" framing.

Triage ran all three lenses in parallel (complaint was vague enough that none could
be excluded up front), blind to each other, each given only the lens file, the
surface contract, the complaint verbatim, and the baseline snapshot. All three
converged on the same event: infra-process and interfaces lenses both independently
found the `chaos_enabled` marker and classified it `infra-process` per each lens's
own classification rule (an internal operational switch is `infra-process` even
though its symptom is gateway-shaped 503s). The software-defect lens found no
evidence in its domain — no unhandled exceptions, no data-dependent single-route/
single-input concentration — and explicitly reported no anomaly.

Selection: **no deep-dives**. The evidence is already deterministic — the failure
mechanism and its parameters (`failure_rate`, `error_status`) are stated directly
in the application's own log line, not inferred from correlation — so H1 went
straight to the judge per the skill's rule that deterministic, complete evidence
skips deep-dive.

The judge (fresh context, cited evidence only, no narrative) returned **validated**,
calling out one thin point: the "`/health` unaffected" claim rested on a single
post-enable probe. Two additional `/health` resamples were taken afterward (E17,
E18), spanning to 6.5 minutes after the toggle, both 200 — closing that gap without
needing a second investigation round.

Budget: one triage round (3 lenses), zero deep-dives of a permitted three, one
judge — concluded in round 1.

## Hypotheses

### H1 — chaos/degradation switch left on (validated)

`POST /chaos/enable` (E2) set `failure_rate=0.4, error_status=503` (E1), active for
the rest of the observed window (E11, E19). Four observed requests across three
business routes failed with a `chaos_failure` marker immediately preceding their
503 (E3–E10) — the application's own labeling of cause, not an inference from
timing. Successes interleave on the same routes (E15, E16), matching a probabilistic
rather than total failure mode. `/health` is unaffected across five probes spanning
the whole window (E14, E17, E18, E19), explaining the green dashboard. No unhandled
exceptions (E12) and a single, unchanging process lifetime (E13, E19) rule out a
code defect or an instability/restart explanation.

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Hand to the service owner: confirm whether `POST /chaos/enable` at 18:33:18Z was
  an intended operator/scenario action; if not, the switch should be turned off
  (read-only investigation cannot do this).
- Watch `faultline_chaos_enabled` and the `status="503"` series under
  `http_requests_total` on `/products`, `/products/{product_id}`, and `/orders` —
  both stay elevated as long as the switch is on.
- Because the health check does not exercise the business routes, consider (for the
  service owner, not this investigator) whether the health endpoint should also
  reflect chaos/degradation state so dashboards do not read green during this class
  of incident — noted as an observability gap, not actioned here.

## Gaps

The machine core lists four. In brief: the 0.4 failure rate is read from the log
line's own parameters, not independently measured by extra sampling (1); the
caller behind `POST /chaos/enable` cannot be identified beyond its local socket
address (2); rotated log backups were not opened, though the live log already
covers the full process lifetime with no gap (3); and total real-user impact beyond
the four observed failures is not separately quantified from the cumulative counters
(4).
