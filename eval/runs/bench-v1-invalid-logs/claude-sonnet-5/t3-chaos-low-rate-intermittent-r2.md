---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-occasional-errors
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-18T21:28:09Z
  concluded: 2026-08-18T21:36:10Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos-mode fault injection (failure_rate=0.08, error_status=503), armed via POST /chaos/enable at 21:27:28Z and re-armed with the identical config after a clean process restart at 21:27:59Z, is still active and produces probabilistic 503 responses across GET /products, GET /products/{id}, and POST /orders — an 8% per-request failure rate resolves on retry roughly 92% of the time, matching the reported occasional-error/works-on-retry/most-notice-nothing pattern."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos-mode fault injection (failure_rate=0.08, error_status=503) explains the complaint: probabilistic 503s interleaved with successes across multiple shop routes, in the last few minutes, still armed."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The complaint is explained by GET /products/3's uncaught ZeroDivisionError (HTTP 500)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E11, E12]
latent_findings:
  - statement: "GET /products/3 deterministically raises an uncaught ZeroDivisionError (500) on every request — faultline/shop.py:64 divides units_ordered by units_in_stock without a zero-check, and product 3 has units_in_stock=0. Reproduced live this session. Real and reproducible, but not this complaint's cause: every occurrence across the full log (10 total, spanning multiple investigation sessions) carries an investigator-prefixed request id — no organic/user traffic has ever hit this route — and the failure is 100% deterministic per-input, not intermittent, so it does not fit 'works on retry.'"
    evidence: [E9, E10, E11, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:28.547Z"
    quote: "{\"ts\": \"2026-08-18T21:27:28.547Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"14a360148cad\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:29.631Z"
    quote: "{\"ts\": \"2026-08-18T21:27:29.631Z\", \"message\": \"GET /products/1 -> 503\", \"request_id\": \"4d03f6f619cd\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 503, \"duration_ms\": 0.202} (request_id not investigator-prefixed)"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:30.070Z"
    quote: "{\"ts\": \"2026-08-18T21:27:30.070Z\", \"level\": \"WARNING\", \"message\": \"chaos-injected failure\", \"request_id\": \"995c872515b2\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} / \"GET /products/1 -> 503\" status 503 duration_ms 0.152 (request_id not investigator-prefixed)"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:53.279Z - 2026-08-18T21:27:59.598Z"
    quote: "\"Shutting down\" 21:27:53.279Z -> \"Started server process [26746]\" 21:27:54.636Z, immediately followed by faultline.app \"faultline 0.1.0 started\" (event startup) -> 5s later, {\"ts\": \"2026-08-18T21:27:59.598Z\", \"message\": \"chaos mode enabled\", \"request_id\": \"02e576f03a28\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0} (identical config re-armed after a clean restart, no crash marker)"
  - id: E5
    type: log
    source: "lab/logs/app.log — full-file grep of event chaos_disabled"
    quote: "Only 3 chaos_disabled events exist in the entire log: 20:07:27.300Z, 20:08:29.480Z, 20:22:07.911Z. None appear after 20:22:07.911Z, despite 5 further chaos_enabled reconfigurations through 21:27:59.598Z — chaos has been continuously armed since 20:22:01Z."
  - id: E6
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1787088705-27135, 2026-08-18T21:31:45.333Z"
    quote: "faultline_chaos_enabled 1 ; process_uptime_seconds 230.76678979210556"
  - id: E7
    type: log
    source: "lab/logs/app.log — full-file grep of \"status\": 503"
    quote: "Exactly 9 lines match in the whole file, spanning GET /products, GET /products/1, GET /products/2, POST /orders (e.g. 20:07:22.009Z GET /products -> 503; 20:08:27.366Z POST /orders -> 503; 21:27:29.631Z and 21:27:30.070Z GET /products/1 -> 503). Every one falls inside a chaos_enabled window (E1, E5 and their predecessors); none carry an investigator (konan-) request id."
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:31:45.333Z (last line)"
    quote: "{\"ts\": \"2026-08-18T21:31:45.333Z\", \"message\": \"GET /metrics -> 200\", \"request_id\": \"konan-1787088705-27135\", \"status\": 200} — no \"status\": 503 line appears anywhere after 21:27:30.070Z through this, the last entry in the log, ~4 minutes after the 21:27:59.598Z re-arm"
  - id: E9
    type: log
    source: "lab/logs/app.log — full-file grep of event unhandled_exception"
    quote: "10 occurrences total, ts 20:11:52.043Z through 21:30:18.354Z; every single request_id is konan-*-prefixed (e.g. konan-1787083912-22619, konan-1787087551-25827, konan-1787088618-27073) — no non-investigator request id ever appears against this exception."
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:30:18.354Z - 21:30:18.362Z"
    quote: "{\"ts\": \"2026-08-18T21:30:18.354Z\", \"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787088618-27073\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"} / {\"ts\": \"2026-08-18T21:30:18.362Z\", \"message\": \"GET /products/3 -> 500\", \"status\": 500, \"duration_ms\": 8.408}"
  - id: E11
    type: probe
    source: "scripts/probe.sh /products/2 and /products/1 @ request_ids konan-1787088621-27079, konan-1787088621-27085, 2026-08-18T21:30:21Z"
    quote: "GET /products/2 -> 200 ; GET /products/1 -> 200 (both immediately after the /products/3 -> 500 in E10 — only product 3 fails, deterministically, on the same code path)"
  - id: E12
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1787088705-27135"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 1 — matches exactly the single /products/3 probe made this process lifetime (since the 21:27:54Z restart), no other contribution"
gaps:
  - "No caller identity distinguishes who armed chaos mode (E1, E4's request ids 14a360148cad / 02e576f03a28 are not investigator-prefixed, consistent with eval-side scripts/scenario.sh per the surface contract's architecture, but that attribution is architectural inference, not a logged actor id)."
  - "Chaos has been continuously enabled since 20:22:01Z through several reconfigurations (failure_rate 0.6, then 0.0 with extra latency, then 0.08); why it was reconfigured to the current 0.08/503 setting specifically at 21:27:28Z, or on what schedule, is outside the visible surface (no operator/scheduler log)."
  - "Only 2 of the predicted ~8%-rate 503s have landed in the log so far (E2, E3, both before the restart); none has recurred since the 21:27:59Z re-arm through the last log line at 21:31:45Z (E8) — consistent with sampling noise at modest request volume, but the exact 0.08 rate is not independently confirmed by a larger sample."
usage:
  model: claude-sonnet-5
  tokens: 4921562
  wall_clock_seconds: 481
---

# Shop occasional errors — chaos-mode fault injection, still active

## Summary

**Root cause identified.** The occasional shop errors users are hitting right now are
chaos-mode fault injection: `POST /chaos/enable` armed an 8% failure rate returning 503
(`failure_rate: 0.08, error_status: 503`) at `21:27:28Z`, and the identical config was
re-armed at `21:27:59Z` after a clean process restart (H1, validated). An 8% per-request
failure rate means a retry succeeds about 92% of the time — exactly the "works on retry,
most people notice nothing" shape reported. Two non-investigator 503s on `GET
/products/1` at `21:27:29–30Z` (E2, E3) are the direct hit the reporting users likely
experienced. `faultline_chaos_enabled` still reads `1` as of this journal (E6) — **the
condition is still armed**, so more occasional errors should be expected until it is
turned off.

A separate, real defect was checked as an alternative explanation and ruled out: `GET
/products/3` always 500s with an uncaught `ZeroDivisionError` (division by
`units_in_stock=0` at `faultline/shop.py:64`). It reproduces every time, not
occasionally, and every one of its 10 occurrences in the visible log — across this and
prior investigation sessions — carries an investigator request id, meaning no user has
ever hit it (H2, invalidated as an explanation for this complaint; the defect itself
rides along as a latent finding).

Confidence: high for H1 (explicit config markers bracketing the failure pattern,
matching status codes and routes, reproduced-in-spirit by the pattern of every 503 in
the full log falling inside a chaos-enabled window). The one caveat: only 2 actual 503s
have landed since the current 0.08 config was armed, so the exact rate is not
independently confirmed by a large sample (see Gaps).

## Timeline (2026-08-18, all UTC)

- `20:22:07.911Z`: last explicit `chaos_disabled` marker in the entire log (E5).
- `20:22:01Z` onward: chaos remains continuously enabled through several
  reconfigurations (0.6 failure rate, then 0.0 with added latency, then the current
  0.08/503 config) — never disabled again (E5).
- `21:27:28.547Z`: chaos re-armed at `failure_rate: 0.08, error_status: 503` (E1).
- `21:27:29.631Z` and `21:27:30.070Z`: two `GET /products/1 -> 503`, one explicitly
  tagged `chaos_failure`, neither from an investigator (E2, E3).
- `21:27:53.279Z` - `21:27:54.636Z`: process restarts cleanly (`"Shutting down"` ->
  `"Started server process [26746]"` -> `"faultline 0.1.0 started"`), no crash marker
  adjacent (E4).
- `21:27:59.598Z`: chaos re-armed again, identical config (E4).
- `21:28:05Z`: complaint reported to konan.
- `21:28:09Z` - `21:31:45Z`: investigation baseline, triage, and probing; no new 503
  observed in this window (E7, E8); one investigator probe to `/products/3` reproduces
  the unrelated latent defect (E10-E12).
- `21:31:45.333Z`: last log line; `faultline_chaos_enabled` still `1` (E6, E8).

## Investigation

- **Baseline**: `/health` showed `uptime_seconds: 30.8` — the process had just
  restarted. `/metrics` immediately showed `faultline_chaos_enabled 1`. The log tail
  showed a `chaos_enabled` marker with `failure_rate: 0.08, error_status: 503` five
  seconds after that restart, plus a matching `chaos_failure` 503 from just before the
  restart — a config-driven explanation was visible before triage even started, so
  triage was run to check for competing or hidden causes rather than to find the first
  lead.
- **Triage** (three lenses, run in parallel, each blind to the others): infra-process
  found the restart cadence graceful (clean shutdown/startup pairs, no crash marker, no
  RSS or latency degradation) and ruled out a crash loop as the complaint's cause;
  interfaces independently identified the same two `chaos_enabled` markers as the
  config-change event and confirmed every 503 in the full log falls inside a
  chaos-enabled window; software-defect found and reproduced the `/products/3`
  `ZeroDivisionError`, confirmed it is 100% deterministic on that one input (control
  probes on `/products/1`, `/products/2` succeed), and flagged it as a mismatch for the
  complaint's "occasional/retry" shape.
- **Deep-dive**: skipped for both hypotheses — H1's triage evidence was already a
  cited config marker plus matching failure instances plus a full-log census with no
  counter-examples; H2's was already a reproduced, deterministic stack trace. Neither
  needed further probing to reach a verdict; the only thing added after triage was
  pulling exact verbatim log lines and a fresh `/metrics` read to build the evidence
  ledger precisely, plus a full-log grep confirming every `unhandled_exception` request
  id is investigator-prefixed (E9) — the single fact that most directly kills H2 as an
  explanation for organic user complaints.
- **Judge** (adversarial, evidence-only, fresh subagent seeing only hypotheses +
  verbatim evidence): validated H1, noting the qualitative fit (8% failure rate = ~92%
  retry success = "works on retry, most notice nothing"; failures spread across
  routes, not one input; only 9 failures total across 509 log lines = "most people
  notice nothing") and flagging two non-blocking gaps — the exact 0.08 rate isn't
  confirmed by a large sample, and the most recent 503 predates the judge's own probe
  by about two minutes rather than being caught live. Invalidated H2 as an explanation
  for the complaint: the deterministic per-input shape contradicts "works on retry,"
  the last organic-looking occurrence is ~17 minutes stale relative to "the last few
  minutes," and the reproduction itself was investigator-triggered, not organic
  traffic.

## Hypotheses

### H1 — chaos-mode fault injection (validated)
Explicit `chaos_enabled` markers (E1, E4) with `failure_rate: 0.08, error_status: 503`
bracket the complaint window, still active with no `chaos_disabled` since `20:22:07Z`
(E5, E6). Two 503s land immediately after the pre-restart marker, on a
non-investigator request id (E2, E3) — real (simulated) user impact, not an artifact
of probing. A full-log census shows every 503 ever logged (9 total) falls inside a
chaos-enabled window, spread across `/products`, `/products/{id}`, and `/orders` (E7)
— the textbook injected-degradation signature: probabilistic, multi-route, self-clears
on retry. The soft spot, called out by the judge: only 2 failures have actually landed
under the *current* 0.08 config so far (E2, E3), and none since the restart-triggered
re-arm through the end of the log (E8) — consistent with 8% sampling noise at modest
volume, not independently large-sample-confirmed.

### H2 — `/products/3` ZeroDivisionError explains the complaint (invalidated)
The defect is real and reproduces every time (E10), with a clean control showing
adjacent products succeed (E11) and the exception counter incrementing exactly 1:1 with
the investigator's own probe (E12) — but that determinism is precisely why it does not
fit the complaint: "works on retry" implies intermittent success, and this route never
succeeds. More decisively, every one of the 10 times this exception has ever fired in
the visible log carries an investigator-prefixed request id (E9) — no user traffic has
ever reached `/products/3`, so it cannot be the source of a user-reported "occasional
error." It rides along as a **latent finding** instead.

## Safe next steps

- Re-check `faultline_chaos_enabled` via `/metrics` periodically — it is still `1` as
  of this journal; if the eval/operator side intended a short chaos episode, it has
  outlasted the two previous ones considerably (continuously armed since `20:22:01Z`).
- If a larger sample is wanted to confirm the 8% rate empirically, read-only repeated
  probing of `/products` or `/health` over a longer window (still via `scripts/probe.sh`)
  would accumulate enough 503s to compare against the configured rate — not done here
  to stay within a lean probe budget.
- Track `http_exceptions_total{type="ZeroDivisionError"}` going forward; if it ever
  increments against a non-`konan-`-prefixed request id, that would mean the latent
  `/products/3` defect has started affecting real users and deserves its own
  investigation.

## Gaps

- No caller identity distinguishes who armed chaos mode — the request ids on the
  `chaos_enabled` events (E1, E4) are not investigator-prefixed, consistent with the
  documented architecture (`/chaos` sits outside `probe.sh`'s allowlist; only
  `scripts/scenario.sh` can reach it), but that attribution is architectural inference,
  not a logged actor id.
- Chaos has been continuously enabled since `20:22:01Z` through several
  reconfigurations (0.6 → 0.0-with-latency → 0.08); why the config changed to the
  current 0.08/503 setting specifically at `21:27:28Z`, or on what schedule, is outside
  the visible surface — no operator/scheduler log is exposed by the contract.
- Only 2 of the predicted ~8%-rate 503s have landed in the log under the current
  config (E2, E3), both before the complaint was even reported; none has recurred
  since the `21:27:59Z` re-arm through the last log line at `21:31:45Z` (E8). This is
  consistent with sampling noise at modest request volume but leaves the exact 0.08
  rate unconfirmed by a large sample.
