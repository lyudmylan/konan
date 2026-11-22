#!/usr/bin/env python3
"""Pins for the alert receiver. Plain asserts, stdlib only: `python3 scripts/tests.py`.

Each pin fixes one automatic check of intents/alert-webhook.md and cites its number.
Every pin runs against a receiver on a free port of the loopback interface, with a
temporary inbox and a temporary token; the inbox of the repository is never written."""
import contextlib
import io
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import receive  # noqa: E402

TOKEN = "pin-token-4f1c9a"
SUMMARY = "checkout latency above the limit"


def _alert(fingerprint="a1b2c3", starts="2026-11-16T10:00:00Z", status="firing", **extra):
    alert = {
        "status": status,
        "labels": {"alertname": "HighLatency", "severity": "page"},
        "annotations": {"summary": SUMMARY},
        "startsAt": starts,
        "endsAt": "0001-01-01T00:00:00Z",
        "generatorURL": "http://prometheus.example/graph?g0.expr=up",
        "fingerprint": fingerprint,
    }
    alert.update(extra)
    return alert


def _group(*alerts, status="firing"):
    return {"version": "4", "groupKey": '{}:{alertname="HighLatency"}', "status": status,
            "receiver": "konan", "alerts": list(alerts)}


class _Lab:
    """One receiver in a thread, with its temporary inbox and its captured log."""

    def __init__(self, inbox=None, token=TOKEN, read_seconds=receive.READ_SECONDS):
        self.dir = tempfile.mkdtemp(prefix="konan-receiver-")
        self.inbox = Path(inbox) if inbox else Path(self.dir) / "inbox.jsonl"
        self.log = io.StringIO()
        self.receiver = receive.Receiver(self.inbox, token, log=self.log)
        self.server = receive.make_server("127.0.0.1", 0, self.receiver, read_seconds=read_seconds)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(5)

    def lines(self):
        """The lines of the inbox, split on the line feed only."""
        if not self.inbox.exists():
            return []
        text = self.inbox.read_bytes().decode("utf-8")
        return [line for line in text.split("\n") if line]

    def call(self, payload, token=TOKEN, method="POST", path="/alerts", auth=None):
        """One call; returns (answer code, parsed answer body)."""
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}",
                                     data=None if method == "GET" else data, method=method)
        if auth is not None:
            req.add_header("Authorization", auth)
        elif token is not None:
            req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def raw(self, request: bytes, timeout=5.0) -> bytes:
        """Send raw bytes, half-close nothing, and return what the receiver answers."""
        with socket.create_connection(("127.0.0.1", self.port), timeout=timeout) as s:
            s.sendall(request)
            chunks = []
            try:
                while chunk := s.recv(65536):
                    chunks.append(chunk)
            except OSError:
                pass
            return b"".join(chunks)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run_script(env_extra: dict, timeout=10):
    env = {k: v for k, v in os.environ.items() if not k.startswith("KONAN_RECEIVER_")}
    env.update(env_extra)
    return subprocess.run([sys.executable, str(HERE / "receive.py")], env=env,
                          capture_output=True, text=True, timeout=timeout)


def test_call_without_the_token_is_refused():
    """Check 1: no header, a wrong token and another scheme get 401 and write nothing;
    a token file that ends with a line break accepts the call with the token."""
    with _Lab() as lab:
        assert lab.call(_group(_alert()), token=None)[0] == 401
        assert lab.call(_group(_alert()), token="not-the-token")[0] == 401
        assert lab.call(_group(_alert()), token=TOKEN + "x")[0] == 401
        assert lab.call(_group(_alert()), auth=f"Basic {TOKEN}")[0] == 401
        assert lab.call(_group(_alert()), auth=TOKEN)[0] == 401
        assert lab.lines() == []
    with tempfile.TemporaryDirectory() as tmp:
        token_file = Path(tmp) / "token"
        token_file.write_text(TOKEN + "\n", encoding="utf-8")
        assert receive.read_token(token_file) == TOKEN
        token_file.write_text("  \n\n", encoding="utf-8")
        assert receive.read_token(token_file) is None
        assert receive.read_token(Path(tmp) / "missing") is None
        token_file.write_text(TOKEN + "\n", encoding="utf-8")
        with _Lab(token=receive.read_token(token_file)) as lab:
            assert lab.call(_group(_alert()))[0] == 200
            assert len(lab.lines()) == 1


def test_firing_group_becomes_one_line_per_alert():
    """Check 2: a group of two firing alerts adds two lines, each one complaint object
    with the fields of the call; a line break in an annotation stays inside its line."""
    first = _alert("f-one", annotations={"summary": "line one\nline two\r\nline three"})
    second = _alert("f-two", starts="2026-11-16T10:05:00Z")
    del second["generatorURL"]
    with _Lab() as lab:
        code, counts = lab.call(_group(first, second))
        assert code == 200 and counts == {"new": 2, "known": 0, "resolved": 0}
        lines = lab.lines()
        assert len(lines) == 2
        objs = [json.loads(line) for line in lines]
        for obj, alert in zip(objs, (first, second)):
            assert obj["source"] == "alert"
            for field in ("fingerprint", "labels", "annotations", "startsAt"):
                assert obj[field] == alert[field], field
        assert objs[0]["generatorURL"] == first["generatorURL"]
        assert set(objs[0]) == {"source", "fingerprint", "labels", "annotations", "startsAt", "generatorURL"}
        assert set(objs[1]) == {"source", "fingerprint", "labels", "annotations", "startsAt"}
        assert lab.inbox.read_bytes().endswith(b"\n")


def test_repeat_adds_no_line_and_a_new_start_adds_one():
    """Check 3: a repeat of a pair adds no line, also after a restart on the same inbox,
    also with a line in the inbox that does not parse, also for two identical calls at
    the same time; the same fingerprint with a later startsAt adds one line."""
    with _Lab() as lab:
        assert lab.call(_group(_alert()))[1] == {"new": 1, "known": 0, "resolved": 0}
        code, counts = lab.call(_group(_alert()))
        assert code == 200 and counts == {"new": 0, "known": 1, "resolved": 0}
        assert len(lab.lines()) == 1
        inbox = lab.inbox
    with open(inbox, "a", encoding="utf-8") as f:           # a line that does not parse,
        f.write("not a json line\n")                         # and a last line with no end
        f.write('{"source": "alert", "fingerprint": "lab-1", "startsAt": "t"}')
    with _Lab(inbox=inbox) as lab:                           # the restart
        assert ("a1b2c3", "2026-11-16T10:00:00Z") in lab.receiver.pairs
        assert lab.call(_group(_alert()))[1] == {"new": 0, "known": 1, "resolved": 0}
        assert len(lab.lines()) == 3
        fresh = _group(_alert("same-time"))                  # two identical calls at once
        barrier, answers = threading.Barrier(2), []

        def send():
            barrier.wait(5)
            answers.append(lab.call(fresh))

        threads = [threading.Thread(target=send) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(15)
        assert sorted(a[0] for a in answers) == [200, 200]
        assert sorted(a[1]["new"] for a in answers) == [0, 1]
        assert len(lab.lines()) == 4
        later = _alert(starts="2026-11-16T14:00:00Z")        # the alert fires again later
        assert lab.call(_group(later))[1] == {"new": 1, "known": 0, "resolved": 0}
        lines = lab.lines()
        assert len(lines) == 5
        assert json.loads(lines[2])["fingerprint"] == "lab-1"    # the open line got its end
        assert json.loads(lines[4])["startsAt"] == "2026-11-16T14:00:00Z"


def test_resolved_alert_adds_no_line():
    """Check 4: a resolved alert gets 200 and adds no line; a call with one firing and
    one resolved alert adds one line."""
    with _Lab() as lab:
        code, counts = lab.call(_group(_alert(status="resolved"), status="resolved"))
        assert code == 200 and counts == {"new": 0, "known": 0, "resolved": 1}
        assert lab.lines() == []
        code, counts = lab.call(_group(_alert("f-fire"), _alert("f-done", status="resolved")))
        assert code == 200 and counts == {"new": 1, "known": 0, "resolved": 1}
        lines = lab.lines()
        assert len(lines) == 1 and json.loads(lines[0])["fingerprint"] == "f-fire"


def test_malformed_call_writes_nothing():
    """Check 5: each fault gets an answer in the 400 range and writes nothing, also for
    the valid alerts of the same call; a wrong path and a wrong method write nothing; a
    connection that sends no body does not block the next call."""
    good = _alert("f-good")
    no_fingerprint = _alert()
    del no_fingerprint["fingerprint"]
    no_start = _alert()
    del no_start["startsAt"]
    faults = [
        b"this is not json",
        b"\xff\xfe\x00",
        b"[]",
        {"status": "firing"},
        {"alerts": "none"},
        _group(good, no_fingerprint),
        _group(good, no_start),
        _group(good, _alert(fingerprint="")),
        _group(good, _alert(fingerprint=7)),
        _group(good, _alert(status="pending")),
        _group(good, _alert(labels=["a"])),
        _group(good, "not an alert"),
    ]
    with _Lab(read_seconds=0.5) as lab:
        for fault in faults:
            assert lab.call(fault)[0] == 400, fault
        auth = f"Authorization: Bearer {TOKEN}\r\n".encode()
        # A declared length over the limit: 413 before any body is read.
        answer = lab.raw(b"POST /alerts HTTP/1.1\r\n" + auth
                         + f"Content-Length: {receive.MAX_BODY + 1}\r\n\r\n".encode())
        assert answer.startswith(b"HTTP/1.0 413"), answer[:40]
        # A real body over the limit, sent in full.
        big = _group(_alert("f-big", annotations={"summary": "x" * (receive.MAX_BODY + 10)}))
        try:
            assert lab.call(big)[0] == 413
        except OSError:
            pass                                  # the receiver may close while the body is sent
        # No length.
        answer = lab.raw(b"POST /alerts HTTP/1.1\r\n" + auth + b"\r\n")
        assert answer.startswith(b"HTTP/1.0 411"), answer[:40]
        # A wrong path, and a method other than POST.
        assert lab.call(_group(good), path="/")[0] == 404
        assert lab.call(_group(good), path="/alerts/")[0] == 404
        assert lab.call(_group(good), method="GET")[0] == 405
        assert lab.call(_group(good), method="PUT")[0] == 405
        # A connection that sends headers and no body, and one that sends nothing at all.
        stalled = socket.create_connection(("127.0.0.1", lab.port), timeout=5)
        stalled.sendall(b"POST /alerts HTTP/1.1\r\n" + auth + b"Content-Length: 50\r\n\r\n")
        silent = socket.create_connection(("127.0.0.1", lab.port), timeout=5)
        assert lab.lines() == []
        began = time.monotonic()
        assert lab.call(_group(good)) == (200, {"new": 1, "known": 0, "resolved": 0})
        assert time.monotonic() - began < 5
        stalled.close()
        silent.close()
        assert len(lab.lines()) == 1              # only the valid call wrote


def test_no_token_no_listener():
    """Check 6: without a token file, and with an empty one, the script exits with a
    non-zero code and opens no port."""
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty-token"
        empty.write_text("\n  \n", encoding="utf-8")
        for token_file in (Path(tmp) / "missing-token", empty):
            port = _free_port()
            done = _run_script({"KONAN_RECEIVER_TOKEN_FILE": str(token_file),
                                "KONAN_RECEIVER_PORT": str(port)})
            assert done.returncode == 2, done
            assert "no token" in done.stderr and done.stdout == ""
            try:
                socket.create_connection(("127.0.0.1", port), timeout=1).close()
                raise AssertionError("a port is open without a token")
            except OSError:
                pass


def test_default_address_is_loopback():
    """Check 7: without KONAN_RECEIVER_HOST the receiver binds the loopback address."""
    assert receive.address({}) == ("127.0.0.1", 9911)
    assert receive.address({"KONAN_RECEIVER_PORT": "9912"}) == ("127.0.0.1", 9912)
    assert receive.address({"KONAN_RECEIVER_HOST": "0.0.0.0"}) == ("0.0.0.0", 9911)
    for bad in ("0", "70000", "port"):
        try:
            receive.address({"KONAN_RECEIVER_PORT": bad})
            raise AssertionError(f"accepted the port {bad!r}")
        except ValueError:
            pass


def test_log_holds_no_token_and_no_body():
    """Check 8: the log of a call holds the answer code and the counts, and holds
    neither the token nor the summary text of the alert."""
    with _Lab() as lab:
        lab.call(_group(_alert(), _alert("f-done", status="resolved")))
        lab.call(_group(_alert()), token="a-wrong-token")
        lab.call(b"not json " + SUMMARY.encode())
        log = lab.log.getvalue()
    lines = log.splitlines()
    assert len(lines) == 3
    assert lines[0].endswith(" 200 new=1 known=0 resolved=1")
    assert lines[1].endswith(" 401 new=0 known=0 resolved=0")
    assert lines[2].endswith(" 400 new=0 known=0 resolved=0")
    for secret in (TOKEN, "a-wrong-token", SUMMARY, "HighLatency", "a1b2c3"):
        assert secret not in log, secret


def test_settings_allow_the_receiver_without_arguments():
    """Check 9: the allow list holds the two exact entries, and no entry for the
    receiver with an argument form."""
    settings = json.loads((HERE.parent / ".claude" / "settings.json").read_text(encoding="utf-8"))
    entries = [e for e in settings["permissions"]["allow"] if "receive.py" in e]
    assert sorted(entries) == ["Bash(./scripts/receive.py)", "Bash(scripts/receive.py)"], entries
    with contextlib.redirect_stderr(io.StringIO()):
        assert receive.main(argv=["--port", "1"]) == 2    # the script takes no argument


def test_write_failure_is_500_and_taken_port_exits():
    """Check 10: a write to the inbox that fails gets 500 and adds no line; with the
    port taken, the script exits with a non-zero code."""
    with _Lab() as lab:
        blocked = Path(lab.dir) / "a-directory"
        blocked.mkdir()
        lab.receiver.inbox = blocked                          # an append to a directory fails
        code, _ = lab.call(_group(_alert("f-lost")))
        assert code == 500
        assert list(blocked.iterdir()) == [] and lab.lines() == []
        assert ("f-lost", "2026-11-16T10:00:00Z") not in lab.receiver.pairs
        lab.receiver.inbox = lab.inbox                        # the retry of the sender
        assert lab.call(_group(_alert("f-lost")))[1]["new"] == 1
    with tempfile.TemporaryDirectory() as tmp, socket.socket() as holder:
        holder.bind(("127.0.0.1", 0))
        holder.listen(1)
        token_file = Path(tmp) / "token"
        token_file.write_text(TOKEN + "\n", encoding="utf-8")
        done = _run_script({"KONAN_RECEIVER_TOKEN_FILE": str(token_file),
                            "KONAN_RECEIVER_PORT": str(holder.getsockname()[1])})
        assert done.returncode == 1, done
        assert "cannot listen" in done.stderr and TOKEN not in done.stderr


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"OK: {len(tests)} receiver pins hold")
