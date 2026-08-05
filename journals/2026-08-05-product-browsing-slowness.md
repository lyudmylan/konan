---
konan_journal: 1
investigation:
  id: 2026-08-05-product-browsing-slowness
  trigger: manual
  complaint: "periodic slowness reported on product browsing this morning; nothing confirmed; please verify current state"
  started: "2026-08-05T16:04:49+03:00"
  concluded: "2026-08-05T22:14:26+03:00"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "Periodic slowness is intermittently active on the product-browsing surface (/products, /products/{id}) in the current process — latency spikes recurring with some period, missed by short probe bursts."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E9, E10, E11, E12, E14, E15, E7]
  - id: H2
    statement: "Operator-injected probabilistic degradation (chaos latency/failure injection) is active on the browsing surface, causing intermittent slowness."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E8, E10]
  - id: H3
    statement: "The target service was not running during the reported morning window: the previous process shut down cleanly at 2026-08-02T04:52:26Z and nothing served or logged until the current process started at 2026-08-05T13:03:42Z — no target-side telemetry exists for the complained-of period."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4]
    evidence_against: []
  - id: H4
    statement: "The user-facing incident behind the complaint is the deterministic defect on GET /products/3 (ZeroDivisionError -> HTTP 500) on the product-browsing surface."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E16, E17, E18]
    evidence_against: [E4, E6]
latent_findings:
  - statement: "Deterministic per-input defect: GET /products/3 raises ZeroDivisionError at faultline shop.py:64 (\"turnover_score\": units_ordered / product[\"units_in_stock\"]) because product id 3 (Unobtainium Ingot) is the catalog's only zero-stock item; fast 500 (<10 ms), reproduced 9/9, siblings 1/2/4/5 return 200; every recorded occurrence carries a konan-* investigator request id — no user has ever hit it."
    evidence: [E16, E17, E18, E7, E6]
  - statement: "Catalog data anomaly: product id 4 (Mystery Box) carries price:null in the /products payload; served with HTTP 200 and no failure observed from it anywhere on the read surface."
    evidence: [E7, E17, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-02T04:52:26.928Z (line 30) — clean shutdown of the previous process; preceded at 04:52:26.826-.928Z by 'Shutting down' / 'Application shutdown complete', no stack, no exception"
    quote: |-
      {"ts": "2026-08-02T04:52:26.928Z", "level": "INFO", "logger": "uvicorn.error", "message": "Finished server process [93504]"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-05T13:03:42.614Z (line 31 — the line immediately following E1's; the file contains nothing between them); the 'faultline 0.1.0 started' startup event follows at 13:03:42.615Z"
    quote: |-
      {"ts": "2026-08-05T13:03:42.614Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [47943]"}
  - id: E3
    type: metric
    source: "probe /metrics, request_id=konan-1785935096-48001 @ 2026-08-05T13:04:56Z — 13:04:56 minus 73.47s places process start at ~13:03:42.5Z, independently matching E2"
    quote: |-
      process_uptime_seconds 73.46543595893309
  - id: E4
    type: metric
    source: "probe /metrics, request_id=konan-1785935096-48001 @ 2026-08-05T13:04:56Z — 19s after the complaint was raised this was the ONLY http_requests_total series in existence, and no http_exceptions_total sample existed: zero browsing traffic, zero errors, on a process then ~74s old"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 5
  - id: E5
    type: probe
    source: "probe /health, request_id=konan-1785935095-47996 @ 2026-08-05T13:04:55Z — baseline health"
    quote: |-
      {"status":"ok","uptime_seconds":72.98219350003637}
      -- HTTP 200 in 0.001728s request_id=konan-1785935095-47996
  - id: E6
    type: log
    source: "lab/logs/app.log @ 13:03:43.195Z, 13:03:45.262Z, 13:04:49.182Z — the ONLY request lines in the current-process window whose request_id is not konan-stamped; all three are localhost /health checks consistent with lab.sh lifecycle probes. Zero non-investigator requests ever reached the business surface of this process."
    quote: |-
      {"ts": "2026-08-05T13:03:43.195Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "14948ba02524", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 8.865, "client": "127.0.0.1:50670"}
      {"ts": "2026-08-05T13:03:45.262Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "a825d6240ff3", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.81, "client": "127.0.0.1:50671"}
      {"ts": "2026-08-05T13:04:49.182Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "c8ff16970e06", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.481, "client": "127.0.0.1:50677"}
  - id: E7
    type: probe
    source: "probe /products, request_id=konan-1785953182-53162 @ 2026-08-05T18:06:22Z — conclusion-time catalog read: browsing fast (2.2 ms); id 3 is the only zero-stock product; id 4 carries price:null"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.002243s request_id=konan-1785953182-53162
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-05T13:07:39.012Z — the HIGHEST duration_ms among all request lines in the entire log, both process windows (127 request lines at final scan; none >= 50 ms) — and it is the /products/3 500, not a slow success"
    quote: |-
      {"ts": "2026-08-05T13:07:39.012Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1785935258-48073", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.656, "client": "127.0.0.1:50700"}
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1785935701-48508 @ 2026-08-05T13:15:01Z — deep-dive opening bracket"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products"} 0.012059957254678011
      http_request_duration_seconds_count{method="GET",path="/products"} 25
  - id: E10
    type: metric
    source: "probe /metrics, request_id=konan-1785952551-52892 @ 2026-08-05T17:55:51Z — deep-dive closing bracket: delta vs E9 is 21.4 ms over 17 additional /products requests (mean 1.26 ms); the lifetime sum alone (33.5 ms across 42 requests) arithmetically excludes even one >=50 ms /products response ever having been served"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products"} 0.03349520894698799
      http_request_duration_seconds_count{method="GET",path="/products"} 42
  - id: E11
    type: metric
    source: "probe /metrics, request_id=konan-1785953188-53169 @ 2026-08-05T18:06:28Z — /products/{id} lifetime summary including the nine 500s: mean ~1.6 ms"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.06469212309457362
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 41
  - id: E12
    type: metric
    source: "probe /metrics, request_id=konan-1785953188-53169 @ 2026-08-05T18:06:28Z — bit-identical value at the 13:04:56Z scrape (konan-1785935096-48001) and the 13:15:01Z scrape (konan-1785935701-48508): peak RSS flat across ~5 hours, no saturation onset"
    quote: |-
      process_max_rss_bytes 46530560
  - id: E13
    type: metric
    source: "probe /metrics, request_id=konan-1785953188-53169 @ 2026-08-05T18:06:28Z — also 0 at every earlier scrape (13:04:56Z, 13:15:01Z, 17:55:51Z); a scan of the entire log found zero chaos_enabled/chaos_disabled/chaos_failure/simulated_exception events"
    quote: |-
      faultline_chaos_enabled 0
  - id: E14
    type: probe
    source: "probe /products, request_id=konan-1785952266-52632 @ 2026-08-05T17:51:06Z — the WORST client-side reading among the deep-dive's 34 spaced probes 17:51:06-17:55:08Z (17x /products, 12x /products/{1,2,4}, 5x trailing-slash 307); every other /products* probe read 0.001472-0.004364s"
    quote: |-
      -- HTTP 200 in 0.029359s request_id=konan-1785952266-52632
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-05T17:51:07.047Z — the server-side line for E14's request: 8.0 ms served; the ~21 ms remainder was client-side cold-start after the idle gap, not service latency"
    quote: |-
      {"ts": "2026-08-05T17:51:07.047Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1785952266-52632", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 8.026, "client": "127.0.0.1:52183"}
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-05T13:07:39.002Z — the first exception ever recorded in this process, on an investigator probe; stack trimmed ([...]) to the throwing frame, kept text unaltered"
    quote: |-
      {"ts": "2026-08-05T13:07:39.002Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1785935258-48073", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  [...]  File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E17
    type: probe
    source: "probe /products/3, request_id=konan-1785935258-48073 @ 2026-08-05T13:07:39Z — deterministic on repeat: konan-1785935273-48148 and konan-1785935413-48218 also 500; 9/9 across the investigation, with interleaved /products/1,2,4,5 probes all 200"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1785935258-48073"}
      -- HTTP 500 in 0.010443s request_id=konan-1785935258-48073
  - id: E18
    type: metric
    source: "probe /metrics, request_id=konan-1785953188-53169 @ 2026-08-05T18:06:28Z — the only exception series and the only 5xx series in existence; both equal the 9 investigator probes of /products/3 (the log holds exactly 9 'GET /products/3 -> 500' lines, all konan-stamped)"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 9
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 9
gaps:
  - "No target-side telemetry exists for the complained-of window (the morning of 2026-08-05 before 13:03:42Z): the single unrotated log jumps from the 2026-08-02T04:52:26Z shutdown directly to the 2026-08-05T13:03:42Z startup (H3). The reporter's experience can be neither confirmed nor refuted from this surface; only a reporter-side capture (timestamps, exact URL/host, HAR) could settle what they saw."
  - "Zero non-investigator requests reached the business surface during the entire investigation, so the current-state verdict rests exclusively on konan-stamped probes; degradation that manifests only under real user load was not exercised."
  - "Sampling dead zone 13:15-17:51Z (session idle): no /products* requests occurred at all in that stretch, so no latency samples exist inside it. Slowness at those moments is excluded only by the whole-log scan (no request line >= 50 ms ever, E8's source) covering every request actually served; a request that hung and never completed would never produce a log line and would evade that scan."
  - "The deep-dive loop never sampled /products/5 (a trailing-slash artifact sent those probes to /products/ -> 307); id 5 is covered only by triage-time probes and the shared /products/{product_id} duration summary (E11)."
  - "faultline_chaos_enabled was read as 0 at four instants, not continuously; 'enabled earlier, disabled before first read' is excluded only by the empty chaos-event scan of the whole log (an absence, so no quotable ledger line exists) and by the total absence of latency effects (E8, E10)."
  - "User-vs-investigator attribution rests on the request-id convention (unstamped = non-investigator); all observed traffic originates from 127.0.0.1."
usage:
  model: claude-fable-5
  tokens: null
  wall_clock_seconds: 22177
---

# Product-browsing slowness report — no active incident; the reported window has no telemetry (target was down)

## Summary

**No active incident.** The current state of product browsing is verified fast and
error-free: across ~60 investigator probes in two sampling campaigns (13:05-13:11Z and
spaced 17:51-17:55Z), no `/products*` response exceeded 9.7 ms server-side in the
process's entire lifetime (E8), the route's cumulative duration budget arithmetically
excludes even one hidden >=50 ms response (E9, E10), memory is flat (E12), and chaos
injection is off with zero chaos events ever logged (E13). The reported symptom itself —
"periodic slowness ... this morning" — cannot be confirmed *or* attributed, because the
target was not running that morning: the previous process shut down cleanly on
2026-08-02T04:52:26Z and the current one started 2026-08-05T13:03:42Z, 55 seconds before
the complaint was filed (E1, E2, E3; hypothesis H3, judge-validated). Whatever the
reporter saw, this service's telemetry holds no trace of it, and no user traffic has
reached the business surface since startup (E4, E6). Two latent findings ride along
without changing the verdict: a deterministic `ZeroDivisionError` 500 on `GET
/products/3` (zero-stock division at shop.py:64 — real, reproducible, so far triggered
only by investigator probes: E16, E17, E18) and a `price:null` datum on product 4 (E7).
Confidence in "no active incident now" is high; confidence about the morning is
explicitly none — that window is a documented gap, not a cleared one.

## Timeline

All times UTC, anchored to evidence ids.

- **2026-08-02T04:42:14Z** — previous process (93504) starts; serves a small healthy
  user-traffic window (all 200/201, sub-10 ms) until shutdown.
- **2026-08-02T04:52:26.928Z** — clean shutdown: "Finished server process [93504]"
  (E1). The log then falls silent for ~3 days 8 hours.
- **[gap]** — the complaint's "this morning" (2026-08-05 before 13:03Z) falls entirely
  inside this silence: no process, no log lines, no counters (E1→E2 adjacency).
- **2026-08-05T13:03:42.614Z** — current process (47943) starts (E2); the only
  change-marker in the entire log. Three unstamped localhost `/health` checks follow
  (13:03:43-13:04:49, E6) — lab lifecycle, not user browsing.
- **13:04:37Z** — complaint raised (`startsAt`).
- **13:04:49Z** — investigation starts (trigger latency 12 s). Baseline 13:04:55-56Z:
  health green at uptime ~73 s (E5, E3), counters near-empty with zero exceptions (E4).
- **13:05-13:11Z** — triage: three lenses in parallel. First-ever exception in the
  process at 13:07:39.002Z — an investigator probe of `/products/3` (E16, E17); the
  same request is the slowest line the log will ever hold, 9.656 ms (E8).
- **13:15:01Z** — deep-dive opens its metrics bracket (E9).
- **13:15-17:51Z** — session idle; zero `/products*` requests of any origin (E9→E10
  counts).
- **17:51:06-17:55:08Z** — deep-dive spaced sampling, 34 probes across 4m02s; worst
  client-side reading 29.4 ms (E14) resolves to 8.0 ms server-side (E15); all others
  1.5-4.4 ms.
- **17:55:51Z** — deep-dive closing bracket: mean 1.26 ms across the window (E10).
- **18:06:22-28Z** — conclusion snapshot: catalog fast and intact (E7), per-id summary
  ~1.6 ms mean (E11), RSS bit-identical to baseline (E12), chaos 0 (E13), exception
  census unchanged at 9, all investigator-stamped (E18).
- **19:14:26Z** — investigation concluded.

## Investigation

**Trigger.** Manual (`/konan`). Complaint object as synthesized by the adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1785935077",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "periodic slowness reported on product browsing this morning; nothing confirmed; please verify current state" },
  "startsAt": "2026-08-05T13:04:37Z"
}
```

No severity: the reporter stated none and none was inferred. Investigation start
2026-08-05T13:04:49Z — trigger latency 12 seconds.

**Baseline (13:04:49-56Z).** Health 200 at uptime ~73 s (E5, E3); the only request
series in existence was five `/health` 200s, no exception series (E4); chaos gauge 0;
RSS ~46.5 MB. Two facts shaped everything after: the process was one minute old, and
the log showed a 3-day silence ending at today's startup (E1, E2).

**Triage (one round, three lenses, parallel and blind to each other):**
infra-process, interfaces, software-defect — the complaint is vague, so no domain could
be excluded a priori; no lens was skipped. Convergent findings, deduplicated: (a) the
complained-of window has zero telemetry coverage — the service was down (all three
lenses); (b) the current browsing surface is uniformly fast — dozens of probes, all
1.2-3.6 ms (all three); (c) a deterministic per-input 500 on `/products/3`,
ZeroDivisionError, the catalog's only zero-stock item, exclusively investigator-
triggered (interfaces + software-defect); (d) minor: `price:null` on product 4, and no
Product response schema declared in `/openapi.json`. The interfaces lens also ran the
change-marker sweep: zero chaos/config events in the whole log; the only change marker
is the 13:03:42Z startup itself.

**Hypotheses formed:** H1 (periodic slowness active now), H2 (chaos injection active),
H3 (target down during the reported window), H4 (the /products/3 defect is the
reported incident). Selection: H2, H3, H4 had deterministic, complete triage evidence
and went straight to the judge; only H1 had a real evidence gap — "periodic" could hide
from short bursts — so one deep-dive (of a budgeted three) ran spaced sampling.

**Deep-dive (H1):** bracketing metrics snapshots (E9, E10) around 34 probes spread
over 4m02s, plus a whole-log duration scan. Every predicted channel came back
negative: no sample >= 50 ms (worst: E14, explained server-side by E15), sum-delta
math excludes hidden spikes (E10), RSS flat (E12), no restart, no new non-investigator
traffic. One sampling artifact recorded honestly: the loop's id-5 probes hit
`/products/` (307) instead of `/products/5` (gap 4).

**Judge (fresh, evidence-only — saw the hypothesis list and verbatim quotes, no
narrative):** H1 **invalidated** (every channel affirmatively contradicted; noted the
lifetime `/products` sum of 33.5 ms makes a >=50 ms spike arithmetically impossible,
not merely unseen). H2 **invalidated** (gauge 0, no gateway statuses, failures
deterministic per-input — the opposite signature of probabilistic injection; residual
"chaos was on earlier" closed by the empty lifecycle-event scan, kept as gap 5 because
an absence has no quotable line). H3 **validated** (log adjacency, uptime arithmetic,
and near-empty counters cross-corroborate; the judge's only unfalsifiable residue — a
second instance logging elsewhere — is asserted by no one). H4 **invalidated** (at
13:04:56Z, 19 s after the complaint, zero `/products*` requests and no exception
series existed — the defect's first occurrence ever is an investigator probe at
13:07:39Z, after the complaint; also a category mismatch: the complaint says slowness,
the defect produces fast 500s). Latent findings L1 and L2 validated; the judge's
citation improvement for L2 (add E17, E18) is applied in the machine core.

**Iteration decision:** validated H3 plus three invalidations left nothing a second
round could settle from this surface — the judge's remaining "settling evidence" for
H4/the morning report is reporter-side data, outside the surface contract. Concluded
within round one. Budget spent: 1 triage round (3 lenses), 1 deep-dive of 3, 1 judge.
Tokens: subagents alone consumed ~204k (three lenses ~119k, deep-dive ~42k, judge
~43k); the orchestrator's share is not measurable in an interactive session, so the
machine core records `tokens: null`.

## Hypotheses

### H1 — periodic slowness active now (infra-process) — invalidated

Formed because "periodic" can evade short bursts. Refuted on every predicted channel:
the slowest request line in the process's entire life is 9.656 ms — and it is the
`/products/3` 500, not a slow success (E8); the `/products` lifetime duration sum,
33.5 ms over 42 requests, cannot contain a single >=50 ms response (E9, E10); the
per-id route means ~1.6 ms including the 500s (E11); RSS is bit-identical across five
hours (E12); and the one elevated client-side reading, 29.4 ms (E14), was served in
8.0 ms (E15) — cold-start overhead, not service latency. Conclusion-time browsing is
2.2 ms (E7). Residuals (idle dead zone, hung-request shape) are recorded as gaps 3-4,
not as evidence.

### H2 — chaos/injected degradation active (interfaces) — invalidated

`faultline_chaos_enabled 0` at every read (E13); no 502/503/504 series exists; no slow
tail anywhere (E8, E10); and the only failures observed are deterministic per-input —
the signature of a code defect, not probabilistic injection. The whole-log scan found
zero chaos lifecycle events (empty result, gap 5).

### H3 — target down during the reported window (infra-process) — validated

The strongest result of the investigation: E1 (clean shutdown 2026-08-02T04:52:26.928Z)
and E2 (startup 2026-08-05T13:03:42.614Z) are *adjacent lines* in a single unrotated
log; uptime arithmetic independently confirms the start time (E3); and 19 s after the
complaint the counters held nothing but five health checks (E4). "This morning" falls
entirely inside the silence. Consequence, stated precisely: the reported slowness is
not confirmable, not refutable, and not attributable from this surface — this validated
hypothesis explains why the complaint cannot be verified, and it is not itself an
active incident (the shutdown was clean and operator-shaped, and the service is up and
healthy now).

### H4 — the /products/3 defect caused the report (software-defect) — invalidated

The defect is real (E16, E17, E18) but cannot be what the reporter saw: before and at
the complaint's timestamp no exception series and no `/products*` requests existed at
all (E4); the defect's first-ever occurrence is a konan-stamped probe at 13:07:39Z; the
only non-investigator requests in the whole process are three health checks (E6); and
during the morning the service was not running (H3), so no user could have received
this 500 then. The complaint also alleges slowness, while the defect fails fast
(<10 ms).

### Latent findings (ride along; not the incident)

**L1** — `GET /products/3` deterministically 500s: `ZeroDivisionError` at
`shop.py:64`, `"turnover_score": units_ordered / product["units_in_stock"]`, with id 3
the catalog's only `units_in_stock: 0` item (E16, E17, E7). All nine occurrences in
the counters are investigator probes (E18, E6) — zero user impact to date, but any
real user opening that product page will hit it. **L2** — product 4 serves
`price:null` (E7); tolerated by every read path observed (E17, E18); noted as a
poisoned-datum candidate for paths outside the read-only surface.

## Safe next steps

Read-only; remediation is out of scope, and lab defects are faultline's contract — not
ours to fix.

- Ask the reporter for client-side specifics: exact time window, URL/host actually
  browsed, and if possible a HAR or screenshot with timestamps. That is the single
  piece of evidence the judge named that could settle the morning report — target-side
  telemetry for that window cannot exist (H3).
- Confirm with the lab operator that the 2026-08-02T04:52Z stop and 2026-08-05T13:03Z
  start were intentional, and whether users could have been pointed at any other
  instance this morning — if so, that instance's telemetry is where the slowness would
  live.
- Surface L1 to the target's owners as a latent-defect report: `/products/3` will 500
  for the first real user who opens it. Surface L2 (price:null) alongside.
- If longer-horizon assurance on "periodic" is wanted: a brief re-probe plus a
  chaos-gauge re-read once real traffic resumes beats long-horizon polling (the
  deep-dive's recommendation).

## Gaps

The machine core lists six; in brief: the complained-of window has no telemetry at all
— the verdict says nothing about what the reporter experienced, only that this service
holds no trace and was down (1); zero real-user traffic means the current-state
verdict rests on investigator probes alone (2); the 13:15-17:51Z idle stretch has no
samples and a hung-request shape would never log (3); the deep-dive's id-5 probes were
lost to a trailing-slash 307, leaving id 5 to triage coverage only (4); the chaos
gauge was read at instants, with "briefly enabled earlier" excluded only by an empty
event scan that has no quotable line (5); and user-vs-investigator attribution rests
on the request-id convention over all-localhost traffic (6).
