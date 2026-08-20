---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-wide-latency
  trigger: manual
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-08-19T06:08:14Z
  concluded: 2026-08-19T06:15:30Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Fault-injection (chaos) mode was enabled on the running process at 06:07:49.108Z with extra_latency_ms=1500 and failure_rate=0.0, adding a variable per-request delay of up to ~1.5 s to business routes while /health and /metrics are exempt — so the shop is slow, nothing errors, and health checks stay green."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime fault-injection configuration change (chaos mode, extra_latency_ms=1500, failure_rate=0.0) enabled at 06:07:49.108Z injects a variable per-request delay into business routes while leaving /health and /metrics unaffected."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E12, E13, E16, E19]
    evidence_against: [E8, E11]
  - id: H2
    statement: "Resource saturation (CPU, memory, or worker/event-loop starvation) causes the slowness."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E16, E18, E15]
  - id: H3
    statement: "A defect in the shop application code causes the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E8, E17, E19]
  - id: H4
    statement: "Process instability (crash or restart loop) causes the slowness."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E17]
  - id: H5
    statement: "A slow downstream or third-party dependency shared by the business routes, and not by /health, causes the slowness."
    incident_class: third-party
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E7, E14, E15]
latent_findings:
  - statement: "GET /products/{id} raises an unhandled ZeroDivisionError when the product's units_in_stock is 0 (product id 3), returning HTTP 500. Only investigator-stamped probes ever reached this path — no user traffic triggered it, so it is not the reported incident."
    evidence: [E19, E20, E21, E14]
  - statement: "Monitoring blind spot: the injected latency does not apply to /health or /metrics, so liveness checks and any alerting keyed on them stay green for the entire incident (~200x gap between /health and business-route means)."
    evidence: [E10, E11, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:43.170Z (sole event=startup line in the file)"
    quote: '{"ts": "2026-08-19T06:07:43.170Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:43.926Z"
    quote: '{"ts": "2026-08-19T06:07:43.926Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "43b9091cb065", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.147, "client": "127.0.0.1:57062"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:44.983Z"
    quote: '{"ts": "2026-08-19T06:07:44.983Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "6173610d0267", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.992, "client": "127.0.0.1:57063"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:49.108Z"
    quote: '{"ts": "2026-08-19T06:07:49.108Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "6dd0bc358446", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:49.109Z"
    quote: '{"ts": "2026-08-19T06:07:49.109Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "6dd0bc358446", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.768, "client": "127.0.0.1:57065"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:52.456Z"
    quote: '{"ts": "2026-08-19T06:07:52.456Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "dae67edfded7", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1294.635, "client": "127.0.0.1:57066"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:55.014Z"
    quote: '{"ts": "2026-08-19T06:07:55.014Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "dc6c13d47154", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1493.999, "client": "127.0.0.1:57067"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:07:56.188Z"
    quote: '{"ts": "2026-08-19T06:07:56.188Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "e699b173bbc7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 118.484, "client": "127.0.0.1:57068"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:08:00.665Z"
    quote: '{"ts": "2026-08-19T06:08:00.665Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "80a5fa28d139", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 841.143, "client": "127.0.0.1:57071"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:08:26.594Z"
    quote: '{"ts": "2026-08-19T06:08:26.594Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787119706-46617", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.556, "client": "127.0.0.1:57094"}'
  - id: E11
    type: probe
    source: "GET /health, request_id=konan-1787119706-46617"
    quote: |-
      {"status":"ok","uptime_seconds":43.43558616703376}
      -- HTTP 200 in 0.001641s request_id=konan-1787119706-46617
  - id: E12
    type: probe
    source: "GET /products, request_id=konan-1787119711-46633"
    quote: '-- HTTP 200 in 1.223345s request_id=konan-1787119711-46633'
  - id: E13
    type: metric
    source: "GET /metrics @ 06:08:32Z (konan-1787119712-46639) and again @ 06:14:27Z (konan-1787120067-46850)"
    quote: 'faultline_chaos_enabled 1'
  - id: E14
    type: metric
    source: "GET /metrics @ 06:14:27Z, request_id=konan-1787120067-46850"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 1'
  - id: E15
    type: metric
    source: "GET /metrics @ 06:14:27Z, request_id=konan-1787120067-46850"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1'
  - id: E16
    type: metric
    source: "GET /metrics @ 06:14:27Z, request_id=konan-1787120067-46850"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.014590709237381816
      http_request_duration_seconds_count{method="GET",path="/health"} 5
      http_request_duration_seconds_sum{method="GET",path="/metrics"} 0.0028553318697959185
      http_request_duration_seconds_count{method="GET",path="/metrics"} 5
      http_request_duration_seconds_sum{method="GET",path="/orders"} 2.5737000431399792
      http_request_duration_seconds_count{method="GET",path="/orders"} 3
      http_request_duration_seconds_sum{method="GET",path="/products"} 4.234045626828447
      http_request_duration_seconds_count{method="GET",path="/products"} 7
  - id: E17
    type: metric
    source: "GET /metrics, scrapes @ 06:08:32Z and @ 06:14:27Z"
    quote: 'process_uptime_seconds 49.53817283408716  →  process_uptime_seconds 404.35928075015545'
  - id: E18
    type: metric
    source: "GET /metrics, scrapes @ 06:08:32Z and @ 06:14:27Z"
    quote: 'process_max_rss_bytes 47628288'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:10:08.724Z (the only /products/3 request line in the file)"
    quote: '{"ts": "2026-08-19T06:10:08.724Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787119807-46773", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1288.611, "client": "127.0.0.1:57122"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:10:08.705Z (stack trimmed to the raising frame)"
    quote: '{"level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1787119807-46773", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": ... File "src/faultline/shop.py", line 64, in get_product\n    "turnover_score": units_ordered / product["units_in_stock"]}'
  - id: E21
    type: probe
    source: "GET /products, request_id=konan-1787119711-46633"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
gaps:
  - "Mechanism is inferred, not read: faultline's source is outside the investigator's surface contract (docs/lab.md) and the eval blinding contract, so the claim that the delay is middleware-level and skips /health rests on the self-describing config event (E4), the observed ~1500 ms ceiling, and the route-exemption pattern — not on code."
  - "No counterfactual arm: disabling chaos to observe latency return to ~1 ms requires the operator surface (/chaos), which is read-only-forbidden for the investigator. Causality rests on the before/after step on the same route in the same process, plus the declared knob."
  - "The surface exposes no CPU-time, queue-depth, or connection-pool metric, so H2 (saturation) was killed indirectly — via route selectivity (E10 vs E16) and flat peak RSS (E18) — rather than by direct resource telemetry."
  - "Non-investigator impact sample is small: 4 slow unstamped requests (E6–E9), all from 127.0.0.1, and user traffic in the log stops at 06:08:00.665Z. No SLO or latency threshold is defined on this surface, so 'painfully slow' is quantified but not scored against a target."
  - "Only three lens files exist (infra-process, software-defect, interfaces); the data-db and third-party taxonomy branches had no dedicated lens and were reasoned about by the orchestrator alone (H5)."
  - "Log history is limited to the current process: no app.log.1–.3 backups exist, so no pre-restart baseline was available for comparison."
usage:
  model: claude-opus-5
  tokens: 1662950
  wall_clock_seconds: 436
---

# Shop-wide latency from chaos fault injection, health checks exempt

## Summary

**Root cause identified.** At `2026-08-19T06:07:49.108Z` a runtime fault-injection
("chaos") configuration change was applied to the running faultline process via
`POST /chaos/enable`, with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E4, E5).
From the next request onward, every business route pays a variable added delay of up to
about 1.5 s, while `/health` and `/metrics` are exempt. That single configuration
accounts for all three parts of the complaint at once: the shop is slow (business-route
means ~605–858 ms against a ~1 ms pre-change baseline, E2/E3 vs E16), nothing errors
(`failure_rate: 0.0`; the only 5xx in the whole window is the investigator's own probe,
E14/E15/E19), and health checks are green and fast (0.556 ms, E10) because the injected
delay never touches them.

**The incident is ongoing at the time of writing** — `faultline_chaos_enabled 1` on a
scrape at 06:14:27Z, roughly 6.5 minutes after onset (E13).

Confidence is high on the what and the when: the onset is a sharp step on the same route
in the same continuous process (`/products/1` 0.992 ms at 06:07:44 → 118.484 ms at
06:07:56, no restart between, E3/E8/E17), and the observed delays all sit under the
ceiling the config event declared three seconds earlier. Confidence is moderate on the
precise mechanism, because faultline's source is outside my surface contract — see Gaps.

One correction to the obvious reading: the delay is **not** a fixed 1.5 s. Observed
values span 118 ms to 1494 ms (E6, E7, E8, E9), so it behaves as a sampled delay bounded
by `extra_latency_ms`, not a constant one. A responder who expects every request to take
1.5 s will misread the dashboards.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 06:07:43.170 | Process starts — `faultline 0.1.0 started`; the only startup marker in the log | E1 |
| 06:07:43.9–06:07:46 | Healthy baseline: `/products` 1.147 ms, `/products/1` 0.992 ms, `POST /orders` 1.954 ms | E2, E3 |
| **06:07:49.108** | **Configuration change marker** — chaos mode enabled, `failure_rate: 0.0`, `error_status: 503`, `extra_latency_ms: 1500` | E4 |
| 06:07:49.109 | Applied externally via `POST /chaos/enable -> 200` (client 127.0.0.1:57065) | E5 |
| 06:07:52.456 | First known-bad user request: `/products` 1294.635 ms — a ~1100x step, 3.3 s after the marker | E6 |
| 06:07:55–06:08:00 | Degradation is shop-wide: `/products/2` 1493.999 ms, `/products/1` 118.484 ms, `/orders` 841.143 ms — all HTTP 200 | E7, E8, E9 |
| 06:08:00.665 | Last non-investigator request in the log | E9 |
| 06:08:14 | Investigation starts (trigger latency from `startsAt` 06:08:06: 8 s) | — |
| 06:08:26.594 | `/health` returns in 0.556 ms while the shop is degraded — the healthy-monitoring trap, live | E10 |
| 06:10:08.724 | Investigator probe of `/products/3` returns 500 (`ZeroDivisionError`) — latent defect, investigator-triggered only | E19, E20 |
| 06:14:27 | Chaos still enabled; uptime 404 s, one continuous process throughout | E13, E17 |

## Investigation

**Baseline.** `/health` (200 in 1.6 ms) against `/products` (200 in 1.223 s) split the
picture immediately (E11, E12), and the first `/metrics` scrape showed
`faultline_chaos_enabled 1` with an empty `http_exceptions_total` family. The log tail
gave the config marker and a clean pre/post boundary.

**Triage — three lenses in parallel** (infra-process, software-defect, interfaces), each
blind to the others and given only the lens path, the surface contract, the verbatim
complaint, and the baseline facts. All three converged on the same onset anchor and,
usefully, each contributed a distinct kill: infra-process ruled out restart-loop and
saturation (monotonic uptime, flat peak RSS, a 0.556 ms `/health` interleaved between
841 ms and 1221 ms business calls); software-defect ruled out a code cause (same route,
same input, fast before and slow after, no restart) and surfaced the latent
`ZeroDivisionError`; interfaces established that the degradation is latency-only with no
gateway-shaped statuses, and quantified the ~200x health-versus-shop split.

**Deep-dive: deliberately skipped.** The skill reserves deep-dives for filling evidence
gaps. H1's triage evidence was already deterministic and complete — a declared config
event, a sharp before/after step on an identical request, and a matching ceiling — so
re-proving it would have spent budget without adding information. The hypotheses went
straight to the judge.

**Judge (adversarial, evidence-only).** The judge validated H1 and killed H2–H4, but
returned four fair objections. Three were cheap to settle read-only, and I did settle
them in a second gathering round:

1. *"`http_exceptions_total` may be structurally incapable of showing errors, so 'no
   errors' rests on nothing."* **Refuted.** A fresh scrape shows
   `http_exceptions_total{type="ZeroDivisionError"} 1` and
   `http_requests_total{...,status="500"} 1` (E14, E15). The counter does record
   failures; the earlier empty family was simply a scrape taken before the event. This
   strengthens the no-errors claim rather than weakening it.
2. *"'No user traffic reached /products/3' was cited to a scrape 96 s too early."*
   **Settled correctly.** A whole-file scan finds exactly one `/products/3` request, and
   it carries a `konan-` id (E19). The defect is latent, confirmed by the right
   evidence.
3. *"E1 quotes one startup line; it does not prove there was only one."* **Settled** — a
   whole-file count returns exactly 1, and uptime backdates start to ~06:07:42.5,
   matching E1 (E17).
4. *"No hypothesis covered a slow downstream dependency, which has the same signature."*
   **Fair, and now recorded as H5** rather than left silent. See below for its honest
   strength.

The judge's fifth suggestion — read faultline's request middleware to close the
mechanism gap — I declined. It is outside `docs/lab.md` and outside the eval blinding
contract, so it is recorded as a Gap, not acted on. A read-only suggestion that breaches
the surface contract is still a breach.

## Hypotheses

### H1 — chaos latency injection — **validated**

*Statement:* the 06:07:49.108Z fault-injection config change adds a variable per-request
delay to business routes, exempting `/health` and `/metrics`.

For: the same URL in the same uninterrupted process went 0.992 ms → 118.484 ms across
the marker (E3, E8, E17), so deployed code cannot explain it. Every post-marker duration
sits below the declared `extra_latency_ms: 1500`, one within 6 ms of it (E7) — neither a
code defect nor a saturating resource has any reason to respect a ceiling a config event
announced three seconds earlier. The `failure_rate: 0.0` field predicts errorless
degradation, and the traffic confirms it (E13, E15). `/health` stayed at 0.556 ms inside
the same window (E10).

Against (recorded honestly, and it is why the statement says *variable*): E8 at 118 ms
and the 182 ms probe show the delay is sampled, not fixed at 1500 ms — the naive "every
page takes 1.5 s" version of this hypothesis is false. E11's fast `/health` is listed
against as well, since it is the observation any "the whole service is slow" framing
must explain away; the route-exemption reading absorbs it.

*Impact, stated precisely:* four non-investigator requests are observably slow (E6–E9),
covering 3 of 3 business routes seen. User traffic in the log ends at 06:08:00.665Z, so
this journal cannot speak to impact after that time.

### H2 — resource saturation — **invalidated**

Saturation is not route-selective: a starved worker pool or a blocked event loop would
delay `/health` too, yet `/health` ran at 0.556 ms interleaved between multi-hundred-ms
business calls (E10, E16). Peak RSS is byte-identical across scrapes ~5 min apart
(E18), and total traffic is ~30 requests over 6 minutes — there is no load present to
saturate. Killed indirectly, since the surface carries no CPU or queue-depth metric
(Gap 3).

### H3 — application code defect — **invalidated as the cause of the slowness**

Same route, same input, same process, no restart: 0.992 ms then 118.484 ms (E3, E8,
E17). Code was constant across the transition. Narrow verdict, deliberately: a code
defect *does* exist in this service (E19, E20) — it just does not explain the latency.
Supporting detail: the investigator's failing 500 request was *also* delayed 1288.611 ms
(E19), so the wait applies even when the handler throws, which places it above the
business logic.

### H4 — crash or restart loop — **invalidated**

One startup marker in the file (E1), and `process_uptime_seconds` climbing 49.5 → 404.4
with no reset (E17) backdates process start to ~06:07:42.5, matching E1. A single
process spans the entire incident window.

### H5 — slow downstream or third-party dependency — **invalidated (weakest kill)**

Added at the judge's prompting, because its signature — business routes slow, `/health`
and `/metrics` fast — is genuinely identical to H1's. What separates them is that H1's
cause is self-describing: a logged event names the exact knob and value (E4), and the
observed delays honor that value as a ceiling (E7). A dependency stall has no reason to
respect a number announced by an unrelated config event. Additionally, no
dependency-shaped failure telemetry appears — no 502/503/504, no timeout, no error
series other than the investigator's own (E14, E15). This is the least direct of the
four kills, and I flag it as such rather than dressing it up.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. Confirm current state before anything else: scrape `/metrics` for
   `faultline_chaos_enabled` — it was still `1` at 06:14:27Z (E13). If it reads `1`, the
   degradation is live and the shop is still slow for users.
2. Establish who enabled it: the change arrived as `POST /chaos/enable` from
   `127.0.0.1:57065` at 06:07:49.109 (E5). Correlate that client and time against
   operator/deploy records outside this target to identify whether this was an intended
   exercise left running.
3. Read `/metrics` per-route means rather than `/health` when judging user impact — the
   `/health` series (~2.9 ms mean, and that includes the 12 ms cold-start sample) is
   structurally blind to this incident class (E16).
4. Track the latent `ZeroDivisionError` on zero-stock products as its own item (E19,
   E20, E21). It is unrelated to this incident and no user has hit it, but products can
   reach `units_in_stock: 0` through ordinary trading.
5. Consider whether alerting should key on business-route latency percentiles; this
   incident produced no alert, and the human report beat every automated signal.

## Gaps

1. **Mechanism inferred, not read.** faultline's source is outside `docs/lab.md` and the
   eval blinding contract. That the delay lives in middleware and skips `/health` follows
   from the config event, the ceiling behavior, and the route-exemption pattern — not
   from code. The judge proposed reading the middleware; I declined on contract grounds.
2. **No counterfactual.** Observing latency return to ~1 ms with chaos off needs the
   operator surface (`/chaos`), which the investigator may not touch. Causality rests on
   the before/after step and the declared knob.
3. **No resource telemetry.** No CPU-time, queue-depth, or connection-pool metric
   exists on this surface, so H2 was killed by route selectivity and flat peak RSS
   rather than directly.
4. **Small non-investigator sample.** Four slow user-side requests (E6–E9), all from
   127.0.0.1, with user traffic ending 06:08:00.665Z. No SLO threshold is defined on this
   surface, so severity is quantified in milliseconds but not scored against a target.
5. **Two taxonomy branches had no lens.** Only infra-process, software-defect, and
   interfaces lens files exist; data-db and third-party were covered by orchestrator
   reasoning alone (H5).
6. **Limited log history.** No `app.log.1`–`.3` backups exist, so there is no
   pre-restart baseline for comparison beyond this process's own first six seconds.
