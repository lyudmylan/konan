---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-down-simulate-crash
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-11-02T22:52:01Z
  concluded: 2026-11-02T22:56:04Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A GET /simulate/crash call triggered an intentional process exit (code 1); with no process listening on the port, every request — including the investigator's own health, metrics, and product probes — fails at TCP connect."
  incident_class: infra-process
  cause: process-crashed
hypotheses:
  - id: H1
    statement: "The faultline process exited after a /simulate/crash call, taking the whole service down; the resulting total connection refusal (not an HTTP error) matches a report of pages not loading at all, not even an error page."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:51:46.761Z"
    quote: "{\"ts\": \"2026-11-02T22:51:46.761Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"84e2d6456cb5\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.264, \"client\": \"127.0.0.1:62025\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:51:47.264Z"
    quote: "{\"ts\": \"2026-11-02T22:51:47.264Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"84e2d6456cb5\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E3
    type: probe
    source: "/health, request_id konan-1793659981-9358"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000170s request_id=konan-1793659981-9358"
  - id: E4
    type: probe
    source: "/metrics, request_id konan-1793659986-9364"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000193s request_id=konan-1793659986-9364"
  - id: E5
    type: probe
    source: "/products, request_id konan-1793659987-9369"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000176s request_id=konan-1793659987-9369"
gaps:
  - "scripts/lab.sh status (process/port status via the lab's own operator command) required interactive approval not available in this session; process-down state was inferred from connection-refused on three independent probed paths (E3-E5) rather than a direct process snapshot."
  - "No telemetry covers the ~74s between the crash log line (E2, 22:51:47.264Z) and the first probe (E3, ~22:53:01Z); a restart-then-recrash inside that window cannot be ruled out from the evidence gathered, only a continuously-down process consistent with no startup line appearing after E2 in the 14-line log."
  - "Triage fan-out across other lenses (data-db, third-party, interfaces) was not spawned: docs/lab.md states the lab is one process with no database, no third-party dependency, and no distributed topology, and the baseline log tail already carried deterministic evidence of the mechanism (E1-E2), so deep-dive and discipline-parallel triage were skipped per budget and the hypothesis went straight to the adversarial judge, which returned validated."
usage:
  model: claude-sonnet-5
  tokens: 2140406
  wall_clock_seconds: 243
---

# Shop fully down: faultline process exited after a /simulate/crash call

## Summary

**Root cause identified.** The faultline process crashed — exited with code 1 —
immediately after a `GET /simulate/crash` call (E1, E2), and nothing restarted it. With
no process listening on port 8000, every request fails at TCP connect rather than
receiving an HTTP response of any kind, which is exactly the reported shape: "pages do
not load at all, not even an error page." Three independent probes against unrelated
paths (`/health`, `/metrics`, `/products`) all returned `curl: (7) ... Couldn't connect
to server` (E3-E5), ruling out a single-endpoint bug and confirming a total outage at
the process level, not the application level. An adversarial judge reviewed the
evidence independently and returned **validated**, noting the loopback connection
refusal rules out firewall/DNS/routing causes and that the consistency across three
unrelated endpoints rules out a single-handler defect. Confidence: high.

## Timeline

- `2026-11-02T22:51:40.761Z` — process starts, serving normally (log startup markers,
  pre-incident baseline, not separately cited).
- `2026-11-02T22:51:41Z`-`22:51:44Z` — normal traffic: health checks, product listing,
  an order created, order listing, all 200/201 (log tail, pre-incident baseline).
- `2026-11-02T22:51:46.761Z` (**E1**) — `GET /simulate/crash` returns 200.
- `2026-11-02T22:51:47.264Z` (**E2**) — CRITICAL log: "crashing now: exiting with code
  1", same `request_id` as E1 — the process exits.
- `2026-11-02T22:51:57Z` — human complaint received ("fine ten minutes ago" — the
  reporter's elapsed-time estimate is looser than the ~10s actually measured between
  the crash and the complaint, but the direction and the outage itself check out).
- `~2026-11-02T22:53:01Z`-`22:53:07Z` (**E3, E4, E5**) — investigator probes to
  `/health`, `/metrics`, `/products` all fail at TCP connect; no listener on port 8000.

## Investigation

1. **Baseline**: read the surface contract (`docs/lab.md`), then probed `/health`,
   `/metrics`, `/products` (all refused at TCP connect) and read the full log tail
   (`lab/logs/app.log`, 14 lines). The log tail itself carried the deciding evidence:
   normal traffic, then a `/simulate/crash` call, then an immediate CRITICAL exit line,
   then nothing — no further startup line.
2. **Triage/deep-dive**: skipped. The lab surface contract rules out the data-db,
   third-party, and interfaces lenses structurally (single process, no database, no
   external dependency, no distributed topology), and the remaining candidates
   (software-defect, load-saturation, infra-process) were already discriminated by the
   baseline log: this is not a per-input defect (every endpoint fails identically), not
   a gradual saturation (abrupt, not graded, and no load evidence precedes it), and
   matches a process lifecycle event precisely. Per budget rules, a hypothesis whose
   evidence is already deterministic goes straight to the judge.
3. **Judge**: one fresh adversarial judge agent reviewed H1 against the verbatim
   evidence only (no investigation narrative). Verdict: **validated**, with one noted
   residual gap (see Gaps) that does not change the verdict.

## Hypotheses

### H1 — process crashed via /simulate/crash — validated

The process received a `GET /simulate/crash` (E1), logged a CRITICAL intentional exit
0.5s later under the same request id (E2), and has not served a request since: three
probes on unrelated paths all fail at TCP connect (E3, E4, E5), which is the loopback
signature of nothing bound to the port — not a slow/erroring app, not a network/DNS
problem. No evidence contradicts this. The judge's adversarial pass independently
confirmed: connection-refused-at-TCP on loopback rules out firewall/DNS/routing;
consistency across three unrelated endpoints rules out a single-handler bug.

## Safe next steps

- Re-probe `/health` periodically (read-only) to detect when/if the process comes back
  up on its own; a fresh `startup` log line would mark a restart.
- If an operator/process supervisor exists outside this investigator's surface, check
  there whether the process is configured to restart on crash and why it has not — that
  check is outside konan's read-only surface and belongs to whoever runs the service.

## Gaps

- `scripts/lab.sh status` was not available in this session (required interactive
  approval that this session could not grant), so process state was inferred from
  connection-refused probes on three paths rather than a direct process/port snapshot.
- No telemetry covers the roughly 74 seconds between the crash log line and the first
  investigator probe; a restart-then-recrash inside that window cannot be excluded from
  the evidence gathered, only inferred absent from the lack of a new startup line in the
  log.
- Discipline-parallel triage across data-db/third-party/interfaces lenses was not
  spawned — excluded on the lab's documented single-process topology plus the already
  deterministic baseline evidence, not on fresh per-lens probing.
