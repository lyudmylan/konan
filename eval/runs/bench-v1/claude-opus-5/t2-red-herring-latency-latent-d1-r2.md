---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-wide-latency
  trigger: "manual — /konan human profile; complaint object source=human, fingerprint=human-1787143252, labels.alertname=human-report (no severity stated by reporter), startsAt=2026-08-19T12:40:52Z; investigation started 2026-08-19T12:40:59Z (trigger latency 7s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-19T12:40:59Z
  concluded: 2026-08-19T12:46:36Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change enabled chaos mode at 12:40:35.935Z, injecting randomized per-request latency bounded by 1500ms into shop routes while leaving /health and /metrics unaffected; the setting is still active."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode, enabled by a runtime configuration change at 12:40:35.935Z with extra_latency_ms 1500, injects randomized latency into shop routes and is the cause of the shop-wide slowness."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The reported error page was produced by the same chaos configuration's failure injection returning HTTP 503."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E9, E10, E11]
  - id: H3
    statement: "The reported error page was produced by a data-dependent code defect: GET /products/3 divides by units_in_stock, which is 0, raising ZeroDivisionError and returning HTTP 500."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E12, E13, E14]
    evidence_against: [E15, E11, E16]
  - id: H4
    statement: "A process restart or crash loop degraded the service."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E16, E17]
  - id: H5
    statement: "Resource exhaustion — memory pressure or worker/event-loop starvation — degraded the service."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E17, E18, E5, E7]
  - id: H6
    statement: "The slowness is service-wide including the monitoring endpoints, and the complaint's claim that health checks are green and fast is mistaken."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E7]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 deterministically: product 3 has units_in_stock 0 and the handler divides by it without a guard (ZeroDivisionError at shop.py:64). Both observed 500s were triggered by investigator probes; no user request reached this path in the retained window, so it is latent rather than the observed incident — but it is a live 500 source and the leading candidate for the reported error page."
    evidence: [E12, E13, E14, E15]
  - statement: "The health check does not traverse the degraded path: /health and /metrics returned in under 1ms while shop routes took over a second in the same window, so liveness monitoring is structurally blind to this class of incident."
    evidence: [E5, E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:40:35.935Z"
    quote: '{"ts": "2026-08-19T12:40:35.935Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "314410d935a9", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:40:35.936Z"
    quote: '{"ts": "2026-08-19T12:40:35.936Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "314410d935a9", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 3.124, "client": "127.0.0.1:60652"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:40:30.734Z (last known-good, pre-change)"
    quote: '{"ts": "2026-08-19T12:40:30.734Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e314ce08c866", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.895, "client": "127.0.0.1:60647"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:40:39.221Z (first known-bad, post-change, same route)"
    quote: '{"ts": "2026-08-19T12:40:39.221Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e8d8f6c2db69", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1217.557, "client": "127.0.0.1:60653"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:40:41.467Z through 12:40:45.876Z (post-change user traffic, all shop routes) and 12:42:24.674Z / 12:42:44.914Z (interleaved monitoring vs shop)"
    quote: 'GET /products/2 -> 200 duration_ms 1164.459; GET /products/1 -> 200 duration_ms 198.27; POST /orders -> 201 duration_ms 619.841; GET /orders -> 200 duration_ms 349.695. Interleaved: {"ts": "2026-08-19T12:42:24.674Z", "message": "GET /health -> 200", "request_id": "konan-1787143344-59264", "duration_ms": 0.427} versus {"ts": "2026-08-19T12:42:44.914Z", "message": "GET /products/1 -> 200", "request_id": "konan-1787143363-59315", "duration_ms": 1045.598}'
  - id: E6
    type: log
    source: "lab/logs/app.log — full post-onset shop-route duration set, 12:40:39.221Z onward"
    quote: 'duration_ms values (ms): 35.1, 198.3, 349.7, 442.9, 480.5, 596.5, 619.8, 1016.0, 1045.6, 1164.5, 1194.0, 1217.6 — spread across 0 to the configured 1500ms ceiling, no value above it'
  - id: E7
    type: probe
    source: "scripts/probe.sh /products (konan-1787143340-59251, konan-1787143345-59278); scripts/probe.sh /health and /metrics, same window"
    quote: '-- HTTP 200 in 1.196237s request_id=konan-1787143340-59251 ; -- HTTP 200 in 0.598657s request_id=konan-1787143345-59278 ; /health -- HTTP 200 in 0.001452s ; /metrics -- HTTP 200 in 0.001464s'
  - id: E8
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787143596-59459, at process_uptime_seconds 366.32"
    quote: 'faultline_chaos_enabled 1'
  - id: E9
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787143272-59200, before any investigator probe of an error path"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 3 / {method="GET",path="/orders",status="200"} 1 / {method="GET",path="/products",status="200"} 2 / {method="GET",path="/products/{product_id}",status="200"} 3 / {method="POST",path="/chaos/enable",status="200"} 1 / {method="POST",path="/orders",status="201"} 2 — every series 2xx; http_exceptions_total declared with no series'
  - id: E10
    type: log
    source: "lab/logs/app.log — full-file search for injected-failure markers"
    quote: 'no line matches chaos_failure or simulated_exception anywhere in the file'
  - id: E11
    type: log
    source: "lab/logs/app.log — status distribution over all access lines by request-id origin"
    quote: 'every unstamped (user) request in the window returned 200 or 201; unstamped traffic reached only /health, /products, /products/1, /products/2 and /orders (GET and POST) — no unstamped request to /products/3, and no unstamped non-2xx line exists'
  - id: E12
    type: probe
    source: "scripts/probe.sh /products/3, request_id=konan-1787143365-59321 (reproduced at konan-1787143373-59337)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787143365-59321"} -- HTTP 500 in 0.481919s'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:42:45.466Z"
    quote: '{"ts": "2026-08-19T12:42:45.466Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787143365-59321", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E14
    type: probe
    source: "scripts/probe.sh /products — response body, plus control probes of /products/1, /products/2, /products/4"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0} — while /products/1, /products/2 and /products/4 all returned HTTP 200, including /products/4 with "price":null'
  - id: E15
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787143596-59459, cross-checked against the two unhandled_exception log lines"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2 and http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2 — both corresponding log lines carry investigator-stamped ids konan-1787143365-59321 and konan-1787143373-59337'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:40:30.001Z, plus `ls lab/logs/`"
    quote: '{"ts": "2026-08-19T12:40:30.001Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"} — the only startup marker in the file; lab/logs/ contains app.log only, with no .1-.3 rotated backups'
  - id: E17
    type: metric
    source: "/metrics via scripts/probe.sh — five samples across the investigation"
    quote: 'process_uptime_seconds 41.9 -> 42.55 -> 112.35 -> 115.52 -> 173.04 -> 366.32, monotonic with no reset; http_requests_total monotonic with no reset'
  - id: E18
    type: metric
    source: "/metrics via scripts/probe.sh — three samples over ~130s of uptime"
    quote: 'process_max_rss_bytes 47415296 -> 47513600 -> 48693248'
gaps:
  - "No telemetry exists before 2026-08-19T12:40:30.001Z: the process started then and lab/logs/ holds no rotated backups (E16). The reported error page cannot be confirmed or excluded for any moment before that instant, and the pre-onset healthy baseline is only ~5s wide (n=1 per shop route)."
  - "The reported error page is unattributed. No user-originated 5xx exists in the retained window (E11), so the ZeroDivisionError defect (H3) remains a candidate mechanism rather than an observed cause. A reverse-proxy or upstream access log covering before 12:40:30.001Z, or the reporting user's approximate timestamp or request id, would settle it."
  - "The latency-injection mechanism is inferred from observed behaviour, not read. E1 records a scalar extra_latency_ms 1500 while observed durations spread from 35ms to 1218ms (E6); a fixed 1500ms addition is refuted by that spread, and a randomized draw bounded by 1500ms is the fit. The chaos middleware source is outside the investigator's surface, so the exact distribution is unverified."
  - "User-side impact is measured only through the 6 unstamped shop requests in the window; there is no client-side or edge telemetry, so client timeouts — a slow request a browser abandons and renders as an error page — can be neither confirmed nor excluded from this surface."
  - "Who made the configuration change, and why, is not on the investigator's surface: E2 shows the enabling request arrived over the wire from 127.0.0.1 with an unstamped id, but the operator surface (/chaos) is outside the probe allowlist by contract."
usage:
  model: claude-opus-5
  tokens: 1608253
  wall_clock_seconds: 337
---

# Shop-wide latency from an active chaos-mode configuration change

## Summary

**Root cause identified.** A runtime configuration change enabled chaos mode at
`12:40:35.935Z`, injecting randomized per-request latency bounded by 1500ms into the
shop routes (E1). The change is logged as a single WARNING marker delivered over the
wire as `POST /chaos/enable -> 200` (E2), and it sits exactly on the boundary between
healthy and degraded traffic: the same route went from 0.895ms (E3) to 1217.557ms (E4)
across that instant, a ~1360x step with no intermediate ramp. **The setting is still
active** — `faultline_chaos_enabled 1` at the last read, six minutes after onset (E8),
and live probes of `/products` still take 0.6–1.2s (E7).

Impact covers every shop route including the write path: product listing, product
detail, order creation and order listing all degraded (E5), while every request still
returned 200 or 201. The complaint's "health checks are green and fast" is **accurate,
not a misreading** — the injection spares `/health` and `/metrics`, which answered in
under 1ms in the same window that `/products/1` took 1045.598ms (E5, E7). That is the
healthy-monitoring trap in its textbook form: liveness monitoring here is structurally
incapable of seeing this incident.

The **"error page once" is not explained.** Two candidate mechanisms were tested. The
chaos configuration itself cannot produce errors — it carries `failure_rate: 0.0`, and
no 5xx or `chaos_failure` line exists anywhere in the retained telemetry (E1, E9, E10,
E11). A separate, real defect was found — `GET /products/3` returns HTTP 500
deterministically because product 3 has `units_in_stock: 0` and the handler divides by
it (E12, E13, E14) — but every 500 in existence was triggered by this investigation's
own probes (E15), and no user request reached that path (E11). It is a **latent finding
and the leading candidate**, not a confirmed cause. Confidence: high on the latency
cause, low on the error-page attribution.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 12:40:30.001 | Process starts — `faultline 0.1.0 started`. No telemetry is retained before this instant. | E16 |
| 12:40:30.7–12:40:32.9 | Healthy baseline: `/products` 0.895ms, `/products/1` 1.193ms, `POST /orders` 2.418ms. | E3 |
| **12:40:35.935** | **Configuration change marker** — chaos mode enabled: `failure_rate 0.0`, `error_status 503`, `extra_latency_ms 1500`. Arrived over the wire, unstamped id `314410d935a9`. | E1, E2 |
| 12:40:39.2–12:40:45.9 | All six subsequent user shop requests degraded: 1217.6ms, 1164.5ms, 198.3ms, 619.8ms, 349.7ms — all still 200/201. | E4, E5, E6 |
| 12:40:52 | Complaint raised by human reporter (`startsAt`); investigation starts 12:40:59. | — |
| 12:41:11 onward | Investigator probes: shop routes slow (0.6–1.2s), `/health` and `/metrics` under 1ms throughout. | E5, E7 |
| 12:42:45, 12:42:53 | Investigator probes of `/products/3` return HTTP 500, `ZeroDivisionError` — the only 500s in the window, both self-inflicted. | E12, E13, E15 |
| 12:46:36 | Chaos still enabled at `process_uptime_seconds` 366.32; no restart, no counter reset across the whole investigation. | E8, E17 |

## Investigation

**Baseline** — `/health`, `/metrics`, and the full 21-line log. The log had no rotated
backups, so the process's entire history was readable at once, which made the
before/after split unambiguous and bounded the window hard at 12:40:30.001Z.

**Triage** — all three lenses spawned in parallel (`infra-process`, `interfaces`,
`software-defect`), each blind to the others. No lens was skipped: the complaint mixed a
latency symptom, an error symptom, and a monitoring observation, so no domain could be
excluded on baseline evidence alone. All three independently converged on the
`chaos_enabled` marker as the onset boundary; the software-defect lens additionally
found the `/products/3` defect, and the infra lens ruled out the process-lifecycle and
saturation families with explicit negatives.

**Deep-dive** — none spawned. H1's triage evidence was already deterministic and
complete (logged config marker, step change on the same route, live reproduction,
still-active gauge), so per the loop it went straight to the judge rather than being
re-proved. The one genuine evidence gap — whether a user ever hit the 500 path — was
already answered exhaustively by triage against the full log, and no further probe could
reach behind 12:40:30.001Z. Spawning agents to re-derive that would have been ceremony.

**Judge** — one fresh adversarial judge, given the hypothesis list and verbatim evidence
only, with no narrative. It validated H1 while flagging two residuals now recorded under
Gaps (the injection mechanism is inferred, not read; the pre-onset baseline is thin);
invalidated H2, H4, H5 and H6; and ruled H3 inconclusive, drawing the distinction this
report keeps: the defect is validated, its attribution to the user's report is not.

Budget: one triage round, zero deep-dives, one judge — concluded within budget.

## Hypotheses

### H1 — Chaos-mode latency injection (validated) — root cause

A logged configuration event at a known instant (E1, E2), a step from 0.895ms to
1217.6ms across it with no ramp (E3, E4), the effect on four distinct shop routes
including a write path (E5), all twelve post-onset durations under the declared 1500ms
ceiling (E6), the flag still set at six separate metric reads (E8), and live
re-reproduction by probe (E7). Route selectivity is confirmed twice independently —
server-side in the access log and client-side in probe trailers. The enabling request id
`314410d935a9` is unstamped, so the investigation did not cause the condition it
reported. Nothing in the evidence argues against.

The word "randomized" is a reconstruction, not a reading: the scalar `extra_latency_ms:
1500` with a 35–1218ms observed spread refutes a fixed addition and fits a bounded random
draw. Recorded under Gaps.

### H2 — Chaos failure injection produced the error page (invalidated)

Refuted three ways by its own evidence. `failure_rate: 0.0` in the marker itself (E1);
every `http_requests_total` series was 2xx before any investigator error probe, with
`http_exceptions_total` empty (E9); no `chaos_failure` or `simulated_exception` line
exists (E10). Both of its predictions fail against direct observation.

### H3 — ZeroDivisionError on `/products/3` produced the error page (inconclusive)

The claim splits, and so does the evidence. *The defect is real and fully validated*:
product 3 carries `units_in_stock: 0` (E14), and two probes reproduced HTTP 500 with a
stack terminating at `shop.py:64`, `units_ordered / product["units_in_stock"]` (E12,
E13). Control probes isolate the trigger to that one field value — `/products/1`, `/2`
and `/4` all return 200, including `/4` with `"price": null` (E14), so this is not
general malformed-data handling.

*The attribution is not supported.* `http_exceptions_total{type="ZeroDivisionError"}` is
exactly 2, and both log lines carry investigator-stamped ids (E15) — every 500 in the
retained window was manufactured by this investigation. No unstamped request reached
`/products/3` at all (E11). E16 explains why this cannot be resolved from the file, but
explaining an evidentiary gap does not fill it. Reporting this as "the cause of the error
page" would assert a coincidence of kind as a match of instance; it rides along as a
latent finding instead.

### H4 — Restart or crash loop (invalidated)

Exactly one startup marker in the file (E16); `process_uptime_seconds` and
`http_requests_total` both monotonic across six samples with no reset (E17) — a restart
would have zeroed both.

### H5 — Resource exhaustion or worker starvation (invalidated)

RSS moved 47.42MB → 48.69MB over ~130s, about 2.7%, with no pressure signal or OOM event
(E18) — ordinary allocation, not exhaustion. The worker-starvation variant dies
independently: under a shared-resource bottleneck the cheap `/health` path would queue
behind the slow shop paths, and instead it returned in 0.427–0.519ms while shop requests
took over a second in the same window (E5, E7). Selective, path-dependent latency is
incompatible with a shared bottleneck.

### H6 — Complaint framing wrong about health checks (invalidated)

Tested because complaint framing is untrusted by default. Here the evidence vindicates
the reporter: monitoring endpoints were fast concurrently with slow shop paths at two
independent measurement points (E5, E7). The observation should be treated as reliable.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Confirm the configuration change was intended and by whom.** The marker shows a
   local, unstamped `POST /chaos/enable` (E2). Whoever owns the operator surface should
   check whether this was a deliberate exercise left running — the flag has now been
   active for over six minutes and is still injecting latency into live shop traffic
   (E8).
2. **Retrieve user-originated telemetry from before 12:40:30.001Z** — an edge or
   reverse-proxy access log, or the reporting users' approximate timestamps. This is the
   single artifact that would settle the error-page attribution (E16, E11).
3. **Treat `GET /products/3` as a live bug on its own merits**, independent of this
   incident: it 500s deterministically for any caller while product 3 holds
   `units_in_stock: 0` (E12, E14). Worth checking whether any other catalogue item can
   reach zero stock.
4. **Review what the health check covers.** `/health` stayed green and sub-millisecond
   through a service-wide user-facing degradation (E5, E7); alerting built on it will
   stay silent through this entire class of incident. A latency signal drawn from the
   business routes — the `http_request_duration_seconds` series already exposed per path
   — would have caught this at onset.

## Gaps

- **No telemetry before 12:40:30.001Z.** The process started then and `lab/logs/` holds
  no rotated backups (E16). Anything users experienced before that instant — including
  the reported error page — is unknowable from this surface, and the healthy baseline is
  only ~5s wide.
- **The error page is unattributed.** No user-originated 5xx exists in the retained
  window (E11); H3 stays a candidate mechanism, not an observed cause.
- **The injection mechanism is inferred, not read.** The observed 35–1218ms spread fits a
  random draw bounded by the logged 1500ms (E1, E6), but the chaos middleware source is
  outside the investigator's surface, so the distribution is unverified.
- **No client-side telemetry.** A slow request abandoned by a browser would render as an
  error page with no server-side 5xx. This cannot be confirmed or excluded from the six
  unstamped shop requests visible here.
- **The operator surface is out of contract.** `/chaos` is deliberately outside the probe
  allowlist, so who changed the configuration, and why, was not investigable.
- **Investigator-induced telemetry is disclosed, not hidden.** This investigation's own
  probes account for both 500s and several slow shop requests; user impact above is
  counted from unstamped traffic only (E11, E15).
