---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-latency-injection
  trigger: "manual — /konan adapter (human profile, docs/triggers.md); complaint object: source=human, fingerprint=human-1787120311, labels.alertname=human-report, no severity stated, startsAt=2026-08-19T06:18:31Z; investigation start 2026-08-19T06:18:31Z (trigger latency 0s — the adapter stamped both in one call)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-08-19T06:18:31Z
  concluded: 2026-08-19T06:23:57Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change enabled the target's fault-injection (chaos) mode at 06:18:13.888Z with failure_rate 0.0 and extra_latency_ms 1500, adding a randomized per-request delay bounded by ~1.5 s to shop routes while leaving status codes untouched."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled at 2026-08-19T06:18:13.888Z with failure_rate 0.0 and extra_latency_ms 1500; the injected randomized delay is what makes every shop route slow while every response stays 2xx."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E14, E15, E16, E17, E22]
    evidence_against: []
  - id: H2
    statement: "Organic load or resource saturation (traffic surge, memory pressure, worker starvation) is causing the slowness."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E17, E18]
  - id: H3
    statement: "A process crash, restart loop, or other lifecycle event is causing the slowness."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E16, E18]
  - id: H4
    statement: "The ZeroDivisionError on GET /products/{id} for a zero-stock product is the cause of the reported incident."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E19, E20, E21]
    evidence_against: [E15, E16]
  - id: H5
    statement: "The reporter's 'health checks are green and fast' is consistent with H1 rather than contradicting it, because /health and /metrics take no injected delay."
    incident_class: infra-process
    state: validated
    evidence_for: [E12, E13, E17]
    evidence_against: []
latent_findings:
  - statement: "GET /products/{product_id} raises an unhandled ZeroDivisionError for any product with units_in_stock == 0 (product id 3), returning HTTP 500. Deterministic and reproducible, but triggered in this window only by investigator-stamped probes — a latent defect, not the reported incident."
    evidence: [E19, E20, E21]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:07.955Z"
    quote: '{"ts": "2026-08-19T06:18:07.955Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:08.706Z"
    quote: '{"ts": "2026-08-19T06:18:08.706Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "c06d4f086bac", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.088, "client": "127.0.0.1:57171"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:09.764Z"
    quote: '{"ts": "2026-08-19T06:18:09.764Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "d436a38937cf", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.013, "client": "127.0.0.1:57172"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:10.827Z"
    quote: '{"ts": "2026-08-19T06:18:10.827Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "6ace6e83186d", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.924, "client": "127.0.0.1:57173"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:13.888Z"
    quote: '{"ts": "2026-08-19T06:18:13.888Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "d1c8573ab137", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:13.889Z"
    quote: '{"ts": "2026-08-19T06:18:13.889Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "d1c8573ab137", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.158, "client": "127.0.0.1:57174"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:17.373Z"
    quote: '{"ts": "2026-08-19T06:18:17.373Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "a14d5ee23817", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1424.611, "client": "127.0.0.1:57175"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:19.528Z"
    quote: '{"ts": "2026-08-19T06:18:19.528Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "97507a56a842", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1086.59, "client": "127.0.0.1:57176"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:21.613Z"
    quote: '{"ts": "2026-08-19T06:18:21.613Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "9432fcfc9e99", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1019.273, "client": "127.0.0.1:57177"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:23.768Z"
    quote: '{"ts": "2026-08-19T06:18:23.768Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "ce1cf1a15df5", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1088.524, "client": "127.0.0.1:57179"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:25.983Z"
    quote: '{"ts": "2026-08-19T06:18:25.983Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "f743321cd918", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1151.112, "client": "127.0.0.1:57180"}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:18:48.010Z"
    quote: '{"ts": "2026-08-19T06:18:48.010Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787120328-47113", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.492, "client": "127.0.0.1:57203"}'
  - id: E13
    type: probe
    source: "GET /health, request_id=konan-1787120328-47113"
    quote: |-
      {"status":"ok","uptime_seconds":40.067357499850914}
      -- HTTP 200 in 0.001494s request_id=konan-1787120328-47113
  - id: E14
    type: metric
    source: "GET /metrics, request_id=konan-1787120331-47119"
    quote: "faultline_chaos_enabled 1"
  - id: E15
    type: metric
    source: "GET /metrics, request_id=konan-1787120331-47119"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E16
    type: metric
    source: "GET /metrics, request_id=konan-1787120331-47119"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E17
    type: metric
    source: "GET /metrics, request_id=konan-1787120331-47119"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.013570873765274882
      http_request_duration_seconds_count{method="GET",path="/health"} 3
      http_request_duration_seconds_sum{method="GET",path="/products"} 2.5768114167731255
      http_request_duration_seconds_count{method="GET",path="/products"} 3
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 2.106876540929079
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 3
  - id: E18
    type: metric
    source: "GET /metrics, request_id=konan-1787120331-47119, and a later scrape in the same session"
    quote: |-
      process_uptime_seconds 43.999820332974195
      process_max_rss_bytes 47398912
      (later scrape) process_uptime_seconds 109.11846504197456 / process_max_rss_bytes 47398912
  - id: E19
    type: probe
    source: "GET /products/3, request_id=konan-1787120407-47216"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError",...}
      -- HTTP 500 in 0.675660s request_id=konan-1787120407-47216
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:20:08.056Z"
    quote: 'message "unhandled exception: division by zero", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", stack ends at File "…/faultline/src/faultline/shop.py", line 64, in get_product: "turnover_score": units_ordered / product["units_in_stock"],'
  - id: E21
    type: probe
    source: "GET /products (item for product id 3)"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E22
    type: probe
    source: "GET /products, investigator-stamped probes after the chaos marker"
    quote: |-
      -- HTTP 200 in 0.096810s request_id=konan-1787120397-47184
      -- HTTP 200 in 0.223159s request_id=konan-1787120399-47190
      -- HTTP 200 in 0.254927s request_id=konan-1787120400-47196
      -- HTTP 200 in 1.303830s request_id=konan-1787120425-47241
gaps:
  - "The complaint's own window ('the last few minutes') could not be tied to telemetry: lab/logs/app.log begins at the process start marker 06:18:07.955Z (E1), about 24 s before the complaint was stamped, and no rotated backups (app.log.1–.3) existed. Slowness the users felt before that timestamp is outside retained telemetry — this journal explains the window it can see."
  - "Who or what enabled chaos is not attributable from the investigator's surface: the change arrived as POST /chaos/enable from 127.0.0.1 with request_id d1c8573ab137 (E6), and /chaos is operator surface excluded from the probe allowlist, so no actor, caller, or intent could be established."
  - "The fixed-versus-random shape of the injected delay is inferred from the observed spread (E22, E17), not read from the target's code: the chaos middleware source lives in the faultline repo, outside this investigation's blinding contract."
  - "Real user-impact volume could not be measured beyond this process's 13 requests (E15). There is no upstream request log, no session or user counter, and no traffic history across restarts on the investigator's surface."
  - "The repo ships three lens files (infra-process, software-defect, interfaces). Domains named in the taxonomy but with no dedicated lens — load-saturation, third-party, data-db — were covered only by the overlap of the three that ran, so a finding specific to one of those domains could have been missed."
usage:
  model: claude-opus-5
  tokens: 1265749
  wall_clock_seconds: 326
---

# Shop-wide latency from a chaos-mode fault injection

## Summary

**Root cause identified.** At `2026-08-19T06:18:13.888Z` a runtime configuration change
enabled faultline's fault-injection ("chaos") mode with `failure_rate: 0.0` and
`extra_latency_ms: 1500` (E5) — a latency-only injection. Every shop route degraded at
that instant from ~1 ms to ~1.0–1.4 s while every response stayed 2xx: `/products` went
1.088 ms → 1424.611 ms (E2 → E7), `/products/1` 1.013 ms → 1019.273 ms (E3 → E9),
`POST /orders` 1.924 ms → 1088.524 ms (E4 → E10). The injected delay is a randomized
per-request draw bounded by ~1.5 s, not a fixed penalty — post-change samples spread
0.097 s–1.42 s (E22), and the cumulative mean for `/products` is ~859 ms (E17).

The condition is **still active**: `faultline_chaos_enabled 1` at the last scrape (E14).

`failure_rate: 0.0` is why nothing errors: `http_requests_total` carries only 2xx series
and `http_exceptions_total` has no series at all (E15, E16). And the reporter's green
health checks are not a contradiction — they are a monitoring blind spot. `/health` and
`/metrics` take no injected delay: 0.492 ms server-side 34 s *after* the change (E12),
against a ~859 ms `/products` mean over the same window (E17). Health-check greenness is
not evidence of service health here.

Confidence: high. Three independent predictions hold — the sharp onset at the config
marker, the error-free shape that `failure_rate: 0.0` specifically predicts, and the
route split that spares the control plane. The adversarial judge validated H1 and
refuted the load-saturation and lifecycle alternatives outright.

Impact: user-facing. The slow requests carry unstamped request ids (`a14d5ee23817`,
`ce1cf1a15df5`, …), which is non-investigator traffic — real users, not our probes.

One **latent** defect was found along the way and is *not* this incident: `GET
/products/{id}` raises an unhandled `ZeroDivisionError` for the zero-stock product id 3
(E19, E20, E21). Only investigator-stamped probes ever reached it; no user request did.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 06:18:07.955 | faultline 0.1.0 starts — the only startup marker in the log | E1 |
| 06:18:08.706 | Healthy baseline: `GET /products` in **1.088 ms** | E2 |
| 06:18:09.764 | Healthy baseline: `GET /products/1` in **1.013 ms** | E3 |
| 06:18:10.827 | Healthy baseline: `POST /orders -> 201` in **1.924 ms** | E4 |
| **06:18:13.888** | **Configuration change: chaos mode enabled — `failure_rate: 0.0`, `extra_latency_ms: 1500`** | E5, E6 |
| 06:18:17.373 | First known-bad: `GET /products` in **1424.611 ms**, status 200 | E7 |
| 06:18:19.528 | `GET /products/2` in 1086.59 ms, status 200 | E8 |
| 06:18:21.613 | `GET /products/1` in 1019.273 ms, status 200 | E9 |
| 06:18:23.768 | `POST /orders -> 201` in 1088.524 ms | E10 |
| 06:18:25.983 | `GET /products` in 1151.112 ms, status 200 | E11 |
| 06:18:31 | Complaint stamped; investigation starts | — |
| 06:18:48.010 | `GET /health -> 200` in **0.492 ms** — 34 s into the incident, unaffected | E12, E13 |
| 06:18:51 | Metrics confirm the condition is live: `faultline_chaos_enabled 1` | E14 |
| 06:20:08.056 | Investigator probe of `/products/3` surfaces a latent `ZeroDivisionError` | E19, E20 |

## Investigation

**Baseline.** `/health` green in 1.5 ms with `uptime_seconds: 40.07` (E13); a full
`/metrics` scrape; the 22-line log tail. The baseline itself carried the answer's shape:
all-2xx counters, an empty exception counter, and `faultline_chaos_enabled 1` sitting
next to a `/products` mean three orders of magnitude above `/health`'s.

**Triage — three lenses in parallel**, each blind to the others: infra-process,
software-defect, interfaces. All three independently anchored on the same 06:18:13.888Z
marker and on the `/health`-versus-shop-route split. The software-defect lens returned a
negative for its own domain — uniform latency across every route with zero exceptions is
not a code defect — and separately surfaced the latent `ZeroDivisionError`, correctly
labelling it as its own probe's doing.

**Deep-dive: skipped, deliberately.** Per the skill, a hypothesis whose triage evidence
is already deterministic and complete goes straight to the judge. H1 had a config marker,
before/after pairs on three identical paths, and a still-live gauge; deep-dives fill
evidence gaps, they do not re-prove.

**Judge.** One fresh adversarial judge, given the evidence ledger and hypothesis list
only — no narrative. It validated H1 and H5, invalidated H2, H3, and H4-as-cause, and
made two corrections that are carried into this journal: the delay must be described as
*randomized and bounded by* 1500 ms, not fixed at it (E22 shows a 0.097 s sample); and
the complaint's own time window is never tied to telemetry, which is now the first gap.
It also flagged that `/health` being *exempt by design* is an inference — what the
evidence proves is that `/health` was not delayed. The wording above respects that.

## Hypotheses

### H1 — Chaos-mode latency injection (validated) → root cause

Fault injection enabled at 06:18:13.888Z with `failure_rate: 0.0` and
`extra_latency_ms: 1500` (E5) adds a randomized delay to shop routes.

*For:* every fast shop sample precedes the marker (E2 1.088 ms, E3 1.013 ms, E4
1.924 ms) and every slow one follows it (E7, E8, E9, E10, E11) — no counterexample in
either direction. The metric sums reconcile exactly and add samples the log excerpt did
not show: `/products` 2.5768 s over 3 requests minus E2 and E7 leaves 1151.1 ms;
`/products/{id}` 2.1069 s minus E3 and E9 leaves 1086.6 ms (E17) — both also slow. The
error dimension matches the specific config, not a generic latency fault: `failure_rate:
0.0` predicts slow-but-clean, and E15/E16 deliver exactly that. The gauge confirms the
condition persisted through the investigation (E14). Provenance is clean: the enabling
request carries an unstamped id (E6), so the investigator did not cause what it reports.

*Against:* none. The apparently-fast investigator samples in E22 (0.097 s, 0.223 s) do
not undermine the hypothesis as stated — they refute only a *fixed* 1.5 s delay. Even
the fastest is ~90× the 1.088 ms baseline, and the spread with a ~750 ms mean is what a
uniform random draw bounded by 1500 ms produces, matching E17's measured ~859 ms mean.

### H2 — Organic load or resource saturation (invalidated)

Three independent facts each defeat it: total traffic across the whole process lifetime
is 13 requests (E15); RSS is byte-identical at 47398912 across both scrapes (E18); and
saturation does not spare one route by path name while crushing another — `/health` ran
a ~4.5 ms mean against `/products` at ~859 ms (E17). The `/health` bound is tight: 13.57
ms *total* for all three checks, so no health check lost even 14 ms.

### H3 — Crash, restart, or lifecycle event (invalidated)

One startup marker only, before any request (E1). Uptime climbs monotonically 44.0 →
109.1 with no reset, and `process_max_rss_bytes` — a max gauge, which a restart would
zero — is unchanged (E18). Note the trap the judge named: the pid in
`konan-<epoch>-<pid>` is the *investigator client's* pid, not the target's; its changes
are not target restarts.

### H4 — The ZeroDivisionError is the incident (invalidated as cause; real as a defect)

The defect is real and reproducible: `/products/3` returns HTTP 500 with
`exception_type: ZeroDivisionError` (E19), the stack ends at `shop.py:64`
`units_ordered / product["units_in_stock"]` (E20), and product 3 carries
`units_in_stock: 0` (E21). Ids 1, 2, and 4 return 200 — a data-dependent failure.

It is not this incident. It predicts errors; the complaint says nothing errors out, and
E15/E16 show no 5xx and no exception series across user traffic. No unstamped request
ever reached `/products/3` — the exception counter was empty until our own probes
incremented it. It rides along as a latent finding and deserves its own ticket.

### H5 — Green health checks are consistent with H1 (validated)

`/health` returned 200 in 0.492 ms server-side at 06:18:48 (E12), 34 s after the change
and squarely inside the slow window, with 0.001494 s client-side (E13); E17 bounds all
three health checks at 13.57 ms total. The reporter's observation is therefore evidence
*for* H1's route split, not against the incident. This is the healthy-monitoring trap in
its textbook form: the monitored path is the one path that was never slow.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Confirm the current state before anything else** — `faultline_chaos_enabled` on
   `/metrics` is the single-gauge answer to "is it still happening" (E14). The chaos
   state is operator surface, so whoever owns that surface should read it there.
2. **Establish who enabled it.** `POST /chaos/enable` at 06:18:13.889Z, request_id
   `d1c8573ab137`, client `127.0.0.1` (E6) is the whole trail available from telemetry.
   Attribution needs the operator-side record — deploy log, shell history, or whatever
   drove the chaos surface — which is outside the investigator's surface.
3. **Treat health-check greenness as non-evidence for this failure mode.** A synthetic
   check against a *business* route (`/products`, `/orders`) with a latency threshold
   would have caught this at 06:18:17; the current check cannot, by construction (E12
   vs E17).
4. **File the `ZeroDivisionError` separately** (E19, E20, E21) — `shop.py:64` divides by
   `units_in_stock` with no zero guard. It is latent today only because no user has
   requested a zero-stock product; that is luck, not safety.
5. **Extend log retention.** The whole investigation ran against 22 lines from a process
   that started 24 s before the complaint. See the first gap.

## Gaps

1. **The complaint window was never tied to telemetry.** `lab/logs/app.log` begins at
   the process start marker 06:18:07.955Z (E1), about 24 s before the complaint was
   stamped, and no rotated backups (`app.log.1`–`.3`) existed. If users felt slowness
   *before* that timestamp, this process's log cannot cover it. This journal explains
   the window it can see, and the judge held it as the one gap it could not close.
2. **The change's originator is unattributable.** The trail ends at request_id
   `d1c8573ab137` from `127.0.0.1` (E6); `/chaos` is operator surface excluded from the
   probe allowlist, so no actor or intent could be established from here.
3. **Fixed-versus-random delay is inferred, not read.** The bounded-random shape comes
   from the observed spread (E22, E17); the chaos middleware source lives in the
   faultline repo, outside this investigation's blinding contract.
4. **User-impact volume could not be measured** beyond this process's 13 requests (E15).
   No upstream request log, no session or user counter, no history across restarts.
5. **Three lenses shipped, six taxonomy domains exist.** infra-process, software-defect,
   and interfaces ran; load-saturation, third-party, and data-db have no dedicated lens
   file in the repo and were covered only by the overlap of the three that ran. H2 was
   killed on infra-process evidence, which is strong here, but a finding specific to an
   uncovered domain could have been missed.
