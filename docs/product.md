# konan (כונן) — product contract

**konan** is an agentic production-incident investigator built as Claude Code skills.
When something breaks, konan is the on-call agent: it triages, forms hypotheses, gathers
evidence, and delivers an investigation report in which every claim cites its evidence —
running on the Claude Code harness and subscription you already have.

Hebrew: כונן, the on-call engineer — the role that owns an incident end to end. (Bonus:
Konan ≈ Conan, as in Doyle, the author behind the detective.)

## The bet

Every player in the AI-SRE landscape ships the same shape: a deployed service with the
intelligence welded into orchestration code, billed per investigation. konan ships the
opposite shape:

| | The field | konan |
|---|---|---|
| Ships as | Deployed service (SaaS or self-hosted) | A skills repo installed into Claude Code |
| Intelligence lives in | Orchestration code | Readable markdown methodology (skills) |
| Marginal cost per investigation | API tokens or a license | ~zero on flat plans — the subscription is already paid |
| When a better model lands | Vendor re-engineers; you wait | Delete skills; evals show what was absorbed |

The design rule that follows: **whatever a new model can do out of the box must not
require re-architecting konan.** Capability lives in skills (cheap to rewrite or delete);
the harness provides the loop, tools, and subagents; code exists only where determinism
is the point.

## Architecture stance

- **Skills carry the methodology** — triage, hypothesis discipline
  (validated / invalidated / inconclusive), evidence rules, report format.
- **The harness carries the loop** — triggers are harness primitives (slash command,
  Monitor, webhook/channel, routine). No custom loop or orchestration code, ever.
- **Triggers are detector / adapter / profile** — detection lives in the observability
  stack (or a human); one adapter normalizes every delivery to the complaint contract
  (`docs/triggers.md`); adding a stack costs a configuration profile, never code.
  Delivery is push or event, never poll.
- **Code is allowed only for**: trigger plumbing, the read-only permission boundary
  (allowlists/hooks — a security boundary is never a prompt), the eval scorer, and the
  investigation report/journal contract.
- **Evidence collection is not our code** — existing MCP servers (Grafana, Sentry,
  Datadog, Kubernetes) later; for the lab target, plain allowlisted Bash (curl + logs).
- **faultline is a lab, not the architecture** — methodology skills, the report
  contract, and the eval scorer never encode a target's endpoints or defects. A target
  plugs in as a thin target adapter — probe allowlist, runner, scenario controls — plus a
  surface-contract doc (faultline's is `docs/lab.md`). Swapping targets swaps the target adapter;
  the methodology and scorer don't change.

## Investigation model

- **Taxonomy first, lab second.** Methodology derives from general incident classes —
  software defects, load/saturation, infra/process, third-party dependencies,
  interfaces/contracts, data/DB. faultline instantiates only the subset it can exercise;
  its gaps are stated in `docs/lab.md`, so lab scores are never read as methodology
  completeness.
- **The loop:** triage → deep-dive → judge → iterate or conclude.
  1. **Triage — discipline-parallel sweep.** A cheap pass where each lens answers
     "anomalies in my domain?" over the same evidence, blind to the others (diverse
     first looks are the point). Triage gates fan-out: it decides which hypotheses
     deserve deeper spend — the quota ladder's cheap-triage-first rung.
  2. **Deep-dive — hypothesis-parallel.** Each candidate cause becomes a focused
     workstream through the fitting lens, tasked to confirm *and* refute with targeted
     queries. Never summarize-everything.
  3. **Judge — non-deterministic, adversarial.** Judges cited evidence only; verdicts
     are validated / invalidated / inconclusive, plus "what evidence would settle it",
     which seeds the next round. Its job is to refute, not to bless.
  4. **Terminate** on confident conclusion, evidence exhausted, or budget hit.
- **Lenses are data.** Discipline lenses (devops, DBA, software, …) ship as markdown
  agent definitions; a team extends the taxonomy without touching konan.
- **Baseline primitive.** Know normal before declaring abnormal: konan argues from the
  diff against a healthy baseline, a hypothesis must predict observable state, and
  validation probes the prediction. "No incident" is a legitimate conclusion.
- **Judge ≠ scorer.** The in-loop judge is part of the system being measured; the eval
  scorer stays deterministic, or the eval spine measures nothing.
- Parallelism is harness-native: the orchestrator is the main session running the
  investigate skill; fan-out is built-in subagents; no orchestration code.

## The lab: faultline

[faultline](https://github.com/lyudmylan/faultline) is the controlled chaos target:
seeded defects (D1, D2), deterministic `/simulate` triggers, chaos mode, structured JSON
logs, Prometheus `/metrics`. Boundary: **konan investigates read-only** (GET endpoints,
`/metrics`, log files). Only the eval harness may trigger scenarios (`/simulate`,
`/chaos`).

## Evals are the spine (triple duty)

1. **CI gate** — every skill change re-runs the scenario corpus: seeded faults, chaos
   scenarios, and a **healthy-baseline scenario** whose correct verdict is "no incident"
   (the test almost nobody in the field runs).
2. **Model benchmark** — skills constant, model swapped; scorecard = root-cause accuracy,
   false attributions, evidence-citation compliance, tokens, wall-clock per investigation.
3. **Forward-compat instrument** — when a new model lands, the scorecard diff says which
   skills it absorbed. Delete them.

## v0.1 — first investigation, measured

Goal: konan investigates faultline end to end, and a scorecard proves it.

Exit criteria:

- A triggered investigation of D1 produces an evidence-cited report (journal committed).
- The eval harness runs the scenario corpus, including the healthy baseline, and emits
  `scorecard.md`.
- The repo flips public together with the scorecard and the retroactive origin post.

Out of scope for v0.1: remediation, the quota-resilience ladder, multi-model benchmark
automation, real observability-stack integrations (MCP), enterprise distribution.

Status: v0.1 closed 2026-08-18 — met, privately (both investigation criteria; the flip
moved to v0.2 by decision the same day: a first public version must be credible, which
means benchmarked, installable by a stranger, and proven on a real telemetry plane).

## v0.2 — credible public flip

Goal: the first public version — benchmarked, installable, and proven on real pipes.

Exit criteria:

- **Benchmark v1 published.** Corpus v2 on the lab's existing controls (difficulty tiers,
  attribution traps, a healthy battery), repeated runs, at least three models with the
  skills held constant, tokens and wall clock captured by the eval runner, protocol and
  limits documented (`eval/BENCHMARK.md`), results table in the README.
  Decided when the first round landed: a tier ships a published number only once its
  fixtures are shown to measure the agent rather than themselves. Tier 3 failed that
  test in round one — three models that diverge everywhere else scored identically on
  it, which is the signature of a matcher, not of a difficulty. Re-run in bench-v2
  (2026-11-02 to 2026-11-03, 90 runs) after the taxonomy and matcher fixes: its rows
  differ by model as scored, and on the verdict and the cause every tier-3 run of every
  model is right, so the tier carries its number with the reading that it does not
  separate the models on this lab. The pass rate the protocol committed to before the
  runs is always reported, even where the corpus, not the agent, is what it measures.
- **Onboarding is agent-run.** `/setup` runs the lab quickstart end to end (the human
  installs Claude Code, clones, trusts the workspace, approves operator prompts —
  nothing else); the plugin installs the methodology with the boundary hook; `/adapter`
  onboards a real target by interview (surface contract + permission profile + smoke
  run). Verified by a stranger test on a fresh clone.
- **One real-stack target adapter proof.** An evidence plane outside the lab's files — Grafana Cloud
  through the official MCP server — one blind investigation, journal committed and
  scored. Proves "swapping targets swaps the target adapter" on real pipes.
- The repo flips public together with the benchmark and the origin post.

Out of scope for v0.2: remediation, the quota-resilience ladder, report contract v2
(except its cause field, pulled forward because the benchmark cannot score false
attributions from prose), the cloud on-call routine, external benchmarks,
team-designated safe checks.

## Roadmap (deliberately unexpanded until close)

- **Quota-exhaustion resilience** (must-solve, post-v0.1): prevent (per-investigation
  budgets, cheap-triage-first model tiering, event-driven idle) → detect (quota-aware at
  start and mid-run) → degrade (zero-LLM deterministic evidence bundle) → fail over
  (per-seat team topology; credit reserve) → verify (an exhaustion eval scenario).
- **Remediation** (deliberate later phase): draft-only plans, then approval-gated
  execution; inherits ai-incident-investigator's safety schema (approval quorum, exact
  allowlists, audit trail).
- **Model-comparison content engine**: benchmark v1 lands in v0.2; re-run it on each
  model release; publish the scorecard.
- **Real-stack integrations**: the first target adapter proof (Grafana Cloud via MCP) lands in v0.2;
  team-designated checks, change-context sources, and alert-webhook triggers follow.
- **Enterprise distribution**: the plugin lands in v0.2 (methodology + boundary hook,
  scoped to a konan workspace; the target adapter stays per-target). Team/Enterprise seats (verified:
  full parity for skills, plugins, hooks, routines; org-managed policies make guardrails
  admin-enforced). Not Bedrock/Vertex — no skills/plugins/routines there per the current
  feature matrix.

## Policies

- **Subscription, not API**: everything runs on Claude Code auth the user already has.
  Stay indifferent to Anthropic's interactive-vs-programmatic billing split (announced,
  then paused).
- **Artifact-first publishing**: a version is not announced; it flips public together
  with its scorecard. Every public post ships same-day with its artifact. Each epic's
  definition of done includes a publishable artifact.
- **Prior art** (researched 2026-07-29): closest cousin is HolmesGPT (agentic loop,
  per-source toolsets, own eval harness). Field gaps konan ships against, receipts
  committed: healthy-baseline testing (a corpus scenario whose correct verdict is "no
  incident"), schema-enforced evidence citation (journal schema + deterministic
  scorer), a seeded-fault eval corpus with a committed scorecard. Cost-per-investigation
  numbers and the corpus-in-CI gate land with runner automation.
