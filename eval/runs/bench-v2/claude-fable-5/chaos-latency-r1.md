---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-slow-pages
  trigger: "manual (/konan human-report; fingerprint human-1793634006; startsAt 2026-11-02T15:40:06Z; investigation start 2026-11-02T15:40:16Z; trigger latency 10s)"
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-02T15:40:16Z
  concluded: 2026-11-02T15:46:24Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The target's internal chaos degradation switch was enabled at 2026-11-02T15:39:37.256Z with extra_latency_ms=1500 and failure_rate=0.0 and is still on: it injects up to ~1.5 s of random latency into every shop endpoint, injects zero errors, and exempts /health — users see latency-only slowness while health checks stay green."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos degradation switch, enabled at 15:39:37.256Z with extra_latency_ms=1500 and failure_rate=0.0, adds up to ~1.5 s of random latency to shop endpoints with no injected errors; /health is exempt; the switch is still active."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "A defect in the shop's own code produces the slowness (wrong behavior or unhandled errors for some inputs)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E2, E3, E4]
  - id: H3
    statement: "A process lifecycle failure (crash loop, restart, or hang) degrades service."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E12, E7]
  - id: H4
    statement: "Demand exceeds capacity (load saturation): queues back up and all requests slow down."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E11, E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:39:37.256Z"
    quote: |-
      {"ts": "2026-11-02T15:39:37.256Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "e8435b1f3c7b", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:39:32.078Z"
    quote: |-
      {"ts": "2026-11-02T15:39:32.078Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "a4cacc54dfef", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.104, "client": "127.0.0.1:59204"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:39:40.730Z"
    quote: |-
      {"ts": "2026-11-02T15:39:40.730Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "af99e9f2b314", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1408.842, "client": "127.0.0.1:59208"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:39:45.888Z"
    quote: |-
      {"ts": "2026-11-02T15:39:45.888Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "da644c648684", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1078.089, "client": "127.0.0.1:59211"}
  - id: E5
    type: metric
    source: "/metrics @ 2026-11-02T15:40:36Z (request_id konan-1793634036-95487)"
    quote: faultline_chaos_enabled 1
  - id: E6
    type: metric
    source: "/metrics @ 2026-11-02T15:40:36Z (request_id konan-1793634036-95487) — scrape contains the header lines and zero series"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E7
    type: probe
    source: "/health @ request_id konan-1793634036-95482 (2026-11-02T15:40:36Z)"
    quote: |-
      {"status":"ok","uptime_seconds":65.05295387492515}
      -- HTTP 200 in 0.001599s request_id=konan-1793634036-95482
  - id: E8
    type: probe
    source: "/products/1 @ request_id konan-1793634114-95518 (2026-11-02T15:41:55Z)"
    quote: "-- HTTP 200 in 1.454581s request_id=konan-1793634114-95518"
  - id: E9
    type: probe
    source: "/products @ request_id konan-1793634114-95513 (2026-11-02T15:41:54Z)"
    quote: "-- HTTP 200 in 0.152450s request_id=konan-1793634114-95513"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:39:31.306Z (the only startup event in the complete log)"
    quote: |-
      {"ts": "2026-11-02T15:39:31.306Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E11
    type: metric
    source: "/metrics @ 2026-11-02T15:40:36Z (request_id konan-1793634036-95487)"
    quote: process_max_rss_bytes 47153152
  - id: E12
    type: metric
    source: "/metrics @ 2026-11-02T15:40:36Z (request_id konan-1793634036-95487)"
    quote: process_uptime_seconds 65.66705345897935
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-02T15:40:36Z (request_id konan-1793634036-95487)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
gaps:
  - "Caller attribution: one successful POST /chaos/enable exists (E13) and its request_id (e8435b1f3c7b, E1) is not an investigator id, but the telemetry surface carries no identity or audit trail, so who flipped the switch cannot be determined from this surface. The mechanism is proven; the actor is not."
  - "The interfaces, third-party, and data-db triage lenses were not spawned: excluded with evidence — the surface contract (docs/lab.md, 'Known gaps of this lab') states the target has no real database, no third-party dependency, and no distributed topology, and every recorded status is 200/201 (E13)."
  - "No CPU or queue-depth metric exists on the surface, so the load-saturation kill rests on near-zero demand (E13: 13 requests over the process lifetime), flat RSS (E11), and the sub-millisecond health path (E7) rather than a utilization curve across the onset."
usage:
  model: claude-fable-5
  tokens: 947226
  wall_clock_seconds: 368
---

# Shop-wide slow pages with green health checks — chaos degradation switch (latency-only)

## Summary

Root cause identified. At 2026-11-02T15:39:37.256Z the target's internal chaos
degradation switch was enabled with `extra_latency_ms: 1500` and `failure_rate: 0.0`
(E1), and it is still on (E5). It injects a random delay of up to ~1.5 s into every
shop endpoint — request durations stepped from 0.8–12 ms (E2) to 48–1409 ms (E3, E4)
at the marker — while injecting zero errors (`failure_rate: 0.0`; all statuses 200/201,
E13; no exceptions, E6) and exempting `/health` (0.5–1.6 ms throughout, E7). This
reproduces the complaint exactly: every page slow, nothing errors out, health checks
green and fast. Confidence is high: the onset is a step at one configuration marker,
the magnitude is capped by the configured value, and competing hypotheses are
invalidated by direct evidence.

## Timeline

- 15:39:31.306Z — process start, faultline 0.1.0, the only startup event (E10).
- 15:39:32–15:39:34 — normal traffic: durations 0.8–12 ms, statuses 200/201 (E2).
- 15:39:37.256Z — **configuration-change marker**: `chaos_enabled`, `failure_rate: 0.0`,
  `error_status: 503`, `extra_latency_ms: 1500` (E1).
- 15:39:40–15:39:49 — user traffic slow: 48–1409 ms, still all 200/201 (E3, E4).
- 15:40:06Z — human complaint raised (`startsAt`).
- 15:40:16Z — investigation start (trigger latency 10 s).
- 15:40:36Z — baseline: `/health` 200 in 1.6 ms (E7); `faultline_chaos_enabled 1` (E5);
  no exception series (E6).
- 15:41:54–15:41:55Z — business-surface probes: `/products` 200 in 152 ms (E9),
  `/products/1` 200 in 1455 ms (E8) — degradation ongoing.
- 15:46:24Z — concluded.

## Investigation

Complaint object, verbatim as synthesized by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1793634006",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast." },
  "startsAt": "2026-11-02T15:40:06Z"
}
```

Investigation start: 2026-11-02T15:40:16Z (trigger latency 10 s).

- **Baseline**: health, metrics snapshot, and the complete log since startup (the log
  covers the whole process lifetime). The baseline itself surfaced the configuration
  marker (E1) and the duration step (E2 vs E3). Per the healthy-monitoring-trap rule,
  the business surface was probed directly: slow (E8, E9) while `/health` stayed
  sub-2 ms (E7).
- **Triage**: two lenses spawned in parallel, blind to each other — software-defect and
  infra-process. The interfaces lens was excluded with evidence (see Gaps). The
  software-defect lens reported no defect signature in its domain (no exceptions, no
  per-input determinism — its re-probe of `/products/1` returned 395 ms against the
  earlier 1455 ms). The infra-process lens reported the switch (E1, E5), the duration
  step, and the health exemption.
- **Deep-dive**: skipped — the triage evidence for H1 was deterministic and complete
  (a logged configuration marker plus a capped, onset-aligned duration step), so the
  hypothesis list went straight to the judge.
- **Judge** (adversarial, evidence-only): H1 validated; H2, H3, H4 invalidated. The
  judge flagged one open point — the evidence proves the mechanism but not the actor —
  recorded under Gaps.

## Hypotheses

### H1 — chaos degradation switch (validated)

An internal operational switch injects latency. For: the marker line itself (E1); the
duration step at the marker (E2 → E3, E4); the switch still reading enabled (E5); the
magnitude cap matching `extra_latency_ms: 1500` (E3: 1408.842 ms; E8: 1454.581 ms,
never above ~1.5 s); zero injected errors matching `failure_rate: 0.0` (E6, E13); and
the `/health` exemption (E7) explaining the green checks. Nothing contradicts it.

### H2 — software defect (invalidated)

Predicts exception or wrong-result evidence, or a deterministic per-input signature.
Against: zero exception series (E6); every route slowed equally in the same band and
all statuses stayed 200/201 (E2, E3, E4); the same input varied 1455 ms → 395 ms.
Code did not change at 15:39:37.256Z; configuration did (E1).

### H3 — process lifecycle failure (invalidated)

Predicts restart markers, uptime resets, or an unresponsive process. Against: exactly
one startup event (E10); monotonic uptime (E12); the process answers `/health` in
1.6 ms (E7) — alive and serving, not crashed or hung.

### H4 — load saturation (invalidated)

Predicts demand exceeding capacity. Against: 13 requests total over the process
lifetime (E13) — near-zero demand; flat peak RSS at ~47 MB (E11); a saturated process
would not serve one route at sub-millisecond speed while others take 1.4 s (E7 vs E8).

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Watch for a `chaos_disabled` event in the log and `faultline_chaos_enabled`
  returning to 0; after that, confirm business-route durations return to the
  single-digit-millisecond baseline (this would also close the judge's residual H2
  caveat).
- Identify who issued the one `POST /chaos/enable` (E13) through an operator-side
  channel (shell history, operator session records) — the telemetry surface carries
  no identity.
- If health checks are meant to represent user experience, note the exemption shape:
  `/health` bypasses the injected latency, so latency-only degradations are invisible
  to the current checks.

## Gaps

1. **Actor attribution.** The switch was flipped by one `POST /chaos/enable` whose
   request id (e8435b1f3c7b) is not an investigator id, but the surface exposes no
   caller identity or audit log. Mechanism proven; actor unknown.
2. **Lenses excluded with evidence.** interfaces / third-party / data-db were not
   spawned: the surface contract states the lab has no database, no third-party
   dependency, and no distributed topology, and the status profile is all-2xx (E13).
3. **No utilization metrics.** The surface has no CPU or queue-depth metric; the
   load-saturation refutation rests on demand counters, flat RSS, and the health
   exemption rather than a utilization curve across the onset.
