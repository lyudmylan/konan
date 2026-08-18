---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-handover-check
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-18T20:09:03Z
  concluded: 2026-08-18T20:19:37Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "Two brief eval-side chaos-injection episodes (failure_rate=0.6, error_status=503) toggled on and off between 20:07:20Z and 20:08:29Z, producing intermittent 503s on GET /products, GET /products/2, and POST /orders; both were bracketed by explicit chaos_enabled/chaos_disabled log markers and self-resolved, with no 5xx traffic logged since."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "GET /products/3 deterministically raises an uncaught ZeroDivisionError (HTTP 500) at faultline/shop.py:64 because product 3 (Unobtainium Ingot) has units_in_stock=0, making the turnover_score division (units_ordered / units_in_stock) divide by zero; reproduced twice; only investigator probes have ever hit this route in the visible log history, so it has not yet caused organic user impact."
    incident_class: software-defect
    state: validated
    evidence_for: [E13, E14, E15, E16, E17, E18, E19]
    evidence_against: []
  - id: H3
    statement: "The process restarted 5 times within roughly 19 minutes (19:52:52Z-20:08:19Z) with no crash markers; the two most recent restarts were each followed ~3.9s later by a chaos-enable event, a close enough match to suggest a shared scripted trigger, but the three earlier restarts show no such correlation and their cause cannot be determined from the available surface."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E12, E1, E4]
    evidence_against: []
  - id: H4
    statement: "GET /products (list) and GET /products/{id} (detail) return different field sets for the same resource (product 4 lacks units_ordered/turnover_score in the list view) — considered as a possible contract violation, but the service's own OpenAPI schema declares both endpoints with additionalProperties:true and no fixed required field list, so the difference is permitted by the documented contract, not a violation of it."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E17, E20]
    evidence_against: [E21]
latent_findings:
  - statement: "GET /products/3 will 500 for any real caller, not just the investigator, because product 3 has units_in_stock=0 and the turnover_score calculation divides by it uncaught; confirmed reproducible on demand, but request ids show only investigator probes (prefixed konan-) have ever hit this route — no organic/user-triggered occurrence found in the visible log history."
    evidence: [E13, E14, E15, E16, E17, E18, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:20.948Z"
    quote: "{\"ts\": \"2026-08-18T20:07:20.948Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:22.009Z"
    quote: "{\"ts\": \"2026-08-18T20:07:22.009Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} / \"GET /products -> 503\" status 503 duration_ms 0.294"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:07:27.300Z"
    quote: "{\"ts\": \"2026-08-18T20:07:27.300Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"event\": \"chaos_disabled\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:23.129Z"
    quote: "{\"ts\": \"2026-08-18T20:08:23.129Z\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:25.247Z"
    quote: "{\"ts\": \"2026-08-18T20:08:25.247Z\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/2\"} / \"GET /products/2 -> 503\""
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:27.366Z"
    quote: "{\"ts\": \"2026-08-18T20:08:27.366Z\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"} / \"POST /orders -> 503\""
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:28.423Z"
    quote: "{\"ts\": \"2026-08-18T20:08:28.423Z\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} / \"GET /products -> 503\""
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:29.480Z"
    quote: "{\"ts\": \"2026-08-18T20:08:29.480Z\", \"event\": \"chaos_disabled\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:08:49.542Z"
    quote: "{\"ts\": \"2026-08-18T20:08:49.542Z\", \"message\": \"GET /products -> 200\", \"status\": 200} (first request after the second chaos_disable; every request from here through the end of the read tail is 200/201)"
  - id: E10
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1787084350-22818, 2026-08-18T20:19:10Z"
    quote: "faultline_chaos_enabled 0 ; http_exceptions_total{type=\"ZeroDivisionError\"} 2 ; no other status>=400 counters beyond the two chaos-episode 503s already accounted for in H1 and the two ZeroDivisionError 500s accounted for in H2"
  - id: E11
    type: probe
    source: "scripts/probe.sh /health @ request_id konan-1787084345-22810"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":646.7234832090326}"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T19:52:52.328Z - 2026-08-18T20:08:19.219Z"
    quote: "\"Started server process [21190]\" 19:52:52.328Z ; \"Shutting down\" 19:55:58.241Z -> \"Started server process [21479]\" 19:55:59.565Z ; \"Shutting down\" 20:01:08.970Z -> \"Started server process [21849]\" 20:01:10.255Z ; \"Shutting down\" 20:07:15.740Z -> \"Started server process [22156]\" 20:07:17.072Z ; \"Shutting down\" 20:08:17.974Z -> \"Started server process [22301]\" 20:08:19.219Z ; each start immediately followed by faultline.app \"faultline 0.1.0 started\" and no unhandled_exception or crash marker adjacent to any of the five"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.043Z"
    quote: "{\"ts\": \"2026-08-18T20:11:52.043Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787083912-22619\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:52.050Z"
    quote: "{\"ts\": \"2026-08-18T20:11:52.050Z\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787083912-22619\", \"status\": 500, \"duration_ms\": 7.675}"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:57.810Z"
    quote: "{\"ts\": \"2026-08-18T20:11:57.810Z\", \"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787083917-22635\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:57.813Z"
    quote: "{\"ts\": \"2026-08-18T20:11:57.813Z\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787083917-22635\", \"status\": 500, \"duration_ms\": 2.925} (these two lines, E14 and E16, are the only \"/products/3\" access lines in the entire log file; grep -c unhandled_exception lab/logs/app.log = 2, matching E13 and E15 exactly)"
  - id: E17
    type: probe
    source: "scripts/probe.sh /products @ request_id konan-1787084220-22737"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0} ; {\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75}"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:11:38.271Z"
    quote: "{\"ts\": \"2026-08-18T20:11:38.271Z\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"konan-1787083898-22568\", \"status\": 200} (control: product with units_in_stock>0 succeeds under the same code path)"
  - id: E19
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1787084350-22818"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 2"
  - id: E20
    type: probe
    source: "scripts/probe.sh /products/4 @ request_id konan-1787084339-22789"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E21
    type: probe
    source: "scripts/probe.sh /openapi.json @ request_id konan-1787084156-22684"
    quote: "\"/products\":{\"get\":{...\"schema\":{\"items\":{\"additionalProperties\":true,\"type\":\"object\"},\"type\":\"array\"}}} ; \"/products/{product_id}\":{\"get\":{...\"schema\":{\"type\":\"object\",\"additionalProperties\":true}}} (no required field list on either response schema)"
gaps:
  - "Root cause of the three earliest process restarts (pid 21190 -> 21479 -> 21849, spanning 2026-08-18T19:52:52.328Z-20:07:17.072Z) could not be determined: no crash marker or correlated event appears in logs/metrics, and supervisor/orchestration logs that might show what triggers restarts are outside the investigator's surface contract (docs/lab.md exposes only probe.sh, app.log, and /metrics)."
  - "No caller identity or source field distinguishes who triggered the chaos_enabled/chaos_disabled events in H1; attribution to eval-side scripts/scenario.sh rests on the documented architecture (docs/lab.md: /chaos sits outside the probe.sh allowlist, mechanically enforced) rather than a directly logged actor id."
  - "No rotated log backups (app.log.1-.3) existed to check; the earliest visible line is 2026-08-18T19:52:52.328Z, so whether the restart cadence or any other anomaly predates that is unknown."
usage:
  model: claude-sonnet-5
  tokens: 5641951
  wall_clock_seconds: 634
---

# Routine handover check — shop service: chaos noise self-resolved, one latent defect found

## Summary

**No active incident right now.** The "noise earlier" the complaint refers to matches two
short eval-side chaos-injection episodes (20:07:20Z-20:07:27Z and 20:08:23Z-20:08:29Z on
2026-08-18) that produced intermittent 503s on `/products`, `/products/2`, and `POST
/orders` (H1, validated). Both were explicitly bracketed by `chaos_enabled`/`chaos_disabled`
log markers and self-resolved; `faultline_chaos_enabled` reads `0` right now and every
request since 20:08:29Z has been 2xx/201 (E9-E11).

While probing for other explanations, a real, reproducible code defect turned up: `GET
/products/3` always 500s with an uncaught `ZeroDivisionError`, because product 3 has
`units_in_stock: 0` and the turnover-score calculation divides by it (H2, validated,
`faultline/shop.py:64`). This is real but **latent** — every hit to `/products/3` in the
visible log history came from an investigator probe (`konan-`-prefixed request id); no
organic/user traffic has exercised this route yet, so it rides along as a latent finding
rather than changing the incident verdict.

Two secondary threads were opened and closed: a restart cadence (5 restarts in ~19
minutes) is real but its root cause is only partly explained — the two most recent
restarts line up with the chaos episodes' timing, the three before that don't correlate
with anything visible (H3, inconclusive). A list/detail field-shape difference on
product 4 looked like a contract issue at first glance but the service's own OpenAPI
schema permits it (H4, invalidated).

Confidence: high for H1 and H2 (both reproduced/confirmed directly); low for H3's earlier
restarts (genuine surface gap, not resolvable from here).

## Timeline (2026-08-18, all UTC)

- `19:52:52.328Z` - `20:07:17.072Z`: three process restarts (pid 21190->21479->21849->22156),
  each with a clean shutdown/startup pair, no crash markers (E12).
- `20:07:20.948Z`: chaos enabled, failure_rate 0.6, error_status 503 (E1) - ~3.9s after the
  restart into pid 22156.
- `20:07:22.009Z`: `GET /products` -> 503, chaos-injected (E2).
- `20:07:27.300Z`: chaos disabled (E3).
- `20:08:19.219Z`: restart into pid 22301 (E12).
- `20:08:23.129Z`: chaos enabled again (E4) - ~3.9s after this restart too.
- `20:08:25.247Z`-`20:08:28.423Z`: three more chaos-injected 503s, on `/products/2`,
  `POST /orders`, `/products` (E5-E7).
- `20:08:29.480Z`: chaos disabled (E8); all requests after this point are 2xx/201 (E9).
- `20:11:38.271Z`-`20:11:57.813Z`: investigator control probes and reproduction of the
  `/products/3` defect - two deterministic `ZeroDivisionError` 500s (E13-E16, E18).
- `20:19:10Z`: final health/metrics check confirms chaos off, no new restarts, exactly
  2 `ZeroDivisionError`s total (both investigator-caused) (E10, E11, E19).

## Investigation

- **Baseline**: `/health` and `/metrics` looked clean at the current moment, but the log
  tail immediately showed two bracketed chaos episodes and a restart cadence in the
  last ~19 minutes - not something to wave off as "just noise" without checking further.
- **Triage** (three lenses run in parallel, blind to each other): infra-process flagged
  the restart cadence and one short-lived process instance; interfaces flagged the two
  chaos episodes as self-resolved and confirmed current state is clean, plus noted the
  product-4 field-shape difference; software-defect found and reproduced the
  `/products/3` `ZeroDivisionError`, and confirmed via a full-log scan that only
  investigator request ids had ever hit that route.
- **Deep-dive**: skipped. H1 and H2's triage evidence was already deterministic and
  complete (reproduced, bracketed by explicit markers, or backed by a stack trace) -
  no further probing would add anything a fresh test could disconfirm.
- **Judge** (adversarial, evidence-only): validated H1 with a caveat (no evidence
  directly names the chaos-toggle actor - the "eval-side, not organic" framing is
  architectural inference, not a logged fact) and validated H2 outright. Judged H3
  inconclusive - and flagged that H1's own evidence (E1, E4) undercuts H3's "no
  explanation at all" framing for the two most recent restarts, while leaving the three
  earlier ones genuinely unexplained. Judged H4 inconclusive, since "contract
  inconsistency" presupposes a contract that wasn't cited.
- **Follow-up** (cheap, targeted): checked `/openapi.json` to settle H4 - the schema
  permits the field difference, so H4 is invalidated as a violation claim.

## Hypotheses

### H1 - chaos-injection episodes (validated)
Two enable/inject/disable cycles (E1-E3, E4-E8) fully explain the "noise earlier": a
stable failure rate (0.6) interleaved with successes on the same routes, the classic
injected-degradation signature, cleanly bracketed by config-change markers, with clean
traffic before and after (E9-E11). The one soft spot: no evidence ties the toggle to a
specific actor - the "eval-side" attribution rests on the surface contract's architecture
(only `scripts/scenario.sh` can reach `/chaos`; `probe.sh` mechanically refuses it) rather
than a logged caller id. That gap is recorded, not glossed over.

### H2 - `/products/3` ZeroDivisionError (validated, latent)
`shop.py:64` divides `units_ordered` by `units_in_stock` without a zero check; product 3
has `units_in_stock: 0` (E17), so every hit 500s (E13-E16), reproduced twice. Control
probes on non-zero-stock products succeed on the same code path (E18). The metrics
counter (E19) shows exactly 2 `ZeroDivisionError`s total, matching the two investigator
probes exactly - meaning no user has hit this route (yet). That is why it is recorded as
a latent finding rather than folded into the incident verdict.

### H3 - restart cadence (inconclusive)
Five restarts in ~19 minutes (E12) is a real pattern. The two most recent line up with
chaos-enable events ~3.9s later each (E1, E4) - close enough to suggest a shared scripted
sequence (restart -> enable chaos -> inject -> disable), which would make those two
restarts explained, not anomalous. The three before that have no correlated event in
logs or metrics. Genuinely inconclusive, and the missing piece - supervisor/orchestration
logs - is outside this investigation's surface contract (see Gaps).

### H4 - product-4 list/detail field difference (invalidated)
The raw observation is real (E17, E20: list response lacks `units_ordered`/
`turnover_score` that the detail response has), but the service's own OpenAPI schema
(E21) declares both endpoints with `additionalProperties: true` and no fixed required
field set - so the difference is permitted by the documented contract. Not a violation.

## Safe next steps

- Re-check `/health`, `/metrics`, and the `/products/3` route periodically during the
  shift - if `http_exceptions_total{type="ZeroDivisionError"}` climbs above 2 without a
  matching investigator probe, that is the signal H2 has gone from latent to active.
- If restart cadence continues past this shift, a future investigation with access to
  process-supervisor or deploy logs (outside this lab's current surface) could settle
  whether all five restarts share one trigger.
- No configuration change, rollback, or fix is proposed here - remediation is out of
  scope for this journal.

## Gaps

- Root cause of the three earliest restarts (pid 21190->21479->21849) is unknown -
  no crash marker or correlated event in logs/metrics, and the surface contract doesn't
  expose supervisor/orchestration logs that might explain it.
- No caller identity confirms who toggled chaos on/off; the "eval-side, not organic"
  read is architectural inference (`/chaos` is outside `probe.sh`'s allowlist), not a
  directly logged fact.
- No rotated log backups existed; the log's earliest line is `2026-08-18T19:52:52.328Z`,
  so anything before that is unknown.
