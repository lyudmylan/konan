# Plan: Charter 0.3.19 and the boundary of a run (#123)

Intent: `intents/charter-factory.md`, checks 1 to 11. The leader gave the word to build and to merge this
work item on 2026-11-25. She reads this plan in the first change request; it was not shown to her before
the files.

## Steps

The first change request, on a branch from the main branch:

1. Run `charter-setup` of 0.3.19 into an empty folder outside the repo, with the values of the contract of
   konan, the source version `v2`, the three quality commands in their new form, and a toolchain file of
   two steps (`astral-sh/setup-uv@v5`, then `uv sync --script eval/tests.py --cache-dir .uv-cache`).
2. Copy `verdict.yml`, `review-intents.yml`, `review-code.yml` and `run.yml` from that folder, and the two
   templates.
3. `charter.toml`: the version 0.3.19, and the comment of `[build]` names `plans/<part>.md`.
4. `.gitignore`: `.uv-cache/` and `.venv/`.
5. `AGENTS.md`, section "Charter": the rule on who merges with the two forms of the link, and the place
   of a plan with the sentence on the plans that exist.
6. Check 8 with the scripts of the tag `charter--v0.3.1`; the quality gate of 0.3.19 with `--repo-only`,
   as the workflow `tests` runs it.
7. The review loop on the change request, then the merge on the leader's word.

The second change request, on a branch from the main branch after the first merge:

8. `charter.toml`: the source `v2`, `review.code_blocks`, `documents.absent`, `[boundary]`,
   `checks.no_product_reason`, and the first quality command.
9. `tests.yml` from the folder of step 1.
10. `AGENTS.md`: the other rules of the section "Charter", the paragraph on a run in this repo, the
    quality command and the step that fills the cache in the sections "Workflow" and "Commands".
11. Checks 1 to 7 and 11 on the branch; checks 9 and 10 on the change request.
12. One issue for the risk that the intent leaves open: the boundary hook freezes a run after two
    denials.

## Files

First: `charter.toml`, `.github/workflows/verdict.yml`, `.github/workflows/review-intents.yml`,
`.github/workflows/review-code.yml`, `.github/workflows/run.yml`, `intents/_template.md`,
`plans/_template.md`, `.gitignore`, `AGENTS.md`, `intents/charter-factory.md`, and this file.

Second: `charter.toml`, `.github/workflows/tests.yml`, `AGENTS.md`.

## Tests

None added. The quality commands do not change what they test; the first one changes its flags. The
checks of the intent are commands on the contract and on the files, and the checks of the code host.
