---
konan_journal: 1
investigation:
  id: 2026-08-24-product-page-500-report
  trigger: "manual — /konan human profile. Complaint object: source=human, fingerprint=human-1787590989, labels.alertname=human-report (no severity stated), startsAt=2026-08-24T17:03:09Z. Investigation start 2026-08-24T17:03:31Z; trigger latency 22 s."
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-24T17:03:31Z
  concluded: 2026-08-24T17:08:15Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "GET /products/{product_id} fails deterministically for product 3: get_product (shop.py line 64) computes units_ordered / product[\"units_in_stock\"], product 3 has units_in_stock 0, and the resulting ZeroDivisionError surfaces as HTTP 500 'internal server error'."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E10]
    evidence_against: []
  - id: H2
    statement: "Non-investigator (customer) traffic received HTTP 5xx from a product page within the observable telemetry window (2026-08-24T17:02:55Z onward)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11, E12, E13, E4, E5, E6]
  - id: H3
    statement: "Injected degradation (chaos mode) or a failing dependency/gateway causes probabilistic 5xx on product pages."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E19, E1, E2, E8, E11]
  - id: H4
    statement: "A process crash/restart or resource saturation caused product-page 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E15, E16, E17, E18]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 (ZeroDivisionError in get_product, shop.py line 64: units_ordered / units_in_stock with units_in_stock 0) on every request; 3 of 3 investigator probes failed identically; other product ids return 200. Only investigator probes triggered it in the observable window."
    evidence: [E1, E2, E3, E4, E5, E6, E7, E8, E10]
evidence:
  - id: E1
    type: probe
    source: "GET /products/3 request_id=konan-1787591068-27214"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787591068-27214\"} -- HTTP 500 in 0.010083s request_id=konan-1787591068-27214"
  - id: E2
    type: probe
    source: "GET /products/3 request_id=konan-1787591075-27249"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787591075-27249\"} -- HTTP 500 in 0.003314s request_id=konan-1787591075-27249"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:04:28.511Z"
    quote: "{\"ts\": \"2026-08-24T17:04:28.511Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787591068-27214\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"Traceback (most recent call last):\\n  File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/middleware.py\\\", line 72, in _handle\\n    return await call_next(request)\\n ... File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:04:28.520Z"
    quote: "{\"ts\": \"2026-08-24T17:04:28.520Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787591068-27214\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 9.21, \"client\": \"127.0.0.1:63006\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:04:35.477Z"
    quote: "{\"ts\": \"2026-08-24T17:04:35.477Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787591075-27249\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 2.51, \"client\": \"127.0.0.1:63010\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:04:38.716Z"
    quote: "{\"ts\": \"2026-08-24T17:04:38.716Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787591078-27274\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 2.614, \"client\": \"127.0.0.1:63015\"}"
  - id: E7
    type: probe
    source: "GET /products request_id=konan-1787591062-27199 (HTTP 200; list entry for id 3)"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0}"
  - id: E8
    type: probe
    source: "GET /products/4 request_id=konan-1787591068-27221"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200 in 0.001394s request_id=konan-1787591068-27221"
  - id: E9
    type: metric
    source: "/metrics request_id=konan-1787591013-27158 (baseline, before any investigator product probe; no status=\"500\" series and no http_exceptions_total series were present)"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3"
  - id: E10
    type: metric
    source: "/metrics request_id=konan-1787591080-27280 (after three investigator probes of /products/3)"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 3 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 3 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 5"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:02:57.339Z"
    quote: "{\"ts\": \"2026-08-24T17:02:57.339Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"9cf85b6a30ec\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.283, \"client\": \"127.0.0.1:62966\"}"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:02:58.408Z"
    quote: "{\"ts\": \"2026-08-24T17:02:58.408Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/2 -> 200\", \"request_id\": \"1d0192c1886b\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 200, \"duration_ms\": 1.115, \"client\": \"127.0.0.1:62967\"}"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:03:01.612Z"
    quote: "{\"ts\": \"2026-08-24T17:03:01.612Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/5 -> 200\", \"request_id\": \"85f4810da0d8\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/5\", \"status\": 200, \"duration_ms\": 0.866, \"client\": \"127.0.0.1:62970\"}"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-24T17:02:55.542Z (line 3 of the file; the only startup event; no .1-.3 backups exist)"
    quote: "{\"ts\": \"2026-08-24T17:02:55.542Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E15
    type: probe
    source: "GET /health request_id=konan-1787591012-27152"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":36.824118999997154} -- HTTP 200 in 0.001907s request_id=konan-1787591012-27152"
  - id: E16
    type: probe
    source: "GET /health request_id=konan-1787591068-27208"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":92.68529654107988} -- HTTP 200 in 0.001337s request_id=konan-1787591068-27208"
  - id: E17
    type: metric
    source: "/metrics request_id=konan-1787591013-27158 (baseline)"
    quote: "process_max_rss_bytes 47955968"
  - id: E18
    type: metric
    source: "/metrics request_id=konan-1787591068-27227 (about 56 s after baseline)"
    quote: "process_max_rss_bytes 47955968"
  - id: E19
    type: metric
    source: "/metrics request_id=konan-1787591013-27158 (baseline; same value at konan-1787591075-27255); log scan found zero chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events"
    quote: "faultline_chaos_enabled 0"
gaps:
  - "Telemetry begins at 2026-08-24T17:02:55.542Z (one process start, no rotated log backups). The complaint's 'this morning' period is before that point and is not observable from this surface: customer-facing 500s in that period can be neither confirmed nor ruled out."
  - "The complaint carries no product id, timestamp, or request id, so no support-side correlation against the logs was possible."
  - "lab/server.out was not read: it is outside the three-item investigator surface defined in docs/lab.md."
  - "The boundary hook denied one log-grep command whose search pattern contained the faultline source path copied from the stack trace (eval-blind rule), and the following command hit a permission prompt. Per AGENTS.md a denial is a stop signal, so no further shell commands were run: the E3 stack tail is quoted from two independent lens reads of log line 20 rather than a final re-read by the orchestrator, and a final /metrics scrape after 17:04:51Z was not taken."
  - "Journal schema validation was not run for the same reason (no shell after the boundary signal)."
usage:
  model: claude-fable-5
  tokens: 836542
  wall_clock_seconds: 284
---

# Product-page 500 report: no customer-facing errors in telemetry; latent ZeroDivisionError on /products/3

## Summary

**Verdict: no active incident** in the observable telemetry. Every request from non-investigator traffic in the log window (17:02:55Z onward) returned 200/201, the baseline `/metrics` had no 5xx series and no exception counter, chaos mode is off, and the process has run continuously with flat memory and ~1 ms latencies. The complaint is not corroborated by the telemetry available.

**Latent finding, high confidence:** `GET /products/3` returns HTTP 500 on every request. The stack trace names `get_product` (`shop.py` line 64) dividing `units_ordered` by `units_in_stock`, and product 3 ("Unobtainium Ingot") is the only product with `units_in_stock: 0`. Three of three investigator probes failed identically with `ZeroDivisionError`; product ids 1, 2, 4, 5 return 200. Any client that opens the product-3 page gets exactly the symptom support describes. In the observable window only investigator probes hit it, so it is recorded as latent rather than as the active incident.

**Attribution to the customer reports: unverified.** The reported period ("this morning") predates the current process start; no logs from that period exist on this surface. The product-3 defect is the most plausible mechanism for the reports, but that link is not evidenced.

## Timeline

- 2026-08-24T17:02:55.542Z — process start, single startup marker, version 0.1.0 (E14). No earlier telemetry exists.
- 17:02:56Z–17:03:01Z — non-investigator traffic: `/products`, `/products/1`, `/products/2`, `/products/5`, `POST /orders`, `/orders` — all 200/201 (E11, E12, E13).
- 17:03:09Z — complaint `startsAt` (human report via /konan).
- 17:03:31Z — investigation start (trigger latency 22 s). Baseline: health ok, uptime 36.8 s (E15), no 5xx series (E9), RSS 47955968 (E17), chaos 0 (E19).
- 17:04:28.511Z — first `unhandled_exception` ZeroDivisionError, request `konan-1787591068-27214`, an investigator probe of `/products/3` (E3, E4, E1).
- 17:04:35.477Z, 17:04:38.716Z — two more investigator probes of `/products/3`, both 500 (E5, E6, E2).
- 17:04:xxZ — `/metrics` after probes: `http_exceptions_total{type="ZeroDivisionError"} 3`, `status="500"` count 3 — exactly the three investigator probes (E10).
- 17:08:15Z — concluded.

No configuration, deploy, flag, or chaos change markers appear anywhere in the log.

## Investigation

- **Baseline** (orchestrator): `/health` 200 (E15), `/metrics` (E9, E17, E19), 16-line log tail — all 2xx, no exceptions, no backups.
- **Triage** — three lenses spawned in parallel, blind to each other, each given only the lens path, the surface contract, the verbatim complaint, and the baseline summary:
  - *software-defect*: found the deterministic `/products/3` ZeroDivisionError (E1–E4, E7, E8, E10); noted all 500s are investigator-originated.
  - *infra-process*: no lifecycle or saturation anomaly — single startup, monotonic uptime, flat RSS, no latency drift (E14–E18).
  - *interfaces*: no chaos, no change markers, no gateway statuses, no probabilistic shape; failure is 100% on one input, 0% on others (E19, E8, E11–E13).
- **Deep-dive**: skipped. H1's triage evidence was already deterministic and complete (3/3 reproductions, stack trace, input data); H2–H4 had clean disconfirming evidence from the baseline and triage.
- **Judge** (fresh agent, evidence ledger only): H1 validated; H2, H3, H4 invalidated. The judge noted H1 and H2 are consistent together: "the defect is real and deterministic, but every observed hit came from investigator probes."
- **Boundary event**: after the judge, one verification grep was denied by the eval-blind hook because its pattern contained the faultline source path from the stack trace; the next command hit a permission prompt. Investigation stopped taking new telemetry at that point and concluded on the evidence in hand.

## Hypotheses

### H1 — data-dependent ZeroDivisionError on /products/3 (software-defect) — validated

For: probe responses E1, E2 carry `exception_type ZeroDivisionError` with HTTP 500; log E3 shows the throwing operation `units_ordered / product["units_in_stock"]` in `get_product`; E7 shows product 3 has `units_in_stock: 0`; E8 shows the same computation returns `turnover_score 0.0` for a product with nonzero stock; E4, E5, E6 are three consecutive 500 access lines for `/products/3`; E10 shows counters that match exactly (3 exceptions, 3 500s). Against: none. Deterministic per-input failure is a code-defect signature.

### H2 — customer traffic received 5xx in the observable window — invalidated

The prediction (a non-`konan-` request line with 5xx, or a `status="500"` series before investigator probes) does not hold: E9 shows no 500 series at baseline; E11–E13 show every non-investigator product request returned 200; E4, E5, E6 account for all three 500 lines and all carry `konan-` ids. E10's 500 count equals the number of investigator probes. Scope limit: this says nothing about periods before 17:02:55Z (see Gaps).

### H3 — injected degradation / dependency failure (interfaces) — invalidated

E19: `faultline_chaos_enabled 0` throughout, no chaos or simulated-exception events. The failure is deterministic on one input (E1, E2) and absent on others (E8, E11), the opposite of a probabilistic per-request shape; no 502/503/504 anywhere.

### H4 — process crash/restart or saturation (infra-process) — invalidated

E14: exactly one startup marker. E15 → E16: uptime rises 36.8 s → 92.7 s with no reset, consistent with the 17:02:55Z start. E17 = E18: RSS unchanged. Request durations stay ~1–9 ms.

## Safe next steps

Read-only suggestions only:

- Ask support for the product id(s), timestamps, and any request ids shown to the customers; if the product is id 3, the latent finding explains the reports.
- Retrieve logs and metrics from before the 17:02:55Z process start (previous process generation, log shipping, or the host) to check whether non-investigator `/products/3` requests returned 500 "this morning", and whether any other product page did.
- Check the catalog for other products with `units_in_stock: 0` (only id 3 has it in the current `/products` list, E7); each would fail the same way.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and `http_requests_total{path="/products/{product_id}",status="500"}` for growth beyond the 3 investigator-caused counts — any increase is customer impact.

## Gaps

- The telemetry window starts at the current process start (E14) with no rotated backups; the complaint's period is before it. Customer-facing errors then can be neither confirmed nor excluded from this surface.
- The complaint has no product id, timestamp, or request id, so nothing support-side could be correlated with the log.
- `lab/server.out` exists but is outside the investigator surface in `docs/lab.md`; it was not read.
- A boundary-hook denial (grep pattern containing the faultline source path from the stack trace) and a following permission prompt stopped further shell use, per the AGENTS.md stop rule. Consequences: the E3 stack tail is quoted from two independent lens reads of the log line rather than a final orchestrator re-read; no final `/metrics` scrape after 17:04:51Z; journal schema validation not run.
