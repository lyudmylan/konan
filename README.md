# konan

**konan** is an agentic production-incident investigator built as Claude Code skills.
When something breaks, konan is the on-call agent: it triages, forms hypotheses, gathers
evidence, and delivers an investigation report in which every claim cites its evidence —
running on the Claude Code harness and subscription you already have.

Hebrew: כונן, the on-call engineer — the role that owns an incident end to end. (Bonus:
Konan ≈ Conan, as in Doyle, the author behind the detective.)

## Measured before believed

konan is scored by a deterministic eval harness against seeded faults before any claim
is made about it. The committed scorecard: [eval/scorecard.md](eval/scorecard.md).

| Corpus v1 (5 scenarios) | Result |
|---|---|
| Scenarios passed | **5/5** |
| Root-cause accuracy | 4/4 (the fifth scenario correctly concludes "no incident") |
| False attributions | 0 |
| Evidence-citation compliance | 5/5 (schema-enforced: no citation, no claim) |

The corpus includes a **healthy-baseline scenario** whose correct verdict is
"no active incident" — the test almost nobody in the field runs, because agents under
findings-pressure hallucinate incidents on healthy systems.

**Triggered operation is proven live, not described.** An alert — not a human — started
an unattended investigation of a seeded defect: root cause identified, every claim
cited, the journal committed by the on-call session itself, trigger latency 13 seconds
([journal](journals/2026-08-06-products-3-user-500s.md)). An alert raised while nobody
was on shift waited 62 minutes in a durable inbox and was investigated at the next
shift start, the wait stamped honestly ([journal](journals/2026-08-06-overnight-latency-flag.md)).
Between events an on-call shift is idle at zero model cost — delivery is push or
event, never poll.

**Honesty over polish**: token costs are not yet captured (they land with runner
automation); wall-clock numbers include real interruptions, documented inside the
journals rather than hidden.

## How it works

Pictures first: [docs/architecture.md](docs/architecture.md) — the system and its
boundaries, the investigation loop, the on-call trigger path.

- **Skills carry the methodology** — baseline before judgment, discipline-parallel
  triage lenses blind to each other, hypothesis deep-dives tasked to confirm *and*
  refute, an adversarial judge whose job is to refute. The loop is readable markdown
  under [skills/](skills/README.md).
- **The harness carries the loop** — triggers, parallelism, and scheduling are Claude
  Code primitives. No orchestration code exists in this repo.
- **Detection is not konan's job** — an observability stack (or a human) delivers a
  complaint; a trigger is an adapter, and adding a stack costs a configuration
  profile, never code ([docs/triggers.md](docs/triggers.md)).
- **Read-only, mechanically** — the investigator touches a target only through an
  allowlisted probe, and the boundary is code, not prompts: a `PreToolUse` hook
  ([hooks/boundary.py](hooks/boundary.py)) reads every shell command whole and denies
  raw network clients, operator surfaces, and destructive git forms by content;
  only the probe and the journal-commit shapes are pre-approved; everything else
  prompts, and an unattended shift fails closed on a prompt. A second denial freezes
  the session — a denied action is a signal to stop, never a puzzle to solve. The
  decisions are pinned by tests ([hooks/tests.py](hooks/tests.py)). A security
  boundary is never a prompt.

## The eval spine (triple duty)

1. **Quality gate** — skill changes are validated by re-running the seeded-fault corpus
   through the eval runner (blinded, headless, tokens and wall clock captured); the CI
   wiring is the remaining step.
2. **Model benchmark** — skills constant, model swapped; the scorecard grows a
   per-model dimension on each model release.
3. **Forward-compat instrument** — when a new model absorbs part of the methodology,
   the scorecard diff says which skills to delete.

## Try it

Onboarding is agent-run. Install [Claude Code](https://code.claude.com), clone this
repo, start `claude` in it, and type:

```
/setup
```

The agent checks prerequisites, wires up [faultline](https://github.com/lyudmylan/faultline)
(the deliberately unreliable lab service) beside the repo, runs a first read-only
investigation, and scores it in front of you. Your manual steps are only: install,
clone, trust the workspace, and approve the operator prompts. By hand instead:

```sh
scripts/lab.sh start          # needs a faultline checkout (FAULTLINE_DIR=../faultline)
/konan "users report errors opening a product page"   # manual trigger
/oncall                       # or: take the shift and let alerts drive it
```

The full lab contract — what the investigator may touch, and the eval-side scenario
controls — is in [docs/lab.md](docs/lab.md).

## Docs

- Product contract: [docs/product.md](docs/product.md)
- Architecture & flows: [docs/architecture.md](docs/architecture.md)
- Trigger contract: [docs/triggers.md](docs/triggers.md)
- The lab: [docs/lab.md](docs/lab.md)
- Eval semantics & blinding contract: [eval/README.md](eval/README.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
