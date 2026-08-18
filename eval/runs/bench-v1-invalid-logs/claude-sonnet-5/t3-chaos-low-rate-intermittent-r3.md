---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-intermittent-503s
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-18T21:38:11Z
  concluded: 2026-08-18T21:52:56Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A chaos-injection config flag (failure_rate=0.08, error_status=503) was armed via POST /chaos/enable shortly before and again right at the complaint window, injecting a low, probabilistic rate of 503s into real shop traffic on GET /products and GET /products/1, matching the complaint's occasional/retry-succeeds/mostly-unnoticed shape."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "The chaos flag (failure_rate=0.08, error_status=503), armed at 21:27:28.547Z and re-armed at 21:38:04.051Z after an intervening process restart, injected intermittent 503s into real (non-investigator) traffic on GET /products and GET /products/1 — two failures in the 21:27:29-30Z burst and one in the 21:38:05Z burst — each interleaved with successes on the same routes, with at least one confirmed same-path retry succeeding 93ms later."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "GET /products/3 deterministically raises an uncaught ZeroDivisionError (HTTP 500) at faultline/shop.py:64 because product 3 has units_in_stock=0, making turnover_score = units_ordered / units_in_stock divide by zero; reproduced live during this investigation. http_exceptions_total{type=\"ZeroDivisionError\"} reads exactly 2, matching the two investigator probes that have ever hit this route — no organic/real-traffic occurrence found."
    incident_class: software-defect
    state: validated
    evidence_for: [E13, E14, E15, E16]
    evidence_against: []
  - id: H3
    statement: "Process restarts recur roughly every 5-30 minutes, and nearly every restart in the reviewed window is followed 5-7 seconds later by a POST /chaos/enable re-arm call — consistent with an external harness cycling scenarios (restart, then re-apply chaos config) rather than an independent stability problem, but no logged actor identity confirms this and the surface contract exposes no supervisor/orchestration log to settle it directly."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E9, E11, E12]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 will 500 for any caller, real or investigator, because product 3 has units_in_stock=0 and the turnover_score calculation divides by it uncaught. Confirmed reproducible on demand; every occurrence in the visible log carries a konan-prefixed (investigator) request id, and the exception counter (2) matches the investigator-probe count exactly — no user has hit this route yet."
    evidence: [E13, E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:37:59.122Z"
    quote: "{\"ts\": \"2026-08-18T21:37:59.122Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:38:01.995Z"
    quote: "{\"ts\": \"2026-08-18T21:38:01.995Z\", \"message\": \"POST /orders -> 201\", \"request_id\": \"70332de4d360\", \"status\": 201} (clean, non-konan traffic immediately after restart, before the chaos marker)"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:38:04.051Z"
    quote: "{\"ts\": \"2026-08-18T21:38:04.051Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"2be6e4408b9f\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:38:05.551Z"
    quote: "{\"ts\": \"2026-08-18T21:38:05.551Z\", \"message\": \"chaos-injected failure\", \"request_id\": \"641748043a66\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} / \"GET /products -> 503\" status 503 duration_ms 0.17 (non-konan request id, i.e. real/simulated shop traffic)"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:28.547Z"
    quote: "{\"ts\": \"2026-08-18T21:27:28.547Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"14a360148cad\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:29.630Z-21:27:29.631Z"
    quote: "{\"event\": \"chaos_failure\", \"request_id\": \"4d03f6f619cd\", \"method\": \"GET\", \"path\": \"/products/1\"} / \"GET /products/1 -> 503\" status 503 duration_ms 0.202 (non-konan request id)"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:29.724Z"
    quote: "{\"ts\": \"2026-08-18T21:27:29.724Z\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"7693b5e0b53f\", \"status\": 200, \"duration_ms\": 0.422} (93ms after E6, same path, different request id — same-path retry succeeds)"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:30.070Z"
    quote: "{\"ts\": \"2026-08-18T21:27:30.070Z\", \"event\": \"chaos_failure\", \"request_id\": \"995c872515b2\", \"method\": \"GET\", \"path\": \"/products/1\"} / \"GET /products/1 -> 503\" status 503 duration_ms 0.152 (second real-traffic failure in the same burst, non-konan request id)"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:59.598Z"
    quote: "{\"ts\": \"2026-08-18T21:27:59.598Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"02e576f03a28\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0} (re-armed ~5s after the E11 restart, same config as E5)"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T20:22:07.911Z"
    quote: "{\"ts\": \"2026-08-18T20:22:07.911Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"0d3ed61424da\", \"event\": \"chaos_disabled\"} (last explicit chaos_disabled marker anywhere in the log; every chaos_enabled since is a re-arm, not a fresh toggle from a known-off state)"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:27:53.279Z-21:27:54.637Z"
    quote: "\"Shutting down\" 21:27:53.279Z -> \"Finished server process\" -> \"Started server process\" 21:27:54.637Z -> \"Uvicorn running\" (clean restart landing between the E6/E8 failures and the E9 re-arm)"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:37:57.871Z-21:37:59.122Z"
    quote: "\"Finished server process [26746]\" 21:37:57.871Z -> \"Started server process [27297]\" 21:37:59.122Z (E1) -> chaos re-armed 4.9s later at E3"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:52:43.341Z-21:52:43.345Z"
    quote: "{\"ts\": \"2026-08-18T21:52:43.341Z\", \"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787089963-28069\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"} followed by \"GET /products/3 -> 500\" status 500 duration_ms 5.459, same request_id"
  - id: E14
    type: probe
    source: "scripts/probe.sh /products/3 @ request_id konan-1787089963-28069"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787089963-28069\"} -- HTTP 500 in 0.007532s"
  - id: E15
    type: probe
    source: "scripts/probe.sh /products/1 @ request_id konan-1787089964-28075"
    quote: "{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":116,\"units_ordered\":4,\"turnover_score\":0.034482758620689655} -- HTTP 200 in 0.001441s (control: non-zero-stock product succeeds on the same code path)"
  - id: E16
    type: metric
    source: "scripts/probe.sh /metrics @ request_id konan-1787089967-28092"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 2"
gaps:
  - "No caller identity confirms who armed the chaos flag (E3, E5, E9) or triggers the recurring process restarts (H3); /chaos sits outside the probe.sh allowlist by contract, and the surface exposes no supervisor/orchestration log, so the 'external harness' read is architectural inference, not a logged actor id."
  - "No direct link ties the specific complaining users to a specific failed request — the lab has no user-identity field, only client ip:port and request id. The mapping from complaint to the 21:27:29-30Z and 21:38:05Z failures rests on timing and pattern match (rate, retry-succeeds shape), not a named user or session."
  - "No same-path retry evidence exists for the E4 (21:38:05.551Z) failure specifically — the next real-traffic request in the log is a different path (/products/1, not /products), and real traffic stops shortly after in the reviewed window. Whether that particular failure was retried by the affected user cannot be confirmed from this surface."
  - "Root cause of the wider restart cadence (multiple restarts per hour across the full ~2-hour log history) could not be fully determined; some restarts (e.g. 20:35:37Z, 20:46:53Z) are not followed by a nearby chaos_enable, so the pattern is not fully uniform."
usage:
  model: claude-sonnet-5
  tokens: 5982738
  wall_clock_seconds: 885
---

# Shop intermittent 503s — chaos flag re-armed on real traffic, one latent defect riding along

## Summary

**Root cause identified.** The reported "occasional error... works on retry... most
people notice nothing" matches a chaos-injection config flag (`failure_rate=0.08`,
`error_status=503`) that was armed via `POST /chaos/enable` at `21:27:28.547Z` and
re-armed at `21:38:04.051Z` (H1, validated). Across the two bursts of real shop traffic
surrounding those markers, exactly three real (non-investigator) requests failed with
503 — two at `21:27:29-30Z` on `GET /products/1`, one at `21:38:05Z` on `GET /products` —
each interleaved with many successes on the same routes, and one confirmed to succeed on
an immediate same-path retry 93ms later. That is a low, bursty failure rate consistent
with "a couple of users," "occasional," and "most people notice nothing."

While triaging, a second, unrelated defect turned up: `GET /products/3` deterministically
500s with an uncaught `ZeroDivisionError` (H2, validated) because product 3 has
`units_in_stock: 0`. Reproduced live during this investigation. It is **latent, not
active**: the exception counter and every log occurrence trace back to investigator
probes only — no organic user traffic has hit that route yet, so it rides along as a
latent finding rather than the incident itself (its failure shape — 100% reproducible on
one product id — does not match the complaint's intermittent, retry-succeeds pattern
anyway).

A third thread, restart cadence, was opened and left open: the process restarts
repeatedly, and most (not all) restarts are followed 5-7 seconds later by a chaos
re-arm call, suggesting a scripted harness cycling scenarios rather than an independent
stability problem — but no logged actor confirms this (H3, inconclusive).

Confidence: high for H1 and H2 (both reproduced or directly log-correlated); low for H3
and for the exact mapping of "which specific failure the complaining users hit" (see
Gaps) — the complaint itself carries no request-level detail to pin that down further.

## Timeline (2026-08-18, UTC)

- `20:22:07.911Z`: last explicit `chaos_disabled` marker in the entire log (E10) — every
  later `chaos_enabled` is a re-arm, not a fresh toggle from a confirmed-off baseline.
- `21:27:23.613Z`-`21:27:28.547Z`: process restart, then chaos re-armed 4.9s later,
  `failure_rate=0.08` (E5).
- `21:27:29.630Z`-`21:27:30.070Z`: two real-traffic 503s on `GET /products/1` (E6, E8),
  the first followed 93ms later by a same-path 200 (E7).
- `21:27:53.279Z`-`21:27:54.637Z`: another restart lands mid-episode (E11).
- `21:27:59.598Z`: chaos re-armed again, same config (E9).
- `21:30:18.354Z`: investigator probe reproduces the `/products/3` `ZeroDivisionError`
  (pre-existing occurrence, outside this journal's fresh evidence but consistent with
  E13-E16).
- `21:37:57.871Z`-`21:37:59.122Z`: restart into the current process (E12, E1).
- `21:38:01.995Z`: clean `POST /orders -> 201`, before any chaos marker (E2).
- `21:38:04.051Z`: chaos re-armed, `failure_rate=0.08` (E3) — 4.9s after the restart.
- `21:38:05.551Z`: one real-traffic 503 on `GET /products` (E4); no same-path retry
  found afterward — real traffic tapers off shortly after in the reviewed window.
- `21:38:11Z`: complaint filed (this investigation's `startsAt`).
- `21:52:43.341Z`-`21:52:43.345Z`: this investigation reproduces the `/products/3`
  defect directly (E13, E14), confirms a healthy control on `/products/1` (E15), and
  confirms via `/metrics` that the exception counter matches the investigator-probe
  count exactly (E16).

## Investigation

- **Baseline**: `/health` (200, fresh process, uptime ~42s) and `/metrics` looked mostly
  clean at first glance (`faultline_chaos_enabled 1`, one `GET /products 503` already in
  the fresh process's own counters) — enough of a signal not to wave the complaint off.
- **Triage** (three lenses, run in parallel, blind to each other): infra-process flagged
  an elevated restart cadence with tight back-to-back pairs but no crash markers and no
  latency/RSS anomaly in the current process; interfaces found a sharp onset tied to the
  `21:38:04.051Z` chaos marker, a probabilistic ~1-in-7 failure rate on real traffic
  matching the configured 8%, and a recurring re-toggle pattern stretching back over an
  hour; software-defect found and reproduced the deterministic `/products/3`
  `ZeroDivisionError`, confirmed only investigator request ids had ever hit that route.
- **Judge, round 1**: validated H2 outright. Called H1 **inconclusive** — the cited
  timeline math was wrong (the `21:38:04.051Z` marker is ~7s before the complaint, not
  ~39s as first summarized, too fresh to fit "over the last few minutes"), and an
  earlier `21:27:28-30Z` episode fit the phrase better but wasn't cross-checked; also
  flagged that the `/metrics` totals used to argue the ~8% rate match weren't filtered
  to exclude investigator traffic.
- **Deep-dive, round 2**: built a real-traffic-only timeline across `21:20Z-21:40Z`
  (all `konan-*` request ids excluded), confirming exactly 3 real 503s in the whole
  window, both episodes' onset markers, and retry behavior (E6-E9 above).
- **Judge, round 2**: validated H1. Corrected a secondary framing error (the flag had
  not been "continuously enabled for 10.5 minutes" — restarts reset it three times and
  it was re-armed each time, E9/E11/E12) but held that this didn't change the verdict:
  the direct `chaos_failure`-to-503 request-id correlation, the low real-traffic rate,
  and the confirmed retry-success are sufficient, within the lab's limit that no
  user-identity-to-request link is possible.

## Hypotheses

### H1 — chaos-flag-injected intermittent 503s on real traffic (validated)
Two episodes of the same config (`failure_rate=0.08`, `error_status=503`) armed at
`21:27:28.547Z` (E5) and `21:38:04.051Z` (E3) produced exactly three real-traffic 503s
(E4, E6, E8) interleaved with many successes on the same routes — the classic
low-rate injected-degradation signature. One failure's same-path retry is directly
confirmed to succeed 93ms later (E7). Both episodes sit inside restart/re-arm pairs
(E9, E11, E12), which the round-2 judge treated as a detail, not a defeater: the
request-id-correlated failure evidence stands on its own. Soft spot, recorded rather
than glossed over: no evidence names who calls `POST /chaos/enable`, and no retry
evidence exists for the specific `21:38:05Z` failure (see Gaps).

### H2 — `/products/3` ZeroDivisionError (validated, latent)
`shop.py:64` divides `units_ordered` by `units_in_stock` without a zero check; product 3
has `units_in_stock: 0`, so every hit 500s. Reproduced live in this investigation (E13,
E14), with a healthy control on a non-zero-stock product on the same code path (E15).
`http_exceptions_total{type="ZeroDivisionError"}` reads exactly 2 (E16), matching the two
investigator probes exactly (the earlier software-defect lens's confirmation probe, and
this journal's own reproduction) — no organic occurrence found. Its failure shape (100%
reproducible on one specific id) doesn't match the complaint's intermittent pattern
either, reinforcing that it's a separate, latent issue.

### H3 — restart cadence (inconclusive)
Most restarts in the reviewed window are followed 5-7 seconds later by a `POST
/chaos/enable` call (E9, E11, E12) — a pattern consistent with a scripted harness
cycling scenarios (restart, then re-apply chaos config) rather than an independent
process-stability problem. But the pattern isn't fully uniform (some restarts, e.g.
`20:35:37Z` and `20:46:53Z`, have no nearby chaos-enable in the log), and no logged actor
identity or supervisor/orchestration log is available on this surface to settle either
reading. Left open rather than forced to a verdict.

## Safe next steps

- Re-check `/metrics` (`faultline_chaos_enabled`, `http_requests_total{status="503"}`)
  periodically — if the real-traffic 503 rate on `/products*` climbs materially above
  the ~8% configured rate, or stops being interleaved with successes, that would signal
  a change from "occasional, mostly unnoticed" to something worse.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` — if it climbs above the
  current count of 2 without a matching investigator probe, H2 has gone from latent to
  active user impact.
- No configuration change, rollback, or fix is proposed here — remediation is out of
  scope for this journal.

## Gaps

- No caller identity confirms who arms the chaos flag or triggers the recurring
  process restarts; the "external harness" read is architectural inference from the
  surface contract (`/chaos` is outside `probe.sh`'s allowlist), not a logged actor id.
- No user-identity field exists in this lab's telemetry, so the specific complaining
  users cannot be tied to a specific failed request; the complaint-to-evidence mapping
  rests on timing and pattern match only.
- No same-path retry evidence exists for the `21:38:05.551Z` failure specifically —
  real traffic tapers off in the log shortly after it, so whether that particular
  failure was retried by the affected user is unconfirmed.
- The wider restart cadence across the full ~2-hour log history is not fully explained
  by the chaos-re-arm pattern; a few restarts have no nearby chaos-enable event, and
  the root trigger for restarts in general is outside this surface's visibility.
