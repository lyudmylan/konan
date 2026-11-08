# Intent: the scope of the boundary hook

Work item: #74. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The boundary hook governs a konan workspace and is silent everywhere else, so a developer who installs the
plugin keeps the read-only boundary on a target and loses nothing on other projects.

## In scope

- `hooks/boundary.py`: a scope decision before every other decision, from the `cwd` of the hook event. A
  session is inside a konan workspace when its `cwd`, or any parent directory of it up to the filesystem
  root, holds `docs/triggers.md` and `skills/investigate/` (a checkout of this repo, the runner's worktree
  included) or the marker file `.konan-workspace` (a target that an adapter onboarded), or when
  `KONAN_BOUNDARY=1` or `KONAN_EVAL_BLIND=1` is set in the environment. The walk up the parents is the
  rule because the `cwd` of a session is its current directory, not the root of the project: a session
  that moved into a subdirectory of a workspace stays governed. Outside a workspace the hook returns no
  decision, for every tool and every command, frozen or not, and the tripwire counts nothing: the freeze
  belongs to the workspace. An event without `cwd` is governed: the hook fails closed, on the deny side,
  as it does on unreadable input. The `cd <dir> &&` prefix keeps its rule: the scope is the session's
  `cwd`, not the target of the `cd`. The docstring states the scope.
- `hooks/tests.py`: the scoped rows, negative-tested through the same path the process takes (`cwd` into
  the scope function into the decision): the same commands governed inside a workspace and silent outside
  it; a subdirectory of a workspace governed; the marker alone governs; each override governs; no `cwd`
  governs; the tripwire outside a workspace stays at zero; the process contract outside a workspace prints
  nothing. The closing line counts the new pins.
- `README.md`, "Install as a plugin": the scope in two sentences (where the hook decides, how to force it
  on). `AGENTS.md`, "Lab boundary": one sentence that names the scope and points to the README section,
  so the definition lives in one place. The eval-blind mode and the settings registration of this repo do
  not change.
- `docs/product.md`: the enterprise-distribution line of the roadmap ("the plugin lands in v0.2
  (methodology + boundary hook; ...)") names the scope of the plugin's hook, because `hooks/**` is a code
  path of the contract.
- The adapter marker is defined here; the adapter skill writes it when #52 lands (noted on #52).

## Out of scope

The adapter skill (#52). The permission lists of `.claude/settings.json`: they are scoped to this repo already.
A change to the content rules of the hook, to the pre-approved shapes, or to the tripwire threshold. The
marketplace files of the plugin.

## Acceptance checks

## Automatic checks

1. Outside a workspace, a command that the content rules deny inside one gets no decision: the pin runs the
   denied rows of the decision table with an empty temporary directory as `cwd`, through the scope function
   into the decision, and expects silence; the same rows with a directory that holds the marker expect the
   decision of the table.
   test: `hooks/tests.py`, the pin "scope: silent outside a workspace". command: `python3 hooks/tests.py`
2. Inside a checkout of this repo the decision table is unchanged: every existing row of `PINS` and
   `BLIND_PINS` holds with the scope granted, and a process pin with the repository as `cwd` returns the
   table decision for one denied row.
   test: `hooks/tests.py`, `test_decision_table`, `test_blind_mode_decision_table`, and the pin "scope:
   the repository governs".
3. The marker `.konan-workspace` alone governs a directory; `KONAN_BOUNDARY=1` governs any directory;
   `KONAN_EVAL_BLIND=1` governs any directory.
   test: `hooks/tests.py`, the pins "scope: marker", "scope: force-on", "scope: eval mode".
4. A subdirectory of a workspace is governed: the pin runs a denied row with a `cwd` two levels below a
   directory that holds the marker, and two levels below a directory that holds the signature, and expects
   the table decision in both.
   test: `hooks/tests.py`, the pin "scope: subdirectory of a workspace governs".
5. An event without `cwd` is governed.
   test: `hooks/tests.py`, the pin "scope: no cwd fails closed".
6. Outside a workspace the tripwire counts nothing: two commands that the content rules deny leave the
   state at zero denials and not frozen.
   test: `hooks/tests.py`, the pin "scope: tripwire untouched".
7. The process contract: `python3 hooks/boundary.py` with an event whose `cwd` is an empty temporary
   directory prints nothing for a raw network client; with a workspace `cwd` it prints the deny JSON. The
   pins build the environment of the process explicitly, with `KONAN_BOUNDARY` and `KONAN_EVAL_BLIND`
   removed, and set them only in the rows of check 3.
   test: `hooks/tests.py`, the pin "scope: process silence".
8. The README, the repository instructions and the product document state the scope: the README names the
   marker, the instructions name the marker and point to the README section, and the enterprise-
   distribution line of the product document names the workspace scope.
   command: `grep -q 'konan-workspace' README.md && grep -q 'konan-workspace' AGENTS.md && tr "\n" " " < docs/product.md | grep -q "scoped to a konan workspace"`
   (the product line is hard-wrapped, so the file is read with the line breaks removed)
9. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

10. With the plugin installed on the operator computer, a raw network client in a directory that is not a
    workspace is not denied, and the same command in a checkout of this repo is denied. who: the engineer.
    Not automatic: it needs the plugin installed and a session outside the repository; the receipt of #57
    showed the denial that this check reverses.
