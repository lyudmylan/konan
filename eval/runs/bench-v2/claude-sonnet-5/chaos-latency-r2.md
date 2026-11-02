---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-latency-chaos-switch
  trigger: "manual (/konan adapter; human report, fingerprint human-1793647539; trigger latency startsAt(2026-11-02T19:25:39Z) -> started(2026-11-02T19:25:43Z) = 4 s)"
  complaint: |-
    {"source": "human", "fingerprint": "human-1793647539", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."}, "startsAt": "2026-11-02T19:25:39Z"}
  started: "2026-11-02T19:25:43Z"
  concluded: "2026-11-02T19:34:39Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos/degradation switch inside the faultline process was turned on at 2026-11-02T19:25:21.036Z (extra_latency_ms: 1500, failure_rate: 0.0), injecting variable added latency on the business routes /products, /products/{id}, and /orders while leaving /health and /metrics unaffected and producing zero errors."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "A chaos/degradation switch inside the faultline process was enabled at 2026-11-02T19:25:21.036Z with extra_latency_ms: 1500 and failure_rate: 0.0 (E3); every request to /products, /products/{id}, and /orders issued afterward still returned 200 but took far longer than its pre-toggle baseline (0.8-1.9 ms before E3; 77.8-1337.2 ms immediately after, and 994.3 ms still elevated 8.5 minutes later) (E2, E4, E5, E10), while /health stayed sub-millisecond throughout (E7) and faultline_chaos_enabled read 1 on every later scrape (E6) — matching the complaint's \"every page... painfully slow... nothing errors out... health checks are green and fast\" exactly."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E10]
    evidence_against: []
  - id: H2
    statement: "Resource saturation (CPU, memory, or connection/worker-pool exhaustion) in the faultline process caused the slowdown, rather than an application-level toggle."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E9]
  - id: H3
    statement: "A code-level defect (an inefficient loop, a data-dependent slow path, or an unhandled exception) in a specific business-route handler caused the slowdown."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E5, E8]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:25:14.913Z — process startup marker"
    quote: |-
      {"ts": "2026-11-02T19:25:14.913Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:25:15.864Z-17.976Z — pre-toggle baseline traffic, all sub-2 ms"
    quote: |-
      {"ts": "2026-11-02T19:25:15.864Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "212ed331de23", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.833, "client": "127.0.0.1:60510"}
      {"ts": "2026-11-02T19:25:16.918Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "cd0e4ec330f4", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.87, "client": "127.0.0.1:60511"}
      {"ts": "2026-11-02T19:25:17.976Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "29f9b4f05a35", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.925, "client": "127.0.0.1:60512"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:25:21.036Z-21.037Z — the toggle event and its own access line, same request_id"
    quote: |-
      {"ts": "2026-11-02T19:25:21.036Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "161339aa2f32", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
      {"ts": "2026-11-02T19:25:21.037Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "161339aa2f32", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.19, "client": "127.0.0.1:60513"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:25:23.176Z-26.741Z — first three post-toggle business requests, all 200, all slow"
    quote: |-
      {"ts": "2026-11-02T19:25:23.176Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "3f906dd672a3", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 77.812, "client": "127.0.0.1:60514"}
      {"ts": "2026-11-02T19:25:25.565Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b2bf29321a30", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1327.312, "client": "127.0.0.1:60515"}
      {"ts": "2026-11-02T19:25:26.741Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "8ec5b6d08731", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 111.109, "client": "127.0.0.1:60516"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:25:27.999Z-32.796Z — next three post-toggle business requests, all 2xx, all slow"
    quote: |-
      {"ts": "2026-11-02T19:25:27.999Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "548004c36afd", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 192.91, "client": "127.0.0.1:60517"}
      {"ts": "2026-11-02T19:25:30.391Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "9eaaa49b17a9", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1329.528, "client": "127.0.0.1:60518"}
      {"ts": "2026-11-02T19:25:32.796Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "ddd5e2f32bbd", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1337.151, "client": "127.0.0.1:60519"}
  - id: E6
    type: metric
    source: "/metrics @ request_id konan-1793647577-1649 (2026-11-02T19:26:17.306Z)"
    quote: |-
      faultline_chaos_enabled 1
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:26:14.045Z — investigator /health probe, well after the toggle"
    quote: |-
      {"ts": "2026-11-02T19:26:14.045Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793647574-1642", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.863, "client": "127.0.0.1:60540"}
  - id: E8
    type: metric
    source: "/metrics @ request_id konan-1793647577-1649 (2026-11-02T19:26:17.306Z); independently reconfirmed by the software-defect triage lens against the complete 26-line lab/logs/app.log history (process start to its re-probe)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      (no sample lines beneath the TYPE header — the counter has never incremented; zero unhandled_exception/simulated_exception log events anywhere in app.log)
  - id: E9
    type: metric
    source: "infra-process triage lens — two /metrics re-probes approximately 70 s apart, spanning the slowdown window"
    quote: |-
      process_uptime_seconds 62.4048690830823 (first read) -> 132.47 (second read, ~70 s later; monotonic, no reset)
      process_max_rss_bytes 47644672 (unchanged across both reads)
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:33:51.761Z — confirming re-probe of the same route/input as E2's /products/1 line, 8.5 minutes after the toggle"
    quote: |-
      {"ts": "2026-11-02T19:33:51.761Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1793648030-1880", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 994.257, "client": "127.0.0.1:60575"}
gaps:
  - "The actor and channel behind the toggle flip (E3, request_id 161339aa2f32) are outside the surface: docs/lab.md gives the investigator no identity/audit trail for who or what called the operator-side /chaos/enable — the log confirms the toggle fired but not who flipped it."
  - "The injected-latency distribution (fixed vs. jittered) could not be fully characterized: observed post-toggle durations ranged 77.8-1337.2 ms against a configured extra_latency_ms of 1500 (E3, E4, E5, E10), consistent with randomized/jittered injection, but the exact algorithm is ground truth inside faultline's own code, which docs/lab.md places outside investigator reach."
  - "No deep-dive round was run: triage evidence (E1-E9) was already deterministic — a named mechanism in a log line, a clean before/after timing match, and three independent lenses finding no competing explanation — so the investigation went straight from triage to the judge per the budget rule for evidence that is already complete; one orchestrator-run confirming probe (E10) settled the judge's sole residual caveat (latency-magnitude variability) without needing a dedicated deep-dive agent."
usage:
  model: claude-sonnet-5
  tokens: 3376881
  wall_clock_seconds: 536
---

# Shop-wide slowness: a chaos/degradation switch injecting latency on business routes

## Summary

Verdict: **root-cause-identified**. At 2026-11-02T19:25:21.036Z an internal
chaos/degradation switch inside the faultline process was turned on, configured with
`extra_latency_ms: 1500` and `failure_rate: 0.0` (E3). From that instant, every
probed business route — `/products`, `/products/{id}`, `/orders` — kept returning
`200`/`201` but took 50-1800x longer than its pre-toggle baseline (E2 vs. E4, E5),
while `/health` stayed sub-millisecond throughout (E7) and `/metrics` confirmed the
switch still on (`faultline_chaos_enabled 1`, E6). A confirming probe 8.5 minutes
later showed the slowdown still active (E10). This matches the complaint precisely:
"every page... painfully slow... nothing errors out... health checks are green and
fast." Resource saturation and a code-level defect were both tested and invalidated
(H2, H3) — no RSS growth or uptime reset (E9), zero exceptions anywhere in the log
history (E8), and the slowdown hit unrelated routes simultaneously rather than
concentrating on one input (E4, E5 vs. E2). Confidence: high — the toggle's own
logged parameters (zero error rate, nonzero added latency) predict exactly the
symptom reported, and the prediction held on a fresh probe taken minutes later.

## Timeline

- **2026-11-02T19:25:14.913Z** — faultline process starts (E1).
- 2026-11-02T19:25:15.864Z-17.976Z — pre-toggle baseline: `/products`, `/products/1`,
  `POST /orders` all complete in under 2 ms (E2).
- **2026-11-02T19:25:21.036Z — the toggle: chaos mode enabled, `extra_latency_ms:
  1500`, `failure_rate: 0.0` (E3).**
- 2026-11-02T19:25:23.176Z-32.796Z — six post-toggle business requests, all 2xx,
  durations 77.8-1337.2 ms (E4, E5) — up to ~1600x the pre-toggle baseline.
- 2026-11-02T19:25:39Z — complaint `startsAt` (human report).
- 2026-11-02T19:25:43Z — investigation starts (trigger latency 4 s).
- 2026-11-02T19:26:14.045Z — investigator `/health` probe, still sub-millisecond
  (E7).
- 2026-11-02T19:26:17.306Z — `/metrics` scrape: `faultline_chaos_enabled 1` (E6);
  `http_exceptions_total` has no samples (E8).
- 2026-11-02T19:33:51.761Z — confirming re-probe: `/products/1` still slow at
  994.257 ms, 8.5 minutes after the toggle (E10).
- 2026-11-02T19:34:39Z — investigation concludes.

## Investigation

**Baseline** (19:26:14-17Z): `/health` fast and green (E7); `/metrics` showed chaos
mode on and elevated per-path average latency on every business route, with an empty
exception counter; the log tail already contained the toggle event and the clean
before/after timing split (E1-E5). The baseline diff was not clean — it pointed
straight at one mechanism — so triage fanned out across all three lenses rather than
closing early.

**Triage**: three lenses spawned in parallel, each blind to the others, given only
the lens file, the surface contract, the verbatim complaint, and this baseline.
*Interfaces* named the toggle itself as a runtime-config flip whose logged payload
(`failure_rate: 0.0`, `extra_latency_ms: 1500`) predicts exactly "slow, not
erroring." *Infra-process* found no restart, no uptime reset, and flat `max_rss`
across the window (E9), and noted that `/health` stayed fast through the slowdown —
arguing against a process-wide resource cause. *Software-defect* found zero
exceptions across the full log history (E8) and showed the slowdown hit unrelated
routes simultaneously and the same route/input inconsistently over time — the
opposite of a deterministic per-input code defect.

**Deep-dive**: skipped. All three lenses converged on one mechanism with no
competing explanation surviving their own domain's disconfirming checks, so the
hypothesis list's evidence was already deterministic and complete per the budget
rule. One cheap orchestrator probe (E10) settled the single open question — whether
the slowdown was still live and whether its magnitude was consistent — rather than
spawning a dedicated deep-dive agent.

**Judge** (fresh subagent, claims + verbatim evidence only): H1 validated, citing
E3's named mechanism and the E2->E4/E5 before/after match as "a direct, named
mechanism, not an inference"; it flagged one residual caveat — observed durations
(77.8-1337.2 ms) don't uniformly match the configured 1500 ms, suggesting jittered
rather than fixed injection. H2 invalidated on E7 (process-wide resource exhaustion
would have also slowed `/health`) and E9 (flat RSS, no restart). H3 invalidated on
E8 (zero exceptions), E4/E5 (cross-route synchrony incompatible with a single-route
defect), and E2 vs. E4's `/products/1` entries (same input, order-of-magnitude
different latency at different times — incompatible with a deterministic
data-dependent slow path).

**Probe accounting**: investigator traffic this round — `/health` x1, `/metrics`
x2, `/products/1` x1 (E7, E6/E8, E10), all `konan`-stamped. None of my probes
triggered the slowdown; the toggle (E3) predates my first probe by over four
minutes, and the six earliest slow requests (E4, E5) are all unstamped —
pre-existing non-investigator traffic.

## Hypotheses

### H1 — validated (root cause): chaos/degradation switch injecting latency

E3 names the mechanism directly: a logged `chaos_enabled` event with
`failure_rate: 0.0` and `extra_latency_ms: 1500`. The before/after timing brackets
it exactly — sub-2ms baseline (E2) immediately followed by 77.8-1337.2 ms business
requests (E4, E5), still elevated at 994.3 ms 8.5 minutes later (E10) — while
`/health` never slowed (E7) and `/metrics` kept reading the switch as on (E6). The
zero configured failure rate explains "nothing errors out"; the switch being
business-path-scoped (and not touching `/health`/`/metrics`) explains "health
checks are green and fast." One loose end the judge raised — observed latency
(77.8-1337.2 ms) varies rather than clustering tightly at 1500 ms — doesn't break
the mechanism; it says the injection is variable/jittered rather than a fixed
add-on, which E10's later 994.3 ms reading is consistent with.

### H2 — invalidated: resource saturation

With zero evidence_for, this stands only if the evidence_against fails to land — it
doesn't. E7 shows `/health` staying sub-millisecond throughout the slowdown window;
a process genuinely starved on CPU or memory would be expected to slow a trivial,
same-process endpoint too. E9 shows `process_max_rss_bytes` flat across the window
with `process_uptime_seconds` climbing monotonically — no restart, no memory growth.

### H3 — invalidated: code-level defect in a specific route

E8 rules out the unhandled-exception sub-case outright: zero exceptions anywhere in
the log's full history. E4 and E5 rule out a single-route defect: `/products`,
`/products/{id}`, and `/orders` — three different handlers — all slowed in the same
narrow window, which a defect confined to one route's code would not produce. E2
vs. E4's `/products/1` entries (1.87 ms before the toggle, 111.1 ms after, same
route and same input) rule out a deterministic data-dependent slow path, which
would reproduce the same cost for the same input regardless of when it's called.

## Safe next steps

- Treat `faultline_chaos_enabled` remaining at `1` and elevated
  `http_request_duration_seconds` on `/products`, `/products/{id}`, and `/orders` as
  continued user impact; non-`konan`-stamped request ids in the access lines
  distinguish real user traffic from investigator probes (E4, E5, E10 for the
  pattern to watch).
- The switch and its effect are fully characterized on the read-only surface;
  turning it off is an operator action (`scripts/scenario.sh chaos-off`) outside
  this investigation's read-only mandate — no fix is proposed here.
- If the exact actor or timing behind the `/chaos/enable` call is needed, that
  sits in the operator/eval surface outside `docs/lab.md` and was not retrievable
  from here.

## Gaps

Elaborated in the frontmatter list: the actor and channel behind the toggle flip
are outside the investigator's surface; the exact shape of the injected-latency
distribution (fixed vs. jittered) is ground truth inside faultline's own code,
placed out of reach by `docs/lab.md`; and no dedicated deep-dive agent was spawned
because triage evidence was already deterministic and complete, with one cheap
orchestrator probe settling the judge's sole residual caveat.
