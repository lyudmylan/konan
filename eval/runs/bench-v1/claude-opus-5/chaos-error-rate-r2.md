---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-injection-503s
  trigger: "manual — /konan human adapter (docs/triggers.md human profile); source human, fingerprint human-1787111597, labels.alertname human-report, no severity stated by the reporter; startsAt 2026-08-19T03:53:17Z; investigation start 2026-08-19T03:53:24Z (trigger latency 7s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-19T03:53:24Z
  concluded: 2026-08-19T03:59:14Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime fault-injection flag (chaos mode) was enabled on the live target at 2026-08-19T03:52:59.899Z with failure_rate 0.4 and error_status 503, short-circuiting a random ~40% of shop requests with HTTP 503 before they reach handler code, while /health is exempt from the injection."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime fault-injection flag (chaos mode) was enabled at 2026-08-19T03:52:59.899Z with failure_rate 0.4 and error_status 503, causing a random ~40% of shop requests to be short-circuited with HTTP 503 regardless of route or input, with /health exempt."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E11]
    evidence_against: []
  - id: H2
    statement: "The reported intermittent user failures are caused by the unhandled ZeroDivisionError in the product detail handler at shop.py:64."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E8, E9]
    evidence_against: [E10, E12]
  - id: H3
    statement: "The failures are caused by a process crash/restart loop — workers dying and recovering, which would explain 'works again on retry'."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14, E15]
  - id: H4
    statement: "The failures are caused by resource exhaustion or load saturation — queueing, memory growth, or worker starvation."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E16, E17]
latent_findings:
  - statement: "Unguarded division at shop.py:64 ('turnover_score': units_ordered / product['units_in_stock']) raises ZeroDivisionError and returns HTTP 500 for any product whose units_in_stock is 0 — currently product 3 ('Unobtainium Ingot'). Deterministic per input. Only investigator probes (konan- request ids) have triggered it; no user traffic reached it. It will affect users whenever any product's stock reaches zero."
    evidence: [E8, E9, E10]
  - statement: "The health check is a blind monitor for this class of incident: /health is exempt from the chaos injection and never traverses a shop path, so it returned 200 throughout while shop routes failed. This is why the reporter's dashboard was green during active user impact."
    evidence: [E7, E1]
  - statement: "Metrics label the chaos-injected failures with the raw request path (/products/1) while successes for the same route are labelled with the route template (/products/{product_id}). Per-route error rate is therefore not computable, and a dashboard grouping on the template sees /products/{product_id} as 100% healthy during the incident — a second, independent reason the dashboard reads green."
    evidence: [E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:52:59.899Z"
    quote: '{"ts": "2026-08-19T03:52:59.899Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "82c6d2829750", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:53:03.020Z"
    quote: '{"ts": "2026-08-19T03:53:03.020Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ef7153d2c77d", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:53:10.433Z"
    quote: '{"ts": "2026-08-19T03:53:10.433Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5b3903834cd2", "event": "chaos_failure", "method": "GET", "path": "/orders"}'
  - id: E4
    type: log
    source: "lab/logs/app.log — counted over user-traffic access lines (non-konan request ids), windows 2026-08-19T03:52:52.631Z–03:52:56.838Z and 03:53:01.960Z–03:53:11.492Z"
    quote: "Pre-marker window: 6 user requests, 0 failures. Post-marker user window: 10 user requests, 4 x 503 = 40.0%, matching the configured failure_rate 0.4. The 4 failures are chaos_failure lines on /products/1 (x2), /products, /orders. The same path /products/1 both failed (03:53:09.375Z, 503) and succeeded (03:52:53.714Z, 200) for user traffic."
  - id: E5
    type: probe
    source: "/products/1 — request ids konan-1787111689-43138 then konan-1787111691-43146"
    quote: '-- HTTP 503 request_id=konan-1787111689-43138 body {"error":"service temporarily degraded"} ... then -- HTTP 200 request_id=konan-1787111691-43146 with a full product body'
  - id: E6
    type: probe
    source: "/products — three consecutive probes, request ids konan-1787111692-43152, konan-1787111694-43158, konan-1787111696-43170"
    quote: '-- HTTP 503 in 0.000965s request_id=konan-1787111692-43152 {"error":"service temporarily degraded"} / -- HTTP 503 in 0.000936s request_id=konan-1787111694-43158 {"error":"service temporarily degraded"} / -- HTTP 200 in 0.001309s request_id=konan-1787111696-43170 [full product list]'
  - id: E7
    type: metric
    source: "/metrics @ request_id=konan-1787111804-43331"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 10 — and no /health series with any non-200 status exists in the scrape.'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:55:00.094Z (stack trace trimmed to the throwing frame)"
    quote: '{"ts": "2026-08-19T03:55:00.094Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787111700-43182", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E9
    type: metric
    source: "/metrics @ request_id=konan-1787111804-43331"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:55:00.103Z and 2026-08-19T03:55:01.990Z"
    quote: '{"ts": "2026-08-19T03:55:00.103Z", ... "message": "GET /products/3 -> 500", "request_id": "konan-1787111700-43182", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.692} / {"ts": "2026-08-19T03:55:01.990Z", ... "message": "GET /products/3 -> 500", "request_id": "konan-1787111701-43194", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.668} — both request ids carry the konan- investigator prefix; user traffic carries 12-char hex ids.'
  - id: E11
    type: metric
    source: "/metrics @ request_id=konan-1787111804-43331"
    quote: "faultline_chaos_enabled 1 / process_uptime_seconds 232.96022983407602"
  - id: E12
    type: log
    source: "lab/logs/app.log — filter over all access lines with a non-konan request id and 4xx/5xx status"
    quote: 'Exactly 4 such records exist, all the chaos-injected 503s of E4; zero user-traffic 500s appear anywhere in the log. The last user-traffic request line in the file is: {"ts": "2026-08-19T03:53:11.492Z", ... "message": "GET /products/4 -> 200", "request_id": "1d67c0a99b19", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 1.076}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:52:51.906Z — the only startup marker in the file"
    quote: '{"ts": "2026-08-19T03:52:51.906Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E14
    type: metric
    source: "/metrics — five successive scrapes across the investigation"
    quote: "process_uptime_seconds read 50.11056866706349, then 117.68461283412762, then 130.4079014591407, then 142.68437170912512, then 232.96022983407602 — strictly increasing, no reset, consistent with the single 2026-08-19T03:52:51.906Z start."
  - id: E15
    type: metric
    source: "/metrics — http_requests_total across all scrapes"
    quote: "http_requests_total counters only ever increased across all scrapes; no counter reset was observed."
  - id: E16
    type: metric
    source: "/metrics — scrapes at uptime 50.11s, 117.68s, 142.68s, 232.96s"
    quote: "process_max_rss_bytes 46759936 — byte-identical at every scrape across the whole window."
  - id: E17
    type: metric
    source: "lab/logs/app.log access lines and /metrics @ request_id=konan-1787111804-43331"
    quote: 'Failing requests are faster than successful ones on the same route: "GET /products/4 -> 503" duration_ms 0.151 vs "GET /products/4 -> 200" duration_ms 0.507; "GET /products -> 503" duration_ms 0.159 vs "GET /products -> 200" duration_ms 0.444. Aggregate http_request_duration_seconds_sum{method="GET",path="/products"} 0.003305917140096426 over _count 7 = 0.47ms mean. E1 records "extra_latency_ms": 0.'
  - id: E18
    type: metric
    source: "/metrics @ request_id=konan-1787111804-43331"
    quote: 'http_requests_total{method="GET",path="/products/1",status="503"} 3 / http_requests_total{method="GET",path="/products/4",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2 — the 503s never appear under the route template, and the 200/500s never appear under a raw id.'
gaps:
  - "Who enabled chaos mode, and why, could not be determined: the /chaos operator surface is outside the probe allowlist by contract (docs/lab.md), so the actor behind request_id 82c6d2829750 is not identifiable from the investigator's surface. That the toggle arrived with a 12-char hex request id (the non-investigator format) is the only attribution evidence available."
  - "Current user impact could not be measured: no user traffic appears after 2026-08-19T03:53:11.492Z (E12), so the incident's ongoing blast radius is inferred from the still-set flag (E11), not observed."
  - "The 40% observed failure rate rests on a 10-request post-marker window (E4), which is statistically weak on its own. The claim is carried instead by the per-request chaos_failure instrumentation (E2, E3), which names the mechanism directly rather than inferring it from a rate."
  - "The judge's settling item for H3 could not be obtained: this surface exposes no PID or process_start_time_seconds metric, so a multi-worker restart masked by scrape-to-scrape worker mixing is excluded only indirectly, via monotonic uptime (E14) and byte-identical max_rss (E16)."
  - "The judge's settling item for H4 could not be obtained: the surface has no queue-depth or in-flight concurrency instrumentation, and process_max_rss_bytes is a peak gauge rather than current RSS. Saturation is excluded from flat peak RSS (E16), inverted failure latency (E17), and request volume, not from direct concurrency data."
  - "The user blast radius of the latent ZeroDivisionError could not be measured: user traffic had already stopped before the defect was first triggered, so 'no user 500s' (E12) partly reflects absent users rather than a harmless defect."
usage:
  model: claude-opus-5
  tokens: 2034527
  wall_clock_seconds: 350
---

# Intermittent shop 503s from chaos-mode fault injection enabled on the live target

## Summary

**Root cause identified.** A runtime fault-injection flag ("chaos mode") was enabled on
the running faultline process at 2026-08-19T03:52:59.899Z with `failure_rate 0.4` and
`error_status 503` (E1). Since that moment a random ~40% of shop requests are
short-circuited with HTTP 503 and the body `{"error":"service temporarily degraded"}`
before they reach handler code — independent of route and of input. This reproduces the
reported symptom exactly: the same URL fails and then succeeds on retry (E5, E6), and
failures are spread across unrelated routes `/products`, `/products/{id}` and `/orders`
(E2, E3, E4).

The dashboard is green for a structural reason, not a lucky one: `/health` is exempt from
the injection and never traverses a shop path, so it returned 200 on all 10 requests with
no non-200 series existing at all (E7). A second, independent reason compounds it — the
injected failures are counted under the raw path label while successes for the same route
are counted under the route template, so a dashboard grouping on `path` sees
`/products/{product_id}` as fully healthy throughout (E18).

The flag is **still set** at the time of writing: `faultline_chaos_enabled 1` at
`process_uptime_seconds 232.96` (E11). Impact is ongoing for any user traffic that arrives.
Confidence is high — this is not a correlation argument: the service's own per-request
instrumentation labels each failure `event: chaos_failure` (E2, E3), naming the mechanism
rather than implying it.

Three competing explanations were tested and killed: an unhandled `ZeroDivisionError`
(H2), a crash/restart loop (H3), and load saturation (H4). One real but separate defect
was found and is recorded as latent, not as the incident.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 03:52:51.906 | faultline 0.1.0 starts — the only startup marker in the log | E13 |
| 03:52:52.631 – 03:52:56.838 | Pre-change window: 6 user requests, 0 failures | E4 |
| **03:52:59.899** | **Configuration change marker — chaos mode enabled, `failure_rate 0.4`, `error_status 503`, `extra_latency_ms 0`** | **E1** |
| 03:53:03.020 | First failing request, 3.1s after the marker — `chaos_failure` on `/products/1` | E2 |
| 03:53:06.197 | `chaos_failure` on `/products` | E4 |
| 03:53:09.375 | `chaos_failure` on `/products/1` again — a path that had succeeded earlier | E4 |
| 03:53:10.433 | `chaos_failure` on `/orders` — a third, unrelated route | E3 |
| 03:53:11.492 | Last user-traffic request in the log (`GET /products/4 -> 200`) | E12 |
| **03:53:17** | **Complaint raised by the reporter (`startsAt`) — 17s after the change marker** | complaint object |
| 03:53:24 | Investigation starts (trigger latency 7s) | — |
| 03:55:00.094 | Investigator probe triggers a latent `ZeroDivisionError` on `/products/3` | E8, E10 |
| 03:58:24 | Flag still set: `faultline_chaos_enabled 1`, uptime 232.96s | E11 |

The complaint window is fully covered by the telemetry: the reporter's `startsAt`
(03:53:17Z) falls 17 seconds after the change marker, the log's only startup marker is
03:52:51.906Z (E13), and `lab/logs/` holds no rotated backups — so the file spans the
entire process life with no hidden earlier window.

## Investigation

**Baseline.** `/health` returned 200 with `uptime_seconds 46.4` — green, as reported. The
first `/metrics` scrape immediately contradicted that green: `faultline_chaos_enabled 1`,
a `POST /chaos/enable` in the counters, and 503s scattered across `/orders`, `/products`
and `/products/1` while the same routes also served 200s. Latency was flat and sub-2ms
everywhere, and `http_exceptions_total` was empty.

**Triage.** All three lenses were spawned in parallel and blind to each other. The
baseline already carried a decisive marker, but complaint framing is untrusted and
secondary causes hide behind obvious ones, so no lens was skipped. All three converged on
the chaos flag independently. The `infra-process` lens ruled out restart loops and
saturation; the `software-defect` lens ruled the incident out of its own domain and
surfaced the latent divide-by-zero; the `interfaces` lens quantified the onset and matched
the observed 40% to the configured rate.

**Deep-dive: skipped by design.** H1's triage evidence was already deterministic and
complete — per-request `chaos_failure` instrumentation plus a config marker plus a live
flag gauge. Deep-dives exist to fill evidence gaps, not to re-prove, so H1 went straight to
the judge. Budget spent: one triage round, zero deep-dive agents, one judge.

**Judge.** The judge validated H1 and invalidated H2, H3 and H4. It correctly attacked the
weakest link — that the 4/10 = 40% match is statistically thin on its own — and noted the
claim survives regardless, because it rests on named per-request instrumentation rather
than on the rate. Its one open scoping concern, whether the complaint window overlaps the
log window, is closed above in the Timeline. Its settling items for H3 and H4 name
instrumentation this surface does not expose; both are recorded under Gaps rather than
treated as satisfied.

## Hypotheses

### H1 — chaos-mode fault injection — **validated**

*For:* the change marker with exact parameters (E1); the service's own `chaos_failure`
event naming the mechanism per request on three unrelated routes (E2, E3); a clean
pre-change window against a 40% post-change failure rate matching the configured 0.4 (E4);
non-determinism on identical input, both in user traffic and under direct probe (E4, E5,
E6); `/health` exempt with no failure series at all (E7); the flag still set now (E11).

*Against:* nothing found. Disconfirming attempts — probing for a per-input pattern, looking
for pre-marker failures, checking whether `/health` merely got lucky — all failed to
disconfirm.

Note on classification: the injection code behaved exactly as configured. Nothing in the
application misbehaved, which is why this is `infra-process` (an operational change to a
live system) and not `software-defect`.

### H2 — ZeroDivisionError in the product detail handler — **invalidated**

*For:* the exception is real and deterministic — `shop.py:64`,
`units_ordered / product["units_in_stock"]` (E8), with two exceptions and two 500s counted
(E9).

*Against:* both 500s carry `konan-` request ids — the investigator's own probes (E10) — and
no user-traffic 500 exists anywhere in the log (E12). It is also deterministic per product
id (2 of 2 identical failures), which cannot produce "works again on retry"; the injection
produces that symptom directly. Recorded as a latent finding, not as the incident.

### H3 — process crash/restart loop — **invalidated**

*Against:* a single startup marker in the whole file (E13), strictly increasing uptime
across five scrapes with no reset (E14), and monotonic request counters with no reset
(E15). The process also absorbed both unhandled exceptions without dying.

### H4 — resource exhaustion / load saturation — **invalidated**

*Against:* peak RSS byte-identical across the entire window (E16); failing requests
consistently *faster* than successful ones on the same route, with `extra_latency_ms 0`
configured (E17) — saturation makes failures slower, not faster. Request volume (single
digits per route) cannot saturate anything.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

1. **Identify who enabled chaos mode and whether it was intended.** The change marker
   carries `request_id 82c6d2829750` (E1), a non-investigator id. The `/chaos` surface is
   outside konan's contract, so this needs an operator with access to that surface and to
   whatever fronts it. This is the one question that decides whether this is an incident or
   an authorized exercise — and it is the fastest path to ending user impact, since the
   flag is still set (E11).
2. **Treat the green dashboard as a finding in its own right.** Alerting keyed to `/health`
   is structurally incapable of seeing this class of failure (E7). Worth reviewing whether
   any monitor watches a business surface, and whether the label split in E18 hides
   per-route error rates on existing dashboards.
3. **Review the unguarded division at `shop.py:64`** (E8). It is latent only because no
   user has requested product 3 yet; it fires for any product whose `units_in_stock`
   reaches 0.
4. **Re-scrape `/metrics` for `faultline_chaos_enabled` to confirm when the flag clears**,
   and watch for user-traffic (hex request id) 5xx resuming — user traffic stopped before
   the incident could be measured at steady state.

## Gaps

- **Attribution of the change.** Who enabled chaos mode, and why, is not answerable from
  the investigator's surface: `/chaos` is outside the probe allowlist by contract
  (`docs/lab.md`). The only attribution evidence is that the toggle carried a 12-char hex
  request id, i.e. it did not come from an investigator probe.
- **Ongoing user impact is inferred, not observed.** No user traffic appears after
  03:53:11.492Z (E12), so present blast radius rests on the still-set flag (E11).
- **The 40% figure is thin on its own.** It comes from a 10-request window (E4). The
  hypothesis is carried by the `chaos_failure` instrumentation (E2, E3), not by the rate;
  the rate is corroboration.
- **H3 could not be settled by identifier.** This surface exposes no PID or
  `process_start_time_seconds`, so a multi-worker restart masked by scrape-to-scrape worker
  mixing is excluded only indirectly (E14, E16).
- **H4 could not be settled by direct concurrency data.** No queue-depth or in-flight
  instrumentation exists, and `process_max_rss_bytes` is a peak rather than current gauge
  (E16, E17).
- **The latent defect's user blast radius is unmeasured.** User traffic had stopped before
  it was first triggered, so "no user 500s" (E12) partly reflects absent users rather than a
  harmless defect.
