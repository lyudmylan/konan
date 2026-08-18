---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-slowness-chaos-latency
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-18T20:57:34Z
  concluded: 2026-08-18T21:06:26Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was enabled with extra_latency_ms=1500 (failure_rate=0.0) at 20:57:14.657Z, injecting several hundred milliseconds to over a second of added latency into /products, /products/{id}, and /orders, while /health stayed fast because it isn't gated by the same latency-injection path — explaining both the site-wide slowness and the green, fast health checks."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode's extra_latency_ms=1500 config, enabled 20:57:14.657Z, is injecting added latency into shop routes and is still active, causing the reported slowness."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: []
  - id: H2
    statement: "The complaint's 'seeing an error page once' came from real (non-investigator) user traffic hitting the known /products/3 ZeroDivisionError defect (HTTP 500)."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E7, E8]
    evidence_against: [E9, E10, E11]
latent_findings:
  - statement: "GET /products/3 deterministically raises an unhandled ZeroDivisionError (HTTP 500) — faultline/shop.py divides by units_in_stock, which is 0 for product 3. Reproducible on demand, but every occurrence found in the log (8 total, 20:11:52Z-21:01:05Z) carries an investigator konan- request id; no organic traffic has been observed to trigger it."
    evidence: [E7, E8, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:57:14.657Z"
    quote: "{\"ts\": \"2026-08-18T20:57:14.657Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"28930dbf7474\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.0, \"error_status\": 503, \"extra_latency_ms\": 1500}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:57:11.595Z"
    quote: "{\"ts\": \"2026-08-18T20:57:11.595Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"90f0772c905d\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.795, \"client\": \"127.0.0.1:51384\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:57:22.012Z"
    quote: "{\"ts\": \"2026-08-18T20:57:22.012Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"f4de99ed36cd\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1446.612, \"client\": \"127.0.0.1:51388\"}"
  - id: E4
    type: probe
    source: "GET /health probe @ request_id konan-1787086987-25267, ~345s after E1"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":358.3349495001603} -- HTTP 200 in 0.001700s"
  - id: E5
    type: metric
    source: "/metrics probe @ request_id konan-1787086988-25273, ~345s after E1"
    quote: "faultline_chaos_enabled 1\nhttp_request_duration_seconds_sum{method=\"GET\",path=\"/products/{product_id}\"} 3.5931679990608245\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products/{product_id}\"} 4"
  - id: E6
    type: probe
    source: "GET /products probe @ request_id konan-1787087181-25319, ~527s after E1"
    quote: "-- HTTP 200 in 1.137340s request_id=konan-1787087181-25319"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:01:05.791Z"
    quote: "{\"ts\": \"2026-08-18T21:01:05.791Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787086864-25168\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 840.379, \"client\": \"127.0.0.1:51439\"}"
  - id: E8
    type: probe
    source: "GET /products probe @ request_id konan-1787087181-25319"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0}"
  - id: E9
    type: metric
    source: "/metrics probe @ request_id konan-1787086988-25273"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 1"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:05.794Z"
    quote: "{\"ts\": \"2026-08-18T20:22:05.794Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 503\", \"request_id\": \"d40f49113600\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.283, \"client\": \"127.0.0.1:51003\"}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:07.911Z"
    quote: "{\"ts\": \"2026-08-18T20:22:07.911Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"0d3ed61424da\", \"event\": \"chaos_disabled\"}"
gaps:
  - "No non-investigator (organic) traffic was found hitting /products/3 anywhere in the log, so the complaint's 'error page' sighting could not be tied to a specific request. It may reference the /products/3 latent defect, the earlier 20:07-20:22Z chaos failure_rate=0.6 cycle recalled imprecisely as 'the last few minutes', or something outside this surface's telemetry — undetermined."
  - "The lab exposes no client/session-level trace linking a specific end user to a server request id, so 'once' (singular) could not be corroborated or refuted against real traffic volume."
  - "extra_latency_ms=1500 is the configured value, but observed durations after E1 (259ms-1447ms, later 1137ms) don't cluster at a fixed 1500ms addition, suggesting jitter or partial/per-hop application. The exact injection mechanism wasn't probed further since it doesn't change the root-cause conclusion — noted as an open question, not chased."
usage:
  model: claude-sonnet-5
  tokens: 3887163
  wall_clock_seconds: 532
---

# Shop-wide slowness: chaos-injected latency, still active

## Summary

**Root cause identified.** At 2026-08-18T20:57:14.657Z, chaos mode was enabled
(`extra_latency_ms=1500`, `failure_rate=0.0`) via `POST /chaos/enable` — operator/eval
traffic, not the investigator. Immediately after, request durations on `/products`,
`/products/{id}`, and `/orders` jumped from single-digit milliseconds to 259ms-1447ms
(E2, E3), and a probe taken ~9 minutes later still showed 1.14s (E6) — the injection is
ongoing at time of writing, no `chaos_disabled` event follows E1. `/health` stayed fast
throughout (E4), which explains the complaint's "health checks are green and fast": the
health route isn't gated by the same latency path as the shop routes, so it's blind to
this class of degradation.

The complaint's second detail — "some also mention seeing an error page once" — is
**not corroborated** by telemetry from real user traffic. A known, reproducible defect
exists (`GET /products/3` throws an unhandled `ZeroDivisionError` → 500, latent_findings
below), but every single occurrence of that route in the log carries an investigator
`konan-` request id (E7, E9); no organic 5xx appears anywhere in or near the current
incident window (E10, E11 mark the last organic 5xx at 20:22:05Z, from an earlier,
already-closed, unrelated chaos cycle). This piece of the complaint is logged as
inconclusive (H2) rather than asserted.

**Impact:** ongoing, site-wide latency on product browsing, product detail, and order
routes; no availability impact (all sampled requests during the window returned 2xx).
**Confidence:** high on the latency root cause (sharp onset at an exact config marker,
before/after duration jump, still reproducing); low/unresolved on the error-page detail.

## Timeline (UTC)

- 20:57:08.704Z — current process starts (`faultline 0.1.0 started`).
- 20:57:09.451Z-20:57:11.595Z — baseline shop traffic, 0.6ms-12ms durations (E2).
- **20:57:14.657Z — `chaos_enabled`, `extra_latency_ms=1500`, `failure_rate=0.0`, via `POST /chaos/enable` (E1).**
- 20:57:17.131Z-20:57:24.913Z — shop-route durations jump to 259ms-1447ms (E3).
- 21:01:05.791Z — investigator probe of `/products/3` reproduces the pre-existing `ZeroDivisionError` → 500 (E7).
- 21:01:33Z (approx, `process_uptime_seconds` 358.3 at probe) — fresh `/health` probe still fast (1.7ms, E4); `/metrics` confirms `faultline_chaos_enabled 1` still set (E5).
- 21:06:21Z (approx) — fresh `/products` probe still slow, 1.14s (E6). No `chaos_disabled` event has appeared since E1.

Earlier, unrelated chaos cycle for context (not part of this incident): `chaos_enabled`
`failure_rate=0.6` at 20:22:01.558Z produced real 503s including E10 at 20:22:05.794Z,
closed by `chaos_disabled` at 20:22:07.911Z (E11) — over half an hour before this
incident's onset.

## Investigation

1. **Baseline** — `/health` (200, fast) and `/metrics` showed `faultline_chaos_enabled 1`
   already set and elevated per-route duration sums, prompting an immediate look at the
   log for a config-change marker.
2. **Triage** — three lenses spawned in parallel (infra-process, interfaces,
   software-defect), each given only the lens file, `docs/lab.md`, the complaint, and
   the baseline summary:
   - infra-process: confirmed injected latency on a live, undegraded process (no
     restart loop), flagged the health-endpoint blind spot.
   - interfaces: found the `chaos_enabled` config marker (E1) as a clean sharp-onset
     explanation, confirmed no `chaos_disabled` since, and independently surfaced the
     `/products/3` defect while probing.
   - software-defect: independently reproduced and root-caused the `/products/3`
     `ZeroDivisionError` (zero-stock product, unguarded division), confirmed no other
     route defect, and flagged — within its own remit — that every occurrence in the
     log carries an investigator request id.
3. Both hypotheses had deterministic, complete triage evidence (exact config-change
   timestamp with clean before/after; a defect reproduced on demand with a full stack
   trace) — per protocol, that skips deep-dive and goes straight to judge.
4. **Judge** (fresh subagent, evidence only, no narrative): validated H1 outright
   (with two flagged-but-non-blocking caveats: the observed latencies don't cluster
   at a flat 1500ms, and the before/after samples don't show a non-investigator
   request id directly, though the mechanism is process-wide middleware). Validated
   H2's hedged form — the defect is real, but the "not yet tied to organic traffic"
   qualifier holds up against the negative grep evidence (E10/E11 boundary).
5. Recast H2 in the machine core as `inconclusive` (is this defect the source of the
   complaint's error-page mention?) with the underlying defect itself split out as a
   `latent_finding`, since the judge's validation was of the hedge, not of causation.

## Hypotheses

### H1 — chaos-injected latency (validated, root cause)

Config-change marker E1 lands at an exact timestamp between four fast baseline requests
(E2 and others, 0.6ms-12ms) and five/six subsequently slow ones (E3, E6: 259ms-1447ms,
1.14s). No `chaos_disabled` follows it; a fresh probe 345s later still shows
`faultline_chaos_enabled 1` (E5) and elevated per-route duration stats; a probe 527s
later is still slow (E6). `/health` is unaffected throughout (E4), matching the
complaint's "health checks are green and fast" detail. This is the textbook
healthy-monitoring trap: a green health endpoint alongside failing/slow business
traffic.

### H2 — /products/3 defect is the reported "error page" (inconclusive)

The defect is real and deterministic: E7 shows `GET /products/3 -> 500` with a full
`ZeroDivisionError` stack trace at `faultline/shop.py`'s stock-turnover division; E8
confirms product 3 has `units_in_stock: 0`, the only such product. But E9 (exactly one
`ZeroDivisionError` in the exception counter, matching only investigator probes) and
the E10/E11 boundary (last organic 5xx anywhere in the log was 20:22:05.794Z, from an
already-closed, unrelated chaos cycle) argue against organic traffic having hit it
recently. Not enough evidence either way to confirm or rule out that a real user hit
this route in the "last few minutes" the complaint describes — left inconclusive.

## Safe next steps

- Re-probe `/health`, `/metrics`, and a sample of `/products`, `/products/{id}`, and
  `/orders` periodically (read-only) to confirm whether the chaos-injected latency
  self-resolves or requires operator action to clear.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and grep future log segments
  for non-`konan-`-prefixed `GET /products/3` hits — if one appears, it would directly
  settle H2.
- Consider extending the health check's business-surface coverage (read-only
  observation suggestion, not a fix) given the confirmed blind spot in E4/E5.

## Gaps

- No non-investigator (organic) traffic was found hitting `/products/3` anywhere in the
  log, so the complaint's "error page" sighting could not be tied to a specific
  request. It may reference the `/products/3` latent defect, the earlier
  20:07-20:22Z `failure_rate=0.6` chaos cycle recalled imprecisely as "the last few
  minutes," or something outside this surface's telemetry — undetermined.
- The lab exposes no client/session-level trace linking a specific end user to a server
  request id, so "once" (singular) could not be corroborated or refuted against real
  traffic volume.
- `extra_latency_ms=1500` is the configured value, but observed durations after E1
  (259ms-1447ms, later 1.14s) don't cluster at a flat 1500ms addition, suggesting
  jitter or partial/per-hop application. The exact injection mechanism wasn't probed
  further since it doesn't change the root-cause conclusion — noted as an open
  question, not chased.
