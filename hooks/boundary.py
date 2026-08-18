#!/usr/bin/env python3
"""konan boundary hook — the read-only boundary as a content-based PreToolUse guard.

Runs before every Bash tool call (registered in .claude/settings.json; a plugin ships
it via hooks/hooks.json). It reads the WHOLE command string, not a prefix, and returns
one of three decisions:

  deny  — a raw network client anywhere in the command (curl, wget, http, xh, nc, …,
          inline python/node/ruby/perl network calls, /dev/tcp), an operator surface
          (/simulate, /chaos) by any route other than scripts/scenario.sh, or a
          destructive git push form (--force, -f, --force-with-lease, --delete, :ref).
  allow — exactly the pre-approved shapes an unattended shift needs: a single
          scripts/probe.sh call, `git add journals/…`, `git commit -m "…"`.
  (none) — everything else takes the normal permission flow: settings rules, then a
          prompt; an unattended shift fails closed on a prompt (docs: AGENTS.md).

Eval-blind mode (`KONAN_EVAL_BLIND=1`, set by eval/run.py): the blinding contract of
eval/README.md becomes mechanical — Bash commands that call `gh`, mention `eval/` paths,
the faultline checkout, or run git against eval are denied; Read/Grep/Glob/Edit/Write
calls whose path fields point under `eval/` or into faultline are denied. Outside eval
mode those tools get no decision from this hook.

Tripwire: the second denial in one session freezes the session — every further Bash
call is denied with a reason telling the agent to stop and page a human. A denied
action is a signal to stop, never a puzzle to solve. Threshold: KONAN_BOUNDARY_TRIP
(default 2); state lives in the temp dir, keyed by session id.

Deterministic on purpose: same input, same output; no model in the loop. Stdlib only —
python3 is the only dependency, so plugin consumers need nothing else. Pins:
`python3 hooks/tests.py`. Semantics: AGENTS.md (lab boundary). Fails closed on any
internal error.
"""
import json
import os
import re
import sys
import tempfile

# --- deny: raw network clients, as shell words anywhere in the command ---------------
# A "word start" is the command start or a shell separator/prefix boundary; a path prefix
# (/usr/bin/curl) or an env/`sudo`/`timeout` prefix still ends in the bare word.
_WORD_START = r"(?:^|[\s;&|(){}`\"']|/)"
_NET_CLIENTS = r"(?:curl|wget|xh|nc|ncat|netcat|telnet|socat|openssl)"
RE_NET_CLIENT = re.compile(_WORD_START + _NET_CLIENTS + r"(?=$|[\s;&|)}`\"'])")
# HTTPie's `http`/`https` as a COMMAND word only — never the scheme inside a URL
# (`http://…` has a colon right after the word).
RE_HTTPIE = re.compile(_WORD_START + r"https?(?=\s)")
# Inline interpreters reaching for a network module in the same command.
RE_INLINE_NET = re.compile(
    r"(?:python[0-9.]*|node|ruby|perl)\s+-[ec]\b.*"
    r"(?:urllib|requests|http\.client|httpx|aiohttp|socket|fetch\(|http\.request|"
    r"net\.connect|Net::HTTP|LWP|IO::Socket)",
    re.S,
)
RE_DEV_TCP = re.compile(r"/dev/(?:tcp|udp)/")
# --- deny: operator surfaces by any route ------------------------------------------
RE_OPERATOR_SURFACE = re.compile(r"/(?:simulate|chaos)(?=$|[/?\s\"';&|)])")
# --- deny: destructive git push forms ----------------------------------------------
RE_GIT_PUSH_DESTRUCTIVE = re.compile(
    r"\bgit\s+push\b[^;&|]*?"
    r"(?:\s--force(?:-with-lease)?\b|\s-f\b|\s--delete\b|\s--prune\b|\s--mirror\b|\s\+\S+|\s:\S+)"
)
# --- eval-blind mode: the blinding contract, mechanical ------------------------------------
RE_BLIND_BASH = re.compile(
    r"(?:(?:^|[\s;&|(){}`\"'])gh(?=$|[\s;&|)}`\"'])"          # the issue tracker
    r"|(?:^|[\s\"'=:(<])(?:\./)?eval/"                        # ground truth on disk
    r"|\.\./faultline|(?:^|[\s\"'=:(</])faultline/|FAULTLINE_DIR"  # the lab's own checkout
    r"|\bgit\b[^;&|]*\beval\b)"                                # git against eval
)
BLIND_TOOLS = {"Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit"}
PATH_FIELDS = ("file_path", "path", "notebook_path", "glob", "pattern")


def blind_path_violation(tool_name: str, tool_input: dict) -> bool:
    """Pure: does a file-tool call reach into eval/ or the faultline checkout?"""
    if tool_name not in BLIND_TOOLS:
        return False
    for f in PATH_FIELDS:
        if f == "pattern" and tool_name != "Glob":
            continue  # Grep's pattern is text, not a path
        v = (tool_input or {}).get(f)
        if not isinstance(v, str) or not v:
            continue
        norm = v.replace("\\", "/")
        if norm.startswith("eval/") or norm == "eval" or "/eval/" in norm or norm.endswith("/eval") \
                or "faultline/" in norm or norm.endswith("/faultline") or norm.startswith("../faultline"):
            return True
    return False


# --- allow: exact pre-approved shapes (no chaining, no subshells) --------------------
RE_ALLOW_PROBE = re.compile(r"^\s*(?:\./)?scripts/probe\.sh\s+/[^\s;&|<>`$()]*\s*$")
RE_ALLOW_GIT_ADD = re.compile(r"^\s*git\s+add\s+(?:journals/[^\s;&|<>`$()]+\s*)+$")
RE_ALLOW_GIT_COMMIT = re.compile(
    r"^\s*git\s+commit(?:\s+-m\s+(?:\"[^\"`$]*\"|'[^']*'))+\s*$", re.S
)


def decide(command: str, blind: bool = False) -> tuple[str | None, str]:
    """Return (decision, reason). decision is 'deny', 'allow', or None (normal flow).

    Order matters: operator surfaces are denied even in a pre-approved shape; the
    pre-approved shapes are then allowed before content checks, because their quoted
    text cannot execute (no subshell, no backtick, no `$` inside the quotes) — a commit
    message that mentions curl is not a network call; everything else is denied by
    content or left to the normal flow."""
    cmd = command or ""
    if RE_OPERATOR_SURFACE.search(cmd):
        return "deny", ("boundary: /simulate and /chaos are operator surface, not telemetry — "
                        "eval-side only via scripts/scenario.sh (prompts by design)")
    if blind and RE_BLIND_BASH.search(cmd):
        return "deny", ("boundary (eval-blind): the tracker, eval/ fixtures, and the lab checkout are "
                        "out of bounds for an evaluated investigation (eval/README.md, blinding contract)")
    if RE_ALLOW_PROBE.match(cmd) or RE_ALLOW_GIT_ADD.match(cmd) or RE_ALLOW_GIT_COMMIT.match(cmd):
        return "allow", "boundary: pre-approved shape"
    if RE_DEV_TCP.search(cmd):
        return "deny", "boundary: raw socket via /dev/tcp is outside the read-only surface"
    if RE_NET_CLIENT.search(cmd) or RE_HTTPIE.search(cmd) or RE_INLINE_NET.search(cmd):
        return "deny", ("boundary: raw network clients are denied by content — the only hand "
                        "on a target is scripts/probe.sh (docs/lab.md)")
    if RE_GIT_PUSH_DESTRUCTIVE.search(cmd):
        return "deny", "boundary: force-push and remote-branch deletion forms are denied"
    return None, ""


# --- tripwire state ------------------------------------------------------------------
def _state_path(session_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "unknown")
    return os.path.join(tempfile.gettempdir(), f"konan-boundary-{safe}.json")


def _load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"denials": 0, "frozen": False}


def _save(path: str, state: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, path)


RE_CD_PREFIX = re.compile(r'^\s*cd\s+(?:"([^"]+)"|\'([^\']+)\'|(\S+))\s*&&\s*(.*)$', re.S)


def strip_cd_to_cwd(command: str, cwd: str | None) -> str:
    """Pure: `cd <dir> && rest` → `rest` when <dir> is the session's own cwd — the
    harness idiom for subagents; same surface, different syntax. Any other target
    leaves the command untouched (and thus outside the pre-approved shapes)."""
    if not cwd:
        return command
    m = RE_CD_PREFIX.match(command or "")
    if not m:
        return command
    target = next(g for g in m.groups()[:3] if g is not None)
    try:
        same = os.path.realpath(target) == os.path.realpath(cwd)
    except (OSError, ValueError):
        same = False
    return m.group(4) if same else command


def evaluate(event: dict, state: dict, trip: int, blind: bool = False) -> tuple[str | None, str, dict]:
    """Pure decision over (event, state) → (decision, reason, new_state)."""
    tool = event.get("tool_name")
    if tool != "Bash":
        if blind and blind_path_violation(tool, event.get("tool_input") or {}):
            state = dict(state)
            state["denials"] = int(state.get("denials", 0)) + 1
            reason = ("boundary (eval-blind): eval/ and the lab checkout are out of bounds for an "
                      "evaluated investigation (eval/README.md, blinding contract)")
            if state["denials"] >= trip:
                state["frozen"] = True
                reason += f" — {state['denials']} denials in this session: the session is now frozen; stop"
            return "deny", reason, state
        return None, "", state
    if state.get("frozen"):
        return ("deny",
                "boundary: session frozen after repeated denials — stop, record the wall in "
                "your report, and page a human; a fresh session is required",
                state)
    command = strip_cd_to_cwd((event.get("tool_input") or {}).get("command", ""), event.get("cwd"))
    decision, reason = decide(command, blind)
    if decision == "deny":
        state = dict(state)
        state["denials"] = int(state.get("denials", 0)) + 1
        if state["denials"] >= trip:
            state["frozen"] = True
            reason += (f" — {state['denials']} denials in this session: the session is now "
                       "frozen; stop and page a human")
        else:
            reason += " — this is a signal to stop and page, never a puzzle to solve"
    return decision, reason, state


def _emit(decision: str | None, reason: str) -> None:
    if decision is None:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))


def main() -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
        if not isinstance(event, dict):
            raise ValueError("hook input is not an object")
    except Exception as exc:  # fail closed: unreadable input never opens the boundary
        _emit("deny", f"boundary: unreadable hook input ({exc.__class__.__name__}) — failing closed")
        return 0
    try:
        trip = max(1, int(os.environ.get("KONAN_BOUNDARY_TRIP", "2")))
        blind = os.environ.get("KONAN_EVAL_BLIND") == "1"
        path = _state_path(str(event.get("session_id", "")))
        decision, reason, new_state = evaluate(event, _load(path), trip, blind)
        if new_state is not None and decision == "deny":
            _save(path, new_state)
        _emit(decision, reason)
        return 0
    except Exception as exc:  # fail closed
        _emit("deny", f"boundary: internal error ({exc.__class__.__name__}) — failing closed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
