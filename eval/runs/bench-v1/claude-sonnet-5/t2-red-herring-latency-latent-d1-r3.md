---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-latency-slowdown
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-19T02:53:04Z
  concluded: 2026-08-19T02:58:26Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was enabled at 2026-08-19T02:52:46.291Z with extra_latency_ms=1500, injecting extra latency into business-path requests while /health was left unaffected."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled via POST /chaos/enable at 2026-08-19T02:52:46.291Z (extra_latency_ms=1500, failure_rate=0.0), injecting extra latency into business-path requests (/products, /products/{id}, /orders) while leaving /health unaffected, causing the reported shop-wide slowness while health checks stayed green and fast."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E12]
    evidence_against: []
  - id: H2
    statement: "The users' report of seeing an error page once corresponds to an actual server-side 5xx response or unhandled exception on the target."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E10, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:46.291Z"
    quote: "{\"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.0, \"error_status\": 503, \"extra_latency_ms\": 1500}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:41.116Z"
    quote: "GET /products -> 200, duration_ms 1.156"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:48.866Z"
    quote: "GET /products -> 200, duration_ms 514.378"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:42.172Z"
    quote: "GET /products/1 -> 200, duration_ms 0.901"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:52.495Z"
    quote: "GET /products/1 -> 200, duration_ms 1477.196"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:43.230Z"
    quote: "POST /orders -> 201, duration_ms 1.908"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:54.053Z"
    quote: "POST /orders -> 201, duration_ms 492.217"
  - id: E8
    type: probe
    source: "GET /health via scripts/probe.sh, request_id konan-1787108015-40247 @ 2026-08-19T02:53:35.399Z"
    quote: "GET /health -> 200, duration_ms 0.635"
  - id: E9
    type: metric
    source: "/metrics scrape @ 2026-08-19T02:53:35Z"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: metric
    source: "/metrics scrape @ 2026-08-19T02:53:35Z"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3 / http_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 1 / http_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 2 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 / http_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2 (no other status series present)"
  - id: E11
    type: metric
    source: "/metrics scrape @ 2026-08-19T02:53:35Z"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter (no data lines follow — zero exception series recorded)"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:52:46.292Z"
    quote: "POST /chaos/enable -> 200, duration_ms 2.718, request_id 2e68923942e9"
gaps:
  - "The application log only covers the current process lifetime (started 2026-08-19T02:52:40.362Z, ~13s before chaos was enabled); nothing earlier could be checked, so a pre-existing condition before process start cannot be ruled out from this surface."
  - "No proxy/gateway/browser-side layer exists in this lab surface (docs/lab.md's known-gaps section: no distributed topology), so the reported 'error page' could reflect a client-side timeout during the ~500-1500ms latency spikes (E3, E5, E7) rather than a server-side error — this cannot be confirmed or refuted from app-level logs/metrics alone, which show zero 5xx and zero exceptions (E10, E11)."
  - "Each business route has only one pre-chaos/post-chaos sample pair in the log window; the pattern is consistent across three independent routes (H1) but the deep-dive round was skipped because triage evidence was already deterministic, so no additional repeated sampling was gathered to further tighten the pre/post comparison."
usage:
  model: claude-sonnet-5
  tokens: 1660984
  wall_clock_seconds: 322
---

# Chaos-mode latency injection explains the shop-wide slowdown; no server-side error corroborates the reported error page

## Summary

**Root cause identified.** Chaos mode was switched on at `02:52:46.291Z` with
`extra_latency_ms=1500` and `failure_rate=0.0` (E1, confirmed as arriving via
`POST /chaos/enable -> 200` at E12). Every business route sampled afterward —
`/products`, `/products/{id}`, `POST /orders` — jumped from sub-2ms to 400–1500ms
(E2–E7), while `/health` stayed fast throughout (E8), matching the complaint's "health
checks are green and fast" almost exactly: health is not on the code path chaos
degrades. The judge validated this hypothesis (H1) as a clean, temporally-ordered
pattern across three independent endpoint families.

The second half of the complaint — "some also mention seeing an error page once" — is
**not corroborated by any server-side evidence**: the chaos config's error path was
configured but disarmed (`failure_rate=0.0`, E1), no 5xx status appears in the request
counters (E10), and the exception counter recorded zero events (E11). The judge
invalidated H2 (that the error page was a real server-side 5xx/exception) on this
evidence. If the report is accurate, the most likely explanation given the observed
400–1500ms spikes is a client-side timeout rendering an error page without ever
reaching a server-side 5xx — but this lab has no proxy/browser layer to confirm that
from telemetry (see Gaps).

Confidence: high on the slowness mechanism (three independent routes, clean onset,
metric-confirmed); the error-page claim is only ruled out as a *server-side* cause, not
independently explained.

## Timeline

- `02:52:40.362Z` — process startup (`faultline 0.1.0 started`).
- `02:52:41.089Z`–`02:52:43.230Z` — baseline traffic, all sub-2ms, all 2xx (E2, E4, E6).
- `02:52:46.291Z` — **chaos mode enabled** (E1): `extra_latency_ms=1500`,
  `failure_rate=0.0`, `error_status=503` (configured but not armed).
- `02:52:46.292Z` — the enabling request itself logged as `POST /chaos/enable -> 200`
  (E12), same `request_id` as E1.
- `02:52:48.866Z`–`02:52:55.552Z` — every subsequent business-route request slows to
  400–1500ms (E3, E5, E7); no 5xx, no exceptions.
- `02:53:35.399Z` — investigator's `/health` probe still fast (E8); `/metrics` confirms
  `faultline_chaos_enabled 1` (E9) and an all-2xx counter set (E10) with zero exception
  series (E11).

## Investigation

1. **Baseline**: `/health` (fast, 200) and `/metrics` scraped; `lab/logs/app.log` read in
   full (21 lines at that point — the whole process lifetime). The chaos-enabled marker
   and the latency jump were both visible directly in the baseline read.
2. **Triage**: all three lenses (infra-process, interfaces, software-defect) run in
   parallel, each blind to the others, given only the lens file, `docs/lab.md`, the
   verbatim complaint, and the baseline summary. All three independently converged on
   the same mechanism: infra-process flagged "alive but degraded, health structurally
   blind to it"; interfaces flagged the config-change marker and sharp onset; software-
   defect found zero exception/5xx evidence and explicitly deferred to
   infrastructure/injected-degradation given the spread-everywhere shape.
3. **Deep-dive skipped**: triage evidence was already deterministic and complete (a
   named config event, bracketed by clean before/after samples on three independent
   routes, plus corroborating metrics) — per protocol this goes straight to judge rather
   than re-proving itself.
4. **Judge**: one fresh adversarial judge agent, given only the hypothesis statements and
   the cited evidence ledger (no lens reasoning). Verdict: H1 validated, H2 invalidated.
   The judge flagged two residual caveats, both carried into Gaps below: only one
   pre/post sample pair per route, and no proxy-layer evidence to rule out a client-side
   timeout behind the "error page" report.

## Hypotheses

### H1 — chaos-induced latency (validated)

Chaos mode's `extra_latency_ms=1500` injected delay into business routes starting
`02:52:46.291Z` (E1, E12); `/products`, `/products/{id}`, and `POST /orders` each swing
from sub-2ms to 400–1500ms immediately after (E2/E3, E4/E5, E6/E7), while `/health`
stays fast throughout (E8) and `/metrics` confirms the flag is active (E9). The judge
validated this as a consistent, independently-corroborated pattern across three route
families with no contradicting evidence.

### H2 — error page reflects a real server-side error (invalidated)

The chaos config's error path was present but disarmed: `failure_rate=0.0` (E1); the
full request-status counter set shows only 200/201 series, no 5xx anywhere (E10); the
exception counter recorded zero events (E11). The judge invalidated this cleanly, while
noting the app-level evidence cannot rule out a client/proxy-side timeout — see Gaps.

## Safe next steps

- Re-scrape `/metrics` and re-read `lab/logs/app.log` after a few more minutes to see
  whether chaos-induced latency is still active and whether its pattern (rate, which
  routes) is stable — read-only, no state change.
- If a report ever includes a client-observable status code or timestamp for the
  "error page," correlate it against `lab/logs/app.log` `request_id`s for that window —
  the app-level surface alone cannot settle a client-side-timeout explanation.

## Gaps

- The application log only covers the current process lifetime (started
  `2026-08-19T02:52:40.362Z`, ~13s before chaos was enabled); anything earlier is out of
  reach on this surface.
- This lab has no proxy/gateway/browser layer (per `docs/lab.md`'s known-gaps section),
  so a client-side timeout during the 400–1500ms spikes remains a plausible but
  unconfirmable explanation for the reported "error page" — app-level telemetry shows
  zero 5xx and zero exceptions, which rules out a server-side cause but not a client-side
  one.
- Each business route has only one pre-chaos/post-chaos sample pair in the window
  gathered; the deep-dive round was skipped because triage evidence was already
  deterministic and consistent across three independent routes, so no additional
  repeated sampling was collected to further tighten the comparison.
