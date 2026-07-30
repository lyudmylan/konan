# konan (כונן) — product contract

**konan** is an agentic production-incident investigator built as Claude Code skills.
When something breaks, konan is the on-call agent: it triages, forms hypotheses, gathers
evidence, and delivers an investigation report in which every claim cites its evidence —
running on the Claude Code harness and subscription you already have.

Hebrew: כונן, the on-call engineer — the role that owns an incident end to end. (Bonus:
Konan ≈ Conan, as in Doyle, the author behind the detective.

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
- **Code is allowed only for**: trigger plumbing, the read-only permission boundary
  (allowlists/hooks — a security boundary is never a prompt), the eval scorer, and the
  investigation report/journal contract.
- **Evidence collection is not our code** — existing MCP servers (Grafana, Sentry,
  Datadog, Kubernetes) later; for the lab target, plain allowlisted Bash (curl + logs).

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

## Roadmap (deliberately unexpanded until close)

- **Quota-exhaustion resilience** (must-solve, post-v0.1): prevent (per-investigation
  budgets, cheap-triage-first model tiering, event-driven idle) → detect (quota-aware at
  start and mid-run) → degrade (zero-LLM deterministic evidence bundle) → fail over
  (per-seat team topology; credit reserve) → verify (an exhaustion eval scenario).
- **Remediation** (deliberate later phase): draft-only plans, then approval-gated
  execution; inherits ai-incident-investigator's safety schema (approval quorum, exact
  allowlists, audit trail).
- **Model-comparison content engine**: re-run the benchmark on each model release;
  publish the scorecard.
- **Real-stack integrations**: MCP evidence layer, alert-webhook triggers.
- **Enterprise distribution**: Team/Enterprise seats (verified: full parity for skills,
  plugins, hooks, routines; org-managed policies make guardrails admin-enforced). Not
  Bedrock/Vertex — no skills/plugins/routines there per the current feature matrix.

## Policies

- **Subscription, not API**: everything runs on Claude Code auth the user already has.
  Stay indifferent to Anthropic's interactive-vs-programmatic billing split (announced,
  then paused).
- **Artifact-first publishing**: never announce intentions. The repo stays private until
  v0.1; every public post ships same-day with its artifact. Each epic's definition of
  done includes a publishable artifact.
- **Prior art** (researched 2026-07-29): closest cousin is HolmesGPT (agentic loop,
  per-source toolsets, own eval harness). Field gaps konan targets: evals in CI,
  healthy-baseline testing, published cost-per-investigation, schema-enforced evidence
  citation.
