---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-latency-chaos-flag
  trigger: "manual (human report via /konan; source=human, fingerprint=human-1787077781)"
  complaint: |-
    {"source": "human", "fingerprint": "human-1787077781", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."}, "startsAt": "2026-08-18T18:29:41Z"}
  started: "2026-08-18T18:29:41Z"
  concluded: "2026-08-18T18:37:26Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An unstamped POST /chaos/enable at 2026-08-18T18:29:24.068Z turned on faultline's chaos mode (extra_latency_ms=1500, failure_rate=0.0), injecting variable extra latency into /products, /products/{id}, and /orders while leaving /health untouched and producing zero errors."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled via an unstamped POST /chaos/enable at 2026-08-18T18:29:24.068Z (failure_rate=0.0, error_status=503, extra_latency_ms=1500), injecting variable extra latency into /products, /products/{id}, and /orders — observed 67-1463ms, upper-bounded by the 1500ms cap — while /health stayed fast (sub-3ms) throughout, including inside the same ~4 s window as a 541ms /products call more than five minutes after onset, and zero exceptions or 5xx were ever recorded."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "Process-level trouble — a restart, crash loop, or resource saturation — explains the shop-wide slowness rather than a config change."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E7, E8]
  - id: H3
    statement: "The slowness is a data-dependent software defect in one code path (an expensive computation gated by a specific product or order id) rather than a uniform injected effect."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E8]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1787077848-17273 (2026-08-18T18:30:48Z, baseline)"
    quote: |-
      {"status":"ok","uptime_seconds":90.1761843750719}
      -- HTTP 200 in 0.002999s request_id=konan-1787077848-17273
  - id: E2
    type: metric
    source: "/metrics @ request_id konan-1787077850-17280 (2026-08-18T18:30:50Z, baseline scrape)"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.013603667030110955
      http_request_duration_seconds_count{method="GET",path="/health"} 3
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 1.6866719571407884
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 3
      faultline_chaos_enabled 1
      process_uptime_seconds 92.47701941709965
      process_max_rss_bytes 48054272
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:29:17.911Z — the only startup marker in the file's full history"
    quote: |-
      {"ts": "2026-08-18T18:29:17.911Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:29:21.013Z — last request before the chaos-enable marker"
    quote: |-
      {"ts": "2026-08-18T18:29:21.013Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "6d8e582fc3b2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.962, "client": "127.0.0.1:49764"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:29:24.068Z-.069Z — the chaos-enable event and its own access line, same request_id, client-originated (not konan-stamped)"
    quote: |-
      {"ts": "2026-08-18T18:29:24.068Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "57ee29738398", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
      {"ts": "2026-08-18T18:29:24.069Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "57ee29738398", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.517, "client": "127.0.0.1:49765"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:29:26.198Z-18:29:35.393Z — six business-route requests immediately following the chaos-enable marker, spread across /products, /products/2, /products/1, and /orders, all HTTP 2xx"
    quote: |-
      {"ts": "2026-08-18T18:29:26.198Z", "message": "GET /products -> 200", "path": "/products", "status": 200, "duration_ms": 67.789}
      {"ts": "2026-08-18T18:29:27.484Z", "message": "GET /products/2 -> 200", "path": "/products/2", "status": 200, "duration_ms": 222.249}
      {"ts": "2026-08-18T18:29:30.014Z", "message": "GET /products/1 -> 200", "path": "/products/1", "status": 200, "duration_ms": 1463.412}
      {"ts": "2026-08-18T18:29:32.025Z", "message": "POST /orders -> 201", "path": "/orders", "status": 201, "duration_ms": 950.494}
      {"ts": "2026-08-18T18:29:33.931Z", "message": "GET /products -> 200", "path": "/products", "status": 200, "duration_ms": 841.89}
      {"ts": "2026-08-18T18:29:35.393Z", "message": "GET /orders -> 200", "path": "/orders", "status": 200, "duration_ms": 393.082}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:34:44.712Z-18:34:49.071Z — konan-stamped health/products/health bracket, 5+ minutes after onset"
    quote: |-
      {"ts": "2026-08-18T18:34:44.712Z", "message": "GET /health -> 200", "request_id": "konan-1787078084-17415", "path": "/health", "status": 200, "duration_ms": 0.446}
      {"ts": "2026-08-18T18:34:46.805Z", "message": "GET /products -> 200", "request_id": "konan-1787078086-17421", "path": "/products", "status": 200, "duration_ms": 541.428}
      {"ts": "2026-08-18T18:34:49.071Z", "message": "GET /health -> 200", "request_id": "konan-1787078089-17427", "path": "/health", "status": 200, "duration_ms": 0.438}
  - id: E8
    type: metric
    source: "/metrics @ request_id konan-1787078100-17441 (2026-08-18T18:35:00Z, refreshed scrape)"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.014487250242382288
      http_request_duration_seconds_count{method="GET",path="/health"} 5
      http_request_duration_seconds_sum{method="GET",path="/products"} 1.4523599580861628
      http_request_duration_seconds_count{method="GET",path="/products"} 4
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 1
      process_uptime_seconds 342.7742808749899
      process_max_rss_bytes 48054272
gaps:
  - "Who or what issued the unstamped POST /chaos/enable at 18:29:24.068Z cannot be determined from telemetry — client 127.0.0.1:49765 and request_id 57ee29738398 confirm it wasn't investigator traffic, but attribution beyond that is operator surface, outside the read-only contract (docs/lab.md)."
  - "Post-onset business-route sampling is thin (4 GET /products, 1 each of several other route/id combinations) — enough to confirm the injected-latency pattern and its upper bound, but not enough to characterize the exact latency distribution (fixed jitter window vs. some other shape)."
  - "Health/business brackets (E7) were sampled sequentially, not as truly overlapping in-flight requests; true concurrency wasn't demonstrated, though the population-level duration aggregates (E2, E8) show the same selective pattern holds across the whole incident window."
  - "No log rotation backups (.1-.3) exist yet — the process started this session, so the reviewed app.log (25 lines) is its complete history; nothing predates it to compare against."
usage:
  model: claude-sonnet-5
  tokens: 2997684
  wall_clock_seconds: 465
---

# Shop-wide latency: chaos mode injected extra latency into every business route

## Summary

Verdict: **root-cause-identified**. The complaint — "every page got painfully slow,
nothing errors out, health checks are green and fast" — is confirmed as real,
ongoing impact with a clean mechanism. At 2026-08-18T18:29:24.068Z an unstamped
`POST /chaos/enable` turned on faultline's chaos mode with `extra_latency_ms: 1500`
and `failure_rate: 0.0` (E5). Every business-route request after that instant —
`/products`, `/products/{id}`, `/orders` — shows sharply elevated duration (67ms to
1463ms, still climbing at 541ms more than five minutes later), while `/health`
stayed fast throughout, including inside the same ~4-second window as one of those
slow calls (E7). No exception was ever logged and no request returned a non-2xx
status (E6, E8) — exactly "nothing errors out, it just takes forever." Confidence:
high — three independent lenses converged on the same event, and an adversarial
judge's objections (no health sample inside the incident window; latencies below
the stated 1500ms parameter) were both closed with fresh, targeted probes (E7, E8)
rather than argued away.

## Timeline

- 2026-08-18T18:29:17.911Z — current faultline process starts (E3); the only
  startup marker in the log's full history.
- 2026-08-18T18:29:18Z-18:29:21Z — early traffic is fast (1-12ms; E4's 1.962ms
  `POST /orders` is the last sample before the change).
- **2026-08-18T18:29:24.068Z — chaos mode enabled: `failure_rate: 0.0,
  error_status: 503, extra_latency_ms: 1500`, by an unstamped client, not the
  investigator (E5).**
- 2026-08-18T18:29:26.198Z-18:29:35.393Z — six business-route requests across four
  distinct routes/ids all land elevated (67-1463ms) and all still 2xx (E6) — sharp
  onset, tracking the marker directly.
- 2026-08-18T18:29:41Z — complaint reported, `/konan` invoked (trigger latency ~0s
  — the human report and the investigation start are the same instant).
- 2026-08-18T18:30:48Z-18:30:50Z — baseline: `/health` fast (E1), `/metrics` shows
  `faultline_chaos_enabled 1` and elevated route averages (E2).
- 2026-08-18T18:34:44.712Z-18:34:49.071Z — targeted re-probe, 5+ minutes after
  onset: health fast (0.446ms) immediately before and after (0.438ms) a 541ms
  `/products` call — the pattern is still live and health is unaffected in the same
  narrow window, not just at a distance (E7).
- 2026-08-18T18:35:00Z — refreshed metrics: chaos still on, uptime continuous since
  E3's single start, zero exceptions ever recorded (E8).

## Investigation

**Baseline** (18:30:48-50Z): `/health` fast with process uptime ~90s (E1); full
metrics scrape shows `faultline_chaos_enabled 1` and business-route duration
averages already well above `/health`'s (E2); the 22-line log tail surfaced the
chaos-enable marker directly.

**Triage**: all three lenses spawned in parallel — the complaint is vague enough
that none could be excluded up front. *interfaces* found the config-change marker
and its sharp-onset match to the complaint. *infra-process* confirmed latency
climbs with zero status change, `/health` unaffected (arguing against process-wide
saturation, which would touch every path), and no restart/uptime-reset.
*software-defect* found zero exceptions ever, zero 5xx, and latency spread across
distinct routes and ids rather than isolated to one input — the opposite of a
data-dependent defect signature. All three converged on the same event; no
competing hypothesis with independent supporting evidence was raised.

**Deep-dive**: skipped by design — the triage evidence was already deterministic (a
log line stating the exact flag flip and its parameters, whose predicted effect the
surrounding request timings confirm) — per protocol this goes straight to the
judge rather than re-proving what's already settled.

**Judge, round 1**: inconclusive. Objected that (a) the sole post-onset `/health`
sample (E1) was 84s after the last logged slow request, not inside the incident
window, and (b) observed durations (67-1463ms) don't match a flat reading of
`extra_latency_ms: 1500`. Both are fair — the settling evidence didn't exist yet.

**Targeted round 2**: fetched a health/business/health bracket within a 4.4s span,
5+ minutes into the incident (E7), and a refreshed metrics scrape (E8). Revised the
hypothesis wording from "bounded near the cap" to "upper-bounded by the cap" to
stop overclaiming a clustering the data doesn't show.

**Judge, round 2**: validated. The bracket adequately closes the sampling gap
(population-level aggregates in E2/E8 corroborate the same selective pattern), the
corrected wording no longer overclaims, and route-selectivity under identical
investigator-probe load argues against an investigator-side artifact rather than
for one.

**Probe accounting**: investigator traffic this round — three `/health`, two
`/metrics`, one `/products`, all `konan-`stamped (E1, E7, E8). None of the six
originally-reported slow requests (E6) carry a `konan-` prefix — the reported user
impact is not investigator-induced.

## Hypotheses

### H1 — validated (root cause): chaos-flag latency injection

The marker names its own parameters (E5); the observed post-marker durations
(E6) all fall under its 1500ms cap with zero failures, matching `failure_rate: 0.0`
exactly; `/health` — a route chaos mode does not appear to touch — stays sub-3ms
even bracketed tightly around a 541ms business-route call five minutes later (E7);
and the effect is still live at the close of the investigation (E8). This is a
closed, reconciling chain, not a loose correlation.

### H2 — invalidated: process-level trouble

A restart, crash loop, or resource exhaustion would be expected to touch every
route, including `/health` — it doesn't (E7). Uptime is continuous from the single
startup marker (E3) through both metrics scrapes, growing from ~92s to ~343s with
no reset (E2, E8) — the elapsed wall-clock matches, ruling out a hidden restart.

### H3 — invalidated: data-dependent software defect

`http_exceptions_total` carries zero data series at both scrapes (E2 baseline
implicitly, confirmed explicitly at E8) — no exception has ever been logged on this
process. The slowness spans four distinct routes/ids (`/products`, `/products/2`,
`/products/1`, `/orders` — E6), not one poisoned input, which is the opposite of
the data-dependent signature this class predicts.

## Safe next steps

- Re-run `scripts/probe.sh /metrics` periodically to watch `faultline_chaos_enabled`
  and route duration averages — the incident is confirmed still active as of this
  journal's close.
- If chaos mode is expected to be toggled only by the eval harness's
  `scripts/scenario.sh`, review who/what issued the 18:29:24.068Z toggle
  (attribution is outside this investigation's read-only surface — see Gaps).
- No code or configuration change is indicated for faultline itself — this is
  confirmed as configuration-injected latency, not a defect to fix in application
  code.

## Gaps

- The unstamped `POST /chaos/enable` caller's identity is outside the read-only
  surface: confirmed not investigator traffic (client port and request id), but no
  further attribution is possible from `docs/lab.md`'s telemetry.
- Post-onset sampling density is modest (4 `/products` samples, 1 each on several
  other route/id pairs) — sufficient to confirm the injected-latency pattern and
  its upper bound, not to characterize the exact distribution shape.
- The health/business bracket (E7) is sequential probing, not demonstrated
  concurrent in-flight overlap; mitigated by population-level aggregates (E2, E8)
  showing the same pattern across the full window.
- No log rotation backups exist — the reviewed `app.log` is the process's complete
  history since its one startup marker (E3); there is nothing earlier to check.
