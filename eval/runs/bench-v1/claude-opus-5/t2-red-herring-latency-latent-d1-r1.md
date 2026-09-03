---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-latency-injection
  trigger: "manual — /konan human profile; source=human, fingerprint=human-1787142734, labels.alertname=human-report, no severity stated, startsAt=2026-08-19T12:32:14Z; investigation started 2026-08-19T12:32:27Z (trigger latency 13s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-19T12:32:27Z
  concluded: 2026-08-19T12:38:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change at 2026-08-19T12:31:54.621Z enabled chaos mode with extra_latency_ms=1500, which injects a variable per-request delay (observed 64–1436 ms) into every business route while leaving /health and /metrics untouched; the flag is still enabled."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled at 12:31:54.621Z with extra_latency_ms=1500 and failure_rate=0.0, injecting a variable latency of up to ~1.5s into /products, /products/{id} and /orders (GET and POST); the condition persists."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E11]
    evidence_against: []
  - id: H2
    statement: "/health and /metrics are exempt from the injected latency, so a green, fast health check is not evidence of a healthy shop — liveness monitoring cannot see this degradation."
    incident_class: infra-process
    state: validated
    evidence_for: [E4, E5, E9, E10, E11]
    evidence_against: []
  - id: H3
    statement: "GET /products/{id} raises an unguarded ZeroDivisionError computing turnover_score = units_ordered / units_in_stock, so product 3 (units_in_stock: 0) returns 500 deterministically while every other catalog id returns 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E11, E13, E14, E17]
    evidence_against: []
  - id: H4
    statement: "The reported error page was the H3 defect firing for a real user during the incident window."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E12, E13, E15]
  - id: H5
    statement: "The slowness is resource saturation or process churn — a memory leak, OOM pressure, or a crash/restart loop."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E16]
latent_findings:
  - statement: "GET /products/3 returns 500 (ZeroDivisionError, unguarded division by units_in_stock=0) on every request. Product 3 is listed by GET /products, so ordinary browsing reaches it — but in this process's entire telemetry the only two 500s were raised by investigator probes, so no user impact is confirmed. The defect is live for as long as units_in_stock stays 0."
    evidence: [E11, E13, E14, E17]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:31:54.621Z"
    quote: '{"ts": "2026-08-19T12:31:54.621Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "56c5f7e95281", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:31:49.413Z"
    quote: '{"ts": "2026-08-19T12:31:49.413Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "70a64e97d9e5", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.234, "client": "127.0.0.1:60543"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:31:51.549Z"
    quote: '{"ts": "2026-08-19T12:31:51.549Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "8d96eddace26", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.987, "client": "127.0.0.1:60545"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:31:58.054Z"
    quote: '{"ts": "2026-08-19T12:31:58.054Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "3e5ea55ef6cf", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1362.338, "client": "127.0.0.1:60547"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:32:00.512Z"
    quote: '{"ts": "2026-08-19T12:32:00.512Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "423d154f6150", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1379.277, "client": "127.0.0.1:60548"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:32:04.073Z"
    quote: '{"ts": "2026-08-19T12:32:04.073Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "c2a0879fd64f", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 836.778, "client": "127.0.0.1:60550"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:32:06.050Z — the last non-investigator request in the file"
    quote: '{"ts": "2026-08-19T12:32:06.050Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "64ff40c0d5c0", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 893.627, "client": "127.0.0.1:60551"}'
  - id: E8
    type: metric
    source: "/metrics @ 2026-08-19T12:32:32Z (request_id konan-1787142752-58758)"
    quote: "faultline_chaos_enabled 1"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:32:28.215Z"
    quote: '{"ts": "2026-08-19T12:32:28.215Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787142748-58752", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.458, "client": "127.0.0.1:60573"}'
  - id: E10
    type: probe
    source: "GET /health (request_id konan-1787142748-58752)"
    quote: |-
      {"status":"ok","uptime_seconds":39.5979880830273}
      -- HTTP 200 in 0.001556s request_id=konan-1787142748-58752
  - id: E11
    type: probe
    source: "GET /products (request_id konan-1787142955-59005)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.987853s request_id=konan-1787142955-59005
  - id: E12
    type: metric
    source: "/metrics @ 2026-08-19T12:32:32Z (request_id konan-1787142752-58758) — baseline scrape, before any investigator probe of /products/3"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      (no series lines; http_requests_total carried only status="200" and status="201")
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:34:00.534Z"
    quote: '{"ts": "2026-08-19T12:34:00.534Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787142839-58879", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1017.3, "client": "127.0.0.1:60592"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:34:00.514Z (stack tail, request_id konan-1787142839-58879)"
    quote: |-
      "level": "ERROR", "message": "unhandled exception: division by zero", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"
        File "/Users/lyudmylan/Projects/faultline/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
      ZeroDivisionError: division by zero
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:31:48.628Z — the only startup marker in the file; lab/logs/ holds app.log alone, with no .1-.3 rotated backups"
    quote: '{"ts": "2026-08-19T12:31:48.628Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E16
    type: metric
    source: "/metrics, two scrapes: 2026-08-19T12:32:32Z (konan-1787142752-58758) and 2026-08-19T12:34:15Z (konan-1787142855-58943)"
    quote: |-
      process_uptime_seconds 43.791143791982904   -> process_uptime_seconds 147.11793991690502
      process_max_rss_bytes 47415296              -> process_max_rss_bytes 47415296
  - id: E17
    type: metric
    source: "/metrics @ 2026-08-19T12:34:15Z (request_id konan-1787142855-58943)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
gaps:
  - "The reported error page could be neither confirmed nor refuted: the process started at 12:31:48.628Z and lab/logs/ has no rotated backups (E15), so no telemetry survives from before that instant. Anything a user saw earlier is out of reach."
  - "No client-side or edge telemetry (browser, proxy, CDN, load balancer) is on the investigator's surface, so the competing explanation — a client timeout rendered as an error page against the ~1.4s injected delay — could not be tested."
  - "No non-investigator traffic arrived after 12:32:06.050Z (E7), so ongoing user impact could not be measured directly; persistence of the fault was confirmed by investigator probes only (E11)."
  - "The exemption of /health and /metrics from the injected latency is inferred from timing alone; the middleware source that implements the carve-out is outside the surface contract."
  - "process_max_rss_bytes is a high-water mark, and the surface carries no current-RSS, CPU, thread-pool or event-loop metrics. Non-memory saturation is therefore excluded by sufficiency (H1 fully explains the latency), not by direct measurement."
usage:
  model: claude-opus-5
  tokens: 1690597
  wall_clock_seconds: 333
---

# Shop-wide latency from a chaos flag left enabled

## Summary

**Root cause identified.** At `2026-08-19T12:31:54.621Z` a runtime configuration change
enabled chaos mode on faultline with `extra_latency_ms: 1500` and `failure_rate: 0.0`
(E1). From the very next request onward, every business route slowed by two to three
orders of magnitude — `GET /products` went from 1.234 ms to 1362.338 ms across that
marker (E2, E4) — and the flag is still on: `faultline_chaos_enabled 1` (E8), with
investigator probes still seeing ~1s on `/products` (E11). The injected delay is
variable per request, not a flat 1.5s: observed values span 63.8 ms to 1436.3 ms, which
matches the reporters' "painfully slow" with an inconsistent feel.

`/health` and `/metrics` are exempt from the injection — 0.458 ms while the shop sat
near a second (E9, E10). The complaint's "health checks are green and fast" is therefore
not a contradiction; it is the signature of this fault. Confidence is high: the onset is
a single logged config marker with a clean before/after on the same routes, and the
condition reproduces on demand.

The "error page once" is **not explained** by this cause and could not be attributed.
`failure_rate` is `0.0`, so the chaos knob injects delay only and cannot emit an error
status; and at the baseline scrape `http_exceptions_total` had no series at all (E12),
meaning zero exceptions in this process before the investigation began. A separate,
real defect does exist that can produce an error page — `GET /products/3` returns 500
deterministically (E13, E14) — but the only two 500s on record are investigator probes.
It rides along as a latent finding, not as this incident's user impact.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 12:31:48.628 | Process starts, faultline 0.1.0. Only startup marker in the file; no rotated backups exist, so telemetry begins here. | E15 |
| 12:31:49–12:31:51 | Normal: `/products` 1.234 ms, `POST /orders` 1.987 ms. This is the baseline. | E2, E3 |
| **12:31:54.621** | **Configuration change marker** — `chaos_enabled`, `failure_rate: 0.0`, `error_status: 503`, `extra_latency_ms: 1500`. | E1 |
| 12:31:58.054 | First request after the marker: `/products` 1362.338 ms. Step change, no ramp. | E4 |
| 12:32:00–12:32:06 | `/products/2` 1379.277 ms, `POST /orders` 836.778 ms, `GET /orders` 893.627 ms. Last non-investigator request of the incident. | E5, E6, E7 |
| 12:32:14 | Human complaint raised (`startsAt`). | — |
| 12:32:27 | Investigation starts (trigger latency 13s). | — |
| 12:32:28 | Investigator `/health` probe: 0.458 ms — fast, while the shop is slow. | E9, E10 |
| 12:32:32 | Baseline `/metrics`: chaos gauge 1; `http_exceptions_total` has no series — zero errors so far. | E8, E12 |
| 12:34:00 / 12:34:05 | Investigator probes of `/products/3` raise ZeroDivisionError → 500, twice. These are ours, not users'. | E13, E14, E17 |
| 12:34:15 | `/metrics`: uptime monotonic 43.8→147.1s, RSS byte-identical. No churn, no leak. | E16 |
| 12:38:00 | Concluded. Chaos flag still enabled. | E8, E11 |

## Investigation

**Baseline** — `/health` (200, uptime 39.6s), `/metrics`, and the full log tail. The log
turned out to be the complete history since startup: 21 lines, one startup marker, no
rotated backups. That made "normal" a narrow six-second window, but a clean one.

**Triage** — three lenses in parallel, each blind to the others: `infra-process`,
`interfaces`, `software-defect`. The complaint was vague and the baseline excluded no
domain, so no lens was skipped. All three independently anchored the onset to the
12:31:54.621Z chaos marker; the software-defect lens additionally isolated the
`/products/3` 500 by probing every catalog id.

**Deep-dive** — none spawned. H1, H2 and H3 all came out of triage with deterministic,
complete evidence (a logged config marker with before/after on identical routes; a
timing contrast in the same window; a reproduced 500 with a stack and the failing input
isolated). Deep-dives fill evidence gaps; there were none to fill. The one genuinely
open question — the "error page once" — has no test available on the surface, because
the telemetry that would settle it predates process start. Spawning an agent for it
would have been coverage theater.

**Judge** — one fresh adversarial judge, given the hypothesis list and the verbatim
evidence ledger only, with no narrative. It validated H1, H2 and H3; invalidated H4 and
H5. It corrected one overstatement in H1's prediction — "2–3 orders of magnitude on
*every* request" is too strong, since one sample was 63.8 ms (~50x baseline) — so the
claim is stated as a variable delay up to ~1.5s. It also narrowed H2: the exemption is
inferred from timing alone, and no alert configuration is on the surface, so the
defensible claim is "a green `/health` is not evidence of a healthy shop" rather than a
proven alerting blind spot.

**Note on investigator side effects** — our probes added 2 requests to
`http_requests_total{path="/products/{product_id}",status="500"}` and 2 to
`http_exceptions_total{type="ZeroDivisionError"}` (E17). Those counters were empty at
baseline (E12). Anyone reading `/metrics` after this investigation should not count them
as user impact.

## Hypotheses

### H1 — Chaos latency injection enabled at 12:31:54.621Z — **validated** (root cause)

The marker (E1) declares exactly the observed behavior, and the boundary is sharp: the
last pre-marker request was 1.987 ms (E3), the first post-marker request 1362.338 ms
(E4). The step hit every business route at once — `/products`, `/products/{id}`,
`GET /orders`, `POST /orders` (E4, E5, E6, E7) — with no code path in common, which is
the signature of injected degradation rather than a slow query or a hot loop. It is a
flag change, not a deploy: exactly one startup marker in the file (E15), so nothing
restarted between the fast and slow periods. The condition persists — the gauge still
reads 1 (E8) and probes still take ~1s (E11). No evidence against.

### H2 — `/health` and `/metrics` are exempt from the injection — **validated**

In the same window that business routes took 562–1436 ms (E4, E5, E11), `/health`
returned in 0.458 ms (E9) and 0.001556 s wall-clock at the probe (E10). Sub-millisecond
service while chaos is enabled cannot be explained by the delay applying to those paths,
so an exemption is the only fit. Stated narrowly, per the judge: the mechanism is
inferred from timing, and no alert configuration is visible on the surface — what the
evidence supports is that a green `/health` is not evidence of a healthy shop.

### H3 — Unguarded division by `units_in_stock` on `/products/{id}` — **validated** (latent)

`GET /products/3` returned 500 twice (E13), and the stack names the operation:
`turnover_score = units_ordered / product["units_in_stock"]` at `shop.py:64` (E14). The
catalog shows product 3 with `units_in_stock: 0`, and it is the only such item (E11).
Every other id returns 200 — including product 4, whose `price` is `null`, which kills
the rival "bad catalog data in general" reading. The counters corroborate exactly:
2 five-hundreds, 2 ZeroDivisionErrors, no other exception class (E17). Product 3 is
listed by `GET /products`, so ordinary browsing reaches it. Two caveats the judge
insisted on: "every time" rests on n=2 plus a deterministic code path, and the divisor
is a stock value — a restock would end the 500s without any code change.

### H4 — The reported error page was H3 firing for a real user — **invalidated**

The prediction was at least one non-investigator request with a non-2xx status. There is
none. Both 500s carry `konan-` request ids (E13), and the baseline scrape taken *before*
any probe of `/products/3` showed `http_exceptions_total` with no series at all and only
200/201 in `http_requests_total` (E12) — zero errors in this process's life up to that
point. This is not a sampling artifact: the file is complete from the single startup
marker with no rotated backups (E15), and the last non-investigator request was at
12:32:06.050Z (E7). The user's error page therefore predates this process life, or came
from elsewhere. H3 remains a plausible mechanism for what they saw; the attribution is
unproven.

### H5 — Resource saturation or process churn — **invalidated**

All three predicted signals fail. One startup marker in a complete, unrotated file
(E15). `process_uptime_seconds` rises monotonically 43.79 → 147.12 with no reset, and
`process_max_rss_bytes` is byte-identical at 47415296 across those ~103 seconds (E16).
The memory-leak, OOM and crash-loop forms are directly refuted. Non-memory saturation is
excluded by sufficiency rather than measurement — see Gaps.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Confirm with whoever owns the environment whether the chaos toggle at 12:31:54.621Z
   was intended, and by whom — the marker carries `request_id 56c5f7e95281`, which can
   be correlated in any upstream access log.
2. Re-read `/metrics` for `faultline_chaos_enabled` before drawing any conclusion about
   whether the shop has recovered; the gauge, not `/health`, is the state of this fault.
3. If the "error page" matters, look outside faultline's surface for it: proxy or load
   balancer access logs, or an error-tracking event, covering the minutes **before**
   12:31:48.628Z. Nothing inside the lab's telemetry can settle it.
4. Treat latency SLOs as measurable only on business routes. `/health` is exempt from
   this fault class by construction and will read green through it.
5. When reading `/metrics` after this investigation, subtract the two
   `ZeroDivisionError` exceptions and two `/products/{product_id}` 500s — they are
   investigator-induced (E12 vs E17).

## Gaps

- **The reported error page is unresolvable from this surface.** The process started at
  12:31:48.628Z and `lab/logs/` holds `app.log` alone, with no `.1`–`.3` backups (E15).
  No telemetry survives from before that instant, so a user error page from earlier
  cannot be confirmed or refuted here.
- **No client-side or edge telemetry** (browser, proxy, CDN, load balancer) is on the
  investigator's surface. The competing explanation for the error page — a client
  timeout rendered as an error page against the ~1.4s injected delay — could not be
  tested at all.
- **User impact after 12:32:06.050Z is unmeasured.** No non-investigator traffic arrived
  after that line (E7), so persistence of the fault was confirmed by our own probes
  (E11), not by observing users continuing to suffer.
- **The `/health` and `/metrics` exemption is inferred from timing**, not read from
  code. The middleware implementing the carve-out is outside the surface contract.
- **Non-memory saturation was not directly excluded.** `process_max_rss_bytes` is a
  high-water mark, and the surface carries no current-RSS, CPU, thread-pool or
  event-loop metrics. That family is ruled out by sufficiency — H1 fully explains the
  latency with a declared, still-active injected delay — not by measurement.
