---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zero-stock-500s
  trigger: "manual (/konan human profile; fingerprint human-1787176022; alertname human-report; startsAt 2026-08-19T21:47:02Z; investigation start 2026-08-19T21:47:17Z; trigger latency 15s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-19T21:47:17Z
  concluded: 2026-08-19T21:52:32Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} computes turnover_score = units_ordered / units_in_stock without a zero guard; product 3 has units_in_stock = 0, so every request to /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "The GET /products/{id} handler divides by the product's units_in_stock without guarding against zero; product 3 has units_in_stock = 0, so every request to /products/3 fails deterministically with an unhandled ZeroDivisionError (HTTP 500)."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E4, E5, E6, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by injected chaos, process instability (crash/restart loop), or resource exhaustion."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E7, E8]
  - id: H3
    statement: "The 500s are caused by a failing dependency, gateway, or interface/contract change."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E3, E8, E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:46:45.285Z"
    quote: "\"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"769ad8fa932f\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\" — stack ends: File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product | \"turnover_score\": units_ordered / product[\"units_in_stock\"], | ZeroDivisionError: division by zero"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:46:45.297Z–21:46:51.660Z"
    quote: "Four access lines \"GET /products/3 -> 500\" with distinct request_ids: 769ad8fa932f @ 21:46:45.297Z, 951339d1ae76 @ 21:46:46.372Z, 05f27ca7a875 @ 21:46:49.514Z, a3719e820e6b @ 21:46:51.660Z — each paired with an identical ZeroDivisionError unhandled_exception line carrying the same request_id."
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:46:38.979Z–21:46:50.584Z"
    quote: "\"GET /products/1 -> 200\" @ 21:46:40.076Z; \"GET /products/2 -> 200\" @ 21:46:48.441Z (between two /products/3 failures); \"POST /orders -> 201\" @ 21:46:50.584Z; \"GET /health -> 200\" @ 21:46:38.979Z"
  - id: E4
    type: metric
    source: "/metrics @ 2026-08-19T21:47:49Z, request_id konan-1787176069-72740"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 ; http_exceptions_total{type=\"ZeroDivisionError\"} 4 ; faultline_chaos_enabled 0 ; process_uptime_seconds 71.63099199999124 ; process_max_rss_bytes 48234496"
  - id: E5
    type: probe
    source: "/products/3, request_id konan-1787176231-72829"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787176231-72829\"} -- HTTP 500 in 0.004599s"
  - id: E6
    type: probe
    source: "/products, request_id konan-1787176240-72836"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0} -- HTTP 200 in 0.001331s"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:46:38.237Z"
    quote: "{\"ts\": \"2026-08-19T21:46:38.237Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} — the only startup event in app.log; zero chaos_enabled/chaos_disabled/chaos_failure/simulated_exception events; no rotated backups exist."
  - id: E8
    type: metric
    source: "/metrics @ 2026-08-19T21:49:16Z"
    quote: "process_uptime_seconds 157.85799349984154 (no reset since 71.63 at baseline) ; process_max_rss_bytes 48234496 (unchanged) ; http_request_duration_seconds_sum{method=\"GET\",path=\"/products/{product_id}\"} 0.030679335119202733 over _count 7 (≈4.4 ms average)"
  - id: E9
    type: probe
    source: "/products/4, request_id konan-1787176262-72844"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200 in 0.001442s"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:46:45.297Z–21:46:51.660Z"
    quote: "All four failing request_ids (769ad8fa932f, 951339d1ae76, 05f27ca7a875, a3719e820e6b) lack the konan- investigator prefix — end-user traffic; every failure status is 500, never 502/503/504."
gaps:
  - "How and when product 3's units_in_stock reached 0 is not determinable from the surface: the log window begins at process start (21:46:38Z), no rotated backups exist, no order for product 3 appears in the log, and the data store is outside the investigator's surface — the zero stock predates all visible traffic (seed data or pre-restart state)."
  - "The complaint's 'started within the last hour' onset cannot be checked before 21:46:38Z; no pre-restart telemetry exists, so whether customers saw errors before this process start is unknown."
  - "Source code is outside the investigator's surface; the missing zero guard is established from the stack-trace line and the divisor-isolation probe (E9), not from reading the file."
  - "Triage lens subagents were permission-denied on scripts/probe.sh; their live probes were re-run by the orchestrator (E5, E6, E9), so no evidence is missing from this — recorded for process honesty."
usage:
  model: claude-fable-5
  tokens: 1892864
  wall_clock_seconds: 315
---

# Product 3 page returns 500 on every request: unguarded division by zero stock

## Summary

Root cause identified. `GET /products/3` fails deterministically — 4 of 4 customer
requests and a live investigator probe all return HTTP 500 — because the product-detail
handler computes `turnover_score = units_ordered / product["units_in_stock"]`
(`shop.py:64`) with no guard, and product 3 ("Unobtainium Ingot") has
`units_in_stock = 0` (E1, E5, E6). Every other probed route and product succeeds in the
same window (E3, E9), which matches the complaint exactly: one product page errors,
refresh cannot help, other pages load fine. Chaos injection is off and process health is
clean (E4, E7, E8) — this is a data-dependent software defect, not infrastructure or a
dependency. Confidence: high; log, metrics, and live probes corroborate independently,
and the exception count equals the 500 count exactly (E4).

## Timeline

- 21:46:38Z — process start, faultline 0.1.0, the only startup marker; no
  chaos/config-change markers anywhere in the log (E7).
- 21:46:40–48Z — user traffic succeeds on /products/1, /products/2, POST /orders (E3).
- 21:46:45.285Z — first unhandled ZeroDivisionError on GET /products/3 (E1); three more
  identical failures through 21:46:51.660Z, all end-user traffic (E2, E10).
- 21:47:02Z — support complaint delivered via /konan (trigger block above).
- 21:47:17Z — investigation start; baseline captured at ~21:47:41–49Z (E4).
- 21:50:31Z — investigator probe reproduces the 500 on /products/3 (E5); /products shows
  units_in_stock = 0 for product 3 (E6); /products/4 isolates the divisor (E9).
- 21:52:32Z — concluded.

## Investigation

Complaint object, verbatim as synthesized by the /konan adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1787176022",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of." },
  "startsAt": "2026-08-19T21:47:02Z"
}
```

Investigation start 2026-08-19T21:47:17Z (trigger latency 15s). Baseline: /health 200,
chaos off, 4×500 on /products/{product_id} already in metrics (E4). Triage fanned out
across all three lenses in parallel — software-defect, infra-process, interfaces — none
excludable from the baseline. Software-defect found the deterministic per-input failure
(E1, E2); infra-process found a clean lifecycle with one young process and no chaos or
resource pressure (E7, E8); interfaces found no gateway/dependency signature (E10). The
lens subagents' probes were permission-denied, so the orchestrator ran the three
decisive probes itself: reproduction (E5), divisor confirmation (E6), divisor isolation
(E9). H1's evidence was deterministic and complete, so all hypotheses went straight to
the adversarial judge (no deep-dive round needed). Judge: H1 validated, H2 and H3
invalidated. Budget used: 1 triage round of 3 lenses, 0 deep-dive agents, 1 judge.

## Hypotheses

### H1 — unguarded division by zero stock (software-defect) — validated

Statement: the product-detail handler divides by `units_in_stock` with no zero guard;
product 3's stock is 0, so every GET /products/3 raises ZeroDivisionError → 500.
For: the stack trace names the exact expression and line (E1); 4/4 user requests failed
identically (E2); metrics count 4 exceptions = 4 500s (E4); a fresh probe reproduces it
on demand (E5); the listing shows the zero divisor (E6); the same computation succeeds
with a nonzero divisor on product 4, isolating the variable (E9); the failing traffic is
end-user, not investigator (E10). Against: none. The judge noted one weakness — "no
zero guard" is inferred from the stack trace, not read from source (source is outside
the surface) — and held it insufficient to change the verdict.

### H2 — chaos injection / process instability (infra-process) — invalidated

For: none. Against: chaos gauge 0 and no chaos events ever logged (E4, E7); uptime
monotonic with no restart, RSS flat, latency ~4.4 ms (E8); successes interleave between
failures, incompatible with a crash loop or exhaustion (E3). Reviving evidence the judge
named: a metrics sample from inside the failure window showing chaos enabled, or a
second startup/uptime reset — neither exists.

### H3 — dependency / gateway / contract failure (interfaces) — invalidated

For: none. Against: the stack terminates inside the app's own handler on an arithmetic
operation with no dependency frame (E1); pure 500s, never 502/503/504 (E10); failures
complete in milliseconds, no timeout shape (E8); adjacent routes succeed in the same
seconds, incompatible with a shared failing dependency (E3). Reviving evidence the judge
named: any outbound-call frame or upstream-schema change in the /products/3 path — none
is present.

## Safe next steps

Read-only suggestions only; remediation is out of scope for this journal.

- Watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}` — they rise with
  each customer hit on product 3 and will show ongoing impact.
- Check the data store / seed data for other products with `units_in_stock = 0` — any
  such product's page will fail the same way the moment a customer opens it.
- If pre-restart history matters (the "last hour" onset), retrieve logs from before
  21:46:38Z from wherever the previous process's output went; this instance holds none.
- Note for the eventual fix review (not performed here): `shop.py:64`,
  `turnover_score = units_ordered / product["units_in_stock"]`.

## Gaps

Elaborating the frontmatter list: the zero stock's origin is unobservable — the log
starts at process boot, contains no order for product 3, and the data store is outside
the surface contract, so seed data vs. pre-restart depletion cannot be distinguished.
Onset before 21:46:38Z is unverifiable for the same reason; the complaint's "last hour"
is consistent with, but not proven by, the visible window. Source code was not read
(outside the surface); the defect mechanism rests on the stack trace plus the
divisor-isolation probe. The lens subagents could not probe directly (permission
denial); the orchestrator's own probes closed every gap they flagged, so no evidence
was lost. Product 4's `price: null` was checked as a possible second anomaly and is not
a defect on this endpoint (E9) — no latent findings are claimed.
