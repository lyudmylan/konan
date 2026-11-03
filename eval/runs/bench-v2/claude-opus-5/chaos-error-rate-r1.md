---
konan_journal: 2
investigation:
  id: 2026-11-03-intermittent-shop-503s
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-03T00:49:18Z
  concluded: 2026-11-03T00:58:56Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An error-injection switch inside the target was turned on at 00:48:58.858Z, configured to fail a fraction of requests with HTTP 503 before the handler runs, and it short-circuited at least one non-investigator request; it was still on at the end of the investigation."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal error-injection switch is on, configured for a 0.4 failure rate with HTTP 503 and no added latency, and it short-circuits requests before the handler, producing errors that succeed on retry."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E6, E7, E8, E17, E19]
    evidence_against: []
  - id: H2
    statement: "The user-visible incident is caused by a code defect in the target's own request handling raising an unhandled exception."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E9, E10, E11, E13]
  - id: H3
    statement: "The incident is a process-lifecycle fault: the process crashes and restarts, or hangs, so requests fail and then succeed."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E14, E16]
  - id: H4
    statement: "The incident is load-saturation: demand exceeded capacity and produced intermittent errors."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E7, E13, E15]
  - id: H5
    statement: "Separate from the incident: the target's own code raises an unhandled ZeroDivisionError when a product's stock is zero, and only investigator probes ever triggered it."
    incident_class: software-defect
    state: validated
    evidence_for: [E9, E10, E11, E12, E13]
    evidence_against: []
latent_findings:
  - statement: "GET /products/{id} divides by units_in_stock without a zero guard, so the one catalog item with units_in_stock 0 (id 3) returns HTTP 500 deterministically. Only investigator probes reached it: both counted exceptions carry konan-* request ids and no non-investigator request ever asked for /products/3."
    evidence: [E9, E10, E11, E12, E13]
  - statement: "Injected 503s are counted under the raw request path while handler outcomes on the same route are counted under the templated path, so a dashboard grouping by route template shows none of these 503s."
    evidence: [E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:48:58.858Z"
    quote: '{"ts": "2026-11-03T00:48:58.858Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "d75b541affd3", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: metric
    source: "/metrics @ request_id konan-1793667236-14171"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:49:07.264Z"
    quote: '{"ts": "2026-11-03T00:49:07.264Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e1a56733c58f", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:49:07.264Z"
    quote: '{"ts": "2026-11-03T00:49:07.264Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "e1a56733c58f", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.283, "client": "127.0.0.1:62986"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:48:50.863Z"
    quote: '{"ts": "2026-11-03T00:48:50.863Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:48:55.798Z"
    quote: '{"ts": "2026-11-03T00:48:55.798Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "eb31098721b1", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.78, "client": "127.0.0.1:62970"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:28.260Z"
    quote: '{"ts": "2026-11-03T00:51:28.260Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "konan-1793667088-14094", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.152, "client": "127.0.0.1:63027"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:29.945Z"
    quote: '{"ts": "2026-11-03T00:51:29.945Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793667089-14102", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.493, "client": "127.0.0.1:63029"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:12.743Z (stack trimmed to the throwing frame)"
    quote: '{"ts": "2026-11-03T00:51:12.743Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793667072-14058", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:12.751Z"
    quote: '{"ts": "2026-11-03T00:51:12.751Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793667072-14058", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.856, "client": "127.0.0.1:63018"}'
  - id: E11
    type: metric
    source: "/metrics @ request_id konan-1793667236-14171 (read after both logged 500s, at 00:51:12.751Z and 00:51:41.220Z)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2'
  - id: E12
    type: probe
    source: "/products @ request_id konan-1793667065-14041, HTTP 200"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E13
    type: log
    source: "lab/logs/app.log — the complete set of request lines carrying unstamped (non-investigator) request ids, 00:48:51.594Z through 00:49:10.443Z; paths and statuses, ids in brackets"
    quote: 'GET /health 200 [e461394bbbe6]; GET /health 200 [c075500db0fd]; GET /products 200 [eb1afd55f3c8]; GET /products/1 200 [d69241cd4e9f]; POST /orders 201 [c841b76c50a0]; GET /products/2 200 [eb31098721b1]; POST /chaos/enable 200 [d75b541affd3]; GET /products 200 [122ce3e4dee5]; GET /products/1 200 [5b58e7f39a90]; GET /products/2 200 [4eaea1455b14]; POST /orders 201 [f53b3e103fd8]; GET /products 200 [0a2d73e44207]; GET /products/5 200 [c8564c12005a]; POST /orders 503 [e1a56733c58f]; GET /products/1 200 [6e91ce659121]; GET /orders 200 [3b34f8b00806]; GET /products/4 200 [7a6f16b8086b]. No unstamped request line appears after 00:49:10.443Z.'
  - id: E14
    type: metric
    source: "/metrics @ request_id konan-1793667236-14171 (stamp epoch 1793667236 = 00:53:56Z; 00:48:50.863 + 305.201 = 00:53:56.06, so the id and the value agree)"
    quote: "process_uptime_seconds 305.2011281668674"
  - id: E15
    type: metric
    source: "/metrics, three reads: konan-1793666985-13968, konan-1793667071-14053, konan-1793667236-14171"
    quote: "process_max_rss_bytes 48529408 -> 48562176 -> 49577984"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:33.878Z"
    quote: '{"ts": "2026-11-03T00:51:33.878Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793667093-14109", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.48, "client": "127.0.0.1:63030"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:34.205Z"
    quote: '{"ts": "2026-11-03T00:51:34.205Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 503", "request_id": "konan-1793667094-14115", "event": "request", "method": "GET", "path": "/products/3", "status": 503, "duration_ms": 0.163, "client": "127.0.0.1:63031"}'
  - id: E18
    type: metric
    source: "/metrics @ request_id konan-1793667236-14171"
    quote: 'http_requests_total{method="GET",path="/products/3",status="503"} 4 beside http_requests_total{method="GET",path="/products/{product_id}",status="200"} 9 and http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:51:28.260Z and 2026-11-03T00:51:34.204Z"
    quote: '{"ts": "2026-11-03T00:51:28.260Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793667088-14094", "event": "chaos_failure", "method": "GET", "path": "/products"} / {"ts": "2026-11-03T00:51:34.204Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793667094-14115", "event": "chaos_failure", "method": "GET", "path": "/products/3"}'
gaps:
  - "Magnitude of end-user impact is not established. Exactly one non-investigator request failed (E3, E4): one of the 10 unstamped requests logged after the switch went on, a 19-second sample. Everything after 00:49:10.443Z is investigator traffic only (E13)."
  - "The 0.4 failure rate is a configuration value read from the enable event (E1), never a measured rate. The observed non-investigator rate was 1 in 10, which does not corroborate 0.4."
  - "No non-investigator page-load failure was observed. The complaint's 'some page loads error out' is consistent with a route-agnostic switch, but every unstamped GET returned 200 (E13); the only GET 503s carry konan-* ids (E7, E17)."
  - "Unstamped traffic cannot be proven to be end users: the set includes the /chaos/enable call itself and two /health checks, and every client address is loopback 127.0.0.1 (E13)."
  - "There is no healthy baseline window inside this process. It started at 00:48:50.863Z and the switch went on 8 seconds later (E5, E1), so 'normal' rests on 7 pre-switch requests."
  - "Who enabled the switch, and why, is outside the telemetry surface. The enable call shows only a loopback client address (E1, E13)."
  - "The failure rate at the moment the complaint was raised is unknown: no non-investigator traffic exists in that window (E13)."
  - "load-saturation was refuted by proxies only — latency and memory (E7, E15, E18). The surface exposes no concurrency, queue-depth, CPU, or arrival-rate metric, so it was never probed directly."
  - "The data-db and third-party incident classes could not be checked at all: this lab has no database and no external dependency (docs/lab.md, 'Known gaps of this lab'). No lens covered them."
  - "Catalog item 4 carries \"price\": null (E12) and nothing exercised the order path for it. The investigator surface is GET-only, so POST /orders with that id is unreachable."
usage:
  model: claude-opus-5
  tokens: 2302244
  wall_clock_seconds: 578
---

# Intermittent shop 503s while the health endpoint stays green

## Summary

**Root cause identified: an internal error-injection switch is on.** At
2026-11-03T00:48:58.858Z the target logged `chaos_enabled` with `failure_rate: 0.4`,
`error_status: 503`, `extra_latency_ms: 0` (E1), and the switch was still on at the end
of this investigation (E2). It short-circuits requests *before* the handler runs: each
injected failure carries its own `chaos_failure` marker, and the failures return in
0.15–0.28 ms against ~0.5 ms for a success (E3, E4, E7, E19). That mechanism explains
the reported shape exactly — an error on one request and success on the next to the same
path, 1.7 s apart (E7, E8) — and it explains the green dashboard: `/health` returned 200
throughout, including 0.3 s before an injected 503 on a business path (E16, E17). The
class is `infra-process`, not `interfaces`, because the mechanism is a switch inside the
target rather than a boundary component, even though the symptom wears a gateway-shaped
503.

**Confidence is high on the mechanism and low on the magnitude.** The causal link is
proven at the request level for exactly one piece of real traffic: `e1a56733c58f` carries
both the `chaos_failure` marker and the `POST /orders -> 503` (E3, E4). Beyond that single
request, user impact is **not** established — the 40% figure is configuration, not a
measurement, and no non-investigator page load was ever seen to fail (see Gaps). A
responder should treat "the switch is on and injecting 503s" as settled, and "40% of users
are affected" as unverified.

One unrelated latent defect was found and is recorded below; it did not affect users.

## Timeline

- **00:48:50.863Z** — process starts; single startup marker, `faultline 0.1.0` (E5).
- **00:48:51.594Z – 00:48:55.798Z** — 7 requests, all 2xx. Last known-good before the
  switch: `GET /products/2 -> 200` (E6). This is the entire healthy window.
- **00:48:58.858Z** — **configuration-change marker.** `chaos_enabled`, `failure_rate: 0.4`,
  `error_status: 503`, `extra_latency_ms: 0`, from loopback request `d75b541affd3` (E1).
  Exactly one such event; the switch was never reverted (E2).
- **00:49:07.264Z** — the one proven user-visible failure: `chaos_failure` and
  `POST /orders -> 503` under the same unstamped id `e1a56733c58f` (E3, E4).
- **00:49:10.443Z** — last non-investigator request of any kind (E13). All later traffic
  is this investigation's.
- **00:49:18Z** — complaint raised; investigation starts. The switch had been on for 19 s,
  which is tighter than the reporter's "a few minutes ago" — and the process itself was
  only 28 s old, so no earlier onset is possible within this process.
- **00:51:12.751Z** — first investigator-triggered `ZeroDivisionError` → 500 on
  `/products/3` (E9, E10). Latent, not the incident.
- **00:51:28.260Z / 00:51:29.945Z** — the retry shape, captured directly: same path,
  503 then 200, 1.7 s apart (E7, E8, E19).
- **00:51:33.878Z / 00:51:34.205Z** — `/health` 200, then an injected 503 on a business
  path 0.3 s later (E16, E17) — the green-dashboard gap, observed.
- **00:53:56Z** — final read: switch still on, uptime monotonic at 305.2 s (E2, E14).

## Investigation

**Baseline.** `/health` 200 with `uptime_seconds` 44.6, a full `/metrics` scrape, and the
28-line log tail. Two things stood out immediately and shaped everything after: the
process was under a minute old, and `faultline_chaos_enabled` was already `1` while
`http_exceptions_total` had no series at all.

**Triage — three lenses in parallel, each blind to the others** (infra-process,
software-defect, interfaces), each given only its lens path, the surface contract, the
verbatim complaint, and the baseline facts. All three independently landed on the switch
and all three classified it as `infra-process`; the interfaces lens explicitly ruled its
own domain out, finding no external dependency in evidence. The software-defect lens found
the `ZeroDivisionError` and, unprompted, labelled it latent. `load-saturation` and
`data-db`/`third-party` had no lens: the first is refuted by evidence but only by proxy,
the latter two are not exercisable by this lab. Both are recorded in Gaps rather than
quietly dropped.

**Deep-dive: deliberately skipped.** H1's triage evidence was already deterministic and
complete — a marker log line, a live gauge, per-request `chaos_failure` pairing, and a
directly observed fail-then-succeed pair on one path. The loop's rule is that deep-dives
fill evidence gaps rather than re-prove, so the budget went unspent and H1 went straight
to the judge.

**Judge.** One fresh subagent, given the hypothesis list and the verbatim ledger only, no
narrative. It validated H1 and H5, invalidated H2, H3 and H4 — and returned two
corrections that are folded into this journal:

1. **A mislabeled source.** I had attributed an uptime reading of 141.098 s to the wrong
   request id, which made the metrics read look *earlier* than the exception it counted
   and so implied a possible third, unattributed exception. The id was wrong, not the
   timestamp. E14 now cites a read whose stamp and value agree independently
   (epoch → 00:53:56Z; 00:48:50.863 + 305.201 = 00:53:56.06), which also settles H3 with a
   single continuous process across the whole window.
2. **An overclaim on impact.** My framing leaned on the configured 40% as though it were
   observed. It is not: one non-investigator request failed, out of 10 after the switch
   went on, and no real page load failed at all. The Summary and Gaps now say so plainly.

The judge also noted that H3 and H4 were killed by sufficient-rival-cause and proxy
signals rather than by their own direct metrics. That is accurate and is recorded.

## Hypotheses

### H1 — internal error-injection switch (validated, `infra-process` / `degradation-switch`)

**For:** the `chaos_enabled` marker with its full configuration (E1); the gauge still at 1
at the final read (E2); request-id pairing of a `chaos_failure` marker with a 503 response
on real traffic (E3, E4) and on investigator traffic (E7, E17, E19); a clean 2xx window
before the switch (E6); the retry shape on one path (E7, E8).

**Against:** nothing. **Carve-out:** "40%" is the configured rate, not a measured one, and
the clause "produced *the reported* failures" holds for the mechanism and for one proven
request, not for the reported volume.

### H2 — a code defect caused the user-visible incident (invalidated)

Refuted, not merely unsupported. Both counted exceptions carry `konan-*` ids (E9, E10,
E11); no unstamped request returned 500 and none ever touched `/products/3` (E13); and the
one real failure has a sufficient, differently-shaped cause — an injection marker, no
stack, no `exception_type`, 0.283 ms (E3, E4). **Would revive it:** any 500 or
`unhandled_exception` line carrying an unstamped id.

### H3 — crash/restart or hang (invalidated)

One startup marker only (E5); uptime monotonic and arithmetically consistent with that
single epoch at the final read (E14); the process kept serving after an unhandled
exception (E16). Durations of 0.15–8.9 ms rule out hanging.

### H4 — load-saturation (invalidated)

Arrival rate was ~0.9 req/s (E13), mean latency sub-millisecond (E18), RSS effectively
flat (E15), and the failures are *faster* than the successes (E7) — saturation cannot
produce a sub-millisecond 503. A sufficient rival cause is present (E1). Refuted by proxy;
see Gaps.

### H5 — latent zero-stock division defect (validated, not the incident)

`shop.py:64` divides `units_ordered` by `product["units_in_stock"]` with no zero guard
(E9); item 3 is the only catalog entry with `units_in_stock: 0` (E12); that path returns
500 deterministically (E10). Only investigator probes reached it (E11, E13), so it is a
latent finding and does not change the verdict.

## Safe next steps

Read-only; remediation is out of scope for this journal.

- Confirm with whoever operates this target **who issued the `/chaos/enable` call** at
  00:48:58.858Z and whether it was intended. The telemetry shows only a loopback client,
  so the answer is not on this surface.
- Re-read `/metrics` for `faultline_chaos_enabled` before acting on anything here — the
  gauge is the live authority on whether the incident is still in progress.
- To size real impact rather than infer it, observe non-investigator traffic over a window
  that overlaps actual user activity. The current sample is 19 seconds wide and ends long
  before the complaint was raised.
- Note for monitoring review: `/health` returns only `{"status":"ok","uptime_seconds":…}`
  and consults neither the switch gauge nor request outcomes, so a green dashboard is
  fully consistent with this incident (E16, E17).
- Note for metrics review: injected 503s are labeled with the raw path while handler
  outcomes use the templated path (E18), so route-template dashboards hide these errors.

## Gaps

The frontmatter list, in short: user-impact **magnitude** is unestablished (one proven
non-investigator failure, a 19-second sample, nothing after 00:49:10.443Z); the 40% rate is
configuration rather than measurement; no real page-load failure was observed; "unstamped"
traffic is not provably human, since it includes the enable call and health checks on
loopback; there is no healthy baseline window beyond 7 requests, because the switch went on
8 seconds after startup; the switch's origin is off-surface; `load-saturation` was refuted
by proxies only, as this surface exposes no concurrency, queue-depth, CPU or arrival-rate
metric; `data-db` and `third-party` could not be checked at all, since the lab has neither;
and catalog item 4's `"price": null` was never exercised, as the investigator surface is
GET-only.
