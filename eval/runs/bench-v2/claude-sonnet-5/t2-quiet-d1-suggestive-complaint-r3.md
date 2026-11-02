---
konan_journal: 2
investigation:
  id: 2026-11-02-product-page-internal-server-error
  trigger: "manual (human report via /konan)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-02T20:43:25Z
  concluded: 2026-11-02T20:51:23Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError (HTTP 500) when the looked-up product has units_in_stock=0 — product 3, 'Unobtainium Ingot' — because the handler computes turnover_score as units_ordered / units_in_stock with no zero-stock guard; whether this is what produced the complaint's reported customer-facing 'Internal Server Error when opening a product page' this morning could not be confirmed from available telemetry."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: [E7, E8, E9]
latent_findings:
  - statement: "GET /products/3 deterministically returns HTTP 500 right now for any caller (ZeroDivisionError at shop.py:64) — the defect is live and reproducible on demand. The only confirmed callers in available telemetry are the investigator's own stamped probes; no non-investigator request to this route was observed."
    evidence: [E1, E2, E3, E4, E5, E6, E8]
evidence:
  - id: E1
    type: probe
    source: "GET /products via scripts/probe.sh (request_id=konan-1793652480-5169)"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0} — one entry of the 5-product catalog array; sibling products carry units_in_stock 119, 40, 75, 500'
  - id: E2
    type: probe
    source: "GET /products/3 via scripts/probe.sh (request_id=konan-1793652478-5163)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793652478-5163"} -- HTTP 500 in 0.003931s'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:47:58.915Z"
    quote: |
      "message": "unhandled exception: division by zero", "request_id": "konan-1793652478-5163", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"
      stack (tail, path trimmed to the package root): File ".../faultline/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
      ZeroDivisionError: division by zero
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:47:58.917Z"
    quote: '"message": "GET /products/3 -> 500", "request_id": "konan-1793652478-5163", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 3.047'
  - id: E5
    type: metric
    source: "/metrics via scripts/probe.sh (request_id=konan-1793652493-5177)"
    quote: |
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5
      http_exceptions_total{type="ZeroDivisionError"} 5
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:43:08.808Z"
    quote: '"message": "GET /products/2 -> 200", "request_id": "f4de2a042db2", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.983'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:43:05.962Z"
    quote: '"message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0" — the only startup/lifecycle marker in the available log'
  - id: E8
    type: log
    source: "lab/logs/app.log — all access lines with path=/products/3 (2026-11-02T20:45:46.649Z to 2026-11-02T20:47:58.917Z, 5 lines total)"
    quote: "request_id values logged against path=/products/3: konan-1793652346-5104, konan-1793652356-5113, konan-1793652357-5124, konan-1793652361-5136, konan-1793652478-5163 — all five carry the investigator's konan- prefix; zero carry any other prefix. The non-investigator traffic observed in the same log only touched /products/1, /products/2, /products/5, all status 200."
  - id: E9
    type: metric
    source: "/metrics via scripts/probe.sh (request_id=konan-1793652254-4997, baseline scrape taken before any defect-triggering probe)"
    quote: 'faultline_chaos_enabled 0'
gaps:
  - "No telemetry of any kind survives from before the process's 2026-11-02T20:43:05.962Z startup (E7): lab/logs/app.log is 3807 bytes with no .1-.3 rotation backups. The complaint's 'this morning' window is entirely outside the available evidence and could not be checked directly."
  - "Within the available ~8-minute window, every logged request to the failing route (/products/3) carries the investigator's own stamped request id (E8); no non-investigator (customer) request to that route was observed, so real customer impact could not be confirmed or ruled out."
  - "The declared surface (docs/lab.md) offers no evidence source beyond app.log and /metrics — no load-balancer/CDN access log, no support-ticket system. The adversarial judge's named settling evidence (a customer-originated request against /products/3 timestamped to the complaint window, or confirmation that none exists) is outside the investigator's reach, so a second round would gather no new evidence and was not run."
usage:
  model: claude-sonnet-5
  tokens: 3556550
  wall_clock_seconds: 478
---

# Product page "Internal Server Error" — zero-stock division defect found, customer-impact window unconfirmed

## Summary

**Verdict: inconclusive.** Investigation confirmed a real, deterministic software defect — `GET /products/3` ("Unobtainium Ingot", `units_in_stock: 0`) throws an unhandled `ZeroDivisionError` on every call, because the handler computes `turnover_score` as `units_ordered / units_in_stock` with no zero-stock guard (E1-E6). This exactly matches the reported symptom shape ("Internal Server Error when opening a product page"). However, every single logged request against this route in the available telemetry carries the investigator's own `konan-` stamped request id (E8) — none are customer traffic — and no telemetry of any kind survives from before the service process started at 2026-11-02T20:43:05.962Z (E7), which is well after "this morning." The defect is confirmed live and reproducible; whether it is what support's customers actually hit this morning could not be confirmed or refuted from the available surface. See Gaps.

## Timeline

- `2026-11-02T20:43:05.962Z` — faultline process starts; this is the sole startup marker in all available telemetry (E7). Nothing earlier is observable.
- `2026-11-02T20:43:06Z`–`20:43:11Z` — non-investigator (seed/warm-up) traffic: `/health`, `/products`, `/products/1`, `/products/2`, `/products/5`, an order create — all clean 200/201 (E6 is one such line).
- `2026-11-02T20:43:17Z` — complaint raised (`startsAt`, human report via `/konan`).
- `2026-11-02T20:43:25Z` — investigation starts (trigger latency ≈ 8s).
- `2026-11-02T20:44Z`–`20:48Z` — baseline + triage: health/metrics/log tail clean, chaos off (E9); three parallel lenses (infra-process, interfaces, software-defect) independently reproduce `GET /products/3` → 500 `ZeroDivisionError` (E2-E4), deterministic and data-dependent to that one product id (E6 shows sibling product 2 clean).
- `2026-11-02T20:48Z` — final metrics scrape: 5/5 observed 500s on the product-page route are `ZeroDivisionError`, zero elsewhere (E5).
- `2026-11-02T20:51:23Z` — investigation concludes.

## Investigation

1. **Baseline** — `/health` ok, `/metrics` clean (`faultline_chaos_enabled 0`, zero `http_exceptions_total` entries), `lab/logs/app.log` tail showed only the startup marker plus clean seed traffic and the investigator's own first two probes. Process uptime at baseline (~69s) matched the single startup marker — no hidden restart.
2. **Triage** — all three lenses spawned in parallel (vague human complaint; no domain excludable up front): `infra-process`, `interfaces`, `software-defect`. `infra-process` found no lifecycle/latency/saturation anomaly, flagged only the short telemetry window as a domain-relevant coverage gap. `interfaces` found no gateway/chaos/contract-drift anomaly, and flagged `GET /products/3`'s deterministic 500 as out-of-domain (software-defect territory). `software-defect` independently reproduced the same defect, traced it to `shop.py:64`, and explicitly flagged it as latent (investigator-triggered only) rather than confirmed customer impact.
3. **Deep-dive** — skipped. The mechanism evidence was already deterministic and complete across three independent agents (5 total reproductions, consistent stack trace, consistent metrics); no competing hypothesis existed to test. The one open question (did real customers hit this this morning) is not answerable by further live probing — it requires historical data the declared surface does not retain.
4. **Judge** — adversarial judge given only H1 and its cited evidence, blind to this narrative. Verdict: inconclusive. Mechanism prediction (reproducible 500 via the normal code path, isolated to the zero-stock product) fully supported (E1-E6). Customer-impact prediction (non-investigator traffic reaching the route) contradicted by the evidence actually available (E7, E8, E9) rather than merely unsupported — every logged hit on the route is investigator-stamped, and no telemetry predates the recent process start.

## Hypotheses

### H1 — zero-stock division defect on the product-page route (inconclusive)

Statement, incident class, evidence as in the machine core. The defect itself (for/E1-E6) is solid: a clean, isolated, data-dependent failure — the exact kind the rules call out as a real defect shape, not noise. What keeps this inconclusive rather than validated is purely the causal link to the complaint's specific claim ("several customers," "this morning"): the against-evidence (E7-E9) shows the observable window neither contains customer traffic to this route nor reaches back far enough to see "this morning" at all. The judge explicitly ruled this a contradiction by cited evidence, not an absence of evidence — all logged requests to `/products/3` are investigator probes.

## Safe next steps

- Watch `/metrics` for further `http_exceptions_total{type="ZeroDivisionError"}` growth and `http_requests_total{method="GET",path="/products/{product_id}",status="500"}` growth going forward — the first non-investigator (non-`konan-`) request id logged against a 500 on this route would confirm active customer impact.
- Watch `lab/logs/app.log` for any future `/products/{id}` access line whose `request_id` is not `konan-`-prefixed and whose `status` is 500.
- Periodically re-probe `GET /products` to see if other products' `units_in_stock` drops to 0 — each would carry the same exposure as product 3.
- Ask support for the exact timestamps and, if available, the specific product id(s) customers hit this morning, so a future telemetry window (or any system outside this surface that retains longer history) can be checked against it.

## Gaps

- No telemetry of any kind survives from before the process's `2026-11-02T20:43:05.962Z` startup (E7): `lab/logs/app.log` is 3807 bytes with no `.1`-`.3` rotation backups. The complaint's "this morning" window is entirely outside the available evidence and could not be checked directly.
- Within the available ~8-minute window, every logged request to the failing route (`/products/3`) carries the investigator's own stamped request id (E8); no non-investigator (customer) request to that route was observed, so real customer impact could not be confirmed or ruled out.
- The declared surface (`docs/lab.md`) offers no evidence source beyond `app.log` and `/metrics` — no load-balancer/CDN access log, no support-ticket system. The settling evidence the judge named (a customer-originated request against `/products/3` timestamped to the complaint window, or confirmation that none exists) is outside the investigator's reach, so a second round would gather no new evidence and was not run.
