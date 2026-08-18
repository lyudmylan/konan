---
konan_journal: 1
investigation:
  id: 2026-08-18-product-page-500-complaint
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-18T20:35:51Z
  concluded: 2026-08-18T20:44:02Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "GET /products/3 unconditionally throws an uncaught ZeroDivisionError (HTTP 500) because product 3 ('Unobtainium Ingot') has units_in_stock=0 and faultline/src/faultline/shop.py:64 computes turnover_score as units_ordered / product['units_in_stock'] without a zero guard; deterministic and reproducible on every call, independent of chaos mode and process restarts, and the only 500-producing code path found anywhere in the retained telemetry that matches the complaint's 'Internal Server Error when opening a product page' wording. However, every one of the 6 requests that ever exercised this route in the retained log (2026-08-18T19:52:52Z to now — the complete available history) carries an investigator-stamped request_id; no non-investigator request to /products/3 was found."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E1, E2, E3, E4]
    evidence_against: []
  - id: H2
    statement: "The process restarted 7 times within a 43-minute span (19:52:52Z-20:35:37Z) via clean shutdown/startup sequences with no crash, OOM, or exception marker between any pair; /health returned 200 throughout the retained log. The restart cadence brackets the incident window, but no log line ties any 5xx response to a restart, so restarts are not shown to independently cause the reported errors."
    incident_class: infra-process
    state: validated
    evidence_for: [E5, E6, E7, E8]
    evidence_against: []
  - id: H3
    statement: "Three brief eval-side chaos-injection episodes (failure_rate=0.6, error_status=503) toggled on/off at 20:07:20Z-20:07:27Z, 20:08:23Z-20:08:29Z, and 20:22:01Z-20:22:07Z produced intermittent 503s on GET /products and GET /products/2, interleaved with 200s on the same routes. All three episodes are bounded by explicit chaos_enabled/chaos_disabled markers, chaos is confirmed disabled now, and the injected status code (503) does not match the complaint's 'Internal Server Error' framing as precisely as H1's 500."
    incident_class: interfaces
    state: validated
    evidence_for: [E9, E10, E11, E12, E13, E14, E15, E16, E17, E18]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 will return HTTP 500 for any caller — investigator or customer — because product 3 has units_in_stock=0 and the turnover_score calculation divides by it uncaught; reproduced on demand as recently as 2026-08-18T20:38:28Z, well after the process restart at 20:35:37Z, confirming it is a stateless, permanent code defect rather than chaos- or restart-dependent. This same defect was already flagged as latent in an earlier same-day investigation (journals/2026-08-18-shop-handover-check.md, concluded 20:19:37Z); this complaint arrived roughly 16 minutes after that finding was filed, but the retained telemetry still shows no non-investigator request ever reaching this route."
    evidence: [E1, E2, E3, E4]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /products @ request_id konan-1787085614-23896"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":40},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.043Z"
    quote: "{\"ts\": \"2026-08-18T20:11:52.043Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787083912-22619\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.050Z"
    quote: "{\"ts\": \"2026-08-18T20:11:52.050Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787083912-22619\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 7.675, \"client\": \"127.0.0.1:50929\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:38:28.493Z"
    quote: "{\"ts\": \"2026-08-18T20:38:28.493Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787085508-23761\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 9.091, \"client\": \"127.0.0.1:51185\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:52:52.328Z"
    quote: "{\"ts\": \"2026-08-18T19:52:52.328Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:35:36.781Z"
    quote: "{\"ts\": \"2026-08-18T20:35:36.781Z\", \"level\": \"INFO\", \"logger\": \"uvicorn.error\", \"message\": \"Shutting down\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:35:37.082Z"
    quote: "{\"ts\": \"2026-08-18T20:35:37.082Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E8
    type: probe
    source: "scripts/probe.sh /health @ request_id konan-1787085386-23639"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":49.05631154216826}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:20.948Z"
    quote: "{\"ts\": \"2026-08-18T20:07:20.948Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"ddc4edac99ce\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:22.009Z"
    quote: "{\"ts\": \"2026-08-18T20:07:22.009Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 503\", \"request_id\": \"33c824dddf8e\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.294, \"client\": \"127.0.0.1:50818\"}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:27.300Z"
    quote: "{\"ts\": \"2026-08-18T20:07:27.300Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"3aeca5655f5f\", \"event\": \"chaos_disabled\"}"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:23.129Z"
    quote: "{\"ts\": \"2026-08-18T20:08:23.129Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"656197e653c3\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:25.247Z"
    quote: "{\"ts\": \"2026-08-18T20:08:25.247Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/2 -> 503\", \"request_id\": \"2d270de331b6\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 503, \"duration_ms\": 0.326, \"client\": \"127.0.0.1:50864\"}"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:29.480Z"
    quote: "{\"ts\": \"2026-08-18T20:08:29.480Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"c6f66e10e77d\", \"event\": \"chaos_disabled\"}"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:01.558Z"
    quote: "{\"ts\": \"2026-08-18T20:22:01.558Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"33536b678954\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:02.616Z"
    quote: "{\"ts\": \"2026-08-18T20:22:02.616Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 503\", \"request_id\": \"6aa97b0a7688\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.313, \"client\": \"127.0.0.1:51000\"}"
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:07.911Z"
    quote: "{\"ts\": \"2026-08-18T20:22:07.911Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"0d3ed61424da\", \"event\": \"chaos_disabled\"}"
  - id: E18
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1787085388-23645"
    quote: "faultline_chaos_enabled 0"
gaps:
  - "No non-investigator (non-'konan-'-prefixed) request to /products/3 was found anywhere in the retained log (2026-08-18T19:52:52Z-20:44:02Z, the complete available history — no rotation backups exist on disk), so the defect's link to the reported customer impact could not be confirmed or ruled out from telemetry alone."
  - "The support complaint gives no specific customer identifiers, product IDs, or timestamps beyond 'this morning', so no targeted correlation against the retained log was possible."
  - "Log retention covers only the current process lineage's lifetime, starting at its first observed startup (19:52:52Z); any 'this morning' activity that predates that window is outside the investigator's reach."
  - "The cause of the 7 process restarts (external trigger — reload, redeploy, or the eval/session harness cycling the lab) could not be determined from the retained surface; no config/deploy marker beyond the startup/shutdown log lines themselves was available."
usage:
  model: claude-sonnet-5
  tokens: 3911480
  wall_clock_seconds: 491
---

# Support complaint of "Internal Server Error" on product pages — matches a known defect, customer link unconfirmed

## Summary

**Verdict: inconclusive.** The only 500-producing code path found anywhere in the retained
telemetry that could plausibly match "Internal Server Error when opening a product page" is a
deterministic `ZeroDivisionError` on `GET /products/3`: product 3 ("Unobtainium Ingot") has
`units_in_stock: 0`, and `faultline/src/faultline/shop.py:64` divides `units_ordered` by that
field with no zero guard. It reproduces on demand — most recently seconds before this journal
was written, well after a process restart and with chaos mode confirmed off — so it is a
permanent, stateless defect, not an artifact of chaos injection or the restart cadence also
observed in this window. However, every single request that has ever hit `/products/3` in the
retained log carries an investigator-stamped `request_id` (prefix `konan-`); the full log
(the complete available history, no rotation backups exist) contains zero non-investigator
requests to that route, of any status. So while this defect would produce exactly the reported
symptom for any real customer who opened that product's page, nothing in the available
telemetry confirms a customer actually did. Two other candidate mechanisms — a restart loop and
three self-resolved chaos-injection episodes — were checked and do not independently explain
customer-facing 500s on product pages (restarts are clean/instant with no adjacent errors;
chaos produces 503s, not 500s, and has been off since 20:22:07Z).

## Timeline

- **19:52:52Z** — earliest process startup in the retained log (E5); the process restarted 6
  more times through 20:35:37Z (E7), each cleanly (E6), none adjacent to a crash marker.
- **20:07:20Z-20:07:27Z, 20:08:23Z-20:08:29Z, 20:22:01Z-20:22:07Z** — three chaos-injection
  episodes (E9/E11, E12/E14, E15/E17), each producing interleaved 503s (E10, E13, E16) on
  `/products`/`/products/2`; all three self-resolved via explicit `chaos_disabled` markers.
- **20:11:52Z** — first observed `GET /products/3 -> 500` (E2, E3), investigator-stamped.
- **20:19:37Z** — a prior same-day investigation (`journals/2026-08-18-shop-handover-check.md`)
  concluded, already flagging this same `/products/3` defect as a latent finding.
- **20:35:37Z** — process restart (E7); metrics/uptime reset here.
- **20:35:49Z** — support complaint received (verbatim): *"Support says several customers see
  'Internal Server Error' when opening a product page this morning. Can you check what is
  going on?"* (`fingerprint: human-1787085349`).
- **20:35:51Z** — this investigation started (trigger latency: 2s).
- **20:38:28Z** — `/products/3` reproduced live, post-restart, chaos confirmed off (E4/E18) —
  confirms the defect is unconditional, not chaos- or restart-dependent.
- **20:44:02Z** — investigation concluded.

## Investigation

**Baseline** (20:36Z): `/health` ok, fresh process (uptime ~49s, restarted at 20:35:37Z),
`/metrics` clean post-restart. Read the full retained log (`lab/logs/app.log`, the only log
file present — no `.1`-`.3` backups) end to end.

**Triage** — three lenses in parallel, each given only the lens file, `docs/lab.md`, the
complaint verbatim, and the baseline summary:
- *software-defect*: found and live-reproduced the `/products/3` `ZeroDivisionError`;
  confirmed single-input concentration (control probe on `/products/1` succeeds) and flagged
  that all triggering request_ids are investigator-stamped.
- *interfaces*: found the chaos-flag windows, confirmed they are probabilistic/config-bounded
  and self-resolved, ruled out version/config drift across all 7 restarts (identical
  `version: "0.1.0"` each time), and handed the `/products/3` finding to software-defect as
  out of its domain.
- *infra-process*: found the 7-restart cadence, confirmed each is a graceful shutdown/startup
  pair with no crash/OOM markers, and flagged that restart-driven metric resets limit
  visibility into longer-term saturation trends (noted as a gap, not a confirmed problem).

Given the software-defect evidence was already deterministic and complete (live-reproduced,
full stack trace, single-input scope confirmed), no further deep-dive round was needed to
re-prove the mechanism — the open question was strictly whether real traffic had exercised it,
which is a question the retained log can only answer by absence (already checked exhaustively
in triage). Hypotheses went straight to the judge.

**Judge** (evidence-only, no narrative): validated H2 and H3 as stated (both hypotheses were
scoped narrowly enough that their cited evidence fully supports them); ruled H1 inconclusive —
the defect mechanism (E1-E4) is solid, but the claim that it explains *this* complaint is not
supported by direct evidence of customer traffic reaching the route, which the hypothesis's own
stated gap already acknowledges.

No second round was run: the judge's suggested settling evidence for H1 (a non-investigator
request_id hitting `/products/3`) does not exist anywhere in the retained log, which has
already been read in full — there is no more telemetry to gather from this surface.

## Hypotheses

### H1 — `/products/3` ZeroDivisionError (software-defect) — inconclusive

The mechanism is fully evidenced: product 3 has `units_in_stock: 0` (E1), the exact stack
trace names `shop.py:64`'s unguarded division (E2), and the failure is reproducible at will —
first seen at 20:11:52Z (E3) and reproduced again at 20:38:28Z (E4), after a restart and with
chaos off, ruling out both as contributing factors. This is the only 500 in the entire retained
log on a product-detail route, which is what makes it the leading candidate for the complaint.
Against full attribution: all 6 occurrences of this route being hit, ever, in the retained log
carry `konan-`-prefixed request_ids — the investigator's own stamp. No customer- or
scenario-simulated request to `/products/3` appears anywhere. The defect is real and would
produce the exact reported symptom for any real visitor to that product page, but the retained
telemetry cannot confirm that one did.

### H2 — Restart loop (infra-process) — validated

7 clean restarts in 43 minutes (E5, E6, E7), none preceded by a crash or exception marker,
`/health` clean throughout (E8). The claim was scoped to what the evidence actually shows —
restarts happened and were clean — not to any causal link to the complaint, since no log line
ties a 5xx to a restart transition.

### H3 — Chaos-injection episodes (interfaces) — validated

Three explicit, self-bounded chaos windows (E9/E11, E12/E14, E15/E17) produced interleaved
503s (E10, E13, E16) on `/products` and `/products/2`. All resolved before 20:22:08Z and chaos
is confirmed off now (E18). Kept as a considered-and-ruled-out alternative: the status code
(503, "service unavailable") is a weaker match for "Internal Server Error" than H1's 500, and
the episodes ended over 20 minutes before the complaint arrived.

## Safe next steps

- Ask support for the exact product ID(s), approximate time(s), and any request/correlation ID
  customers' browsers reported, to check against future non-investigator traffic on
  `/products/3`.
- If the storefront or an upstream service logs outbound request IDs or session IDs when users
  view a product, cross-reference those against `lab/logs/app.log` for hits on `/products/3`
  during the reported window.
- Keep log retention running (no rotation backups currently exist) so a follow-up complaint has
  a longer window to correlate against.

## Gaps

- No non-investigator request to `/products/3` was found anywhere in the retained log — the
  complete available history — so customer impact could not be confirmed or ruled out.
- The complaint carries no specific customer, product ID, or timestamp beyond "this morning",
  limiting correlation.
- Retained log history starts at the current process lineage's first observed startup
  (19:52:52Z); nothing earlier is available.
- The cause of the 7 process restarts could not be determined from the retained surface.
