---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-wide-latency
  trigger: "manual — /konan adapter (profile: human, docs/triggers.md). Complaint object: source=human, fingerprint=human-1793684760, labels.alertname=human-report (no severity stated by the reporter), startsAt=2026-11-03T05:46:00Z. Investigation entered at 2026-11-03T05:46:07Z — trigger latency 7s."
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-03T05:46:07Z
  concluded: 2026-11-03T05:56:36Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal operational degradation switch in the target was enabled at 05:45:43.536Z with extra_latency_ms=1500 and failure_rate=0.0, so while it is on every business request pays an added delay drawn per request up to ~1.5s and no request is turned into an error; the /health and /metrics paths did not slow with the rest, which is why the health check stayed green and fast."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal degradation switch (enabled at 05:45:43.536Z, extra_latency_ms=1500, failure_rate=0.0) injects per-request latency into the business routes and no errors, while /health and /metrics are observed not to slow."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E22]
    evidence_against: []
  - id: H2
    statement: "Demand exceeded the capacity of the process (CPU, memory, workers or connections), queueing requests and degrading latency."
    incident_class: load-saturation
    state: invalidated
    evidence_for: [E6, E7, E8]
    evidence_against: [E2, E3, E5, E9, E14, E21]
  - id: H3
    statement: "A defect in the target's own application code on the business routes makes those routes slow."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E6, E7, E8]
    evidence_against: [E4, E5, E9, E10]
  - id: H4
    statement: "A process-lifecycle fault — a crash, a restart loop, or a hung process — degrades every route."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E12, E14, E21]
latent_findings:
  - statement: "GET /products/3 fails deterministically with an unhandled ZeroDivisionError: the handler divides by the product's units_in_stock, and product 3 carries units_in_stock=0. Both failures in this process came from investigator probes, so it is not the reported incident — but product 3 is listed on the public /products response, so a user who opens it gets a 500. Latent means untriggered since startup (~10 minutes of counters), not unreachable."
    evidence: [E9, E17, E18, E19, E20]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:37.588Z"
    quote: '{"ts": "2026-11-03T05:45:37.588Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:38.349Z (user traffic — unstamped request id)"
    quote: '{"ts": "2026-11-03T05:45:38.349Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "abb74e27f63d", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.271, "client": "127.0.0.1:64060"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:40.474Z (user traffic — unstamped request id)"
    quote: '{"ts": "2026-11-03T05:45:40.474Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8f6a506e08f3", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.131, "client": "127.0.0.1:64062"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:43.536Z — the change marker"
    quote: '{"ts": "2026-11-03T05:45:43.536Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "ad0346479841", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:45.682Z (user traffic — first request after the marker)"
    quote: '{"ts": "2026-11-03T05:45:45.682Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "5312f87fe101", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 86.777, "client": "127.0.0.1:64064"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:53.428Z (user traffic — same route as E2)"
    quote: '{"ts": "2026-11-03T05:45:53.428Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "777bc3cae0a3", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 939.645, "client": "127.0.0.1:64068"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:51.418Z (user traffic — same route as E3)"
    quote: '{"ts": "2026-11-03T05:45:51.418Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "a4e58ef069c2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1075.718, "client": "127.0.0.1:64067"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:45:55.885Z (user traffic — the last non-investigator request in the log)"
    quote: '{"ts": "2026-11-03T05:45:55.885Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "b21f0e0adc80", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1380.934, "client": "127.0.0.1:64069"}'
  - id: E9
    type: metric
    source: "GET /metrics @ 2026-11-03T05:46:37Z (request_id=konan-1793684797-19315) — every request series present at that moment"
    quote: |
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E10
    type: metric
    source: "GET /metrics @ 2026-11-03T05:46:37Z — the exception family in full: header present, no series beneath it"
    quote: |
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E11
    type: metric
    source: "GET /metrics @ 2026-11-03T05:46:37Z"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: probe
    source: "GET /health @ 2026-11-03T05:46:36Z (request_id=konan-1793684796-19310)"
    quote: |
      {"status":"ok","uptime_seconds":58.919717374956235}
      -- HTTP 200 in 0.002053s request_id=konan-1793684796-19310
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:46:36.495Z (investigator probe, 53s after the marker)"
    quote: '{"ts": "2026-11-03T05:46:36.495Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793684796-19310", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.657, "client": "127.0.0.1:64087"}'
  - id: E14
    type: metric
    source: "GET /metrics @ 2026-11-03T05:55:51Z (request_id=konan-1793685351-19638) — 608s after the marker"
    quote: |
      faultline_chaos_enabled 1
      process_uptime_seconds 614.0654997078236
      process_max_rss_bytes 47644672
  - id: E15
    type: metric
    source: "GET /metrics @ 2026-11-03T05:55:51Z — duration aggregates per route"
    quote: |
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.017992625012993813
      http_request_duration_seconds_count{method="GET",path="/health"} 5
      http_request_duration_seconds_sum{method="GET",path="/metrics"} 0.0035920003429055214
      http_request_duration_seconds_count{method="GET",path="/metrics"} 5
      http_request_duration_seconds_sum{method="GET",path="/orders"} 2.8129056252073497
      http_request_duration_seconds_count{method="GET",path="/orders"} 2
  - id: E16
    type: probe
    source: "GET /products and GET /orders, triage probes after 2026-11-03T05:49:00Z (investigator-stamped)"
    quote: |
      -- HTTP 200 in 0.568559s
      -- HTTP 200 in 1.433579s
  - id: E17
    type: probe
    source: "GET /products/3 @ 2026-11-03T05:49:07Z (request_id=konan-1793684946-19464)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793684946-19464"} -- HTTP 500'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:49:07.670Z (investigator-triggered)"
    quote: '{"level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1793684946-19464", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"} — stack ends at shop.py line 64, in get_product: "turnover_score": units_ordered / product["units_in_stock"],'
  - id: E19
    type: probe
    source: "GET /products @ 2026-11-03T05:55:41Z (request_id=konan-1793685341-19625)"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E20
    type: metric
    source: "GET /metrics @ 2026-11-03T05:55:51Z — both 500s carry investigator request ids konan-1793684946-19464 and konan-1793684966-19495"
    quote: |
      http_exceptions_total{type="ZeroDivisionError"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E21
    type: metric
    source: "GET /metrics @ 2026-11-03T05:46:37Z — process gauges, for comparison with E14 554s later"
    quote: |
      process_uptime_seconds 59.65906887501478
      process_max_rss_bytes 47644672
  - id: E22
    type: probe
    source: "GET /products @ 2026-11-03T05:55:41Z (request_id=konan-1793685341-19625) — a low draw of the injected delay"
    quote: "-- HTTP 200 in 0.024425s request_id=konan-1793685341-19625"
gaps:
  - "The injection mechanism itself is not cited. The surface contract gives no code visibility, so the non-slowing of /health and /metrics is an observation over 5 health and 5 metrics samples (E13, E15), not a proven exemption rule. Reading the target's source would settle it and is deliberately outside the investigator's surface (docs/lab.md, 'Ground truth stays outside')."
  - "No counterfactual. The journal cannot show durations returning to 1–2ms with the switch off, because toggling it is operator/eval surface and the investigator may not touch it."
  - "Continued user impact is inferred, not observed. The last non-investigator request in telemetry is E8 at 05:45:55.885Z; every slow sample after it is investigator-stamped (E16, E22). The switch still reads on (E14), but no user traffic after 05:45:55.885Z appears in the log, so the shop may simply be idle."
  - "Who flipped the switch is unknown. The flip carries request_id ad0346479841, which is not investigator-stamped, and the surface exposes no actor or caller identity beyond client 127.0.0.1:64063 (E4)."
  - "The /metrics duration aggregates mix investigator probes with user traffic (E15), so no current user-latency figure can be read from them; per-request user latency comes only from the log's access lines."
  - "No CPU, in-flight, queue-depth or connection-pool series exists on the surface. The load-saturation refutation therefore rests on arrival volume (E9), step shape (E2, E3 against E5), flat RSS (E21 against E14) and non-overlapping request windows, not on direct capacity gauges."
  - "Whether order creation decrements units_in_stock could not be determined read-only — no pre-order catalogue snapshot exists. So the blast radius of the latent finding is open: if ordering drives stock to zero, the 500 can spread beyond product 3."
  - "Counters and the log cover only this process, started 05:45:37.588Z (E1). 'No user traffic triggered the latent defect' means 'not in these ~10 minutes', not 'never'."
usage:
  model: claude-opus-5
  tokens: 1794838
  wall_clock_seconds: 629
---

# Shop-wide latency from an internal degradation switch, with health checks blind to it

## Summary

**Root cause identified.** An internal operational degradation switch inside the target
was turned on at 05:45:43.536Z, configured `extra_latency_ms: 1500` with
`failure_rate: 0.0` (E4). While it is on, every business request pays an added delay
drawn per request up to about 1.5s, and no request is converted into an error — which is
exactly the reported shape: "painfully slow", "nothing errors out". User-visible latency
on the same routes went from 1.271ms to 939.645ms on `GET /products` (E2 → E6) and from
2.131ms to 1075.718ms on `POST /orders` (E3 → E7), with `GET /orders` at 1380.934ms (E8).
The onset is a step at the marker, not a ramp: the first user request after the flip was
already 66x slower (E5). Every status in user traffic stayed 2xx and no exception series
existed at all (E9, E10).

The health check is green because it does not move with the rest: `/health` was 0.657ms
53s after the flip (E13) and averages 3.6ms over 5 calls while `GET /orders` averages
1.41s over 2 (E15) — roughly 300x apart. The health signal does not exercise the degraded
path, so it is a false negative here, not evidence of health.

**Confidence: high** for the mechanism's existence, timing and effect — the marker's own
configuration predicted both numbers that the data then showed (a ~1500ms ceiling, which
none of the 9 post-flip samples breached, and a zero error rate). **Lower** for two
things stated honestly in Gaps: the injection code and the health exemption rule were
never read (the surface forbids it), and live user impact right now is inferred from the
switch state (E14) rather than observed, because no user request appears in telemetry
after 05:45:55.885Z.

**Impact:** all shop routes — product listing, product detail, order listing, order
creation. The switch was still on at the end of this investigation, 608s after the flip
(E14). Note that the injected delay is a per-request draw, not a constant: one probe came
back in 24ms (E22), so individual requests can still feel normal.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 05:45:37.588 | Process starts — faultline 0.1.0; the only startup line in the log | E1 |
| 05:45:38.349 | Normal: user `GET /products` in 1.271ms | E2 |
| 05:45:40.474 | Normal: user `POST /orders` in 2.131ms | E3 |
| **05:45:43.536** | **Change marker — degradation switch enabled, `extra_latency_ms: 1500`, `failure_rate: 0.0`, caller not investigator-stamped** | **E4** |
| 05:45:45.682 | First user request after the flip: `GET /products` 86.777ms (66x) | E5 |
| 05:45:49–05:45:55 | User traffic degrades across all routes: 579ms, 866ms, 939.645ms, 1075.718ms, 1380.934ms — all 2xx | E6, E7, E8 |
| 05:45:55.885 | Last non-investigator request in telemetry | E8 |
| 05:46:00 | Human raises the complaint (`startsAt`) | — |
| 05:46:07 | Investigation starts (trigger latency 7s) | — |
| 05:46:36 | Baseline: `/health` 200 in 2.1ms, server-side 0.657ms — fast while business routes sit near 1s | E12, E13 |
| 05:46:37 | Baseline metrics: switch on, no exception series, every status 2xx | E9, E10, E11, E21 |
| 05:49:07 | Investigator probe triggers a latent `ZeroDivisionError` on `/products/3` | E17, E18 |
| 05:55:41–05:55:51 | Switch still on at 614s uptime; RSS unchanged from baseline; business routes still slow (568ms, 1.43s) | E14, E15, E16, E19, E22 |

## Investigation

**Baseline** (05:46:36–37Z): `/health` 200 in 2.1ms with `uptime_seconds` 58.9; a
`/metrics` scrape; the full 22-line log. The baseline itself already carried the two
decisive facts — `faultline_chaos_enabled 1` and a pre-flip latency band of 0.8–15.6ms.

**Triage — one round, three lenses in parallel, each blind to the others**
(infra-process, software-defect, interfaces). Each received only its lens file, the
surface contract, the verbatim complaint, and the baseline. All three independently
landed on the 05:45:43.536Z marker from their own domain: infra-process as a runtime
latency switch plus lifecycle checks that came back clean, interfaces as a sharp-onset
configuration change with before/after rates (and correctly handed the class to
infra-process, since the switch is internal rather than a boundary component),
software-defect as "no code-defect signature for the slowness" — while finding a real but
separate defect on `/products/3`.

**No deep-dive round was needed.** H1's triage evidence was already deterministic and
complete — the marker states its own configuration, and the before/after data matches
both of its numbers — so per the loop's rule it went straight to the judge rather than
re-proving itself. Budget used: 1 triage round of 3 lenses, 0 deep-dives, 1 judge.

**Judge** (fresh agent, given only the hypothesis list and the verbatim evidence ledger —
no lens reasoning, no narrative): H1 **validated**, H2 **invalidated**, H3 **invalidated**
for the slowness, L1 **validated** as latent. It sharpened four things that are now in
this journal: the mechanism and the health exemption are inferred rather than read; there
is no counterfactual; "users are still slow" is an inference from switch state; and
"sub-millisecond health" was overstated (3.6ms mean, not sub-ms). It also derived that the
four post-flip user requests were strictly sequential with 1.0–4.7s idle gaps — nothing
was ever queued, which kills saturation arithmetically.

The judge suggested reading the target's middleware source to close the mechanism gap.
I declined: the faultline checkout and its source are outside the investigator's surface
contract (`docs/lab.md`) and the blinding contract. It is recorded as a gap instead.

## Hypotheses

### H1 — internal degradation switch — **validated** (root cause)

The marker (E4) is self-describing: `extra_latency_ms: 1500`, `failure_rate: 0.0`. Both
numbers were predictions made before the data was examined, and both hold. The 9 post-flip
samples — 86.777, 579.426, 866.569, 939.645, 1075.718, 1380.934ms in user traffic (E5–E8),
568.559 and 1433.579ms and 24.425ms in investigator probes (E16, E22) — all sit under the
1500ms ceiling, spread as a per-request draw rather than a fixed addition. `failure_rate:
0.0` predicts no errors: no exception series existed (E10) and every counted status was
2xx (E9). The same routes were 1.271ms and 2.131ms before the flip (E2, E3) and the first
request after it was already 86.777ms (E5) — a step, not a ramp. The switch still read 1
at 608s after the flip (E14). This is more than correlation: the configured magnitude
bounds the observations.

Not covered by the citations, and so not claimed: the injection code, the existence of an
exemption *rule* for `/health` and `/metrics` (observed behaviour only), a counterfactual
with the switch off, and who called the enable route.

### H2 — load-saturation — **invalidated**

All three of its predictions fail. Total demand was 13 requests in 59s of uptime (E9) —
nothing to saturate. The onset is a step (E2, E3 against E5), not the gradual ramp
saturation produces. `process_max_rss_bytes` is byte-identical at 59.7s and 614.1s of
uptime — 47644672 both times (E21 against E14) — so no memory growth over 9 minutes. And
adding each duration to its timestamp shows the post-flip user requests ran strictly one
after another with idle gaps: concurrency never exceeded 1, so nothing queued. The
refutation rests on volume, shape, flat memory and zero concurrency rather than on direct
CPU or queue gauges, which the surface does not expose (Gaps).

### H3 — application-code defect on the business routes — **invalidated** (for the slowness)

Both predictions fail. There were no errors concentrated on the slow routes — zero
exceptions and zero non-2xx anywhere in the complaint window (E9, E10). And the slowness
is not input-specific: it crosses three routes including a POST (E5–E8), and the *same*
route with the same input returns 1.271ms before the marker and 939.645ms after it (E2 vs
E6), so the variable is time, not input. E4 supplies a non-code cause.

This verdict is about the slowness only. The target's code is not clean — see the latent
finding, which is the single best-evidenced item in this investigation.

### H4 — process-lifecycle fault (crash, restart loop, hang) — **invalidated**

The log holds exactly one startup line (E1). `process_uptime_seconds` rises monotonically
with wall clock across three scrapes — 59.66, 320.08, 614.07 (E21, E14) — so no restart
and no loop. `/health` returned 200 on every call with no flap and no connection refusal
(E12). The process is alive and degraded, which is a different family from dead or
cycling.

### Latent — `GET /products/3` raises ZeroDivisionError

Deterministic and reproduced twice (E17, E20). The stack names the expression:
`units_ordered / product["units_in_stock"]` at shop.py line 64 (E18), and product 3
carries `units_in_stock: 0` (E19) — a missing zero-divisor guard. It is **not** the
reported incident: both 500s carry `konan-*` ids, i.e. my own probes created them, and
three user requests to that route returned 200 before any probe ran (E9). The complaint
said nothing errors out, and for users that was true.

Two qualifiers that matter: latent is not unreachable — product 3 sits in the public
`/products` listing (E19), so any user who opens it gets a 500 — and "untriggered" means
within this process's ~10 minutes of counters, not ever. Product 3 is the only zero-stock
row today (E19); whether ordering can drive another product to zero is unresolved (Gaps).

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Re-scrape `/metrics` and watch `faultline_chaos_enabled`. While it reads 1, shop
   latency is explained — do not send anyone hunting through application code.
2. Ask whoever operates the target whether the enable call at 05:45:43.536Z was intended
   (a load test, a drill, a switch left on). The telemetry names no actor (Gaps), so this
   question cannot be answered from the surface.
3. Watch the log's access lines for a non-investigator slow request after 05:45:55.885Z —
   that would confirm live user impact; its continued absence would mean the shop is idle
   rather than suffering.
4. Point a monitor at a business route instead of `/health`. The health path did not move
   while business routes sat near 1s (E13, E15), so the current check is structurally
   unable to see this class of degradation.
5. Expect a 500 from `/products/3` while the zero-divisor guard is missing, and keep it
   out of synthetic checks until then — it is reachable from the public listing (E19).
6. When reading dashboards for this window, discount the two 500s and the
   `ZeroDivisionError` counter (E20) and part of the per-route duration counts (E15):
   they are investigator-caused, not user-facing.

## Gaps

The frontmatter list, elaborated:

- **The mechanism was never read.** The switch's effect is established; its implementation
  is not. That `/health` and `/metrics` did not slow is an observation over 5 and 5
  samples (E13, E15), not a proven exemption rule — they may be excluded by design, or
  merely cheap. The target's source would settle it and is deliberately outside the
  investigator's surface (`docs/lab.md`, "Ground truth stays outside"); the judge
  recommended reading it, and I declined for that reason.
- **No counterfactual.** Nothing here shows latency returning to 1–2ms with the switch
  off, because toggling it is operator/eval surface.
- **Live user impact is inferred.** No user request appears after 05:45:55.885Z (E8). The
  switch is on (E14) and investigator probes are still slow (E16), but the shop may be
  idle.
- **No actor.** The flip's request id is not investigator-stamped (E4); the surface
  exposes no caller identity beyond `127.0.0.1:64063`.
- **Mixed aggregates.** `/metrics` duration counts merge investigator probes with user
  traffic (E15); user latency must be read from access lines only.
- **No capacity gauges.** No CPU, in-flight, queue-depth or connection-pool series exists,
  so H2 was refuted indirectly.
- **Stock behaviour unknown.** Whether order creation decrements `units_in_stock` could
  not be determined read-only, leaving the latent defect's blast radius open.
- **Short horizon.** Counters and log cover one process from 05:45:37.588Z (E1) — about
  10 minutes.
