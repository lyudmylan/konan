---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-zero-stock-500
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-02T20:20:23Z
  concluded: 2026-11-02T20:29:40Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError (HTTP 500) for product id 3 specifically, because the server computes turnover_score = units_ordered / units_in_stock and product 3 (\"Unobtainium Ingot\") has units_in_stock: 0; the failure is deterministic to this one input and does not occur for other product ids."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: []
  - id: H2
    statement: "Non-investigator (real customer or simulated end-user) traffic actually reached the failing /products/3 route and experienced the 500 within the observed telemetry window — i.e. this is the active, customer-impacting incident rather than a defect only the investigator's own probing exercised."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E9]
latent_findings:
  - statement: "faultline's /products/{id} handler unconditionally divides units_ordered by units_in_stock; any request — investigator or customer — to a product with zero stock (currently only product id 3) will deterministically 500 with ZeroDivisionError. Real, reproducible, but in the observed telemetry window it has only ever been exercised by this investigation's own probes."
    evidence: [E1, E2, E3, E4, E5, E6]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /products/3 @ request_id konan-1793651032-4164"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1793651032-4164\"} -- HTTP 500 in 0.003500s request_id=konan-1793651032-4164"
  - id: E2
    type: probe
    source: "scripts/probe.sh /products @ request_id konan-1793651034-4169"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":40},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}] -- HTTP 200"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:23:52.644Z (stack trimmed of framework frames and of the local filesystem path prefix)"
    quote: "{\"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1793651032-4164\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"Traceback (most recent call last):\\n  ...\\n  File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\\nZeroDivisionError: division by zero\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:23:52.646Z"
    quote: "{\"ts\": \"2026-11-02T20:23:52.646Z\", \"level\": \"INFO\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1793651032-4164\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 2.763}"
  - id: E5
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1793651097-4230"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 7 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 7"
  - id: E6
    type: probe
    source: "scripts/probe.sh /products/1 @ request_id konan-1793651107-4236"
    quote: "{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119,\"units_ordered\":1,\"turnover_score\":0.008403361344537815} -- HTTP 200"
  - id: E7
    type: log
    source: "lab/logs/app.log — grep -n '/products/3' lab/logs/app.log, 7 of 7 matches, trimmed to kept fields"
    quote: "{\"ts\":\"2026-11-02T20:22:33.730Z\",\"request_id\":\"konan-1793650953-4031\",\"path\":\"/products/3\",\"status\":500} {\"ts\":\"2026-11-02T20:22:33.798Z\",\"request_id\":\"konan-1793650953-4051\",\"path\":\"/products/3\",\"status\":500} {\"ts\":\"2026-11-02T20:22:38.339Z\",\"request_id\":\"konan-1793650958-4065\",\"path\":\"/products/3\",\"status\":500} {\"ts\":\"2026-11-02T20:22:38.355Z\",\"request_id\":\"konan-1793650958-4068\",\"path\":\"/products/3\",\"status\":500} {\"ts\":\"2026-11-02T20:22:38.370Z\",\"request_id\":\"konan-1793650958-4071\",\"path\":\"/products/3\",\"status\":500} {\"ts\":\"2026-11-02T20:22:40.842Z\",\"request_id\":\"konan-1793650960-4087\",\"path\":\"/products/3\",\"status\":500} {\"ts\":\"2026-11-02T20:23:52.646Z\",\"request_id\":\"konan-1793651032-4164\",\"path\":\"/products/3\",\"status\":500} — every one of the 7 request ids carries the \"konan-\" prefix this session's scripts/probe.sh stamps on its own traffic."
  - id: E8
    type: log
    source: "lab/logs/app.log — complete set of non-\"konan-\"-prefixed (non-investigator) request lines in the file"
    quote: "{\"ts\":\"2026-11-02T20:20:05.793Z\",\"request_id\":\"a2acf5238a9f\",\"path\":\"/health\",\"status\":200} {\"ts\":\"2026-11-02T20:20:05.800Z\",\"request_id\":\"66ab9ff829b1\",\"path\":\"/health\",\"status\":200} {\"ts\":\"2026-11-02T20:20:05.820Z\",\"request_id\":\"9c75d27f40ee\",\"path\":\"/products\",\"status\":200} {\"ts\":\"2026-11-02T20:20:06.879Z\",\"request_id\":\"215c7c263c4c\",\"path\":\"/products/1\",\"status\":200} {\"ts\":\"2026-11-02T20:20:07.937Z\",\"request_id\":\"d1f87762f862\",\"path\":\"/products/2\",\"status\":200} {\"ts\":\"2026-11-02T20:20:08.994Z\",\"request_id\":\"12ff8dafec74\",\"path\":\"/orders\",\"status\":201} {\"ts\":\"2026-11-02T20:20:10.051Z\",\"request_id\":\"936b69146c9a\",\"path\":\"/orders\",\"status\":200} {\"ts\":\"2026-11-02T20:20:11.108Z\",\"request_id\":\"744a566be381\",\"path\":\"/products/5\",\"status\":200} — none hit /products/3, none are non-200/201."
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:20:05.023Z (first line of the file)"
    quote: "{\"ts\": \"2026-11-02T20:20:05.023Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
gaps:
  - "No separate ingress/gateway/CDN access log was checked for additional /products/3 hits from real customer traffic not captured in app.log — docs/lab.md names app.log and /metrics as the complete investigator-visible telemetry surface and does not reference an edge log; if one exists outside that contract it is out of reach by design. This is the judge's named settling evidence for H2."
  - "app.log begins at this faultline process's own startup marker (E9) with no rotated .1-.3 backups present, so any telemetry from a prior process instance (if faultline had been running earlier and restarted before this investigation began) is unavailable."
usage:
  model: claude-sonnet-5
  tokens: 4468802
  wall_clock_seconds: 557
---

# GET /products/3 deterministically 500s on zero stock — no confirmed customer impact yet

## Summary

**Verdict: no active incident**, with one real latent defect riding along. A deterministic,
fully reproduced software defect exists: `GET /products/3` always raises `ZeroDivisionError`
and returns HTTP 500 (E1, E3, E4), because the product page handler computes
`turnover_score = units_ordered / units_in_stock` and product 3 ("Unobtainium Ingot") has
`units_in_stock: 0` (E2) — the only catalog item at zero stock. A control probe on product 1
confirms the same formula works fine with nonzero stock (E6), and the exception counter
matches the 500 counter exactly, 7 for 7 (E5): this is a genuine, deterministic code defect
(software-defect / unhandled-exception), not noise.

However, every single occurrence of this failure in the complete available telemetry (7 of 7,
E7) carries this investigation's own `konan-`-prefixed request id. The complete population of
non-investigator traffic visible in the log (8 requests, E8) never touches `/products/3` and
is 100% successful. Per the investigation's own rule — a defect only the investigator's probes
have triggered is a latent finding, not a confirmed active incident — this cannot be reported
as root-cause-identified for the support complaint. The complaint may well be describing exactly
this defect, but the telemetry available right now does not show any customer request having
hit it.

## Timeline

- `2026-11-02T20:20:19Z` — complaint received (human report via support, verbatim): "Support
  says several customers see 'Internal Server Error' when opening a product page this
  morning." (`fingerprint: human-1793650819`, source: human, no severity stated.)
- `2026-11-02T20:20:23Z` — investigation started (trigger latency from complaint to start: 4s).
- `2026-11-02T20:20:05.023Z` (E9) — faultline process startup marker; this is the earliest
  timestamp in the only available log file, so the entire observable history runs from here.
- `2026-11-02T20:20:05Z`–`20:20:11Z` (E8) — the only non-investigator traffic in the log: 8
  requests across `/health`, `/products`, `/products/1`, `/products/2`, `/orders` (GET+POST),
  `/products/5` — all 200/201, none to `/products/3`.
- `2026-11-02T20:22:33Z`–`20:23:52Z` (E7, E1, E3, E4) — this investigation's own probes to
  `/products/3`, 7 of 7 returning 500 with `ZeroDivisionError`.
- `2026-11-02T20:29:40Z` — investigation concluded.

## Investigation

**Baseline**: `/health` 200, `process_uptime_seconds` ~66s at first probe (fresh process),
`faultline_chaos_enabled 0`, `http_exceptions_total` empty, all logged requests 200/201 at
that point. Only one log file present, no rotation backups.

**Triage** — three lenses spawned in parallel, each given only the lens file, `docs/lab.md`,
the complaint verbatim, and the baseline summary:
- *infra-process*: no anomalies — no restart, no uptime reset, no saturation, no latency
  deterioration, chaos toggle off.
- *interfaces*: found a 100%-reproducible failure on `/products/3` specifically (not a stable
  fraction / gateway-shaped pattern), correctly classified it as deterministic per-input and
  routed it to the software-defect lens rather than claiming it.
- *software-defect*: reproduced the failure 6/6, pulled the stack trace and exception type,
  confirmed every other catalog id (including edge cases 0, -1, 999999, non-numeric) handled
  correctly (404/422, not 500) — isolating the defect to product id 3 only.

All three lenses converged on the same mechanism with deterministic, complete evidence, so
per the investigation's own rule this hypothesis skipped deep-dive and went straight to the
judge. Before judging, the orchestrator additionally checked request-id provenance on every
`/products/3` log line and found all matches were investigator-stamped — material enough to
form a second hypothesis about customer-impact evidence (H2) for the judge to weigh.

**Judge** (adversarial, evidence-only, blind to lens narrative): H1 validated — "all cited
evidence points the same way, with no contrary evidence cited." H2 invalidated — "these show
zero non-investigator requests to the failing route anywhere in the observed telemetry — the
opposite of what H2 claims." Settling evidence named for H2: confirmation that app.log is the
sole ingress log (no separate gateway/CDN log exists that could hide additional real traffic).

## Hypotheses

### H1 — validated
GET /products/3 deterministically raises ZeroDivisionError (500) because turnover_score
divides by a zero stock count unique to that product. Evidence: E1–E6. No evidence against.

### H2 — invalidated
No telemetry shows non-investigator traffic ever reaching `/products/3`. Evidence against:
E7, E8, E9. Nothing cited for it.

## Safe next steps

- Re-check `/metrics` and `/products/3` periodically (read-only) to see if the exception
  counter grows from traffic not stamped `konan-` — that would convert this from a latent
  finding into a confirmed active incident.
- If support can share one example request's timestamp or any client-side request id from an
  affected customer, correlate it against `lab/logs/app.log` (or, if available, any upstream
  gateway/CDN access log outside this contract) to check for a genuine customer hit on
  `/products/3`.
- Ask support whether the affected customers' reports name a specific product, to check
  whether they match product id 3 ("Unobtainium Ingot").

## Gaps

- No separate ingress/gateway/CDN access log was checked for additional `/products/3` hits
  from real customer traffic not captured in `app.log` — `docs/lab.md` names `app.log` and
  `/metrics` as the complete investigator-visible telemetry surface and does not reference an
  edge log; out of reach by design if one exists. This is the judge's named settling evidence
  for H2.
- `app.log` begins at this faultline process's own startup marker (E9) with no rotated
  `.1`–`.3` backups present, so telemetry from any prior process instance, if one ran and
  restarted before this investigation began, is unavailable.
