# Plan: the word adapter replaces rim (#100)

Intent: `intents/adapter-rename.md`. Written 2026-11-08; the work starts after the leader accepts it in the
conversation and after the merge of #54's change request.

## The shape of the change

One branch from `main`, after #54 merges. One mechanical pass over the tracked files, then a read of every
changed line. No behavior changes; the hook's tests and the gates pin that.

## Steps

1. The moves, with `git mv`: `docs/rims` to `docs/adapters`; `skills/rim` to `skills/adapter`;
   `intents/grafana-rim.md` to `intents/grafana-adapter.md`; `intents/grafana-rim.plan.md` to
   `intents/grafana-adapter.plan.md`.
2. The words, one pass with `perl -pi` over the tracked text files that carry the word (the list of check 1,
   without this intent and this plan), word-bounded, the article first: `\ba rim\b` to `an adapter`,
   `\bA rim\b` to `An adapter`, then `rims` to `adapters`, `rim` to `adapter`, `Rim` to `Adapter`, `RIM` to
   `ADAPTER`, and the literal `KONAN_RIM` to `KONAN_ADAPTER` (an underscore is a word character, so the
   bounded rule alone misses it). BSD `sed` has no `\b`; `perl` has.
3. A read of the diff, line by line: grammar after the article rule; the merged plan of #54 names its branch
   by the old name, and the text names the work item instead; the skill's front matter reads
   `name: adapter`; the skill's command reads `/adapter` and `/konan:adapter` where the plugin form appears.
4. The tracker: the title of #58 and the lines of its body that are not dated decisions; one dated decision
   line on #58; any other open item of the milestone whose title carries the word (check 7 lists them).
5. The checks 1 to 7; `python3 hooks/tests.py` green; the two commands of `AGENTS.md` before the push.
6. The change request: `Closes #100`; the tier is the one `charter.toml` gives the changed paths (`intents/**`,
   `.claude/settings.json`, `AGENTS.md` and `hooks/**` are high); the leader reads the diff of the two code
   files (check 8) and approves in the conversation; the merge.
7. After the merge, outside the repository: the operator's shell exports `KONAN_ADAPTER` in place of
   `KONAN_RIM` for the sessions of the blind run (#55).

## Files

Moved: `docs/rims/grafana-cloud.md`, `docs/rims/grafana-cloud.mcp.json`, `docs/rims/grafana-cloud.alloy`,
`skills/rim/SKILL.md`, `intents/grafana-rim.md`, `intents/grafana-rim.plan.md`. Changed in text: the 19 files
of the count, among them `docs/product.md`, `README.md`, `AGENTS.md`, `.claude/settings.json`,
`.claude-plugin/plugin.json`, `docs/architecture.md`, `skills/README.md`, `skills/investigate/SKILL.md`,
`hooks/boundary.py`, `scripts/probe.sh`, `eval/BENCHMARK.md`, `intents/telemetry-plane.md`,
`intents/telemetry-plane.plan.md`, `intents/hook-scope.md`, `intents/hook-scope.plan.md`, and the smoke
journal of #54 under `journals/`. Not changed: `charter.toml`, `hooks/hooks.json`, `hooks/tests.py`, the
lenses, the report contract, the journal schema, `eval/**` beyond the one path, the earlier journals.

## Tests

The commands of checks 1 to 7; `python3 hooks/tests.py` unchanged.

## Facts the plan rests on (as of 2026-11-08)

- 19 tracked files carry the word, about 160 lines; 13 of them with the article `a`. `hooks/boundary.py`
  carries it in two docstring lines and one trailing comment; `scripts/probe.sh` in one comment line;
  `.claude/settings.json` only as `KONAN_RIM`; `charter.toml`, `hooks/hooks.json`, `hooks/tests.py`, the
  journals and the fixtures under `eval/` carry none, except one path in `eval/BENCHMARK.md`.
- A skill's command is its name: the `name` field of the front matter and the directory agree, and both are
  renamed; a plugin's skills arrive as `/<plugin>:<name>`. Source: the Claude Code documentation (skills,
  plugins).
- `git grep -w` treats the underscore as a word character: `KONAN_RIM` needs its own rule, and check 2 reads
  it by the literal.
