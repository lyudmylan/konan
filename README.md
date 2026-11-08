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
The real-stack receipt: [the blind D1 investigation through Grafana Cloud queries only](journals/2026-11-08-products-3-division-by-zero.md),
scored 1/1 in [its scorecard](eval/runs/2026-11-blind-grafana/scorecard.md); the lab's files were out of
bounds and the evidence plane was the adapter's.

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

### The same skills, three models

Skills, lenses and scorer held constant; only the model swapped. bench-v2, 2026-11-02 to
2026-11-03: 90 blind headless investigations - 10 fixtures across three difficulty tiers,
N = 3, one small lab - on the corpus corrected after the first round. Protocol, limits, both
rounds and the false-fail table: [eval/BENCHMARK.md](eval/BENCHMARK.md); generated table:
[eval/BENCHMARK-results.md](eval/BENCHMARK-results.md).

| Model | Journals | Pass (pre-registered) | Pass (class-agnostic) | Root-cause acc. | Citations | Tokens (median) | Wall s (median) |
|---|---|---|---|---|---|---|---|
| Fable 5 | 30/30 | **77%** | **77%** | **86%** | **100%** | **1.47M** | **405** |
| Opus 5 | 30/30 | 63% | 63% | 67% | 97% | 2.21M | 610 |
| Sonnet 5 | 30/30 | 73% | 73% | **86%** | **100%** | 3.38M | 576 |

The two pass columns are equal this round. The first round's gap between them was the
incident-class label ([#63](https://github.com/lyudmylan/konan/issues/63)); the taxonomy fix ([#77](https://github.com/lyudmylan/konan/issues/77))
removed it. What remains in the 26 failed runs is read row by row in the false-fail table
of the protocol: 13 are a `must_claim` matcher that did not list the agent's wording while
the verdict, the class and the cause were right; 12 are verdict errors on the two tier-2
healthy traps; one is a journal the scorer refused.

Two results are worth more than the ranking. The suggestive-complaint fixture - a dormant
defect, a healthy system, a complaint that implies an outage - still catches frontier
models: Fable held the line in 2 of 3 runs, Sonnet in 1 of 3, Opus in 0 of 3; four of the six
runs that failed it promoted a defect their own probes had triggered to the cause of the
reported incident, and two wrote `inconclusive` with the observer effect stated in their
own summary. And the closed-window fixture - a real degradation that ended before the
complaint - caught every model on the verdict label: 7 of 9 runs wrote `root-cause-identified`
for a window they themselves described as over, six of them with "nothing is wrong now" or
"no active incident right now" in the first lines of the summary. The protocol reads that as
a gap in the report contract, which does not say which verdict a closed window gets; the fix
is one line there.

**Honesty over polish**: tokens, wall clock and quota share are captured per run from the
harness envelope and committed with the journals. The harness wall clock undercounts in 24
of 90 runs; the journal's own clock is the measure of an investigation, and its medians are
in the protocol. Tier 3 now differs by model as scored, and on the verdict and the cause
every tier-3 run of every model is right: the scored spread is matcher vocabulary, the
content is at the ceiling, and on this transparent lab the tier separates the models on
cost, not on findings. One journal was refused by the scorer and counts as failed. Sonnet's six missing
journals of the first round did not recur: the same operator command was denied and the
model continued. The earlier batch invalidated by a runner bug stays archived, not deleted,
and is described in the protocol.

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

## Bring your own target

A target plugs in as a **thin target adapter** — a surface-contract doc, a read-only permission
profile, and MCP/CLI config; the methodology never changes per target. `/adapter`
builds one with you: it interviews you about your observability surface, writes the
adapter, pins the tool allowlist from what your server actually serves, and smoke-tests
it. The first live target adapter is Grafana Cloud through the official `mcp-grafana` server,
[docs/adapters/grafana-cloud.md](docs/adapters/grafana-cloud.md): a session under it starts
with `claude --permission-mode manual --mcp-config docs/adapters/grafana-cloud.mcp.json` and
`KONAN_ADAPTER=docs/adapters/grafana-cloud.md` in the environment.

## Install as a plugin

The methodology travels as a Claude Code plugin — skills plus the boundary hook
(plugins cannot carry permission lists, so the read-only boundary ships as the
content-based hook, `hooks/hooks.json`):

```
/plugin marketplace add lyudmylan/konan
/plugin install konan@lyudmylan
```

Then `/konan:setup` onboards you. The per-target adapter — probe allowlist, surface
contract, lab scripts — stays per-repo setup, by design. Working inside a clone of
this repo? Don't also install the plugin there: the repo's own settings already run
the same hook, and two registrations would double-count the tripwire's denials.

The hook decides only inside a konan workspace: a checkout of this repo, or a
directory at or below a target that holds the marker file `.konan-workspace` (the adapter
writes it when it onboards a target). In every other directory the hook is silent and
the normal permission flow applies; `KONAN_BOUNDARY=1` in the environment forces it on
anywhere.

## Docs

- Product contract: [docs/product.md](docs/product.md)
- Architecture & flows: [docs/architecture.md](docs/architecture.md)
- Trigger contract: [docs/triggers.md](docs/triggers.md)
- The lab: [docs/lab.md](docs/lab.md)
- Eval semantics & blinding contract: [eval/README.md](eval/README.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
