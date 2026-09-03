---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-injected-503s
  trigger: "manual (/konan human profile). Complaint object: source=human, fingerprint=human-1787157596, labels.alertname=human-report, severity=<not stated by reporter>, startsAt=2026-08-19T16:39:56Z. Investigation start 2026-08-19T16:40:19Z — trigger latency 23s."
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-19T16:40:19Z
  concluded: 2026-08-19T16:42:28Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime fault-injection flag was switched on at 16:39:49.549Z with failure_rate 0.08 and error_status 503, so a random ~8% of shop requests are rejected with 503 before reaching handler logic; the flag is still enabled."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos/fault-injection configuration was enabled mid-timeline (failure_rate 0.08, error_status 503), causing probabilistic 503s on shop routes that succeed on retry."
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E11]
    evidence_against: []
  - id: H2
    statement: "A data-dependent code defect in the product-detail route makes specific product ids fail consistently."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E13]
  - id: H3
    statement: "The process crashed, restarted, or is resource-saturated, and the errors are lifecycle or saturation symptoms."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E10]
  - id: H4
    statement: "Order placement — the revenue path — is also failing and users are losing purchases."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E14]
latent_findings:
  - statement: "GET /products/3 fails deterministically with an unhandled ZeroDivisionError (product 3 'Unobtainium Ingot' has units_in_stock 0, and turnover_score divides units_ordered by units_in_stock). Only the investigator's probe has ever triggered it in this process lifetime, so it caused no user impact yet — but any user who opens that product will get a 500 that no retry fixes."
    evidence: [E8, E9]
  - statement: "Chaos-injected 503s are recorded in http_requests_total under literal paths (/products/2, /products/5) while successful requests use the templated path (/products/{product_id}), so error and success counters for the same route do not aggregate and error cardinality grows per product id."
    evidence: [E6, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:44.585Z"
    quote: '{"ts": "2026-08-19T16:39:44.585Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:49.549Z"
    quote: '{"ts": "2026-08-19T16:39:49.549Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "0a2457f8fdfe", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:50.742Z"
    quote: '{"ts": "2026-08-19T16:39:50.742Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "da7b20b8cd91", "event": "chaos_failure", "method": "GET", "path": "/products/2"} / {"ts": "2026-08-19T16:39:50.742Z", "message": "GET /products/2 -> 503", "request_id": "da7b20b8cd91", "event": "request", "status": 503, "duration_ms": 0.131, "client": "127.0.0.1:62920"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:50.910Z"
    quote: '{"ts": "2026-08-19T16:39:50.910Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b7aa86631696", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.452, "client": "127.0.0.1:62932"}'
  - id: E5
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787157715-65575 @ 2026-08-19T16:41:55Z"
    quote: "faultline_chaos_enabled 1"
  - id: E6
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787157715-65575 @ 2026-08-19T16:41:55Z"
    quote: 'http_requests_total{method="GET",path="/products/2",status="503"} 2 / http_requests_total{method="GET",path="/products/5",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 17 / http_requests_total{method="POST",path="/orders",status="201"} 6'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:45.346Z"
    quote: '{"ts": "2026-08-19T16:39:45.346Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "18f24cd8c49e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 2.009, "client": "127.0.0.1:62907"}'
  - id: E8
    type: probe
    source: "GET /products/3, request_id konan-1787157698-65568"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787157698-65568"} -- HTTP 500 in 0.009058s'
  - id: E9
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787157715-65575 @ 2026-08-19T16:41:55Z (compare: the http_exceptions_total family was empty at konan-1787157623-65513, before the /products/3 probe)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 1'
  - id: E10
    type: metric
    source: "/metrics via scripts/probe.sh, request_ids konan-1787157623-65513 and konan-1787157715-65575"
    quote: "process_uptime_seconds 38.69382108282298 → process_uptime_seconds 130.47122833295725 / process_max_rss_bytes 47218688 → process_max_rss_bytes 48250880"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:50.840Z"
    quote: '{"ts": "2026-08-19T16:39:50.840Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5ecdf951fe66", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
  - id: E12
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787157623-65513 @ 2026-08-19T16:40:23Z"
    quote: 'http_requests_total{method="GET",path="/products/5",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 14'
  - id: E13
    type: probe
    source: "GET /products/2, request_id konan-1787157685-65537"
    quote: '{"id":2,"name":"Toaster","price":23.0,"units_in_stock":36,"units_ordered":4,"turnover_score":0.1111111111111111} -- HTTP 200 in 0.001969s'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:39:51.037Z"
    quote: '{"ts": "2026-08-19T16:39:51.037Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "af3fce50bf7c", "event": "order_created", "order_id": 6, "product_id": 2, "quantity": 1, "total_price": 23.0}'
gaps:
  - "The observation window is one process lifetime only — ~2 minutes, starting 2026-08-19T16:39:44.585Z (E1). No rotated backups exist (lab/logs/app.log.1 is absent), so the earlier part of the reporter's 'last few minutes' has no telemetry. Errors before 16:39:44Z can be neither confirmed nor excluded."
  - "Who or what enabled the injection flag, and whether it was intentional, is outside the investigator's surface: the enabling call arrives as POST /chaos/enable from 127.0.0.1 with no actor identity in the log line (E2), and /chaos is operator surface that probe.sh refuses by contract."
  - "All three user-facing 503s landed on product-detail routes and none on /products or /orders (E6). With only 3 failures the split is not statistically separable from uniform 8% injection, so whether the injector is route-scoped is untested."
  - "Triage lenses and the adversarial judge ran inline in the orchestrator context rather than as separate blind subagents — this session was instructed not to spawn agents. The lens domains (software-defect, infra-process, interfaces) and the refutation pass were each applied, but without the blindness firewall the investigate skill specifies, so narrative-capture protection is weaker than the standard loop's."
  - "User impact is bounded by log evidence only. Three 503s reached non-investigator clients; there is no client-side or session telemetry, so how many distinct end users saw an error is unknown."
usage:
  model: claude-opus-5
  tokens: 992663
  wall_clock_seconds: 129
---

# Chaos fault-injection flag left enabled, rejecting ~8% of shop requests with 503

## Summary

**Root cause identified, and the fault is still active.** At 16:39:49.549Z a runtime
fault-injection flag was switched on with `failure_rate: 0.08` and `error_status: 503`
(E2). Since that moment a random ~8% of shop requests are rejected with a 503 *before*
handler logic runs — which is exactly why the reporter's users see an occasional error
that goes away on retry: the next attempt draws a different die roll. Three user-facing
503s are in the log (two on `/products/2`, one on `/products/5`), against 32 user
requests after the marker and zero errors before it (E3, E7, E11, E6).

The reporter's instinct — "probably nothing" — is understandable but wrong in one
respect that matters: this is not noise that has passed. The injector is **still armed**
at the end of this investigation (`faultline_chaos_enabled 1`, E5), so the error rate
continues until someone turns it off. The impact is genuinely mild (retry works, orders
are unaffected — 6 of 6 order placements returned 201, E6, E14), but it is ongoing, not
historical. Confidence is high: this is not a correlation argument. Every 503 carries a
`chaos_failure` log line with the *same request_id* as the failed request (E3, E11), so
the telemetry names the mechanism directly rather than merely placing it nearby.

Separately, and **not** part of what users are seeing: `GET /products/3` fails
deterministically with an unhandled `ZeroDivisionError` (E8). Only my own probe has
ever triggered it (`http_exceptions_total{type="ZeroDivisionError"} 1`, and that one is
mine — E9), so it is a latent defect, not the incident. It is the more dangerous of the
two findings in the long run: no retry will ever fix it.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 16:39:44.585Z | Process starts — `faultline 0.1.0 started`. This is the only startup marker; everything below is one process lifetime. | E1 |
| 16:39:45–47 | Normal traffic: `/health`, `/products`, `/products/1`, one order created. All 200/201, sub-3ms. **Last known good.** | E7 |
| **16:39:49.549Z** | **Configuration change marker** — `chaos mode enabled`, `failure_rate: 0.08`, `error_status: 503`, `extra_latency_ms: 0`. | E2 |
| 16:39:50.742Z | **First known bad** — `chaos-injected failure` on `GET /products/2`, request_id `da7b20b8cd91` → 503. 1.2s after the marker. | E3 |
| 16:39:50.826Z | Second injected failure, `GET /products/2` again. | E6 |
| 16:39:50.840Z | Third injected failure, `GET /products/5`. | E11 |
| 16:39:50.910Z | `GET /products/2` → 200. Same input that failed twice, 168ms later — the "works on retry" the reporter describes. | E4 |
| 16:39:51.037Z | Order 6 created successfully; the revenue path is unaffected throughout. | E14 |
| 16:40:19Z | Investigation starts (complaint raised 16:39:56Z; trigger latency 23s). | — |
| 16:41:38Z | Investigator probe of `GET /products/3` returns 500 `ZeroDivisionError` — latent defect, first ever trigger. | E8 |
| 16:41:55Z | `faultline_chaos_enabled 1` — **injection still on at conclusion**. | E5 |

## Investigation

**Baseline.** `/health` returned 200 with `uptime_seconds: 36.3` — a very young process,
so I treated process lifecycle as a live question rather than assuming steady state. The
first `/metrics` scrape immediately broke the case open: `faultline_chaos_enabled 1`
alongside `POST /chaos/enable` in the request counters, plus 503s on two product paths
and an *empty* `http_exceptions_total` family. Health was green while the business
surface was throwing 503s — the healthy-monitoring shape the skill warns about, so I
worked from business-route counters rather than `/health` from that point on.

**Triage.** The complaint is vague ("an error in the shop"), so no lens domain could be
excluded up front; I applied all three. Note the deviation recorded under Gaps: this
session was instructed not to spawn subagents, so the lenses and the judge ran inline in
one context instead of as blind parallel agents.

- *Interfaces* — found the `chaos_enabled` marker (E2): a runtime configuration change
  with a sharp onset, probabilistic gateway-shaped 503s, exactly its domain signature.
- *Software-defect* — found no exceptions and no stack traces behind the 503s, and the
  exception counter family was empty. This lens argued *against* a code defect for the
  reported symptom, and it later produced the latent finding.
- *Infra-process* — one startup marker, no restart loop, RSS ~47MB and flat, all
  durations sub-millisecond, `extra_latency_ms: 0`. Nothing in its domain.

**Deep-dive.** H1's decisive test was cheap and disconfirmable: if injection is the
mechanism, the same product id must both fail and succeed within seconds, and the
before/after rates must straddle the marker. Both held — `/products/2` went 503, 503,
200 inside 170ms (E3, E4), and the rate went 0/5 before the marker to 3/32 (≈9.4%,
against the configured 0.08) after it. The `chaos_failure` line sharing the failed
request's id (E3) upgraded this from correlation to a named mechanism.

H2 was the hypothesis worth trying hardest to save, since "specific inputs fail" is a
real defect shape. I probed the business surface directly: `/products/2`, `/products/5`,
`/products` and `/products/4` all returned 200 (E13) — including `/products/4`, whose
`price: null` in the list response looked like a plausible data-dependent trap. It is
not. Then `/products/3` (`units_in_stock: 0`) returned 500 `ZeroDivisionError` (E8).

**Attribution check on that 500.** Before concluding I had found a second incident, I
asked whether any *user* had ever hit it. `http_exceptions_total{type="ZeroDivisionError"}`
reads exactly 1, the exception family was empty on the earlier scrape, and the only
`/products/3` request in the counters is my own stamped probe (E9). My probe created
that data point. Per the prime directive on investigator-visible traffic, it is a latent
finding and does not touch the verdict. It also fails to explain the complaint on its
own terms: it is deterministic and never recovers, while the reported symptom recovers
on retry.

**Judge (inline, adversarial).** Against H1 I asked what else could produce these 503s
with no exception recorded — and found no competing account that explains a
`chaos_failure` event stamped with the failing request's own id. Against H2 and H3 I
asked what evidence would rescue them; for H2 the same-input 503→200 flip inside 170ms
(E3, E4) is fatal, and for H3 a monotonic uptime across two scrapes with flat RSS (E10)
leaves no lifecycle event to point at. H4 I raised deliberately because "the shop is
erroring" should always be tested against the revenue path, not just the browse path;
6 of 6 orders returned 201 (E6, E14), so it dies too.

## Hypotheses

### H1 — Fault-injection configuration enabled mid-timeline · **validated**

Injection was switched on at 16:39:49.549Z with `failure_rate: 0.08`, `error_status: 503`
(E2). For: the sharp onset at the marker with a clean before-window (E7); three
`chaos_failure` events each sharing the request_id of a 503 access line (E3, E11); an
observed post-marker error rate of 3/32 ≈ 9.4% against a configured 0.08 (E6); the same
product id failing then succeeding 168ms later (E4); and the gauge still reading 1 at
conclusion (E5). Against: nothing found. The rate arithmetic is the weakest link — 3
events is a small sample — but the mechanism does not rest on it: the `chaos_failure`
lines name the cause outright.

### H2 — Data-dependent defect in the product-detail route · **invalidated**

Killed by the same-input flip: `/products/2` returned 503 at :50.742 and :50.826, then
200 at :50.910 (E3, E4). Deterministic per-input failure is the signature of this
domain, and this is the opposite of deterministic. Live probes of ids 2, 4 and 5 all
returned 200 (E13). The defect I *did* find on this route (`/products/3`, E8) belongs to
this hypothesis family but is excluded from the incident by the attribution check in E9.

### H3 — Process crash, restart loop, or resource saturation · **invalidated**

One startup marker in the entire log (E1), uptime advancing monotonically 38.7s → 130.5s
across two scrapes with no reset, RSS flat at ~47–48MB, and `extra_latency_ms: 0` with
all durations sub-millisecond (E10). Nothing in this domain to anchor an anomaly to.

### H4 — Order placement is failing too · **invalidated**

Tested because a browse-path complaint should not be allowed to hide a revenue-path
failure. All 6 order placements in the window returned 201 (E6), the last at 16:39:51.037Z
after injection was live (E14). Injection can in principle hit `/orders`; in this window
it did not.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Confirm with the operator whether the injection flag was switched on deliberately**
   (a load test, a game day, a demo) — that single answer decides whether this is an
   incident to escalate or an exercise to let finish. The flag is still on (E5), so it
   should be asked now rather than queued.
2. **Re-scrape `/metrics` and compare `faultline_chaos_enabled` and the 503 counters** to
   confirm when the flag goes off and that the error rate returns to zero; the gauge is
   the cheapest possible watch signal.
3. **Track the latent `/products/3` defect as its own bug**, independent of this
   incident. Any product whose `units_in_stock` reaches 0 appears to take the same path
   (product 3 is at 0 stock and is the one that fails, E8) — so a normal sell-out could
   convert this from latent to user-facing without any code change.
4. **Note the metrics-labelling inconsistency** for whoever owns dashboards: 503s are
   recorded under literal paths while 200s use the route template (E6, E12), so any
   error-rate panel built on `path="/products/{product_id}"` will read 0% during exactly
   this kind of event.

## Gaps

- **The window is ~2 minutes.** All telemetry comes from one process lifetime beginning
  16:39:44.585Z (E1), and no rotated backups exist. The reporter said "the last few
  minutes"; the earlier part of that span has no telemetry at all, so I can neither
  confirm nor exclude errors before the process started.
- **No actor identity for the change.** The enabling request is logged from
  `127.0.0.1` with no user or source attribution (E2), and `/chaos` is operator surface
  that `probe.sh` refuses by contract. Who turned it on is not answerable from the
  investigator's surface.
- **Route scoping untested.** All three 503s hit product-detail routes and none hit
  `/products` or `/orders` (E6). At 3 failures this is not separable from chance under
  uniform 8% injection, so I make no claim either way.
- **Lens blindness firewall not in force.** Triage and the judge ran inline in one
  context rather than as separate blind subagents, per this session's instruction not to
  spawn agents. Every domain was applied and the refutation pass did run, but the
  structural protection against narrative capture was absent.
- **End-user count unknown.** Three 503s reached non-investigator clients; with no
  client-side or session telemetry, how many distinct people that represents is not
  determinable — consistent with, but not proof of, the reporter's "a couple of users".
