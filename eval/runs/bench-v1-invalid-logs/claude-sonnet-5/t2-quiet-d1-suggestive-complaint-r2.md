---
konan_journal: 1
investigation:
  id: 2026-08-18-products-3-support-report
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-18T20:47:11Z
  concluded: 2026-08-18T20:52:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The complaint's report of customers seeing 'Internal Server Error' (HTTP 500) on product pages this morning reflects an active incident currently affecting real (non-investigator) user traffic."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7]
  - id: H2
    statement: "GET /products/3 deterministically returns HTTP 500 because get_product() computes units_ordered / product['units_in_stock'] and product 3 has zero stock, raising ZeroDivisionError in faultline/src/faultline/shop.py line 64."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4]
    evidence_against: []
  - id: H3
    statement: "Real client traffic received transient HTTP 503 Service Unavailable errors during three brief chaos-mode windows earlier in the session, each self-resolving within seconds; chaos mode is currently disabled."
    incident_class: interfaces
    state: validated
    evidence_for: [E8, E9]
    evidence_against: []
latent_findings:
  - statement: "The /products/3 ZeroDivisionError (H2) is a real, reproducible defect, but every occurrence in the retained log — and this investigation's own confirmation probe — carries an investigator-stamped request id; no real customer has been observed triggering it."
    evidence: [E1, E4, E5]
  - statement: "The service process restarted 8 times inside the ~1-hour retained log window, some only ~1 minute apart. Restarts are clean (ordinary 200-status request immediately precedes each 'Shutting down' line, no crash/exception adjacent) and uncorrelated with either the ZeroDivisionError events or the chaos-503 windows, but the cadence itself is unexplained by any evidence on the investigator's surface."
    evidence: [E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.043Z"
    quote: "\"level\": \"ERROR\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"request_id\": \"konan-1787083912-22619\" ... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\\n ... ZeroDivisionError: division by zero"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.050Z"
    quote: "\"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787083912-22619\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500"
  - id: E3
    type: probe
    source: "GET /products, request_id=konan-1787086294-24616"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":40},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E4
    type: probe
    source: "GET /products/3, request_id=konan-1787086176-24465"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787086176-24465\"} -- HTTP 500"
  - id: E5
    type: log
    source: "lab/logs/app.log, grep '\"path\": \"/products/3\"' over the full retained window (2026-08-18T19:52:52Z onward)"
    quote: "6 lines, all status 500, request_id values: konan-1787083912-22619, konan-1787083917-22635, konan-1787084665-23136, konan-1787084691-23226, konan-1787084820-23309, konan-1787085508-23761 — every request_id begins 'konan-'; zero non-konan-prefixed request_id appears on path /products/3 anywhere in the file"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:35:38.922Z"
    quote: "\"message\": \"GET /products/1 -> 200\", \"request_id\": \"f9a6684bdc05\", \"event\": \"request\", \"path\": \"/products/1\", \"status\": 200"
  - id: E7
    type: log
    source: "lab/logs/app.log, grep of all 'event':'request' lines with non-konan-prefixed request_id, path+status breakdown"
    quote: "non-konan traffic paths observed: /chaos/disable 200, /chaos/enable 200, /health 200, /orders 200/201/503, /products 200/503, /products/1 200, /products/2 200/503, /products/5 200 — path /products/3 does not appear in this breakdown"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:20.948Z - 20:07:27.300Z"
    quote: "\"event\": \"chaos_enabled\", \"request_id\": \"ddc4edac99ce\", \"failure_rate\": 0.6, \"error_status\": 503\" ... \"event\": \"chaos_failure\", \"request_id\": \"33c824dddf8e\", \"method\": \"GET\", \"path\": \"/products\" ... \"event\": \"chaos_disabled\", \"request_id\": \"3aeca5655f5f\""
  - id: E9
    type: metric
    source: "/metrics, probed at investigation start, request_id=konan-1787086064-24312"
    quote: "faultline_chaos_enabled 0"
  - id: E10
    type: log
    source: "lab/logs/app.log, startup/shutdown markers across the retained window"
    quote: "8 \"event\": \"startup\" lines at 19:52:52.328Z, 19:55:59.566Z, 20:01:10.255Z, 20:07:17.072Z, 20:08:19.219Z, 20:21:57.657Z, 20:35:37.082Z, 20:46:53.389Z; each preceding 'Shutting down' line is immediately preceded by an ordinary status-200 request line (e.g. GET /health -> 200 at 20:46:51.949Z followed by 'Shutting down' at 20:46:52.022Z), never by an exception or stack trace"
gaps:
  - "Log retention is a single un-rotated file covering only ~2026-08-18T19:52:52Z through ~20:51:34Z (under one hour); no earlier telemetry exists on the investigator's surface to independently confirm or rule out customer impact further back into 'this morning.'"
  - "The investigating session tripped the lab boundary's PreToolUse tripwire (repeated denials on non-probe Bash commands, including plain read-only commands like `scripts/lab.sh status` and a follow-up `grep` re-check) partway through judge verification and froze per AGENTS.md's hard rule ('a denied action is a signal to stop, never a puzzle to solve'). Planned final precision checks — an exact total request-line recount, per-event exception_type confirmation for all six original /products/3 500s, and a fresh /metrics reread — could not be completed. A fresh session is required to close these out; paging a human per the tripwire instruction."
  - "The adversarial judge sub-agent independently attempted to read the faultline source checkout (to confirm shop.py:64 against the quoted stack trace) and was correctly denied by the same boundary hook, consistent with this repo's blinding contract (the faultline checkout is out of investigator reach). Source-level confirmation of H2 therefore rests on the quoted log stack trace and catalog data only, not an independent source read."
  - "No investigator-visible mechanism exists to attribute the complaint's 'several customers' headcount or exact 'this morning' timing to specific real users; the complaint's framing could not be corroborated or refuted beyond what request-level telemetry shows in the retained window."
usage:
  model: claude-sonnet-5
  tokens: 3662081
  wall_clock_seconds: 289
---

# Support report of "Internal Server Error" on product pages — no active incident found; latent zero-stock defect confirmed

## Summary

**Verdict: no active incident.** Across the entire retained telemetry window (~19:52:52Z–20:51:34Z on 2026-08-18, a single un-rotated log file), no real (non-investigator) client ever received an HTTP 500 on any product page. The only HTTP 500s in the log are six occurrences of `GET /products/3 -> 500`, and all six carry an investigator-stamped `konan-*` request id (E5) — none are real user traffic (E7). Reproducing `GET /products/3` confirms a genuine, deterministic defect: product 3 ("Unobtainium Ingot") has `units_in_stock: 0` (E3), and `get_product()` divides by that value to compute `turnover_score`, raising `ZeroDivisionError` every time (E1, E2, E4). This is real and will 500 for anyone who requests that specific product, but the evidence shows it has only ever been triggered by this investigation's own probes so far — it rides along as a **latent finding**, not the active incident the complaint describes. Separately, three brief chaos-mode windows earlier in the session did cause real clients to see transient `503 Service Unavailable` on `/products`, `/products/2`, and `/orders` (E8); each self-resolved within seconds and chaos is currently off (E9) — a different status code, different routes, and already resolved, so it doesn't match the complaint either. Confidence is high on what was checked, moderated by the gaps below (short log retention, and the investigating session freezing on the lab's boundary tripwire before every last precision re-check could run).

## Timeline

- **19:52:52Z** — earliest timestamp in the only available log file; process startup (E10).
- **20:07:20Z–20:07:27Z, 20:08:23Z–20:08:29Z, 20:22:01Z–20:22:07Z** — three chaos-mode windows; real clients receive scattered 503s on `/products`, `/products/2`, `POST /orders`, each window self-disabling within seconds (E8).
- **20:11:52Z, 20:11:57Z, 20:24:25Z, 20:24:51Z, 20:27:00Z, 20:38:28Z** — the six pre-existing `/products/3` 500s, all under investigator `konan-*` request ids (E1, E2, E5).
- **20:35:37Z, 20:46:53Z** (and 6 other points) — clean process restarts, none adjacent to an error event (E10).
- **20:47:11Z** — this investigation starts (manual trigger via `/konan`).
- **20:47:44Z** — baseline `/metrics`: `faultline_chaos_enabled 0` (E9).
- **20:49:36Z** — software-defect lens reproduces the 500 live (`konan-1787086176-24465`) (E4), confirming determinism.
- **20:51:34Z** — last observed log activity (catalog probe, E3); investigating session's subsequent Bash call trips the boundary tripwire and freezes.

## Investigation

Baseline: `/health` ok, `/metrics` snapshot clean (chaos off, no exception counters post-restart), full log tail read directly. Triage fanned out three lenses in parallel (software-defect, interfaces, infra-process), each given only the lens file, surface contract, complaint, and baseline. Software-defect confirmed the ZeroDivisionError as deterministic and investigator-only. Interfaces traced the three chaos-503 bursts to explicit `chaos_enabled`/`chaos_disabled` flag flips, none overlapping the ZeroDivisionError events. Infra-process flagged a restart cadence (8 startups/~1h) but found every restart clean and uncorrelated with any error. Because triage evidence was already deterministic (full-window grep, live reproduction, catalog cross-check), deep-dive was skipped and the hypothesis list went straight to an adversarial judge. The judge independently re-ran the key greps, validated H2 and H3, invalidated H1 — then its own attempt to read the faultline source checkout was correctly blocked by the lab boundary hook. A follow-up precision re-check in this investigating session then tripped the same boundary tripwire (two denials) and froze per the repo's hard rule; the journal was written from evidence already gathered.

## Hypotheses

### H1 — Active incident affecting real users (invalidated)
Testing the complaint's literal claim. Every `/products/3` 500 in the log carries a `konan-*` (investigator) request id (E5); the breakdown of non-investigator traffic shows no `/products/3` entry at all (E7), and sampled real traffic only ever touched products 1, 2, 4, 5 (E6). No evidence of real customer impact was found in the retained window.

### H2 — ZeroDivisionError on /products/3 from zero stock (validated)
`get_product()` divides `units_ordered` by `product["units_in_stock"]`; product 3 has zero stock (E3). The stack trace (E1) and the matching `GET /products/3 -> 500` access line (E2) confirm the mechanism, and a fresh probe during this investigation reproduced it on demand (E4) — deterministic, single-input, matching the software-defect lens's signature exactly.

### H3 — Transient chaos-induced 503s, self-resolved (validated)
Three explicit `chaos_enabled → failures → chaos_disabled` windows (E8) produced real-client 503s on `/products`, `/products/2`, `/orders`; chaos is confirmed off now (E9). Different status code and routes than the complaint describes, and already resolved by the time of investigation — doesn't explain "Internal Server Error... this morning."

## Safe next steps

- Re-run this investigation from a fresh session (the current one is frozen by the boundary tripwire) to complete the deferred precision checks: exact total request-line count, per-event `exception_type` confirmation for all six original `/products/3` 500s, and a fresh `/metrics` reread.
- If support can supply a request id, timestamp, or client IP from an affected customer's report, grep `lab/logs/app.log` for it directly — that would either surface a real-user hit on `/products/3` (overturning H1) or confirm the report doesn't correlate with this service's telemetry at all.
- Watch `/products/3` and `http_exceptions_total{type="ZeroDivisionError"}` going forward: if a non-`konan-*` request id ever appears against that route, H1 should be revisited immediately — the defect is real and only needs a real customer to open product 3's page to become an active incident.
- Page a human per the tripwire instruction to review why this session's read-only Bash calls (including plain ones like `scripts/lab.sh status`) required approval and were denied — worth confirming whether that's expected friction or a settings gap.

## Gaps

- Log retention is a single un-rotated file covering under one hour (~19:52:52Z–20:51:34Z); nothing earlier is visible on the investigator's surface, so "this morning" beyond that window can't be independently checked.
- The session froze on the lab's boundary tripwire before the last planned precision re-checks (exact line counts, full exception_type confirmation, a fresh `/metrics` reread) could run; a fresh session is needed to close these out.
- The judge's attempt to cross-check `shop.py:64` directly against the faultline source checkout was correctly blocked by the blinding contract — H2's mechanism rests on the quoted stack trace and catalog data, not an independent source read.
- No mechanism on the investigator's surface can confirm or refute the complaint's specific "several customers" / "this morning" framing beyond what request-level telemetry shows.
