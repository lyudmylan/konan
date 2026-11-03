---
konan_journal: 2
investigation:
  id: 2026-11-02-product-3-zero-stock-500s
  trigger: "manual (/konan adapter; complaint fingerprint human-1793640163, startsAt 2026-11-02T17:22:43Z, investigation start 2026-11-02T17:22:46Z — trigger latency 3s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: "2026-11-02T17:22:46Z"
  concluded: "2026-11-02T17:30:00Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's get_product handler (faultline/src/faultline/shop.py:64) divides units_ordered by units_in_stock with no zero-guard; product id 3 has units_in_stock=0, so every GET /products/3 request raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "GET /products/3 fails deterministically (not probabilistically, not chaos-driven, not infra/process-driven) because product id 3's catalog row has units_in_stock=0, which get_product divides into with no zero-guard at shop.py:64, raising ZeroDivisionError on every call."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:22:25.771Z–.780Z — first failing request, request_id 26f9e294ba3a (non-investigator traffic)"
    quote: |-
      {"ts": "2026-11-02T17:22:25.771Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "26f9e294ba3a", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n...\nZeroDivisionError: division by zero"}
      {"ts": "2026-11-02T17:22:25.780Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "26f9e294ba3a", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.137, "client": "127.0.0.1:59686"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:22:26.833Z, 17:22:29.944Z, 17:22:32.064Z — three more failing requests, same exception and same stack line (trimmed), request_ids 884e733cf748, e93f04c47960, 2a6e3c670770 (non-investigator traffic)"
    quote: |-
      {"ts": "2026-11-02T17:22:26.837Z", "message": "GET /products/3 -> 500", "request_id": "884e733cf748", "status": 500, "duration_ms": 4.875}
      {"ts": "2026-11-02T17:22:29.948Z", "message": "GET /products/3 -> 500", "request_id": "e93f04c47960", "status": 500, "duration_ms": 4.823}
      {"ts": "2026-11-02T17:22:32.069Z", "message": "GET /products/3 -> 500", "request_id": "2a6e3c670770", "status": 500, "duration_ms": 4.995}
      each immediately preceded by: {"level": "ERROR", "message": "unhandled exception: division by zero", "exception_type": "ZeroDivisionError", "stack": "...shop.py\", line 64, in get_product...ZeroDivisionError: division by zero"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:22:20.611Z–17:22:31.003Z — every non-/products/3 request in the same window, interleaved with the E1/E2 failures (non-investigator traffic)"
    quote: |-
      {"ts": "2026-11-02T17:22:20.611Z", "message": "GET /products/1 -> 200", "request_id": "b056a96274c8", "status": 200, "duration_ms": 1.072}
      {"ts": "2026-11-02T17:22:21.659Z", "message": "GET /products/2 -> 200", "request_id": "d7fb525586cc", "status": 200, "duration_ms": 1.027}
      {"ts": "2026-11-02T17:22:23.715Z", "message": "POST /orders -> 201", "request_id": "6782ebd4c408", "status": 201, "duration_ms": 1.752}
      {"ts": "2026-11-02T17:22:28.891Z", "message": "GET /products/2 -> 200", "request_id": "708f671040bf", "status": 200, "duration_ms": 0.863}
      {"ts": "2026-11-02T17:22:31.003Z", "message": "POST /orders -> 201", "request_id": "490b253821f9", "status": 201, "duration_ms": 1.442}
  - id: E4
    type: metric
    source: "probe /metrics, request_id=konan-1793640219-96809 @ 2026-11-02T17:23:39.453Z — baseline snapshot"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
      faultline_chaos_enabled 0
  - id: E5
    type: probe
    source: "probe /products, request_id=konan-1793640558-97027 @ 2026-11-02T17:29:18.926Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.003820s request_id=konan-1793640558-97027
  - id: E6
    type: probe
    source: "probe /products/3, request_id=konan-1793640563-97033 @ 2026-11-02T17:29:23.043Z–.048Z — investigator reproduction, confirming the defect is still active at conclusion"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793640563-97033"}
      -- HTTP 500 in 0.005645s request_id=konan-1793640563-97033
      {"ts": "2026-11-02T17:29:23.048Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793640563-97033", "status": 500, "duration_ms": 4.757}
  - id: E7
    type: log
    source: "lab/logs/app.log — full read, line 1 of 35; only occurrence of event=startup, no shutdown/restart/crash marker anywhere in the remaining 34 lines of the current process's log"
    quote: |-
      {"ts": "2026-11-02T17:22:18.637Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E8
    type: log
    source: "lab/logs/app.log — full read, 35 lines: zero occurrences of event values chaos_enabled/chaos_disabled/chaos_failure/simulated_exception, and zero HTTP 422 statuses anywhere in the log; cross-checked against E4's faultline_chaos_enabled reading"
    quote: |-
      grep across all 35 lines: 0 matches for "chaos_enabled"|"chaos_disabled"|"chaos_failure"|"simulated_exception"; 0 matches for "status": 422; all statuses observed are 200, 201, or 500 (ZeroDivisionError-caused)
gaps:
  - "Cannot confirm or refute 'no deploys that we know of' from telemetry: the investigator's surface (docs/lab.md) exposes no deploy/release timeline or git history, and the log only covers the current process's single lifetime starting 2026-11-02T17:22:18Z. Whether product 3's zero-stock state (the defect's trigger condition) predates this process start, or changed at/after it, could not be determined — flagged as unaddressed by the adversarial judge."
  - "Did not enumerate whether product ids beyond the 5 returned by GET /products (1-5) exist with their own zero-stock rows, since none of the complaint's evidence pointed past id 3; cannot rule out other currently-unopened product pages carrying the same latent trigger."
  - "data-db and third-party incident classes were not independently probed beyond what E7/E8 already rule out (process stability, no chaos/validation markers) — this lab target has no real database or third-party dependency (docs/lab.md, 'Known gaps of this lab'), so those classes had no further surface to test."
usage:
  model: claude-sonnet-5
  tokens: 3191717
  wall_clock_seconds: 434
---

# Product detail page 500s: ZeroDivisionError on zero-stock product (id 3)

## Summary

**Root cause identified.** `GET /products/3` ("Unobtainium Ingot") returns HTTP 500 on
every request because `faultline/src/faultline/shop.py:64` divides
`units_ordered / units_in_stock` with no guard against zero, and product id 3's catalog
row carries `units_in_stock=0` (E5). The failure is 100% reproducible, confined to that
one product id, and independent of chaos mode (disabled throughout, E4/E8), process
health (one clean startup, no restarts, E7), or malformed input (zero HTTP 422s, E8).
Four non-investigator requests to `/products/3` failed before this investigation began
(E1, E2), while `/products/1`, `/products/2`, and `/orders` succeeded throughout the same
window (E3) — matching the complaint exactly: one product page down, others fine. A
fresh investigator probe at conclusion reproduced the identical failure (E6), confirming
the defect is still live. Confidence: high, validated by an adversarial judge with one
open caveat — the telemetry available cannot confirm or refute whether the zero-stock
condition (and thus the defect's trigger) predates this process's one lifetime, so "no
deploys that we know of" is unaddressed rather than disproven (see Gaps).

## Timeline

- **17:22:18.637Z** — faultline process starts; the only lifecycle event in the log (E7).
- **17:22:20.611Z–17:22:21.659Z** — `/products/1`, `/products/2` succeed (E3).
- **17:22:23.715Z** — order placed for product 1, succeeds (E3).
- **17:22:25.771Z** — first `/products/3` failure: `ZeroDivisionError` at `shop.py:64` (E1).
- **17:22:26.833Z / 17:22:29.944Z / 17:22:32.064Z** — three more `/products/3` failures,
  identical mechanism (E2), interleaved with successful `/products/2` and an order for
  product 2 at 17:22:28.891Z and 17:22:31.003Z (E3) — ruling out a general outage.
- **17:23:39.453Z** — investigator baseline `/metrics`: 4 failed / 3 succeeded on the
  product-detail route, exception counter at 4, chaos off (E4).
- **17:29:18.926Z–17:29:23.048Z** — investigator confirms product 3's stock is 0 (E5) and
  reproduces the identical 500/`ZeroDivisionError` (E6).

## Investigation

Baseline: `/health` (ok, uptime ~77s), `/metrics` (4/7 `/products/{id}` calls at 500,
`ZeroDivisionError` x4, chaos off), and the full `lab/logs/app.log` tail (35 lines total).
Triage fanned out to all three lenses in parallel, each blind to the others and to this
report: `infra-process` found no restart/resource anomalies; `interfaces` found no
malformed-request or chaos/gateway anomalies (and flagged the zero-stock data point for
the next lens); `software-defect` identified the mechanism and reproduced it with its own
probe. Because the triage evidence was already deterministic and complete — a named code
line, a reproducible trigger condition, and alternative causes independently ruled out —
the single hypothesis skipped deep-dive and went straight to an adversarial judge. The
judge validated it, finding every alternative explanation (chaos injection, transient
blip/race, malformed request, restart) directly ruled out by the cited evidence, with one
caveat: deploy/data-change timing attribution has no direct support in the available
telemetry (noted under Gaps).

## Hypotheses

### H1 — zero-stock division bug in `get_product` (validated)

`shop.py:64` computes `turnover_score = units_ordered / units_in_stock` with no zero
check. Product id 3 is the only catalog row with `units_in_stock=0` (E5), so every call to
`GET /products/3` raises `ZeroDivisionError` and the request fails with HTTP 500 (E1, E2,
E6). Every other observed route and product id in the same window succeeded (E3, E4). The
process itself was stable throughout — one clean startup, no restarts (E7) — and there is
no sign of chaos injection, gateway failure, or malformed input (E4, E8), which rules out
`infra-process` and `interfaces` as competing explanations. The judge validated this
hypothesis without reservation on the mechanism; its only open item is attribution of
*when* the zero-stock condition arose, which the investigator's surface cannot settle.

## Safe next steps

- Poll `GET /products` periodically (read-only) to watch whether product 3's stock
  changes, or whether any other product id drops to zero and would reproduce the same
  failure shape.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{method="GET",path="/products/{product_id}",status="500"}` on
  `/metrics` to track whether impact is still confined to product 3 or is spreading.
- If support can share which product IDs or request IDs customers hit, grep
  `lab/logs/app.log` for those request IDs to confirm scope and count of affected
  customers precisely, beyond "several."

## Gaps

- Cannot confirm or refute "no deploys that we know of" from telemetry: the
  investigator's surface (`docs/lab.md`) exposes no deploy/release timeline or git
  history, and the log only covers the current process's single lifetime starting
  2026-11-02T17:22:18Z. Whether product 3's zero-stock state predates this process start,
  or changed at/after it, could not be determined — flagged as unaddressed by the
  adversarial judge.
- Did not enumerate whether product ids beyond the 5 returned by `GET /products` (1-5)
  exist with their own zero-stock rows, since none of the complaint's evidence pointed
  past id 3; cannot rule out other currently-unopened product pages carrying the same
  latent trigger.
- `data-db` and `third-party` incident classes were not independently probed beyond what
  E7/E8 already rule out (process stability, no chaos/validation markers) — this lab
  target has no real database or third-party dependency (`docs/lab.md`, "Known gaps of
  this lab"), so those classes had no further surface to test.
