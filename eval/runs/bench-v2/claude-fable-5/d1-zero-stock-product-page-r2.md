---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-zero-stock-500s
  trigger: "manual — /konan human profile; complaint object: source=human, fingerprint=human-1793627849, labels.alertname=human-report (no severity stated), startsAt=2026-11-02T13:57:29Z; investigation start 2026-11-02T13:57:42Z; trigger latency 13s"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T13:57:42Z
  concluded: 2026-11-02T14:05:58Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/3 raises an unhandled ZeroDivisionError at src/faultline/shop.py line 64, where the handler divides units_ordered by product[\"units_in_stock\"] and product 3's units_in_stock is 0, so every request for that product returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The target's own code raises an unhandled ZeroDivisionError at src/faultline/shop.py line 64 on every GET /products/3 because product 3 has units_in_stock = 0; this defect produced the customers' Internal Server Errors."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E11, E12, E13, E14]
    evidence_against: []
  - id: H2
    statement: "An internal chaos/degradation switch injects the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E15, E7, E3, E16]
  - id: H3
    statement: "A deploy or restart inside the complaint window introduced the failing behavior; the process started at 13:57:05.896Z and /products/3 failed from its first observed request 7 seconds later."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E3]
    evidence_against: [E17, E2, E11]
  - id: H4
    statement: "Product 3's stock record is wrong data (units_in_stock should not be 0); the data state, not the code, is the root cause."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E11]
    evidence_against: [E14, E2]
latent_findings:
  - statement: "Product 4 ('Mystery Box') carries price: null in the catalog; no observed request has failed on it. A latent data risk, not part of this incident."
    evidence: [E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:05.896Z"
    quote: |-
      {"ts": "2026-11-02T13:57:05.896Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:12.886Z (stack trimmed to the last frame)"
    quote: |-
      {"ts": "2026-11-02T13:57:12.886Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "e15ea16e433f", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n ... ZeroDivisionError: division by zero"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:12.897Z"
    quote: |-
      {"ts": "2026-11-02T13:57:12.897Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "e15ea16e433f", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.764, "client": "127.0.0.1:58442"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:13.959Z"
    quote: |-
      {"ts": "2026-11-02T13:57:13.959Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "0e07236936dc", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.435, "client": "127.0.0.1:58443"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:17.083Z"
    quote: |-
      {"ts": "2026-11-02T13:57:17.083Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "443f22e8cee0", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.544, "client": "127.0.0.1:58445"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:19.195Z"
    quote: |-
      {"ts": "2026-11-02T13:57:19.195Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "3396bd0a8613", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.102, "client": "127.0.0.1:58447"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:57:16.020Z"
    quote: |-
      {"ts": "2026-11-02T13:57:16.020Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "84d0698b5b28", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.911, "client": "127.0.0.1:58444"}
  - id: E8
    type: metric
    source: "/metrics scrape, request_id konan-1793627874-91918 @ ~2026-11-02T13:57:54Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
  - id: E9
    type: metric
    source: "/metrics scrape, request_id konan-1793627874-91918 @ ~2026-11-02T13:57:54Z"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E10
    type: metric
    source: "/metrics scrape, request_id konan-1793627874-91918 @ ~2026-11-02T13:57:54Z"
    quote: |-
      faultline_chaos_enabled 0
  - id: E11
    type: probe
    source: "GET /products, request_id konan-1793627899-91938 (response trimmed to product 3)"
    quote: |-
      {"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}
      -- HTTP 200 in 0.001599s request_id=konan-1793627899-91938
  - id: E12
    type: probe
    source: "GET /products/3, request_id konan-1793627974-92004"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793627974-92004"}
      -- HTTP 500 in 0.004921s request_id=konan-1793627974-92004
  - id: E13
    type: metric
    source: "/metrics scrape, request_id konan-1793628106-92128 @ ~2026-11-02T14:01:46Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5
  - id: E14
    type: metric
    source: "/metrics scrape, request_id konan-1793628106-92128 @ ~2026-11-02T14:01:46Z (only type label present under http_exceptions_total)"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 5
  - id: E15
    type: log
    source: "lab/logs/app.log, full-file grep -cE 'chaos_enabled|chaos_disabled|chaos_failure|simulated_exception'"
    quote: |-
      0
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:59:34.994Z (investigator-stamped request id)"
    quote: |-
      {"ts": "2026-11-02T13:59:34.994Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793627974-92004", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.073, "client": "127.0.0.1:58483"}
  - id: E17
    type: log
    source: "lab/logs/ directory listing @ ~2026-11-02T13:58Z"
    quote: |-
      app.log
  - id: E18
    type: metric
    source: "/metrics scrape, request_id konan-1793628106-92128 @ ~2026-11-02T14:01:46Z"
    quote: |-
      process_uptime_seconds 280.38318170793355
  - id: E19
    type: probe
    source: "GET /products, request_id konan-1793627899-91938 (response trimmed to product 4)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75}
gaps:
  - "No telemetry exists before the process start at 2026-11-02T13:57:05.896Z (single log file, no rotated backups), so no last-known-good state for /products/3 is observable; H3 (a deploy introduced the defect) cannot be settled from this surface."
  - "The authoritative intended stock value for product 3 lives outside the investigator surface (ground truth is excluded by the lab contract), so H4 (the zero is wrong data) cannot be settled from this surface."
  - "The complaint says the error still happens on refresh, but no unstamped user request appears in the log after 13:57:19.195Z; ongoing user impact is inferred from the deterministic reproduction (E12), not observed from fresh user traffic."
  - "The target's source code is outside the surface contract; the code mechanism is read from the logged stack trace only."
usage:
  model: claude-fable-5
  tokens: 2217577
  wall_clock_seconds: 496
---

# Product 3 returns 500: unhandled ZeroDivisionError on zero stock

## Summary

Root cause identified. `GET /products/3` fails deterministically with HTTP 500 because
the product handler computes `units_ordered / product["units_in_stock"]` at
`src/faultline/shop.py` line 64, and product 3 ("Unobtainium Ingot") has
`units_in_stock = 0` — an unhandled `ZeroDivisionError` on every request for that one
product (E2, E11). Four customer-facing 500s are in evidence, all on `/products/3`,
between 13:57:12.886Z and 13:57:19.195Z (E3–E6); every other observed route and product
id succeeds, which matches the complaint's "other pages load fine". One read-only
investigator probe reproduced the failure and moved both the 500 counter and the
exception counter by exactly one (E12, E13, E14). Confidence is high: the prediction
held on every point. Chaos injection is ruled out (E10, E15). The failure persists on
refresh because it is data-dependent and deterministic, not transient.

## Timeline

- 13:57:05.896Z — process start, `faultline 0.1.0 started`; no telemetry exists before
  this marker (E1, E17). This is the only configuration/deploy-shaped marker in the log.
- 13:57:06–13:57:11Z — healthy user traffic: `/health`, `/products`, `/products/1`,
  `/products/2` return 200; `POST /orders` returns 201 (baseline log tail; E8 counts).
- 13:57:12.886Z — first `ZeroDivisionError` (E2); the paired access line logs
  `GET /products/3 -> 500` at 13:57:12.897Z (E3).
- 13:57:13.959Z, 13:57:17.083Z, 13:57:19.195Z — three more user 500s, all
  `GET /products/3` (E4, E5, E6); `GET /products/2 -> 200` interleaves at 13:57:16.020Z
  (E7).
- 13:57:29Z — complaint raised (`startsAt`, /konan adapter).
- 13:57:42Z — investigation start (trigger latency 13 s).
- ~13:57:53Z — baseline probes: health 200, metrics show 4×500 / 4×ZeroDivisionError /
  chaos off (E8, E9, E10).
- 13:59:34.994Z — investigator reproduction: `GET /products/3 -> 500`, stamped
  `konan-1793627974-92004` (E12, E16).
- ~14:01:46Z — post-reproduction scrape: both counters at 5, exactly +1 (E13, E14).

## Investigation

Baseline (13:57:53Z): health green, chaos gauge 0, short log history starting
13:57:05.896Z, four user 500s on `/products/3` only, catalog shows product 3 with zero
stock. Triage fanned out three lenses in parallel — software-defect, infra-process,
interfaces — each with the lens file, the surface contract, the verbatim complaint, and
the baseline summary. Software-defect reproduced the failure with one probe and matched
the counter arithmetic. Infra-process ruled out chaos, crash loops, and saturation, and
flagged the in-window startup with no pre-start history. Interfaces ruled out
dependency, schema, and gateway mechanisms, and noted the untyped response contract plus
product 4's null price. All four hypotheses carried deterministic triage evidence, so
the round skipped deep-dives and went straight to the adversarial judge (evidence-only,
no narrative). Judge verdicts: H1 validated, H2 invalidated, H3 inconclusive, H4
inconclusive.

## Hypotheses

### H1 — unhandled ZeroDivisionError on zero stock (validated)

Every observed `GET /products/3` fails: four user requests (E3–E6) and one investigator
probe (E12, E16), five of five, while the same route serves other product ids with 200
between the failures (E7, E8). Each failure logs the same stack ending at
`shop.py` line 64, dividing by `product["units_in_stock"]` (E2), and the catalog shows
product 3 with `units_in_stock: 0` (E11) — the exact denominator. The prediction was
probed: one reproduction moved `http_requests_total{...,status="500"}` from 4 (E8) to 5
(E13) and `http_exceptions_total{type="ZeroDivisionError"}` from 4 (E9) to 5 (E14),
each by exactly one. No evidence contradicts the mechanism.

### H2 — chaos/degradation switch (invalidated)

`faultline_chaos_enabled` reads 0 (E10) and the full log contains zero chaos or
simulation events (E15) over the whole process lifetime. The failures are not spread
across routes or times, as injection would predict: all 500s sit on one path (E3–E6,
E16) while a neighboring product id returns 200 mid-burst (E7).

### H3 — a deploy/restart introduced the failure (inconclusive)

The process did start inside the complaint window (E1), and `/products/3` failed from
its first observed request 7 seconds later (E3) — the complaint's "no deploys that we
know of" conflicts with a minutes-old process. But no telemetry exists before the start
(E17), so there is no last-known-good to compare against, and the mechanism (an
unguarded division over a stored zero, E2 + E11) does not require a recent deploy. The
single piece of settling evidence — one pre-13:57:05Z request record for `/products/3`
with its status — is not on this surface.

### H4 — product 3's zero stock is wrong data (inconclusive)

The zero is real (E11), but zero stock is a legal catalog state (sold out), and nothing
on the surface shows a failed write, corruption, or any database error class — the only
exception type in the process lifetime is `ZeroDivisionError` (E14), raised by the
target's own division (E2). The settling evidence is the intended stock value in the
inventory source of truth, which is outside the investigator surface. Either way, the
unguarded division stands as a code defect: the code divides by a field its own catalog
serves as zero.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Have the owning engineer read `src/faultline/shop.py`, `get_product`, line 64, and
  confirm the division by `units_in_stock` has no zero guard (source code is outside
  konan's surface; the stack trace names the line).
- Check the inventory source of truth for product 3's intended `units_in_stock`; that
  single value settles H4.
- Check deploy/restart records for the process start at 13:57:05.896Z; a pre-start
  request record for `/products/3` settles H3.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the `/products/{product_id}`
  500 counter for growth from unstamped traffic — growth means customers are still
  hitting the page.
- Scan the catalog for other rows that can reach `units_in_stock = 0`; each such row
  reproduces the same 500. Product 4's `price: null` (E19) deserves a look at the same
  time, as a latent risk.

## Gaps

- **Pre-start history.** The log starts at 13:57:05.896Z and `lab/logs/` holds a single
  file, so the hour named in the complaint is only partly observable. H3 stays
  inconclusive for exactly this reason.
- **Intended data state.** The lab contract keeps ground truth (seed data, fixtures)
  outside the investigator surface, so H4's settling fact is unreachable by design.
- **Ongoing impact.** No user request appears after 13:57:19.195Z; "still happening when
  they refresh" is consistent with the deterministic defect but is not directly observed
  in fresh user traffic.
- **Source code.** The code mechanism rests on the logged stack trace; the file itself
  was not read, per the surface contract.
