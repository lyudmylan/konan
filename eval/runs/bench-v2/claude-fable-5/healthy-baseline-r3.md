---
konan_journal: 2
investigation:
  id: 2026-11-03-routine-handover-check
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-03T10:41:51Z
  concluded: 2026-11-03T10:49:01Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "A degradation switch (chaos mode) inside the target is active and injects errors or latency into user traffic."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E15, E3, E6]
  - id: H2
    statement: "The target process is crashing or restarting in a loop, disrupting service."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1, E4]
    evidence_against: [E5, E14]
  - id: H3
    statement: "GET /products/3 deterministically fails with HTTP 500: the get_product handler (shop.py line 64) computes units_ordered / units_in_stock, and product 3 has units_in_stock 0, raising an unhandled ZeroDivisionError."
    incident_class: software-defect
    state: validated
    evidence_for: [E7, E9, E10, E11, E12, E13]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 (unhandled ZeroDivisionError: division by units_in_stock = 0 in get_product). In the observed window only investigator probes triggered it — user traffic never requested product 3. The defect is content-dependent, not requester-dependent: any user request for product 3 will fail until the zero-stock data or the handler changes."
    evidence: [E7, E9, E10, E11, E12]
evidence:
  - id: E1
    type: probe
    source: "GET /health @ request_id konan-1793702554-29434, 2026-11-03T10:42:34Z"
    quote: |-
      {"status":"ok","uptime_seconds":78.74701779102907}
      -- HTTP 200 in 0.002291s request_id=konan-1793702554-29434
  - id: E2
    type: metric
    source: "GET /metrics @ request_id konan-1793702555-29439, 2026-11-03T10:42:35Z"
    quote: faultline_chaos_enabled 0
  - id: E3
    type: metric
    source: "GET /metrics @ request_id konan-1793702555-29439, 2026-11-03T10:42:35Z (complete http_requests_total set at baseline)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E4
    type: metric
    source: "GET /metrics @ request_id konan-1793702555-29439, 2026-11-03T10:42:35Z"
    quote: process_uptime_seconds 79.39693145803176
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:41:15.916Z (third line of a newly created log file; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-03T10:41:15.916Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:41:20.840Z (one of the 9 user request lines 10:41:16-10:41:25Z, all status 200/201, all with unprefixed request ids)"
    quote: |-
      {"ts": "2026-11-03T10:41:20.840Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "b261ebf8fc92", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.062, "client": "127.0.0.1:49842"}
  - id: E7
    type: probe
    source: "GET /products @ request_id konan-1793702610-29460, 2026-11-03T10:43:30Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001624s request_id=konan-1793702610-29460
  - id: E8
    type: probe
    source: "GET /orders @ request_id konan-1793702611-29465, 2026-11-03T10:43:31Z"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-03T10:41:20.839+00:00"},{"id":2,"product_id":2,"quantity":2,"total_price":46.0,"created_at":"2026-11-03T10:41:21.899+00:00"}]
      -- HTTP 200 in 0.001346s request_id=konan-1793702611-29465
  - id: E9
    type: probe
    source: "GET /products/3 @ request_id konan-1793702626-29479, 2026-11-03T10:43:46Z"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793702626-29479"}
      -- HTTP 500 in 0.010154s request_id=konan-1793702626-29479
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:43:46.805Z (stack field trimmed to its final frame)"
    quote: |-
      {"ts": "2026-11-03T10:43:46.805Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793702626-29479", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E11
    type: probe
    source: "GET /products/3 @ request_id konan-1793702696-29491, 2026-11-03T10:44:56Z (repeat of E9's request, 70 s later)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793702696-29491"}
      -- HTTP 500 in 0.004444s request_id=konan-1793702696-29491
  - id: E12
    type: metric
    source: "GET /metrics @ request_id konan-1793702703-29498, 2026-11-03T10:45:03Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E13
    type: probe
    source: "GET /products/4 @ request_id konan-1793702626-29474, 2026-11-03T10:43:46Z (control: same handler, units_in_stock 75)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001367s request_id=konan-1793702626-29474
  - id: E14
    type: metric
    source: "GET /metrics @ request_id konan-1793702703-29498, 2026-11-03T10:45:03Z"
    quote: process_uptime_seconds 228.02908391598612
  - id: E15
    type: metric
    source: "GET /metrics @ request_id konan-1793702703-29498, 2026-11-03T10:45:03Z"
    quote: faultline_chaos_enabled 0
gaps:
  - "No telemetry exists from before 10:41:15Z: the log file was created at process start with no rotated backups, and all counters reset at start. The pre-start state could not be checked because there is nothing to read."
  - "Whether the 10:41:15Z process start was a scheduled lab start or a recovery from an earlier failure is not decidable from the target's surface; a supervisor or OS process record would settle it, and none is in the surface contract."
  - "The write path was not tested: POST /orders is outside the read-only probe allowlist. Ordering product 3 (zero stock) or product 4 (price null) is therefore unexercised; the null price is flagged under safe next steps, not as a finding."
  - "The chaos gauge was read at two instants (10:42:35Z and 10:45:03Z, both 0). A flip between scrapes would only show as chaos events in the log; none appear, but an absence cannot be quoted."
  - "Triage ran in-orchestrator over the complete telemetry corpus (18 log lines, one metrics page, health) instead of as parallel lens agents; with a corpus this small the sweep reads everything a lens would, but no independent lens re-read it."
usage:
  model: claude-fable-5
  tokens: 980634
  wall_clock_seconds: 430
---

# Routine handover check: shop service healthy; one latent zero-stock defect found

## Summary

**No active incident.** The shop service is up and serving: health returns ok (E1), all 9 user requests in the current process's life completed with 200/201 at millisecond latency (E3, E6), the exception counter was empty before investigator probes (E3 shows no non-2xx), and chaos mode is off at both scrapes (E2, E15). Order data is consistent with the catalog: both stored totals equal price × quantity (E7, E8).

One **latent defect** rides along: `GET /products/3` fails deterministically with an unhandled `ZeroDivisionError` — the `get_product` handler divides `units_ordered` by `units_in_stock`, and product 3 ("Unobtainium Ingot") has stock 0 (E7, E9, E10, E11). Only investigator probes have triggered it (E12 counts exactly the two probe failures); no user has requested product 3 in the observed window. The defect is content-dependent, not requester-dependent: the first user who opens product 3 will get a 500. Confidence is high — the stack trace names the exact expression, and a control probe against a stocked product succeeds (E13).

The observed window is short: the process started at 10:41:15Z (E5), about four minutes before conclusion, and no earlier telemetry exists.

## Timeline

- **10:41:15.916Z** — process start: `faultline 0.1.0 started`; the log file is born with it, no earlier history (E5).
- **10:41:16.6–10:41:25.0Z** — 9 user requests (unprefixed request ids): products browsed, two orders created, all 200/201, durations ≤ 17 ms (E3, E6).
- **10:41:40Z** — complaint raised (`startsAt` of the complaint object).
- **10:41:51Z** — investigation started; trigger latency 11 s.
- **10:42:34–35Z** — baseline: health ok with uptime 78.7 s (E1), chaos gauge 0 (E2), all request counters 2xx (E3), uptime metric 79.4 s (E4).
- **10:43:30–47Z** — business-surface probes: `/products` 200 (E7), `/orders` 200 (E8), `/products/4` 200 (E13), `/products/3` → **500 ZeroDivisionError** (E9, E10), `/orders/1` 200.
- **10:44:56Z** — repeat probe `/products/3` → 500 again; deterministic (E11).
- **10:45:03Z** — final metrics: exactly 2 × 500 and 2 × ZeroDivisionError, both from investigator request ids (E12); uptime 228 s, continuous with E4 (E14); chaos gauge still 0 (E15).
- **10:49:01Z** — investigation concluded.

No configuration, deploy, or flag-change markers appear in the log other than the startup lines.

## Investigation

**Trigger.** Manual, via the `/konan` adapter. The complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1793702500",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-03T10:41:40Z"
}
```

Investigation start: 2026-11-03T10:41:51Z (trigger latency 11 s). No severity was stated, none inferred.

**Baseline.** Health, metrics, and the full log were captured (E1–E6). The entire telemetry corpus at that point was 18 log lines plus one metrics page; the notable facts were a very young process (79 s) and an otherwise spotless record: no non-2xx status, empty exception counter, chaos off.

**Triage.** Run in-orchestrator rather than as parallel lens agents: the complete corpus had already been read verbatim at baseline, so lens agents would re-read the same 18 lines (recorded as a gap). Sweep per domain: software-defect — no error status and no exception in any user request, but two data edges in the catalog (product 3 stock 0, product 4 price null) warranted cheap probes; infra-process — young uptime (hypothesis H2) and the chaos switch (H1); interfaces/third-party/data-db — single local service, no gateway tier, no provider, and order/catalog data cross-checked consistent (E7 vs E8). The business surface was probed directly to avoid the healthy-monitoring trap: `/products`, `/orders`, `/orders/1`, `/products/3`, `/products/4`.

**Deep-dive.** Skipped: H3's triage evidence was already deterministic and complete (probe, log stack, metrics delta, control probe, repeat), and H1/H2 were killed by baseline plus the final scrape. No evidence gap remained that a deep-dive agent could fill.

**Judge.** A fresh judge subagent received the three hypotheses and the verbatim evidence ledger only. Verdicts: H1 invalidated, H2 invalidated, H3 validated; the latent classification of H3 was upheld for the observed window. The judge's overreach flags were applied: E5 is cited as evidence of one recent start only; the latent statement says "not yet triggered by user traffic" rather than "only probes can trigger it"; the user-traffic count was corrected to 9 request lines; chaos-off claims are bounded to the two scrape instants plus the absence of chaos events in the log.

## Hypotheses

### H1 — chaos switch active (infra-process) — invalidated

If chaos injection were on, the gauge would read 1 or errors would appear in user traffic. The gauge reads 0 at baseline and at the final scrape (E2, E15), every user request succeeded (E3, E6), and the only errors in the whole window are the two investigator-triggered 500s accounted for by E12. No chaos event lines appear in the log.

### H2 — crash/restart loop (infra-process) — invalidated

Raised by the young uptime at baseline (78.7 s / 79.4 s — E1, E4). Killed by continuity: exactly one startup marker at the head of a brand-new log (E5), and uptime grows monotonically to 228.0 s across a 148 s wall-clock gap (E4 → E14) — one process life, one start, no restarts in the window. Why the process started at 10:41:15Z is outside the surface (see gaps).

### H3 — zero-stock division defect on GET /products/3 (software-defect) — validated, latent

Product 3 carries `units_in_stock: 0` (E7). Probing `GET /products/3` returns 500 with `exception_type ZeroDivisionError` (E9), the log stack names the mechanism — `shop.py` line 64, `"turnover_score": units_ordered / product["units_in_stock"]` (E10) — a repeat probe 70 s later fails identically (E11), and the control probe against product 4 (stock 75) succeeds and returns a computed `turnover_score` (E13). The metrics delta (E12: exactly 2 × 500, 2 × ZeroDivisionError) matches the two probes and nothing else, which both validates the mechanism and shows no user impact occurred in the window. Latent, not active: users did not request product 3 between process start and conclusion; any user request for it will fail.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Owner of the shop service: read `get_product` around `shop.py` line 64 — the turnover computation divides by `units_in_stock` with no zero guard (E10).
- Watch `http_exceptions_total{type="ZeroDivisionError"}` (E12) for growth beyond 2, and any `/products/{product_id}` 500 with an unprefixed request id — that would mean a real user hit the defect and the finding is no longer latent.
- Check the catalog for other zero-stock products as inventory moves; today product 3 is the only one (E7).
- Review how the order path handles product 4's `price: null` (E7, E13): stored order totals equal price × quantity (E8), so an order for a null-priced product is a plausible failure. Untested here — writes are outside the read-only boundary.

## Gaps

Elaborating the frontmatter list:

1. **No pre-start telemetry.** The log file was created at 10:41:15Z with the process, there are no rotated backups, and every counter reset at start. Nothing before that instant could be checked, because nothing from before it exists on the surface.
2. **Reason for the process start.** One clean startup is visible (E5); whether it was a scheduled lab start or a recovery from something earlier needs a supervisor or OS record, which the surface contract does not include.
3. **Write path unexercised.** POST /orders is outside the probe allowlist, so ordering the zero-stock product 3 or the null-priced product 4 was not tested.
4. **Chaos coverage is two instants.** Both scrapes read 0 (E2, E15) and no chaos events appear in the log, but a between-scrape flip cannot be positively excluded by a quote.
5. **No independent lens pass.** Triage ran in-orchestrator over the full 18-line corpus; equivalent in coverage at this size, but no blind second reader swept the same data.
