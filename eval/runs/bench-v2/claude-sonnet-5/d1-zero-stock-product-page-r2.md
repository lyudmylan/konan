---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-500s
  trigger: manual
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T17:32:55Z
  concluded: 2026-11-02T17:38:09Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} computes turnover_score as units_ordered divided by units_in_stock with no zero-guard; product id 3 (Unobtainium Ingot) has units_in_stock=0, so every request for that one product raises an unhandled ZeroDivisionError and returns HTTP 500, while every other product page is unaffected."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "GET /products/3 fails deterministically because shop.py's get_product divides units_ordered by units_in_stock, and product 3's units_in_stock is 0."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by a process crash/restart loop or an internal chaos/degradation switch, not a code defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2]
  - id: H3
    statement: "The 500s are caused by a gateway/config-change event or probabilistic injected degradation at a boundary, not a deterministic per-input code defect."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:32:29.340Z"
    quote: "{\"ts\": \"2026-11-02T17:32:29.340Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} — the only startup event in the whole log file; no restart, no crash loop."
  - id: E2
    type: metric
    source: "GET /metrics @ 2026-11-02T17:33:38Z (request_id konan-1793640818-97226)"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4 / http_exceptions_total{type=\"ZeroDivisionError\"} 4 / faultline_chaos_enabled 0"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:32:36.243Z (request_id f384b58a8238, non-konan — real client traffic)"
    quote: "unhandled exception: division by zero ... File \".../faultline/src/faultline/shop.py\", line 64, in get_product\\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\\nZeroDivisionError: division by zero — followed by \"GET /products/3 -> 500\" status=500 duration_ms=11.113, same request_id"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T17:32:37.309Z–17:32:42.518Z (request_ids 301bfbfced80, 07a471ac9be8, ce160c9cd9fa — all non-konan, real client traffic)"
    quote: "three further occurrences of the identical traceback at shop.py:64 ending \"ZeroDivisionError: division by zero\", each immediately followed by \"GET /products/3 -> 500\" sharing the same request_id as its exception line; no occurrence for any path other than /products/3"
  - id: E5
    type: probe
    source: "scripts/probe.sh /products (request_id konan-1793640819-97231)"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E6
    type: probe
    source: "scripts/probe.sh /products/1 (request_id konan-1793640832-97237)"
    quote: "{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118,\"units_ordered\":2,\"turnover_score\":0.01694915254237288} -- HTTP 200"
  - id: E7
    type: probe
    source: "scripts/probe.sh /products/4 (request_id konan-1793640833-97252)"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200 (null price does not fail — isolates units_in_stock=0, not price, as the relevant variable)"
  - id: E8
    type: probe
    source: "scripts/probe.sh /products/3, two independent calls (request_id konan-1793640833-97247, then konan-1793640843-97265, 10s apart)"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1793640833-97247\"} -- HTTP 500; repeated: {\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1793640843-97265\"} -- HTTP 500"
gaps:
  - "The surface contract (docs/lab.md) exposes only current inventory state via /products and /products/{id}, with no history/audit endpoint, and the log file covers only since the 2026-11-02T17:32:29Z process startup. Telemetry confirms units_in_stock was 0 for the full observed window but cannot confirm when it reached 0 — it neither confirms nor refutes the complaint's 'started within the last hour' framing."
  - "No direct database/inventory access is in the investigator's read-only HTTP surface, so whether units_in_stock=0 for product 3 is itself a data error (vs. legitimate zero stock) could not be checked from this side of the boundary."
  - "No dedicated infra-process or interfaces triage-lens subagents were spawned. Baseline telemetry (E1: single clean startup event; E2: chaos disabled and a failure pattern concentrated 100% on one route+input) already excluded both classes with evidence, so the sweep was judged unnecessary rather than left unexamined — recorded here for transparency per the triage rule."
usage:
  model: claude-sonnet-5
  tokens: 1788749
  wall_clock_seconds: 314
---

# Product page 500s: /products/3 divides by zero stock

## Summary

**Root cause identified.** GET `/products/3` (the "Unobtainium Ingot" product page) fails on
every request with HTTP 500. The handler computes `turnover_score = units_ordered /
units_in_stock` (`faultline/src/faultline/shop.py:64`) with no guard for zero stock; product
3's `units_in_stock` is `0`, so the division raises `ZeroDivisionError` on every call,
deterministically. Every other product id (1, 2, 4, 5) returns 200, including product 4
whose `price` is `null` — isolating stock-at-zero, not the null price, as the trigger. Real
client traffic (non-`konan-` request ids) was already hitting this failure before the
investigation began, confirming active user impact matching the complaint, not a
latent/investigator-only defect. No chaos switch, restart, or config-change marker was found
in telemetry, so this is a code defect, not infrastructure or a boundary issue. Confidence:
high — reproduced twice independently, with a full matching stack trace.

## Timeline

- `2026-11-02T17:32:29.340Z` — faultline process starts; the only startup event in the log (E1).
- `2026-11-02T17:32:36.243Z`–`17:32:42.518Z` — four real-client requests (non-`konan-` ids) to
  `/products/3` each raise `ZeroDivisionError` and return 500 (E3, E4).
- `2026-11-02T17:32:49Z` — complaint received via `/konan` (trigger latency to investigation
  start: 6s).
- `2026-11-02T17:33:38Z` — baseline `/metrics` scrape shows 4/4 requests to `/products/{id}`
  already failed, `faultline_chaos_enabled 0` (E2).
- `2026-11-02T17:33:52Z`–`17:34:04Z` — investigator probes: `/products/1`, `/products/4` succeed
  (E6, E7); `/products/3` fails twice more, deterministically (E8).
- `2026-11-02T17:38:09Z` — adversarial judge validates H1; investigation concludes.

## Investigation

**Baseline** (`/health`, `/metrics`, log tail) surfaced the anomaly directly: `/metrics`
already showed 4 failed `/products/{product_id}` requests against 3 succeeded, all tagged
`ZeroDivisionError`, before any investigator probe had touched that route. The log tail
(the full file, 34 lines, one process lifetime) showed the exact throwing line and that every
failure was for `/products/3`, from four distinct non-`konan` request ids — real traffic, not
investigator-triggered.

Because this evidence was already deterministic (same input → same failure, confirmed twice)
and already excluded the competing classes — `faultline_chaos_enabled 0` and a single clean
startup event rule out `infra-process`; a 100%-on-one-input split with no config-change marker
anywhere in the log rules out `interfaces` — no triage-lens subagents or deep-dive rounds were
needed. One adversarial judge subagent reviewed H1 against the full evidence set, blind to
this narrative, and returned **validated**.

## Hypotheses

### H1 — software-defect: zero-stock division (validated)

`shop.py:64` divides `units_ordered` by `units_in_stock` unconditionally. Product 3 has
`units_in_stock: 0` (E5), so every request to `/products/3` throws (E3, E4, E8 — two
independent reproductions). Products 1 and 4 succeed with the same code path, including the
null-price product 4 (E6, E7), isolating zero stock as the variable that matters. Judge
verdict: validated, no missing evidence identified.

### H2 — infra-process: crash/restart/chaos switch (invalidated)

A single clean startup with no subsequent restart (E1), and `faultline_chaos_enabled 0` at
the time of the failures (E2), rule this out.

### H3 — interfaces: gateway/config-change/probabilistic degradation (invalidated)

The failure rate is 100% concentrated on one route+input, not a probabilistic fraction spread
across routes (E2, E4), and no configuration or flag-change marker appears anywhere in the
log. This is the per-input deterministic shape of a code defect, not a boundary fault.

## Safe next steps

- Re-run `GET /products/3` after confirming (read-only) whether `units_in_stock` for that
  product is still 0, to see if the condition has changed.
- Check `/metrics` periodically for `http_exceptions_total{type="ZeroDivisionError"}` growth
  to gauge ongoing customer impact while this is triaged.
- Pull the full list of product ids from `/products` and probe each `/products/{id}` read-only
  to confirm no other product currently has `units_in_stock: 0` (would predict the same page
  failing for a different product).

## Gaps

- Telemetry available to the investigator starts at process startup (`2026-11-02T17:32:29Z`)
  and the `/products`/`/products/{id}` surface only exposes current state, not inventory
  history — so when `units_in_stock` first reached 0 for product 3 could not be determined
  from this side of the boundary. The complaint's "started within the last hour" framing is
  therefore neither confirmed nor refuted by telemetry; only that it was already 0 for the
  entire observed window.
- No direct database access is in the read-only HTTP surface, so whether a stock value of
  exactly 0 is itself a data error versus a legitimate inventory state could not be checked.
- Dedicated `infra-process` and `interfaces` triage-lens subagents were not spawned; baseline
  evidence (E1, E2) already excluded both classes deterministically, so the sweep was skipped
  by evidence, not left unchecked. Recorded here per the triage rule's disclosure requirement.
