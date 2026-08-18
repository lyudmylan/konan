#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""konan eval runner — stage a fixture, investigate it blind in a fresh headless session,
score the pair, and record what the run cost. Operator-side, deterministic code: it never
reasons about incidents; it only makes runs comparable and honest.

    uv run eval/run.py --run-id 2026-08-19-bench --model claude-sonnet-5 \
        [--repeat 3] [--fixtures eval/scenarios/*.yaml] [--max-runs 5] [--timeout-min 30] \
        [--dry-run] [--keep-worktree]

Per (fixture, repetition):
  1. Lab — `setup.lab: fresh` restarts faultline (clean logs and counters), from the
     run's worktree so `lab/` is the worktree's.
  2. Stage — executes the fixture's `setup.stage` list (eval-side, operator surface).
  3. Investigate — `claude -p --model <m> --permission-mode acceptEdits` in a detached git
     worktree of HEAD whose `journals/` is emptied (no incident memory, no ground truth),
     with `KONAN_EVAL_BLIND=1` so the boundary hook denies `gh`, reads under `eval/`, and
     the faultline checkout mechanically. The prompt is `/konan <complaint verbatim>` —
     nothing else.
  4. Record — the run's JSON envelope (session id, turns, duration, `modelUsage` = tokens
     for the whole run including subagents, API-equivalent cost, permission denials) into
     `<out>/<model>/<scenario>-r<n>.meta.json`; the journal is copied beside it and its
     `usage.tokens: null` is stamped with the measured total (documented in eval/README).
  5. Score — every (fixture, journal) pair of the run into `<out>/scorecard.md` via
     eval/score.py; per-run exit codes and failures land in `<out>/results.jsonl`.

`<out>` = eval/runs/<run-id>. Runs already present there are skipped (resume). The batch
stops on a rate-limit / quota error so a half-run never masquerades as a result.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "eval" / "runs"


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(cmd, cwd, timeout=120, env=None, check=True):
    p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, timeout=timeout, env=env,
                       stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {cmd}\n{p.stdout}\n{p.stderr}")
    return p


# --- lab (operator side; the runner may use curl — the investigator may not) ------------
def lab_healthy(base):
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def lab_stop(wt, env):
    subprocess.run(["scripts/lab.sh", "stop"], cwd=wt, env=env, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)


def lab_start(wt, env, base):
    # lab.sh backgrounds the server itself; keep every fd away from our pipes.
    subprocess.Popen(["scripts/lab.sh", "start"], cwd=wt, env=env, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    for _ in range(40):
        if lab_healthy(base):
            return
        time.sleep(1)
    raise RuntimeError("lab did not become healthy in 40s (see <worktree>/lab/server.out)")


# --- envelope → meta ----------------------------------------------------------------------
def envelope_meta(env_json):
    """Pure: the fields we keep from a `claude -p --output-format json` envelope."""
    mu = env_json.get("modelUsage") or {}
    total = 0
    per_model = {}
    for model, u in mu.items():
        cats = {k: int(u.get(k, 0) or 0) for k in
                ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens")}
        cats["costUSD"] = u.get("costUSD")
        per_model[model] = cats
        total += sum(v for k, v in cats.items() if k != "costUSD")
    denials = env_json.get("permission_denials") or []
    return {
        "session_id": env_json.get("session_id"),
        "is_error": bool(env_json.get("is_error")),
        "subtype": env_json.get("subtype"),
        "num_turns": env_json.get("num_turns"),
        "duration_ms": env_json.get("duration_ms"),
        "duration_api_ms": env_json.get("duration_api_ms"),
        "total_cost_usd": env_json.get("total_cost_usd"),
        "tokens_total": total if mu else None,          # all categories, whole run incl. subagents
        "model_usage": per_model,
        "permission_denials": [
            {"tool": d.get("tool_name"), "command": (d.get("tool_input") or {}).get("command")}
            for d in denials
        ],
        "result_tail": (env_json.get("result") or "")[-600:],
    }


def looks_like_quota_error(env_json):
    txt = json.dumps(env_json).lower()
    return env_json.get("api_error_status") == 429 or "session limit" in txt or "rate limit" in txt \
        or "usage limit" in txt or "hit your limit" in txt


TOKENS_LINE = re.compile(r"^(\s*tokens:\s*)null(\s*(#.*)?)$", re.M)
USER_5XX = re.compile(r'"event": "request".*?"status": 5\d\d')


def user_error_landed(log_text):
    """Pure: did any NON-investigator request (no konan- request id) end in a 5xx?
    Probabilistic fixtures assert user impact; without it the honest verdict differs
    from the fixture's, so the runner restages instead of scoring a coin flip."""
    for line in log_text.splitlines():
        if USER_5XX.search(line) and "konan-" not in line:
            return True
    return False


def stamp_tokens(journal_text, tokens):
    """Pure: replace the machine core's `tokens: null` with the measured total (once)."""
    if tokens is None:
        return journal_text, False
    head, sep, rest = journal_text.partition("\n---\n")  # front matter ends at the second ---
    if not sep:
        return journal_text, False
    new_head, n = TOKENS_LINE.subn(lambda m: f"{m.group(1)}{tokens}{m.group(2)}", head, count=1)
    return (new_head + sep + rest, True) if n == 1 else (journal_text, False)


# --- main flow ---------------------------------------------------------------------------
def load_fixtures(patterns):
    files = []
    for pat in patterns:
        files.extend(sorted(glob.glob(pat)))
    out = []
    for f in files:
        fx = yaml.safe_load(Path(f).read_text())
        out.append((Path(f).resolve(), fx))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--model", required=True, help="model id or alias passed to `claude --model`")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--fixtures", nargs="+", default=[str(REPO / "eval/scenarios/*.yaml")])
    ap.add_argument("--max-runs", type=int, default=0, help="stop after this many runs this invocation (0 = all)")
    ap.add_argument("--timeout-min", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-worktree", action="store_true")
    ap.add_argument("--restage-check", default="chaos-error-rate,t3-chaos-low-rate-intermittent",
                    help="comma-separated scenario ids whose staging must land a user-visible 5xx "
                         "(restaged up to 3 times; empty string disables)")
    a = ap.parse_args()

    faultline = os.environ.get("FAULTLINE_DIR", str((REPO / ".." / "faultline").resolve()))
    base = os.environ.get("KONAN_LAB_BASE", "http://127.0.0.1:8000")
    claude = os.environ.get("CLAUDE_BIN") or shutil.which("claude")
    fixtures = load_fixtures(a.fixtures)
    out = RUNS / a.run_id
    model_dir = out / re.sub(r"[^A-Za-z0-9._-]", "_", a.model)

    plan = [(fp, fx, r) for fp, fx in fixtures for r in range(1, a.repeat + 1)]
    def already_done(fx, r):
        """Resume rule (protocol): a run with a journal is done; a failed run is done too
        (it counts as failed) — only quota / rate-limit stops are retried."""
        tag = f"{fx['scenario']['id']}-r{r}"
        if (model_dir / f"{tag}.md").exists():
            return True
        meta_path = model_dir / f"{tag}.meta.json"
        if meta_path.exists():
            try:
                return not json.loads(meta_path.read_text()).get("quota_error", False)
            except ValueError:
                return False
        return False

    todo = [(fp, fx, r) for fp, fx, r in plan if not already_done(fx, r)]
    print(f"run {a.run_id}: model={a.model} fixtures={len(fixtures)} repeat={a.repeat} "
          f"planned={len(plan)} todo={len(todo)} out={out}")
    if a.dry_run:
        for fp, fx, r in todo:
            print(f"  {fx['scenario']['id']} r{r}  lab={fx.get('setup', {}).get('lab')} "
                  f"stage={len(fx.get('setup', {}).get('stage', []))} complaint={fx['complaint'][:60]!r}")
        return 0
    if not claude:
        sys.exit("claude CLI not found (set CLAUDE_BIN)")
    if not Path(faultline).is_dir():
        sys.exit(f"no faultline checkout at {faultline} (set FAULTLINE_DIR)")
    dirty = sh("git status --porcelain -- skills hooks .claude scripts docs", REPO).stdout.strip()
    if dirty:
        print("WARNING: uncommitted changes under skills/hooks/.claude/scripts/docs — the worktree runs HEAD, not them:\n" + dirty)

    # Worktree of HEAD with an empty journals/ — no memory, no ground truth in reach.
    wt = Path(tempfile.mkdtemp(prefix=f"konan-eval-{a.run_id}-")) / "wt"
    sh(["git", "worktree", "add", "--detach", str(wt), "HEAD"], REPO, timeout=60)
    for j in (wt / "journals").glob("*.md"):
        j.unlink()
    env = dict(os.environ, FAULTLINE_DIR=faultline, KONAN_EVAL_BLIND="1")
    model_dir.mkdir(parents=True, exist_ok=True)
    results = out / "results.jsonl"
    done = 0
    consecutive_timeouts = 0
    lab_up = False
    try:
        for fp, fx, r in todo:
            sid = fx["scenario"]["id"]
            tag = f"{sid}-r{r}"
            print(f"\n== {tag} ({a.model}) ==", flush=True)
            setup = fx.get("setup", {}) or {}
            if setup.get("lab") == "fresh" or not lab_up:
                lab_stop(wt, env)
                lab_start(wt, env, base)
                lab_up = True
            needs_user_error = sid in {x.strip() for x in a.restage_check.split(",") if x.strip()}
            restages = 0
            while True:
                for cmd in setup.get("stage", []) or []:
                    sh(cmd, wt, timeout=180, env=env)
                if not needs_user_error:
                    break
                log = wt / "lab" / "logs" / "app.log"
                if log.exists() and user_error_landed(log.read_text()):
                    break
                restages += 1
                if restages > 3:
                    raise RuntimeError(f"{tag}: no user-visible 5xx after 3 restages — fixture staging is off")
                print(f"   restage {restages}: no user-visible 5xx landed yet", flush=True)
                lab_stop(wt, env)
                lab_start(wt, env, base)
            for j in (wt / "journals").glob("*.md"):
                j.unlink()
            prompt = f"/konan {fx['complaint']}"
            started = now_iso()
            t0 = time.time()
            timed_out = False
            try:
                p = subprocess.run([claude, "-p", "--model", a.model, "--permission-mode", "acceptEdits",
                                    "--output-format", "json", prompt],
                                   cwd=wt, env=env, stdin=subprocess.DEVNULL, capture_output=True,
                                   text=True, timeout=a.timeout_min * 60)
                out_text, rc_code, err_text = p.stdout, p.returncode, p.stderr
            except subprocess.TimeoutExpired as e:   # the child is killed by run(); record, continue
                timed_out = True
                out_text, rc_code = "", None
                err_text = (e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or ""))
            ended = now_iso()
            if timed_out:
                envelope = {"is_error": True, "subtype": "timeout",
                            "result": f"runner timeout after {a.timeout_min} min (killed)"}
            else:
                try:
                    envelope = json.loads(out_text)
                except ValueError:
                    envelope = {"is_error": True, "result": f"non-JSON output (rc={rc_code}): "
                                f"{out_text[-800:]}\n{err_text[-800:]}"}
            meta = envelope_meta(envelope)
            meta.update({"run_id": a.run_id, "model": a.model, "scenario": sid, "rep": r,
                         "fixture": str(fp.relative_to(REPO)), "started_at": started, "ended_at": ended,
                         "restages": restages,
                         "wall_seconds_runner": round(time.time() - t0)})
            journals = list((wt / "journals").glob("*.md"))
            status = "ok"
            if timed_out:
                status = "timeout"
            elif meta["is_error"]:
                status = "error"
            elif len(journals) != 1:
                status = f"no-journal" if not journals else f"{len(journals)}-journals"
            if status == "ok":
                text = journals[0].read_text()
                text, stamped = stamp_tokens(text, meta["tokens_total"])
                meta["journal_source_name"] = journals[0].name
                meta["tokens_stamped"] = stamped
                (model_dir / f"{tag}.md").write_text(text)
            meta["status"] = status
            meta["quota_error"] = bool(meta["is_error"] and looks_like_quota_error(envelope))
            (model_dir / f"{tag}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
            with results.open("a") as f:
                f.write(json.dumps({k: meta[k] for k in ("run_id", "model", "scenario", "rep", "status",
                                                          "session_id", "num_turns", "duration_ms",
                                                          "tokens_total", "total_cost_usd")}) + "\n")
            print(f"   {status}: turns={meta['num_turns']} dur={meta['duration_ms']}ms "
                  f"tokens={meta['tokens_total']} cost=${meta['total_cost_usd']} "
                  f"denials={len(meta['permission_denials'])}", flush=True)
            done += 1
            consecutive_timeouts = consecutive_timeouts + 1 if timed_out else 0
            if meta["quota_error"]:
                print("STOP: quota / rate-limit error — resume with the same --run-id after the window resets.")
                break
            if consecutive_timeouts >= 2:
                print("STOP: two consecutive timeouts — likely a stalled harness or rate-limit backoff; "
                      "resume with the same --run-id later (timeouts count as failed runs).")
                break
            if a.max_runs and done >= a.max_runs:
                print(f"stopping after --max-runs={a.max_runs}; resume with the same --run-id")
                break
    finally:
        lab_stop(wt, env)
        if not a.keep_worktree:
            sh(["git", "worktree", "remove", "--force", str(wt)], REPO, timeout=60, check=False)
        else:
            print(f"worktree kept: {wt}")

    # Score every pair present for this run (all models), refuse nothing silently.
    pairs = []
    for m in sorted(out.iterdir()):
        if not m.is_dir():
            continue
        for j in sorted(m.glob("*.md")):
            sid = re.sub(r"-r\d+$", "", j.stem)
            fx = next((fp for fp, f in fixtures if f["scenario"]["id"] == sid), None)
            if fx:
                pairs += ["--pair", str(fx), str(j)]
    if pairs:
        rc = subprocess.run(["uv", "run", str(REPO / "eval/score.py"), *pairs, "-o", str(out / "scorecard.md")],
                            cwd=REPO, stdin=subprocess.DEVNULL).returncode
        print(f"scorecard: {out / 'scorecard.md'} (score.py exit {rc})")
        return rc
    print("no journals to score")
    return 2


if __name__ == "__main__":
    sys.exit(main())
