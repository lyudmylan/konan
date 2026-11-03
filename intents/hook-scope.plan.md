# Plan: the scope of the boundary hook (#74)

Intent: `intents/hook-scope.md`. Written 2026-11-03; the code starts after the leader accepts it in the
conversation.

## The shape of the change

One branch, `74-hook-scope`. The hook gains one question before every other: is this session inside a
konan workspace? The answer comes from the `cwd` of the hook event and two environment variables, and it
is computed once, in `main`, then passed into the pure decision function, so every existing pin keeps its
meaning and the new pins test the scope on its own. Outside a workspace the hook prints nothing, which is
the harness's "no decision": the normal permission flow applies, as it does for any other project.

## Steps

1. `hooks/boundary.py`: two constants, `WORKSPACE_SIGNATURE = ("docs/triggers.md", "skills/investigate")`
   and `WORKSPACE_MARKER = ".konan-workspace"`; one function `in_workspace(cwd, env)` that returns True
   when `env` has `KONAN_BOUNDARY=1` or `KONAN_EVAL_BLIND=1`, when `cwd` is missing or empty (fail closed),
   when `cwd` holds the two signature paths (a file and a directory), or when `cwd` holds the marker file;
   otherwise False. `evaluate` gains a keyword `governed=True`; when it is False the function returns
   `(None, "", state)` before the frozen check, so the tripwire state is neither read nor written. `main`
   computes `governed = in_workspace(event.get("cwd"), os.environ)` and passes it. The docstring gains the
   scope paragraph: where the hook decides, the marker, the two overrides, the fail-closed rule.
2. `hooks/tests.py`: the scope pins, one function each, with a temporary directory per case:
   "scope: silent outside a workspace" (every deny row of `PINS` returns no decision with `governed=False`
   and its table decision with `governed=True`); "scope: signature" (`in_workspace` on the repository
   itself is True, on an empty temporary directory False, on a directory with the two signature paths
   True); "scope: marker"; "scope: force-on"; "scope: eval mode"; "scope: no cwd fails closed"; "scope:
   tripwire untouched" (two deny-by-content commands with `governed=False` leave the state at zero and
   not frozen); "scope: process silence" (the hook process with an event whose `cwd` is an empty temporary
   directory prints nothing for a raw network client, and prints the deny JSON when `cwd` holds the
   marker). The closing line counts the scope pins.
3. `README.md`, "Install as a plugin": two sentences after the install lines: the hook decides only inside
   a konan workspace (a checkout of this repo, or a target that holds the marker file `.konan-workspace`,
   which the rim writes) and is silent in every other directory; `KONAN_BOUNDARY=1` forces it on anywhere.
   `AGENTS.md`, "Lab boundary": one sentence with the same content after the plugin sentence.
   `docs/product.md`, the enterprise-distribution line: "(methodology + boundary hook, scoped to a konan
   workspace; ...)".
4. The checks: 1 to 8 of the intent, the two commands of `AGENTS.md`, and the manual check 9 by the
   engineer with the plugin installed in a directory that is not a workspace. One change request,
   `Closes #74`; the review loop (the branch touches `hooks/**`, high tier); the leader's approve in the
   conversation; the merge. A note on #52: the rim writes the marker (already posted on 2026-11-03).

## Files

`hooks/boundary.py`, `hooks/tests.py`, `README.md`, `AGENTS.md`, `docs/product.md`, and this file. Not
changed: `.claude/settings.json`, `hooks/hooks.json`, the content rules, the pre-approved shapes, the
tripwire threshold, the eval-blind rules.

## Tests

The scope pins of step 2, negative-tested as the intent's checks 1 to 6 state. The existing decision
table, the blind rows, the tripwire pins and the process-contract pins run unchanged: `evaluate` keeps its
default `governed=True`, so an event without `cwd` in the existing tests is governed, as the fail-closed
rule says.

## Facts the plan rests on (as of 2026-11-03)

- The hook event carries `cwd`; `strip_cd_to_cwd` reads it already.
- The plugin registers the hook for every session on the machine (`hooks/hooks.json`); the repository
  registers it through `.claude/settings.json`, which is project-scoped. The scope rule applies to both
  registrations the same way, and in a checkout of this repo both give "governed".
- The runner's worktree is a detached checkout of HEAD, so it holds the signature; the eval-blind variable
  governs it in any case.
- `python3 hooks/tests.py` prints "OK: 13 boundary pins hold" on main at the merge of #89; the plugin's
  hook and the repository's hook are the same file.
