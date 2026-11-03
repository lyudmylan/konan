---
konan_journal: 2
investigation:
  id: 2026-11-03-routine-handover-check
  trigger: 'manual (/konan, alertname human-report, fingerprint human-1793701369; startsAt 2026-11-03T10:22:49Z, investigation start 2026-11-03T10:23:07Z, trigger latency 18s)'
  complaint: 'Routine on-call handover check: anything wrong with the shop service right now? No specific user reports.'
  started: '2026-11-03T10:23:07Z'
  concluded: '2026-11-03T10:28:31Z'
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "Product 4's null price causes request failures on the product read paths (a data-dependent defect)."
    incident_class: data-db
    state: invalidated
    evidence_for: [E9]
    evidence_against: [E10]
latent_findings:
  - statement: 'Product 4 (Mystery Box) carries price: null in the catalog data; both product read endpoints tolerate it (HTTP 200); the order path for product 4 is untested — only investigator probes ever touched product 4, and both recorded user orders used products 1 and 2.'
    evidence: [E9, E10, E7]
evidence:
  - id: E1
    type: probe
    source: 'probe /health, request_id konan-1793701402-28613, 10:23:22Z'
    quote: |-
      {"status":"ok","uptime_seconds":55.53811712493189}
      -- HTTP 200 in 0.001566s request_id=konan-1793701402-28613
  - id: E2
    type: metric
    source: 'probe /metrics, request_id konan-1793701407-28619, scrape 10:23:27Z — all http_requests_total series present'
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E3
    type: metric
    source: 'probe /metrics, request_id konan-1793701407-28619, scrape 10:23:27Z — counter declared, zero sample lines follow'
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E4
    type: metric
    source: 'probe /metrics, request_id konan-1793701407-28619, scrape 10:23:27Z'
    quote: 'faultline_chaos_enabled 0'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T10:22:27.431Z — the only startup event; the file is the complete history (no rotated backups)'
    quote: '{"ts": "2026-11-03T10:22:27.431Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T10:22:36.488Z — last non-investigator request; every request event in the file has status 200 or 201, duration_ms <= 14.08'
    quote: '{"ts": "2026-11-03T10:22:36.488Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "1f9622f53916", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.68, "client": "127.0.0.1:49655"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T10:22:32.326Z and 2026-11-03T10:22:33.381Z — both order_created events in the file; each followed by POST /orders -> 201'
    quote: |-
      {"ts": "2026-11-03T10:22:32.326Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "d7e298584580", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-11-03T10:22:33.381Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "c2c7c40fbe7b", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 2, "total_price": 46.0}
  - id: E8
    type: metric
    source: 'probe /metrics, request_id konan-1793701497-28693, scrape ~10:24:57Z (software-defect lens); http_exceptions_total still had no series at this scrape'
    quote: 'process_uptime_seconds 150.1'
  - id: E9
    type: probe
    source: 'probe /products, request_id konan-1793701492-28681, HTTP 200 (interfaces lens) — catalog entry for product 4'
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75}'
  - id: E10
    type: probe
    source: 'probe /products/4, request_id konan-1793701558-28719, 10:25:58Z'
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.004306s request_id=konan-1793701558-28719
  - id: E11
    type: metric
    source: 'probe /metrics, request_id konan-1793701407-28619, scrape 10:23:27Z'
    quote: 'process_max_rss_bytes 47693824'
  - id: E12
    type: metric
    source: 'probe /metrics, infra-process lens follow-up scrape ~10:24:40Z — identical to the baseline value ~70s earlier'
    quote: 'process_max_rss_bytes 47693824'
gaps:
  - 'Telemetry begins at the process start 2026-11-03T10:22:27Z: lab/logs/app.log is the complete history with no rotated backups, and all counters start there — the time before that start is unobservable from the permitted surface.'
  - 'The observation window covers ~3 minutes of traffic; a low-rate or intermittent fault below that resolution would not show.'
  - 'POST /orders with product 4 (the null-price product) cannot be tested: writes are outside the read-only investigator boundary, so whether the order path tolerates the null price is unknown.'
usage:
  model: claude-fable-5
  tokens: 1348458
  wall_clock_seconds: 324
---

# Routine handover check — shop service healthy, one latent data flag

## Summary

Verdict: **no active incident.** The shop service (faultline 0.1.0) serves all traffic
correctly: every request counter is 2xx with no 4xx/5xx series (E2), the exception
counter has zero samples over the whole process lifetime (E3, E8), latency is at or
below 14 ms including cold start (E6), the chaos switch is off (E4), and the process is
stable — one start event, monotonic uptime, unchanged peak RSS (E5, E8, E11, E12). The
complaint was a routine handover check with no reported symptoms, and the telemetry
agrees with "healthy". One latent finding rides along: product 4 ("Mystery Box")
carries a null price in the catalog (E9); read paths tolerate it (E9, E10), but no
order has ever touched it (E7), so the write path's behavior is unknown. Confidence is
high within the observation window; the window itself is short (~3 minutes — see Gaps).

## Timeline

- **2026-11-03T10:22:27.431Z** — faultline 0.1.0 starts; the only startup marker, and
  the beginning of all available telemetry (E5). No configuration, flag, or chaos
  change markers appear at any point after it (E4; no chaos_* or simulated_exception
  events in the log).
- **10:22:28Z–10:22:36Z** — non-investigator user traffic: product browsing and two
  orders, all 200/201 (E6, E7).
- **10:22:49Z** — complaint raised (human report, routine handover check).
- **10:23:07Z** — investigation starts (trigger latency 18 s).
- **10:23:22Z–10:23:27Z** — baseline: health OK (E1), metrics all-2xx (E2–E4, E11).
- **~10:24:30Z–10:25:00Z** — three triage lenses probe in parallel (E8, E9, E12).
- **10:25:58Z** — decisive probe GET /products/4 returns 200 (E10); H1 killed.
- **10:28:31Z** — judge verdicts in; investigation concludes.

## Investigation

Complaint object, verbatim, as synthesized by the /konan adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1793701369",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-03T10:22:49Z"
}
```

Investigation start: 2026-11-03T10:23:07Z (trigger latency 18 s).

Rounds as they ran: baseline (health, metrics, full log read) showed a clean surface
and a fresh process start. Because the complaint was vague, all three lenses ran in
parallel — infra-process, interfaces, software-defect — each blind to the others.
Infra-process: clean lifecycle, no saturation, no switch active (E5, E8, E12).
Software-defect: zero exceptions, no 5xx, order path correct both times it ran (E3,
E6, E7). Interfaces: no active anomaly, but one observation — product 4 has a null
price (E9). That observation became H1; one targeted orchestrator probe (E10) was its
decisive test. The adversarial judge then ruled on evidence only: the no-active-incident
claim validated, H1 invalidated, the latent finding validated.

## Hypotheses

### H1 — Product 4's null price breaks the product read paths (invalidated)

The catalog shows `"price":null` for product 4 (E9), the classic shape of a
data-dependent failure. The prediction: GET /products/4 fails or errors. The probe
refutes it: HTTP 200 with the null price serialized in the body (E10), and the catalog
listing itself also returned 200 with the record present (E9). The read paths tolerate
the null value. The judge's verdict: invalidated. What would have settled it the other
way: one captured 4xx/5xx response or exception log line on /products or /products/4
traceable to the null price — none exists.

The surviving remainder is recorded as a latent finding, not a hypothesis: the null
price is real (E9, E10), only investigator probes ever touched product 4, and both
recorded user orders used products 1 and 2 (E7), so the order path for product 4 is
untested and cannot be tested read-only.

## Safe next steps

- At the next handover, scrape /metrics once and compare against E2: any new series
  with a 4xx/5xx status label is the first sign of change from this baseline.
- If any user ever orders product 4, read the log lines for that request_id first —
  the null price (E9, E10) meets the order path's price arithmetic there (compare the
  numeric `total_price` fields in E7).
- Ask the catalog's data owner whether `price: null` on product 4 ("Mystery Box") is
  intentional. This is a question, not a change.

## Gaps

- **No pre-start telemetry.** The process started at 10:22:27Z (E5) and the log file is
  the complete history — no rotated backups exist. Nothing before that moment is
  observable from the permitted surface, so this journal says nothing about earlier
  behavior.
- **Short window.** All evidence covers ~3 minutes of traffic. A fault that fires
  rarely or under load would not show in a window this small.
- **Order path for product 4 untested.** POST /orders is a write; the read-only
  boundary forbids it. Whether the order path tolerates the null price is unknown —
  recorded as a latent finding, flagged for the data owner.
