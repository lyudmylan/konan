# konan skills

The product lives here: investigation methodology as skills, one directory per skill
(`skills/<name>/SKILL.md`). Current skills: `investigate` — the konan loop (baseline,
discipline-parallel triage, hypothesis-parallel deep-dives, adversarial judge), with its
lens taxonomy under `investigate/lenses/` (org-extensible: drop in a new lens file) and
the journal contract (`investigate/report-contract.md` + `journal.schema.json`) every
investigation's output follows; finished journals land in `journals/`.

Dev mode, once a skill exists — symlink it into the project's skill path so sessions in
this repo load it live:

```sh
mkdir -p .claude/skills
ln -s ../../skills/<name> .claude/skills/<name>
```

Plugin packaging comes later (see the roadmap in `docs/product.md`).
