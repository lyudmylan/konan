# konan skills

The product lives here: investigation methodology as skills, one directory per skill
(`skills/<name>/SKILL.md`). The first skill lands with #9 (investigate).

Dev mode, once a skill exists — symlink it into the project's skill path so sessions in
this repo load it live:

```sh
mkdir -p .claude/skills
ln -s ../../skills/<name> .claude/skills/<name>
```

Plugin packaging comes later (see the roadmap in `docs/product.md`).
