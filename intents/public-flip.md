# Intent: the public flip

Work item: #13. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The repository and its lab are public on the same day as the origin post, with no private material (a
home-directory path, a personal-domain e-mail address, a token shape, a session link or a stack slug: the
patterns of check 1) in any tracked file, archived run or tracker item, and with the protection of `main`
in force as the first action after the switch.

## In scope

- The register of the tracked tree: no home-directory path, personal-domain e-mail address, token shape,
  session link or stack slug (the patterns of check 1) in any tracked file, the archived runs under `eval/runs/` included (62 files carry the operator's
  home path in quoted stack traces and recorded commands, as counted on 2026-11-08). The prefix becomes
  `<checkout>` for the lab checkout and `<home>` elsewhere; `eval/BENCHMARK.md` says so in one sentence; the
  claim surfaces, the evidence ids and the timestamps of the archived journals do not change. The five
  earlier journals under `journals/` are the first part of this (their change request is open).
- The links: the two issue links of the README become absolute URLs; every relative link of the tracked
  documents resolves in a clone.
- The tracker: no private material in any issue or pull request, title, body, comment, review or inline
  review comment, open or closed (they become public with the repository); the checklist of #13 ticked as each step lands.
- The repository settings, by the leader: delete-branch-on-merge on; the merged branches deleted; the
  description and the topics set, from a proposal in the change request.
- The lab repository, by the leader with its own session: the register scan (clean on 2026-11-08), the
  LICENSE and NOTICE (added), the README sentence that links this repository (added), the two unpushed
  commits pushed, the author identity of its early commits decided; flipped public in the same motion.
- The posts: the origin post, the LinkedIn version and the Show HN title with its first comment, drafted on
  2026-11-08 in the document "konan public flip: the posts", edited and published by the leader on the day
  of the flip.
- The switch, by the leader: the visibility of both repositories; then, as the first action, the ruleset on
  `main` (deletion, non-fast-forward, linear history) with the command recorded on #13.
- The history, decided by the leader before the switch: three commit messages carry a session link and
  forty-one commits carry a personal e-mail address as the author. A rewrite is a force push, which the
  rules of this repository forbid to the agent; the leader rewrites, or publishes the history as it is.
  This decision replaces the acceptance of the full history recorded on #13 on 2026-08-06, which was
  written before the commits were counted; the checklist line of #13 says the same.

## Out of scope

Required status checks in the ruleset (they wait for eval CI). The publication of the posts and the Show HN
submission are the leader's acts; this intent records their day, it does not automate them. The product
document, the skills, the hook, the scorer, the fixtures. Any change to the lab repository beyond the scan,
the license and the README sentence. The runner's adapter plumbing and the memory isolation of a blinded
worktree session (noted on #58).

## Acceptance checks

### Automatic checks

1. No private material in the tracked tree: home paths, e-mail addresses, token shapes, session links, a
   stack slug in a datasource name. The one test fixture of the hook (`/Users/x/`) is a one-letter user and
   does not match.
   command: `! git grep -I -q -E '/Users/[A-Za-z]{2,}/|/home/[A-Za-z]{2,}/|@gmail\.com|ghp_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|sk-ant-[A-Za-z0-9-]{10,}|AKIA[A-Z0-9]{12,}|glsa_[A-Za-z0-9]{10,}|glc_[A-Za-z0-9+/=]{20,}|claude\.ai/code|grafanacloud-[a-z]+[0-9]{3,}-' -- . ':!intents/public-flip.md' ':!intents/public-flip.plan.md'`
2. The archived runs say that they are redacted, and the README's issue links are absolute.
   command: `grep -q 'checkout>' eval/BENCHMARK.md && ! grep -q '\.\./\.\./issues' README.md && grep -q 'https://github.com/lyudmylan/konan/issues/63' README.md && test "$(grep -o 'https://github.com/lyudmylan/konan/issues/[0-9]*' README.md | wc -l | tr -d ' ')" -ge 2`
3. No private material in the tracker: the titles, bodies, comments, reviews and inline review comments of
   every issue and change request, open or closed, with one pattern for every list and a guard that fails
   when a list is truncated.
   command: `test "$(gh issue list --state all --limit 1000 --json number --jq length)" -lt 1000 && test "$(gh pr list --state all --limit 1000 --json number --jq length)" -lt 1000 && ! { gh issue list --state all --limit 1000 --json title,body,comments --jq '.[] | .title, .body, .comments[].body'; gh pr list --state all --limit 1000 --json title,body,comments,reviews --jq '.[] | .title, .body, .comments[].body, .reviews[].body'; gh api repos/lyudmylan/konan/pulls/comments --paginate --jq '.[].body'; } | grep -q -E '/Users/[A-Za-z]{2,}/|/home/[A-Za-z]{2,}/|@gmail\.com|ghp_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|sk-ant-[A-Za-z0-9-]{10,}|AKIA[A-Z0-9]{12,}|glsa_[A-Za-z0-9]{10,}|glc_[A-Za-z0-9+/=]{20,}|claude\.ai/code|grafanacloud-[a-z]+[0-9]{3,}-'`
   Checks 1 and 3 carry the same pattern, in two places by design: the gate runs each command on its own,
   so a shared variable would break them; a change to the pattern is made to both in the same commit.
4. The lab repository carries the license and the notice, and names this repository.
   command: `gh api repos/lyudmylan/faultline/contents/LICENSE --jq .name | grep -q '^LICENSE$' && gh api repos/lyudmylan/faultline/contents/NOTICE --jq .name | grep -q '^NOTICE$' && gh api repos/lyudmylan/faultline/readme --jq .content | base64 -d | grep -q 'github.com/lyudmylan/konan'`
5. The repository settings: delete-branch-on-merge on, the merged branches gone (only `main` remains, or
   `main` and the branch of the open change request), a description and at least one topic set.
   command: `test "$(gh repo view --json deleteBranchOnMerge --jq .deleteBranchOnMerge)" = true && test "$(gh api repos/lyudmylan/konan/branches --paginate --jq length)" -le 2 && test -n "$(gh repo view --json description --jq .description)" && test "$(gh repo view --json repositoryTopics --jq '.repositoryTopics | length')" -gt 0`
6. The benchmark is on `main` on the day of the switch, as the artifact-first rule of the product document asks
   (`eval/BENCHMARK.md`, `eval/scorecard.md`, and the README links `eval/BENCHMARK.md`); both repositories are
   public; and the ruleset of `main` exists under the name `main-protection`, the name in the command
   recorded on #13 (this check runs after the switch; the rulesets endpoint answers 403
   while the repository is private). That the ruleset was the first action after the switch, and that the benchmark was on `main` before
   it, are not verifiable afterwards; they are the leader's word, recorded on #13.
   command: `test -s eval/BENCHMARK.md && test -s eval/scorecard.md && grep -q 'eval/BENCHMARK.md' README.md && test "$(gh repo view lyudmylan/konan --json visibility --jq .visibility)" = PUBLIC && test "$(gh repo view lyudmylan/faultline --json visibility --jq .visibility)" = PUBLIC && gh api repos/lyudmylan/konan/rulesets --jq '.[].name' | grep -q 'main-protection'`
7. The redaction of the archived runs changes nothing but the prefixes: in the change request that carries
   it, every changed file under `eval/runs/` equals its old version with the two prefixes substituted. The scorer reads
   the claim surface and the evidence references, never a quote, so a score cannot change; a re-score of
   the archive is not one command, because one archived journal is refused by the scorer by design, so the
   diff is the proof. On `main` after the merge the diff is empty and the check holds.
   command: `b=$(git merge-base origin/main HEAD); for f in $(git diff --name-only "$b" -- eval/runs); do git show "$b:$f" | sed -E 's#/Users/[A-Za-z]{2,}/Projects/faultline#<checkout>#g; s#/Users/[A-Za-z]{2,}#<home>#g' | diff -q - "$f" >/dev/null || exit 1; done`
8. The quality checks and the contract checks pass.
   command: `charter-gate quality --contract charter.toml && charter-check all charter.toml`

### Manual checks

9. The origin post and the Show HN submission are published on the day of the flip, with the repository
   link; #13 records the two links. who: the leader. Not automatic: the platforms are outside the
   repository and the acts are the leader's.
10. The history decision is taken for both repositories, this one and the lab, and recorded on #13 before
    the switch: rewritten, or published as it is, with the reason. who: the leader. Not automatic: a rewrite
    is a force push the agent may not make, and the decision is a judgment.
