---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-total-outage
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-19T03:24:04Z
  concluded: 2026-08-19T03:30:23Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "The faultline process exited (CRITICAL 'exiting with code 1') immediately after a request to /simulate/crash and did not restart; with no process listening on port 8000, every request fails at the TCP layer before any HTTP response — including error pages — for all traffic, not just the investigator's probes."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:23:47.298Z"
    quote: "{\"ts\": \"2026-08-19T03:23:47.298Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:23:51.246Z"
    quote: "{\"ts\": \"2026-08-19T03:23:51.246Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"18a0c38ec73a\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 0.842}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:23:53.305Z"
    quote: "{\"ts\": \"2026-08-19T03:23:53.305Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"d43a52c64f11\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.826}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:23:53.807Z (final line in file)"
    quote: "{\"ts\": \"2026-08-19T03:23:53.807Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"d43a52c64f11\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E5
    type: probe
    source: "GET /health @ 2026-08-19T03:24:24Z request_id=konan-1787109864-41700"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000190s request_id=konan-1787109864-41700"
  - id: E6
    type: probe
    source: "GET /products @ 2026-08-19T03:24:30Z request_id=konan-1787109870-41708"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000195s request_id=konan-1787109870-41708"
  - id: E7
    type: probe
    source: "GET /metrics @ 2026-08-19T03:24:30Z request_id=konan-1787109870-41714"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000204s request_id=konan-1787109870-41714"
  - id: E8
    type: log
    source: "lab/logs/app.log directory listing @ 2026-08-19T03:27:30Z"
    quote: "-rw-r--r--@ 1 lyudmylan staff 3182 Aug 19 06:23 lab/logs/app.log"
  - id: E9
    type: probe
    source: "GET /health @ 2026-08-19T03:27:30Z request_id=konan-1787110050-41791"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000182s request_id=konan-1787110050-41791"
gaps:
  - "OS-level process/port confirmation (ps, lsof, supervisor status) is outside the investigator's surface contract (docs/lab.md: probes + lab/logs/app.log + /metrics only) — permanently unavailable in this environment, not merely unattempted. The adversarial judge (two rounds) held H1 at 'inconclusive' specifically because of this structural gap: the crash-trigger log line, the CRITICAL exit log, and connection refusal on every probed endpoint checked twice 3m37s apart with zero log growth in between are all consistent with 'process died, never restarted' and none of them independently prove it at the OS level."
  - "No telemetry exists from before the captured process lifetime — app.log's earliest line is the 03:23:47.298Z startup marker, and no rotated backups (app.log.1-.3) are present. The complaint's framing ('fine ten minutes ago') could not be independently verified or refuted beyond the ~6 seconds of healthy traffic (E1-E2) captured before the crash trigger (E3)."
  - "interfaces and software-defect triage lenses were not spawned as separate agents. Baseline evidence already showed total TCP connection refusal on every probed endpoint (not a partial/gateway-style failure and not a per-route response of any kind), which falls outside both lenses' signature shapes — those require a live listener returning statuses. Accepted as a blind spot in the sense that no independent agent re-confirmed this exclusion; recorded here rather than silently skipped."
usage:
  model: claude-sonnet-5
  tokens: 2037711
  wall_clock_seconds: 379
---

# Shop-wide outage: faultline process crashed and did not restart

## Summary

**Inconclusive** (evidence ceiling reached, not evidence absence). The shop is down for
everyone because nothing is listening on port 8000 — every probed endpoint (`/health`,
`/products`, `/metrics`) fails to connect at the TCP layer (curl exit 7, ~0ms, no HTTP
response at all), which matches the complaint's "not even an error page" precisely: a
dead process cannot serve even a 500. The log shows a request to `/simulate/crash`
immediately followed by a CRITICAL log line announcing the process's own exit, and
nothing else has been logged since — no restart, no further traffic — across a check
window spread 3m37s apart. This is a single, coherent, uncontradicted account. It falls
short of a fully validated verdict only because this investigator's surface contract
(read-only probes, `lab/logs/app.log`, `/metrics`) cannot obtain OS-level proof that the
process is actually gone (`ps`/`lsof` are out of contract) — a structural limit, not a
sign of competing evidence. Two independent adversarial judge rounds confirmed the same
account and confirmed the same residual gap. Confidence is high; certainty, by the
letter of what this investigator is allowed to check, is not reachable here.

## Timeline (UTC)

- **03:23:47.298** — faultline process starts (E1).
- **03:23:48–03:23:51** — six requests succeed normally: `/health` x2, `/products`,
  `/products/1`, `POST /orders`, `GET /orders` (E2 is the last of these).
- **03:23:53.305** — `GET /simulate/crash -> 200` (E3) — an eval/operator-surface
  request, not investigator traffic: its `request_id` (`d43a52c64f11`) does not match
  the `konan-<epoch>-<pid>` stamp this investigation's own probes carry, and it precedes
  this investigation's first probe by ~31 seconds. The outage predates the investigation.
- **03:23:53.807** — CRITICAL: "crashing now: exiting with code 1" (E4). Last line in
  the log file.
- **03:24:04** — investigation start (per the konan trigger stamp).
- **03:24:24–03:24:30** — `/health`, `/products`, `/metrics` all refuse connection
  (E5, E6, E7).
- **03:27:30** — re-check: log file unchanged (same size/mtime/last line, E8); `/health`
  still refuses connection (E9). No restart-then-crash cycle surfaced in the 3m37s gap.

## Investigation

Baseline (surface contract §Running the lab / §investigator's surface): a single probe
of `/health` failed to connect at all — before checking anything else — which is
already an anomaly strong enough to redirect straight at process lifecycle. `/products`
and `/metrics` were probed next specifically to rule out the healthy-monitoring trap
(a live app with only `/health` broken) and a plain misrouted-request explanation
(single bad path) — both failed identically, which is evidence of a dead listener, not
a single-route problem. The log tail (baseline's third leg) supplied the causal
narrative directly: healthy traffic, an explicit crash trigger, a CRITICAL exit log,
silence.

Given that shape, `interfaces` and `software-defect` lenses were judged excluded by
evidence rather than spawned (see Gaps) — both presume a live process still answering
requests with some status code, and nothing here does. `infra-process` is the only
domain this evidence fits, and the baseline evidence for it was already deterministic
(a crash-lifecycle event immediately followed by connection refusal), so deep-dive was
skipped per protocol and the single hypothesis (H1) went straight to judge.

**Judge round 1** (evidence E1–E7 equivalent): verdict inconclusive. Flagged that E4 is
the process's own self-report of intent to exit, not an OS-confirmed death; that "no
restart logged" only proves no restart wrote a log line, not that none occurred; and
that a ~30s gap between predicted crash and first probe was unmonitored. Named the
settling evidence as an OS-level process/port check (`ps`/`lsof`).

**Follow-up round**: gathered E8/E9 — a second log-file state check and a second
`/health` probe, 3m37s after the crash, both unchanged/still-refused. Judge round 2:
narrowed the unmonitored-window gap but held the verdict at inconclusive, explicitly
naming the OS-level check as a permanent, structural limit of this investigator's
contract (docs/lab.md) rather than an open action item — more probes or log reads of
the same kind cannot close it. That is the honest evidence ceiling for this incident
class in this environment, and further budget would not change it, so the investigation
concludes here rather than looping.

## Hypotheses

### H1 — process crash, no observed restart (infra-process)

**Statement**: the process was killed by its own `/simulate/crash` handler and never
came back; the resulting absent listener explains total, response-less failure on every
endpoint.

**State**: inconclusive.

**For**: E1–E2 establish the process was healthy immediately beforehand. E3 shows the
crash-trigger request. E4 is the process's own CRITICAL exit announcement, the last
line ever written to the log. E5–E7 show every probed endpoint refusing TCP connection
outright (not an HTTP error — no listener at all), immediately after E4. E8–E9, taken
3m37s later, show zero log growth and continued connection refusal, arguing against a
silent restart-and-crash-again cycle inside that window.

**Against**: none found. No evidence contradicts this account; the gap is an absence of
independent OS-level confirmation, not a competing signal.

## Safe next steps

- Re-run `scripts/probe.sh /health` periodically (read-only) to see whether the process
  ever restarts on its own; a fresh `startup` event in `lab/logs/app.log` would move
  this hypothesis toward validated (or reveal a restart-crash loop, moving it toward a
  related but distinct hypothesis).
- If OS-level confirmation is ever brought into scope for a future investigation
  (outside this investigator's current contract), a single `ps`/`lsof`-style check
  against port 8000 would settle H1 outright.
- Re-read `lab/logs/app.log` for a subsequent startup marker before assuming the
  service needs manual intervention — this journal makes no remediation claim.

## Gaps

- OS-level process/port confirmation is outside the investigator's surface contract and
  permanently unavailable here — see the corresponding entry in the machine core for
  detail on why this specifically caps H1 at inconclusive.
- No telemetry predates the captured process lifetime (log starts at the 03:23:47
  startup marker; no rotated backups present), so the complaint's "fine ten minutes ago"
  framing is untested beyond the ~6 seconds of pre-crash traffic actually captured.
- `interfaces` and `software-defect` lenses were not independently spawned; the decision
  to exclude them rested on this investigator's own reading of the baseline (total,
  response-less connection failure on every route), not on a second agent's
  confirmation.
