# konan skills

The product lives here: investigation methodology as skills, one directory per skill
(`skills/<name>/SKILL.md`). Current skills: `investigate` — the konan loop (baseline,
discipline-parallel triage, hypothesis-parallel deep-dives, adversarial judge), with its
lens taxonomy under `investigate/lenses/` (org-extensible: drop in a new lens file) and
the journal contract (`investigate/report-contract.md` + `journal.schema.json`) every
investigation's output follows; finished journals land in `journals/`. `konan` — the
manual trigger adapter (`/konan <complaint text>`): synthesizes the complaint object
per the trigger contract (`docs/triggers.md`) and starts the investigate loop.
`oncall` — the shift (`/oncall`): watches `alerts/inbox.jsonl`, catch-up first then
Monitor, investigates every alert serially, commits each journal, pages the owner.
`setup` — agent-run onboarding (`/setup`): prerequisite checks, lab wiring, a first
scored investigation, and the hand-over map; the operator's manual steps are only
install / clone / trust / operator prompts.

Dev mode, once a skill exists — symlink it into the project's skill path so sessions in
this repo load it live:

```sh
mkdir -p .claude/skills
ln -s ../../skills/<name> .claude/skills/<name>
```

Plugin packaging is the post-flip fast-follow, tracked in #44 — a hook port of the
read-only boundary comes first, because plugins cannot ship permission lists.
