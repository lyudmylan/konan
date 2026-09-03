---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-down-process-exit
  trigger: "manual — /konan human profile; complaint object source=human, fingerprint=human-1787158276, labels.alertname=human-report (no severity stated by reporter), startsAt=2026-08-19T16:51:16Z; investigation started 2026-08-19T16:51:22Z (trigger latency 6s)"
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-19T16:51:22Z
  concluded: 2026-08-19T16:52:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The faultline server process deliberately exited with code 1 at 16:51:09.684Z after a non-investigator request to GET /simulate/crash, and nothing restarted it, so the listener on 127.0.0.1:8000 is gone and every connection is refused."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The application process terminated (exit code 1, triggered via the /simulate/crash operator surface) and was not restarted; with no listener bound, TCP connections are refused before any HTTP response can be produced."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7]
    evidence_against: []
  - id: H2
    statement: "Chaos injection was enabled and is returning failures for all traffic."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E1, E2]
  - id: H3
    statement: "The service is saturated or hanging under load, so requests time out rather than being served."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E8]
  - id: H4
    statement: "The investigator's own read-only probes triggered the failure."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E9, E10]
evidence:
  - id: E1
    type: probe
    source: "GET /health, request_id=konan-1787158294-65998"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000256s request_id=konan-1787158294-65998"
  - id: E2
    type: probe
    source: "GET /products, request_id=konan-1787158330-66017"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000164s request_id=konan-1787158330-66017"
  - id: E3
    type: probe
    source: "GET /metrics, request_id=konan-1787158334-66024"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000195s request_id=konan-1787158334-66024"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:51:09.684Z"
    quote: "{\"ts\": \"2026-08-19T16:51:09.684Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"2f047a5bbb29\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:51:09.182Z"
    quote: "{\"ts\": \"2026-08-19T16:51:09.182Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"2f047a5bbb29\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.411, \"client\": \"127.0.0.1:63087\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log — final line of file is the 16:51:09.684Z crash record; no lines after it"
    quote: "{\"ts\": \"2026-08-19T16:51:09.684Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"2f047a5bbb29\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:51:03.083Z"
    quote: "{\"ts\": \"2026-08-19T16:51:03.083Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:51:03.897Z and 16:51:07.110Z — representative pre-crash traffic"
    quote: "\"message\": \"GET /products -> 200\", \"status\": 200, \"duration_ms\": 1.176 … \"message\": \"GET /orders -> 200\", \"status\": 200, \"duration_ms\": 0.952"
  - id: E9
    type: probe
    source: "scripts/probe.sh (the investigator's only target surface), lines 18-21"
    quote: "/health|/metrics|/openapi.json|/products|/products/*|/orders|/orders/*) ;;\n  *) echo \"probe.sh: '$path' is outside the read-only allowlist\" >&2; exit 2 ;;\nesac\nrid=\"konan-$(date +%s)-$$\""
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T16:51:09.182Z — client field of the crash-triggering request"
    quote: "\"request_id\": \"2f047a5bbb29\", \"path\": \"/simulate/crash\", \"client\": \"127.0.0.1:63087\""
gaps:
  - "Process-table confirmation was not obtained: the `ps` check on the PIDs in lab/faultline.pid (65904, 65905) and on the server process 65907 required an interactive approval that was not granted. Process death is inferred from the CRITICAL exit record (E4), the absence of any later log line (E6), and connection-refused on all three probed paths (E1-E3) — not from a direct process listing."
  - "History before 2026-08-19T16:51:03Z is unavailable: lab/logs/ holds only app.log with no .1-.3 rotated backups, and the file begins at this process's startup marker. The reporter's 'fine ten minutes ago' cannot be verified against telemetry — the observable healthy window is only 16:51:03 to 16:51:09."
  - "Who or what called /simulate/crash was not established beyond the client address 127.0.0.1:63087 (E10). That surface is operator/eval-side and outside the investigator's contract, so it could not be queried."
  - "Restart policy was not inspected: whether a supervisor was expected to bring the process back (and failed to) is outside the readable surface, so 'nothing restarted it' is an observation of effect (E6), not of configuration."
  - "Triage lenses and the adversarial judge ran inline in the orchestrator rather than as separate blind subagents, because this session's harness configuration forbids spawning agents unless the user asks. The narrative firewall the skill relies on was therefore not in place; the evidence is deterministic enough that this is judged low-risk, but it is a real deviation from the loop."
usage:
  model: claude-opus-5
  tokens: 546768
  wall_clock_seconds: 81
---

# Shop fully down — faultline process exited and did not come back

## Summary

**Root cause identified.** The faultline server process exited on purpose with code 1 at
16:51:09.684Z, immediately after serving a request to the operator surface
`GET /simulate/crash` (E4, E5). Nothing restarted it: the log file ends at that crash
record with no later startup marker (E6), and probes to `/health`, `/products` and
`/metrics` all fail at the TCP layer with "Couldn't connect to server" — HTTP status 000,
in under 0.3 ms (E1, E2, E3).

This matches the complaint exactly. "Not even an error page" is the signature of a dead
listener rather than a failing application: with no process bound to 127.0.0.1:8000, the
connection is refused before any HTTP response — error page included — can be generated.
Impact is total: every path is affected, for every user, continuously since
16:51:09.684Z. Confidence is high; the exit is self-reported by the service at CRITICAL
level and the mechanism is directly observable.

One correction to the report's framing: the reporter said "fine ten minutes ago", but the
service was only up from 16:51:03.083Z (E7) — about six seconds before it died. Telemetry
for any earlier period does not exist on this host (no rotated log backups), so the
healthy window I can attest to is short. This does not change the verdict; it does mean
the "ten minutes" figure is the reporter's estimate, not a telemetry fact.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 16:51:03.083 | faultline 0.1.0 starts; uvicorn binds 127.0.0.1:8000 | E7 |
| 16:51:03.865 – 16:51:07.110 | Normal traffic: `/health`, `/products`, `/products/1`, `POST /orders` (201), `/orders` — all 2xx, 0.9–2.0 ms | E8 |
| 16:51:09.182 | `GET /simulate/crash` served, 200, from client 127.0.0.1:63087 — request_id `2f047a5bbb29` | E5, E10 |
| 16:51:09.684 | CRITICAL "crashing now: exiting with code 1" — same request_id, after the declared 0.5 s delay | E4 |
| 16:51:09.684 → now | No further log lines of any kind; no startup marker; no restart | E6 |
| 16:51:34 onward | Investigator probes to `/health`, `/products`, `/metrics` all fail: connection refused, HTTP 000 | E1, E2, E3 |

No configuration-change, deploy, or `chaos_enabled` marker appears anywhere in the log —
the only state change in the window is the crash itself.

## Investigation

**Baseline.** The intended first step — health, metrics snapshot, log tail — was cut
short at once: `/health` returned connection refused (E1). That is itself the strongest
baseline fact available, so the log became the primary surface. It gave both a healthy
reference period (E8) and the terminal event (E4).

**Triage.** With connection refused established on three separate paths and an explicit
self-reported process exit in the log, the infra-process domain was decisive and the
remaining lens domains were excluded on evidence rather than skipped: a software defect
in request handling, a saturation condition, and an interface/contract fault all require
a process that accepts connections, and none is present. Per the skill's rule that
deterministic, complete triage evidence goes straight to the judge, no deep-dive round was
spawned. Lenses and judge ran inline rather than as blind subagents — see Gaps.

**Adversarial pass.** Three alternatives were actively pursued to refute H1, and all three
were killed on evidence (H2–H4 below). The self-implication check mattered most and is
recorded in full under H4.

## Hypotheses

### H1 — process exited and was not restarted (validated)

The service logged its own termination at CRITICAL: `"crashing now: exiting with code 1"`,
`event: crash`, `delay: 0.5` (E4). The preceding line shows the trigger: `GET
/simulate/crash -> 200` at 16:51:09.182Z carrying the same `request_id` `2f047a5bbb29`
(E5) — the 502 ms between the two lines matches the declared `delay: 0.5` exactly, which
ties trigger to exit rather than merely placing them near each other. The log then stops
(E6): no shutdown sequence, no new startup marker, nothing. The prediction this makes —
that the port is unbound and every path fails identically at the transport layer — was
probed and confirmed on `/health`, `/products` and `/metrics` (E1, E2, E3), each failing
in ~0.2 ms, far too fast for any application-level path. No evidence against.

### H2 — chaos injection (invalidated)

Chaos would produce HTTP error responses, not refused connections. The log contains no
`chaos_enabled` event at any point (E6 — the file's full content ends at the crash), and
the observed failures carry no HTTP status at all (E1, E2). Killed.

### H3 — saturation or hang (invalidated)

A saturated or hung service accepts connections and then stalls; these probes never
completed a TCP handshake, failing in 0.000164–0.000256 s (E1, E2). Pre-crash latencies
were 0.9–2.0 ms with no upward trend (E8). Killed.

### H4 — investigator-caused (invalidated)

Required by the prime directive that probes are telemetry-visible. Refuted three ways.
First, `/simulate/crash` is mechanically outside the probe allowlist — `probe.sh` refuses
any path but `/health`, `/metrics`, `/openapi.json`, `/products`, `/orders` and their
sub-paths (E9), so the investigator cannot reach that surface. Second, investigator
requests are stamped `konan-<epoch>-<pid>` (E9), while the crash-triggering request carried
the server-generated id `2f047a5bbb29` (E10) — unstamped user traffic. Third, the crash at
16:51:09.684Z (E4) precedes this investigation's start at 16:51:22Z and its first probe at
16:51:34. The crash is user-side; the outage is active and real, not latent. Killed.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Confirm process death directly with a process listing for the PIDs in
   `lab/faultline.pid` (65904, 65905) and the logged server process 65907 — this closes
   the one inferential step in the chain (see Gaps).
2. Identify the caller of `GET /simulate/crash` from client address 127.0.0.1:63087 (E10).
   The exposure question worth answering is whether a surface that terminates the process
   is reachable by ordinary traffic in this environment, since one unauthenticated GET
   took the whole shop down.
3. Check whether a supervisor or restart policy was expected to bring the process back.
   Six seconds of uptime followed by an unrecovered exit suggests either no supervision or
   a supervisor that also gave up — the log cannot distinguish these.
4. Preserve `lab/logs/app.log` before any restart. It holds the only record of this
   incident, has no rotated backups, and a fresh start will overwrite the evidence.

## Gaps

- **No direct process-table confirmation.** The `ps` check on PIDs 65904, 65905 and 65907
  required an approval that was not granted in this session. Death is inferred from E4
  (self-reported exit), E6 (log stops) and E1–E3 (connection refused on every path) — a
  chain strong enough to act on, but one step short of direct observation.
- **No history before 16:51:03Z.** `lab/logs/` contains only `app.log`, with no `.1`–`.3`
  backups, and the file opens with this process's startup marker. The reporter's "ten
  minutes ago" is therefore unverifiable; the attested healthy window is 16:51:03 to
  16:51:09 (E7, E8).
- **Crash caller not identified.** Only the client address 127.0.0.1:63087 is known (E10).
  `/simulate/*` is operator/eval surface, outside the investigator's contract, so it could
  not be queried.
- **Restart policy not inspected.** "Nothing restarted it" is an observation of effect
  (E6), not of configuration; supervisor config is outside the readable surface.
- **Loop deviation: lenses and judge ran inline.** This session's harness forbids spawning
  subagents unless the user asks, so the discipline-parallel triage sweep and the
  firewalled adversarial judge were performed by the orchestrator itself. The narrative
  firewall that normally guards against a self-confirming story was not in place. The
  evidence here is deterministic and the alternatives were killed on transport-layer facts,
  so the risk is low — but a reader should weigh the verdict knowing an independent judge
  did not see it.
