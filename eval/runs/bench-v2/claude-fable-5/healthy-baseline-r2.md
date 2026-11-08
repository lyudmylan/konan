---
konan_journal: 2
investigation:
  id: 2026-11-03-routine-handover-check
  trigger: "manual (/konan adapter; complaint object: source=human, fingerprint=human-1793701847, alertname=human-report, startsAt=2026-11-03T10:30:47Z; investigation start 2026-11-03T10:30:54Z, trigger latency 7s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-03T10:30:54Z
  concluded: 2026-11-03T10:39:36Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "GET /products/3 fails deterministically with HTTP 500: the handler get_product (shop.py line 64) computes units_ordered / product[\"units_in_stock\"] and product 3 has units_in_stock = 0, raising ZeroDivisionError. Latent: only investigator probes have triggered it."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "Within the window the surface can observe, there is no active user-impacting incident: all non-investigator traffic succeeded (200/201), no exceptions preceded investigator probes, chaos is off, the process is stable, and the surface holds no sign of a failed prior run."
    incident_class: no-incident
    state: validated
    evidence_for: [E1, E2, E3, E4, E10, E11, E12, E13]
    evidence_against: []
  - id: H3
    statement: "Product 4 carries price: null in the catalog — a latent data edge a strict client could reject; the server tolerates it (GET /products/4 returns 200) and no request has failed because of it."
    incident_class: data-db
    state: validated
    evidence_for: [E8, E9, E11]
    evidence_against: []
latent_findings:
  - statement: "Deterministic ZeroDivisionError on GET /products/3 (units_in_stock = 0 divides units_ordered at shop.py:64). Live for any user who requests that path; so far triggered only by investigator probes. Any product whose stock reaches 0 would expose the same 500 on its detail route."
    evidence: [E5, E6, E7, E8, E9]
  - statement: "Product 4 (Mystery Box) has price: null in the catalog; tolerated by the server, risky for strict clients."
    evidence: [E8, E9, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:30:19.407Z"
    quote: '{"ts": "2026-11-03T10:30:19.407Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log, lines 6-16, 2026-11-03T10:30:20.157Z-10:30:28.562Z (9 request lines, unstamped request ids, every status 200 or 201; sample line quoted)"
    quote: '{"ts": "2026-11-03T10:30:24.375Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "417236f4960a", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.92, "client": "127.0.0.1:49766"}'
  - id: E3
    type: metric
    source: "/metrics @ 2026-11-03T10:31:27Z, request_id=konan-1793701887-29029"
    quote: |-
      http_requests_total rows: all status "200"/"201" (no other statuses present)
      http_exceptions_total: no rows
      faultline_chaos_enabled 0
      process_uptime_seconds 67.73831987497397
      process_max_rss_bytes 47824896
  - id: E4
    type: probe
    source: "/health, request_id=konan-1793701886-29024"
    quote: |-
      {"status":"ok","uptime_seconds":67.23967566713691}
      -- HTTP 200 in 0.002621s request_id=konan-1793701886-29024
  - id: E5
    type: probe
    source: "/products/3, request_id=konan-1793701981-29153"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793701981-29153"}
      -- HTTP 500 in 0.008278s request_id=konan-1793701981-29153
  - id: E6
    type: probe
    source: "/products/3 (reproduction), request_id=konan-1793701988-29182"
    quote: "-- HTTP 500 in 0.004081s request_id=konan-1793701988-29182"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:33:01.293Z (same ERROR repeats @ 10:33:08.179Z for request_id konan-1793701988-29182; middle stack frames trimmed)"
    quote: |-
      {"ts": "2026-11-03T10:33:01.293Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793701981-29153", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):
        [trimmed middleware/routing frames]
        File \"<checkout>/src/faultline/shop.py\", line 64, in get_product
          \"turnover_score\": units_ordered / product[\"units_in_stock\"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero"}
  - id: E8
    type: probe
    source: "/products, request_id=konan-1793702035-29212 (HTTP 200; two catalog rows quoted)"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0} ... {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75}'
  - id: E9
    type: probe
    source: "/products/4, request_id=konan-1793702057-29220"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001591s request_id=konan-1793702057-29220
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-03T10:32:40Z, request_id=konan-1793701960-29116"
    quote: |-
      process_uptime_seconds 141.5
      process_max_rss_bytes 47824896
  - id: E11
    type: log
    source: "lab/logs/app.log, whole file as of 2026-11-03T10:34:17Z (the only non-2xx request lines; both request ids konan-stamped; every unstamped request line is 200/201)"
    quote: |-
      {"ts": "2026-11-03T10:33:01.300Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793701981-29153", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 7.491, "client": "127.0.0.1:49802"}
      {"ts": "2026-11-03T10:33:08.182Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793701988-29182", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 3.155, "client": "127.0.0.1:49805"}
  - id: E12
    type: log
    source: "lab/server.out, whole file as of 2026-11-03T10:34Z (exactly one start sequence; nothing precedes it — no earlier start, no shutdown, no traceback; first two lines quoted)"
    quote: |-
      warning: `VIRTUAL_ENV=<home>/.cache/uv/environments-v2/run-5cf50e8d1a8b3cfb` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
      {"ts": "2026-11-03T10:30:19.407Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [28895]"}
  - id: E13
    type: log
    source: "filesystem listing of lab/ (ls -la) @ 2026-11-03T10:34Z — directory metadata recorded under the log type; local time is UTC+2"
    quote: |-
      drwxr-xr-x@  5 lyudmylan  staff    160 Nov  3 12:30 .
      -rw-r--r--@  1 lyudmylan  staff     12 Nov  3 12:30 faultline.pid
      drwxr-xr-x@  3 lyudmylan  staff     96 Nov  3 12:30 logs
      -rw-r--r--@  1 lyudmylan  staff  18274 Nov  3 12:34 server.out
gaps:
  - "No pre-start telemetry exists: the observable history begins at the 10:30:19.407Z startup. No rotated log backups (lab/logs/ holds only app.log), and lab/server.out opens with the same start event. Conditions before that instant cannot be checked from this surface."
  - "Thin traffic base: all non-investigator traffic is 9 requests in one 9-second burst (10:30:20-10:30:28Z), then silence. 'All user traffic succeeded' rests on that sample."
  - "The data behind units_ordered and the order store could not be inspected beyond API responses — the surface has no database access."
  - "H2 is scoped to realized user impact in the observed window: it expires the moment a non-investigator request touches GET /products/3."
usage:
  model: claude-fable-5
  tokens: 1975081
  wall_clock_seconds: 522
---

# Routine handover check: shop service healthy; one latent 500 on /products/3

## Summary

**Verdict: no active incident.** All end-user traffic since process start succeeded (200/201), the exception counter was empty before investigator probes, chaos injection is off, and the process is stable (monotonic uptime, flat memory). Two latent findings ride along, neither triggered by any user so far: (1) `GET /products/3` returns a deterministic HTTP 500 — `get_product` (shop.py:64) divides `units_ordered` by `units_in_stock`, and product 3 ("Unobtainium Ingot") has `units_in_stock = 0`, raising `ZeroDivisionError`; (2) product 4 ("Mystery Box") carries `price: null` in the catalog. Confidence in the no-active-incident verdict is high within the observable window, with one honest limit: telemetry begins at the 10:30:19Z process start, 28 seconds before the complaint, so nothing before that instant is observable — though the runtime directory's own creation timestamps show a first start, not a crash recovery.

**Handover note:** `http_exceptions_total{type="ZeroDivisionError"}` now reads 2 — both are this investigation's stamped probes (`konan-1793701981-29153`, `konan-1793701988-29182`), not user impact.

## Timeline

- **10:30:19.407Z** — faultline 0.1.0 starts, pid 28895 (E1). The whole `lab/` runtime directory is created in this minute (E13); `lab/server.out` holds no earlier run (E12). No config/flag/chaos markers appear at any later point.
- **10:30:20–10:30:28Z** — 9 unstamped (simulated end-user) requests, all 200/201, including two successful order creations (E2).
- **10:30:47Z** — complaint raised (`startsAt`); **10:30:54Z** — investigation starts (trigger latency 7 s).
- **10:31:26–27Z** — baseline probes: health ok, uptime 67 s, all-2xx counters, zero exceptions, chaos off (E3, E4).
- **10:33:01.293Z** — first probe of `/products/3` → 500, `ZeroDivisionError` at shop.py:64 (E5, E7).
- **10:33:08.179Z** — reproduction → 500, identical stack (E6, E7); contrast probe `/products/4` → 200 (E9).
- **10:33:55Z** — catalog probe shows product 3 `units_in_stock: 0` (E8).
- **10:34:17Z** — final contrast probe confirms product 4 computes `turnover_score` without error (E9).

## Investigation

- **Baseline:** health, metrics, full log read. Clean, but the process was only ~68 s old; no rotated logs.
- **Triage (3 lenses in parallel: infra-process, interfaces, software-defect):** infra-process — no anomaly (one start, monotonic uptime, flat RSS). interfaces — no anomaly at the edges; noted product 4 `price: null` and the short history. software-defect — found and reproduced the `/products/3` 500 with the stack trace.
- **Deep-dive:** skipped — the defect evidence was already deterministic and complete (two reproductions + stack trace + divisor value + control case). One orchestrator probe captured the divisor (E8), one the control (E9).
- **Judge round 1:** H1 validated, H3 validated (with a citation fix, applied), H2 inconclusive — the unexplained process start 28 s before the complaint left "crash recovery" open.
- **Round 2 targeted gathering (the judge's settling item):** `lab/server.out` and the runtime directory metadata — exactly one start sequence, nothing older on the surface (E12, E13).
- **Judge round 2:** H2 validated as scoped; caveats carried into this report (E13 promoted into the ledger, thin traffic base, H2's expiry condition).

## Hypotheses

### H1 — deterministic 500 on GET /products/3 (software-defect) — validated

Two probes of `/products/3` both returned 500 with `exception_type: ZeroDivisionError` (E5, E6). The stack trace names the mechanism: `"turnover_score": units_ordered / product["units_in_stock"]` at `shop.py` line 64 in `get_product` (E7). The catalog shows the divisor: product 3 has `units_in_stock: 0` (E8). The control case holds: product 4, stock 75, returns 200 and computes `turnover_score: 0.0` (E9) — a zero numerator is safe, a zero denominator is not. No evidence against. **Latent**, not the active incident: both 500s are konan-stamped (E11); no user has hit this path.

### H2 — no active user-impacting incident (scoped to the observable window) — validated

All 9 unstamped requests succeeded (E2, E11); the exception counter was empty before the probes (E3); chaos is off (E3); uptime grows monotonically with flat memory (E3, E10); and the surface holds no sign of a failed prior run — one start sequence in stdout, a runtime directory born with it (E12, E13). The judge's round-1 objection (possible crash recovery before the window) was settled by E12/E13: there is nothing older to recover from. Standing caveats: the traffic sample is thin (one 9-second burst), and this verdict expires the moment a non-investigator request touches `/products/3`.

### H3 — product 4 price: null (data-db) — validated

The catalog row carries `price: null` (E8); the server tolerates it (`GET /products/4` → 200, E9); the whole-log sweep shows no request ever failed on it (E11). Low severity, latent. The "a strict client could reject it" clause is a risk statement that server-side telemetry cannot test.

## Safe next steps

All read-only; remediation is out of scope.

- Report the `/products/3` defect to the service owners: `get_product` divides by `units_in_stock`, which is user-visible the moment any shopper opens product 3. Any other product whose stock reaches 0 exposes the same 500 on its detail route.
- Watch for the latent defect going active: any `GET /products/3 -> 500` log line with an **unstamped** request id, or `http_exceptions_total{type="ZeroDivisionError"}` rising above 2, means realized user impact — this report's verdict then no longer holds.
- Flag product 4's `price: null` to the data owners; watch order traffic for failures referencing product 4.
- At handover, read the exception counter as 2 investigator-caused entries, not user impact.

## Gaps

- **No pre-start telemetry.** The surface's history begins at 10:30:19.407Z. No rotated backups exist and `server.out` opens with the same start event, so conditions before that instant are unobservable. The runtime directory metadata (E13) supports "first start", but a planned-start record (supervisor or deploy log) is outside this surface.
- **Thin traffic base.** Nine user requests in nine seconds, then silence. The all-2xx claim is true of that sample only.
- **No data-layer access.** `units_ordered` provenance and the order store could not be inspected beyond API responses.
- **Scope of the verdict.** "No active incident" means no realized user impact in the observed window; H1 is one user request away from becoming active.
