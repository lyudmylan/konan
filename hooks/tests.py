#!/usr/bin/env python3
"""Decision pins for the boundary hook. Plain asserts, stdlib only: `python3 hooks/tests.py`.

Each pin fixes one rule of the read-only boundary (AGENTS.md → Lab boundary): what is
denied by content, what is pre-approved by exact shape, what falls through to the normal
permission flow, and how the tripwire freezes a session. A future edit that drifts the
boundary fails loudly here — negative-tested, like the scorer's pins."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boundary  # noqa: E402

DENY, ALLOW, FLOW = "deny", "allow", None

# (command, expected decision) — the boundary as a table.
PINS = [
    # pre-approved shapes → allow (the unattended shift never prompts on these)
    ("scripts/probe.sh /health", ALLOW),
    ("./scripts/probe.sh /products/3", ALLOW),
    ("scripts/probe.sh /metrics", ALLOW),
    ("scripts/probe.sh /orders?limit=5", ALLOW),
    ('git add journals/2026-08-06-overnight-latency-flag.md', ALLOW),
    ('git commit -m "journal: 2026-08-06 HighErrorRate — root cause identified"', ALLOW),
    ("git commit -m 'journal: verdict' -m 'second paragraph'", ALLOW),
    ('git commit -m "journal: probes go through probe.sh, which wraps curl"', ALLOW),   # a word in a message is not a call
    ("git add journals/2026-08-18-curl-notes.md", ALLOW),
    # raw network clients anywhere in the command → deny, whatever the prefix or wrapper
    ("curl http://127.0.0.1:8000/health", DENY),
    ("/usr/bin/curl -s http://127.0.0.1:8000/health", DENY),
    ('bash -c "curl http://127.0.0.1:8000/products/3"', DENY),
    ("sudo curl http://127.0.0.1:8000/health", DENY),
    ("env X=1 curl http://127.0.0.1:8000/health", DENY),
    ("timeout 5 curl http://127.0.0.1:8000/health", DENY),
    ("A=1; curl http://127.0.0.1:8000/health", DENY),
    ("scripts/probe.sh /health && curl http://127.0.0.1:8000/chaos", DENY),
    ("echo hi | curl -d @- http://127.0.0.1:8000/orders", DENY),
    ("$(curl http://127.0.0.1:8000/health)", DENY),
    ('git commit -m "$(curl http://127.0.0.1:8000/health)"', DENY),                  # subshell in the message: not a pre-approved shape
    ("git commit -m `curl http://127.0.0.1:8000/health`", DENY),
    ("wget -qO- http://127.0.0.1:8000/health", DENY),
    ("nc -z 127.0.0.1 8000", DENY),
    ("ncat 127.0.0.1 8000", DENY),
    ("telnet 127.0.0.1 8000", DENY),
    ("socat - TCP:127.0.0.1:8000", DENY),
    ("openssl s_client -connect 127.0.0.1:8000", DENY),
    ("http GET :8000/health", DENY),
    ("https example.com/health", DENY),
    ("xh :8000/health", DENY),
    ('python3 -c "import urllib.request as u; print(u.urlopen(\'http://127.0.0.1:8000/health\').read())"', DENY),
    ('python -c "import requests; requests.get(\'http://127.0.0.1:8000/orders\')"', DENY),
    ('node -e "fetch(\'http://127.0.0.1:8000/health\').then(r=>r.text()).then(console.log)"', DENY),
    ("perl -e 'use LWP::Simple; print get(\"http://127.0.0.1:8000/health\")'", DENY),
    ("exec 3<>/dev/tcp/127.0.0.1/8000; echo -e 'GET /health HTTP/1.0\\n' >&3", DENY),
    # operator surfaces by any route → deny (probe.sh refuses them too; the hook is earlier)
    ("scripts/probe.sh /chaos", DENY),
    ("scripts/probe.sh /simulate/status/500", DENY),
    ("cat lab/logs/app.log | grep /chaos/enable", DENY),
    # destructive git push forms → deny
    ("git push --force origin main", DENY),
    ("git push -f origin main", DENY),
    ("git push --force-with-lease origin main", DENY),
    ("git push --delete origin 47-boundary-hook", DENY),
    ("git push origin :47-boundary-hook", DENY),
    ("git push origin +main", DENY),                                              # plus-refspec is a force push
    ("git push --prune origin", DENY),
    ("git push --mirror origin", DENY),
    # everything else → normal permission flow (settings rules, then a prompt)
    ("ls -la", FLOW),
    ("git status", FLOW),
    ("git push origin 47-boundary-hook", FLOW),
    ("git push -u origin main", FLOW),
    ("git push origin HEAD:main", FLOW),                                          # a colon inside a refspec is not deletion
    ("scripts/scenario.sh chaos-on 0.3 503", FLOW),
    ("scripts/scenario.sh sim status/500", FLOW),
    ("scripts/alert.sh 'HighErrorRate' HighErrorRate critical", FLOW),
    ("scripts/lab.sh start", FLOW),
    ("grep -c '\"status\": 500' lab/logs/app.log", FLOW),
    ("tail -n 20 lab/logs/app.log", FLOW),
    ("KONAN_LAB_BASE=http://127.0.0.1:8000 scripts/probe.sh /health", FLOW),   # URL scheme is not the http command
    ('echo "see https://example.com/docs"', FLOW),                                # scheme inside text, not a client
    ("scripts/probe.sh /metrics | grep http_requests_total", FLOW),               # piped: not the exact shape, not a violation
    ("scripts/probe.sh /health; ls", FLOW),                                       # chained: same
    ("git add journals/x.md README.md", FLOW),                                    # widened add: not pre-approved
    ('git commit -m "$(cat <<EOF\nmsg\nEOF\n)"', FLOW),                           # subshell in the message: not pre-approved
    ("git commit -am 'x'", FLOW),
    ("python3 eval/score.py --pair eval/scenarios/x.yaml journals/x.md", FLOW),
    ("uv run eval/tests.py", FLOW),
]


def test_decision_table():
    failures = []
    for cmd, expected in PINS:
        got, _ = boundary.decide(cmd)
        if got != expected:
            failures.append(f"  {cmd!r}: expected {expected}, got {got}")
    assert not failures, "decision table drift:\n" + "\n".join(failures)


def _event(cmd, tool="Bash", session="s-test"):
    return {"session_id": session, "hook_event_name": "PreToolUse", "tool_name": tool,
            "tool_input": {"command": cmd}}


def test_non_bash_tools_are_not_the_hooks_business():
    d, _, _ = boundary.evaluate({"tool_name": "Read", "tool_input": {"file_path": "x"}}, {}, 2)
    assert d is None


def test_tripwire_freezes_after_second_denial():
    st = {"denials": 0, "frozen": False}
    d1, r1, st = boundary.evaluate(_event("curl x"), st, 2)
    assert d1 == "deny" and st["denials"] == 1 and not st["frozen"] and "signal to stop" in r1
    d2, r2, st = boundary.evaluate(_event("wget x"), st, 2)
    assert d2 == "deny" and st["denials"] == 2 and st["frozen"] and "frozen" in r2
    d3, r3, st = boundary.evaluate(_event("ls"), st, 2)              # harmless, but the session is frozen
    assert d3 == "deny" and "frozen" in r3
    d4, _, _ = boundary.evaluate(_event("scripts/probe.sh /health"), st, 2)  # even pre-approved shapes
    assert d4 == "deny"


def test_tripwire_threshold_is_configurable():
    st = {"denials": 0, "frozen": False}
    d, _, st = boundary.evaluate(_event("curl x"), st, 1)
    assert d == "deny" and st["frozen"]


def test_allow_and_flow_do_not_touch_the_counter():
    st = {"denials": 1, "frozen": False}
    d, _, st2 = boundary.evaluate(_event("scripts/probe.sh /health"), st, 2)
    assert d == "allow" and st2 == st
    d, _, st3 = boundary.evaluate(_event("ls"), st, 2)
    assert d is None and st3 == st


SCOPE_ENV = ("KONAN_BOUNDARY", "KONAN_EVAL_BLIND")


def _hook_env(tmp, extra=None):
    """The environment of a hook process, built explicitly (intents/hook-scope.md, check 7):
    the runner's environment without the two scope variables (an eval session or the
    runner sets them), a private TMPDIR, then the pin's own variables."""
    env = {k: v for k, v in os.environ.items() if k not in SCOPE_ENV}
    env["TMPDIR"] = tmp
    env.update(extra or {})
    return env


def _run_hook(stdin_text, env_extra=None):
    env = _hook_env(tempfile.mkdtemp(prefix="konan-hook-test-"), env_extra)
    p = subprocess.run([sys.executable, str(HERE / "boundary.py")], input=stdin_text,
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout.strip(), p.stderr


def test_process_contract_deny_json():
    rc, out, _ = _run_hook(json.dumps(_event('bash -c "curl http://127.0.0.1:8000/health"')))
    assert rc == 0
    payload = json.loads(out)["hookSpecificOutput"]
    assert payload["hookEventName"] == "PreToolUse" and payload["permissionDecision"] == "deny"
    assert "scripts/probe.sh" in payload["permissionDecisionReason"]


def test_process_contract_allow_and_silence():
    rc, out, _ = _run_hook(json.dumps(_event("scripts/probe.sh /health")))
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "allow"
    rc, out, _ = _run_hook(json.dumps(_event("ls")))
    assert rc == 0 and out == ""            # no decision → normal permission flow


def test_process_contract_fails_closed_on_garbage():
    rc, out, _ = _run_hook("this is not json")
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_process_tripwire_persists_across_calls():
    tmp = tempfile.mkdtemp(prefix="konan-hook-test-")
    env = _hook_env(tmp)
    def run(cmd):
        p = subprocess.run([sys.executable, str(HERE / "boundary.py")],
                           input=json.dumps(_event(cmd, session="s-persist")),
                           capture_output=True, text=True, env=env)
        return json.loads(p.stdout)["hookSpecificOutput"] if p.stdout.strip() else None
    assert run("curl x")["permissionDecision"] == "deny"
    assert run("wget x")["permissionDecision"] == "deny"
    frozen = run("ls")
    assert frozen and frozen["permissionDecision"] == "deny" and "frozen" in frozen["permissionDecisionReason"]


# --- eval-blind mode (KONAN_EVAL_BLIND=1): the blinding contract, mechanical --------------
BLIND_PINS = [
    # denied in blind mode
    ("gh issue view 12", DENY),
    ("cat eval/scenarios/d1-zero-stock-product-page.yaml", DENY),
    ("ls eval/", DENY),
    ("grep -r zero eval/scenarios", DENY),
    ("cat ../faultline/SPEC.md", DENY),
    ("ls /Users/x/Projects/faultline/", DENY),
    ("FAULTLINE_DIR=../faultline scripts/lab.sh status", DENY),
    ("git show HEAD:eval/scenarios/x.yaml", DENY),
    ("git log -- eval", DENY),
    # still fine in blind mode
    ("scripts/probe.sh /health", ALLOW),
    ("tail -n 50 lab/logs/app.log", FLOW),
    ("grep -c evaluated lab/logs/app.log", FLOW),          # the word, not the directory
    ("git status", FLOW),
    ("ls journals/", FLOW),
]


def test_blind_mode_decision_table():
    failures = []
    for cmd, expected in BLIND_PINS:
        got, _ = boundary.decide(cmd, blind=True)
        if got != expected:
            failures.append(f"  {cmd!r}: expected {expected}, got {got}")
    for cmd, expected in BLIND_PINS:          # outside blind mode these are not specially denied
        if expected == DENY:
            got, _ = boundary.decide(cmd, blind=False)
            if got == DENY:
                failures.append(f"  {cmd!r}: denied outside blind mode (should be flow/allow)")
    assert not failures, "blind decision table drift:\n" + "\n".join(failures)


def test_blind_mode_file_tools():
    ev = lambda tool, inp: {"session_id": "s-b", "tool_name": tool, "tool_input": inp}
    st = {"denials": 0, "frozen": False}
    d, r, st = boundary.evaluate(ev("Read", {"file_path": "eval/scenarios/x.yaml"}), st, 2, blind=True)
    assert d == "deny" and "eval-blind" in r and st["denials"] == 1
    d, _, st = boundary.evaluate(ev("Read", {"file_path": "/abs/konan/eval/fixture.schema.json"}), st, 2, blind=True)
    assert d == "deny" and st["frozen"]                       # second denial freezes, file tools too
    st = {"denials": 0, "frozen": False}
    d, _, _ = boundary.evaluate(ev("Grep", {"pattern": "eval", "path": "lab/logs"}), st, 2, blind=True)
    assert d is None                                          # Grep pattern is text, path is fine
    d, _, _ = boundary.evaluate(ev("Glob", {"pattern": "eval/**/*.yaml"}), st, 2, blind=True)
    assert d == "deny"
    d, _, _ = boundary.evaluate(ev("Read", {"file_path": "../faultline/SPEC.md"}), st, 2, blind=True)
    assert d == "deny"
    d, _, _ = boundary.evaluate(ev("Read", {"file_path": "docs/lab.md"}), st, 2, blind=True)
    assert d is None
    d, _, _ = boundary.evaluate(ev("Read", {"file_path": "eval/scenarios/x.yaml"}), st, 2, blind=False)
    assert d is None                                          # outside blind mode: not the hook's business


def test_process_blind_env():
    rc, out, _ = _run_hook(json.dumps(_event("gh issue list")), {"KONAN_EVAL_BLIND": "1"})
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"
    rc, out, _ = _run_hook(json.dumps(_event("gh issue list")))
    assert rc == 0 and out == ""                              # no env → normal flow
    ev = {"session_id": "s-e", "tool_name": "Read", "tool_input": {"file_path": "eval/README.md"}}
    rc, out, _ = _run_hook(json.dumps(ev), {"KONAN_EVAL_BLIND": "1"})
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_cd_prefix_to_session_cwd_is_transparent():
    ev = lambda cmd, cwd: {"session_id": "s-cd", "tool_name": "Bash", "cwd": cwd, "tool_input": {"command": cmd}}
    st = {"denials": 0, "frozen": False}
    d, _, _ = boundary.evaluate(ev('cd "/tmp" && scripts/probe.sh /health', "/tmp"), st, 2)
    assert d == "allow"                                       # same dir: pre-approved shape survives
    d, _, _ = boundary.evaluate(ev("cd /tmp && scripts/probe.sh /health", "/tmp"), st, 2)
    assert d == "allow"
    d, _, _ = boundary.evaluate(ev('cd "/tmp/elsewhere" && scripts/probe.sh /health', "/tmp"), st, 2)
    assert d is None                                          # another dir: not pre-approved
    d, _, _ = boundary.evaluate(ev('cd "/tmp" && curl http://127.0.0.1:8000/health', "/tmp"), st, 2)
    assert d == "deny"                                        # deny by content still applies
    d, _, _ = boundary.evaluate(ev("scripts/probe.sh /health", None), st, 2)
    assert d == "allow"                                       # no cwd in the event: nothing stripped


# --- scope (intents/hook-scope.md): the hook decides only inside a konan workspace ---------
REPO = HERE.parent


def _outside_dir():
    """An empty temporary directory: not a workspace, and under no workspace."""
    d = tempfile.mkdtemp(prefix="konan-outside-")
    assert not boundary.in_workspace(d, {}), \
        f"{d} lies inside a workspace; the scope pins need a temp dir outside one"
    return d


def _marker_dir():
    d = tempfile.mkdtemp(prefix="konan-marker-")
    Path(d, boundary.WORKSPACE_MARKER).touch()
    return d


def _signature_dir():
    d = tempfile.mkdtemp(prefix="konan-signature-")
    sig_file, sig_dir = boundary.WORKSPACE_SIGNATURE
    Path(d, sig_file).parent.mkdir(parents=True, exist_ok=True)
    Path(d, sig_file).write_text("# triggers\n")
    Path(d, sig_dir).mkdir(parents=True, exist_ok=True)
    return d


def _scoped(cmd, cwd, env=None, state=None):
    """The path the process takes, in-process: cwd and env into the scope, then the decision."""
    env = env or {}
    ev = _event(cmd)
    if cwd is not None:
        ev["cwd"] = cwd
    st = state if state is not None else {"denials": 0, "frozen": False}
    governed = boundary.in_workspace(cwd, env)
    return boundary.evaluate(ev, st, 2, blind=env.get("KONAN_EVAL_BLIND") == "1", governed=governed)


def test_scope_silent_outside_a_workspace():
    """Check 1: every row of the table gets no decision outside a workspace (frozen or not)
    and its table decision inside one; the target of a `cd` does not move the scope."""
    outside, marker = _outside_dir(), _marker_dir()
    failures = []
    for cmd, expected in PINS:
        got, _, _ = _scoped(cmd, outside)
        if got is not None:
            failures.append(f"  {cmd!r}: outside a workspace expected silence, got {got}")
        got, _, _ = _scoped(cmd, marker)
        if got != expected:
            failures.append(f"  {cmd!r}: inside a workspace expected {expected}, got {got}")
    assert not failures, "scope drift:\n" + "\n".join(failures)
    d, _, _ = _scoped("ls", outside, state={"denials": 2, "frozen": True})
    assert d is None                                          # a frozen state means nothing outside
    d, _, _ = _scoped(f"cd {marker} && curl x", outside)
    assert d is None                                          # the scope is the session's cwd, not the cd target


def test_scope_the_repository_governs():
    """Check 2: a checkout of this repo is a workspace; every row keeps its table decision
    with the scope granted, and the hook process with the repository as cwd prints the
    deny JSON for a denied row."""
    assert boundary.in_workspace(str(REPO), {})
    failures = [f"  {cmd!r}: expected {expected}, got {got}"
                for cmd, expected in PINS
                for got in [_scoped(cmd, str(REPO))[0]] if got != expected]
    assert not failures, "decision table drift inside the repository:\n" + "\n".join(failures)
    rc, out, _ = _run_hook(json.dumps(dict(_event("curl x"), cwd=str(REPO))))
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_scope_marker():
    """Check 3: the marker alone governs a directory."""
    marker = _marker_dir()
    assert boundary.in_workspace(marker, {})
    d, _, _ = _scoped("curl x", marker)
    assert d == "deny"
    d, _, _ = _scoped("scripts/probe.sh /health", marker)
    assert d == "allow"


def test_scope_force_on():
    """Check 3: KONAN_BOUNDARY=1 governs any directory, in-process and in the process."""
    outside = _outside_dir()
    assert boundary.in_workspace(outside, {"KONAN_BOUNDARY": "1"})
    assert not boundary.in_workspace(outside, {"KONAN_BOUNDARY": "0"})
    d, _, _ = _scoped("curl x", outside, {"KONAN_BOUNDARY": "1"})
    assert d == "deny"
    rc, out, _ = _run_hook(json.dumps(dict(_event("curl x"), cwd=outside)), {"KONAN_BOUNDARY": "1"})
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_scope_eval_mode():
    """Check 3: KONAN_EVAL_BLIND=1 governs any directory, with the blind rules on."""
    outside = _outside_dir()
    assert boundary.in_workspace(outside, {"KONAN_EVAL_BLIND": "1"})
    d, _, _ = _scoped("curl x", outside, {"KONAN_EVAL_BLIND": "1"})
    assert d == "deny"
    d, r, _ = _scoped("gh issue list", outside, {"KONAN_EVAL_BLIND": "1"})
    assert d == "deny" and "eval-blind" in r
    rc, out, _ = _run_hook(json.dumps(dict(_event("gh issue list"), cwd=outside)), {"KONAN_EVAL_BLIND": "1"})
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_scope_subdirectory_of_a_workspace_governs():
    """Check 4: a cwd two levels below the marker, and two levels below the signature."""
    for root in (_marker_dir(), _signature_dir()):
        below = Path(root, "lab", "logs")
        below.mkdir(parents=True)
        assert boundary.in_workspace(str(below), {})
        d, _, _ = _scoped("curl x", str(below))
        assert d == "deny"
    assert not boundary.in_workspace(str(Path(_outside_dir(), "a", "b")), {})   # nothing above: silent


def test_scope_no_cwd_fails_closed():
    """Check 5: an event without cwd is governed."""
    assert boundary.in_workspace(None, {}) and boundary.in_workspace("", {})
    d, _, _ = _scoped("curl x", None)
    assert d == "deny"
    d, _, _ = _scoped("curl x", "")
    assert d == "deny"


def test_scope_tripwire_untouched():
    """Check 6: outside a workspace two denied-by-content commands leave the state at zero,
    in-process and in the process: no state file, and a later governed call is not frozen."""
    outside, marker = _outside_dir(), _marker_dir()
    st = {"denials": 0, "frozen": False}
    d, _, st = _scoped("curl x", outside, state=st)
    assert d is None
    d, _, st = _scoped("wget x", outside, state=st)
    assert d is None and st == {"denials": 0, "frozen": False}
    tmp = tempfile.mkdtemp(prefix="konan-hook-test-")
    env = _hook_env(tmp)
    def run(cmd, cwd):
        p = subprocess.run([sys.executable, str(HERE / "boundary.py")],
                           input=json.dumps(dict(_event(cmd, session="s-scope"), cwd=cwd)),
                           capture_output=True, text=True, env=env)
        return p.stdout.strip()
    assert run("curl x", outside) == "" and run("wget x", outside) == ""
    assert not os.path.exists(os.path.join(tmp, "konan-boundary-s-scope.json"))
    assert run("ls", marker) == ""                            # governed now, and not frozen


def test_scope_process_silence():
    """Check 7: the hook process prints nothing outside a workspace for a raw network
    client, and the deny JSON with the marker as cwd; the environment is built by
    _hook_env, so an eval session or the runner does not grant the scope."""
    outside, marker = _outside_dir(), _marker_dir()
    rc, out, _ = _run_hook(json.dumps(dict(_event('bash -c "curl x"'), cwd=outside)))
    assert rc == 0 and out == ""
    rc, out, _ = _run_hook(json.dumps(dict(_event('bash -c "curl x"'), cwd=marker)))
    assert rc == 0 and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    scope = sum(1 for k in globals() if k.startswith("test_scope_"))
    print(f"OK: {len(tests)} boundary pins hold ({len(PINS)} decision-table rows + "
          f"{len(BLIND_PINS)} blind rows + {scope} scope pins)")
