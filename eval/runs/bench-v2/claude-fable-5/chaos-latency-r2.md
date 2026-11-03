---
konan_journal: 2
investigation:
  id: 2026-11-03-shopwide-slowness
  trigger: "manual (/konan adapter; complaint fingerprint human-1793700280, startsAt 2026-11-03T10:04:40Z, investigation start 2026-11-03T10:05:06Z — trigger latency 26s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: "2026-11-03T10:05:06Z"
  concluded: "2026-11-03T10:12:47Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos degradation switch, enabled at 2026-11-03T10:04:21.625Z via POST /chaos/enable with failure_rate 0.0 and extra_latency_ms 1500 and still on at conclusion, injects variable extra latency (observed 3.6–1298 ms, bounded by the 1500 ms setting) into business-path requests that still return correct 200/201 responses — storewide slowness with zero errors, while every sampled /health and /metrics request stayed under 1 ms."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos switch, enabled at 2026-11-03T10:04:21.625Z with failure_rate 0.0 and extra_latency_ms 1500 and still active, injects extra latency into business-path requests (/products, /orders) while sampled /health and /metrics requests stay fast — producing page slowness with zero errors."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E14, E15, E2, E19, E3, E4, E5, E6, E7, E8, E18]
    evidence_against: [E16]
  - id: H2
    statement: "A defect in the target's own code (wrong result or unhandled error on some input) causes the slowdown."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E13, E11, E4, E5]
  - id: H3
    statement: "Demand exceeding capacity (load saturation) causes the slowdown."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E12, E17, E3, E4, E8, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:21.625Z — the mechanism marker: chaos enabled, latency-only (failure_rate 0.0, extra_latency_ms 1500)"
    quote: |-
      {"ts": "2026-11-03T10:04:21.625Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "082f57bd684c", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: metric
    source: "probe /metrics, request_id=konan-1793700307-27921 @ 2026-11-03T10:05:07Z — the switch is on at investigation start"
    quote: |-
      faultline_chaos_enabled 1
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:16.450Z — user traffic 5 s before the switch: /products in 1.278 ms"
    quote: |-
      {"ts": "2026-11-03T10:04:16.450Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "ac3f909a42b6", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.278, "client": "127.0.0.1:49492"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:24.986Z — first user request after the switch: same path, ~1000x slower, still 200"
    quote: |-
      {"ts": "2026-11-03T10:04:24.986Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "1bc8da56d404", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1297.692, "client": "127.0.0.1:49497"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:31.775Z — a second business path slow after the switch, still 200"
    quote: |-
      {"ts": "2026-11-03T10:04:31.775Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "7e5ab320ca5f", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 646.406, "client": "127.0.0.1:49503"}
  - id: E6
    type: probe
    source: "probe /products, request_id=konan-1793700426-28016 @ ~2026-11-03T10:07:06Z (interfaces lens) — degradation live during the investigation"
    quote: |-
      -- HTTP 200 in 1.170732s request_id=konan-1793700426-28016
  - id: E7
    type: probe
    source: "probe /health, request_id=konan-1793700428-28022, adjacent to E6 (interfaces lens) — fast control probe next to a 1.17 s business probe; excludes a client- or network-side cause"
    quote: |-
      -- HTTP 200 in 0.001287s request_id=konan-1793700428-28022
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:05:07.278Z — /health sub-millisecond during the slow window; matches the green-health complaint"
    quote: |-
      {"ts": "2026-11-03T10:05:07.278Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793700307-27916", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.869, "client": "127.0.0.1:49531"}
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1793700307-27921 @ 2026-11-03T10:05:07Z — the exception counter header is immediately followed by the next metric's header: zero exception samples"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E10
    type: metric
    source: "probe /metrics, request_id=konan-1793700307-27921 @ 2026-11-03T10:05:07Z — the complete request-counter block: every row 200/201, 13 requests total in the whole process life"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:15.531Z — the only startup event in app.log; no rotated backups exist"
    quote: |-
      {"ts": "2026-11-03T10:04:15.531Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E12
    type: metric
    source: "probe /metrics, request_id=konan-1793700307-27921 @ 2026-11-03T10:05:07Z — peak RSS at baseline"
    quote: |-
      process_max_rss_bytes 47972352
  - id: E13
    type: probe
    source: "probe /products/1, request_id=konan-1793700756-28146 @ ~2026-11-03T10:12:36Z — slow but complete and well-formed; the same path served in 2.02 ms pre-switch (log @ 10:04:17.510Z, duration_ms 2.02)"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 0.896224s request_id=konan-1793700756-28146
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:21.626Z — the operator call that flipped the switch; same request_id as the E1 marker"
    quote: |-
      {"ts": "2026-11-03T10:04:21.626Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "082f57bd684c", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.601, "client": "127.0.0.1:49495"}
  - id: E15
    type: metric
    source: "probe /metrics, request_id=konan-1793700307-27921 @ 2026-11-03T10:05:07Z — exactly one enable call in the process life"
    quote: |-
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:04:30.072Z — a post-switch business request with almost no added latency: the injection is variable, not a constant 1500 ms add"
    quote: |-
      {"ts": "2026-11-03T10:04:30.072Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e1bfcb95edac", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 3.577, "client": "127.0.0.1:49502"}
  - id: E17
    type: metric
    source: "probe /metrics, request_id=konan-1793700401-27973 @ ~2026-11-03T10:06:41Z (infra-process lens) — uptime monotonic vs baseline 52.18 s ninety seconds earlier (one process, no restart); peak RSS identical to E12"
    quote: |-
      process_uptime_seconds 145.9572680001147
      process_max_rss_bytes 47972352
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:05:07.702Z — /metrics also sub-millisecond during the slow window"
    quote: |-
      {"ts": "2026-11-03T10:05:07.702Z", "level": "INFO", "logger": "faultline.request", "message": "GET /metrics -> 200", "request_id": "konan-1793700307-27921", "event": "request", "method": "GET", "path": "/metrics", "status": 200, "duration_ms": 0.6, "client": "127.0.0.1:49532"}
  - id: E19
    type: metric
    source: "probe /metrics, request_id=konan-1793700432-28029 @ ~2026-11-03T10:07:12Z (interfaces lens) — the switch is still on mid-investigation; no chaos_disabled event exists in app.log"
    quote: |-
      faultline_chaos_enabled 1
gaps:
  - "Causal confirmation by removal was not performed: the chaos switch is operator surface, and the investigator is read-only. The one observation that would make H1 airtight — faultline_chaos_enabled at 0 with /products back near 1 ms — remains unobserved."
  - "The semantics of extra_latency_ms are not observable from the surface: post-switch durations vary from 3.577 ms to 1297.692 ms, all at or below the 1500 ms setting. The evidence supports a variable injection bounded by the setting, not a constant add; the exact distribution is unknown."
  - "The exemption of /health and /metrics from the injection is sampled, not proven: every sample in the window was sub-millisecond, but E16 shows business paths can also sample fast, so a small number of fast samples cannot prove an exemption under a variable injection."
  - "Who or what issued POST /chaos/enable is outside the telemetry surface: the log records only client 127.0.0.1:49495 on the enable call."
  - "No non-investigator request appears in the log after 10:04:31.775Z, so user impact is directly evidenced only for 10:04:21–10:04:31 (six slow user requests); impact after that is inferred from investigator probes, which remained slow through 10:12:36Z."
  - "Only three triage lenses exist (infra-process, software-defect, interfaces); load-saturation was nonetheless tested as H3 from telemetry, and the lab target has no external provider or database per docs/lab.md, so third-party and data-db domains have no surface here to inspect."
usage:
  model: claude-fable-5
  tokens: 1462132
  wall_clock_seconds: 461
---

# Storewide shop slowness — internal chaos latency switch enabled

## Summary

Root cause identified: an internal chaos degradation switch was turned on at
2026-11-03T10:04:21.625Z (POST /chaos/enable, request_id 082f57bd684c) with
`failure_rate 0.0` and `extra_latency_ms 1500`, and it is still on at conclusion
(`faultline_chaos_enabled 1`, no `chaos_disabled` event). It injects variable extra
latency — observed 3.6 ms to 1298 ms, bounded by the 1500 ms setting — into business
paths (`/products`, `/orders`) while responses stay complete and correct (all 200/201,
zero exceptions). Sampled `/health` and `/metrics` requests stayed under 1 ms
throughout, which is why health checks look green while every shop page crawls. All six
non-investigator requests after the switch were slow; investigator probes confirm the
degradation is live at 10:12:36Z. Confidence is high: the mechanism marker, the sharp
onset bracketing it, a live fast-control/slow-business probe pair, and the exclusion of
code-defect and saturation alternatives all align. The one unobserved confirmation is
removal (switch off, latency back to baseline) — the investigator cannot toggle the
switch.

## Timeline

- **10:04:15.531Z** — process start, faultline 0.1.0, the only startup in the log (E11).
- **10:04:16–10:04:18Z** — user traffic fast: 0.9–12 ms, e.g. `/products` in 1.278 ms (E3).
- **10:04:21.625Z** — configuration-change marker: chaos mode enabled, latency-only,
  1500 ms (E1), via `POST /chaos/enable -> 200` from 127.0.0.1 (E14), one call ever (E15).
- **10:04:24.986Z** — first user request after the switch: `/products` in 1297.692 ms,
  still 200 (E4).
- **10:04:24–10:04:31Z** — user business traffic slow: 187–1298 ms across `/products`,
  `/products/{id}`, `/orders` (E4, E5), with one fast outlier at 3.577 ms (E16). Last
  non-investigator request at 10:04:31.775Z.
- **10:04:40Z** — human complaint raised (`startsAt`).
- **10:05:06Z** — investigation start (trigger latency 26 s).
- **10:05:07Z** — baseline: `/health` 0.869 ms (E8), `/metrics` 0.6 ms (E18), gauge
  `faultline_chaos_enabled 1` (E2), zero exceptions (E9), all counters 200/201 (E10).
- **10:06:41–10:07:12Z** — lens probes: `/products` 1.17 s with adjacent `/health`
  1.3 ms (E6, E7); uptime monotonic, RSS flat (E17); gauge still 1 (E19).
- **10:12:36Z** — final probe: `/products/1` complete body in 0.896 s (E13).
- **10:12:47Z** — concluded. No `chaos_disabled` event observed at any point.

## Investigation

Complaint object (manual trigger, recorded verbatim):

```json
{
  "source": "human",
  "fingerprint": "human-1793700280",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast." },
  "startsAt": "2026-11-03T10:04:40Z"
}
```

Investigation start 2026-11-03T10:05:06Z — trigger latency 26 s. No severity was
stated, so none was recorded.

**Baseline** (10:05:06–10:05:08Z): health 200 in 2.5 ms, metrics clean of exceptions,
all request counters 200/201, chaos gauge at 1, log tail showing the 10:04:21.625Z
chaos marker with a latency jump immediately after it.

**Triage** — three lenses in parallel, each blind to the others: infra-process,
software-defect, interfaces. All three converged on the same mechanism marker. The
software-defect lens found a fully clean error surface and slow-but-correct bodies; the
interfaces lens found the sharp onset at the marker and the live fast-health/slow-business
probe pair; the infra-process lens confirmed one process, monotonic uptime, flat RSS,
and the still-on gauge.

**Deep-dive** — skipped: the triage evidence for H1 was deterministic and complete
(mechanism marker, before/after bracket, live probes, current gauge state), so the
hypothesis list went straight to the judge.

**Judge** — adversarial, evidence-only: H1 validated (mechanism marker and predicted
behavior change confirmed, alternatives excluded), H2 and H3 invalidated. The judge
imposed three limits, kept in this report: the injection is variable rather than a
constant 1500 ms add (E16); the health/metrics exemption is sampled, not proven; and
confirmation by removal is the single missing piece of settling evidence. All three are
recorded under Gaps.

## Hypotheses

### H1 — internal degradation switch injects latency (validated)

An internal chaos switch, enabled at 10:04:21.625Z with `failure_rate 0.0` and
`extra_latency_ms 1500`, injects extra latency into business-path requests while
sampled health/metrics requests stay fast. For: the target itself declares the
mechanism (E1) tied by request_id to the operator call (E14, E15); the gauge reads 1 at
start and mid-investigation (E2, E19); `/products` goes from 1.278 ms (E3) to
1297.692 ms (E4) across an 8-second bracket around the marker; `/orders` is slow too
(E5); the degradation is live during the investigation with a sub-millisecond adjacent
`/health` control (E6, E7) and fast `/health`/`/metrics` log lines (E8, E18). Against,
as nuance: one post-switch request took 3.577 ms (E16), so the injection is variable
and bounded by the setting, not a constant add. Judge: validated.

### H2 — software defect (invalidated)

No evidence supports it: zero exception samples (E9), only 200/201 statuses (E10), a
slow response that is complete and well-formed (E13), a clean single start (E11), and a
slowdown uniform across distinct routes (E4, E5) — not the per-input failure shape of a
code defect. Judge: invalidated. Revival condition: business-path latency that stays
high while `faultline_chaos_enabled` reads 0.

### H3 — load saturation (invalidated)

No evidence supports it: 13 requests total in the whole process life (E10), flat peak
RSS across scrapes (E12, E17), sub-millisecond `/health` during the slow period (E8),
and a step onset at a logged switch event (E3 vs E4) rather than a ramp, on a process
that never restarted (E11). Judge: invalidated.

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Watch for a `chaos_disabled` event or the gauge flipping to 0, then re-read
  `/products` latency. Business paths back near 1 ms confirms causality by removal;
  latency that stays high revives H2.
- Trace who or what issued `POST /chaos/enable` at 10:04:21.626Z from
  127.0.0.1:49495 — operator shell history, deploy or automation logs. That surface is
  outside konan's contract.
- Keep sampling `/products` or `/orders` (not `/health`) for user-facing latency while
  the switch is on — health checks are blind to this incident shape.

## Gaps

Elaborated from the frontmatter list:

1. **No confirmation by removal.** The switch is operator surface; the read-only
   investigator cannot turn it off. The judge named the single settling observation —
   gauge at 0 with business latency back at baseline — and it remains unobserved.
2. **Injection semantics unknown.** Post-switch durations span 3.577–1297.692 ms, all
   at or below 1500 ms. A randomized injection bounded by the setting fits; the surface
   cannot prove the distribution.
3. **Health/metrics exemption is sampled.** Every `/health` and `/metrics` sample in
   the window was sub-millisecond, but E16 proves fast samples occur on injected paths
   too, so the exemption is probable, not proven.
4. **Operator identity out of reach.** Only `client 127.0.0.1:49495` is logged for the
   enable call.
5. **User impact window is narrow.** Direct user-traffic evidence of slowness covers
   10:04:21–10:04:31Z (six requests); after that only investigator probes exist, and
   they stayed slow through 10:12:36Z.
6. **Lens coverage.** Three lenses exist and all ran; load-saturation was tested as H3
   from telemetry, and third-party/data-db domains have no surface on this target
   (docs/lab.md, "Known gaps of this lab").
