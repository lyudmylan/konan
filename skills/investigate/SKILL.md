---
name: investigate
description: "Use when asked to investigate a suspected production issue, incident, outage, error spike, or 'something is wrong' report against a target system. Runs the konan investigation loop: baseline first, discipline-parallel triage, hypothesis-parallel deep-dives, adversarial judge, evidence-cited conclusion. Read-only always; 'no incident' is a legitimate verdict."
---

# Investigate

Prime directives, in force for every step:

- **Argue only from telemetry** gathered through the target's surface contract. Every
  claim cites its evidence: a quoted log line with timestamp, a metric name and value,
  or a probe response with status. No citation, no claim.
- **Read-only, always.** You observe the target; you never change it.
- **"No incident" is a legitimate conclusion** — reaching it requires evidence too.
- **Correlated is not causal.** A suspicious signal near the failure is a hypothesis,
  not a cause, until its prediction checks out.
- **Your probes are telemetry-visible.** Read-only probes still increment request and
  exception counters, and can exercise latent defects. Your stamped request-id prefix
  distinguishes your traffic from users' — when assessing user impact, count only
  non-investigator traffic; a defect only your own probes have triggered is a **latent**
  finding, not the active incident.

## 0. Setup

1. Read the target surface contract — the document defining what you may probe, where
   logs live, and what metrics exist. Default for this repo's lab: `docs/lab.md`. Touch
   nothing outside that contract.
2. Record the complaint verbatim (who reports what, since when — as given).
3. Budget for this investigation, unless the caller overrides: one triage round, at most
   3 deep-dive agents per round, at most 2 rounds. When the budget runs out you conclude
   with the honest state — never with manufactured certainty.

## 1. Baseline — know normal before declaring abnormal

Capture, via the contract's surface: current health, a metrics snapshot, and the recent
log tail. Establish what normal looks like (steady counters, error-free cadence, stable
latency). Later, every hypothesis must predict a deviation from THIS baseline, and its
validation probes that prediction.

## 2. Triage — discipline-parallel sweep (cheap; it gates everything after it)

Fan out across every lens whose domain the complaint and baseline cannot already
exclude with evidence — for a vague complaint that is all of them: complaint framing is
untrusted (misattribution is normal, and secondary causes hide behind obvious ones). A
lens you skip is a blind spot you accepted — record it under Gaps. Never spawn a lens as
coverage theater. Spawn the chosen lenses in a single message so they run in parallel,
each blind to the others. Each triage prompt contains exactly: the lens file path, the
surface contract path, the complaint verbatim, and the baseline summary — nothing else.
Each lens answers only:

> "Anomalies in your domain? At most 3 findings, each with cited evidence. No deep
> dives, no fixes, no speculation beyond your domain."

Collect findings, deduplicate, and turn them into a hypothesis list. A hypothesis is:
`{cause statement, incident class, prediction (observable state it implies), evidence so
far}`. If no lens finds anomalies and the baseline diff is clean, conclude **no
incident**, citing the checks performed.

## 3. Deep-dive — hypothesis-parallel

**The orchestrator selects.** Rank hypotheses by: evidence strength from triage,
explanatory power against the complaint, cost of the decisive test (prefer cheap tests
that can kill a hypothesis), and severity if true. Take at most the budgeted number. A
hypothesis whose triage evidence is already deterministic and complete skips deep-dive
and goes straight to the judge — deep-dives exist to fill evidence gaps, not to
re-prove. Spawn one subagent per selected hypothesis (parallel in a single message when
there are several — one hypothesis is one agent, never ceremony), through the fitting
lens, tasked to **confirm and refute**:

> "Test this hypothesis with targeted queries only — probe what it predicts, and
> actively seek disconfirming evidence. Never collect everything. Return: proposed
> verdict, evidence for, evidence against, confidence, what is still missing."

## 4. Judge — adversarial, evidence-only

Spawn one fresh judge subagent whose prompt contains only the hypothesis list with the
verbatim cited evidence (quotes, not summaries) — no lens reasoning, no narrative. Its
job is to refute, not to bless:

> "For each hypothesis: does the cited evidence actually support it? Verdict
> validated / invalidated / inconclusive. For every non-validated verdict, state what
> single piece of evidence would settle it."

The judge sees claims and evidence, never the investigation story — that firewall
prevents narrative capture.

## 5. Iterate or conclude

- A **validated** hypothesis whose prediction was confirmed by probing → conclude.
- **Inconclusive** verdicts with budget remaining → the judge's "what would settle it"
  items become the next round's targeted gathering; return to step 3 with the refined
  list. The judge names the missing evidence; the orchestrator still selects which
  hypotheses proceed.
- Budget or evidence exhausted → conclude with the honest state: ranked hypotheses,
  verdicts, and gaps.

## Conclusion (interim shape — the full report contract is #10)

- **Verdict**: root cause identified / no active incident (latent findings noted) /
  inconclusive (ranked hypotheses).
- **Evidence**: every claim cited (log quote + timestamp, metric name + value, probe
  status + request id).
- **Timeline** of key events, including any configuration/deploy/flag-change markers
  found in logs — a behavior change right after a config-change marker is prime
  timeline evidence.
- **Safe next steps** — read-only suggestions only; remediation is out of scope.
- **Gaps**: what could not be checked, and why.

## Rules that survive contact

- The healthy-monitoring trap: a green health endpoint while business traffic fails is
  a known incident shape — always check the business surface, not just health.
- Prefer disconfirming queries; the fastest investigations kill hypotheses early.
- Data-dependent failures are real: "most inputs succeed, specific inputs fail" is a
  defect shape, not noise.
- Uptime resets, counter resets, and startup markers are process-lifecycle evidence —
  read them before theorizing.
