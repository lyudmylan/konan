---
konan_journal: 1
investigation:
  id: 2026-08-06-products-3-user-500s
  trigger: alert-inbox (lab profile, alerts/inbox.jsonl, fingerprint lab-1786010643; delivered live by the shift watch)
  complaint: |-
    {"source": "alert", "fingerprint": "lab-1786010643", "labels": {"alertname": "HighErrorRate", "severity": "critical"}, "annotations": {"summary": "error-rate alert: repeated HTTP 500 responses on product page requests; multiple users affected in the last minutes"}, "startsAt": "2026-08-06T10:04:03Z"}
  started: "2026-08-06T10:04:16Z"
  concluded: "2026-08-06T10:18:00Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/3 raises an unhandled ZeroDivisionError in get_product's turnover_score computation (units_ordered / product[\"units_in_stock\"]) because product 3 (Unobtainium Ingot) is served with units_in_stock 0 — a zero denominator — so every request for that product, including the six user requests at 2026-08-06T10:04:03Z, returns HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/3 fails deterministically with an unhandled ZeroDivisionError raised in the get_product handler at the turnover_score computation (units_ordered / product[\"units_in_stock\"]) because product id 3 (Unobtainium Ingot) is served with units_in_stock 0; at 2026-08-06T10:04:03Z six non-investigator requests hit that input within 79 ms and every one received HTTP 500, while sibling catalog requests in the same second succeeded."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The 500 burst was operator-injected degradation (chaos mode) or probabilistic per-request failure, not a per-input code defect."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E5, E6]
  - id: H3
    statement: "The 500s stem from process-level trouble — restart, crash loop, or resource exhaustion — rather than an application code path."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E3, E4, E5]
latent_findings:
  - statement: "Catalog data anomaly, unchanged from the 2026-08-05 journal: product id 4 (Mystery Box) is served with price:null in the /products payload; HTTP 200, no failure observed from it on the read surface."
    evidence: [E7]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1786010656-64653 (2026-08-06T10:04:16Z) — 8233 s back-computes to process start 2026-08-06T07:47:04Z; the process lifetime spans the burst with no restart"
    quote: |-
      {"status":"ok","uptime_seconds":8233.154887582874}
      -- HTTP 200 in 0.001881s request_id=konan-1786010656-64653
  - id: E2
    type: metric
    source: "/metrics @ request_id konan-1786010657-64658 (2026-08-06T10:04:17Z, 14 s after the burst)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 7
      http_exceptions_total{type="ZeroDivisionError"} 7
      faultline_chaos_enabled 0
      process_uptime_seconds 8233.46512675006
      process_max_rss_bytes 46940160
  - id: E3
    type: metric
    source: "/metrics @ request_id konan-1786007714-63458 (2026-08-06T09:15:15Z — pre-incident reference scrape, 49 min before the burst; its single 500/exception was investigator probe konan-1786006758-62862, see E8)"
    quote: |-
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
      http_exceptions_total{type="ZeroDivisionError"} 1
      faultline_chaos_enabled 0
      process_max_rss_bytes 46940160
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-06T10:04:03.215Z and .222Z — first burst request, exception line (stack trimmed to final frames) plus its access line, same request_id"
    quote: |-
      {"ts": "2026-08-06T10:04:03.215Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "76d12cc0356e", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
        File "/Users/lyudmylan/Projects/faultline/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
      {"ts": "2026-08-06T10:04:03.222Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "76d12cc0356e", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.845, "client": "127.0.0.1:56051"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-06T10:04:03.236-03.294Z — the remaining five burst access lines; each is paired (same request_id) with an unhandled_exception line, exception_type ZeroDivisionError, at .234/.249/.263/.278/.292"
    quote: |-
      {"ts": "2026-08-06T10:04:03.236Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "46889869e5e8", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.752, "client": "127.0.0.1:56052"}
      {"ts": "2026-08-06T10:04:03.251Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "e9a2c13a477c", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.44, "client": "127.0.0.1:56053"}
      {"ts": "2026-08-06T10:04:03.266Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "ff47a9a19f86", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.423, "client": "127.0.0.1:56054"}
      {"ts": "2026-08-06T10:04:03.280Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "faee278cc984", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.588, "client": "127.0.0.1:56055"}
      {"ts": "2026-08-06T10:04:03.294Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "d1778a991547", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.533, "client": "127.0.0.1:56056"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-06T10:04:03.308Z and .320Z — the two requests immediately following the burst, same second"
    quote: |-
      {"ts": "2026-08-06T10:04:03.308Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "16fe8908675e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.813, "client": "127.0.0.1:56057"}
      {"ts": "2026-08-06T10:04:03.320Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "47bdc066a2cc", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.463, "client": "127.0.0.1:56058"}
  - id: E7
    type: probe
    source: "GET /products @ request_id konan-1786011027-64831 (~2026-08-06T10:10:27Z), full body — product 3 is the catalog's only zero-stock item"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001952s request_id=konan-1786011027-64831
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-06T08:59:18.982Z and .990Z — the pre-incident investigator-stamped trigger of the same signature, exception line plus its paired access line, same request_id"
    quote: |-
      {"ts": "2026-08-06T08:59:18.982Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1786006758-62862", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
      {"ts": "2026-08-06T08:59:18.990Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1786006758-62862", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.981, "client": "127.0.0.1:55651"}
gaps:
  - "The chaos-flag reading that helps kill H2 is a snapshot 14 s after the burst; the judge's settling item — a toggle audit trail covering 10:04:03Z itself — is outside the surface. In-surface mitigation: docs/lab.md lists chaos_enabled/chaos_disabled as logged events, and no such event exists anywhere in the log; a toggle mechanism that logs nothing cannot be excluded from inside the surface."
  - "No continuous resource/process trace exists between the 09:15:15Z and 10:04:16Z scrapes (judge's H3 residual); host- or supervisor-level traces are outside the surface. The invalidation rests on uptime continuity, an unchanged max-RSS high-water mark bracketing the incident, and sub-9 ms burst durations."
  - "Traffic origin is outside the surface: the six failing requests carry only loopback client ports (56051-56056). Why user traffic began hitting /products/3 at exactly 10:04:03Z — and whether the six requests are six users or one client retrying — cannot be determined from target-side telemetry; 'multiple users affected' is supported only as six distinct unstamped requests."
  - "During triage the software-defect lens read journals/2026-07-30-products-3-500s.md — permitted for the shift (past journals are the blinding contract's stated exception) but outside the minimal telemetry-only surface its prompt declared; the lens flagged this itself and re-derived every cited claim from lab/logs/app.log. Recorded for audit honesty."
usage:
  model: claude-fable-5
  tokens: null
  wall_clock_seconds: 824
---

# HighErrorRate: the latent /products/3 ZeroDivisionError went user-facing — six user 500s in 79 ms

## Summary

Verdict: **root-cause-identified**. At 2026-08-06T10:04:03Z six non-investigator
requests to `GET /products/3` failed with HTTP 500 inside 79 ms — the complaint's
"repeated HTTP 500 responses on product page requests" is confirmed as real user
impact. The mechanism is a deterministic, data-dependent software defect: the
`get_product` handler computes `turnover_score` as
`units_ordered / product["units_in_stock"]`, and product 3 (Unobtainium Ingot) is the
catalog's only item served with `units_in_stock: 0` (E7) — a zero denominator, so the
handler raises an unhandled `ZeroDivisionError` on every request for that product
(E4, E5). Sibling requests in the same second succeeded (E6), the rest of the catalog
is healthy, chaos is off (E2), and the process ran continuously through the incident
(E1). This is the same defect root-caused as a *latent* finding on 2026-07-30 — until
today only investigator probes had ever triggered it; as of 10:04:03Z it is
user-facing. Confidence: high — the counter deltas between the pre-incident and
post-burst scrapes reconcile with the log lines with zero residue (E3 vs E2).

## Timeline

- 2026-07-30 — defect first root-caused from konan probes; recorded latent
  (journals/2026-07-30-products-3-500s.md).
- 2026-08-06T07:47:04Z — current process starts (E1 uptime back-computation).
- 2026-08-06T08:59:18Z — investigation 1's probe re-confirms the defect, still
  konan-only (E8); pre-incident counters: one 500, one exception, both mine (E3).
- **2026-08-06T10:04:03.215-03.294Z — the incident: six unstamped requests to
  /products/3, six 500s, six ZeroDivisionError exceptions, distinct client ports
  56051-56056 (E4, E5).**
- 2026-08-06T10:04:03.308-03.320Z — same second: /products and /products/1 return 200
  (E6) — the failure is input-isolated.
- 2026-08-06T10:04:03Z — alert startsAt (matches the burst to the second).
- 2026-08-06T10:04:16Z — investigation starts (trigger latency 13 s; the alert was
  delivered live by the shift watch, not polled).
- 2026-08-06T10:04:17Z — post-burst scrape: 500-count and exception-count both 7,
  chaos 0, RSS unchanged (E2).
- 2026-08-06T10:10:27Z — catalog payload probe: product 3 served with
  units_in_stock 0, the only zero-stock item (E7).

## Investigation

**Baseline** (10:04:16-17Z): health 200 with uptime spanning the incident (E1); full
metrics scrape (E2) diffed against investigation 1's closing scrape (E3) — the delta
is exactly the incident: +6 product-id 500s, +6 ZeroDivisionError, +1 /products 200,
+1 /products/{id} 200; log window 09:15:16Z->10:04:17Z enumerated completely (16
lines: the burst, its two sibling successes, and my two probes — nothing else).

**Triage**: one lens spawned — *software-defect*, the only lens whose domain the
baseline could not exclude. Its findings: named throw site 6/6 deterministic, first
non-konan triggers on record; data-dependent isolation (id 3 fails while id 1 and the
list succeed in the same second); total concentration (every exception and every 5xx
in the log's history is this one signature; no chaos/injection events anywhere).
*infra-process* was excluded with evidence (uptime continuity E1, flat max-RSS E2 vs
E3, sub-9 ms burst durations E4/E5); *interfaces* likewise (chaos gauge 0 at E2,
zero chaos events in the log, deterministic per-input concentration E4/E5/E6 — the
opposite of probabilistic degradation). Lens-boundary note: the lens read the
2026-07-30 journal (permitted for the shift; outside its own prompt's minimal
surface) and flagged it itself — recorded under Gaps.

**Deep-dive**: no agents — H1's one open prediction (the served denominator is
literally zero) was settled by a single orchestrator probe of the catalog payload
(E7). H2/H3 carried complete disconfirming evidence from baseline.

**Judge** (fresh subagent, claims + verbatim evidence only): H1 validated — "a
closed, mutually-reconciling chain rather than loose correlation"; H2 invalidated
(both disjuncts contradicted); H3 invalidated (uptime, RSS high-water mark, and the
stack trace itself). The judge's residual caveats (post-hoc chaos snapshot; scrape
spacing; E8's missing access line) are addressed: E8 here carries its paired access
line, and the other two are recorded under Gaps with their in-surface mitigations.

**Probe accounting**: my investigation traffic this round — one /health, one
/metrics, one /products (E1, E2, E7), all konan-stamped; the /products probe bumped
its 200-counter 4->5 after E2. No investigator request contributed to the incident's
counters: the six 500s at 10:04:03Z are all unstamped (E4, E5).

## Hypotheses

### H1 — validated (root cause): data-dependent ZeroDivisionError on /products/3

The stack trace names the operation and line (E4); ZeroDivisionError requires the
denominator to be exactly 0 at evaluation, and the served catalog shows product 3 as
the only zero-stock item (E7) — mechanism proven, not inferred. Six unstamped
requests, 6/6 failures, 1:1 exception pairing by request id (E4, E5); siblings
succeed in the same second (E6); counter deltas reconcile exactly (E3 -> E2: +6/+6).
The defect predates the incident and was previously konan-only (E8) — what changed at
10:04:03Z is the arrival of user traffic on the poisoned input, not the code's
behavior.

### H2 — invalidated: injected or probabilistic degradation

Chaos gauge 0 fourteen seconds post-burst (E2); failures concentrated 6/6 on one
input with a genuine application stack trace (E4, E5) while adjacent same-second
requests pass 2/2 (E6) — a per-request injector would be expected to clip siblings.
No chaos_enabled/chaos_disabled/chaos_failure event exists anywhere in the log.
Residual (out of surface): a toggle audit trail covering the burst instant — see
Gaps.

### H3 — invalidated: process-level trouble

Uptime 8233 s observed 13 s after the burst spans it without a break (E1, E2);
max-RSS — a high-water mark that cannot decrease — is byte-identical across scrapes
bracketing the incident (E3, E2); burst requests completed in 2.4-8.8 ms (E4, E5),
the profile of a fast in-process exception, not starvation; and the fault sits
provably inside an application code path (E4). Residual (out of surface): continuous
resource traces between scrapes — see Gaps.

## Safe next steps

- Treat any further growth of `http_requests_total{path="/products/{product_id}",status="500"}`
  or `http_exceptions_total{type="ZeroDivisionError"}` beyond 7 as continued user
  impact on /products/3 (E2 is the reference point); unstamped request ids in the
  paired log lines distinguish users from konan probes.
- The defect and its trigger condition (zero-stock product served to the detail
  endpoint) are fully characterized here and in journals/2026-07-30-products-3-500s.md;
  remediation is out of scope for this journal, and the lab's defects are its
  contract (AGENTS.md) — no fix is proposed.
- If "multiple users" needs to be firmed up beyond six distinct unstamped requests,
  the traffic source's own logs (outside this surface) would settle users-vs-retries.
- Product 4's price:null (latent, unchanged) remains worth tracking when the order
  surface is next exercised.

## Gaps

Elaborated in the frontmatter list: the chaos-toggle audit and continuous resource
traces the judge named as settling evidence for the two invalidated hypotheses sit
outside the surface contract (with their in-surface mitigations noted); traffic
origin behind the six user requests is unknowable from target telemetry; and the
triage lens's read of a past journal — permitted shift-wide, outside its own minimal
prompt surface — is recorded transparently.
