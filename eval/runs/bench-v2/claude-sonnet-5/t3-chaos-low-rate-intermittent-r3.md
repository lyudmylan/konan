---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-intermittent-errors-chaos-toggle
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-02T23:26:14Z
  concluded: 2026-11-02T23:30:57Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A degradation switch (chaos mode) was turned on via POST /chaos/enable at 23:25:01.777Z with an 8% failure rate on HTTP 503, and the two observed 503s (GET /orders, GET /products/5) in the following traffic burst are chaos-tagged failures caused directly by that switch."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "Chaos mode injects a randomized 8% failure rate (503) into requests while enabled, producing the two observed 503s and matching the complaint's 'occasional error, works on retry' shape."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E8]
    evidence_against: []
evidence:
  - id: E1
    type: metric
    source: "GET /metrics probe, request_id konan-1793661995-10842 @ 2026-11-02T23:26:35Z"
    quote: "faultline_chaos_enabled 1"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:25:01.777Z"
    quote: "{\"ts\": \"2026-11-02T23:25:01.777Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"7a1b232c0040\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.08, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:25:03.022Z"
    quote: "{\"ts\": \"2026-11-02T23:25:03.022Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"f326c24011f7\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/orders\"}; {\"ts\": \"2026-11-02T23:25:03.022Z\", \"level\": \"INFO\", \"message\": \"GET /orders -> 503\", \"request_id\": \"f326c24011f7\", \"status\": 503, \"duration_ms\": 0.139}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:25:03.092Z"
    quote: "{\"ts\": \"2026-11-02T23:25:03.092Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"3a444bbd110b\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/5\"}; {\"ts\": \"2026-11-02T23:25:03.092Z\", \"level\": \"INFO\", \"message\": \"GET /products/5 -> 503\", \"request_id\": \"3a444bbd110b\", \"status\": 503, \"duration_ms\": 0.132}"
  - id: E5
    type: metric
    source: "GET /metrics probe, two independent reads @ 2026-11-02T23:26:35Z and ~23:28:32Z"
    quote: "http_exceptions_total family present (HELP/TYPE lines) with zero counter lines in either read"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:24:56.901Z (only startup marker in the full log history)"
    quote: "{\"ts\": \"2026-11-02T23:24:56.901Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E7
    type: metric
    source: "GET /metrics probe, two independent reads @ 2026-11-02T23:26:35Z and ~23:28:32Z"
    quote: "process_max_rss_bytes 47054848 (identical on both reads despite the intervening traffic burst)"
  - id: E8
    type: metric
    source: "GET /metrics probe @ 2026-11-02T23:26:35Z"
    quote: "http_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 4; http_requests_total{method=\"GET\",path=\"/orders\",status=\"503\"} 1; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 16; http_requests_total{method=\"GET\",path=\"/products/5\",status=\"503\"} 1"
gaps:
  - "Client-level retry behavior ('works on retry') could not be verified: the surface exposes aggregate request counters and per-request access/warning log lines, not a client-side chain linking one failed attempt to a later successful retry of the same logical operation."
  - "Which users, or how many, hit a 503 could not be determined: the lab surface carries no user or session identifier, only client socket address and request id."
usage:
  model: claude-sonnet-5
  tokens: 1905211
  wall_clock_seconds: 283
---

# Shop: intermittent 503s traced to a chaos-mode toggle, not a defect

## Summary

**Root cause identified.** The occasional shop errors a couple of users reported are two
HTTP 503 responses (`GET /orders`, `GET /products/5`) directly caused by an internal
chaos/degradation switch that was turned on moments earlier (`POST /chaos/enable`,
8% configured failure rate). No code defect, no process crash, no resource saturation,
and no contract/interface fault were found. Impact matches the complaint shape: a small,
probabilistic fraction of requests fail while most succeed — consistent with "most people
notice nothing." Confidence is high: both 503s carry an explicit `chaos_failure` tag with
a matching request id to the failing access line, and no other anomaly was found in any
discipline. One gap: whether a failed request actually succeeded on an immediate retry at
the client level could not be verified from this surface (see Gaps).

## Trigger

Complaint object, as synthesized by the `/konan` adapter from the human report, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1793661969",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-11-02T23:26:09Z"
}
```

Investigation start: `2026-11-02T23:26:14Z`. Trigger latency (`startsAt` → start): 5 seconds.

## Timeline

- `2026-11-02T23:24:56.901Z` (E6) — process start, single startup marker; no restarts
  anywhere in the log history.
- `2026-11-02T23:24:57Z`–`23:24:59Z` — normal baseline traffic (health, products, one
  order), all 200/201.
- `2026-11-02T23:25:01.777Z` (E2) — chaos mode enabled via `POST /chaos/enable`:
  `failure_rate=0.08`, `error_status=503`, `extra_latency_ms=0`. Confirmed still active
  at investigation time: `faultline_chaos_enabled 1` (E1).
- `2026-11-02T23:25:02.836Z`–`23:25:03.316Z` — a ~23-request traffic burst; two requests
  fail with chaos-tagged 503s, interleaved with successes on the same routes:
  - `23:25:03.022Z` (E3) `GET /orders` → 503, tagged `chaos_failure`.
  - `23:25:03.092Z` (E4) `GET /products/5` → 503, tagged `chaos_failure`.
- `23:25:03.316Z`–`23:26:33Z` — quiet gap, no traffic.
- `23:26:33Z` onward — investigator probes only (`konan-*` request ids); health green,
  metrics stable, no further errors observed.

## Investigation

1. **Baseline** — health probe (200, ok), `/metrics` snapshot, and the full `lab/logs/app.log`
   (54 lines — the entire process history). The baseline itself already surfaced the
   `chaos_enabled` marker and the two matching 503s.
2. **Triage (discipline-parallel)** — all three lenses spawned in parallel, each blind to
   the others, given the same baseline:
   - `infra-process`: identified the chaos toggle as the direct cause, confirmed clean
     process lifecycle (one startup marker, no restarts) and no resource saturation
     (flat RSS, no latency growth).
   - `interfaces`: confirmed the config-change marker precedes the failures by ~1s,
     confirmed the observed ~8.7% (2/23) failure rate matches the configured 0.08,
     explicitly deferred classification to `infra-process` since the mechanism is an
     internal switch, not a boundary/contract fault.
   - `software-defect`: confirmed zero unhandled exceptions in two independent `/metrics`
     reads and the full log, confirmed both 503s are explicitly self-tagged
     `chaos_failure` rather than thrown, confirmed no data-dependent (per-input) failure
     shape — ruled out a code defect.
   All three lenses converged on the same single mechanism with no contradicting evidence;
   evidence was already deterministic and complete, so no deep-dive round was needed
   (per the loop's skip rule).
3. **Judge** — one fresh adversarial judge, given only the hypothesis and the verbatim
   evidence (E1–E8), no lens narrative. Verdict: **validated**. The judge noted the
   ~8.7%-vs-8% rate match is weak support on its own (n=23 is a small sample) but found
   the per-request `chaos_failure` tag paired by request id with each 503 (E3, E4) to be
   direct, not merely correlated, causal evidence. The judge flagged one unverified point:
   the complaint's "works on retry" framing has no request-level retry trace in the
   evidence — carried into Gaps below.

## Hypotheses

### H1 — Chaos-mode degradation switch (validated)

Chaos mode, enabled via `POST /chaos/enable` with `failure_rate=0.08`, injects a
randomized 503 into GET requests while active. Both observed 503s in the subsequent
traffic burst carry an explicit `chaos_failure` tag whose request id matches the failing
access log line one-for-one (E3, E4) — not just a time correlation. No alternative
mechanism survived: zero unhandled exceptions (E5), a single clean startup marker with
no restarts (E6), and flat memory with no latency growth (E7) rule out a code defect,
a process crash, and resource saturation respectively. The observed ~8.7% failure rate
in the burst (E8) is directionally consistent with the configured 8% rate, though the
judge correctly notes this alone is weak evidence at n=23 — the request-id-linked tags
(E3, E4) carry the proof.

## Safe next steps

- Re-read `/metrics` (`faultline_chaos_enabled`) periodically to confirm when the switch
  is turned back off — it was still `1` as of this investigation's last probe.
- If the switch is expected to be on (e.g. a scheduled chaos drill), no action is needed;
  if not, this is an operator-surface question (`/chaos`) outside this investigation's
  read-only reach — flag to whoever controls that toggle.
- To confirm user-level retry success (the complaint's "works on retry" claim), a future
  investigation would need request-level client tracing, not just the aggregate counters
  available on this surface.

## Gaps

- Client-level retry behavior ("works on retry") could not be verified: the surface
  exposes aggregate request counters and per-request access/warning log lines, not a
  client-side chain linking one failed attempt to a later successful retry of the same
  logical operation.
- Which users, or how many, hit a 503 could not be determined: the lab surface carries
  no user or session identifier, only client socket address and request id.
