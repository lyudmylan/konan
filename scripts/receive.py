#!/usr/bin/env python3
"""konan alert receiver: the HTTP transport of the trigger contract (docs/triggers.md).

It waits for the webhook call of Alertmanager at one address, verifies the token of the
call, and appends one complaint object per new firing alert to alerts/inbox.jsonl, the
inbox that the on-call shift watches. It starts no investigation itself and sends nothing.

  address   POST /alerts on 127.0.0.1:9911; KONAN_RECEIVER_HOST and KONAN_RECEIVER_PORT
            change it. A host other than loopback sends the token in clear text.
  origin    `Authorization: Bearer <token>`. The token is the content of
            alerts/receiver-token, or of the file that KONAN_RECEIVER_TOKEN_FILE names,
            with the whitespace at both ends removed. No token, no listener.
  payload   the native webhook payload of Alertmanager: an object with a list `alerts`.
            A firing alert becomes {source, fingerprint, labels, annotations, startsAt,
            generatorURL}, the fields copied as they came. The whole payload is checked
            before anything is written.
  repeat    the key of an alert is the pair (fingerprint, startsAt). A pair already in
            the inbox adds no line; a resolved alert adds no line. The inbox is the only
            memory: the pairs are read from it at start, and again when the file was
            changed from outside (emptied, replaced, appended).
  one       a lock file next to the inbox, held for the life of the process: a second
            receiver on the same inbox exits, also when it could bind its address.
  answers   200 with the counts; 401 token; 404 path; 405 method; 411 or 413 length;
            400 payload; 500 when the write fails, so that the sender retries.
  log       one line per call on standard output: time, answer code, the three counts.
            Never the token, never the body. A read that passed its limit is logged as
            408 and gets no answer.

One call at a time, in one thread, so the test of a pair and the append of its line are
one step. The read of one call has a limit of READ_SECONDS in total. Standard library
only. No option on the command line: the permission entries of the shift are exact.
Intent: intents/alert-webhook.md. Pins: `python3 scripts/tests.py`.
"""
import fcntl
import hmac
import io
import json
import os
import socket
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "alerts" / "inbox.jsonl"
TOKEN_FILE = ROOT / "alerts" / "receiver-token"
ALERTS_PATH = "/alerts"
DEFAULT_HOST, DEFAULT_PORT = "127.0.0.1", 9911
MAX_BODY = 1 << 20          # 1 MiB
READ_SECONDS = 10.0         # the whole read of one call: request line, headers and body
NO_COUNTS = {"new": 0, "known": 0, "resolved": 0}


class BadCall(Exception):
    """The payload is not the webhook payload of Alertmanager."""


def read_token(path) -> str | None:
    """The token of the file, with the whitespace at both ends removed; None for a
    missing, unreadable or empty file."""
    try:
        token = Path(path).read_text(encoding="utf-8-sig").strip()
    except (OSError, UnicodeDecodeError):
        return None
    return token or None


def address(env) -> tuple[str, int]:
    """The host and the port from the environment; loopback and 9911 without the two
    variables. A port that is not a port number raises ValueError."""
    host = env.get("KONAN_RECEIVER_HOST") or DEFAULT_HOST
    port = int(env.get("KONAN_RECEIVER_PORT") or DEFAULT_PORT)
    if not 1 <= port <= 65535:
        raise ValueError(f"port out of range: {port}")
    return host, port


def known_pairs(inbox) -> set[tuple[str, str]]:
    """The (fingerprint, startsAt) pairs of the inbox. A line that does not parse, or
    that lacks one of the two fields, is skipped; a missing inbox has no pairs."""
    pairs = set()
    try:
        with open(inbox, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if isinstance(obj, dict) and isinstance(obj.get("fingerprint"), str) \
                        and isinstance(obj.get("startsAt"), str):
                    pairs.add((obj["fingerprint"], obj["startsAt"]))
    except FileNotFoundError:
        pass
    return pairs


def complaints(payload) -> tuple[list[dict], int]:
    """Check the whole payload, then return the complaint objects of its firing alerts,
    in the order of the list, and the count of its resolved alerts. Any fault raises
    BadCall, so a call with one bad alert writes nothing."""
    if not isinstance(payload, dict) or not isinstance(payload.get("alerts"), list):
        raise BadCall("no list `alerts`")
    firing, resolved = [], 0
    for alert in payload["alerts"]:
        if not isinstance(alert, dict):
            raise BadCall("an alert is not an object")
        if alert.get("status") not in ("firing", "resolved"):
            raise BadCall("an alert has no status `firing` or `resolved`")
        for field in ("fingerprint", "startsAt"):
            if not isinstance(alert.get(field), str) or not alert[field]:
                raise BadCall(f"an alert has no `{field}`")
        for field in ("labels", "annotations"):
            if not isinstance(alert.get(field, {}), dict):
                raise BadCall(f"`{field}` of an alert is not an object")
        if "generatorURL" in alert and not isinstance(alert["generatorURL"], str):
            raise BadCall("`generatorURL` of an alert is not a text")
        if alert["status"] == "resolved":
            resolved += 1
            continue
        obj = {
            "source": "alert",
            "fingerprint": alert["fingerprint"],
            "labels": alert.get("labels", {}),
            "annotations": alert.get("annotations", {}),
            "startsAt": alert["startsAt"],
        }
        if "generatorURL" in alert:
            obj["generatorURL"] = alert["generatorURL"]
        firing.append(obj)
    return firing, resolved


class Receiver:
    """The state of one receiver: the inbox, the token, and the pairs it knows."""

    def __init__(self, inbox, token: str, log=None):
        self.inbox = Path(inbox)
        self.token = token
        self.log = log if log is not None else sys.stdout
        self._seen = self._signature()
        self.pairs = known_pairs(self.inbox)

    def _signature(self):
        """What tells that the inbox changed: its file, its size, its last write."""
        try:
            st = os.stat(self.inbox)
        except OSError:
            return None
        return st.st_ino, st.st_size, st.st_mtime_ns

    def _refresh(self) -> None:
        """Read the pairs again when the inbox was changed from outside, so that a
        pair counts as known only while its line is in the inbox."""
        signature = self._signature()
        if signature != self._seen:
            self.pairs = known_pairs(self.inbox)
            self._seen = signature

    def authorized(self, header: str | None) -> bool:
        """http.server decodes a header as ISO-8859-1, so the bytes of the credentials
        are compared with the bytes of the token."""
        scheme, _, credentials = (header or "").partition(" ")
        try:
            sent = credentials.strip(" \t").encode("latin-1")
        except UnicodeEncodeError:
            return False
        return scheme.lower() == "bearer" and hmac.compare_digest(sent, self.token.encode("utf-8"))

    def accept(self, body: bytes) -> tuple[int, dict]:
        """Decide one authorized call: (answer code, counts)."""
        try:
            firing, resolved = complaints(json.loads(body))
        except (ValueError, RecursionError, BadCall):
            return 400, dict(NO_COUNTS)
        counts = {"new": 0, "known": 0, "resolved": resolved}
        try:
            self._refresh()
            for obj in firing:
                pair = (obj["fingerprint"], obj["startsAt"])
                if pair in self.pairs:
                    counts["known"] += 1
                    continue
                self._append(obj)
                self.pairs.add(pair)
                counts["new"] += 1
        except OSError:
            # Lines written before the error stay; the retry of the sender finds them known.
            return 500, counts
        return 200, counts

    def _append(self, obj: dict) -> None:
        """One JSON line, on disk before the answer. json.dumps keeps a line break of a
        text escaped, so one object is always one line."""
        line = json.dumps(obj) + "\n"
        with open(self.inbox, "a+b") as f:
            if f.tell():                      # an inbox whose last line has no end
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    line = "\n" + line
            f.write(line.encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())
        self._seen = self._signature()

    def note(self, code: int, counts: dict | None = None) -> None:
        c = counts or NO_COUNTS
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"{stamp} {int(code)} new={c['new']} known={c['known']} resolved={c['resolved']}",
              file=self.log, flush=True)


class _DeadlineReader(io.RawIOBase):
    """The read side of one connection with one limit for all of its reads."""

    def __init__(self, sock, seconds: float):
        self._sock = sock
        self._deadline = time.monotonic() + seconds

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("read limit")
        self._sock.settimeout(remaining)
        return self._sock.recv_into(buffer)


def make_server(host: str, port: int, receiver: Receiver,
                read_seconds: float = READ_SECONDS) -> HTTPServer:
    """Bind the address and return the server. HTTPServer answers one call at a time."""

    class Handler(BaseHTTPRequestHandler):
        server_version = "konan-receiver"
        sys_version = ""

        def setup(self):
            super().setup()
            self.rfile = io.BufferedReader(_DeadlineReader(self.connection, read_seconds))

        def log_message(self, format, *args):     # the library prints the request line
            pass

        def log_error(self, format, *args):
            if format.startswith("Request timed out"):
                receiver.note(408)

        def send_error(self, code, message=None, explain=None):
            """The answers of the library (a bad request line, a method with no
            handler) take the same route as ours, so each call has its log line."""
            self._answer(405 if int(code) == 501 else int(code))

        def _answer(self, code: int, counts: dict | None = None):
            receiver.note(code, counts)           # before the write: a sender that left is logged too
            body = json.dumps(counts if code == 200 else {"code": code}).encode("utf-8")
            self.close_connection = True
            try:
                self.connection.settimeout(read_seconds)
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)
            except OSError:
                return
            self._linger()

        def _linger(self):
            """Close the write side, then discard what the sender still sends, for one
            second at most. Without it, an answer that comes before the body was read
            (401, 411, 413) can be lost when the connection closes with unread bytes."""
            try:
                self.wfile.flush()
                self.connection.shutdown(socket.SHUT_WR)
                tail = _DeadlineReader(self.connection, min(read_seconds, 1.0))
                buffer, left = bytearray(65536), MAX_BODY + 65536
                while left > 0:
                    n = tail.readinto(buffer)
                    if not n:
                        break
                    left -= n
            except OSError:
                pass

        def _not_post(self):
            self._answer(404 if self.path != ALERTS_PATH else 405)

        do_GET = do_HEAD = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = _not_post

        def do_POST(self):
            if self.path != ALERTS_PATH:
                return self._answer(404)
            if not receiver.authorized(self.headers.get("Authorization")):
                return self._answer(401)
            length = self.headers.get("Content-Length", "")
            if not (length.isascii() and length.isdigit()):
                return self._answer(411)
            if len(length) > 7 or int(length) > MAX_BODY:
                return self._answer(413)
            try:
                body = self.rfile.read(int(length))
            except OSError:                       # the read limit, or a broken connection
                self.close_connection = True
                return receiver.note(408)
            if len(body) != int(length):          # the sender closed before the end
                self.close_connection = True
                return receiver.note(400)
            self._answer(*receiver.accept(body))

    return HTTPServer((host, port), Handler)


def hold_inbox(inbox):
    """Take the lock of one inbox for the life of the process. Returns the open lock
    file, or None when another receiver holds it. Two receivers can bind the same port
    on some systems (one on the loopback address, one on all addresses), and each would
    keep its own memory of the pairs."""
    lock = open(Path(inbox).with_name("receiver.lock"), "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock.close()
        return None
    return lock


def main(argv=None, env=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    env = os.environ if env is None else env
    if argv:
        print("usage: scripts/receive.py (no arguments; see the docstring)", file=sys.stderr)
        return 2
    token_file = Path(env.get("KONAN_RECEIVER_TOKEN_FILE") or TOKEN_FILE)
    token = read_token(token_file)
    if not token:
        print(f"receiver: no token in {token_file}; not listening", file=sys.stderr)
        return 2
    try:
        host, port = address(env)
    except ValueError as e:
        print(f"receiver: bad address: {e}", file=sys.stderr)
        return 2
    try:
        receiver = Receiver(INBOX, token)
        server = make_server(host, port, receiver)
    except OSError as e:
        print(f"receiver: cannot listen on {host}:{port}: {e}", file=sys.stderr)
        return 1
    INBOX.parent.mkdir(parents=True, exist_ok=True)
    lock = hold_inbox(INBOX)
    if lock is None:
        server.server_close()
        print(f"receiver: another receiver holds {INBOX.parent.name}/{INBOX.name}; not listening",
              file=sys.stderr)
        return 1
    print(f"receiver: listening on http://{host}:{port}{ALERTS_PATH}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        lock.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
