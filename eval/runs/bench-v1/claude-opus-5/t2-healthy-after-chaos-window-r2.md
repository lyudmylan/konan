---
konan_journal: 1
investigation:
  id: 2026-08-19-handover-check
  trigger: "manual — /konan human adapter; source: human, fingerprint: human-1787140257, labels.alertname: human-report (no severity stated by reporter), startsAt 2026-08-19T11:50:57Z; investigation started 2026-08-19T11:51:05Z (trigger latency 8s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-19T11:51:05Z
  concluded: 2026-08-19T11:53:31Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The 'noise earlier' was an operator-enabled chaos injection window (failure_rate 0.6, error_status 503) running 11:50:21.878Z to 11:50:28.264Z, which ended when chaos was disabled; it is not ongoing."
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E7]
    evidence_against: []
  - id: H2
    statement: "The shop service is currently degraded — an ongoing fault (process instability, saturation, or sustained errors) is affecting users right now."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E12, E13, E15]
  - id: H3
    statement: "GET /products/{id} raises ZeroDivisionError for any product whose units_in_stock is 0, because shop.py computes turnover_score as units_ordered / product['units_in_stock']; product 3 holds units_in_stock 0, so that route deterministically returns 500 — a latent data-dependent defect no user request has reached."
    incident_class: software-defect
    state: validated
    evidence_for: [E8, E9, E10, E11, E14]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 deterministically returns HTTP 500 (ZeroDivisionError at shop.py:64, turnover_score = units_ordered / units_in_stock, with units_in_stock 0). Both occurrences were triggered by investigator probes; the exception counter equals exactly the investigator's two requests, so no user has hit it."
    evidence: [E8, E9, E10, E11, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:17.998Z"
    quote: "{\"ts\": \"2026-08-19T11:50:17.998Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:21.878Z"
    quote: "{\"ts\": \"2026-08-19T11:50:21.878Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"4c6cbfa867b3\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.6, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:22.943Z"
    quote: "{\"ts\": \"2026-08-19T11:50:22.943Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"0bdc8d1f09ab\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:28.264Z"
    quote: "{\"ts\": \"2026-08-19T11:50:28.264Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode disabled\", \"request_id\": \"d7f761f1273f\", \"event\": \"chaos_disabled\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:48.335Z"
    quote: "{\"ts\": \"2026-08-19T11:50:48.335Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"5c88f09ba488\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 0.629, \"client\": \"127.0.0.1:60002\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:50.465Z"
    quote: "{\"ts\": \"2026-08-19T11:50:50.465Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"232ea787a450\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 1.516, \"client\": \"127.0.0.1:60005\"}"
  - id: E7
    type: metric
    source: "/metrics @ request_id konan-1787140371-56615"
    quote: "faultline_chaos_enabled 0"
  - id: E8
    type: probe
    source: "/products @ request_id konan-1787140317-56569"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E9
    type: probe
    source: "/products/3 @ request_id konan-1787140349-56598"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787140349-56598\"}\n-- HTTP 500 in 0.009458s request_id=konan-1787140349-56598"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:52:29.782Z"
    quote: "\"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787140349-56598\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"... File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\""
  - id: E11
    type: metric
    source: "/metrics @ request_id konan-1787140371-56615"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 2"
  - id: E12
    type: probe
    source: "/health @ request_id konan-1787140276-56549"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":58.423860375070944}\n-- HTTP 200 in 0.001545s request_id=konan-1787140276-56549"
  - id: E13
    type: metric
    source: "/metrics @ request_ids konan-1787140276-56555 then konan-1787140371-56615"
    quote: "process_uptime_seconds 58.945151542080566 / process_max_rss_bytes 46825472  →  process_uptime_seconds 153.15762270917185 / process_max_rss_bytes 46825472"
  - id: E14
    type: probe
    source: "/products/3 @ request_id konan-1787140368-56609"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787140368-56609\"}\n-- HTTP 500 in 0.003603s request_id=konan-1787140368-56609"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:50:51.531Z"
    quote: "{\"ts\": \"2026-08-19T11:50:51.531Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"45d89a56410b\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 0.998, \"client\": \"127.0.0.1:60006\"}"
gaps:
  - "Telemetry visibility begins at the process start marker 2026-08-19T11:50:17.998Z (E1) and lab/logs/ holds no rotated backups, so anything before that time is unobservable. Attributing the reporter's vague 'noise earlier' to the chaos window rests on that window being the only degradation inside the observable period, not on a direct link to what the reporter heard."
  - "No non-investigator traffic has been recorded since 2026-08-19T11:50:52.596Z. The 'right now' part of the answer therefore rests on investigator probes, not on live user requests."
  - "Product 4 ('Mystery Box') exposes \"price\": null in the catalog (E8). GET /products/4 returns 200, but whether order creation for a null-priced product faults cannot be tested read-only — POST /orders is outside the probe allowlist, and triggering it is eval-side only."
  - "Triage lenses and the adversarial judge ran inside the orchestrator rather than as blind parallel subagents, because subagent use was barred for this session. The judge's narrative-capture firewall was therefore not in place; hypothesis states here are self-reviewed against the cited evidence."
  - "Why chaos was enabled, and by whom, is not answerable from the investigator's surface — /chaos is operator surface and outside the probe allowlist."
  - "One Bash form (a shell loop iterating probe paths) was denied by the boundary hook. It was re-run as individual scripts/probe.sh calls, so no intended coverage was lost."
usage:
  model: claude-opus-5
  tokens: 774357
  wall_clock_seconds: 146
---

# Handover check: chaos window already closed, plus a latent 500 on /products/3

## Summary

**No active incident.** The shop service is serving correctly right now. The "noise
earlier" is fully explained by an operator-enabled chaos injection window that ran for
about six seconds — 11:50:21.878Z to 11:50:28.264Z — at a 0.6 failure rate returning
503s (E2, E3, E4). It ended when chaos was disabled, and the chaos gauge now reads 0
(E7). Every user request after that window succeeded: catalog, product detail, order
creation, and order listing all returned 2xx (E5, E6, E15). The process has not
restarted, and memory is flat across two scrapes (E13).

Two things the handover should carry forward. First, the four 503s during the window
were real user-facing failures, not investigator traffic — so if anyone did notice
something, they were not imagining it; there is simply nothing left to fix, because the
window is closed. Second, and more useful: the investigation found a **latent defect**
unrelated to the chaos. `GET /products/3` returns HTTP 500 every time, with a
ZeroDivisionError thrown at `shop.py:64`, where `turnover_score` is computed as
`units_ordered / product["units_in_stock"]` — and product 3 ("Unobtainium Ingot") holds
`units_in_stock: 0` (E8, E9, E10, E14). This is latent, not active: the exception
counter reads exactly 2 (E11), which is exactly the two probes this investigation sent.
No user has reached it yet. Any user who views that product will get a 500, and any
product whose stock falls to zero will start behaving the same way.

Confidence is high on both findings. The chaos attribution is direct rather than
correlational — each 503 carries its own `chaos_failure` event under the same request
id. The defect is confirmed by stack trace plus two identical reproductions.

## Timeline

- **11:50:17.998Z** — process starts; this is the earliest telemetry that exists (E1).
- **11:50:18–11:50:19** — healthy traffic: `/health`, `/products`, `/products/1`, all 200.
- **11:50:21.878Z** — configuration change marker: chaos mode enabled, `failure_rate: 0.6`,
  `error_status: 503` (E2).
- **11:50:22.943Z** — first injected failure, `GET /products -> 503` (E3). Three more
  follow, on `/products/2`, `/products/1`, and `/products`, interleaved with one
  successful order creation — the probabilistic shape a 0.6 rate predicts.
- **11:50:28.264Z** — chaos mode disabled (E4). The last 503 was at 11:50:27.198Z.
- **11:50:48–11:50:52** — user traffic resumes clean: `/products` 200 (E5),
  `/products/1` 200, `POST /orders` 201 (E6), `/orders` 200 (E15), `/products/5` 200.
- **11:50:57Z** — the complaint is raised.
- **11:51:16Z onward** — investigator probes. All healthy except `/products/3`, which
  returns 500 at 11:52:29.782Z (E9, E10) and again at 11:52:48 (E14).

## Investigation

Baseline came from `/health` (E12), a `/metrics` scrape, and the log. The log turned out
to cover the entire process lifetime — 31 lines from startup to the moment of reading —
so the observable history was complete rather than sampled, which is why triage
converged quickly.

The three lenses were applied against that baseline. **Interfaces** owned the answer to
the complaint: it found the chaos configuration markers bracketing the failures, with a
sharp onset and a sharp end, and a probabilistic rather than per-input failure shape.
**Infra-process** found nothing: one startup marker only, monotonic uptime, RSS byte-identical
across two scrapes 95 seconds apart (E13), and sub-2ms durations throughout. **Software-defect**
is what turned up the real news — following the healthy-monitoring rule past a green
`/health` into the business surface, the catalog listing exposed two data oddities
(product 3 with zero stock, product 4 with a null price), and probing product 3 returned
a deterministic 500.

Per the skill's own rule, hypotheses whose triage evidence was already deterministic and
complete went straight to judgement rather than to a deep-dive round; there were no
evidence gaps left to fill by probing. The adversarial pass ran in-orchestrator — see
Gaps, this is a genuine methodological weakness of this run — and specifically tested
whether the 500 could be chaos residue (it cannot: chaos was off, the gauge reads 0, and
chaos produces 503 with no stack trace, not 500 with a ZeroDivisionError) and whether
the 503s could have a cause other than chaos (they cannot: each carries its own
`chaos_failure` event under a matching request id).

## Hypotheses

### H1 — the noise was an operator chaos window (validated)

The `chaos_enabled` marker at 11:50:21.878Z declares the exact parameters — 0.6 failure
rate, 503 status (E2) — and every failure in the window carries a `chaos_failure` event
with the same request id as its 503 access line (E3). The `chaos_disabled` marker at
11:50:28.264Z (E4) closes it, and no 5xx appears in user traffic afterward. The chaos
gauge now reads 0 (E7). Attribution here is direct, not correlational. The one caveat is
about the *reporter's* words rather than the evidence: "noise earlier" is vague, and this
window is the only degradation inside the observable period — it is not independently
confirmed to be the thing they heard about.

### H2 — the shop is currently degraded (invalidated)

Every disconfirming check came back clean: five consecutive user requests across four
distinct business routes returned 2xx after the window closed (E5, E6, E15), the chaos
gauge is 0 (E7), health is 200 (E12), and the process shows no restart and no memory
growth (E13). This hypothesis is dead for the service as a whole. It does not cover
`/products/3`, which H3 handles.

### H3 — latent ZeroDivisionError on zero-stock products (validated, latent)

The stack trace names the throwing operation exactly: `shop.py:64`,
`"turnover_score": units_ordered / product["units_in_stock"]` (E10). The catalog shows
product 3 with `units_in_stock: 0` (E8), which makes the divisor zero. Two probes
produced identical 500s (E9, E14) — deterministic per-input failure, the classic code
defect signature, and clearly distinct from the probabilistic chaos failures. The
data-dependent shape is confirmed from the other direction too: products 1, 2, 4 and 5
all return 200 on the same route.

It is **latent, not active**. `http_exceptions_total{type="ZeroDivisionError"}` reads
exactly 2 (E11), matching the investigation's own two requests; no user traffic in the
log ever requested `/products/3`. This finding therefore rides along without changing
the verdict — but it is the thing most worth handing to the next shift, since it will
become a user-facing 500 as soon as anyone views that product, or as soon as any other
product sells out.

## Safe next steps

All read-only; remediation belongs to whoever owns faultline.

1. Confirm with the operator who enabled chaos at 11:50:21.878Z that it was intentional
   and that the window is meant to stay closed — the reason is not visible in the
   investigator's surface.
2. Watch `http_exceptions_total{type="ZeroDivisionError"}` for growth beyond 2. Any
   increase means real user traffic has reached the zero-stock path, which promotes the
   latent finding to an active incident.
3. Treat `units_in_stock: 0` in the catalog listing as an early-warning signal: it
   predicts which product ids will 500 on their detail route, and it is readable from
   `/products` without triggering the fault.
4. Raise the null price on product 4 with the service owner as an open question — it is
   an untested risk, not a finding.

## Gaps

Listed in the machine core; the ones that would change the answer if resolved:

- **History before 11:50:17.998Z does not exist on disk.** There are no rotated log
  backups, so the investigation cannot see whether anything happened before the process
  started. If the reporter's "noise" predates that marker, this journal did not examine it.
- **No live user traffic since 11:50:52.596Z.** The claim that the service is healthy
  *right now* rests on investigator probes rather than on real user requests. A synthetic
  probe passing is weaker evidence than users succeeding.
- **The adversarial judge was not firewalled.** Session policy barred subagents, so
  lenses and judge ran inside the orchestrator with full sight of the investigation
  narrative — exactly the narrative capture the separate-judge design exists to prevent.
- **The null price on product 4 is untested.** Order creation is outside the read-only
  boundary, so its behavior for a null-priced product is unknown rather than safe.
</content>
</invoke>
