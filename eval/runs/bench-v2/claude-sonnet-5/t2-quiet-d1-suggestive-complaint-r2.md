---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-zero-stock-500
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-02T20:33:24Z
  concluded: 2026-11-02T20:41:08Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The GET /products/{id} handler computes turnover_score as units_ordered / units_in_stock; product 3 ('Unobtainium Ingot') has units_in_stock=0, so every request to that product's page raises an unhandled ZeroDivisionError and returns 500 Internal Server Error, deterministically, while every other product page succeeds."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "GET /products/3 fails with 500 due to an unhandled ZeroDivisionError in the turnover_score calculation (units_ordered / units_in_stock) because product 3 has zero stock; the failure is confined to that one product id."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:33:00.720Z"
    quote: "{\"ts\": \"2026-11-02T20:33:00.720Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:35:41.488Z (request_id konan-1793651741-4663)"
    quote: "{\"message\": \"unhandled exception: division by zero\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n...ZeroDivisionError: division by zero\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:35:41.497Z (request_id konan-1793651741-4663)"
    quote: "{\"ts\": \"2026-11-02T20:35:41.497Z\", \"message\": \"GET /products/3 -> 500\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 9.565}"
  - id: E4
    type: probe
    source: "GET /products (request_id konan-1793651873-4805)"
    quote: "[{\"id\":1,\"name\":\"Anvil\",...,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",...,\"units_in_stock\":40},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",...,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",...,\"units_in_stock\":500}]"
  - id: E5
    type: metric
    source: "GET /metrics (request_id konan-1793651873-4808)"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 5 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 5 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 9 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"404\"} 4"
  - id: E6
    type: log
    source: "lab/logs/app.log, repeated reproductions and contrast ids, 2026-11-02T20:35:42Z-20:36:20Z"
    quote: "GET /products/3 -> 500 (request_id konan-1793651749-4704, konan-1793651780-4771, konan-1793651780-4775, konan-1793651780-4779) vs GET /products/4 -> 200 (konan-1793651742-4668), GET /products/1 -> 200 (konan-1793651745-4673), GET /products/6 -> 404 (konan-1793651758-4731) in the same window"
  - id: E7
    type: metric
    source: "GET /metrics, successive probes 2026-11-02T20:34:14Z-20:36:19Z"
    quote: "faultline_chaos_enabled 0 (unchanged across all probes); process_uptime_seconds climbing monotonically 73.3 -> 152.77 -> 194.03 -> 292.70 with no reset"
  - id: E8
    type: log
    source: "lab/logs/app.log, full file"
    quote: "exactly one line with \"event\": \"startup\" in the entire log (E1); no second startup line, no crash/exit event anywhere in the file"
gaps:
  - "The observable log window begins at process start (2026-11-02T20:33:00.720Z, E1); no rotated backups exist, so there is no telemetry from before that point. Every logged hit on /products/3 that returned 500 came from an investigator probe (request_id prefixed konan-); no non-investigator traffic was observed reaching /products/3 in-window. The root cause is grounded in the defect's determinism and product 3's presence in the normal catalog listing (E4) that any customer browses, not in a directly observed customer request that failed."
  - "load-saturation, third-party, and data-db incident classes have no triage lens in this repo and faultline has no real database or third-party dependency (docs/lab.md, Known gaps) — those classes could not be investigated on this target."
usage:
  model: claude-sonnet-5
  tokens: 2783102
  wall_clock_seconds: 464
---

# GET /products/3 returns 500: zero-stock division by zero in turnover_score

## Summary

**Root cause identified.** Product 3 ("Unobtainium Ingot") is listed in the shop catalog
with `units_in_stock: 0` (E4). The `GET /products/{id}` handler unconditionally computes
`turnover_score = units_ordered / units_in_stock` (E2); for product 3 this divides by
zero, raising an unhandled `ZeroDivisionError` that FastAPI surfaces as a 500 Internal
Server Error (E2, E3). The failure is 100% deterministic and confined to this one product:
every probe against `/products/3` fails the same way, while `/products/1`, `/products/2`,
`/products/4`, `/products/5` succeed and unknown ids return clean 404s (E6). Chaos mode is
off and the process has not restarted or leaked resources (E7, E8), ruling out
infrastructure causes. This matches the complaint exactly: a customer opening this
product's page gets "Internal Server Error." Confidence is high on the mechanism; the one
open question is how long this has been reachable by real traffic (see Gaps) — the
telemetry window only covers the last few minutes.

## Timeline

- **2026-11-02T20:33:00.720Z** — process start, only startup marker in the log (E1, E8).
- **2026-11-02T20:33:01Z–20:33:06Z** — pre-investigation traffic: health checks, catalog
  browse, successful views of products 1/2/5, one order placed — no errors.
- **2026-11-02T20:35:41.488Z** — first investigator probe of `/products/3` raises
  `ZeroDivisionError` in `shop.py:64` (E2), logged as `GET /products/3 -> 500` nine
  milliseconds later (E3).
- **2026-11-02T20:35:49Z, 20:36:20Z (×3)** — reproduced four more times, same exception,
  same route, 5/5 failures (E6); contrasted against ids 1 and 4 (200) and 6 (404) in the
  same window.
- **20:36:19Z–20:41:08Z** — final metrics snapshot: `http_exceptions_total{type="ZeroDivisionError"} 5`,
  `http_requests_total{...,status="500"} 5` — exactly matching the five reproductions,
  no other path or id contributing (E5).

## Investigation

1. **Baseline**: fresh process (uptime ~73s at first check), chaos off, zero exceptions,
   clean recent request log.
2. **Triage, three lenses in parallel** (software-defect, infra-process, interfaces):
   software-defect found the deterministic `ZeroDivisionError` on `/products/3` and
   confirmed it reproduces, confined to that one id; infra-process found no restart loop,
   no RSS growth, no chaos/latency signature; interfaces found no gateway-shaped statuses,
   no config-change marker, and confirmed the failure is deterministic per-input rather
   than probabilistic — explicitly handing the finding to the software-defect lens.
3. Evidence was already deterministic and complete across three independent lenses, so
   deep-dive was skipped (per budget rule) and the hypothesis went straight to judgment.
4. **Judge** (fresh subagent, evidence-only): verdict **validated** — the stack trace,
   the zero-stock catalog entry, the exact match between exception count and 500 count,
   and the contrast against succeeding/404 ids all support the mechanism; alternate
   infra/interface causes are ruled out by the chaos/restart/latency evidence. The judge
   flagged one caveat (below, carried into Gaps): all cited request ids are
   investigator-stamped.

## Hypotheses

### H1 — zero-stock division by zero on `/products/3` (validated)

**For:** stack trace pinpointing `shop.py:64`, `units_ordered / product["units_in_stock"]`
(E2); catalog entry showing `units_in_stock: 0` for product 3 (E4); the 500 access line
sharing the same request id as the exception (E3); five-for-five reproduction with the
global exception/500 counters matching exactly (E5, E6); no chaos toggle, no restart, no
resource trend that could explain it instead (E7, E8).

**Against:** none found.

## Safe next steps

- Re-run `GET /products/3` once more via `scripts/probe.sh` at a later time to confirm the
  defect is still live (read-only, no state change).
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}` on `/metrics` going
  forward — any further increase confirms continued customer exposure.
- Check whether other catalog ids reach zero stock over time (re-probe `GET /products`
  periodically); any item hitting `units_in_stock: 0` will reproduce this same failure
  mode under the current code.

## Gaps

- The log only covers the process's current lifetime (started 2026-11-02T20:33:00.720Z,
  E1); there are no rotated backups, so nothing from "this morning" as the complaint
  describes is directly visible. Every `/products/3` 500 actually observed was triggered
  by an investigator probe (request id prefixed `konan-`); no non-investigator traffic was
  seen hitting that id in the observable window. The conclusion rests on the defect's
  proven determinism and product 3's visible presence in the normal `/products` catalog
  (E4) — the path a real customer would take — rather than on a directly witnessed
  customer failure.
- `load-saturation`, `third-party`, and `data-db` incident classes have no triage lens in
  this repo, and faultline has no real database or third-party dependency (docs/lab.md,
  "Known gaps of this lab") — those classes were structurally out of reach on this target.
