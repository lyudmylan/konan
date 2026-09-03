---
konan_journal: 1
investigation:
  id: 2026-08-18-chaos-mode-503s
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-18T22:26:11Z
  concluded: 2026-08-18T22:37:52Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A chaos-mode fault injector was toggled on at 22:25:47.450Z (failure_rate=0.4, error_status=503), injecting probabilistic 503s across GET and POST routes alike (product browsing, order listing, order creation); /health is not subject to this injection, so the health dashboard stayed green while business traffic failed intermittently."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos-mode fault injection (enabled 22:25:47.450Z, failure_rate=0.4, error_status=503) causes probabilistic 503 responses across both GET and POST routes and is the sole active failure mechanism; /health is not subject to it."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E6, E7, E8, E10, E11, E12, E13]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:25:47.450Z"
    quote: "{\"ts\": \"2026-08-18T22:25:47.450Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"a4a21bed2ff7\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:25:52.690Z"
    quote: "{\"ts\": \"2026-08-18T22:25:52.690Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"ad26e215a956\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:25:52.691Z"
    quote: "{\"ts\": \"2026-08-18T22:25:52.691Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 503\", \"request_id\": \"ad26e215a956\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.319, \"client\": \"127.0.0.1:52463\"}"
  - id: E4
    type: metric
    source: "GET /metrics @ 2026-08-18T22:26:38Z, request_id konan-1787091998-30570"
    quote: "faultline_chaos_enabled 1"
  - id: E5
    type: probe
    source: "GET /health, request_id konan-1787091995-30563, 2026-08-18T22:26:35Z"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":55.68754908302799} -- HTTP 200 in 0.002001s request_id=konan-1787091995-30563"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:29:00.714Z"
    quote: "{\"ts\": \"2026-08-18T22:29:00.714Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"konan-1787092140-30705\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:29:06.440Z"
    quote: "{\"ts\": \"2026-08-18T22:29:06.440Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"konan-1787092146-30738\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:29:08.614Z"
    quote: "{\"ts\": \"2026-08-18T22:29:08.614Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"konan-1787092148-30774\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/orders\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:29:09.724Z"
    quote: "{\"ts\": \"2026-08-18T22:29:09.724Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /health -> 200\", \"request_id\": \"konan-1787092149-30798\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/health\", \"status\": 200, \"duration_ms\": 0.544, \"client\": \"127.0.0.1:52534\"}"
  - id: E10
    type: metric
    source: "GET /metrics @ 2026-08-18T22:26:38Z, request_id konan-1787091998-30570"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 2"
  - id: E11
    type: metric
    source: "GET /metrics @ 2026-08-18T22:27:46Z"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E12
    type: metric
    source: "GET /metrics @ 2026-08-18T22:34:16Z, request_id konan-1787092456-31128, process_uptime_seconds 517.2"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 26 / http_requests_total{method=\"GET\",path=\"/orders\",status=\"503\"} 4 / http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 3 / http_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/3\",status=\"503\"} 2 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 2 — no /health series at any status other than 200 exists in this scrape"
  - id: E13
    type: probe
    source: "20x GET /health via scripts/probe.sh, run while faultline_chaos_enabled=1, 2026-08-18T22:33Z window"
    quote: "-- HTTP 200 in 0.001459s request_id=konan-1787092386-30970 / -- HTTP 200 in 0.001622s request_id=konan-1787092398-31040 / -- HTTP 200 in 0.001334s request_id=konan-1787092407-31088 (20/20 calls returned HTTP 200, 0 failures)"
gaps:
  - "Cannot see the chaos middleware's source or route registration (out of the investigator's reach per docs/lab.md — ground truth stays outside the surface contract), so /health's exemption from fault injection is established empirically (26/26 successes, 20 of them during confirmed-active chaos, p≈3.7×10⁻⁵ under the 0.4 failure-rate null) rather than structurally proven."
  - "Rotated log backups (app.log.1-.3) do not exist for this process lifetime, so the full-file sweep for unexplained 5xx/error lines covers only this process's uptime (since 22:25:39.452Z) — nothing before that is checked, though nothing before it is relevant to an incident that started at 22:25:47.450Z."
  - "No visibility into real end-user request volume or business-metric impact beyond this service's own counters — the investigator's surface has no user-facing analytics, only the service's own HTTP/log telemetry."
usage:
  model: claude-sonnet-5
  tokens: 6230710
  wall_clock_seconds: 701
---

# Chaos-mode fault injection causing intermittent 503s on both page loads and orders

## Summary

**Root-cause-identified.** At 2026-08-18T22:25:47.450Z, chaos mode was enabled on faultline (`failure_rate=0.4`, `error_status=503`) via a logged `POST /chaos/enable` call (E1). From that point on, ~40% of requests across both GET routes (product browsing, order listing) and the `POST /orders` write path returned 503, explaining both halves of the complaint — "some page loads and orders error out, then work again on retry" — as one mechanism, not two. `/health` is not subject to this injection: it returned 200 on every one of 26 observed calls, including 20 probed specifically while chaos was confirmed active (E12, E13), which is why the health dashboard stayed green throughout. A full sweep of the service's own log found zero 5xx, ERROR, or unhandled-exception lines that aren't explained by an adjacent `chaos_failure` event — this is the sole active failure mechanism, not a code defect (E11) or an infrastructure/process problem (no restarts, flat memory, sub-2ms latency observed by the infra-process lens). Confidence: high — validated by an adversarial judge across two rounds, closing both gaps the first round raised.

## Timeline (UTC)

- **22:25:39.452Z** — faultline process starts (fresh lab instance).
- **22:25:47.450Z** — chaos mode enabled: `failure_rate=0.4`, `error_status=503` (E1). Sharp onset marker.
- **22:25:52.690Z** — first observed failure: `POST /orders` → 503, 5.2s after the toggle (E2, E3).
- **22:25:55.866Z** — second `POST /orders` 503 (pre-investigation, real user/simulated traffic — not investigator probes).
- **22:26:04Z** — human complaint received; investigation triggered.
- **22:26:11Z** — investigation start.
- **22:26:35Z–22:26:38Z** — baseline: `/health` green (E5), `/metrics` shows `faultline_chaos_enabled 1` (E4) and 2 of 3 `POST /orders` calls failed.
- **22:29:00Z–22:29:11Z** — deep-dive probe batch confirms GET routes also fail under chaos: `/products` (E6), `/products/1` (E7), `/orders` list (E8) all show `chaos_failure` events; `/health` stays 200 throughout, including seconds after active GET failures (E9).
- **22:33Z** — round-2 batch: 20/20 `/health` probes succeed while chaos remains active (E13).
- **22:34:16Z** — full metrics scrape: 13 total 5xx across `/orders` and `/products*`, zero on `/health` (E12).
- **22:37:52Z** — investigation concluded.

## Investigation

**Baseline** (step 1): `/health` green, uptime 55.7s (fresh process), `/metrics` snapshot taken. The metrics snapshot itself already contained the first strong signal (`faultline_chaos_enabled 1` plus `POST /orders` 503 counts), so triage was scoped around confirming/refuting that lead rather than starting blind.

**Triage** (step 2, 3 lenses in parallel, blind to each other):
- *interfaces* — found the `chaos_enabled` config-change marker immediately preceding the first failure, scoped initially to `POST /orders`, and flagged the disjoint health-vs-business-surface pattern as the explanation for "dashboard is green."
- *software-defect* — found zero unhandled exceptions, zero data-dependent (per-input) failure shape; both 5xx responses tagged as explicit chaos injections, not silent code failures. No code-defect signature.
- *infra-process* — found a single startup event (no restarts), flat RSS (46825472→46841856 bytes over 65s), all durations under 2ms including the 503s. No saturation, no degradation.

**Deep-dive round 1** (step 3): the complaint named both "page loads" and "orders" failing, but triage evidence only showed `POST /orders` failures. One deep-dive agent (interfaces lens) ran a batch of 18 read-only GET probes across `/products`, `/products/{id}`, `/orders`. Result: GET routes failed too (56% observed, consistent with the configured 0.4 rate under small-sample noise), with `chaos_failure` log events explicitly naming the GET method/path — direct confirmation, not inference from status codes alone.

**Judge round 1** (step 4): returned **inconclusive**. Two gaps: (a) no full-log sweep had ruled out a second, non-chaos failure mechanism contributing alongside chaos (the "sole cause" claim was unverified), and (b) the "`/health` is exempt" claim rested on only 2 successful probes — statistically too weak (36% chance of that happening by luck alone).

**Deep-dive round 2** (step 5, targeted at exactly those two gaps): one agent (a) read the full log and enumerated every 5xx/ERROR/unhandled-exception line, checking each against a paired `chaos_failure` event, and (b) ran 20 more `/health` probes during confirmed-active chaos. Result: 13/13 5xx lines paired 1:1 with `chaos_failure` events, zero unexplained; 20/20 additional `/health` probes succeeded (cumulative 26/26).

**Judge round 2**: returned **validated**. The judge independently re-swept the (by-then-grown) log itself rather than trusting the evidence packet's stale line count, confirmed the 1:1 pairing held for the full file, and flagged two citation-accuracy defects in the evidence draft (a stale "68 lines" description in one entry, and a mislabeled scrape timestamp in another) — both corrected in the evidence ledger above (E12's timestamp now reads 22:34:16Z, matching the judge's independently derived value; the narrative-only "full sweep" claim is described in prose rather than as a single misleading quoted entry). Neither defect changed the underlying data, which the judge hand-verified against the raw log.

## Hypotheses

### H1 — Chaos-mode fault injection (validated)

Statement: a runtime chaos toggle, flipped at 22:25:47.450Z with `failure_rate=0.4` and `error_status=503`, injects probabilistic 503s across all sampled routes — GET and POST alike — and is the sole active failure mechanism during the incident window; `/health` is not wired into this injection path.

For: the config-change marker itself (E1); paired `chaos_failure`/503 events on `POST /orders` (E2, E3), `GET /products` (E6), `GET /products/1` (E7), and `GET /orders` (E8); the chaos-enabled gauge staying at 1 throughout (E4); `POST /orders` 503 counter matching observed failures (E10); zero unhandled-exception series the entire run (E11); a full-file sweep finding zero 5xx lines unexplained by an adjacent `chaos_failure`; 26/26 cumulative `/health` successes with zero `/health` 503 series ever recorded (E12) including a 20/20 batch run specifically during confirmed-active chaos (E13).

Against: none found. The one soft spot raised by the judge — that empirical non-failure isn't the same as a structural guarantee that `/health` can never fail under chaos — is recorded as a gap, not counter-evidence.

## Safe next steps

- Re-check `/metrics` and `/health` periodically (read-only) to confirm whether chaos mode is toggled off again, since this is a config state, not a code deploy — no code fix is implied by this root cause.
- If this pattern recurs, correlating future `chaos_enabled`/`chaos_disabled` log markers against complaint timestamps (as done here) is the fastest read-only confirmation path.
- Consider (as a follow-up discussion, not a journal action) whether the health check should exercise a request path that reflects business-traffic health, given the "green dashboard during a real incident" pattern confirmed here — flagged for the team, not for konan to act on.

## Gaps

- No access to the chaos middleware's source or route registration — `/health`'s exemption from fault injection is shown empirically (26/26 successes under load, 20 during confirmed-active chaos) rather than structurally. Out of reach per the lab's surface contract (`docs/lab.md`), which deliberately keeps ground truth outside the investigator's surface.
- The full-log sweep for unexplained failures covers only this process's lifetime (since 22:25:39.452Z, no rotated backups exist) — nothing earlier is checked, though nothing earlier is relevant to an incident with a confirmed 22:25:47.450Z onset.
- No user-facing business-impact telemetry (e.g. real traffic volume, cart abandonment) is on this investigator's surface — impact is inferred from the service's own request counters only.
