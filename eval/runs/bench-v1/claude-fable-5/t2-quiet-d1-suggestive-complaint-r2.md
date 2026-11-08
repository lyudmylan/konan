---
konan_journal: 1
investigation:
  id: 2026-08-24-products-3-500s
  trigger: "manual (/konan, profile human). Complaint object: source=human, fingerprint=human-1787591428, labels.alertname=human-report (no severity stated), startsAt=2026-08-24T17:10:28Z. Investigation start 2026-08-24T17:10:42Z; trigger latency 14s."
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-24T17:10:42Z
  concluded: 2026-08-24T17:14:15Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} divides units_ordered by units_in_stock in shop.py get_product; product 3 has units_in_stock 0, so every request for product 3 raises ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/{id} computes turnover_score = units_ordered / units_in_stock; product 3 (units_in_stock 0) raises ZeroDivisionError on every request and returns HTTP 500 — deterministic, data-dependent; all other product ids succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7]
    evidence_against: [E9, E10]
  - id: H2
    statement: "Chaos / fault-injection mode is enabled and returns 500s probabilistically on product pages."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E13, E4]
  - id: H3
    statement: "The process crashed, restarted, or is resource-degraded, causing 500s on product pages this morning."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E11]
    evidence_against: [E12, E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:11:40.146Z"
    quote: "{\"ts\": \"2026-08-24T17:11:40.146Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787591500-27624\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"... File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n ... ZeroDivisionError: division by zero\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:11:40.154Z"
    quote: "{\"ts\": \"2026-08-24T17:11:40.154Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787591500-27624\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 8.014, \"client\": \"127.0.0.1:63078\"}"
  - id: E3
    type: probe
    source: "/products/3 request_id=konan-1787591500-27624"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787591500-27624\"} -- HTTP 500 in 0.008820s request_id=konan-1787591500-27624"
  - id: E4
    type: probe
    source: "/products/3 request_id=konan-1787591518-27713 (repeat by a second lens)"
    quote: "-- HTTP 500 in 0.003400s request_id=konan-1787591518-27713"
  - id: E5
    type: probe
    source: "/products request_id=konan-1787591576-27782"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":40},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}] -- HTTP 200 in 0.001542s request_id=konan-1787591576-27782"
  - id: E6
    type: probe
    source: "/products/1 konan-1787591508-27667; /products/2 konan-1787591508-27673; /products/4 konan-1787591519-27719; /products/6 (software-defect lens)"
    quote: "/products/1 HTTP 200; /products/2 HTTP 200; /products/4 HTTP 200; /products/6 HTTP 404 {\"detail\":\"no such product: 6\"}"
  - id: E7
    type: metric
    source: "/metrics request_id=konan-1787591583-27789"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 4 | http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4 | http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 10 | http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"404\"} 1"
  - id: E8
    type: metric
    source: "/metrics request_id=konan-1787591583-27789 (also 0 at baseline konan-1787591449-27526)"
    quote: "faultline_chaos_enabled 0"
  - id: E9
    type: log
    source: "lab/logs/app.log — all \"status\": 500 lines, 17:11:40Z–17:11:58Z"
    quote: "request_id values on every 500 line: konan-1787591500-27624, konan-1787591509-27679, konan-1787591510-27695, konan-1787591518-27713; grep of 5xx lines without the konan- prefix returns 0 lines"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:10:18.658Z / 17:10:19.710Z / 17:10:22.915Z (all non-investigator product-page requests)"
    quote: "\"message\": \"GET /products/1 -> 200\", \"request_id\": \"471f5b2799cf\" | \"message\": \"GET /products/2 -> 200\", \"request_id\": \"6ffed3ebd072\" | \"message\": \"GET /products/5 -> 200\", \"request_id\": \"614349b5954b\""
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:10:16.824Z (first application line; no app.log.1–.3 backups exist)"
    quote: "{\"ts\": \"2026-08-24T17:10:16.824Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E12
    type: metric
    source: "/metrics konan-1787591449-27526 (17:10:49Z), konan-1787591487-27569 (17:11:27Z), konan-1787591583-27789 (17:13:03Z)"
    quote: "process_uptime_seconds 32.207840875023976 -> 71.02053062501363 -> 166.46657225000672; process_max_rss_bytes 47038464 -> 48070656"
  - id: E13
    type: log
    source: "lab/logs/app.log — full file grep at 17:12Z"
    quote: "0 lines with event chaos_enabled, chaos_disabled, chaos_failure, or simulated_exception"
gaps:
  - "The log begins at process startup 2026-08-24T17:10:16.824Z and no rotated backups exist, so the 'this morning' window the complaint refers to is not covered by any telemetry. No customer request to /products/3 is visible; customer impact is inferred from the deterministic defect, not observed."
  - "Whether a process restart occurred before 17:10:16Z cannot be determined from the surface (no supervisor or OS records are in the contract)."
  - "units_ordered is not exposed on the surface; the numerator's value is not observable, only that the denominator (units_in_stock for product 3) is 0."
usage:
  model: claude-fable-5
  tokens: 1311069
  wall_clock_seconds: 213
---

# GET /products/3 returns 500: ZeroDivisionError on a zero-stock product

## Summary

**Verdict: root cause identified.** `GET /products/{id}` computes a `turnover_score` as `units_ordered / units_in_stock` in `shop.py:64 get_product`. Product 3 ("Unobtainium Ingot") has `units_in_stock: 0`, so every request for that product raises `ZeroDivisionError` and the service answers HTTP 500 "internal server error" (E1, E2, E3, E5). The failure is deterministic and data-dependent: four out of four probes of `/products/3` failed (E4, E7); products 1, 2, 4, and 5 return 200 and product 6 returns a clean 404 (E6). Chaos mode is off and the process is stable (E8, E12, E13).

Impact: any customer who opens the product 3 page gets "Internal Server Error". This matches the reported symptom. Caveat on confidence: the available log starts at 17:10:16Z (E11) and contains no customer request to `/products/3` (E9, E10) — only the investigator's own probes triggered the exception in the visible window. The mechanism is validated with high confidence; the customer impact "this morning" is consistent with it but not observed in telemetry.

## Timeline

- 2026-08-24T17:10:16.824Z — faultline 0.1.0 starts; the log begins here (E11).
- 17:10:18Z–17:10:22Z — customer traffic: `/products/1`, `/products/2`, `/products/5` all 200 (E10). No customer request for product 3.
- 17:10:28Z — complaint raised via `/konan` (trigger `startsAt`).
- 17:10:42Z — investigation start; baseline clean, uptime 32 s (E12), chaos off (E8).
- 17:11:40.146Z — first probe of `/products/3` raises `ZeroDivisionError` in `get_product` (E1) and returns 500 (E2, E3).
- 17:11:49Z–17:11:58Z — three further probes of `/products/3` by other lenses, all 500 (E4, E9); exception counter reaches 4 (E7).
- 17:13:03Z — final metrics: uptime monotonic at 166 s, no restart, memory flat (E12).
- 17:14:15Z — concluded.

No configuration, deploy, or chaos-toggle markers were found in the log (E13).

## Investigation

- **Baseline** (17:10:48Z): `/health` 200, uptime 31 s; all counters 2xx; `http_exceptions_total` empty; chaos 0; 16 log lines, no ERROR level.
- **Triage** — three lenses spawned in parallel: `software-defect`, `infra-process`, `interfaces`. Software-defect reproduced a deterministic 500 on `/products/3` with the traceback and identified the zero-stock product as the distinguishing input. Interfaces independently reproduced it 2/2, found no chaos, no change markers, no 502/503/504, and zero non-investigator 5xx. Infra-process found one startup, monotonic uptime, flat RSS, no latency degradation.
- **Deep-dive**: skipped. H1's triage evidence was deterministic and complete (traceback to the source line, distinguishing input on the surface, 4/4 reproduction across two independent lenses).
- **Judge**: H1 validated; H2 invalidated; H3 invalidated. The judge flagged that the ledger shows the defect, not a customer hit — recorded under Gaps.

## Hypotheses

### H1 — ZeroDivisionError on product 3 (software-defect) — validated

The traceback names the exact expression and line (E1); the paired access line shows the 500 (E2); the probe body echoes the exception type (E3). The product list exposes the trigger: product 3 is the only entry with `units_in_stock: 0` (E5). Neighbouring ids succeed, including product 4 with `price: null`, so price is not the trigger (E6). Repeat probes fail 4/4 and the exception counter matches exactly (E4, E7). Against: every observed 500 carries an investigator request id (E9) and the customer traffic in the window is all 2xx (E10) — this limits the *impact* claim, not the mechanism.

### H2 — chaos / fault injection (interfaces) — invalidated

`faultline_chaos_enabled 0` at baseline and at conclusion (E8); no chaos or simulated-exception events exist in a log that starts at process startup (E13); the failure is deterministic on one id rather than probabilistic (E4).

### H3 — process crash / restart / resource degradation (infra-process) — invalidated

One startup marker (E11), one monotonic uptime series with no counter resets and about 1 MB RSS growth (E12), all post-start customer traffic 2xx (E10). The startup at 17:10:16Z is itself a lifecycle event with nothing before it; the surface cannot say whether a restart preceded it, but nothing links such an event to the 500s, which occur ~80 s after start with a specific exception.

## Safe next steps

- Ask Support for the product id or URL the affected customers opened; a match on product 3 confirms the link to this defect.
- If an earlier log window exists outside this surface (before 17:10:16Z), grep it for `"path": "/products/3"` with `"status": 500` and non-`konan-` request ids to measure customer impact.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and `http_requests_total{path="/products/{product_id}",status="500"}`: any increment not matching an investigator probe is a customer hit.
- Check whether other products can reach `units_in_stock: 0` (e.g. after orders drain stock); the same failure would then spread to those pages.

## Gaps

- **Telemetry window.** The log begins at 17:10:16.824Z and no `.1`–`.3` backups exist. The complaint's "this morning" period is not observable; customer impact is inferred from a deterministic defect, not seen.
- **Pre-start history.** No supervisor/OS records are in the contract, so a restart before 17:10:16Z can be neither confirmed nor excluded.
- **`units_ordered`.** The numerator is not on the surface; only the zero denominator is observable.
