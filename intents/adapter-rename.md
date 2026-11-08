# Intent: the word adapter replaces rim

Work item: #100. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The per-target layer of konan carries the industry's name: `adapter` replaces `rim` in every tracked text
of the repository, in the environment variable, the skill's name, the paths and the open tracker items,
and nothing changes in behavior.

## In scope

- The word, bounded, in every case, in every tracked text file, as check 1 finds them: `rim` to `adapter`,
  `rims` to `adapters`, `Rim` to `Adapter`, `RIM` to `ADAPTER`; `a rim` to `an adapter`. `adapter` already
  names the trigger adapter (`docs/triggers.md`: one adapter normalizes every delivery). Where a text also
  speaks of trigger adapters (`docs/product.md`, `docs/architecture.md`, `README.md`,
  `.claude-plugin/plugin.json`), the per-target layer is written `target adapter`; the skill, the variable
  and the paths keep the short form. Where a text names a git branch by its old name, the text names the
  work item instead: a branch keeps its name.
- The paths: `docs/rims/` to `docs/adapters/` (the three Grafana Cloud files inside); `skills/rim/` to
  `skills/adapter/`, with `name: adapter` in its front matter and the command `/adapter` (`/konan:adapter`
  in the plugin); `intents/grafana-rim.md` and `intents/grafana-rim.plan.md` to `intents/grafana-adapter.md`
  and `intents/grafana-adapter.plan.md`, their check commands with the new paths and the new variable.
  Every reference to these paths follows.
- The variable: `KONAN_RIM` to `KONAN_ADAPTER` in the Setup step of the investigate skill, the allow entry
  `Bash(printenv KONAN_ADAPTER)` of `.claude/settings.json`, the adapter document and `AGENTS.md`.
- The smoke journal of #54: its `surface_contract` value becomes `docs/adapters/grafana-cloud.md`, and check 5
  of the renamed intent reads it there.
- The tracker: the titles of the open items of the milestone that carry the word, and the lines of #58 that
  are not dated decisions (the goal, the order, the children; check 7 reads them); one dated decision line
  on #58 records the rename. Closed items and the comments of any item stay as they are.
- The order: the work starts after the merge of #54's change request. Both touch the same files, and the
  smoke journal lands first.

## Out of scope

Any change of behavior: the hook's decisions and its tests, the probe, the steps of the skills, the lenses,
the allowlisted tools, the content of the Alloy configuration beyond its comment line. The git history and
the names of branches. Closed tracker items and the comments of any item. The word inside other words
(`primitive`, `experiment`, `trim`). The trigger adapter and its documents keep their word. The journals of
earlier investigations and the archived runs and fixtures under `eval/` carry no occurrence and are
untouched (check 1 reads the whole tree); `eval/BENCHMARK.md` carries one path, which follows the rename.

## Acceptance checks

### Automatic checks

1. No occurrence of the word remains in the tracked files, outside this intent and its plan, which name the
   old word to describe the change.
   command: `! git grep -I -w -i -q -E 'rim|rims' -- . ':!intents/adapter-rename.md' ':!intents/adapter-rename.plan.md'`
2. The old paths, the old intent names and the old variable are gone, and the new ones exist.
   command: `! git grep -I -q -E 'KONAN_RIM|docs/rims|skills/rim|grafana-rim' -- . ':!intents/adapter-rename.md' ':!intents/adapter-rename.plan.md' && test -f docs/adapters/grafana-cloud.md && test -f docs/adapters/grafana-cloud.mcp.json && test -f docs/adapters/grafana-cloud.alloy && test -f skills/adapter/SKILL.md && test -f intents/grafana-adapter.md && test -f intents/grafana-adapter.plan.md && ! test -e docs/rims && ! test -e skills/rim`
3. The skill carries the new name, the skill and the two READMEs name the command in its slash form (not a
   path), and the plugin's description names the target adapter.
   command: `grep -q '^name: adapter$' skills/adapter/SKILL.md && grep -qE '(^|[^a-z/])/adapter([^a-z-]|$)' skills/adapter/SKILL.md && grep -qE '(^|[^a-z/])/adapter([^a-z-]|$)' README.md && grep -qE '(^|[^a-z/])/adapter([^a-z-]|$)' skills/README.md && grep -q 'target adapter' .claude-plugin/plugin.json`
4. The settings allow the one read of the new variable, and the README's session command names the new
   path; the rest of the wiring (the skill reads the variable, the adapter document and `AGENTS.md` name
   it) is check 3 of the renamed intent, run by check 5.
   command: `jq -r '.permissions.allow[]' .claude/settings.json | grep -qx 'Bash(printenv KONAN_ADAPTER)' && grep -q -- '--mcp-config docs/adapters/grafana-cloud.mcp.json' README.md`
5. The renamed intent of the Grafana Cloud adapter holds with the new names: each of its six indented
   `command:` lines passes as written there, with the new paths and the new variable (its inline quality
   check, number 7, is the one check 6 runs); an extraction of fewer than six lines fails.
   command: `test "$(grep -cE '^ *command: `' intents/grafana-adapter.md)" -eq 6 && grep -oE '^ *command: `.*`$' intents/grafana-adapter.md | sed -E 's/^ *command: `(.*)`$/\1/' | while IFS= read -r c; do bash -c "$c" || exit 1; done`
6. No behavior changes: the hook's tests stay green and the gates of the contract pass.
   command: `python3 hooks/tests.py && charter-gate quality --contract charter.toml && charter-check all charter.toml`
7. No open item of the milestone carries the old word in its title, outside #100 itself, and the body of
   #58 carries it only in its dated decision lines and in the line that names #100.
   command: `! gh issue list --state open --milestone "v0.2 — credible public flip" --json number,title --jq '.[] | select(.number != 100) | .title' | grep -qiw -E 'rim|rims' && ! gh issue view 58 --json body --jq .body | grep -v -E '^- 20[0-9]{2}-[0-9]{2}-[0-9]{2}|#100' | grep -qiw -E 'rim|rims'`

### Manual checks

8. The two code files change in comment and docstring lines only: the diff of `hooks/boundary.py` and
   `scripts/probe.sh` on the change request. who: the leader, at the approval. Not automatic: a docstring
   line carries no marker a tool can read, so the kind of a changed line is a reading of the diff; the
   behavior itself is pinned by check 6.
